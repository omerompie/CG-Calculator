import tkinter as tk
from tkinter import messagebox, simpledialog
import json
import os

MAX_TOTAL_FUEL_KG = 33171 * 2 + 87887


def interpolate_arm(arm_table, fill_l):
    if fill_l <= arm_table[0][0]:
        return arm_table[0][1]
    if fill_l >= arm_table[-1][0]:
        return arm_table[-1][1]
    for i in range(1, len(arm_table)):
        if fill_l < arm_table[i][0]:
            l1, a1 = arm_table[i - 1]
            l2, a2 = arm_table[i]
            return a1 + (a2 - a1) * (fill_l - l1) / (l2 - l1)
    return arm_table[-1][1]


class FuelLoadSystem:
    def __init__(self, master, tank_data, on_change_callback=None):
        self.master = master
        self.tank_data = tank_data
        self.state = {}
        self.widgets = {}
        self.fuel_density = 0.8507
        self.on_change_callback = on_change_callback
        self.create_widgets()
        self.update_summary()

    def create_widgets(self):
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(self.frame, text="Fuel Loading by Tank", font=("Arial", 16, "bold")).pack(pady=10)

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

        btn_frame = tk.Frame(self.frame)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Set Fuel Density", command=self.set_density).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Deselect All", command=self.deselect_all).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="End & Export Results", command=self.export_results).pack(pady=10)

        self.summary_label = tk.Label(self.frame, text="Total: ...", font=("Arial", 13))
        self.summary_label.pack(pady=10)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def set_density(self):
        density = simpledialog.askfloat("Fuel Density",
                                        "Enter fuel density (kg/L) between 0.7309 and 0.8507:",
                                        minvalue=0.7309, maxvalue=0.8507,
                                        initialvalue=self.fuel_density)
        if density:
            self.fuel_density = density
            messagebox.showinfo("Density Set", f"Fuel density set to {density:.4f} kg/L")
            for tank in self.tank_data:
                tname = tank["tank"]
                if tname == "main_tanks_combined_table":
                    continue
                entry_val = self.widgets[tname]["entry"].get()
                try:
                    lit = float(entry_val)
                except:
                    lit = 0
                self.set_liters(tank, lit)

    def deselect_all(self):
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
        self.update_summary()

    def set_liters_popup(self, tank):
        max_l = tank["max_l"]
        val = simpledialog.askfloat("Fuel Amount", f"Enter liters for {tank['tank']} (max {max_l} L):",
                                    minvalue=0, maxvalue=max_l)
        if val is not None:
            self.set_liters(tank, val)

    def set_liters(self, tank, liters):
        liters = round(liters, 1)
        tname = tank["tank"]
        # Store liters; delay arm/weight calculation until final
        self.state[tname] = {"liters": liters}
        # Recalculate arm and weight immediately
        arm = interpolate_arm(tank["arm_table"], liters)
        kg = round(liters * self.fuel_density, 1)
        self.state[tname]["arm"] = arm
        self.state[tname]["weight"] = kg

        # update UI display
        w = self.widgets[tname]
        w["entry"].delete(0, tk.END)
        w["entry"].insert(0, str(liters))
        w["arm_label"].config(text=f"Arm: {arm:.2f} in")
        w["kg_label"].config(text=f"Weight: {kg:.1f} kg")
        self.update_summary()
        # Call callback if exists
        if hasattr(self, 'on_change_callback') and self.on_change_callback:
            self.on_change_callback()

    def update_summary(self):
        total_weight, total_moment = 0, 0

        # Check if BOTH main tanks have fuel - if so, use combined table
        main1_liters = self.state.get("Main Tank 1", {}).get("liters", 0)
        main2_liters = self.state.get("Main Tank 2", {}).get("liters", 0)
        main_liters = main1_liters + main2_liters
        combined_tank = next((t for t in self.tank_data if t.get("tank") == "main_tanks_combined_table"), None)

        # Use combined ONLY when BOTH tanks have fuel (not just one)
        use_combined = (combined_tank is not None and main1_liters > 0 and main2_liters > 0)

        if use_combined:
            # Use combined table for main tanks
            combined_arm = interpolate_arm(combined_tank["arm_table"], main_liters)
            combined_weight = round(main_liters * self.fuel_density, 1)
            self.state["Main Tanks Combined"] = {"liters": main_liters, "arm": combined_arm, "weight": combined_weight}
            total_weight += combined_weight
            total_moment += combined_weight * combined_arm
        else:
            # Clear combined entry if not using it
            if "Main Tanks Combined" in self.state:
                del self.state["Main Tanks Combined"]

        # Add all other tanks (skip main tanks if using combined, and always skip the table entry)
        for tank in self.tank_data:
            tname = tank["tank"]
            if tname == "main_tanks_combined_table":
                continue
            if use_combined and tname in ("Main Tank 1", "Main Tank 2"):
                continue  # Skip individual main tanks when using combined

            tank_data = self.state.get(tname, {})
            weight = tank_data.get("weight", 0)
            arm = tank_data.get("arm", 0)
            total_weight += weight
            total_moment += weight * arm

        # Calculate CG
        total_cg = total_moment / total_weight if total_weight > 0 else 0

        # Update display
        warning = ""
        if total_weight > MAX_TOTAL_FUEL_KG:
            warning = f"\n!!! WARNING: Total fuel weight exceeds {MAX_TOTAL_FUEL_KG:,} kg !!!"
        self.summary_label.config(
            text=f"Total Fuel: {total_weight:.1f} kg\nTotal Moment: {total_moment:.1f} kg-in\nFuel CG: {total_cg:.2f} in{warning}"
        )

        # Call callback
        if hasattr(self, 'on_change_callback') and self.on_change_callback:
            self.on_change_callback()

    def get_fuel_cg(self):
        """Calculate total fuel weight, moment, and CG."""
        total_weight = 0
        total_moment = 0

        # Check if BOTH main tanks have fuel - if so, use combined table
        main1_liters = self.state.get("Main Tank 1", {}).get("liters", 0)
        main2_liters = self.state.get("Main Tank 2", {}).get("liters", 0)
        main_liters = main1_liters + main2_liters
        combined_tank = next((t for t in self.tank_data if t.get("tank") == "main_tanks_combined_table"), None)

        # Use combined ONLY when BOTH tanks have fuel (not just one)
        use_combined = (combined_tank is not None and main1_liters > 0 and main2_liters > 0)

        if use_combined:
            # Use combined table for main tanks
            combined = self.state.get("Main Tanks Combined", {})
            if combined:
                total_weight += combined.get("weight", 0)
                total_moment += combined.get("weight", 0) * combined.get("arm", 0)

        # Add all other tanks (skip main tanks if using combined, and always skip the table entry)
        for tank in self.tank_data:
            tname = tank["tank"]
            if tname == "main_tanks_combined_table":
                continue
            if use_combined and tname in ("Main Tank 1", "Main Tank 2"):
                continue  # Skip individual main tanks when using combined

            tank_data = self.state.get(tname, {})
            weight = tank_data.get("weight", 0)
            arm = tank_data.get("arm", 0)
            if weight > 0:
                total_weight += weight
                total_moment += weight * arm

        cg = total_moment / total_weight if total_weight > 0 else 0
        return total_weight, total_moment, cg

    def export_results(self):
        total_weight, total_moment = 0, 0
        details = ""

        # Check if using combined tanks
        main1_liters = self.state.get("Main Tank 1", {}).get("liters", 0)
        main2_liters = self.state.get("Main Tank 2", {}).get("liters", 0)
        main_liters = main1_liters + main2_liters
        combined_tank = next((t for t in self.tank_data if t.get("tank") == "main_tanks_combined_table"), None)

        # Use combined ONLY when BOTH tanks have fuel
        use_combined = (combined_tank is not None and main1_liters > 0 and main2_liters > 0)

        if use_combined:
            combined = self.state.get("Main Tanks Combined", {})
            if combined:
                total_weight += combined.get("weight", 0)
                total_moment += combined.get("weight", 0) * combined.get("arm", 0)
                details += f"Main Tanks Combined: {combined.get('liters', 0)} L, {combined.get('weight', 0)} kg, Arm: {combined.get('arm', 0):.2f} in\n"

        # Export other tanks
        for tank, dat in self.state.items():
            if tank == "Main Tanks Combined":
                continue  # Already handled
            if use_combined and tank in ("Main Tank 1", "Main Tank 2"):
                continue  # Skip if using combined
            if dat.get("weight", 0) > 0:
                total_weight += dat["weight"]
                total_moment += dat["weight"] * dat["arm"]
                details += f"{tank}: {dat['liters']} L, {dat['weight']} kg, Arm: {dat['arm']:.2f} in\n"

        cg = total_moment / total_weight if total_weight else 0
        summary = (
            f"Fuel Results:\nTotal Weight: {total_weight:.1f} kg\nTotal Moment: {total_moment:.1f} kg-in\n"
            f"Fuel CG: {cg:.2f} in\n\n{details}"
        )
        messagebox.showinfo("Export Results", summary)


def load_fuel_data():
    with open(os.path.join("..", "data", "fuel_tanks.json"), "r") as f:
        return json.load(f)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x400")
    tank_data = load_fuel_data()
    app = FuelLoadSystem(root, tank_data)
    root.mainloop()