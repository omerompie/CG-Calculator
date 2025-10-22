import tkinter as tk
from tkinter import messagebox
import json

class CargoLoadSystem:
    def __init__(self, master, cargo_data):
        self.master = master
        self.cargo_data = cargo_data
        self.state = {}  # slot load state
        self.buttons = {}  # slot buttons
        self.create_widgets()
        self.update_all_blocks()

    def create_widgets(self):
        self.master.title("Cargo Loading System")
        self.frame = tk.Frame(self.master)
        self.frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(self.frame, text="Cargo Loading Positions", font=("Arial", 16, "bold")).pack(pady=10)

        # Canvas with horizontal scrollbar
        self.canvas = tk.Canvas(self.frame, height=150)
        self.scrollbar = tk.Scrollbar(self.frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Horizontal frame inside canvas
        self.slot_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.slot_frame, anchor='nw')

        self.slot_frame.bind("<Configure>", self.on_frame_configure)

        # Create slot buttons horizontally, grouped by compartment
        current_compartment = None
        col = 0

        for slot in self.cargo_data:
            if slot["compartment"] != current_compartment:
                current_compartment = slot["compartment"]
                # Insert compartment label with some spacing
                label = tk.Label(self.slot_frame, text=f"{current_compartment} Hold", font=("Arial", 14, "bold"))
                label.grid(row=0, column=col, padx=20)
                col += 1

            pos_key = (slot["compartment"], slot["position"])

            # Create a frame per slot to hold label, button, max button
            sub_frame = tk.Frame(self.slot_frame, bd=1, relief="solid", padx=5, pady=5)
            sub_frame.grid(row=1, column=col, padx=5)

            # Position label
            tk.Label(sub_frame, text=slot["position"], font=("Arial", 12)).pack()

            # Load max button
            btn_max = tk.Button(sub_frame, text="Load Max",
                          command=lambda k=pos_key: self.load_max_weight(k))
            btn_max.pack(pady=3)

            # Normal slot button (grayed when blocked, lime when loaded)
            btn_slot = tk.Button(sub_frame, text="Select", width=7,
                                command=lambda k=pos_key: self.toggle_load(k))
            btn_slot.pack(pady=3)

            self.buttons[pos_key] = (btn_slot, btn_max)

            col += 1

        # Load all button
        tk.Button(self.frame, text="Load Max Weight to All", command=self.load_max_all).pack(pady=10)

        # Summary below
        self.summary_label = tk.Label(self.frame, text="", font=("Arial", 12), justify='left')
        self.summary_label.pack()

    def on_frame_configure(self, event):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def load_max_weight(self, key):
        slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
        allowed_ULDs = slot.get("allowed_ULDs", [])
        if not allowed_ULDs:
            messagebox.showwarning("No ULDs", f"No allowed ULDs for {key[1]} in {key[0]}")
            return

        max_uld = allowed_ULDs[0]
        self.state[key] = {"weight": max_uld["max_kg"], "ULD_type": max_uld["type"]}
        self.update_all_blocks()

    def load_max_all(self):
        for slot in self.cargo_data:
            key = (slot['compartment'], slot['position'])
            allowed_ULDs = slot.get("allowed_ULDs", [])
            if allowed_ULDs:
                max_uld = allowed_ULDs[0]
                self.state[key] = {"weight": max_uld["max_kg"], "ULD_type": max_uld["type"]}
            else:
                self.state[key] = None
        self.update_all_blocks()

    def toggle_load(self, key):
        # If loaded, clear. Else load max weight for first ULD
        if self.state.get(key):
            self.state[key] = None
        else:
            self.load_max_weight(key)
        self.update_all_blocks()

    def update_all_blocks(self):
        blocked_keys = set()
        for key, load in self.state.items():
            if not load:
                continue
            slot = next(s for s in self.cargo_data if (s['compartment'], s['position']) == key)
            if "blocks" in slot:
                # Pallet blocks container slots
                for b in slot["blocks"]:
                    blocked_keys.add((slot['compartment'], b))
            else:
                # Container slots blocked by loaded pallets
                for s in self.cargo_data:
                    if "blocks" in s and key in [(s['compartment'], p) for p in s["blocks"]]:
                        if self.state.get((s['compartment'], s['position'])):
                            blocked_keys.add(key)
                            break

        # Update buttons
        for key, (btn_slot, btn_max) in self.buttons.items():
            if key in blocked_keys:
                btn_slot.config(state=tk.DISABLED, bg="lightgray")
                btn_max.config(state=tk.DISABLED)
            else:
                btn_slot.config(state=tk.NORMAL, bg="SystemButtonFace")
                btn_max.config(state=tk.NORMAL)

        # Highlight loaded buttons
        for key, load in self.state.items():
            if load:
                btn_slot, btn_max = self.buttons.get(key, (None, None))
                if btn_slot:
                    btn_slot.config(bg="limegreen", state=tk.NORMAL)
                    btn_max.config(state=tk.NORMAL)

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

def load_cargo_data():
    with open("../data/cargo_positions.json", "r") as f:
        return json.load(f)

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("900x300")
    cargo_data = load_cargo_data()
    app = CargoLoadSystem(root, cargo_data)
    root.mainloop()
