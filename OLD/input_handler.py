class FlightLoad:
    def __init__(self):
        self.passenger_distribution = {}  # {row_num: pax_count}
        self.cargo_distribution = {}  # {compartment: weight_kg}
        self.fuel_distribution = {}  # {tank: weight_kg}

    def input_passengers(self):
        print("Enter passenger counts per row: (type 'done' to finish)")
        while True:
            row = input("Row number (or 'done'): ")
            if row.lower() == 'done':
                break
            try:
                row_num = int(row)
                pax_count = int(input(f"Number of passengers in row {row_num}: "))
                self.passenger_distribution[row_num] = pax_count
            except ValueError:
                print("Please enter valid integers for row and passenger count.")

    def input_cargo(self):
        print("Enter cargo per compartment (type 'done' to finish):")
        while True:
            compartment = input("Compartment (or 'done'): ")
            if compartment.lower() == 'done':
                break
            try:
                weight = float(input(f"Weight in kg for {compartment}: "))
                self.cargo_distribution[compartment] = weight
            except ValueError:
                print("Please enter a valid number for weight.")

    def input_fuel(self):
        print("Enter fuel per tank (type 'done' to finish):")
        while True:
            tank = input("Tank name (or 'done'): ")
            if tank.lower() == 'done':
                break
            try:
                weight = float(input(f"Weight in kg for {tank}: "))
                self.fuel_distribution[tank] = weight
            except ValueError:
                print("Please enter a valid number for weight.")

    def summary(self):
        print("\nPassenger Distribution:", self.passenger_distribution)
        print("Cargo Distribution:", self.cargo_distribution)
        print("Fuel Distribution:", self.fuel_distribution)
