import tkinter as tk
from tkinter import simpledialog, messagebox
import json

class SeatSelector:
    BUSINESS_SEATPLAN = ["A", "C", None, "D", "F", None, "G", "J"]
    ECONOMY_SEATPLAN = ["A", "B", None, "D", "E", "F", "G", "H", None, "J", "K"]

    def __init__(self, master, seat_map, on_change_callback=None):
        self.master = master
        self.seat_map = seat_map
        self.selected = set()
        self.buttons = {}
        self.on_change_callback = on_change_callback
        self.create_widgets()

    def create_widgets(self):
        # Canvas setup with vertical scrollbar
        self.canvas = tk.Canvas(self.master)
        self.scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

        tk.Label(self.scrollable_frame, text="Select Seats", font=("Arial", 16, "bold")).grid(row=0, column=0,
                                                                                              columnspan=15, pady=12)

        current_class = None
        row_idx = 1

        for row_data in self.seat_map:
            # Check for class divider
            if current_class != row_data["class"]:
                if current_class is not None:
                    # Insert separator (thick line)
                    sep = tk.Frame(self.scrollable_frame, height=3, bd=1, relief='sunken', bg='black')
                    sep.grid(row=row_idx, column=0, columnspan=20, sticky="ew", pady=10)
                    row_idx += 1
                current_class = row_data["class"]

            # Label for row number
            tk.Label(self.scrollable_frame, text=f"Row {row_data['row']}", font=("Arial", 12)).grid(row=row_idx,
                                                                                                    column=0, padx=6,
                                                                                                    pady=6, sticky='w')

            seat_plan = self.BUSINESS_SEATPLAN if row_data["class"] == "F" else self.ECONOMY_SEATPLAN

            seats_present = {seat["seat"]: seat for seat in row_data["seats"]}

            col_idx = 1
            for seat in seat_plan:
                if seat is None:
                    # Aisle gap: visually distinct blank label
                    lbl = tk.Label(self.scrollable_frame, width=3, bg="#ccc")
                    lbl.grid(row=row_idx, column=col_idx, padx=5, pady=6)
                elif seat in seats_present:
                    btn = tk.Button(
                        self.scrollable_frame, text=seat, width=4, height=2, font=("Arial", 14),
                        bg='lightblue' if row_data["class"] == "F" else 'white',
                        command=lambda r=row_data['row'], s=seat: self.toggle_seat(r, s)
                    )
                    btn.grid(row=row_idx, column=col_idx, padx=5, pady=6)
                    self.buttons[(row_data['row'], seat)] = btn
                else:
                    # Empty seat position (no seat here)
                    lbl = tk.Label(self.scrollable_frame, width=4, height=2, bg="#eee")
                    lbl.grid(row=row_idx, column=col_idx, padx=5, pady=6)
                col_idx += 1

            # Select Row button
            tk.Button(self.scrollable_frame, text="Select Row", font=("Arial", 11),
                      command=lambda row=row_data['row']: self.select_row(row)).grid(row=row_idx, column=col_idx,
                                                                                     padx=8, pady=6)

            row_idx += 1

        # Control buttons below
        controls = tk.Frame(self.master)
        controls.grid(row=1, column=0, columnspan=2, pady=10, sticky='ew')

        tk.Button(controls, text="Select All", command=self.select_all, width=12).grid(row=0, column=0, padx=10)
        tk.Button(controls, text="Deselect All", command=self.deselect_all, width=12).grid(row=0, column=1, padx=10)
        tk.Button(controls, text="Select Row", command=self.prompt_select_row, width=12).grid(row=0, column=2, padx=10)
        tk.Button(controls, text="Select Seat Letter", command=self.prompt_select_seat_letter, width=12).grid(row=0,
                                                                                                              column=3,
                                                                                                              padx=10)
        tk.Button(controls, text="Done", command=self.done, width=12).grid(row=0, column=4, padx=10)

    def toggle_seat(self, row, seat):
        key = (row, seat)
        btn = self.buttons.get(key)
        if btn is None:
            return

        if key in self.selected:
            self.selected.remove(key)
            btn.config(relief='raised', bg='lightblue' if self.get_class(row) == 'F' else 'white')
        else:
            self.selected.add(key)
            btn.config(relief='sunken', bg='lime green')

        if self.on_change_callback:
            self.on_change_callback()

    def get_class(self, row):
        for r in self.seat_map:
            if r['row'] == row:
                return r['class']
        return None

    def select_all(self):
        for key, btn in self.buttons.items():
            self.selected.add(key)
            btn.config(relief='sunken', bg='lime green')

        if self.on_change_callback:
            self.on_change_callback()

    def deselect_all(self):
        for key, btn in self.buttons.items():
            self.selected.discard(key)
            btn.config(relief='raised', bg='lightblue' if self.get_class(key[0]) == 'F' else 'white')

        if self.on_change_callback:
            self.on_change_callback()

    def select_row(self, row):
        for key, btn in self.buttons.items():
            if key[0] == row:
                self.selected.add(key)
                btn.config(relief='sunken', bg='lime green')

        if self.on_change_callback:
            self.on_change_callback()

    def prompt_select_row(self):
        row_str = simpledialog.askstring("Select Row", "Enter row number to select:")
        if row_str and row_str.isdigit():
            self.select_row(int(row_str))

        if self.on_change_callback:
            self.on_change_callback()

    def prompt_select_seat_letter(self):
        letter = simpledialog.askstring("Select Seat Letter", "Enter seat letter to select:")
        if letter:
            letter = letter.upper()
            for key, btn in self.buttons.items():
                if key[1] == letter:
                    self.selected.add(key)
                    btn.config(relief='sunken', bg='lime green')

            if self.on_change_callback:
                self.on_change_callback()

    def done(self):
        if not self.selected:
            messagebox.showinfo("No Selection", "No seats selected!")
            return

        if self.on_change_callback:
            self.on_change_callback()

        # Calculate passenger weight and moment; default weight 88.5 kg
        total_weight, total_moment, cg = self.get_passenger_cg()
        seat_list = sorted(self.selected)

        summary = f"Passengers selected: {len(seat_list)}\n"
        summary += f"Total weight: {total_weight:.1f} kg\n"
        summary += f"Total moment: {total_moment:.1f} kg-in\n"
        summary += f"Passenger CG (arm): {cg:.2f} inches\n"
        summary += "\nSelected seats:\n" + ", ".join(f"Row {row} Seat {seat}" for row, seat in seat_list)

        messagebox.showinfo("Load Summary", summary)

        # Use a default passenger weight — you can later override this via summary or config
        PAX_WEIGHT = 88.5
        total_weight = 0
        total_moment = 0
        row_map = {r['row']: r for r in self.seat_map}
        for (row, seat) in self.selected:
            seats = row_map[row]['seats']
            arm = next((s['arm_in'] for s in seats if s['seat'] == seat), 0)
            total_weight += PAX_WEIGHT
            total_moment += PAX_WEIGHT * arm
        cg = total_moment / total_weight if total_weight > 0 else 0

        print(f"Total passenger weight: {total_weight:.2f} kg")
        print(f"Total passenger moment: {total_moment:.2f} kg-in")
        print(f"Passenger CG (arm): {cg:.2f} inches")
        return total_weight, total_moment, cg

    def get_passenger_cg(self, pax_weight=88.5):
        total_weight = 0
        total_moment = 0
        row_map = {r['row']: r for r in self.seat_map}
        for (row, seat) in self.selected:
            seats = row_map[row]['seats']
            arm = next((s['arm_in'] for s in seats if s['seat'] == seat), 0)
            total_weight += pax_weight
            total_moment += pax_weight * arm
        cg = total_moment / total_weight if total_weight > 0 else 0
        return total_weight, total_moment, cg


def load_seat_map_from_json(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


if __name__ == "__main__":
    root = tk.Tk()
    root.title("Boeing 777-300ER Seat Selector")
    root.geometry("1300x900")

    seat_map_data = load_seat_map_from_json("../data/seat_map_new.json")


    app = SeatSelector(root, seat_map_data)
    root.mainloop()

