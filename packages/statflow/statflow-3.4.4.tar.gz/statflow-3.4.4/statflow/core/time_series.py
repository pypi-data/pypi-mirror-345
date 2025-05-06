#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Module for time series operations in statistical analysis.
"""

#----------------#
# Import modules #
#----------------#

import numpy as np
from pandas import Grouper

#------------------------#
# Import project modules #
#------------------------#

from filewise.general.introspection_utils import get_caller_args, get_type_str
from pygenutils.arrays_and_lists.patterns import count_consecutive
from pygenutils.strings.string_handler import find_substring_index
from pygenutils.strings.text_formatters import format_string
from pygenutils.time_handling.date_and_time_utils import find_dt_key

#------------------#
# Define functions #
#------------------#

# Statistical Processing #
#------------------------#

def periodic_statistics(obj, statistic, freq,
                        groupby_dates=False,
                        drop_date_idx_col=False,
                        season_months=None):
    """
    Calculates basic statistics (not climatologies) for the given data 
    object over a specified time frequency.

    This function supports data analysis on Pandas DataFrames and 
    xarray objects, allowing for grouping by different time frequencies 
    such as yearly, quarterly, monthly, etc.

    Parameters
    ----------
    obj : pandas.DataFrame or xarray.Dataset or xarray.DataArray
        The data object for which statistics are to be calculated.
    
    statistic : {"max", "min", "mean", "std", "sum"}
        The statistical measure to compute.
    
    freq : str
        The frequency for resampling or grouping the data.
        For example, "D" for daily, "M" for monthly, etc.
        Refer to the Pandas documentation for more details 
        on time frequency aliases.
    
    groupby_dates : bool, optional
        Only applicable for xarray.Dataset or xarray.DataArray.
        If True, the function will group the dates according to 
        the specified frequency.
    
    drop_date_idx_col : bool, optional
        Whether to drop the date index column from the results. 
        Default is False, retaining the dates in the output.
    
    season_months : list of int, optional
        A list of three integers representing the months of a season,
        used if 'freq' is "SEAS". Must contain exactly three months.

    Returns
    -------
    pandas.DataFrame or xarray object
        The computed statistics as a DataFrame or xarray object,
        depending on the type of input data.

    Raises
    ------
    ValueError
        If the specified statistic is unsupported, the frequency is 
        invalid, or if the season_months list does not contain exactly 
        three integers.
    """
    
    # Input validation block #
    #-#-#-#-#-#-#-#-#-#-#-#-#-
    
    param_keys = get_caller_args()
    seas_months_arg_pos = find_substring_index(param_keys, "season_months")
    
    obj_type = get_type_str(obj, lowercase=True)
    seas_mon_arg_type = get_type_str(season_months)
    
    if statistic not in STATISTICS:
        format_args_stat = ("statistic", statistic, STATISTICS)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_stat))
        
    
    if obj_type not in ["dataframe", "dataset", "dataarray"]:
        format_args_obj_type = ("data type",
                                obj_type, 
                                "{pandas.DataFrame, xarray.Dataset, xarray.DataArray}")
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_obj_type))

    if freq not in FREQ_ABBREVIATIONS:
        format_args_freq = ("frequency", freq, FREQ_ABBREVIATIONS)
        raise ValueError(format_string(UNSUPPORTED_OPTION_ERROR_TEMPLATE, format_args_freq))
    
    if seas_mon_arg_type != "list":
        raise TypeError("Expected a list for parameter 'season_months' "
                        f"(number {seas_months_arg_pos}) got '{seas_mon_arg_type}'.")
    
    if freq == "SEAS" and not season_months:
        raise ValueError("Seasonal frequency requires parameter 'season_months'.")
    
    if season_months and len(season_months) != 3:
        raise ValueError(SEASON_MONTH_FMT_ERROR_TEMPLATE)

    # Operations #
    #-#-#-#-#-#-#-

    # GroupBy Logic
    date_key = find_dt_key(obj)

    if obj_type in ["dataset", "dataarray"]:
        groupby_key = f"{date_key}.dt.{freq}"
    else:
        groupby_key = date_key

    # Handling grouping logic
    if groupby_dates and obj_type in ["dataset", "dataarray"]:
        obj_groupby = obj.groupby(groupby_key)
    else:
        obj_groupby = Grouper(key=date_key, freq=freq)

    # Calculate Statistics
    result = getattr(obj_groupby, statistic)()
    if obj_type == "dataframe":
        result.reset_index(drop=drop_date_idx_col)
    
    return result


def decompose_cumulative_data(cumulative_array, fill_value=None, zeros_dtype='d'):    
    """
    Convert cumulative values into individual values by subtracting consecutive elements,
    with an option to handle negative differences.

    This function takes an array of cumulative values and returns the individual values
    that make up the cumulative sum. Negative differences can either be preserved or replaced 
    with a specified fill value.
    
    Parameters
    ----------
    cumulative_array : numpy.ndarray
        A multi-dimensional array representing cumulative values over time or other axes.
    fill_value : scalar or None, optional
        Value to replace negative differences. If None (default), negative differences are preserved.
    zeros_dtype : str or numpy dtype
        Data type for the array of zeros if `fill_value` is used. Default is 'd' (float).
    
    Returns
    -------
    individual_values_array : numpy.ndarray
        A multi-dimensional array with individual values extracted from the cumulative array.
    
    Examples
    --------
    Example 1: Basic cumulative data decomposition
    >>> cumulative_array = np.array([6, 7, 13, 13, 20, 22, 30, 31, 38, 43, 52, 55])
    >>> decompose_cumulative_data(cumulative_array)
    array([ 6.,  1.,  6.,  0.,  7.,  2.,  8.,  1.,  7.,  5.,  9.,  3.])

    Example 2: Preserving negative differences
    >>> cumulative_array = np.array([6, 7, 13, 12, 20, 22])
    >>> decompose_cumulative_data(cumulative_array)
    array([ 6.,  1.,  6., -1.,  8.,  2.])

    Example 3: Replacing negative differences with zeros
    >>> decompose_cumulative_data(cumulative_array, fill_value=0)
    array([ 6.,  1.,  6.,  0.,  8.,  2.])
    """
    
    records = len(cumulative_array)
    
    # Define the behavior for negative differences
    def handle_negative_difference(diff):
        if fill_value is None:
            return diff
        return np.full_like(diff, fill_value, dtype=zeros_dtype) if np.any(diff < 0) else diff
    
    # Calculate the individual values, applying the fill_value if necessary
    individual_values_array = \
        np.array([handle_negative_difference(cumulative_array[t+1] - cumulative_array[t])
                  for t in range(records-1)])
    
    # Add the average of the last two differences to match the shape of the original array
    individual_values_array = np.append(individual_values_array,
                                        np.mean(individual_values_array[-2:], axis=0)[np.newaxis,:],
                                        axis=0)
    
    return individual_values_array


def hourly_ts_cumul(array, zero_threshold, zeros_dtype='d'):    
    """
    Obtain the 1-hour time step cumulative data by subtracting the 
    previous cumulative value from the next.

    Parameters
    ----------
    array : numpy.ndarray
        Time-series array (first index corresponds to time).
    zero_threshold : float
        Values below this threshold are considered unrealistic and set to zero.
    zeros_dtype : str or numpy type, optional
        Data type of the resulting zero array, by default 'd' (double-precision float).

    Returns
    -------
    hour_ts_cumul : numpy.ndarray
        Array of 1-hour time step cumulative data with unrealistic edges set to zero.
    """
    
    hour_ts_data = decompose_cumulative_data(array)  # Apply your decomposition logic
    unmet_case_values = np.zeros_like(array, dtype=zeros_dtype)

    hour_ts_cumul = np.where(np.all(hour_ts_data >= zero_threshold, axis=1),
                                 hour_ts_data, unmet_case_values)
    
    return hour_ts_cumul


def consec_occurrences_maxdata(array,
                               max_threshold,
                               min_consec=None,
                               calc_max_consec=False):
    
    """
    Count the occurrences where values exceed a threshold,
    with an option to calculate the longest consecutive occurrences.

    Parameters
    ----------
    array : numpy.ndarray or pandas.Series
        Input array with maximum value data.
    max_threshold : float
        Threshold for counting occurrences.
    min_consec : int, optional
        Minimum number of consecutive occurrences.
    calc_max_consec : bool, optional
        If True, returns the maximum length of consecutive occurrences.
        Defaults to False.

    Returns
    -------
    int
        Number of occurrences or max length of consecutive occurrences 
        based on input parameters.
    """
    
    above_idx = array > max_threshold
    
    if min_consec is None:
        if calc_max_consec:
            return count_consecutive(above_idx, True) or 0
        return np.count_nonzero(above_idx)

    # Handle cases with a minimum number of consecutive occurrences
    block_idx = \
    np.flatnonzero(np.convolve(above_idx, np.ones(min_consec, dtype=int), mode='valid') >= min_consec)
    consec_nums = count_consecutive(block_idx)

    if consec_nums:
        return len(consec_nums) * min_consec + sum(consec_nums)
    return 0
    
    
def consec_occurrences_mindata(array, min_thres, 
                               threshold_mode="below", 
                               min_consec=None, 
                               calc_min_consec=False):
    """
    Count the occurrences where values are below or above a threshold,
    with an option to calculate the longest consecutive occurrences.

    Parameters
    ----------
    array : numpy.ndarray or pandas.Series
        Input array with minimum value data.
    min_thres : float
        Threshold for counting occurrences.
    threshold_mode : {"below", "above"}, optional
        Whether to count values below or above the threshold. Defaults to "below".
    min_consec : int, optional
        Minimum number of consecutive occurrences.
    calc_min_consec : bool, optional
        If True, returns the maximum length of consecutive occurrences.
        Defaults to False.

    Returns
    -------
    int
        Number of occurrences or max length of consecutive occurrences based on input parameters.
    """
    
    if threshold_mode not in {"below", "above"}:
        raise ValueError("Invalid threshold mode. Choose one from {'below', 'above'}.")

    above_idx = array < min_thres if threshold_mode == "below" else array > min_thres

    if min_consec is None:
        if calc_min_consec:
            return count_consecutive(above_idx, True) or 0
        return np.count_nonzero(above_idx)

    block_idx = \
    np.flatnonzero(np.convolve(above_idx, np.ones(min_consec, dtype=int), mode='valid') >= min_consec)
    consec_nums = count_consecutive(block_idx)

    if consec_nums:
        return len(consec_nums) * min_consec + sum(consec_nums)
    return 0


# Correlations #
#--------------#

def autocorrelate(x, twosided=False):
    """
    Computes the autocorrelation of a time series.

    Autocorrelation measures the similarity between a time series and a 
    lagged version of itself. This is useful for identifying repeating 
    patterns or trends in data, such as the likelihood of future values 
    based on current trends.

    Parameters
    ----------
    x : list or numpy.ndarray
        The time series data to autocorrelate.
    twosided : bool, optional, default: False
        If True, returns autocorrelation for both positive and negative 
        lags (two-sided). If False, returns only non-negative lags 
        (one-sided).

    Returns
    -------
    numpy.ndarray
        The normalised autocorrelation values. If `twosided` is False, 
        returns only the non-negative lags.

    Notes
    -----
    - This function uses `numpy.correlate` for smaller datasets and 
      `scipy.signal.correlate` for larger ones.
    - Be aware that NaN values in the input data must be removed before 
      computing autocorrelation.
    - For large arrays (> ~75000 elements), `scipy.signal.correlate` is 
      recommended due to better performance with Fourier transforms.
    """
    from scipy.signal import correlate

    # Remove NaN values and demean the data
    x_nonan = x[~np.isnan(x)]
    x_demean = x_nonan - np.mean(x_nonan)
    
    if len(x_demean) <= int(5e4):
        x_autocorr = np.correlate(x_demean, x_demean, mode="full")
    else:
        x_autocorr = correlate(x_demean, x_demean)
    
    # Normalise the autocorrelation values
    x_autocorr /= np.max(x_autocorr)
    
    # Return two-sided or one-sided autocorrelation
    return x_autocorr if twosided else x_autocorr[len(x_autocorr) // 2:]


#--------------------------#
# Parameters and constants #
#--------------------------#

# Statistics #
STATISTICS = ["max", "min", "sum", "mean", "std"]

# Time frequency abbreviations #
FREQ_ABBREVIATIONS = ["Y", "SEAS", "M", "D", "H", "min", "S"]

# Template strings #
#------------------#

UNSUPPORTED_OPTION_ERROR_TEMPLATE = "Unsupported {} '{}'. Options are {}."
SEASON_MONTH_FMT_ERROR_TEMPLATE = """Parameter 'season_months' must contain exactly \
3 integers representing months. For example: [12, 1, 2]."""
