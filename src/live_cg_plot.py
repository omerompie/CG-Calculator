import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import threading


class LiveCGPlot:
    def __init__(self):
        # Lock for thread safety
        self._lock = threading.Lock()

        # Figure setup
        self.fig, self.ax = plt.subplots(figsize=(7, 10))
        self.fig.canvas.manager.set_window_title("Live CG Trace - Boeing 777-300ER")

        self._setup_plot()

        # --- MODIFIED: Three separate lines for each segment ---
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

        # --- MODIFIED: Three separate scatter plots for point types ---
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

        # Enable interactive mode and show figure
        plt.ion()
        plt.show(block=False)

    def _setup_plot(self):
        """Set up the CG envelope plot (unchanged)."""
        lower_points = [
            (138573, 7.5), (204116, 7.5),
            (237682, 10.5), (251290, 11.5),
            (325996, 15.4), (345455, 17.8),
            (352441, 22.0), (352441, 27.4)
        ]
        upper_points = [
            (138573, 26.9), (158031, 34.1),
            (224029, 44.0), (279911, 44.0), (304814, 44.0),
            (343414, 38.1), (352441, 27.4)
        ]

        lower_weights, lower_mac = zip(*lower_points)
        upper_weights, upper_mac = zip(*upper_points)

        X_poly = list(lower_mac) + list(reversed(upper_mac))
        Y_poly = list(lower_weights) + list(reversed(upper_weights))

        self.ax.fill(X_poly, Y_poly, color='lightgray', alpha=0.7, label='Certified Envelope', zorder=1)
        self.ax.plot(lower_mac, lower_weights, color='black', lw=2)
        self.ax.plot(upper_mac, upper_weights, color='black', lw=2)

        self.ax.set_xlabel("Center of Gravity (% MAC)")
        self.ax.set_ylabel("Gross Weight (kg)")
        self.ax.set_title("777-300ER Certified Center of Gravity Envelope")
        self.ax.set_xlim(5, 50)
        self.ax.set_ylim(130000, 380000)
        self.ax.set_xticks(np.arange(5, 55, 5))
        self.ax.set_yticks(np.arange(130000, 390000, 10000))
        self.ax.set_yticklabels(np.arange(130000, 390000, 10000), rotation=45)
        self.ax.grid(axis='y', which='major', linestyle='--', alpha=0.5)

    # --- MODIFIED: This method now updates all 6 plot artists ---
    def update_full_trace(self, trace_points):
        """
        Update the entire sequential loading trace.

        Parameters:
         - trace_points: A list of 4 (mac, weight) tuples.
                         [DOW, DOW+Pax, ZFW, TOW]
        """
        if not trace_points or len(trace_points) != 4:
            return

        # Deconstruct the 4 points
        p_dow = trace_points[0]
        p_pax = trace_points[1]
        p_zfw = trace_points[2]
        p_tow = trace_points[3]

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

            # Redraw canvas
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def reset_trace(self):
        """Clear all traces and points, then refresh plot."""
        with self._lock:
            # Clear all 3 lines
            self.line_pax.set_data([], [])
            self.line_cargo.set_data([], [])
            self.line_fuel.set_data([], [])

            # Clear all 3 scatter plots
            # set_offsets requires an empty (0, 2) array
            empty_data = np.empty((0, 2))
            self.scatter_intermediate.set_offsets(empty_data)
            self.scatter_zfw.set_offsets(empty_data)
            self.scatter_tow.set_offsets(empty_data)

            # Redraw canvas
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def close(self):
        """Close the plot window."""
        plt.close(self.fig)


# Optional: simple test run if run standalone
if __name__ == "__main__":
    import time

    live_plot = LiveCGPlot()

    # Define the 4 points
    dow = (29.9, 170200)
    dow_pax = (31.5, 195000)
    zfw = (30.8, 225000)
    tow = (28.5, 340000)

    # Simulate empty plot
    print("Showing empty plot...")
    time.sleep(2)

    # Simulate loading just DOW (e.g., on startup)
    print("Showing DOW...")
    # DOW is point 0, all other points are also DOW
    live_plot.update_full_trace([dow, dow, dow, dow])
    time.sleep(2)

    # Simulate adding passengers
    print("Showing DOW + Pax...")
    # DOW -> DOW+Pax (p_pax), ZFW and TOW are also at p_pax
    live_plot.update_full_trace([dow, dow_pax, dow_pax, dow_pax])
    time.sleep(2)

    # Simulate adding cargo (ZFW)
    print("Showing ZFW...")
    # DOW -> DOW+Pax -> ZFW (p_zfw), TOW is also at p_zfw
    live_plot.update_full_trace([dow, dow_pax, zfw, zfw])
    time.sleep(2)

    # Simulate adding fuel (TOW)
    print("Showing full TOW...")
    # Full trace with all 4 unique points
    live_plot.update_full_trace([dow, dow_pax, zfw, tow])
    time.sleep(3)

    # Simulate resetting
    print("Resetting trace...")
    live_plot.reset_trace()
    time.sleep(2)

    # Show final trace again
    print("Showing full TOW again...")
    live_plot.update_full_trace([dow, dow_pax, zfw, tow])

    print("Live CG trace simulation done; close the plot window to end.")
    while plt.fignum_exists(live_plot.fig.number):
        plt.pause(0.5)