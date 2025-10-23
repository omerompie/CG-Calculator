import tkinter as tk
from tkinter import messagebox, simpledialog
# Removed 'import json' and 'import os'

# --- Local Imports ---
import src.config as config
from src.calculations import interpolate_arm
from src.app_utils import load_json_data


class FuelLoadSystem:
    """
    A tkinter GUI module for managing fuel load across multiple tanks,
    calculating individual and total fuel weight, moment, and CG.
    """

    def __init__(self, master, tank_data, on_change_callback=None):
        """
        Initializes the FuelLoadSystem widget.

        Args:
            master (tk.Widget): The parent tkinter widget.
            tank_data (list): The list of dictionaries defining the fuel tanks.
            on_change_callback (callable, optional): A function to call
                whenever the fuel load changes.
        """
        self.master = master
        self.tank_data = tank_data
        self.state = {}  # Stores current load {tname: {"liters": l, "arm": a, "weight": w}}
        self.widgets = {}  # Stores UI widgets for each tank

        self.fuel_density = config.DEFAULT_FUEL_DENSITY_KG_L  # Set initial density from config

        self.on_change_callback = on_change_callback
        self.create_widgets()
        self.update_summary()  # Initial summary calculation

    def create_widgets(self):
        """Creates and lays out all tkinter widgets for the fuel tanks."""
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.frame, text="Fuel Loading by Tank", font=("Arial", 16, "bold")).pack(pady=10)

        # Canvas for horizontal scrolling
        self.canvas = tk.Canvas(self.frame, height=260)
        self.scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.tank_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.tank_frame, anchor='nw')
        self.tank_frame.bind("<Configure>", self.on_frame_configure)

        col = 0
        for tank in self.tank_data:
            tname = tank["tank"]
            # SKIP backend-only combined tank table from UI
            if tname == "main_tanks_combined_table":
                continue

            widget = {}
            tf = tk.Frame(self.tank_frame, bd=1, relief="solid", padx=5, pady=5)
            tf.grid(row=0, column=col, padx=5, pady=5)
            tk.Label(tf, text=tname, font=("Arial", 12)).pack()

            tk.Label(tf, text=f"Max: {tank['max_l']} L / {tank['max_kg']} kg", font=("Arial", 10)).pack()

            widget["entry"] = tk.Entry(tf, width=10, justify='center')
            widget["entry"].insert(0, "0")
            widget["entry"].pack(pady=2)

            tk.Button(tf, text="Set Liters", command=lambda t=tank: self.set_liters_popup(t)).pack(pady=1)
            tk.Button(tf, text="Load Max", command=lambda t=tank: self.set_liters(t, t["max_l"])).pack(pady=1)

            widget["arm_label"] = tk.Label(tf, text="Arm: --")
            widget["arm_label"].pack(pady=1)
            widget["kg_label"] = tk.Label(tf, text="Weight: --")
            widget["kg_label"].pack(pady=1)

            self.widgets[tname] = widget
            col += 1

        # Control buttons
        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=10)
        tk.Button(btn_frame, text="Set Fuel Density", command=self.set_density).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="End & Export Results", command=self.export_results).pack(pady=10)

        # Summary display
        self.summary_label = tk.Label(self.frame, text="Total: ...", font=("Arial", 13))
        self.summary_label.pack(pady=10)

    def _trigger_callback(self):
        """Safely triggers the on_change_callback if it exists."""
        if self.on_change_callback:
            self.on_change_callback()

    def on_frame_configure(self, event):
        """Updates the canvas scroll region when the inner frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def set_density(self):
        """
        Opens a dialog to set a new fuel density.
        Recalculates all tank weights upon change.
        """
        density = simpledialog.askfloat("Fuel Density",
                                        "Enter fuel density (kg/L) between 0.7309 and 0.8507:",
                                        minvalue=0.7309, maxvalue=0.8507,
                                        initialvalue=self.fuel_density)
        if density:
            self.fuel_density = density
            messagebox.showinfo("Density Set", f"Fuel density set to {density:.4f} kg/L")
            # Re-calculate all tanks based on new density
            for tank in self.tank_data:
                tname = tank["tank"]
                if tname == "main_tanks_combined_table":
                    continue

                liters = self.state.get(tname, {}).get("liters", 0)
                self.set_liters(tank, liters)  # This will update state and UI

            # No need to call update_summary() here, as set_liters() does it.

    def deselect_all(self):
        """Sets all fuel tanks to 0 liters."""
        for tank in self.tank_data:
            tname = tank["tank"]
            if tname == "main_tanks_combined_table":
                continue

            self.state[tname] = {"liters": 0, "arm": 0, "weight": 0}
            w = self.widgets[tname]
            w["entry"].delete(0, tk.END)
            w["entry"].insert(0, "0")
            w["arm_label"].config(text="Arm: --")
            w["kg_label"].config(text="Weight: --")

        self.update_summary()  # Update summary once after all changes

    def set_liters_popup(self, tank):
        """
        Opens a dialog to set the liter amount for a specific tank.

        Args:
            tank (dict): The tank data dictionary.
        """
        max_l = tank["max_l"]
        val = simpledialog.askfloat("Fuel Amount", f"Enter liters for {tank['tank']} (max {max_l} L):",
                                    minvalue=0, maxvalue=max_l)
        if val is not None:
            self.set_liters(tank, val)

    def set_liters(self, tank, liters):
        """
        Sets the liter amount for a tank and recalculates its arm and weight.

        Args:
            tank (dict): The tank data dictionary.
            liters (float): The amount of fuel in liters.
        """
        liters = round(liters, 1)
        tname = tank["tank"]

        # Call the imported interpolate_arm function
        arm = interpolate_arm(tank["arm_table"], liters)
        # ---

        kg = round(liters * self.fuel_density, 1)

        # Update the internal state
        self.state[tname] = {"liters": liters, "arm": arm, "weight": kg}

        # Update UI display
        w = self.widgets[tname]
        w["entry"].delete(0, tk.END)
        w["entry"].insert(0, str(liters))
        w["arm_label"].config(text=f"Arm: {arm:.2f} in")
        w["kg_label"].config(text=f"Weight: {kg:.1f} kg")

        self.update_summary()  # Update totals

    def update_summary(self):
        """
        Recalculates and displays the total fuel weight, moment, and CG.
        This handles the special logic for combined main tanks.
        """
        total_weight, total_moment = 0, 0

        # Check if BOTH main tanks have fuel to use the combined table
        main1_liters = self.state.get("Main Tank 1", {}).get("liters", 0)
        main2_liters = self.state.get("Main Tank 2", {}).get("liters", 0)
        main_liters = main1_liters + main2_liters
        combined_tank = next((t for t in self.tank_data if t.get("tank") == "main_tanks_combined_table"), None)

        # Use combined table ONLY when BOTH tanks have fuel (not just one)
        use_combined = (combined_tank is not None and main1_liters > 0 and main2_liters > 0)

        if use_combined:
            combined_arm = interpolate_arm(combined_tank["arm_table"], main_liters)
            combined_weight = round(main_liters * self.fuel_density, 1)

            # Store the combined calculation in the state
            self.state["Main Tanks Combined"] = {"liters": main_liters, "arm": combined_arm, "weight": combined_weight}
            total_weight += combined_weight
            total_moment += combined_weight * combined_arm
        else:
            # Clear combined entry if not using it
            if "Main Tanks Combined" in self.state:
                del self.state["Main Tanks Combined"]

        # Add all other tanks
        for tank in self.tank_data:
            tname = tank["tank"]
            if tname == "main_tanks_combined_table":
                continue  # Always skip the table itself
            if use_combined and tname in ("Main Tank 1", "Main Tank 2"):
                continue  # Skip individual main tanks when using combined

            tank_data = self.state.get(tname, {})
            weight = tank_data.get("weight", 0)
            arm = tank_data.get("arm", 0)
            total_weight += weight
            total_moment += weight * arm

        total_cg = total_moment / total_weight if total_weight > 0 else 0

        # Update display
        warning = ""
        # --- MODIFIED ---
        if total_weight > config.MAX_TOTAL_FUEL_KG:
            warning = f"\n!!! WARNING: Total fuel weight exceeds {config.MAX_TOTAL_FUEL_KG:,} kg !!!"
        # ---

        self.summary_label.config(
            text=f"Total Fuel: {total_weight:.1f} kg\nTotal Moment: {total_moment:.1f} kg-in\nFuel CG: {total_cg:.2f} in{warning}"
        )

        self._trigger_callback()

    def get_fuel_cg(self):
        """
        Calculates total fuel weight, moment, and CG.
        This is the primary method for the main app to get fuel load data.
        It mirrors the logic from update_summary() but only returns values.

        Returns:
            tuple (float, float, float):
                - total_weight (kg)
                - total_moment (kg-in)
                - cg (inches)
        """
        total_weight = 0
        total_moment = 0

        # Re-check combined tank logic
        main1_liters = self.state.get("Main Tank 1", {}).get("liters", 0)
        main2_liters = self.state.get("Main Tank 2", {}).get("liters", 0)
        combined_tank = next((t for t in self.tank_data if t.get("tank") == "main_tanks_combined_table"), None)
        use_combined = (combined_tank is not None and main1_liters > 0 and main2_liters > 0)

        if use_combined:
            # Use combined data from state
            combined = self.state.get("Main Tanks Combined", {})
            if combined:
                weight = combined.get("weight", 0)
                arm = combined.get("arm", 0)
                total_weight += weight
                total_moment += weight * arm

        # Add all other tanks
        for tank in self.tank_data:
            tname = tank["tank"]
            if tname == "main_tanks_combined_table":
                continue
            if use_combined and tname in ("Main Tank 1", "Main Tank 2"):
                continue  # Skip individual main tanks

            tank_data = self.state.get(tname, {})
            weight = tank_data.get("weight", 0)
            arm = tank_data.get("arm", 0)
            if weight > 0:
                total_weight += weight
                total_moment += weight * arm

        cg = total_moment / total_weight if total_weight > 0 else 0
        return total_weight, total_moment, cg

    def export_results(self):
        """Shows a message box with a summary of the current fuel load."""
        total_weight, total_moment, cg = self.get_fuel_cg()

        details = ""
        use_combined = "Main Tanks Combined" in self.state

        if use_combined:
            combined = self.state["Main Tanks Combined"]
            details += f"Main Tanks Combined: {combined.get('liters', 0)} L, {combined.get('weight', 0)} kg, Arm: {combined.get('arm', 0):.2f} in\n"

        # Export other tanks
        for tank, dat in self.state.items():
            if tank == "Main Tanks Combined":
                continue  # Already handled
            if use_combined and tank in ("Main Tank 1", "Main Tank 2"):
                continue  # Skip if using combined

            if dat.get("weight", 0) > 0:
                details += f"{tank}: {dat['liters']} L, {dat['weight']} kg, Arm: {dat['arm']:.2f} in\n"

        summary = (
            f"Fuel Results:\nTotal Weight: {total_weight:.1f} kg\nTotal Moment: {total_moment:.1f} kg-in\n"
            f"Fuel CG: {cg:.2f} in\n\n{details}"
        )
        messagebox.showinfo("Export Results", summary)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x400")

    try:
        # Load data using the new utility function and config path
        tank_data = load_json_data(config.FUEL_TANKS_FILEPATH)
        app = FuelLoadSystem(root, tank_data)
        root.mainloop()
    # Add some error handling for file not found
    except FileNotFoundError:
        messagebox.showerror("Error", f"Could not find fuel tanks file:\n{config.FUEL_TANKS_FILEPATH}")
        root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred loading the app:\n{e}")
        root.destroy()