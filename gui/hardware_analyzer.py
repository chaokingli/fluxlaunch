#!/usr/bin/env python3
"""
Hardware analyzer for detecting system hardware and providing parameter recommendations
for llama-server configuration.
"""

import psutil
import logging
from typing import Tuple, Dict, Optional

# Try to import pynvml for NVIDIA GPU detection
try:
    import pynvml

    NVIDIA_AVAILABLE = True
except ImportError:
    NVIDIA_AVAILABLE = False
    logging.warning("pynvml not available - NVIDIA GPU detection disabled")

logger = logging.getLogger(__name__)


class HardwareAnalyzer:
    """
    Analyzes system hardware and provides parameter recommendations for llama-server.

    This class detects CPU, RAM, and NVIDIA GPU (if available) and provides
    heuristic-based recommendations for server configuration parameters.
    """

    # Common model configurations for layer count estimation
    MODEL_CONFIGS = {
        "llama-3": {"layers": 32},
        "qwen2.5": {"layers": 64},
        # Add more models as needed
    }

    def __init__(self):
        """Initialize the hardware analyzer."""
        self._gpu_initialized = False
        if NVIDIA_AVAILABLE:
            try:
                pynvml.nvmlInit()
                self._gpu_initialized = True
            except pynvml.NVMLError as e:
                logger.warning(f"Failed to initialize NVML: {e}")
                self._gpu_initialized = False

    def detect_hardware(self) -> Tuple[str, float, float, int]:
        """
        Detect system hardware and return specifications.

        Returns:
            Tuple containing:
            - gpu_name: GPU name (empty string if not available)
            - vram_gb: Total VRAM in GB (0.0 if not available)
            - ram_gb: Total system RAM in GB
            - cpu_cores: Number of logical CPU cores
        """
        # Detect CPU cores and RAM
        cpu_cores = psutil.cpu_count(logical=True)
        ram_gb = psutil.virtual_memory().total / (1024**3)

        # Detect GPU (NVIDIA only for now)
        gpu_name = ""
        vram_gb = 0.0

        if self._gpu_initialized:
            try:
                device_count = pynvml.nvmlDeviceGetCount()
                if device_count > 0:
                    # Get info from the first GPU (or combine for multi-GPU)
                    total_vram = 0
                    gpu_names = []

                    for i in range(device_count):
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        gpu_name_i = pynvml.nvmlDeviceGetName(handle)
                        if isinstance(gpu_name_i, bytes):
                            gpu_name_i = gpu_name_i.decode("utf-8")
                        gpu_names.append(gpu_protect(gpu_name_i))

                        mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        total_vram += mem_info.total

                    # Use the first GPU name (or combine names for multi-GPU)
                    gpu_name = (
                        " + ".join(gpu_names) if len(gpu_names) > 1 else gpu_names[0]
                    )
                    vram_gb = total_vram / (1024**3)

            except pynvml.NVMLError as e:
                logger.warning(f"Error detecting GPU: {e}")
                gpu_name = ""
                vram_gb = 0.0

        return gpu_name, vram_gb, ram_gb, cpu_cores

    def recommend_params(
        self, model_size_gb: float, target_tps: float = 100.0
    ) -> Dict[str, any]:
        """
        Recommend server parameters based on hardware and model characteristics.

        Args:
            model_size_gb: Size of the model in GB
            target_tps: Target tokens per second (default: 100.0)

        Returns:
            Dictionary with recommended configuration parameters
        """
        gpu_name, vram_gb, ram_gb, cpu_cores = self.detect_hardware()

        # Basic recommendations
        params = {
            "threads": min(cpu_cores, 16),  # Cap at 16 threads for now
            "context_size": 4096,  # Default context size
            "batch_size": 512,  # Default batch size
            "gpu_layers": 0,  # Default to CPU-only
        }

        # GPU layer recommendation (heuristic-based)
        if vram_gb > 0 and model_size_gb > 0:
            # Estimate available VRAM for model layers (reserve 2GB for overhead)
            available_vram_for_model = max(0, vram_gb - 2.0)

            if available_vram_for_model > 0:
                # Determine model type and layer count
                layer_count = self._estimate_layer_count(model_size_gb)

                if layer_count > 0:
                    # Calculate how many layers can fit in available VRAM
                    # Formula: recommended_layers = (available_vram_for_model) / (model_size_gb / layer_count)
                    vram_per_layer = model_size_gb / layer_count
                    if vram_per_layer > 0:
                        recommended_layers = int(
                            available_vram_for_model / vram_per_layer
                        )
                        # Cap at actual layer count
                        params["gpu_layers"] = min(recommended_layers, layer_count)

        # Adjust batch size based on available memory
        if vram_gb > 0:
            # Scale batch size with VRAM (roughly)
            base_batch_size = 512
            batch_multiplier = min(vram_gb / 8.0, 4.0)  # Max 4x scaling
            params["batch_size"] = int(base_batch_size * batch_multiplier)
        else:
            # CPU-only: scale with RAM
            base_batch_size = 256
            batch_multiplier = min(ram_gb / 16.0, 2.0)  # Max 2x scaling
            params["batch_size"] = int(base_batch_size * batch_multiplier)

        # Adjust threads based on CPU cores
        params["threads"] = min(max(cpu_cores // 2, 1), 16)

        return params

    def _estimate_layer_count(self, model_size_gb: float) -> int:
        """
        Estimate the number of layers based on model size using common patterns.

        This is a heuristic estimation that works for common model families.

        Args:
            model_size_gb: Model size in GB

        Returns:
            Estimated number of layers
        """
        # Common model patterns
        # Llama-3 8B Q4_K_M: ~4.9GB, 32 layers
        # Qwen2.5 32B Q4_K_M: ~18.5GB, 64 layers

        if model_size_gb <= 6.0:
            # Small models (7B-8B range) typically have 32 layers
            return 32
        elif model_size_gb <= 12.0:
            # Medium models (13B range) typically have 40-48 layers
            return 40
        elif model_size_gb <= 20.0:
            # Large models (30B-34B range) typically have 60-64 layers
            return 64
        elif model_size_gb <= 35.0:
            # Very large models (65B-70B range) typically have 80 layers
            return 80
        else:
            # For very large models, estimate linearly
            # Rough estimation: ~2GB per layer for quantized models
            return max(32, int(model_size_gb / 2.0))

    def get_hardware_summary(self) -> str:
        """
        Get a human-readable summary of detected hardware.

        Returns:
            String summarizing hardware specifications
        """
        gpu_name, vram_gb, ram_gb, cpu_cores = self.detect_hardware()
        summary = f"CPU: {cpu_cores} cores, RAM: {ram_gb:.1f} GB"
        if vram_gb > 0:
            summary += f", GPU: {gpu_name} ({vram_gb:.1f} GB VRAM)"
        return summary


def gpu_protect(name: str) -> str:
    """
    Helper function to safely handle GPU name strings.

    Args:
        name: Raw GPU name string

    Returns:
        Cleaned GPU name string
    """
    if isinstance(name, bytes):
        return name.decode("utf-8", errors="ignore")
    return str(name)


# Example usage and testing
if __name__ == "__main__":
    analyzer = HardwareAnalyzer()
    gpu, vram, ram, cores = analyzer.detect_hardware()
    print(f"Detected hardware:")
    print(f"  GPU: {gpu}")
    print(f"  VRAM: {vram:.1f} GB")
    print(f"  RAM: {ram:.1f} GB")
    print(f"  CPU Cores: {cores}")

    # Test recommendations
    print("\nRecommendations for 8B model (~4.9GB):")
    rec = analyzer.recommend_params(4.9)
    print(f"  GPU Layers: {rec['gpu_layers']}")
    print(f"  Threads: {rec['threads']}")
    print(f"  Batch Size: {rec['batch_size']}")

    print("\nRecommendations for 32B model (~18.5GB):")
    rec = analyzer.recommend_params(18.5)
    print(f"  GPU Layers: {rec['gpu_layers']}")
    print(f"  Threads: {rec['threads']}")
    print(f"  Batch Size: {rec['batch_size']}")
