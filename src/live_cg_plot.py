import matplotlib

matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import threading


class LiveCGPlot:
    def __init__(self):
        # Persistent trace data
        self.traces = {
            "passenger": {"x": [], "y": []},  # (%MAC, Weight)
            "cargo": {"x": [], "y": []},
            "fuel": {"x": [], "y": []}
        }
        # Lock for thread safety (if needed)
        self._lock = threading.Lock()

        # Figure setup
        self.fig, self.ax = plt.subplots(figsize=(7, 10))
        self.fig.canvas.manager.set_window_title("Live CG Trace - Boeing 777-300ER")

        self._setup_plot()

        # Initialize empty lines for each trace
        self.lines = {
            "passenger": self.ax.plot([], [], color='red', linewidth=2, label="Passengers")[0],
            "cargo": self.ax.plot([], [], color='green', linewidth=2, label="Cargo")[0],
            "fuel": self.ax.plot([], [], color='blue', linewidth=2, label="Fuel")[0]
        }
        # Black point markers for all points combined
        self.points = self.ax.scatter([], [], color='black', s=14, zorder=3, label="Intermediate updates")

        self.ax.legend()

        # Enable interactive mode and show figure
        plt.ion()
        plt.show(block=False)

    def _setup_plot(self):
        """Set up the CG envelope plot to match main program's plot perfectly."""
        # Draw certified envelope polygon
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

    def _refresh_plot(self):
        """Replot the traces and points."""
        with self._lock:
            # Update line data
            for key, data in self.traces.items():
                self.lines[key].set_data(data["x"], data["y"])

            # Aggregate all points for scatter plot
            all_x = []
            all_y = []
            for data in self.traces.values():
                all_x.extend(data["x"])
                all_y.extend(data["y"])
            self.points.set_offsets(np.column_stack((all_x, all_y)))

            # Redraw canvas
            self.fig.canvas.draw_idle()
            self.fig.canvas.flush_events()

    def update_trace(self, module_name, zfw_mac, zfw_weight, tow_mac, tow_weight):
        """
        Append new CG points for module and update plot in real-time.

        Parameters:
         - module_name: 'passenger', 'cargo', or 'fuel'
         - zfw_mac / tow_mac: percent MAC locations
         - zfw_weight / tow_weight: corresponding weights
        """
        if module_name not in self.traces:
            return
        with self._lock:
            self.traces[module_name]["x"].append(zfw_mac)
            self.traces[module_name]["y"].append(zfw_weight)
            self.traces[module_name]["x"].append(tow_mac)
            self.traces[module_name]["y"].append(tow_weight)

        self._refresh_plot()

    def reset_trace(self):
        """Clear all traces and refresh plot."""
        with self._lock:
            for key in self.traces:
                self.traces[key]["x"].clear()
                self.traces[key]["y"].clear()

        self._refresh_plot()

    def reset_module_trace(self, module_name, dow_mac, dow_weight):
        """Reset a specific module's trace back to DOW starting point."""
        if module_name not in self.traces:
            return
        with self._lock:
            self.traces[module_name]["x"] = [dow_mac]
            self.traces[module_name]["y"] = [dow_weight]
        self._refresh_plot()

    def close(self):
        """Close the plot window."""
        plt.close(self.fig)

    def initialize_aircraft_dow(self, dow_mac, dow_weight):
        """Initialize all traces with the dry operating weight point."""
        with self._lock:
            for key in self.traces:
                self.traces[key]["x"] = [dow_mac]
                self.traces[key]["y"] = [dow_weight]
        self._refresh_plot()


# Optional: simple test run if run standalone
if __name__ == "__main__":
    import time

    live_plot = LiveCGPlot()

    # Initialize with DOW
    live_plot.initialize_aircraft_dow(29.9, 170200)
    time.sleep(1)

    # Simulate incremental loading trace for passenger
    for i in range(20):
        x = 29.9 + i * 0.1
        y = 170200 + i * 2000
        live_plot.update_trace("passenger", x, y, x + 0.3, y + 1500)
        time.sleep(0.2)

    # Simulate deselection - reset passenger trace
    print("Resetting passenger trace...")
    live_plot.reset_module_trace("passenger", 29.9, 170200)
    time.sleep(1)

    # Simulate cargo trace
    for i in range(15):
        x = 30.5 - i * 0.1
        y = 170200 + i * 1500
        live_plot.update_trace("cargo", x, y, x + 0.15, y + 1300)
        time.sleep(0.3)

    # Fuel trace example
    for i in range(25):
        x = 29.0 + i * 0.15
        y = 210000 + i * 900
        live_plot.update_trace("fuel", x, y, x - 0.2, y + 1200)
        time.sleep(0.3)

    print("Live CG trace simulation done; close the plot window to end.")
    while plt.fignum_exists(live_plot.fig.number):
        plt.pause(0.5)