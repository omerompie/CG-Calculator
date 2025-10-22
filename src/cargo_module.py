import tkinter as tk
from tkinter import messagebox, simpledialog
import json


class CargoLoadSystem:
    def __init__(self, master, cargo_data, on_change_callback=None):
        self.master = master
        self.cargo_data = cargo_data
        self.state = {}  # track loaded weights per slot
        self.buttons = {}  # store buttons keyed by slot
        self.on_change_callback = on_change_callback  # callback on changes
        self.create_widgets()
        self.update_all_blocks()

    def create_widgets(self):
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

        # Figure out compartments and group container/pallet slots
        compartments = []
        for slot in self.cargo_data:
            if slot['compartment'] not in compartments:
                compartments.append(slot['compartment'])

        row_map = {}
        for comp in compartments:
            row_map[comp] = {'containers': [], 'pallets': []}
        for slot in self.cargo_data:
            ctype = 'pallets' if 'blocks' in slot else 'containers'
            row_map[slot['compartment']][ctype].append(slot)

        self.row_containers = 0
        self.row_pallets = 1
        col_index = 0

        for comp in compartments:
            compartment_label = tk.Label(self.slot_frame, text=f"{comp} Hold", font=("Arial", 14, "bold"))
            compartment_label.grid(row=0, column=col_index, padx=20, sticky='w', columnspan=2)

            for slot in row_map[comp]['containers']:
                self._create_slot_widget(slot, self.row_containers, col_index)
                col_index += 1
            cont_len = len(row_map[comp]['containers'])
            for i, slot in enumerate(row_map[comp]['pallets']):
                self._create_slot_widget(slot, self.row_pallets, col_index - cont_len + i)
            col_index += 2

        # Added End button for export
        tk.Button(self.frame, text="Load Max Weight to All (Containers only)", command=self.load_max_all).pack(pady=10)
        tk.Button(self.frame, text="End & Export Results", command=self.export_results).pack(pady=10)
        tk.Button(self.frame, text="Deselect All", command=self.deselect_all).pack(pady=5)

        self.summary_label = tk.Label(self.frame, text="", font=("Arial", 12))
        self.summary_label.pack()

    def _create_slot_widget(self, slot, row, col):
        key = (slot["compartment"], slot["position"])

        container = tk.Frame(self.slot_frame, bd=1, relief="solid", padx=5, pady=5)
        container.grid(row=row + 2, column=col, padx=5, pady=5)

        pos_label = tk.Label(container, text=slot["position"], font=("Arial", 12))
        pos_label.pack()

        btn_max = tk.Button(container, text="Load Max", command=lambda k=key: self.load_max_weight(k))
        btn_max.pack(pady=3)

        btn_custom = tk.Button(container, text="Custom Load", command=lambda k=key: self.custom_weight_input(k))
        btn_custom.pack(pady=3)

        btn_load = tk.Button(container, text="Select/Deselect", width=12, command=lambda k=key: self.toggle_load(k))
        btn_load.pack(pady=3)

        self.buttons[key] = (btn_load, btn_max, btn_custom)

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_max_weight(self, key):
        slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
        allowed_ULDs = slot.get("allowed_ULDs", [])
        if not allowed_ULDs:
            messagebox.showwarning("No ULD", f"No allowed ULDs for {key[1]} in {key[0]}")
            return
        max_uld = allowed_ULDs[0]
        self.state[key] = {"weight": max_uld["max_kg"], "ULD_type": max_uld["type"]}
        self.update_all_blocks()
        if self.on_change_callback:
            self.on_change_callback()

    def custom_weight_input(self, key):
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
            return  # Cancelled
        weight = round(input_val, 1)
        if weight > max_uld['max_kg']:
            messagebox.showerror("Error", f"Weight exceeds max allowed ({max_uld['max_kg']} kg).")
            return
        self.state[key] = {"weight": weight, "ULD_type": max_uld["type"]}
        self.update_all_blocks()
        if self.on_change_callback:
            self.on_change_callback()

    def load_max_all(self):
        # Load only container slots max weight, skip pallets to avoid overlap conflict
        for slot in self.cargo_data:
            key = (slot['compartment'], slot['position'])
            if "blocks" in slot:
                # Skip pallet slots
                continue
            allowed_ULDs = slot.get("allowed_ULDs", [])
            if allowed_ULDs:
                max_uld = allowed_ULDs[0]
                self.state[key] = {"weight": max_uld["max_kg"], "ULD_type": max_uld["type"]}
            else:
                self.state[key] = None
        self.update_all_blocks()
        if self.on_change_callback:
            self.on_change_callback()

    def deselect_all(self):
        for slot in self.cargo_data:
            key = (slot['compartment'], slot['position'])
            self.state[key] = None
        self.update_all_blocks()
        if self.on_change_callback:
            self.on_change_callback()

    def toggle_load(self, key):
        if self.state.get(key):
            self.state[key] = None
        else:
            self.load_max_weight(key)
        self.update_all_blocks()
        if self.on_change_callback:
            self.on_change_callback()

    def update_all_blocks(self):
        blocked_keys = set()
        for key, load in self.state.items():
            if not load:
                continue
            slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
            if "blocks" in slot:
                for b in slot["blocks"]:
                    blocked_keys.add((slot['compartment'], b))
            else:
                for s in self.cargo_data:
                    if "blocks" in s and key in [(s['compartment'], p) for p in s["blocks"]]:
                        if self.state.get((s['compartment'], s['position'])):
                            blocked_keys.add(key)
                            break

        for key, (btn_load, btn_max, btn_custom) in self.buttons.items():
            if key in blocked_keys:
                btn_load.config(state=tk.DISABLED, bg="lightgray")
                btn_max.config(state=tk.DISABLED)
                btn_custom.config(state=tk.DISABLED)
            else:
                btn_load.config(state=tk.NORMAL, bg="SystemButtonFace")
                btn_max.config(state=tk.NORMAL)
                btn_custom.config(state=tk.NORMAL)
        for key, load in self.state.items():
            if load:
                btn_load, btn_max, btn_custom = self.buttons.get(key, (None, None, None))
                if btn_load:
                    btn_load.config(bg="limegreen", state=tk.NORMAL)
                    btn_max.config(state=tk.NORMAL)
                    btn_custom.config(state=tk.NORMAL)

        self.update_summary()

    def update_summary(self):
        total_weight = 0
        total_moment = 0
        for key, load in self.state.items():
            if not load:
                continue
            slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
            arm = slot.get("arm_in", 0)
            weight = load['weight']
            total_weight += weight
            total_moment += weight * arm
        cg = total_moment / total_weight if total_weight else 0
        self.summary_label.config(text=f"Total Cargo Weight: {total_weight:.1f} kg\n"
                                       f"Total Cargo Moment: {total_moment:.1f} kg-in\n"
                                       f"Cargo CG (arm): {cg:.2f} in")

    def get_cargo_cg(self):
        """Return (total_weight, total_moment, cg_arm_in) of loaded cargo."""
        total_weight = 0
        total_moment = 0
        for key, load in self.state.items():
            if not load:
                continue
            slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
            arm = slot.get("arm_in", 0)
            weight = load['weight']
            total_weight += weight
            total_moment += weight * arm
        cg = total_moment / total_weight if total_weight else 0
        return total_weight, total_moment, cg


    def export_results(self):
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
        print(total_weight)
        print(total_moment)
        print(cg)
        messagebox.showinfo("Export Results", summary)


def load_cargo_data():
    with open("../data/cargo_positions.json", "r") as f:
        return json.load(f)


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1000x400")
    cargo_data = load_cargo_data()
    app = CargoLoadSystem(root, cargo_data)
    root.mainloop()
