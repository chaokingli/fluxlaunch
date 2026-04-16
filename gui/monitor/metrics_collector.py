"""
Metrics collector for llama-server Prometheus metrics endpoint.
Collects RAM, VRAM, tokens per second, and KV cache ratio metrics.
"""

import logging
import queue
import re
import time
from typing import Dict, Optional

import psutil
import requests

# Try to import pynvml for NVIDIA GPU support, but handle gracefully if not available
try:
    import pynvml

    NVIDIA_SUPPORT = True
except ImportError:
    NVIDIA_SUPPORT = False
    logging.warning("pynvml not available. NVIDIA GPU monitoring will be disabled.")

logger = logging.getLogger(__name__)


def parse_prometheus_metrics(metrics_text: str) -> Dict[str, float]:
    """
    Parse Prometheus metrics text and extract key metrics.

    Args:
        metrics_text: Raw Prometheus metrics text from /metrics endpoint

    Returns:
        Dictionary containing parsed metrics:
        - llamacpp_predicted_tokens_seconds: tokens per second
        - llamacpp_kv_cache_usage_ratio: KV cache usage ratio (0-1)
    """
    metrics = {}

    # Extract llamacpp:predicted_tokens_seconds (tokens per second)
    predicted_tokens_match = re.search(
        r"llamacpp:predicted_tokens_seconds\s+([0-9.]+)", metrics_text
    )
    if predicted_tokens_match:
        metrics["llamacpp_predicted_tokens_seconds"] = float(
            predicted_tokens_match.group(1)
        )

    # Extract llamacpp:kv_cache_usage_ratio (0-1 ratio)
    kv_cache_match = re.search(
        r"llamacpp:kv_cache_usage_ratio\s+([0-9.]+)", metrics_text
    )
    if kv_cache_match:
        metrics["llamacpp_kv_cache_usage_ratio"] = float(kv_cache_match.group(1))

    return metrics


class MetricsCollector:
    """
    Collects metrics from llama-server /metrics endpoint and system resources.

    Supports:
    - HTTP metrics from /metrics endpoint (Prometheus format)
    - System RAM usage via psutil
    - NVIDIA GPU VRAM usage via pynvml (if available)
    - Thread-safe data passing via queue.Queue
    """

    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initialize MetricsCollector.

        Args:
            host: Host address of llama-server (default: localhost)
            port: Port of llama-server (default: 8080)
        """
        self.host = host
        self.port = port
        self.metrics_url = f"http://{host}:{port}/metrics"
        self._nvml_initialized = False

    def _initialize_nvml(self) -> bool:
        """Initialize NVML if NVIDIA support is available."""
        if not NVIDIA_SUPPORT:
            return False

        try:
            if not self._nvml_initialized:
                pynvml.nvmlInit()
                self._nvml_initialized = True
            return True
        except pynvml.NVMLError as e:
            logger.warning(f"Failed to initialize NVML: {e}")
            return False

    def _get_gpu_vram_mb(self) -> Optional[float]:
        """Get total GPU VRAM usage in MB."""
        if not self._initialize_nvml():
            return None

        try:
            device_count = pynvml.nvmlDeviceGetCount()
            total_vram_used = 0

            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                total_vram_used += mem_info.used

            return total_vram_used / (1024 * 1024)  # Convert bytes to MB
        except pynvml.NVMLError as e:
            logger.warning(f"Failed to get GPU VRAM info: {e}")
            return None

    def _get_system_ram_mb(self) -> float:
        """Get current process RAM usage in MB."""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            return memory_info.rss / (1024 * 1024)  # Convert bytes to MB
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.warning(f"Failed to get RAM info: {e}")
            return 0.0

    def collect_metrics(self) -> Dict[str, float]:
        """
        Collect all metrics from server and system.

        Returns:
            Dictionary with keys:
            - ram_mb: System RAM usage in MB
            - vram_mb: GPU VRAM usage in MB (None if not available)
            - tokens_per_sec: Tokens processed per second
            - kv_cache_ratio: KV cache usage ratio (0-1)

        Note: Returns default values (0 for tokens_per_sec and kv_cache_ratio)
              when server is not available or metrics cannot be collected.
        """
        # Initialize result dictionary with defaults
        result = {
            "ram_mb": self._get_system_ram_mb(),
            "vram_mb": self._get_gpu_vram_mb(),
            "tokens_per_sec": 0.0,
            "kv_cache_ratio": 0.0,
        }

        try:
            # Make HTTP request with 2-second timeout
            response = requests.get(self.metrics_url, timeout=2.0)
            response.raise_for_status()

            # Parse Prometheus metrics
            prometheus_metrics = parse_prometheus_metrics(response.text)

            # Update result with collected metrics
            if "llamacpp_predicted_tokens_seconds" in prometheus_metrics:
                result["tokens_per_sec"] = prometheus_metrics[
                    "llamacpp_predicted_tokens_seconds"
                ]
            if "llamacpp_kv_cache_usage_ratio" in prometheus_metrics:
                result["kv_cache_ratio"] = prometheus_metrics[
                    "llamacpp_kv_cache_usage_ratio"
                ]

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout while fetching metrics from {self.metrics_url}")
        except requests.exceptions.ConnectionError:
            logger.warning(
                f"Connection error while fetching metrics from {self.metrics_url}"
            )
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request failed while fetching metrics: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while collecting metrics: {e}")

        return result


# Example usage for testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    collector = MetricsCollector()
    metrics = collector.collect_metrics()
    print("Collected metrics:", metrics)
