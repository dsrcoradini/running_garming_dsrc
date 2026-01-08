"""
Metrics calculation module for running data analysis.
"""

from running_analyzer.metrics.calculations import (
    add_hrv_metrics,
    add_pace_metrics,
    compute_run_stats,
)

__all__ = [
    'add_hrv_metrics',
    'add_pace_metrics',
    'compute_run_stats',
]
