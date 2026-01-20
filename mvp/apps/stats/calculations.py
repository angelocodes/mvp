import numpy as np
import statistics


def linear_regression(concentrations, responses):
    """Perform linear regression and return slope, intercept, r_squared"""
    if len(concentrations) != len(responses) or len(concentrations) < 2:
        raise ValueError("Invalid data for regression")

    x = np.array(concentrations)
    y = np.array(responses)

    # Linear regression
    slope, intercept = np.polyfit(x, y, 1)

    # R-squared
    y_pred = slope * x + intercept
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

    return slope, intercept, r_squared


def calculate_recovery(theoretical, measured):
    """Calculate % recovery"""
    return (measured / theoretical) * 100 if theoretical != 0 else 0


def calculate_rsd(values):
    """Calculate %RSD"""
    if len(values) < 2:
        return 0
    mean_val = statistics.mean(values)
    std_dev = statistics.stdev(values)
    return (std_dev / mean_val) * 100 if mean_val != 0 else 0


def calculate_lod_lod(blank_responses, slope):
    """Calculate LOD and LOQ"""
    if not blank_responses:
        raise ValueError("Blank responses required")

    sigma = statistics.stdev(blank_responses)
    lod = 3.3 * sigma / slope if slope != 0 else 0
    loq = 10 * sigma / slope if slope != 0 else 0

    return lod, loq
