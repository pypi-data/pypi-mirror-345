# -*- coding: utf-8 -*-
# -*- Python Version: 2.7 -*-

"""Functions for creating a Phius2024 Resiliency EPW Weather File.

    See: https://vimeo.com/phius/review/998041212/3323b22b3e for background
"""

import math
from copy import copy

try:
    from itertools import izip as zip  # Using Python2.x # type: ignore
except ImportError:
    pass  # Using Python 3.x

try:
    from ladybug.analysisperiod import AnalysisPeriod
    from ladybug.datacollection import HourlyContinuousCollection, HourlyDiscontinuousCollection
    from ladybug.dt import DateTime
    from ladybug.epw import EPW
    from ladybug.stat import STAT
except ImportError as e:
    raise ImportError("\nFailed to import ladybug:\n\t{}".format(e))

try:
    from ladybug_revive.adjustment_factors import calculate_summer_morphing_factors, calculate_winter_morphing_factors
except ImportError as e:
    raise ImportError("\nFailed to import calculate_winter_morphing_factors:\n\t{}".format(e))


def apply_factor_to_hourly_value(_temp, _hour, _factor, _period_total_hours):
    # type: (float, int, float, int) -> float
    """
    Apply the Phius2024 REVIVE adjustment factor to a single hourly value based.

    See also Section 6.1.2.1 'Resilience Extreme Week Morphing Algorithm' Phius Revive 2024 Retrofit Standard for Buildings v24.1.1:
        > T_x_week2_dry_h = T_x_week_dry_h + Delta_dry*sin(phase)
        > T_x_week2_dew_h = T_x_week_dew_h + Delta_dew*sin(phase)
        > T_x_week is the temperature history in the extreme week period of the EPW STAT file.
        > T_x_week2 is the morphed temperature history.
        > h is the hour within the outage period, 0 ≤ h ≤ h_out
        > h_out is the outage duration in hours minus 1
        > h_out = 167
        > Phase_h = math.pi * h / h_out
    """

    return _temp + _factor * math.sin(math.pi * _hour / _period_total_hours)


def apply_adjustment_factor_to_epw_data(_epw_data, _period_values, _period, _factor):
    # type: (HourlyContinuousCollection, list[float], AnalysisPeriod, float) -> HourlyContinuousCollection
    """Apply the Phius2024 REVIVE adjustment factor to the EPW data for a specific period."""

    adjusted_temps = [
        apply_factor_to_hourly_value(temp, hour, _factor, len(_period_values))
        for hour, temp in enumerate(_period_values)
    ]

    start_index = _period._st_time.int_hoy
    end_index = _period._end_time.int_hoy + 1
    new_values = list(_epw_data.values)
    new_values[start_index:end_index] = adjusted_temps

    return HourlyContinuousCollection(header=_epw_data.header, values=new_values)


def check_dew_point_temperature(_dew_point, _dry_bulb):
    # type: (HourlyContinuousCollection, HourlyContinuousCollection) -> HourlyContinuousCollection
    """Check the dew-point temperature to make sure it is never higher than the dry-bulb temperature."""

    new_values = [min(dew, dry) for dew, dry in zip(_dew_point.values, _dry_bulb.values)]

    return HourlyContinuousCollection(header=_dew_point.header, values=new_values)


def get_outage_period(_extreme_week):
    # type: (AnalysisPeriod | None) -> tuple[AnalysisPeriod, AnalysisPeriod]
    """Get the outage period from the STAT file and expand it by a day on either side.

    Also, note that Ladybug applies an 'offset' to the analysis period which I think is confusing.
    So lets reverse that offset, so that the data lines up with the EPW dates (and Phius' original tool).

    See: https://discourse.ladybug.tools/t/why-does-analaysis-period-have-a-1-hour-offset/35017
    """

    if not _extreme_week or len(_extreme_week) != 168:
        raise ValueError("The extreme week should be 168 hours long. Got: {}".format(len(_extreme_week or [])))

    # -- Undo Ladybug's 'offset' so that the data lines up with the EPW dates
    extreme_week_ = AnalysisPeriod.from_start_end_datetime(
        DateTime.from_hoy(_extreme_week._st_time.int_hoy + 1),
        DateTime.from_hoy(_extreme_week._end_time.int_hoy + 1),
        timestep=_extreme_week.timestep,
    )

    # -- Add a day to the start and end of the period
    # -- this is needed to ensure we have the right starting conditions (temp, RH, etc...)
    # -- before we shut off all the power.
    expanded_extreme_week_ = AnalysisPeriod.from_start_end_datetime(
        DateTime.from_hoy(extreme_week_._st_time.int_hoy - 24),
        DateTime.from_hoy(extreme_week_._end_time.int_hoy + 24),
        timestep=extreme_week_.timestep,
    )
    return extreme_week_, expanded_extreme_week_


