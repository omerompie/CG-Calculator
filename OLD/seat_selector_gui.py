import tkinter as tk
from tkinter import simpledialog, messagebox
from data.seat_map_new import seat_map

class SeatSelector:
    def __init__(self, master, seat_map):
        self.master = master
        self.seat_map = seat_map
        self.selected = set()
        self.buttons = {}
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self.master, bg="#f0f0f0")
        self.scrollbar = tk.Scrollbar(self.master, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg="#f0f0f0")
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

        tk.Label(self.scrollable_frame, text="Select Seats", font=("Arial", 16, "bold"), bg="#f0f0f0").grid(row=0, column=0, columnspan=15, pady=12)

        for i, row_data in enumerate(self.seat_map):
            row = row_data["row"]
            tk.Label(self.scrollable_frame, text=f"Row {row}", font=("Arial", 12), bg="#f0f0f0").grid(row=i + 1, column=0, padx=6, pady=6, sticky='w')
            if row_data["class"] == "F":
                seat_cols = ["A", "C", "D", "F", "G", "J"]
            else:
                seat_cols = ["A", "B", "C", "D", "E", "F", "G", "H", "J", "K"]
            seats_present = {seat["seat"]: seat for seat in row_data["seats"]}
            for idx, seat in enumerate(seat_cols):
                if seat in seats_present:
                    btn = tk.Button(
                        self.scrollable_frame, text=seat, width=5, height=2, font=("Arial", 15), state=tk.NORMAL,
                        command=(lambda r=row, s=seat: self.toggle_seat(r, s))
                    )
                    self.buttons[(row, seat)] = btn
                    btn.grid(row=i + 1, column=idx + 1, padx=4, pady=6)
                else:
                    tk.Label(self.scrollable_frame, text="", width=5, height=2, bg="#e0e0e0").grid(row=i + 1, column=idx + 1, padx=4, pady=6)
            tk.Button(
                self.scrollable_frame, text="Select Row", width=8, font=("Arial", 11),
                command=lambda current_row=row: self.select_row_direct(current_row)
            ).grid(row=i + 1, column=len(seat_cols) + 1, padx=6)

        controls_frame = tk.Frame(self.master)
        controls_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

        tk.Button(controls_frame, text="Select All", command=self.select_all, width=12).grid(row=0, column=0, padx=8)
        tk.Button(controls_frame, text="Deselect All", command=self.deselect_all, width=12).grid(row=0, column=1, padx=8)
        tk.Button(controls_frame, text="Select Row", command=self.select_row_prompt, width=12).grid(row=0, column=2, padx=8)
        tk.Button(controls_frame, text="Select Seat Letter", command=self.select_seat_letter_prompt, width=12).grid(row=0, column=3, padx=8)
        tk.Button(controls_frame, text="Done", command=self.done, width=12).grid(row=0, column=4, padx=8)

    def toggle_seat(self, row, seat):
        key = (row, seat)
        if key in self.selected:
            self.selected.remove(key)
            self.buttons[key].config(bg="SystemButtonFace")
        else:
            self.selected.add(key)
            self.buttons[key].config(bg="lightblue")

    def select_all(self):
        for key, btn in self.buttons.items():
            self.selected.add(key)
            btn.config(bg="lightblue")

    def deselect_all(self):
        for key, btn in self.buttons.items():
            self.selected.discard(key)
            btn.config(bg="SystemButtonFace")

    def select_row_prompt(self):
        row_str = simpledialog.askstring("Select Row", "Enter row number to select:")
        if row_str and row_str.isdigit():
            row = int(row_str)
            for (r, s), btn in self.buttons.items():
                if r == row:
                    self.selected.add((r, s))
                    btn.config(bg="lightblue")

    def select_seat_letter_prompt(self):
        seat_letter = simpledialog.askstring("Select Seat Letter", "Enter seat letter to select:")
        if seat_letter:
            seat_letter = seat_letter.upper()
            for (r, s), btn in self.buttons.items():
                if s == seat_letter:
                    self.selected.add((r, s))
                    btn.config(bg="lightblue")

    def select_row_direct(self, row):
        for (r, s), btn in self.buttons.items():
            if r == row:
                self.selected.add((r, s))
                btn.config(bg="lightblue")

    def calculate_passenger_weight_and_moment(self, standard_pax_weight=88.5):
        total_weight = 0
        total_moment = 0
        row_map = {row["row"]: row for row in self.seat_map}
        for (row, seat) in self.selected:
            seat_info = next(s for s in row_map[row]["seats"] if s["seat"] == seat)
            arm = seat_info["arm_in"]
            total_weight += standard_pax_weight
            total_moment += standard_pax_weight * arm
        cg = total_moment / total_weight if total_weight > 0 else 0

        print(f"Total passenger weight: {total_weight:.2f} kg")
        print(f"Total passenger moment: {total_moment:.2f} kg-in")
        print(f"Passenger CG (arm): {cg:.2f} in")
        return total_weight, total_moment, cg

    def done(self):
        if not self.selected:
            messagebox.showinfo("No selection", "No seats selected!")
            return
        print("Selected seats:", sorted(self.selected))
        total_weight, total_moment, cg = self.calculate_passenger_weight_and_moment()
        messagebox.showinfo(
            "Passenger Load Summary",
            f"Total Passenger Weight: {total_weight:.2f} kg\n"
            f"Total Passenger Moment: {total_moment:.2f} kg-in\n"
            f"Passenger CG (arm): {cg:.2f} in"
        )
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Full Cabin Seat Selector - Aligned")
    root.geometry("1800x900")
    app = SeatSelector(root, seat_map)
    root.mainloop()
