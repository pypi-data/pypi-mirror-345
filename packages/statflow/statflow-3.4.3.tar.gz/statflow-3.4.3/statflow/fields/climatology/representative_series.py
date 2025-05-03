#!/usr/bin/env python3
# -*- coding: utf-8 

#----------------#
# Import modules #
#----------------#

import numpy as np
import pandas as pd

#------------------------#
# Import project modules #
#------------------------#

from climalab.meteorological_variables import meteorological_wind_direction
from paramlib.global_parameters import COMMON_DELIM_LIST
from statflow.core.interpolation_methods import polynomial_fitting
from statflow.core.time_series import periodic_statistics

#-------------------------#
# Define custom functions #
#-------------------------#

# Hourly Design Year #
#--------------------#

# Main function #
#-#-#-#-#-#-#-#-#

def calculate_HDY(hourly_df: pd.DataFrame, 
                  varlist: list, 
                  varlist_primary: list, 
                  drop_new_idx_col: bool = False) -> tuple:
    """
    Calculate the Hourly Design Year (HDY) using ISO 15927-4:2005 (E) standard.
    
    Parameters
    ----------
    hourly_df : pd.DataFrame
        DataFrame containing hourly climatological data.
    varlist : list
        List of all variables (column names) to be considered in HDY DataFrame.
    varlist_primary :list
        Primary variables to be used for ranking calculations.
    drop_new_idx_col : bool
        Whether to drop the reset index column.
        
    Returns
    -------
    tuple: HDY DataFrame and the list of selected years for each month.
    """
    # Initialise the HDY DataFrame to store results
    hdy_df = pd.DataFrame(columns=varlist)

    # Extract unique years and months
    hist_years = pd.unique(hourly_df.date.dt.year)
    months = pd.unique(hourly_df.date.dt.month)

    # List to store selected years for each month
    hdy_years = []

    for m in months:
        try:
            # Filter data for the current month and calculate monthly statkit
            hdata_MONTH = hourly_df[hourly_df.date.dt.month == m].filter(items=varlist_primary).reset_index(drop=drop_new_idx_col)
            hdata_MONTH_rank_phi = hdata_MONTH.copy()
            
            # Step a: Calculate daily means for the primary variables
            hdata_MONTH_dm_bymonth = periodic_statistics(hourly_df[hourly_df.date.dt.month == m], varlist_primary, 'day', 'mean')
            
            

        except ValueError as e:
            print(f"Error in periodic_statistics for month {m}: {e}")
            continue  # Skip the current month if there's an error

        # Get unique days for the current month
        no_of_days = len(pd.unique(hdata_MONTH_rank_phi.date.dt.day))

        # Step a: Calculate rankings for each day by each primary variable
        dict_rank = {}
        dict_phi = {}
        
        for var in varlist_primary[1:]:
            var_orig = hdata_MONTH_dm_bymonth[var].to_numpy()
            var_rank = np.argsort(np.argsort(var_orig)) + 1
            dict_rank[var] = var_rank

            # Step b: Calculate cumulative probabilities (phi)
            phi = (var_rank - 0.5) / no_of_days
            dict_phi[var] = phi

            # Store calculated phi values
            hdata_MONTH_rank_phi[var] = phi
        
        # Step c: Group data by year and calculate year-specific ranks
        dict_rank_per_year = {}
        for year in hist_years:
            year_data = hdata_MONTH_rank_phi[hdata_MONTH_rank_phi.date.dt.year == year]
            dict_rank_per_year[year] = {
                var: np.sum(np.abs(year_data[var] - dict_phi[var]))
                for var in varlist_primary[1:]
            }

        # Step d: Calculate total sum of deviations (Fs_sum) for each year
        Fs_sum = {}
        for year, ranks in dict_rank_per_year.items():
            Fs_sum[year] = sum(ranks.values())

        # Step e: Rank the years based on the Fs_sum and choose the best year for the current month
        selected_year = min(Fs_sum, key=Fs_sum.get)
        hdy_years.append(selected_year)

        # Extract the hourly data for the selected year and append it to the HDY DataFrame
        hourly_data_sel = \
        hourly_df[(hourly_df.date.dt.year == selected_year) 
                  & (hourly_df.date.dt.month == m)].filter(items=varlist)\
                 .reset_index(drop=drop_new_idx_col)
        hdy_df = pd.concat([hdy_df, hourly_data_sel], axis=0)

    return hdy_df, hdy_years


# Helpers #
#-#-#-#-#-#

