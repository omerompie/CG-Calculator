import json
from typing import Dict, Optional


class AircraftConfig:
    def __init__(self, aircraft_reference_file: str, limits_file: str):
        self.aircraft_reference_file = aircraft_reference_file
        self.limits_file = limits_file
        self.reference_data = {}
        self.limits_data = {}
        self.selected_dow_option = None

    def load_data(self):
        """Loads fixed aircraft reference data and limits from JSON files."""
        try:
            with open(self.aircraft_reference_file, 'r') as f:
                self.reference_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File {self.aircraft_reference_file} not found.")
        except json.JSONDecodeError:
            print(f"Error: File {self.aircraft_reference_file} contains invalid JSON.")

        try:
            with open(self.limits_file, 'r') as f:
                self.limits_data = json.load(f)
        except FileNotFoundError:
            print(f"Error: File {self.limits_file} not found.")
        except json.JSONDecodeError:
            print(f"Error: File {self.limits_file} contains invalid JSON.")

    def select_dow_option(self, reg_code: str) -> bool:
        """
        Selects a DOW option by aircraft registration code.
        Returns True if found and selected, False otherwise.
        """
        for option in self.reference_data.get("dow_options", []):
            if option.get("reg") == reg_code:
                self.selected_dow_option = option
                return True
        return False

    def get_selected_dow_weight(self) -> Optional[float]:
        """Returns the selected DOW weight in kg."""
        if self.selected_dow_option:
            return self.selected_dow_option.get("dow_weight_kg")
        return None

    def get_selected_dow_doi(self) -> Optional[float]:
        """Returns the selected DOW DOI percentage."""
        if self.selected_dow_option:
            return self.selected_dow_option.get("doi")
        return None

    def get_selected_fuel_factor(self) -> Optional[float]:
        """Returns the selected fuel factor percentage."""
        if self.selected_dow_option:
            return self.selected_dow_option.get("fuel_factor_percent")
        return None

    def get_lemac(self) -> float:
        """Returns the Leading Edge of Mean Aerodynamic Chord (LEMAC, inches)"""
        return self.reference_data.get("LEMAC_in", 0.0)

    def get_mac_length(self) -> float:
        """Returns the Mean Aerodynamic Chord length (inches)"""
        return self.reference_data.get("MAC_length_in", 0.0)

    def get_gross_weight_limit(self, weight_name: str) -> Optional[int]:
        """Returns a gross weight limit value from limits.json"""
        return self.limits_data.get(weight_name)

