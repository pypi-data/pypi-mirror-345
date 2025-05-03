#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.arrays_and_lists.patterns import count_consecutive
from statflow.core.time_series import consec_occurrences_mindata, consec_occurrences_maxdata

#------------------#
# Define functions #
#------------------#

# Atmospheric variables #
#-----------------------#

def calculate_WSDI(season_daily_tmax, tmax_threshold, min_consec_days):
    """
    Function that calculates the WSDI (Warm Spell Duration Index).
    
    Input data
    ----------
    season_daily_tmax : numpy.ndarray or pandas.Series
          Daily maximum temperature data of the corresponding season in units ºC.
    tmax_threshold : float
          Upper limit of the maximum temperature.
    min_consec_days : int
          Minimum consecutive days number.
    
    Returns
    -------
    int
        Number of total days where at least a specified number of
        consecutive days exceeds certain percentile as a threshold.
    """
    return consec_occurrences_maxdata(season_daily_tmax, tmax_threshold, min_consec_days)


def calculate_SU(season_daily_tmax, tmax_threshold=25):
    """
    Function that calculates the SU (Summer Days).
    
    Parameters
    ----------
    season_daily_tmax : numpy.ndarray or pandas.Series
        Daily maximum temperature data of the corresponding season in units ºC.
    
    tmax_threshold : float
        Upper limit of the maximum temperature in units ºC. Default is 25ºC.
    
    Returns
    -------
    int
        Number of days in which the
        maximum temperature has risen above the threshold.
    """
    return consec_occurrences_maxdata(season_daily_tmax, tmax_threshold)


def calculate_CSU(season_daily_tmax, tmax_threshold=25):
    """
    Function that calculates the CSU (Consecutive Summer Days).
    
    Parameters
    ----------
    season_daily_tmax : numpy.ndarray or pandas.Series
        Daily maximum temperature data of the season in units ºC.
    
    tmax_threshold : float
        Upper limit of the maximum temperature in units ºC. Default is 25ºC.
    
    Returns
    -------
    int
        Number of maximum consecutive days in which
        the temperature has risen above the threshold.
    """
    return consec_occurrences_maxdata(season_daily_tmax,
                                          tmax_threshold,
                                          min_consec_days=None,
                                          max_consecutive_days=True)


def calculate_FD(season_daily_tmin, tmin_threshold=0):
    """
    Function that calculates the FD (Frost Days).
    
    Parameters
    ----------
    season_daily_tmin : numpy.ndarray or pandas.Series
        Daily minimum temperature data of the corresponding season in units ºC.
    
    tmin_threshold : float
        Upper limit of the minimum temperature in units ºC. Defaults to 0ºC.
    
    Returns
    -------
    int
        Number of days in which the
        minimum temperature has fallen below the threshold.
    """
    return consec_occurrences_mindata(season_daily_tmin, tmin_threshold)


def calculate_TN(season_daily_tmin, tmin_threshold=20):
    """
    Function that calculates the TN (Tropical Night Days).
    
    Parameters
    ----------
    season_daily_tmin : numpy.ndarray or pandas.Series
        Daily minimum temperature data of the corresponding season in units ºC.
    
    tmin_threshold : float
        Lower limit of the minimum temperature in units ºC. Default is 20ºC.
    
    Returns
    -------
    int
        Number of nights in which the
        minimum temperature has risen above the threshold.
    """
    return consec_occurrences_mindata(season_daily_tmin,
                                          tmin_threshold,
                                          threshold_mode="above")


def calculate_RR(season_daily_precip, precip_threshold):
    """
    Function that calculates the RR parameter (Wet Days).
    It is defined as the number of days in which the precipitation
    amount exceeds 1 mm.
    
    Parameters
    ----------
    season_daily_precip : numpy.ndarray or pandas.Series
        Daily precipitation data of the corresponding season in units mm.
    
    precip_threshold : float
        Upper limit of the daily precipitation, 1 mm in this case.
    
    Returns
    -------
    int
        Number of days in which the
        precipitation has risen above the threshold.   
    """
    return consec_occurrences_maxdata(season_daily_precip, precip_threshold)


def calculate_CWD(season_daily_precip, precip_threshold):
    """
    Function that calculates the CWD (Consecutive Wet Days),
    i.e. the number of maximum consecutive days in which
    the precipitation amount exceeds 1 mm.
    
    Parameters
    ----------
    season_daily_precip : numpy.ndarray or pandas.Series
        Daily precipitation data of the season in units mm.
    
    precip_threshold : float
        Upper limit of the daily precipitation, 1 mm in this case.
    
    Returns
    -------
    int
        Number of maximum consecutive days in which
        the precipitation has risen above the threshold.
    """
    return consec_occurrences_maxdata(season_daily_precip,
                                          precip_threshold,
                                          min_consec_days=None,
                                          max_consecutive_days=True)


def calculate_hwd(tmax, tmin, max_thresh, min_thresh, dates, min_days):
    """
    Calculate the total heat wave days (HWD) based on daily data.
    
    A heat wave is defined as a period of at least N consecutive days where
    the maximum temperature exceeds the 95th percentile (max_thresh)
    and the minimum temperature exceeds the 90th percentile (min_thresh).
    
    Parameters
    ----------
    tmax : numpy.ndarray or pandas.Series
        Array of daily maximum temperatures.
    tmin : numpy.ndarray or pandas.Series
        Array of daily minimum temperatures.
    max_thresh : float
        Threshold for maximum temperature (95th percentile).
    min_thresh : float
        Threshold for minimum temperature (90th percentile).
    dates : pandas.DatetimeIndex
        Array of dates corresponding to the temperature data.
    min_days : int
        Minimum number of consecutive days for a heat wave.
    
    Returns
    -------
    tuple
        hwd_events : list of tuples
            Each heat wave event's duration, global intensity, peak intensity, and start date.
        total_hwd : int
            Total number of heat wave days.
    """
    # Create a boolean array where both thresholds are satisfied
    heatwave_mask = (tmax > max_thresh) & (tmin > min_thresh)
    
    # Find consecutive blocks of heat wave days
    conv_result = np.convolve(heatwave_mask, np.ones(min_days, dtype=int), mode='valid') >= min_days
    consecutive_indices = np.flatnonzero(conv_result)
    
    hwd_events = []
    total_hwd = 0
    
    if consecutive_indices.size > 0:
        consecutive_lengths = count_consecutive(consecutive_indices)
        
        for count in consecutive_lengths:
            hw_event_indices = np.arange(consecutive_indices[0], consecutive_indices[0] + count)
            hw_max_temps = tmax[hw_event_indices]
            
            # Calculate heat wave characteristics
            duration = hw_event_indices.size
            global_intensity = hw_max_temps.sum() / duration
            peak_intensity = hw_max_temps.max()
            start_date = dates[hw_event_indices[0]]
            
            hwd_events.append((duration, global_intensity, peak_intensity, start_date))
            total_hwd += duration
            
            # Remove used indices
            consecutive_indices = consecutive_indices[count:]

    return hwd_events, total_hwd if hwd_events else ((0, None, None, None), 0)
