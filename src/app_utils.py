"""
This file contains shared utility functions for the application,
such as loading data from files and plotting.
"""
import json
import matplotlib.pyplot as plt
import numpy as np
import src.config as config


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


def draw_cg_envelope_base(ax):
    """
    Draws the base 777-300ER CG envelope (certified envelope + restricted area)
    on a given matplotlib axis. This function is used by both the live plot
    and static plot to ensure consistency.

    This function draws:
    - The certified CG envelope (light grey)
    - The restricted area (darker grey with hatching)
    - Axis labels, limits, ticks, and grid

    Args:
        ax (matplotlib.axes.Axes): The axis to draw on.
    """
    # Load envelope points from config
    lower_points = config.CG_ENVELOPE_LOWER_POINTS
    upper_points = config.CG_ENVELOPE_UPPER_POINTS
    restricted_points = config.RESTRICTED_AREA_POINTS

    # Unzip the points for plotting
    lower_weights, lower_mac = zip(*lower_points)
    upper_weights, upper_mac = zip(*upper_points)

    # Create coordinates for the filled polygon (certified envelope)
    X_poly = list(lower_mac) + list(reversed(upper_mac))
    Y_poly = list(lower_weights) + list(reversed(upper_weights))

    # Draw the certified envelope
    ax.fill(X_poly, Y_poly, color='lightgray', alpha=0.7,
            label='Certified Envelope', zorder=1)
    ax.plot(lower_mac, lower_weights, color='black', lw=2)
    ax.plot(upper_mac, upper_weights, color='black', lw=2)

    # Draw the restricted area (darker grey overlay with hatching)
    if restricted_points and len(restricted_points) >= 3:
        restricted_weights, restricted_mac = zip(*restricted_points)
        ax.fill(restricted_mac, restricted_weights,
                color='darkgray', alpha=0.6,
                label='Restricted Area', zorder=2,
                hatch='///')  # Add hatching pattern for visual distinction

    # Configure plot appearance
    ax.set_xlabel("Center of Gravity (% MAC)")
    ax.set_ylabel("Gross Weight (kg)")
    ax.set_title("777-300ER Certified Center of Gravity Envelope")
    ax.set_xlim(5, 50)
    ax.set_ylim(130000, 380000)
    ax.set_xticks(np.arange(5, 55, 5))
    ax.set_yticks(np.arange(130000, 390000, 10000))
    ax.set_yticklabels(np.arange(130000, 390000, 10000), rotation=45)
    ax.grid(axis='y', which='major', linestyle='--', alpha=0.5)


def plot_cg_envelope(zfw_mac, zfw_weight, tow_mac, tow_weight):
    """
    Displays a static matplotlib chart of the 777-300ER CG envelope
    with the calculated ZFW and TOW points plotted.

    This plot shows ONLY the two final points (ZFW and TOW), not the full trace.

    Args:
        zfw_mac (float): The ZFW CG in %MAC.
        zfw_weight (float): The ZFW in kg.
        tow_mac (float): The TOW CG in %MAC.
        tow_weight (float): The TOW in kg.
    """
    fig, ax = plt.subplots(figsize=(7, 10))

    # Draw the base envelope (certified + restricted area)
    draw_cg_envelope_base(ax)

    # Plot only the two final points (ZFW and TOW)
    ax.scatter([zfw_mac], [zfw_weight],
              color='red', marker='o', s=100, zorder=3, label='ZFW CG')
    ax.scatter([tow_mac], [tow_weight],
              color='blue', marker='o', s=100, zorder=3, label='TOW CG')

    ax.legend()
    plt.tight_layout()
    plt.show()