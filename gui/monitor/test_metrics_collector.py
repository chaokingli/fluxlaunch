#!/usr/bin/env python3
"""
Test script for MetricsCollector functionality.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from monitor.metrics_collector import MetricsCollector, parse_prometheus_metrics


def test_parse_prometheus_metrics():
    test_text = """
# HELP llamacpp:predicted_tokens_seconds Number of tokens per second
# TYPE llamacpp:predicted_tokens_seconds gauge
llamacpp:predicted_tokens_seconds 42.5

# HELP llamacpp:kv_cache_usage_ratio KV cache usage ratio (0-1)
# TYPE llamacpp:kv_cache_usage_ratio gauge
llamacpp:kv_cache_usage_ratio 0.75

# Other metrics...
some_other_metric 123
"""

    result = parse_prometheus_metrics(test_text)
    expected = {
        "llamacpp_predicted_tokens_seconds": 42.5,
        "llamacpp_kv_cache_usage_ratio": 0.75,
    }

    assert result == expected, f"Expected {expected}, got {result}"
    print("✓ parse_prometheus_metrics test passed")


def test_metrics_collector_init():
    collector = MetricsCollector(host="localhost", port=8080)
    assert collector.host == "localhost"
    assert collector.port == 8080
    assert collector.metrics_url == "http://localhost:8080/metrics"
    print("✓ MetricsCollector init test passed")


def test_collect_metrics_structure():
    collector = MetricsCollector()
    metrics = collector.collect_metrics()

    required_keys = ["ram_mb", "vram_mb", "tokens_per_sec", "kv_cache_ratio"]
    for key in required_keys:
        assert key in metrics, f"Missing key: {key}"

    assert isinstance(metrics["ram_mb"], float) and metrics["ram_mb"] >= 0
    assert metrics["vram_mb"] is None or isinstance(metrics["vram_mb"], float)
    assert (
        isinstance(metrics["tokens_per_sec"], float) and metrics["tokens_per_sec"] >= 0
    )
    assert (
        isinstance(metrics["kv_cache_ratio"], float) and metrics["kv_cache_ratio"] >= 0
    )

    print("✓ collect_metrics structure test passed")


if __name__ == "__main__":
    test_parse_prometheus_metrics()
    test_metrics_collector_init()
    test_collect_metrics_structure()
    print("\n✅ All tests passed!")
