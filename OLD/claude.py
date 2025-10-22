import tkinter as tk
from tkinter import ttk, simpledialog, messagebox, scrolledtext
from typing import Dict, List, Tuple, Set
import json


class SeatMap777:
    """Parser for 777-300ER seat configuration"""

    def __init__(self, config_text: str):
        self.rows = []
        self.parse_config(config_text)

    def parse_config(self, config_text: str):
        lines = [l.strip() for l in config_text.strip().split('\n') if l.strip()]
        current_class = None

        for line in lines:
            if line in ['F', 'Y']:
                current_class = line
                continue

            parts = line.split()
            row_num = int(parts[0])

            # Parse triplets: left_count, left_arm, center_count, center_arm, right_count, right_arm
            left_count = int(parts[1])
            left_arm = int(parts[2]) if left_count > 0 else 0
            center_count = int(parts[3])
            center_arm = int(parts[4]) if center_count > 0 else 0
            right_count = int(parts[5])
            right_arm = int(parts[6]) if right_count > 0 else 0

            seats = []

            # Assign seat letters based on configuration
            if current_class == 'F':  # Business 2-2-2
                if left_count > 0:
                    seats.extend([{'seat': 'A', 'arm_in': left_arm}, {'seat': 'C', 'arm_in': left_arm}])
                if center_count > 0:
                    seats.extend([{'seat': 'D', 'arm_in': center_arm}, {'seat': 'F', 'arm_in': center_arm}])
                if right_count > 0:
                    seats.extend([{'seat': 'G', 'arm_in': right_arm}, {'seat': 'J', 'arm_in': right_arm}])
            else:  # Economy
                if left_count > 0:
                    if left_count == 2:
                        seats.extend([{'seat': 'A', 'arm_in': left_arm}, {'seat': 'C', 'arm_in': left_arm}])
                    elif left_count == 3:  # Special case like row 14
                        seats.extend([{'seat': 'A', 'arm_in': left_arm},
                                      {'seat': 'B', 'arm_in': left_arm},
                                      {'seat': 'C', 'arm_in': left_arm}])

                if center_count > 0:
                    if center_count == 5:  # Standard economy center
                        center_letters = ['D', 'E', 'F', 'G', 'H']
                    elif center_count == 4:  # Reduced center (rows 53-56)
                        center_letters = ['D', 'E', 'F', 'G']
                    else:
                        center_letters = ['D', 'E', 'F', 'G', 'H'][:center_count]

                    for letter in center_letters:
                        seats.append({'seat': letter, 'arm_in': center_arm})

                if right_count > 0:
                    seats.extend([{'seat': 'J', 'arm_in': right_arm}, {'seat': 'K', 'arm_in': right_arm}])

            self.rows.append({
                'row': row_num,
                'class': current_class,
                'seats': seats
            })


