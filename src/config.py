"""
This file contains all static configuration, constants, and file paths
for the 777-300ER Weight and Balance application.
"""

# --- File Paths ---
SEAT_MAP_FILEPATH = "../data/seat_map_new.json"
FUEL_TANKS_FILEPATH = "../data/fuel_tanks.json"
CARGO_POSITIONS_FILEPATH = "../data/cargo_positions.json"
AIRCRAFT_REFERENCE_FILEPATH = "../data/aircraft_reference.json"
LIMITS_FILEPATH = "../data/limits.json"

# --- Passenger Constants ---
BUSINESS_SEATPLAN = ["A", "C", None, "D", "F", None, "G", "J"]
ECONOMY_SEATPLAN = ["A", "B", None, "D", "E", "F", "G", "H", None, "J", "K"]
DEFAULT_PASSENGER_WEIGHT_KG = 88.5

# --- Fuel Constants ---
# Max fuel kg: (Main Tank 1 + Main Tank 2) + Center Tank
MAX_TOTAL_FUEL_KG = 33171 * 2 + 87887
DEFAULT_FUEL_DENSITY_KG_L = 0.8507

# --- Aircraft Physics & Index Constants ---
LE_MAC_IN = 1174.5
MAC_LENGTH_IN = 278.5
KLM_REFERENCE_ARM_IN = 1258
KLM_SCALE = 200000
KLM_OFFSET = 50

# --- CG Envelope Plotting Constants ---
CG_ENVELOPE_LOWER_POINTS = [
    (138573, 7.5), (204116, 7.5),
    (237682, 10.5), (251290, 11.5),
    (325996, 15.4), (345455, 17.8),
    (352441, 22.0), (352441, 27.4)
]
CG_ENVELOPE_UPPER_POINTS = [
    (138573, 26.9), (158031, 34.1),
    (224029, 44.0), (279911, 44.0), (304814, 44.0),
    (343414, 38.1), (352441, 27.4)
]