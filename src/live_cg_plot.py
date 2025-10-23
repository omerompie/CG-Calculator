"""
This module defines the LiveCGPlot class, which manages a real-time
Matplotlib window to visualize the 777-300ER's Center of Gravity (CG)
as items are loaded.
"""
import matplotlib
# Set the backend to TkAgg to integrate with the tkinter main app
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import numpy as np
import threading
from typing import List, Tuple

# Import configuration constants for the CG envelope
import src.config as config


class LiveCGPlot:
    """
    Manages a live Matplotlib window showing the 777-300ER CG envelope
    and the sequential loading trace (DOW -> +Pax -> ZFW -> TOW).

    This class is designed to be thread-safe, allowing updates from
    different threads (e.g., the main tkinter app).
    """

    def __init__(self):
        """Initializes the plot figure, axes, and all dynamic artists."""
        # handy feature, because if two UI buttons are clicked simultaneously, prevents race conditions when updating plot data.
        self._lock = threading.Lock()

        # --- Figure and Axis Setup ---
        self.fig: plt.Figure
        self.ax: plt.Axes
        self.fig, self.ax = plt.subplots(figsize=(7, 10))
        try:
            # Set the window title (may fail in some environments)
            self.fig.canvas.manager.set_window_title("Live CG Trace")
        except AttributeError:
            pass  # Not a critical failure

        # Draw the static CG envelope background
        self._setup_plot_envelope()

        # --- Define Dynamic Plot Artists ---
        # These artists (lines and scatters) will be updated with new data.

        # 1. Loading Lines (one for each loading step)
        self.line_pax = self.ax.plot(
            [], [],
            color='orange',
            linewidth=2.5,
            label="Passenger Load",
            zorder=4
        )[0]
        self.line_cargo = self.ax.plot(
            [], [],
            color='green',
            linewidth=2.5,
            label="Cargo Load",
            zorder=4
        )[0]
        self.line_fuel = self.ax.plot(
            [], [],
            color='blue',
            linewidth=2.5,
            label="Fuel Load",
            zorder=4
        )[0]

        # 2. Weight Points (one for each point type)
        self.scatter_intermediate = self.ax.scatter(
            [], [],
            color='black',
            s=50,
            zorder=5,
            label="Intermediate Points (DOW, +Pax)"
        )
        self.scatter_zfw = self.ax.scatter(
            [], [],
            color='red',
            marker='o',
            s=120,
            zorder=6,
            label="ZFW CG"
        )
        self.scatter_tow = self.ax.scatter(
            [], [],
            color='blue',
            marker='o',
            s=120,
            zorder=6,
            label="TOW CG"
        )

        self.ax.legend()

        # Enable interactive mode and show the plot without blocking
        plt.ion()
        plt.show(block=False)

    def _setup_plot_envelope(self):
        """
        Draws the static 777-300ER CG envelope on the plot's axes.
        Loads envelope boundary data from the src.config file.
        """
        # --- MODIFIED: Load from config, not hardcoded ---
        lower_points = config.CG_ENVELOPE_LOWER_POINTS
        upper_points = config.CG_ENVELOPE_UPPER_POINTS
        # ---

        # Unzip the points for plotting
        lower_weights, lower_mac = zip(*lower_points)
        upper_weights, upper_mac = zip(*upper_points)

        # Create coordinates for the filled polygon
        X_poly = list(lower_mac) + list(reversed(upper_mac))
        Y_poly = list(lower_weights) + list(reversed(upper_weights))

        # Draw the envelope polygon and its borders
        self.ax.fill(X_poly, Y_poly, color='lightgray', alpha=0.7, label='Certified Envelope', zorder=1)
        self.ax.plot(lower_mac, lower_weights, color='black', lw=2)
        self.ax.plot(upper_mac, upper_weights, color='black', lw=2)

        # --- Configure Plot Appearance ---
        self.ax.set_xlabel("Center of Gravity (% MAC)")
        self.ax.set_ylabel("Gross Weight (kg)")
        self.ax.set_title("777-300ER Certified Center of Gravity Envelope")
        self.ax.set_xlim(5, 50)
        self.ax.set_ylim(130000, 380000)
        self.ax.set_xticks(np.arange(5, 55, 5))
        self.ax.set_yticks(np.arange(130000, 390000, 10000))
        self.ax.set_yticklabels(np.arange(130000, 390000, 10000), rotation=45)
        self.ax.grid(axis='y', which='major', linestyle='--', alpha=0.5)

    def update_full_trace(self, trace_points: List[Tuple[float, float]]):
        """
        Updates the entire sequential loading trace with 4 new points.

        Args:
            trace_points: A list of 4 (mac, weight) tuples, representing:
                          [1] DOW (Dry Operating Weight)
                          [2] DOW + Passengers
                          [3] ZFW (Zero Fuel Weight)
                          [4] TOW (Takeoff Weight)
        """
        if not trace_points or len(trace_points) != 4:
            return  # Invalid data, do nothing

        # Deconstruct the 4 points for clarity
        p_dow = trace_points[0]  # Point 1: DOW
        p_pax = trace_points[1]  # Point 2: DOW + Pax
        p_zfw = trace_points[2]  # Point 3: ZFW
        p_tow = trace_points[3]  # Point 4: TOW

        # Acquire lock to safely update plot artists
        with self._lock:
            # 1. Update Passenger Line (DOW -> DOW+Pax)
            self.line_pax.set_data([p_dow[0], p_pax[0]], [p_dow[1], p_pax[1]])

            # 2. Update Cargo Line (DOW+Pax -> ZFW)
            self.line_cargo.set_data([p_pax[0], p_zfw[0]], [p_pax[1], p_zfw[1]])

            # 3. Update Fuel Line (ZFW -> TOW)
            self.line_fuel.set_data([p_zfw[0], p_tow[0]], [p_zfw[1], p_tow[1]])

            # 4. Update Intermediate Points (DOW, DOW+Pax)
            self.scatter_intermediate.set_offsets(np.array([p_dow, p_pax]))

            # 5. Update ZFW Point
            self.scatter_zfw.set_offsets(np.array([p_zfw]))

            # 6. Update TOW Point
            self.scatter_tow.set_offsets(np.array([p_tow]))

            # Redraw the canvas with the new data
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def reset_trace(self):
        """Clears all loading traces and points from the plot."""
        # Acquire lock to safely update plot artists
        with self._lock:
            # Clear all 3 lines
            self.line_pax.set_data([], [])
            self.line_cargo.set_data([], [])
            self.line_fuel.set_data([], [])

            # Clear all 3 scatter plots
            # Note: set_offsets requires an empty (0, 2) array
            empty_data = np.empty((0, 2))
            self.scatter_intermediate.set_offsets(empty_data)
            self.scatter_zfw.set_offsets(empty_data)
            self.scatter_tow.set_offsets(empty_data)

            # Redraw the empty canvas
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def close(self):
        """Closes the Matplotlib plot window."""
        plt.close(self.fig)


