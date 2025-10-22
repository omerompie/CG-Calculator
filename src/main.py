import tkinter as tk
from tkinter import ttk, messagebox
import json
import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np

from seat_selector_1 import SeatSelector
from cargo_1 import CargoLoadSystem
from fuel_load_module import FuelLoadSystem
from live_cg_plot import LiveCGPlot


def load_aircraft_reference(filepath="../data/aircraft_reference.json"):
    with open(filepath, "r") as f:
        return json.load(f)


def load_weight_limits(filepath="../data/limits.json"):
    with open(filepath, "r") as f:
        return json.load(f)


def klm_index(weight_kg, arm_in, reference_arm_in=1258, scale=200000, offset=50):
    return (weight_kg * (arm_in - reference_arm_in)) / scale + offset


def plot_cg_envelope(zfw_mac, zfw_weight, tow_mac, tow_weight):
    lower_points = [
        (138573, 7.5), (204116, 7.5),
        (237682, 10.5), (251290, 11.5),
        (325996, 15.4), (345455, 17.8),
        (352441, 22.0), (352441, 27.4)
    ]
    upper_points = [
        (138573, 26.9), (158031, 34.1),
        (224029, 44.0), (279911, 44.0), (304814, 44.0),
        (343414, 38.1), (352441, 27.4)
    ]
    lower_weights, lower_mac = zip(*lower_points)
    upper_weights, upper_mac = zip(*upper_points)
    X_poly = list(lower_mac) + list(reversed(upper_mac))
    Y_poly = list(lower_weights) + list(reversed(upper_weights))

    plt.figure(figsize=(7, 10))
    plt.fill(X_poly, Y_poly, color='lightgray', alpha=0.7, label='Certified Envelope', zorder=1)
    plt.plot(lower_mac, lower_weights, 'black', lw=2)
    plt.plot(upper_mac, upper_weights, 'black', lw=2)

    plt.scatter([zfw_mac], [zfw_weight], color='red', marker='o', s=100, zorder=3, label='ZFW CG')
    plt.scatter([tow_mac], [tow_weight], color='blue', marker='o', s=100, zorder=3, label='TOW CG')

    plt.xlabel("Center of Gravity (% MAC)")
    plt.ylabel("Gross Weight (kg)")
    plt.title("777-300ER Certified Center of Gravity Envelope")
    plt.xlim(5, 50)
    plt.ylim(130000, 380000)
    plt.xticks(np.arange(5, 55, 5))
    plt.yticks(np.arange(130000, 390000, 10000), rotation=45)
    plt.grid(axis='y', which='major', linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()


def check_limits(zfw_weight, tow_weight, limits):
    messages = []
    if zfw_weight > limits["MZFW_kg"]:
        over = zfw_weight - limits["MZFW_kg"]
        messages.append(
            f"Zero Fuel Weight ({zfw_weight:.1f} kg) exceeds Maximum ZFW ({limits['MZFW_kg']} kg) by {over:.1f} kg.")
    if tow_weight > limits["MTOW_kg"]:
        over = tow_weight - limits["MTOW_kg"]
        messages.append(
            f"Takeoff Weight ({tow_weight:.1f} kg) exceeds Maximum TOW ({limits['MTOW_kg']} kg) by {over:.1f} kg.")
    if tow_weight > limits["MTW_kg"]:
        over = tow_weight - limits["MTW_kg"]
        messages.append(
            f"Takeoff Weight ({tow_weight:.1f} kg) exceeds Maximum Taxi Weight ({limits['MTW_kg']} kg) by {over:.1f} kg.")
    if zfw_weight < limits["MFW_kg"]:
        under = limits["MFW_kg"] - zfw_weight
        messages.append(
            f"Zero Fuel Weight ({zfw_weight:.1f} kg) is below Minimum Flight Weight ({limits['MFW_kg']} kg) by {under:.1f} kg.")
    return messages


class AircraftSummaryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("777-300ER: Full Aircraft Load Summary")

        self.weight_limits = load_weight_limits()
        self.aircraft_ref_data = load_aircraft_reference()

        # Runtime config with fuel density included
        self.config = {
            "passenger_weight": 88.5,
            "fuel_density": 0.8507,
            "le_mac": 1174.5,
            "mac_length": 278.5,
            "klm_reference_arm": 1258
        }

        self.dow_options = self.aircraft_ref_data["dow_options"]
        self.selected_reg = tk.StringVar()
        self.selected_reg.set(self.dow_options[0]["reg"])

        # Track previous state for incremental live plot updates
        self._prev_state = {
            "pax_weight": 0, "cargo_weight": 0, "fuel_weight": 0,
            "zfw_mac": 0, "zfw_weight": 0, "tow_mac": 0, "tow_weight": 0
        }

        # UI setup
        pick_frame = tk.Frame(master)
        pick_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)
        tk.Label(pick_frame, text="Select Aircraft (Reg):", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        tk.OptionMenu(pick_frame, self.selected_reg, *(d["reg"] for d in self.dow_options)).pack(side=tk.LEFT, padx=4)
        tk.Button(pick_frame, text="Recalculate", command=self.calculate_aircraft_summary).pack(side=tk.LEFT, padx=10)

        main_frame = tk.Frame(master)
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.pax_tab = tk.Frame(self.notebook)
        self.cargo_tab = tk.Frame(self.notebook)
        self.fuel_tab = tk.Frame(self.notebook)
        self.config_tab = tk.Frame(self.notebook)

        self.notebook.add(self.pax_tab, text="Passengers")
        self.notebook.add(self.cargo_tab, text="Cargo")
        self.notebook.add(self.fuel_tab, text="Fuel")
        self.notebook.add(self.config_tab, text="Config")

        # Load module data with original relative paths
        with open("../data/seat_map_new.json", "r") as f:
            seat_map_data = json.load(f)
        with open("../data/cargo_positions.json", "r") as f:
            cargo_data = json.load(f)
        with open("../data/fuel_tanks.json", "r") as f:
            fuel_data = json.load(f)

        self.seat_module = SeatSelector(self.pax_tab, seat_map_data)
        self.cargo_module = CargoLoadSystem(self.cargo_tab, cargo_data)
        self.fuel_module = FuelLoadSystem(self.fuel_tab, fuel_data)

        self._update_after_id = None

        # Register callbacks after module initialization
        self.seat_module.on_change_callback = lambda: self.on_load_change("passenger")
        self.cargo_module.on_change_callback = lambda: self.on_load_change("cargo")
        self.fuel_module.on_change_callback = lambda: self.on_load_change("fuel")

        # Initialize live plot
        self.live_plot = LiveCGPlot()

        # Summary panel
        self.summary_frame = tk.Frame(main_frame, bd=2, relief='sunken', bg="#f4f4f4")
        self.summary_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        tk.Button(self.summary_frame, text="Calculate Aircraft Summary",
                  command=self.calculate_aircraft_summary, font=("Arial", 13)).pack(pady=10, padx=8, fill=tk.X)
        tk.Button(self.summary_frame, text="Show CG Envelope Chart",
                  command=self.show_cg_plot, font=("Arial", 12)).pack(pady=8, padx=8, fill=tk.X)
        tk.Button(self.summary_frame, text="Reset Live CG Trace",
                  command=self.live_plot.reset_trace, font=("Arial", 12)).pack(pady=8, padx=8, fill=tk.X)

        self.output_box = tk.Text(self.summary_frame, width=64, height=46, font=("Consolas", 11), bg="#f9f9f9")
        self.output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.build_config_ui()

        # Initial calculation
        self.calculate_aircraft_summary()

    def build_config_ui(self):
        """Build configuration tab with all adjustable parameters."""
        row = 0

        # Passenger Weight
        tk.Label(self.config_tab, text="Passenger Weight (kg)", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=6, pady=6)
        self.passenger_weight_var = tk.DoubleVar(value=self.config["passenger_weight"])
        tk.Entry(self.config_tab, textvariable=self.passenger_weight_var).grid(row=row, column=1, padx=6, pady=6)
        row += 1

        # Fuel Density
        tk.Label(self.config_tab, text="Fuel Density (kg/L)", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=6, pady=6)
        self.fuel_density_var = tk.DoubleVar(value=self.config["fuel_density"])
        fuel_entry = tk.Entry(self.config_tab, textvariable=self.fuel_density_var)
        fuel_entry.grid(row=row, column=1, padx=6, pady=6)
        tk.Label(self.config_tab, text="(0.7309 - 0.8507)", font=("Arial", 9), fg="gray").grid(
            row=row, column=2, sticky="w", padx=6)
        row += 1

        # LEMAC
        tk.Label(self.config_tab, text="LEMAC (inches)", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=6, pady=6)
        self.le_mac_var = tk.DoubleVar(value=self.config["le_mac"])
        tk.Entry(self.config_tab, textvariable=self.le_mac_var).grid(row=row, column=1, padx=6, pady=6)
        row += 1

        # MAC Length
        tk.Label(self.config_tab, text="MAC Length (inches)", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=6, pady=6)
        self.mac_length_var = tk.DoubleVar(value=self.config["mac_length"])
        tk.Entry(self.config_tab, textvariable=self.mac_length_var).grid(row=row, column=1, padx=6, pady=6)
        row += 1

        # KLM Reference Arm
        tk.Label(self.config_tab, text="KLM Ref Arm (inches)", font=("Arial", 11)).grid(
            row=row, column=0, sticky="w", padx=6, pady=6)
        self.klm_ref_arm_var = tk.DoubleVar(value=self.config["klm_reference_arm"])
        tk.Entry(self.config_tab, textvariable=self.klm_ref_arm_var).grid(row=row, column=1, padx=6, pady=6)
        row += 1

        # Apply button
        tk.Button(self.config_tab, text="Apply Changes", command=self.apply_config_changes,
                  font=("Arial", 12, "bold"), bg="#4CAF50", fg="white").grid(
            row=row, column=0, columnspan=3, pady=20, padx=10, sticky="ew")

    def on_load_change(self, module_name):
        """Schedule update with module identification."""
        if self._update_after_id:
            self.master.after_cancel(self._update_after_id)
        self._update_after_id = self.master.after(150, lambda: self._process_load_change(module_name))

    def _process_load_change(self, module_name):
        """Process load change and update only the affected module's trace."""
        self._update_after_id = None

        # Get current weights to detect deselection
        pax_weight, _, _ = self.seat_module.get_passenger_cg(pax_weight=self.config["passenger_weight"])
        cargo_weight, _, _ = self.cargo_module.get_cargo_cg()
        fuel_weight, _, _ = self.fuel_module.get_fuel_cg()

        prev = self._prev_state

        # Detect if weight decreased significantly (deselection) - reset that module's trace
        weight_decreased = False
        if module_name == "passenger" and pax_weight < prev["pax_weight"] * 0.9:
            weight_decreased = True
        elif module_name == "cargo" and cargo_weight < prev["cargo_weight"] * 0.9:
            weight_decreased = True
        elif module_name == "fuel" and fuel_weight < prev["fuel_weight"] * 0.9:
            weight_decreased = True

        if weight_decreased:
            # Reset this module's trace to DOW and rebuild from there
            reg = self.selected_reg.get()
            aircraft_ref = next((d for d in self.dow_options if d["reg"] == reg), self.dow_options[0])
            dow_weight = aircraft_ref["dow_weight_kg"]
            doi = aircraft_ref.get("doi", 0)
            scale = 200000
            offset = 50
            dow_arm = ((doi - offset) * scale / dow_weight) + self.config["klm_reference_arm"]
            dow_mac = ((dow_arm - self.config["le_mac"]) * 100 / self.config["mac_length"])

            # Reset only the affected module's trace
            self.live_plot.reset_module_trace(module_name, dow_mac, dow_weight)

        self.calculate_aircraft_summary(live_update_module=module_name)

    def apply_config_changes(self):
        """Apply configuration changes and sync with fuel module."""
        try:
            self.config["passenger_weight"] = self.passenger_weight_var.get()
            self.config["fuel_density"] = self.fuel_density_var.get()
            self.config["le_mac"] = self.le_mac_var.get()
            self.config["mac_length"] = self.mac_length_var.get()
            self.config["klm_reference_arm"] = self.klm_ref_arm_var.get()

            # Sync fuel density to fuel module
            if hasattr(self.fuel_module, 'fuel_density'):
                self.fuel_module.fuel_density = self.config["fuel_density"]
                # Trigger recalculation in fuel module
                for tank in self.fuel_module.tank_data:
                    tname = tank["tank"]
                    if tname == "main_tanks_combined_table":
                        continue
                    liters = self.fuel_module.state.get(tname, {}).get("liters", 0)
                    if liters > 0:
                        self.fuel_module.set_liters(tank, liters)

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid config input: {e}")
            return

        messagebox.showinfo("Config Updated",
                            "Configuration values successfully updated.\nRecalculating aircraft summary...")
        self.calculate_aircraft_summary()

    def calculate_aircraft_summary(self, live_update_module=None):
        """Calculate complete aircraft summary and optionally update live plot for specific module."""
        reg = self.selected_reg.get()
        aircraft_ref = next((d for d in self.dow_options if d["reg"] == reg), self.dow_options[0])
        dow_weight = aircraft_ref["dow_weight_kg"]
        doi = aircraft_ref.get("doi", 0)

        # Reverse calculate DOW arm from DOI using KLM index formula
        # DOI = (weight * (arm - ref_arm)) / scale + offset
        # Solving for arm: arm = ((DOI - offset) * scale / weight) + ref_arm
        scale = 200000
        offset = 50
        dow_arm = ((doi - offset) * scale / dow_weight) + self.config["klm_reference_arm"]
        dow_moment = dow_weight * dow_arm

        pax_weight, pax_moment, pax_cg = self.seat_module.get_passenger_cg(
            pax_weight=self.config["passenger_weight"])
        cargo_weight, cargo_moment, cargo_cg = self.cargo_module.get_cargo_cg()
        fuel_weight, fuel_moment, fuel_cg = self.fuel_module.get_fuel_cg()

        zfw_weight = dow_weight + pax_weight + cargo_weight
        zfw_moment = dow_moment + pax_moment + cargo_moment
        zfw_cg = zfw_moment / zfw_weight if zfw_weight > 0 else 0

        tow_weight = zfw_weight + fuel_weight
        tow_moment = zfw_moment + fuel_moment
        tow_cg = tow_moment / tow_weight if tow_weight > 0 else 0

        zfw_mac = ((zfw_cg - self.config["le_mac"]) * 100 / self.config["mac_length"]) if zfw_weight > 0 else 0
        tow_mac = ((tow_cg - self.config["le_mac"]) * 100 / self.config["mac_length"]) if tow_weight > 0 else 0

        # Update live plot only for the changed module
        if live_update_module:
            prev = self._prev_state
            if live_update_module == "passenger" and pax_weight != prev["pax_weight"]:
                self.live_plot.update_trace("passenger", zfw_mac, zfw_weight, tow_mac, tow_weight)
            elif live_update_module == "cargo" and cargo_weight != prev["cargo_weight"]:
                self.live_plot.update_trace("cargo", zfw_mac, zfw_weight, tow_mac, tow_weight)
            elif live_update_module == "fuel" and fuel_weight != prev["fuel_weight"]:
                self.live_plot.update_trace("fuel", zfw_mac, zfw_weight, tow_mac, tow_weight)

            # Update previous state
            self._prev_state.update({
                "pax_weight": pax_weight,
                "cargo_weight": cargo_weight,
                "fuel_weight": fuel_weight,
                "zfw_mac": zfw_mac,
                "zfw_weight": zfw_weight,
                "tow_mac": tow_mac,
                "tow_weight": tow_weight
            })

        # Calculate KLM indices
        klm_dow = klm_index(dow_weight, dow_arm, reference_arm_in=self.config["klm_reference_arm"])
        klm_pax = klm_index(pax_weight, pax_cg, reference_arm_in=self.config["klm_reference_arm"])
        klm_car = klm_index(cargo_weight, cargo_cg, reference_arm_in=self.config["klm_reference_arm"])
        klm_fuel = klm_index(fuel_weight, fuel_cg, reference_arm_in=self.config["klm_reference_arm"])
        klm_all_zfw = klm_dow + klm_pax + klm_car
        klm_all_tow = klm_all_zfw + klm_fuel
        doi_value = aircraft_ref.get("doi", None)

        # Check limits
        breach_messages = check_limits(zfw_weight, tow_weight, self.weight_limits)
        limits_section = ""
        if breach_messages:
            limits_section += "\n*** LIMITS VIOLATED ***\n"
            for msg in breach_messages:
                limits_section += "- " + msg + "\n"
        else:
            limits_section += "\nAll gross weight limits within certified ranges.\n"

        # Build summary
        summary_str = f"Selected Aircraft: {reg}\n\n"
        summary_str += "------ 777-300ER Aircraft Load Summary ------\n\n"
        summary_str += f"Operating (DOW):     {dow_weight:.1f} kg   @ {dow_arm:.2f} in\n"
        summary_str += f"Passengers:          {pax_weight:.1f} kg   Moment: {pax_moment:.1f}\n"
        summary_str += f"Cargo:               {cargo_weight:.1f} kg   Moment: {cargo_moment:.1f}\n"
        summary_str += f"Fuel:                {fuel_weight:.1f} kg   Moment: {fuel_moment:.1f}\n\n"
        summary_str += f"ZERO FUEL WEIGHT:    {zfw_weight:.1f} kg   ZFW CG: {zfw_cg:.2f} in (%MAC: {zfw_mac:.2f})\n"
        summary_str += f"TAKEOFF WEIGHT:      {tow_weight:.1f} kg   TOW CG: {tow_cg:.2f} in (%MAC: {tow_mac:.2f})\n\n"
        summary_str += f"KLM INDEX (CGI) [ref {self.config['klm_reference_arm']} in]:\n"
        summary_str += f"  ZFW Index:         {klm_all_zfw:.2f}\n"
        summary_str += f"  TOW Index:         {klm_all_tow:.2f}\n"
        if doi_value is not None:
            summary_str += f"  Certified DOW Index: {doi_value}\n"
        summary_str += "\nBreakdown (KLM Index):\n"
        summary_str += f"  DOW Index:         {klm_dow:.2f}\n"
        summary_str += f"  Pax Index:         {klm_pax:.2f}\n"
        summary_str += f"  Cargo Index:       {klm_car:.2f}\n"
        summary_str += f"  Fuel Index:        {klm_fuel:.2f}\n"
        summary_str += "\n---------------------------------------------\n"
        summary_str += limits_section

        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, summary_str)

        # Store for plot
        self._last_zfw_mac = zfw_mac
        self._last_zfw_weight = zfw_weight
        self._last_tow_mac = tow_mac
        self._last_tow_weight = tow_weight

    def show_cg_plot(self):
        """Display static CG envelope plot."""
        if not hasattr(self, '_last_zfw_mac'):
            self.calculate_aircraft_summary()
        plot_cg_envelope(
            self._last_zfw_mac,
            self._last_zfw_weight,
            self._last_tow_mac,
            self._last_tow_weight,
        )


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1900x1050")
    app = AircraftSummaryApp(root)
    root.mainloop()