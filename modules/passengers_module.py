import tkinter as tk
from tkinter import simpledialog, messagebox

import src.config as config
from src.app_utils import load_json_data


class SeatSelector:
    """
    A tkinter GUI module for visualizing and selecting aircraft seats,
    and calculating the resulting passenger weight and moment.
    """

    def __init__(self, master, seat_map, on_change_callback=None):
        """
        Initializes the SeatSelector widget.

        Args:
            master (tk.Widget): The parent tkinter widget.
            seat_map (list): The list of dictionaries defining the seat layout.
            on_change_callback (callable, optional): A function to call
                whenever the seat selection changes.
        """
        self.master = master
        self.seat_map = seat_map
        self.selected = set()  # Stores selected seats as (row, seat) tuples
        self.buttons = {}  # Maps (row, seat) tuples to their tk.Button widgets
        self.on_change_callback = on_change_callback
        self.create_widgets()

    def create_widgets(self):
        """Creates and lays out all tkinter widgets for the seat map."""
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

            # Get seat plan from config file
            seat_plan = config.BUSINESS_SEATPLAN if row_data["class"] == "F" else config.ECONOMY_SEATPLAN
            # ---

            seats_present = {seat["seat"]: seat for seat in row_data["seats"]}

            col_idx = 1
            for seat in seat_plan:
                if seat is None:
                    # Aisle gap
                    lbl = tk.Label(self.scrollable_frame, width=3, bg="#ccc")
                    lbl.grid(row=row_idx, column=col_idx, padx=5, pady=6)
                elif seat in seats_present:
                    # Seat button
                    btn = tk.Button(
                        self.scrollable_frame, text=seat, width=4, height=2, font=("Arial", 14),
                        bg='lightblue' if row_data["class"] == "F" else 'white',
                        command=lambda r=row_data['row'], s=seat: self.toggle_seat(r, s)
                    )
                    btn.grid(row=row_idx, column=col_idx, padx=5, pady=6)
                    self.buttons[(row_data['row'], seat)] = btn
                else:
                    # Empty seat position
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

    def _trigger_callback(self):
        """Safely triggers the on_change_callback if it exists."""
        if self.on_change_callback:
            self.on_change_callback()

    def toggle_seat(self, row, seat):
        """
        Toggles the selection state of a single seat.

        Args:
            row (int): The row number of the seat.
            seat (str): The seat letter (e.g., "A", "K").
        """
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

        self._trigger_callback()

    def get_class(self, row):
        """
        Finds the class ("F" or "Y") for a given row number.

        Args:
            row (int): The row number.

        Returns:
            str or None: The class identifier ("F", "Y") or None if not found.
        """
        for r in self.seat_map:
            if r['row'] == row:
                return r['class']
        return None

    def select_all(self):
        """Selects all available seats."""
        for key, btn in self.buttons.items():
            self.selected.add(key)
            btn.config(relief='sunken', bg='lime green')
        self._trigger_callback()

    def deselect_all(self):
        """Deselects all seats."""
        for key, btn in self.buttons.items():
            self.selected.discard(key)
            btn.config(relief='raised', bg='lightblue' if self.get_class(key[0]) == 'F' else 'white')
        self._trigger_callback()

    def select_row(self, row):
        """
        Selects all seats in a specific row.

        Args:
            row (int): The row number to select.
        """
        for key, btn in self.buttons.items():
            if key[0] == row:
                self.selected.add(key)
                btn.config(relief='sunken', bg='lime green')
        self._trigger_callback()

    def prompt_select_row(self):
        """Shows a dialog box to ask the user for a row number to select."""
        row_str = simpledialog.askstring("Select Row", "Enter row number to select:")
        if row_str and row_str.isdigit():
            self.select_row(int(row_str))
        self._trigger_callback()  # Trigger even if canceled

    def prompt_select_seat_letter(self):
        """Shows a dialog box to ask the user for a seat letter to select."""
        letter = simpledialog.askstring("Select Seat Letter", "Enter seat letter to select:")
        if letter:
            letter = letter.upper()
            for key, btn in self.buttons.items():
                if key[1] == letter:
                    self.selected.add(key)
                    btn.config(relief='sunken', bg='lime green')
            self._trigger_callback()

    def done(self):
        """
        Finalizes selection, triggers callback, and shows a summary message.
        This function is for UI interaction, not for external data retrieval.
        """
        if not self.selected:
            messagebox.showinfo("No Selection", "No seats selected!")
            return

        self._trigger_callback()

        # Calculate passenger weight and moment
        # Use the default passenger weight from config
        total_weight, total_moment, cg = self.get_passenger_cg(config.DEFAULT_PASSENGER_WEIGHT_KG)
        seat_list = sorted(self.selected)

        summary = f"Passengers selected: {len(seat_list)}\n"
        summary += f"Total weight: {total_weight:.1f} kg\n"
        summary += f"Total moment: {total_moment:.1f} kg-in\n"
        summary += f"Passenger CG (arm): {cg:.2f} inches\n"
        summary += "\nSelected seats:\n" + ", ".join(f"Row {row} Seat {seat}" for row, seat in seat_list)

        messagebox.showinfo("Load Summary", summary)

        # Print debug info
        print(f"Total passenger weight: {total_weight:.2f} kg")
        print(f"Total passenger moment: {total_moment:.2f} kg-in")
        print(f"Passenger CG (arm): {cg:.2f} inches")

    def get_passenger_cg(self, pax_weight=config.DEFAULT_PASSENGER_WEIGHT_KG):
        """
        Calculates the total weight, moment, and CG for all selected passengers.
        This is the primary method for the main app to get passenger load data.

        Args:
            pax_weight (float, optional): The weight to use for a single passenger.
                Defaults to DEFAULT_PASSENGER_WEIGHT_KG from config.

        Returns:
            tuple (float, float, float):
                - total_weight (kg)
                - total_moment (kg-in)
                - cg (inches)
        """
        total_weight = 0
        total_moment = 0

        # Create a quick-lookup map for row data
        row_map = {r['row']: r for r in self.seat_map}

        for (row, seat) in self.selected:
            if row in row_map:
                seats = row_map[row]['seats']
                # Find the arm for the specific seat in that row
                arm = next((s['arm_in'] for s in seats if s['seat'] == seat), 0)

                if arm == 0:
                    print(f"Warning: Could not find arm for seat {row}{seat}")

                total_weight += pax_weight
                total_moment += pax_weight * arm
            else:
                print(f"Warning: Could not find row data for row {row}")

        cg = total_moment / total_weight if total_weight > 0 else 0
        return total_weight, total_moment, cg

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Boeing 777-300ER Seat Selector")
    root.geometry("1300x900")

    try:
        # Load data using the new utility function and config path
        seat_map_data = load_json_data(config.SEAT_MAP_FILEPATH)
        app = SeatSelector(root, seat_map_data)
        root.mainloop()
    # Add some error handling for file not found
    except FileNotFoundError:
        messagebox.showerror("Error", f"Could not find seat map file:\n{config.SEAT_MAP_FILEPATH}")
        root.destroy()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred loading the app:\n{e}")
        root.destroy()