# Test harness to run this module standalone
if __name__ == "__main__":
    import time
    import os
    import sys

    # This allows the script to find and import `src.config`
    # when run directly (e.g., `python modules/live_cg_plot.py`).
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        sys.path.insert(0, parent_dir)
        import src.config
    # Add some error handling for file not found
    except (ImportError, FileNotFoundError):
        print("Error: Could not import src.config.")
        print("Please run this script from the project's root directory or ensure 'src' is in PYTHONPATH.")
        sys.exit(1)
    # ---

    print("Initializing Live CG Plot...")
    live_plot = LiveCGPlot()

    # Define 4 sample points for the trace
    dow = (29.9, 170200)      # Point 1
    dow_pax = (31.5, 195000)  # Point 2
    zfw = (30.8, 225000)      # Point 3
    tow = (28.5, 340000)      # Point 4

    # Simulate empty plot
    print("Showing empty plot (2s)...")
    time.sleep(2)

    # Simulate loading just DOW (e.g., on app startup)
    print("Showing DOW (2s)...")
    # All points are at the DOW position
    live_plot.update_full_trace([dow, dow, dow, dow])
    time.sleep(2)

    # Simulate adding passengers
    print("Showing DOW + Pax (2s)...")
    # DOW -> DOW+Pax. ZFW and TOW are also at the DOW+Pax position
    live_plot.update_full_trace([dow, dow_pax, dow_pax, dow_pax])
    time.sleep(2)

    # Simulate adding cargo (ZFW)
    print("Showing ZFW (2s)...")
    # DOW -> DOW+Pax -> ZFW. TOW is also at the ZFW position
    live_plot.update_full_trace([dow, dow_pax, zfw, zfw])
    time.sleep(2)

    # Simulate adding fuel (TOW)
    print("Showing full TOW (3s)...")
    # Full trace with all 4 unique points
    live_plot.update_full_trace([dow, dow_pax, zfw, tow])
    time.sleep(3)

    # Simulate resetting
    print("Resetting trace (2s)...")
    live_plot.reset_trace()
    time.sleep(2)

    # Show final trace again
    print("Showing full TOW again...")
    live_plot.update_full_trace([dow, dow_pax, zfw, tow])

    print("\nLive CG trace simulation done.")
    print("Close the 'Live CG Trace' plot window to end the script.")
    # Keep the script alive while the plot is open
    while plt.fignum_exists(live_plot.fig.number):
        try:
            plt.pause(0.5)
        except Exception:
            break