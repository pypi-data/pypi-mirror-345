# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Functions for calculating the Phius2024 REVIVE weather adjustment factors.

    See: https://vimeo.com/phius/review/998041212/3323b22b3e for background
"""

import math

try:
    from itertools import izip as zip  # Using Python2.x # type: ignore
except ImportError:
    pass  # Using Python 3.x

try:
    from typing import Callable
except ImportError:
    pass  # IronPython 2.7


def calculate_adjustment_factor(_target_return, _original_week, _extreme_func, _relaxation_factor=0.1, _tolerance=0.01):
    # type: (float, list[float], Callable, float, float) -> tuple[int, float]
    """
    Calculate the delta value for drybulb and dewpoint temps to apply to the original EPW values.
    Adapted from https://github.com/Phius-ResearchComittee/REVIVE/blob/main/REVIVE2024/weatherMorph.py

    See also Section 6.1.2.1 'Resilience Extreme Week Morphing Algorithm' Phius Revive 2024 Retrofit Standard for Buildings v24.1.1:
        > Iteration to determine Delta_dry and Delta_dew:
        > Delta_init = T_return - avg(T_x_week)
        > T_return are the n-year return extreme values of DB and dewpoint, converted from DB and Wet bulb, from ASHRAE Climatic Design Conditions data.
        > For winter, use the 10-year return values.
        > For summer, use the 20-year return values.
        > Delta = Delta_init
        > Repeat
        > K is a relaxation factor = 0.1
        > X = [ max(T_x_week2) for hot week, min(T_x_week2) for cold week ]
        > Delta_next = Delta + K * (T_return_X)
        > Delta = Delta_next
        > Until abs(T_return_X) < tolerance ~ 0.01 F

    Args:
        target_return: n-year return extreme values of dry-bulb or dewpoint
        original_week: original hourly db or dewpoint values from outage week
        extreme_func: function to apply to morphed week: max() for summer and min() for winter

    Returns:
        tuple: iteration count and delta value to apply to original week to get the desired return value
    """
    phase_adjustment = [math.sin(math.pi * hr / len(_original_week)) for hr in range(len(_original_week))]

    # -- Starting conditions
    delta = _target_return - (sum(_original_week) / len(_original_week))
    morphed_week = [temp + delta * adj for temp, adj in zip(_original_week, phase_adjustment)]
    extreme_value = _extreme_func(morphed_week)

    # -- Iteration to determine adjustment factor
    iteration_count = 0
    while abs(_target_return - extreme_value) >= _tolerance:
        if iteration_count >= 100:
            print("Max iterations reached!")
            break
        iteration_count += 1
        delta += _relaxation_factor * (_target_return - extreme_value)
        morphed_week = [temp + delta * adj for temp, adj in zip(_original_week, phase_adjustment)]
        extreme_value = _extreme_func(morphed_week)

    return iteration_count, delta


def calculate_period_morphing_factors(
    _extreme_dry_bulb_C, _hourly_dry_bulb_deg_C, _extreme_dew_point_C, _hourly_dew_point_deg_C, func
):
    # type: (float, list[float], float, list[float], Callable) -> tuple[float, float]
    """Calculate the Phius2024 REVIVE Weather-Morphing Factors for a specific period (winter/summer).

    Adapted from https://github.com/Phius-ResearchComittee/REVIVE/blob/main/REVIVE2024/weatherMorph.py
    """
    print("Using the function: {}".format(func.__name__))

    iters, period_dry_bulb_factor = calculate_adjustment_factor(_extreme_dry_bulb_C, _hourly_dry_bulb_deg_C, func)
    print("Dry-Bulb Factor: {:,.3f} (took {} iterations)".format(period_dry_bulb_factor, iters))

    iters, period_dew_point_factor = calculate_adjustment_factor(_extreme_dew_point_C, _hourly_dew_point_deg_C, func)
    print("Dew-Point Factor: {:,.3f} (took {} iterations)".format(period_dew_point_factor, iters))

    return period_dry_bulb_factor, period_dew_point_factor


def calculate_winter_morphing_factors(
    _extreme_dry_bulb_C,
    _hourly_dry_bulb_deg_C,
    _extreme_dew_point_C,
    _hourly_dew_point_deg_C,
):
    # type: (float, list[float], float, list[float]) -> tuple[float, float]
    """Calculate the Phius2024 REVIVE Weather-Morphing Factors for the Winter period."""
    return calculate_period_morphing_factors(
        _extreme_dry_bulb_C, _hourly_dry_bulb_deg_C, _extreme_dew_point_C, _hourly_dew_point_deg_C, min
    )


def calculate_summer_morphing_factors(
    _extreme_dry_bulb_C,
    _hourly_dry_bulb_deg_C,
    _extreme_dew_point_C,
    _hourly_dew_point_deg_C,
):
    # type: (float, list[float], float, list[float]) -> tuple[float, float]
    """Calculate the Phius2024 REVIVE Weather-Morphing Factors for the Summer period."""
    return calculate_period_morphing_factors(
        _extreme_dry_bulb_C, _hourly_dry_bulb_deg_C, _extreme_dew_point_C, _hourly_dew_point_deg_C, max
    )
