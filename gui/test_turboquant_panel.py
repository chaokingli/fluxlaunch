#!/usr/bin/env python3
"""
Test script for TurboQuantPanel
"""

import sys
import os

# Add the llama directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import customtkinter as ctk
except ImportError:
    print("customtkinter not available - skipping GUI test")
    sys.exit(0)

from gui.turboquant_panel import TurboQuantPanel


def test_turboquant_panel():
    """Test TurboQuantPanel creation and basic functionality."""
    root = ctk.CTk()
    root.title("TurboQuant Panel Test")
    root.geometry("600x400")

    # Create panel with default VRAM (16GB)
    panel = TurboQuantPanel(root, initial_vram_gb=16)
    panel.pack(fill="x", padx=10, pady=10)

    # Test getting config
    config = panel.get_config()
    print("Initial config:", config)

    # Test setting config
    test_config = {"cache_type_k": "q8_0", "cache_type_v": "turbo4"}
    panel.set_config(test_config)
    new_config = panel.get_config()
    print("After set_config:", new_config)

    # Test recommendations
    rec_8gb = panel.get_recommended_config(8)
    rec_16gb = panel.get_recommended_config(16)
    rec_48gb = panel.get_recommended_config(48)
    print("8GB recommendation:", rec_8gb)
    print("16GB recommendation:", rec_16gb)
    print("48GB recommendation:", rec_48gb)

    # Verify expected defaults
    assert config.get("cache_type_k") == "q8_0"
    assert config.get("cache_type_v") == "turbo4"

    # Verify recommendations
    assert rec_8gb == {"cache_type_k": "q8_0", "cache_type_v": "turbo2"}
    assert rec_16gb == {"cache_type_k": "turbo4", "cache_type_v": "turbo4"}
    assert rec_48gb == {"cache_type_k": "turbo4", "cache_type_v": "turbo4"}

    print("All tests passed!")
    root.destroy()


if __name__ == "__main__":
    test_turboquant_panel()