def apply_analysis_period_to_data(_data, _analysis_period):
    # type: (HourlyContinuousCollection | HourlyDiscontinuousCollection, AnalysisPeriod) -> list[float]
    """Wrap the LBT .filter_by_analysis_period() method so we can type it properly."""

    print("Applying Extreme Week: {} to EPW data".format(_analysis_period))
    return _data.filter_by_analysis_period(_analysis_period).values  # type: ignore


def generate_ladybug_epw(
    _lbt_epw,
    _lbt_stat,
    _winter_10yr_dry_bulb_C,
    _winter_10yr_dew_point_C,
    _summer_20yr_dry_bulb_C,
    _summer_20yr_dew_point_C,
):
    # type: (EPW, STAT, float, float, float, float) -> tuple[EPW, AnalysisPeriod, AnalysisPeriod]

    # --------------------------------------------------------------------------------------------------------------
    # -- Get the Analysis Periods
    winter_outage_period, winter_outage_period_expanded_ = get_outage_period(_lbt_stat.extreme_cold_week)
    summer_outage_period, summer_outage_period_expanded_ = get_outage_period(_lbt_stat.extreme_hot_week)

    # --------------------------------------------------------------------------------------------------------------
    # -- Slice out the Winter and Summer period hourly data from the EPW
    winter_hourly_dry_bulb_deg_C = apply_analysis_period_to_data(_lbt_epw.dry_bulb_temperature, winter_outage_period)
    winter_hourly_dew_point_deg_C = apply_analysis_period_to_data(_lbt_epw.dew_point_temperature, winter_outage_period)

    summer_hourly_dry_bulb_deg_C = apply_analysis_period_to_data(_lbt_epw.dry_bulb_temperature, summer_outage_period)
    summer_hourly_dew_point_deg_C = apply_analysis_period_to_data(_lbt_epw.dew_point_temperature, summer_outage_period)

    # --------------------------------------------------------------------------------------------------------------
    # -- Calculate the Phius-REVIVE Weather-Morphing Factors
    winter_dry_bulb_factor, winter_dew_point_factor = calculate_winter_morphing_factors(
        _winter_10yr_dry_bulb_C,
        winter_hourly_dry_bulb_deg_C,
        _winter_10yr_dew_point_C,
        winter_hourly_dew_point_deg_C,
    )
    summer_dry_bulb_factor, summer_dew_point_factor = calculate_summer_morphing_factors(
        _summer_20yr_dry_bulb_C,
        summer_hourly_dry_bulb_deg_C,
        _summer_20yr_dew_point_C,
        summer_hourly_dew_point_deg_C,
    )

    # --------------------------------------------------------------------------------------------------------------
    # -- Generate a new EPW with the factors applied to the data
    new_epw_ = copy(_lbt_epw)
    new_epw_._data[6] = apply_adjustment_factor_to_epw_data(
        new_epw_.dry_bulb_temperature, winter_hourly_dry_bulb_deg_C, winter_outage_period, winter_dry_bulb_factor
    )
    new_epw_._data[6] = apply_adjustment_factor_to_epw_data(
        new_epw_.dry_bulb_temperature, summer_hourly_dry_bulb_deg_C, summer_outage_period, summer_dry_bulb_factor
    )
    new_epw_._data[7] = apply_adjustment_factor_to_epw_data(
        new_epw_.dew_point_temperature, winter_hourly_dew_point_deg_C, winter_outage_period, winter_dew_point_factor
    )
    new_epw_._data[7] = apply_adjustment_factor_to_epw_data(
        new_epw_.dew_point_temperature, summer_hourly_dew_point_deg_C, summer_outage_period, summer_dew_point_factor
    )

    # --------------------------------------------------------------------------------------------------------------
    # -- Check the dew-points to make sure they are never higher than the dry-bulb
    new_epw_._data[7] = check_dew_point_temperature(
        new_epw_.dew_point_temperature,
        new_epw_.dry_bulb_temperature,
    )

    return new_epw_, winter_outage_period_expanded_, summer_outage_period_expanded_
