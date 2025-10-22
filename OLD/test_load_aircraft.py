from data_loader import AircraftConfig


def test_select_dow():
    config = AircraftConfig('../data/aircraft_reference.json', '../data/limits.json')
    config.load_data()

    selected = config.select_dow_option('PH-BVA')
    if not selected:
        print("Failed to select DOW option PH-BVA")
        return

    print("Selected DOW Option: PH-BVA")
    print("DOW Weight (kg):", config.get_selected_dow_weight())
    print("DOI (%):", config.get_selected_dow_doi())
    print("Fuel Factor (%):", config.get_selected_fuel_factor())
    print("LEMAC (in):", config.get_lemac())
    print("MAC Length (in):", config.get_mac_length())

    # Example gross weight query
    print("MTOW (kg):", config.get_gross_weight_limit("MTOW_kg"))


if __name__ == "__main__":
    test_select_dow()