def hdy_interpolation(hdy_df,
                      hdy_years,
                      previous_month_last_time_range,
                      next_month_first_time_range,
                      varlist_to_interpolate,
                      polynomial_order,
                      drop_date_idx_col=False):
    """
    Interpolates along a selected time array between two months
    of an HDY constructed following the ISO 15927-4 2005 (E) standard.

    Since the HDY is composed of 'fragments' of completely different months,
    there are unavoidable vertical jumps for every variable. Polynomial interpolation
    helps to smooth these transitions between months.

    Parameters
    ----------
    hdy_df : pd.DataFrame
        DataFrame containing the HDY hourly data.
    hdy_years : list
        List of selected years corresponding to each month in HDY.
    previous_month_last_time_range : str
        Time range (e.g., '23:00-23:59') for the last day of the previous month.
    next_month_first_time_range : str
        Time range (e.g., '00:00-01:00') for the first day of the next month.
    varlist_to_interpolate : list
        Variables to be interpolated between months.
    polynomial_order : int
        Order of the polynomial to use for fitting.
    drop_date_idx_col : bool, optional
        Whether to drop the index column.

    Returns
    -------
    tuple
        - hdy_interp: pd.DataFrame
                Interpolated variables and smoothed transitions, except wind direction
        - wind_dir_meteo_interp: pd.DataFrame
                Interpolated wind direction and smoothed transitions
    """
    hdy_interp = hdy_df.copy()

    # Remove 'ws10' from interpolation list since it's derived from u10, v10
    if "ws10" in varlist_to_interpolate:
        varlist_to_interpolate.remove("ws10")

    for i in range(len(hdy_years) - 1):
        # Extract time slices for interpolation between consecutive months
        days_slice_prev = hdy_interp[(hdy_interp.date.dt.year == hdy_years[i]) &
                                     (hdy_interp.date.dt.month == hdy_interp.date.dt.month[i])]

        days_slice_next = hdy_interp[(hdy_interp.date.dt.year == hdy_years[i + 1]) &
                                     (hdy_interp.date.dt.month == hdy_interp.date.dt.month[i + 1])]

        # Handle time ranges as integers (hours), split the input range strings
        pml1, pml2 = map(int, previous_month_last_time_range.split(SPLIT_DELIM))
        nmf1, nmf2 = map(int, next_month_first_time_range.split(SPLIT_DELIM))

        # Extract the time slices based on the provided ranges
        df_slice1 = days_slice_prev[(days_slice_prev.date.dt.hour >= pml1) & (days_slice_prev.date.dt.hour <= pml2)]
        df_slice2 = days_slice_next[(days_slice_next.date.dt.hour >= nmf1) & (days_slice_next.date.dt.hour <= nmf2)]

        # Concatenate and reset indices for interpolation
        df_slice_to_fit = pd.concat([df_slice1, df_slice2]).reset_index(drop=drop_date_idx_col)

        # Polynomial fitting for each variable in varlist_to_interpolate
        for var in varlist_to_interpolate:
            y_var = df_slice_to_fit[var].to_numpy()  # Dependent variable (data values)
            fitted_values = polynomial_fitting(y_var, polynomial_order, fix_edges=True)

            # Apply the interpolated values back into the DataFrame
            df_slice_to_fit[var] = fitted_values

            # Update the main HDY DataFrame
            hdy_interp.loc[df_slice_to_fit.index, var] = fitted_values

    # Calculate wind speed modulus based on interpolated u10 and 
    """
    On the wind direction calculus
    ------------------------------
    
    ·The sign of both components follow the standard convention:
        * u is positive when the wind is westerly,
          i.e wind blows from the west and is eastwards.
        * v is positive when the wind is northwards,
          i.e wind blows from the south.
          
    ·From the meteorological point of view,
     the direction of the wind speed vector is taken as
     the antiparallel image vector.
     The zero-degree angle is set 90º further than the
     default unit cyrcle, so that 0º means wind blowing from the North. 
    """   
    hdy_interp["ws10"] = np.sqrt(hdy_interp.u10 ** 2 + hdy_interp.v10 ** 2)

    # Calculate wind direction using meteorological convention
    print("\nCalculating the wind direction from the meteorological point of view...")
    wind_dir_meteo_interp = meteorological_wind_direction(hdy_interp.u10.values, hdy_interp.v10.values)

    return hdy_interp, wind_dir_meteo_interp


#--------------------------#
# Parameters and constants #
#--------------------------#

SPLIT_DELIM = COMMON_DELIM_LIST[3]