class EnhancedSeatSelector:
    def __init__(self, master, seat_map):
        self.master = master
        self.seat_map = seat_map
        self.selected = set()
        self.buttons = {}
        self.pax_weight = tk.DoubleVar(value=88.5)  # Standard passenger weight

        self.setup_ui()
        self.update_stats()

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.master, padding="5")
        main_frame.grid(row=0, column=0, sticky="nsew")

        # Control panel (top)
        self.create_control_panel(main_frame)

        # Seat map (center with scroll)
        self.create_seat_display(main_frame)

        # Statistics panel (right)
        self.create_stats_panel(main_frame)

        # Configure grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=0)
        main_frame.rowconfigure(1, weight=1)

    def create_control_panel(self, parent):
        control_frame = ttk.LabelFrame(parent, text="Controls", padding="5")
        control_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        # Weight input
        ttk.Label(control_frame, text="Pax Weight (kg):").grid(row=0, column=0, padx=5)
        ttk.Entry(control_frame, textvariable=self.pax_weight, width=10).grid(row=0, column=1, padx=5)

        # Preset weights
        ttk.Button(control_frame, text="Male (88.5)",
                   command=lambda: self.pax_weight.set(88.5)).grid(row=0, column=2, padx=2)
        ttk.Button(control_frame, text="Female (72)",
                   command=lambda: self.pax_weight.set(72)).grid(row=0, column=3, padx=2)
        ttk.Button(control_frame, text="Child (35)",
                   command=lambda: self.pax_weight.set(35)).grid(row=0, column=4, padx=2)

        # Selection buttons
        ttk.Separator(control_frame, orient='vertical').grid(row=0, column=5, padx=10, sticky='ns')
        ttk.Button(control_frame, text="Select All", command=self.select_all).grid(row=0, column=6, padx=2)
        ttk.Button(control_frame, text="Clear All", command=self.deselect_all).grid(row=0, column=7, padx=2)
        ttk.Button(control_frame, text="Select Row", command=self.select_row_prompt).grid(row=0, column=8, padx=2)
        ttk.Button(control_frame, text="Select Letter", command=self.select_seat_letter_prompt).grid(row=0, column=9,
                                                                                                     padx=2)

        # Export button
        ttk.Separator(control_frame, orient='vertical').grid(row=0, column=10, padx=10, sticky='ns')
        ttk.Button(control_frame, text="Generate Report", command=self.generate_report).grid(row=0, column=11, padx=2)

    def create_seat_display(self, parent):
        # Canvas with scrollbar
        canvas_frame = ttk.Frame(parent)
        canvas_frame.grid(row=1, column=0, sticky="nsew")

        self.canvas = tk.Canvas(canvas_frame, bg='white')
        scrollbar_y = ttk.Scrollbar(canvas_frame, orient="vertical", command=self.canvas.yview)
        scrollbar_x = ttk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)

        self.scrollable_frame = tk.Frame(self.canvas, bg='white')
        self.scrollable_frame.bind("<Configure>",
                                   lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")

        canvas_frame.columnconfigure(0, weight=1)
        canvas_frame.rowconfigure(0, weight=1)

        # Create seat map
        self.create_seats()

    def create_seats(self):
        # Header
        header_frame = tk.Frame(self.scrollable_frame, bg='white')
        header_frame.grid(row=0, column=0, sticky='ew', pady=(0, 10))

        tk.Label(header_frame, text="Boeing 777-300ER Seat Map",
                 font=('Arial', 14, 'bold'), bg='white').pack()
        tk.Label(header_frame, text="Blue=Business Class  |  White=Economy Class",
                 font=('Arial', 9), bg='white').pack()

        # Seat grid
        current_class = None
        display_row = 1

        for i, row_data in enumerate(self.seat_map):
            row = row_data["row"]
            row_class = row_data["class"]

            # Add class separator
            if row_class != current_class:
                separator = tk.Frame(self.scrollable_frame, height=2, bg='gray', relief='sunken')
                separator.grid(row=display_row, column=0, columnspan=20, sticky='ew', pady=5)
                display_row += 1

                class_label = tk.Label(self.scrollable_frame,
                                       text=f"{'BUSINESS CLASS' if row_class == 'F' else 'ECONOMY CLASS'}",
                                       font=('Arial', 10, 'bold'), bg='lightgray')
                class_label.grid(row=display_row, column=0, columnspan=20, sticky='ew', pady=2)
                display_row += 1
                current_class = row_class

            # Row number
            row_label = tk.Label(self.scrollable_frame, text=f"{row}",
                                 font=('Arial', 9, 'bold'), width=4, bg='white')
            row_label.grid(row=display_row, column=0, padx=5, sticky='w')

            # Determine seat layout
            if row_class == "F":
                seat_plan = ["A", "C", None, "D", "F", None, "G", "J"]
            else:
                # Check if row has special configuration
                seats_present = {seat["seat"] for seat in row_data["seats"]}
                if 'B' in seats_present:
                    seat_plan = ["A", "B", "C", None, "D", "E", "F", "G", "H", None, "J", "K"]
                elif 'H' not in seats_present and 'D' in seats_present:  # 2-4-2 or 0-4-0
                    if 'A' in seats_present:
                        seat_plan = ["A", "C", None, "D", "E", "F", "G", None, "J", "K"]
                    else:
                        seat_plan = [None, None, None, "D", "E", "F", "G", None, None, None]
                else:
                    seat_plan = ["A", "C", None, "D", "E", "F", "G", "H", None, "J", "K"]

            seats_present_dict = {seat["seat"]: seat for seat in row_data["seats"]}
            col_idx = 1

            for seat_letter in seat_plan:
                if seat_letter is None:
                    # Aisle gap
                    gap = tk.Label(self.scrollable_frame, text="", width=2, bg='white')
                    gap.grid(row=display_row, column=col_idx, padx=1)
                    col_idx += 1
                    continue

                enabled = seat_letter in seats_present_dict

                if enabled:
                    btn = tk.Button(
                        self.scrollable_frame,
                        text=seat_letter,
                        width=3,
                        height=1,
                        font=('Arial', 8, 'bold'),
                        bg='lightblue' if row_class == 'F' else 'white',
                        relief='raised',
                        command=lambda r=row, s=seat_letter: self.toggle_seat(r, s)
                    )
                    self.buttons[(row, seat_letter)] = btn
                else:
                    btn = tk.Label(self.scrollable_frame, text="", width=3, bg='lightgray')

                btn.grid(row=display_row, column=col_idx, padx=1, pady=1)
                col_idx += 1

            display_row += 1

    def create_stats_panel(self, parent):
        stats_frame = ttk.LabelFrame(parent, text="Load Statistics", padding="10")
        stats_frame.grid(row=1, column=1, sticky="nsew", padx=(5, 0))

        self.stats_text = tk.Text(stats_frame, width=30, height=20, font=('Courier', 9))
        self.stats_text.pack(fill='both', expand=True)

    def toggle_seat(self, row, seat):
        key = (row, seat)
        btn = self.buttons[key]

        if key in self.selected:
            self.selected.remove(key)
            # Restore original color based on class
            row_data = next(r for r in self.seat_map if r['row'] == row)
            original_color = 'lightblue' if row_data['class'] == 'F' else 'white'
            btn.config(bg=original_color, relief='raised')
        else:
            self.selected.add(key)
            btn.config(bg='lime green', relief='sunken')

        self.update_stats()

    def select_all(self):
        for key, btn in self.buttons.items():
            self.selected.add(key)
            btn.config(bg='lime green', relief='sunken')
        self.update_stats()

    def deselect_all(self):
        for key, btn in self.buttons.items():
            row = key[0]
            row_data = next(r for r in self.seat_map if r['row'] == row)
            original_color = 'lightblue' if row_data['class'] == 'F' else 'white'
            btn.config(bg=original_color, relief='raised')
        self.selected.clear()
        self.update_stats()

    def select_row_prompt(self):
        row_str = simpledialog.askstring("Select Row", "Enter row number:")
        if row_str and row_str.isdigit():
            row = int(row_str)
            for (r, s), btn in self.buttons.items():
                if r == row:
                    self.selected.add((r, s))
                    btn.config(bg='lime green', relief='sunken')
            self.update_stats()

    def select_seat_letter_prompt(self):
        seat_letter = simpledialog.askstring("Select Seat Letter", "Enter seat letter (A-K):")
        if seat_letter:
            seat_letter = seat_letter.upper()
            for (r, s), btn in self.buttons.items():
                if s == seat_letter:
                    self.selected.add((r, s))
                    btn.config(bg='lime green', relief='sunken')
            self.update_stats()

    def update_stats(self):
        if not self.selected:
            self.stats_text.delete('1.0', tk.END)
            self.stats_text.insert('1.0', "No seats selected\n\nSelect seats to see\nweight & balance data")
            return

        pax_weight = self.pax_weight.get()
        total_weight = 0
        total_moment = 0
        business_count = 0
        economy_count = 0

        row_map = {row["row"]: row for row in self.seat_map}

        for (row, seat) in self.selected:
            row_data = row_map[row]
            seat_info = next(s for s in row_data["seats"] if s["seat"] == seat)
            arm = seat_info["arm_in"]

            total_weight += pax_weight
            total_moment += pax_weight * arm

            if row_data['class'] == 'F':
                business_count += 1
            else:
                economy_count += 1

        cg = total_moment / total_weight if total_weight > 0 else 0

        # Display statistics
        stats = f"""PASSENGER LOAD SUMMARY
{'=' * 28}

Passengers: {len(self.selected)}
  Business:  {business_count}
  Economy:   {economy_count}

Weight per pax: {pax_weight:.1f} kg

TOTAL WEIGHT:   {total_weight:.1f} kg
TOTAL MOMENT:   {total_moment:.1f} kg-in
PASSENGER CG:   {cg:.2f} in

{'=' * 28}
Weight: {total_weight * 2.20462:.1f} lbs
Moment: {total_moment * 2.20462:.1f} lb-in
CG:     {cg * 0.0254:.3f} m
"""

        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert('1.0', stats)

    def generate_report(self):
        if not self.selected:
            messagebox.showinfo("No Selection", "Please select seats first!")
            return

        report_window = tk.Toplevel(self.master)
        report_window.title("Load Sheet Report")
        report_window.geometry("600x500")

        report_text = scrolledtext.ScrolledText(report_window, font=('Courier', 9))
        report_text.pack(fill='both', expand=True, padx=10, pady=10)

        # Generate detailed report
        pax_weight = self.pax_weight.get()
        total_weight = 0
        total_moment = 0

        report = f"""
{'=' * 60}
        BOEING 777-300ER - PASSENGER LOAD SHEET
{'=' * 60}

Total Passengers: {len(self.selected)}
Standard Weight:  {pax_weight} kg per passenger

SEAT LISTING:
{'-' * 60}
Row  Seat  Class    Arm (in)    Weight (kg)    Moment (kg-in)
{'-' * 60}
"""

        row_map = {row["row"]: row for row in self.seat_map}
        sorted_seats = sorted(self.selected)

        for (row, seat) in sorted_seats:
            row_data = row_map[row]
            seat_info = next(s for s in row_data["seats"] if s["seat"] == seat)
            arm = seat_info["arm_in"]
            moment = pax_weight * arm

            total_weight += pax_weight
            total_moment += moment

            class_name = "Business" if row_data['class'] == 'F' else "Economy"
            report += f"{row:3d}   {seat:3s}  {class_name:8s}  {arm:7.1f}    {pax_weight:8.2f}    {moment:12.2f}\n"

        cg = total_moment / total_weight if total_weight > 0 else 0

        report += f"""
{'-' * 60}
TOTALS:
  Total Weight:         {total_weight:10.2f} kg  ({total_weight * 2.20462:.2f} lbs)
  Total Moment:         {total_moment:10.2f} kg-in
  Passenger CG:         {cg:10.2f} in ({cg * 0.0254:.3f} m)
{'=' * 60}
"""

        report_text.insert('1.0', report)


def main():
    # Configuration data (paste your format here)
    config = """
F
1 2 213 2 206 0 0
2 2 251 2 244 2 233
3 2 289 2 282 2 271
4 2 327 2 320 2 309
5 2 365 2 358 2 347
6 2 403 2 396 2 385
7 2 441 2 434 2 423
Y
8 0 0 5 573 0 0
9 2 602 5 605 2 602
10 2 635 5 637 2 635
11 2 668 5 669 2 668
12 2 701 5 700 2 701
13 2 734 5 731 2 734
14 3 767 5 762 2 767
15 2 800 5 793 2 800
16 2 833 5 824 2 833
17 2 866 5 855 2 866
18 2 899 5 886 2 899
19 2 931 5 917 2 931
20 2 963 5 948 2 963
21 0 0 5 979 0 0
22 2 995 5 1010 2 995
23 2 1027 5 1041 2 1027
24 2 1059 5 1072 2 1059
25 2 1091 5 1103 2 1091
26 0 0 5 1192 0 0
27 2 1227 5 1224 2 1227
28 2 1259 5 1256 2 1259
29 2 1291 5 1288 2 1291
30 2 1323 5 1320 2 1323
31 2 1354 5 1352 2 1354
32 2 1385 5 1384 2 1385
33 2 1416 5 1416 2 1416
34 2 1447 5 1448 2 1447
35 2 1478 5 1480 2 1478
36 2 1509 5 1512 2 1509
37 2 1540 5 1544 2 1540
38 2 1571 5 1575 2 1571
39 2 1602 5 1606 2 1602
40 2 1633 5 1637 2 1633
41 2 1664 0 0 2 1664
42 2 1763 0 0 2 1763
43 2 1795 5 1798 2 1795
44 2 1827 5 1830 2 1827
45 2 1859 5 1862 2 1859
46 2 1891 5 1894 2 1891
47 2 1923 5 1926 2 1923
48 2 1955 5 1958 2 1955
49 2 1987 5 1990 2 1987
50 2 2019 5 2022 2 2019
51 2 2054 5 2053 2 2054
52 2 2086 5 2084 2 2086
53 2 2117 4 2116 2 2117
54 2 2149 4 2148 2 2149
55 2 2181 4 2180 2 2181
56 0 0 4 2212 0 0
"""

    # Parse configuration
    seat_map_obj = SeatMap777(config)

    # Create GUI
    root = tk.Tk()
    root.title("Boeing 777-300ER Load Planning System")
    root.geometry("1200x800")

    # Configure root grid
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)

    app = EnhancedSeatSelector(root, seat_map_obj.rows)
    root.mainloop()


if __name__ == "__main__":
    main()