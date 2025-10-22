import tkinter as tk
from tkinter import messagebox, simpledialog

# --- Local Imports ---
import src.config as config
from src.app_utils import load_json_data


# --- End Local Imports ---


class CargoLoadSystem:
    """
    A tkinter GUI module for managing cargo loads in ULD (Unit Load Device)
    slots, handling container/pallet blocking logic, and calculating
    the resulting cargo weight and moment.
    """

    def __init__(self, master, cargo_data, on_change_callback=None):
        """
        Initializes the CargoLoadSystem widget.

        Args:
            master (tk.Widget): The parent tkinter widget.
            cargo_data (list): The list of dictionaries defining cargo slots.
            on_change_callback (callable, optional): A function to call
                whenever the cargo load changes.
        """
        self.master = master
        self.cargo_data = cargo_data
        self.state = {}  # Tracks loaded weights {key: {"weight": w, "ULD_type": t}}
        self.buttons = {}  # Stores button widgets {key: (load_btn, max_btn, custom_btn)}
        self.on_change_callback = on_change_callback
        self.create_widgets()
        self.update_all_blocks()  # Initial update to set UI state

    def create_widgets(self):
        """Creates and lays out all tkinter widgets for the cargo holds."""
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="Cargo Loading Positions", font=("Arial", 16, "bold")).pack(pady=10)

        # Canvas with horizontal scrollbar
        self.canvas = tk.Canvas(self.frame, height=250)
        self.scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Inner frame for slots
        self.slot_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.slot_frame, anchor='nw')
        self.slot_frame.bind("<Configure>", self.on_frame_configure)

        # --- Organize slots by compartment and type (Container/Pallet) ---
        compartments = []
        for slot in self.cargo_data:
            if slot['compartment'] not in compartments:
                compartments.append(slot['compartment'])

        row_map = {}
        for comp in compartments:
            row_map[comp] = {'containers': [], 'pallets': []}
        for slot in self.cargo_data:
            # Pallets are identified by having a "blocks" key
            ctype = 'pallets' if 'blocks' in slot else 'containers'
            row_map[slot['compartment']][ctype].append(slot)
        # --- End Organization ---

        self.row_containers = 0
        self.row_pallets = 1
        col_index = 0

        # Create the UI grid
        for comp in compartments:
            compartment_label = tk.Label(self.slot_frame, text=f"{comp} Hold", font=("Arial", 14, "bold"))
            compartment_label.grid(row=0, column=col_index, padx=20, sticky='w', columnspan=2)

            for slot in row_map[comp]['containers']:
                self._create_slot_widget(slot, self.row_containers, col_index)
                col_index += 1

            cont_len = len(row_map[comp]['containers'])
            for i, slot in enumerate(row_map[comp]['pallets']):
                # Align pallet widgets under their corresponding containers
                self._create_slot_widget(slot, self.row_pallets, col_index - cont_len + i)

            col_index += 2  # Add spacing for the next compartment

        # Control buttons
        tk.Button(self.frame, text="Load Max Weight to All (Containers only)", command=self.load_max_all).pack(pady=10)
        tk.Button(self.frame, text="End & Export Results", command=self.export_results).pack(pady=10)
        tk.Button(self.frame, text="Deselect All", command=self.deselect_all).pack(pady=5)

        self.summary_label = tk.Label(self.frame, text="", font=("Arial", 12))
        self.summary_label.pack()

    def _create_slot_widget(self, slot, row, col):
        """Helper method to create the UI for a single cargo slot."""
        key = (slot["compartment"], slot["position"])

        container = tk.Frame(self.slot_frame, bd=1, relief="solid", padx=5, pady=5)
        container.grid(row=row + 2, column=col, padx=5, pady=5)  # +2 to be below headers

        pos_label = tk.Label(container, text=slot["position"], font=("Arial", 12))
        pos_label.pack()

        btn_max = tk.Button(container, text="Load Max", command=lambda k=key: self.load_max_weight(k))
        btn_max.pack(pady=3)

        btn_custom = tk.Button(container, text="Custom Load", command=lambda k=key: self.custom_weight_input(k))
        btn_custom.pack(pady=3)

        btn_load = tk.Button(container, text="Select/Deselect", width=12, command=lambda k=key: self.toggle_load(k))
        btn_load.pack(pady=3)

        self.buttons[key] = (btn_load, btn_max, btn_custom)

    def _trigger_callback(self):
        """Safely triggers the on_change_callback if it exists."""
        if self.on_change_callback:
            self.on_change_callback()

    def on_frame_configure(self, event):
        """Updates the canvas scroll region when the inner frame size changes."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_max_weight(self, key):
        """
        Loads the maximum weight for the default ULD in a specific slot.

        Args:
            key (tuple): (compartment, position) of the slot.
        """
        slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
        allowed_ULDs = slot.get("allowed_ULDs", [])
        if not allowed_ULDs:
            messagebox.showwarning("No ULD", f"No allowed ULDs for {key[1]} in {key[0]}")
            return

        max_uld = allowed_ULDs[0]  # Use the first ULD as default
        self.state[key] = {"weight": max_uld["max_kg"], "ULD_type": max_uld["type"]}
        self.update_all_blocks()
        self._trigger_callback()

    def custom_weight_input(self, key):
        """
        Opens a dialog to enter a custom weight for a specific slot.

        Args:
            key (tuple): (compartment, position) of the slot.
        """
        slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
        allowed_ULDs = slot.get("allowed_ULDs", [])
        if not allowed_ULDs:
            messagebox.showwarning("No ULD", f"No allowed ULDs for {key[1]} in {key[0]}")
            return

        max_uld = allowed_ULDs[0]
        input_val = simpledialog.askfloat("Custom Weight",
                                          f"Enter weight (kg) for slot {key[1]} (max {max_uld['max_kg']} kg):",
                                          minvalue=0, maxvalue=max_uld['max_kg'])
        if input_val is None:
            return  # User Cancelled

        weight = round(input_val, 1)
        # Note: simpledialog askfloat already enforces maxvalue
        self.state[key] = {"weight": weight, "ULD_type": max_uld["type"]}
        self.update_all_blocks()
        self._trigger_callback()

    def load_max_all(self):
        """Loads max weight to all CONTAINER slots. Skips pallet slots."""
        for slot in self.cargo_data:
            key = (slot['compartment'], slot['position'])
            if "blocks" in slot:
                continue  # Skip pallet slots

            allowed_ULDs = slot.get("allowed_ULDs", [])
            if allowed_ULDs:
                max_uld = allowed_ULDs[0]
                self.state[key] = {"weight": max_uld["max_kg"], "ULD_type": max_uld["type"]}
            else:
                self.state[key] = None  # No ULD, ensure it's empty

        self.update_all_blocks()
        self._trigger_callback()

    def deselect_all(self):
        """Clears all cargo slots."""
        self.state.clear()  # More efficient than looping
        self.update_all_blocks()
        self._trigger_callback()

    def toggle_load(self, key):
        """
        Toggles a slot between empty and max weight.

        Args:
            key (tuple): (compartment, position) of the slot.
        """
        if self.state.get(key):
            self.state[key] = None  # Deselect
        else:
            self.load_max_weight(key)  # Select (load max)

        self.update_all_blocks()
        self._trigger_callback()

    def update_all_blocks(self):
        """
        Updates the UI based on blocking logic.
        - Disables container slots if a pallet is loaded below them.
        - Disables pallet slots if a container is loaded above them.
        - Updates button colors for loaded slots.
        """
        blocked_keys = set()

        # Check for blocking
        for key, load in self.state.items():
            if not load:
                continue

            try:
                slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
            except StopIteration:
                continue  # Slot not found?

            if "blocks" in slot:
                # This is a PALLET. It blocks all containers listed in "blocks".
                for pos in slot["blocks"]:
                    blocked_keys.add((slot['compartment'], pos))
            else:
                # This is a CONTAINER. Check if it's blocked by any loaded pallet.
                for pallet_slot in self.cargo_data:
                    if "blocks" in pallet_slot and key[1] in pallet_slot["blocks"]:
                        # This container is part of a pallet's footprint
                        pallet_key = (pallet_slot['compartment'], pallet_slot['position'])
                        if self.state.get(pallet_key):
                            # The pallet is loaded, so this container is blocked
                            blocked_keys.add(key)
                            break

        # Update UI state for all buttons
        for key, (btn_load, btn_max, btn_custom) in self.buttons.items():
            load_data = self.state.get(key)

            if key in blocked_keys:
                # This slot is blocked by another
                btn_load.config(state=tk.DISABLED, bg="lightgray", text="Blocked")
                btn_max.config(state=tk.DISABLED)
                btn_custom.config(state=tk.DISABLED)
            elif load_data:
                # This slot is loaded
                btn_load.config(state=tk.NORMAL, bg="limegreen", text=f"{load_data['weight']} kg")
                btn_max.config(state=tk.NORMAL)
                btn_custom.config(state=tk.NORMAL)
            else:
                # This slot is empty and available
                btn_load.config(state=tk.NORMAL, bg="SystemButtonFace", text="Select/Deselect")
                btn_max.config(state=tk.NORMAL)
                btn_custom.config(state=tk.NORMAL)

        self.update_summary()

    def update_summary(self):
        """Recalculates and displays the total cargo weight, moment, and CG."""
        total_weight, total_moment, cg = self.get_cargo_cg()
        self.summary_label.config(text=f"Total Cargo Weight: {total_weight:.1f} kg\n"
                                       f"Total Cargo Moment: {total_moment:.1f} kg-in\n"
                                       f"Cargo CG (arm): {cg:.2f} in")

    def get_cargo_cg(self):
        """
        Calculates the total weight, moment, and CG for all loaded cargo.
        This is the primary method for the main app to get cargo load data.

        Returns:
            tuple (float, float, float):
                - total_weight (kg)
                - total_moment (kg-in)
                - cg (inches)
        """
        total_weight = 0
        total_moment = 0
        for key, load in self.state.items():
            if not load:
                continue

            try:
                slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
            except StopIteration:
                print(f"Warning: Slot data for {key} not found in get_cargo_cg")
                continue

            arm = slot.get("arm_in", 0)
            weight = load['weight']
            total_weight += weight
            total_moment += weight * arm

        cg = total_moment / total_weight if total_weight > 0 else 0
        return total_weight, total_moment, cg

    def export_results(self):
        """Shows a message box with a summary of the current cargo load."""
        total_weight, total_moment, cg = self.get_cargo_cg()
        detailed = ""
        for key, load in sorted(self.state.items()):
            if load:
                detailed += f"{key[0]} - Slot {key[1]}: {load['weight']} kg, ULD type: {load['ULD_type']}\n"

        summary = (
            f"Final Results:\n"
            f"Total Weight: {total_weight:.1f} kg\n"
            f"Total Moment: {total_moment:.1f} kg-in\n"
            f"CG (arm): {cg:.2f} in\n\n"
            f"Details:\n{detailed}"
        )
        messagebox.showinfo("Export Results", summary)


# --- Function REMOVED ---
# def load_cargo_data():
# ---

# --- MODIFIED ---
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x400")

    try:
        # Load data using the new utility function and config path
        cargo_data = load_json_data(config.CARGO_POSITIONS_FILEPATH)
        app = CargoLoadSystem(root, cargo_data)
        root.mainloop()
    except FileNotFoundError:
        messagebox.showerror("Error", f"Could not find cargo positions file:\n{config.CARGO_POSITIONS_FILEPATH}")
        root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred loading the app:\n{e}")
        root.destroy()