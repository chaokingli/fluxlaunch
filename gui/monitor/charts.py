"""
Monitoring chart component for real-time RAM/VRAM/tokens/s visualization.
Uses matplotlib with blitting for performance and FigureCanvasTkAgg for CustomTkinter integration.
"""

import logging
from collections import deque
from typing import Dict, Optional

import matplotlib

matplotlib.use("TkAgg")  # Use TkAgg backend for GUI integration
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)


class MonitoringChart:
    """
    Real-time monitoring chart for RAM, VRAM, and tokens per second metrics.

    Features:
    - 3 subplots: RAM (MB), VRAM (MB), tokens/s
    - Blitting for performance optimization
    - Data buffering with configurable history length
    - CustomTkinter integration via FigureCanvasTkAgg
    - Thread-safe data updates

    Usage:
        chart = MonitoringChart(parent_frame)
        chart.update_data({'ram_mb': 1024.0, 'vram_mb': 2048.0, 'tokens_per_sec': 15.5})
    """

    def __init__(self, parent, buffer_size: int = 100):
        """
        Initialize the monitoring chart.

        Args:
            parent: Parent widget/frame for embedding the chart
            buffer_size: Maximum number of data points to keep in history (default: 100)
        """
        self.parent = parent
        self.buffer_size = buffer_size

        self._init_data_buffers()
        self._init_figure()
        self._init_canvas()

        # Blitting state
        self._blit_background = None
        self._artists_to_blit = []

        # Update state
        self._is_updating = False

        logger.info(f"MonitoringChart initialized with buffer_size={buffer_size}")

    def _init_data_buffers(self):
        """Initialize data buffers for each metric."""
        self.ram_data = deque(maxlen=self.buffer_size)
        self.vram_data = deque(maxlen=self.buffer_size)
        self.tokens_data = deque(maxlen=self.buffer_size)
        self.time_points = deque(maxlen=self.buffer_size)
        self._current_time = 0.0

    def _init_figure(self):
        """Initialize matplotlib figure with 3 subplots."""
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.ax_ram = self.figure.add_subplot(3, 1, 1)
        self.ax_vram = self.figure.add_subplot(3, 1, 2)
        self.ax_tokens = self.figure.add_subplot(3, 1, 3)

        self._configure_subplots()

    def _configure_subplots(self):
        """Configure subplot properties and labels."""
        self.ax_ram.set_ylabel("RAM (MB)")
        self.ax_ram.set_title("System RAM Usage")
        self.ax_ram.grid(True, alpha=0.3)
        (self.line_ram,) = self.ax_ram.plot([], [], "b-", linewidth=1.5, label="RAM")

        self.ax_vram.set_ylabel("VRAM (MB)")
        self.ax_vram.set_title("GPU VRAM Usage")
        self.ax_vram.grid(True, alpha=0.3)
        (self.line_vram,) = self.ax_vram.plot([], [], "r-", linewidth=1.5, label="VRAM")

        self.ax_tokens.set_ylabel("Tokens/s")
        self.ax_tokens.set_xlabel("Time (s)")
        self.ax_tokens.set_title("Tokens Per Second")
        self.ax_tokens.grid(True, alpha=0.3)
        (self.line_tokens,) = self.ax_tokens.plot(
            [], [], "g-", linewidth=1.5, label="Tokens/s"
        )

        self._artists_to_blit = [self.line_ram, self.line_vram, self.line_tokens]

    def _init_canvas(self):
        """Initialize FigureCanvasTkAgg for CustomTkinter integration."""
        self.canvas = FigureCanvasTkAgg(self.figure, self.parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

    def update_data(self, metrics: Dict[str, float]):
        """
        Update chart with new metrics data.

        Args:
            metrics: Dictionary with keys:
                - ram_mb: System RAM usage in MB
                - vram_mb: GPU VRAM usage in MB (can be None if not available)
                - tokens_per_sec: Tokens processed per second
        """
        if not self._is_updating:
            return

        try:
            self._current_time += 1.0

            self.time_points.append(self._current_time)
            self.ram_data.append(metrics.get("ram_mb", 0.0))

            vram_value = metrics.get("vram_mb", 0.0)
            if vram_value is None:
                vram_value = 0.0
            self.vram_data.append(vram_value)

            self.tokens_data.append(metrics.get("tokens_per_sec", 0.0))

            self._update_plot_data()
            self._blit_update()

        except Exception as e:
            logger.error(f"Error updating chart data: {e}")

    def _update_plot_data(self):
        """Update the plot line data with current buffers."""
        time_list = list(self.time_points)
        self.line_ram.set_data(time_list, list(self.ram_data))
        self.line_vram.set_data(time_list, list(self.vram_data))
        self.line_tokens.set_data(time_list, list(self.tokens_data))

        if time_list:
            x_min, x_max = min(time_list), max(time_list)
            self.ax_ram.set_xlim(x_min - 1, x_max + 1)
            self.ax_vram.set_xlim(x_min - 1, x_max + 1)
            self.ax_tokens.set_xlim(x_min - 1, x_max + 1)

            self._set_axis_limits()

    def _set_axis_limits(self):
        """Set appropriate y-axis limits based on current data."""
        if self.ram_data:
            ram_max = max(self.ram_data)
            self.ax_ram.set_ylim(0, ram_max * 1.1 if ram_max > 0 else 100)

        if self.vram_data:
            vram_max = max(self.vram_data)
            self.ax_vram.set_ylim(0, vram_max * 1.1 if vram_max > 0 else 100)

        if self.tokens_data:
            tokens_max = max(self.tokens_data)
            self.ax_tokens.set_ylim(0, tokens_max * 1.1 if tokens_max > 0 else 10)

    def _blit_update(self):
        """Perform blitting update for performance optimization."""
        if self._blit_background is None:
            self.canvas.draw()
            self._blit_background = self.canvas.copy_from_bbox(self.figure.bbox)

        self.canvas.restore_region(self._blit_background)

        for artist in self._artists_to_blit:
            artist.axes.draw_artist(artist)

        self.canvas.blit(self.figure.bbox)
        self.canvas.flush_events()

    def clear_data(self):
        """Clear all data buffers and reset the chart."""
        self._init_data_buffers()
        self._current_time = 0.0
        self._update_plot_data()
        self._blit_background = None
        self.canvas.draw()
        logger.info("MonitoringChart data cleared")

    def start_updating(self):
        """Start accepting data updates."""
        self._is_updating = True
        logger.info("MonitoringChart started updating")

    def stop_updating(self):
        """Stop accepting data updates."""
        self._is_updating = False
        logger.info("MonitoringChart stopped updating")

    def get_canvas(self):
        """Get the canvas widget for embedding in GUI."""
        return self.canvas.get_tk_widget()

    def destroy(self):
        """Clean up resources."""
        if hasattr(self, "canvas"):
            self.canvas.get_tk_widget().destroy()
        logger.info("MonitoringChart destroyed")


# Example usage for testing
if __name__ == "__main__":
    import tkinter as tk
    from customtkinter import CTk, CTkFrame

    logging.basicConfig(level=logging.INFO)

    root = CTk()
    root.title("Monitoring Chart Test")
    root.geometry("800x600")

    chart_frame = CTkFrame(root)
    chart_frame.pack(fill="both", expand=True, padx=10, pady=10)

    chart = MonitoringChart(chart_frame)
    chart.start_updating()

    def simulate_updates():
        import random

        test_data = {
            "ram_mb": random.uniform(1000, 4000),
            "vram_mb": random.uniform(500, 2000),
            "tokens_per_sec": random.uniform(5, 25),
        }
        chart.update_data(test_data)
        root.after(1000, simulate_updates)

    root.after(1000, simulate_updates)

    def on_closing():
        chart.destroy()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)

    root.mainloop()
