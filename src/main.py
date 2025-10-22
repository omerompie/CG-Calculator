import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib

# --- Local Imports ---
# UI Modules
from passengers_module import SeatSelector
from cargo_module import CargoLoadSystem
from fuel_load_module import FuelLoadSystem
from live_cg_plot import LiveCGPlot

# Utility & Calculation Modules
import config as config
import calculations as calc
import app_utils as utils

# --- End Local Imports ---

matplotlib.use('TkAgg')


# --- All global functions have been moved to calculations.py or app_utils.py ---

class AircraftSummaryApp:
    """
    Main application class. This class orchestrates the entire application,
    combining the UI modules (passengers, cargo, fuel) and calculating the
    final weight and balance summary.
    """

    def __init__(self, master):
        """
        Initializes the main application window.

        Args:
            master (tk.Tk): The root tkinter window.
        """
        self.master = master
        self.master.title("777-300ER: Full Aircraft Load Summary")

        # --- MODIFIED: Load data using utils and config ---
        try:
            self.weight_limits = utils.load_json_data(config.LIMITS_FILEPATH)
            self.aircraft_ref_data = utils.load_json_data(config.AIRCRAFT_REFERENCE_FILEPATH)

            # Load data for UI modules
            seat_map_data = utils.load_json_data(config.SEAT_MAP_FILEPATH)
            cargo_data = utils.load_json_data(config.CARGO_POSITIONS_FILEPATH)
            fuel_data = utils.load_json_data(config.FUEL_TANKS_FILEPATH)

        except FileNotFoundError as e:
            messagebox.showerror("Error", f"Failed to load data file: {e.filename}\nApplication will close.")
            master.destroy()
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during loading: {e}\nApplication will close.")
            master.destroy()
            return
        # ---

        # --- MODIFIED: Initialize runtime config from config.py defaults ---
        self.config = {
            "passenger_weight": config.DEFAULT_PASSENGER_WEIGHT_KG,
            "fuel_density": config.DEFAULT_FUEL_DENSITY_KG_L,
            "le_mac": config.LE_MAC_IN,
            "mac_length": config.MAC_LENGTH_IN,
            "klm_reference_arm": config.KLM_REFERENCE_ARM_IN
        }
        # ---

        self.dow_options = self.aircraft_ref_data["dow_options"]
        self.selected_reg = tk.StringVar()
        self.selected_reg.set(self.dow_options[0]["reg"])

        self._update_after_id = None

        # --- UI Setup ---
        self._build_ui_frames(master)

        # --- Initialize UI Modules ---
        self.seat_module = SeatSelector(self.pax_tab, seat_map_data)
        self.cargo_module = CargoLoadSystem(self.cargo_tab, cargo_data)
        self.fuel_module = FuelLoadSystem(self.fuel_tab, fuel_data)

        self._register_callbacks()

        # Initialize live plot
        self.live_plot = LiveCGPlot()

        self._build_summary_panel(self.main_frame)
        self.build_config_ui()

        # Initial calculation, force plot update to show DOW
        self.calculate_aircraft_summary(update_plot=True)

    def _build_ui_frames(self, master):
        """Helper method to create the main UI frames and notebook."""
        pick_frame = tk.Frame(master)
        pick_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)
        tk.Label(pick_frame, text="Select Aircraft (Reg):", font=("Arial", 12, "bold")).pack(side=tk.LEFT, padx=10)
        tk.OptionMenu(pick_frame, self.selected_reg, *(d["reg"] for d in self.dow_options)).pack(side=tk.LEFT, padx=4)
        tk.Button(pick_frame, text="Recalculate",
                  command=lambda: self.calculate_aircraft_summary(update_plot=True)).pack(side=tk.LEFT, padx=10)

        self.main_frame = tk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.pax_tab = tk.Frame(self.notebook)
        self.cargo_tab = tk.Frame(self.notebook)
        self.fuel_tab = tk.Frame(self.notebook)
        self.config_tab = tk.Frame(self.notebook)

        self.notebook.add(self.pax_tab, text="Passengers")
        self.notebook.add(self.cargo_tab, text="Cargo")
        self.notebook.add(self.fuel_tab, text="Fuel")
        self.notebook.add(self.config_tab, text="Config")

    def _build_summary_panel(self, parent_frame):
        """Helper method to create the right-hand summary panel."""
        self.summary_frame = tk.Frame(parent_frame, bd=2, relief='sunken', bg="#f4f4f4")
        self.summary_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=8, pady=8)

        tk.Button(self.summary_frame, text="Calculate Aircraft Summary",
                  command=lambda: self.calculate_aircraft_summary(update_plot=True), font=("Arial", 13)).pack(pady=10,
                                                                                                              padx=8,
                                                                                                              fill=tk.X)
        tk.Button(self.summary_frame, text="Show CG Envelope Chart",
                  command=self.show_cg_plot, font=("Arial", 12)).pack(pady=8, padx=8, fill=tk.X)
        tk.Button(self.summary_frame, text="Reset Live CG Trace",
                  command=self.live_plot.reset_trace, font=("Arial", 12)).pack(pady=8, padx=8, fill=tk.X)

        self.output_box = tk.Text(self.summary_frame, width=64, height=46, font=("Consolas", 11), bg="#f9f9f9")
        self.output_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

    def _register_callbacks(self):
        """Links the on_change_callback from each module to the main app."""
        self.seat_module.on_change_callback = self.on_load_change
        self.cargo_module.on_change_callback = self.on_load_change
        self.fuel_module.on_change_callback = self.on_load_change

    def build_config_ui(self):
        """Builds the configuration tab with all adjustable parameters."""
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

    def on_load_change(self):
        """
        Schedules a single update after a load change.
        This "debounces" rapid changes (e.g., holding a button).
        """
        if self._update_after_id:
            self.master.after_cancel(self._update_after_id)
        self._update_after_id = self.master.after(150, self._process_load_change)

    def _process_load_change(self):
        """
        The scheduled function that is called after a load change.
        It recalculates the summary and updates the live plot.
        """
        self._update_after_id = None
        self.calculate_aircraft_summary(update_plot=True)

    def apply_config_changes(self):
        """
        Applies runtime configuration changes from the 'Config' tab
        and recalculates the summary.
        """
        try:
            # Update runtime config from UI variables
            self.config["passenger_weight"] = self.passenger_weight_var.get()
            self.config["fuel_density"] = self.fuel_density_var.get()
            self.config["le_mac"] = self.le_mac_var.get()
            self.config["mac_length"] = self.mac_length_var.get()
            self.config["klm_reference_arm"] = self.klm_ref_arm_var.get()

            # --- Propagate changes to modules ---

            # Sync fuel density to fuel module
            self.fuel_module.fuel_density = self.config["fuel_density"]
            # Trigger recalculation in fuel module for all loaded tanks
            for tank in self.fuel_module.tank_data:
                tname = tank["tank"]
                if tname == "main_tanks_combined_table":
                    continue
                liters = self.fuel_module.state.get(tname, {}).get("liters", 0)
                if liters > 0:
                    self.fuel_module.set_liters(tank, liters)
                    # set_liters calls update_summary, which triggers on_load_change
                    # so we don't need to call it manually here.

        except ValueError as e:
            messagebox.showerror("Error", f"Invalid config input: {e}")
            return
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
            return

        messagebox.showinfo("Config Updated",
                            "Configuration values successfully updated.\nRecalculating aircraft summary...")

        # Force plot update after config change
        self.calculate_aircraft_summary(update_plot=True)

    def calculate_aircraft_summary(self, update_plot=False):
        """
        Performs the complete weight and balance calculation.
        This is the core logic of the application.

        Args:
            update_plot (bool, optional): If True, the live CG plot will be
                                          updated with the new 4-point trace.
        """
        reg = self.selected_reg.get()
        aircraft_ref = next((d for d in self.dow_options if d["reg"] == reg), self.dow_options[0])
        dow_weight = aircraft_ref["dow_weight_kg"]
        doi = aircraft_ref.get("doi", 0)

        # --- MODIFIED: Use calculation functions ---

        # Get DOW arm from DOI
        dow_arm = calc.calculate_arm_from_doi(
            doi, dow_weight, self.config["klm_reference_arm"]
        )
        dow_moment = dow_weight * dow_arm

        # Point 1: DOW
        dow_mac = calc.calculate_mac_percent(
            dow_arm, self.config["le_mac"], self.config["mac_length"]
        )

        # Get component loads from modules
        pax_weight, pax_moment, pax_cg = self.seat_module.get_passenger_cg(
            pax_weight=self.config["passenger_weight"])
        cargo_weight, cargo_moment, cargo_cg = self.cargo_module.get_cargo_cg()
        fuel_weight, fuel_moment, fuel_cg = self.fuel_module.get_fuel_cg()

        # Point 2: DOW + Passengers
        dow_pax_weight = dow_weight + pax_weight
        dow_pax_moment = dow_moment + pax_moment
        dow_pax_cg = dow_pax_moment / dow_pax_weight if dow_pax_weight > 0 else dow_arm
        dow_pax_mac = calc.calculate_mac_percent(
            dow_pax_cg, self.config["le_mac"], self.config["mac_length"]
        )

        # Point 3: ZFW (DOW + Pax + Cargo)
        zfw_weight = dow_pax_weight + cargo_weight
        zfw_moment = dow_pax_moment + cargo_moment
        zfw_cg = zfw_moment / zfw_weight if zfw_weight > 0 else dow_pax_cg
        zfw_mac = calc.calculate_mac_percent(
            zfw_cg, self.config["le_mac"], self.config["mac_length"]
        )

        # Point 4: TOW (ZFW + Fuel)
        tow_weight = zfw_weight + fuel_weight
        tow_moment = zfw_moment + fuel_moment
        tow_cg = tow_moment / tow_weight if tow_weight > 0 else zfw_cg
        tow_mac = calc.calculate_mac_percent(
            tow_cg, self.config["le_mac"], self.config["mac_length"]
        )
        # --- End Calculation Block ---

        # Update live plot with the new sequential trace
        if update_plot:
            trace_points = [
                (dow_mac, dow_weight),  # Point 1: DOW
                (dow_pax_mac, dow_pax_weight),  # Point 2: DOW + Pax
                (zfw_mac, zfw_weight),  # Point 3: ZFW
                (tow_mac, tow_weight)  # Point 4: TOW
            ]
            self.live_plot.update_full_trace(trace_points)

        # --- MODIFIED: Use calculation functions for Indices & Limits ---
        ref_arm = self.config["klm_reference_arm"]
        klm_dow = calc.klm_index(dow_weight, dow_arm, ref_arm)
        klm_pax = calc.klm_index(pax_weight, pax_cg, ref_arm)
        klm_car = calc.klm_index(cargo_weight, cargo_cg, ref_arm)
        klm_fuel = calc.klm_index(fuel_weight, fuel_cg, ref_arm)
        klm_all_zfw = klm_dow + klm_pax + klm_car
        klm_all_tow = klm_all_zfw + klm_fuel
        doi_value = aircraft_ref.get("doi", None)

        # Check limits
        breach_messages = calc.check_limits(zfw_weight, tow_weight, self.weight_limits)
        # --- End Modified Block ---

        limits_section = ""
        if breach_messages:
            limits_section += "\n*** LIMITS VIOLATED ***\n"
            for msg in breach_messages:
                limits_section += "- " + msg + "\n"
        else:
            limits_section += "\nAll gross weight limits within certified ranges.\n"

        # --- Build summary string ---
        summary_str = f"Selected Aircraft: {reg}\n\n"
        summary_str += "------ 777-300ER Aircraft Load Summary ------\n\n"
        summary_str += f"Operating (DOW):     {dow_weight:.1f} kg   @ {dow_arm:.2f} in (%MAC: {dow_mac:.2f})\n"
        summary_str += f"Passengers:          {pax_weight:.1f} kg   Moment: {pax_moment:.1f}\n"
        summary_str += f"Cargo:               {cargo_weight:.1f} kg   Moment: {cargo_moment:.1f}\n"
        summary_str += f"Fuel:                {fuel_weight:.1f} kg   Moment: {fuel_moment:.1f}\n\n"
        summary_str += f"ZERO FUEL WEIGHT:    {zfw_weight:.1f} kg   ZFW CG: {zfw_cg:.2f} in (%MAC: {zfw_mac:.2f})\n"
        summary_str += f"TAKEOFF WEIGHT:      {tow_weight:.1f} kg   TOW CG: {tow_cg:.2f} in (%MAC: {tow_mac:.2f})\n\n"
        summary_str += f"KLM INDEX (CGI) [ref {ref_arm} in]:\n"
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
        # --- End summary string ---

        self.output_box.delete("1.0", tk.END)
        self.output_box.insert(tk.END, summary_str)

        # Store last values for the static plot
        self._last_zfw_mac = zfw_mac
        self._last_zfw_weight = zfw_weight
        self._last_tow_mac = tow_mac
        self._last_tow_weight = tow_weight

    def show_cg_plot(self):
        """
        Displays the static CG envelope plot with the last calculated
        ZFW and TOW points.
        """
        if not hasattr(self, '_last_zfw_mac'):
            self.calculate_aircraft_summary(update_plot=False)

        # --- MODIFIED: Call function from utils ---
        utils.plot_cg_envelope(
            self._last_zfw_mac,
            self._last_zfw_weight,
            self._last_tow_mac,
            self._last_tow_weight,
        )
        # ---


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1900x1050")
    app = AircraftSummaryApp(root)
    root.mainloop()