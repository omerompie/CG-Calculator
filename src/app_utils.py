"""
This file contains shared utility functions for the application,
such as loading data from files and plotting.
"""
import json
import matplotlib.pyplot as plt
import numpy as np
import src.config as config  # Import config for constants

def load_json_data(filepath):
    """
    Loads and returns data from a specified JSON file.

    Args:
        filepath (str): The relative or absolute path to the JSON file.

    Returns:
        dict or list: The parsed JSON data.

    Raises:
        FileNotFoundError: If the file cannot be found at the specified path.
        json.JSONDecodeError: If the file is not valid JSON.
    """
    with open(filepath, "r") as f:
        data = json.load(f)
    return data


def plot_cg_envelope(zfw_mac, zfw_weight, tow_mac, tow_weight):
    """
    Displays a static Matplotlib chart of the 777-300ER CG envelope
    with the calculated ZFW and TOW points plotted.

    Args:
        zfw_mac (float): The ZFW CG in %MAC.
        zfw_weight (float): The ZFW in kg.
        tow_mac (float): The TOW CG in %MAC.
        tow_weight (float): The TOW in kg.
    """
    # Load envelope points from config
    lower_points = config.CG_ENVELOPE_LOWER_POINTS
    upper_points = config.CG_ENVELOPE_UPPER_POINTS

    lower_weights, lower_mac = zip(*lower_points)
    upper_weights, upper_mac = zip(*upper_points)
    X_poly = list(lower_mac) + list(reversed(upper_mac))
    Y_poly = list(lower_weights) + list(reversed(upper_weights))

    plt.figure(figsize=(7, 10))
    plt.fill(X_poly, Y_poly, color='lightgray', alpha=0.7, label='Certified Envelope', zorder=1)
    plt.plot(lower_mac, lower_weights, 'black', lw=2)
    plt.plot(upper_mac, upper_weights, 'black', lw=2)

    # Plot the calculated points
    plt.scatter([zfw_mac], [zfw_weight], color='red', marker='o', s=100, zorder=3, label='ZFW CG')
    plt.scatter([tow_mac], [tow_weight], color='blue', marker='o', s=100, zorder=3, label='TOW CG')

    plt.xlabel("Center of Gravity (% MAC)")
    plt.ylabel("Gross Weight (kg)")
    plt.title("777-300ER Certified Center of Gravity Envelope")
    plt.xlim(5, 50)
    plt.ylim(130000, 380000)
    plt.xticks(np.arange(5, 55, 5))
    plt.yticks(np.arange(130000, 390000, 10000), rotation=45)
    plt.grid(axis='y', which='major', linestyle='--', alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()