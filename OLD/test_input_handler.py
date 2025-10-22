from input_handler import FlightLoad

if __name__ == "__main__":
    load = FlightLoad()
    load.input_passengers()
    load.input_cargo()
    load.input_fuel()
    load.summary()
