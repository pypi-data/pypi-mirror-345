#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#----------------#
# Import modules #
#----------------#

import numpy as np
import scipy.stats as ss

#------------------------#
# Import project modules #
#------------------------#

from pygenutils.arrays_and_lists.maths import window_sum

#-------------------------#
# Define custom functions #
#-------------------------#

# Atmospheric variables #
#-----------------------#

# Biovariables: set of atmospheric variables #
#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-#-

def biovars(tmax_monthly_climat, tmin_monthly_climat, prec_monthly_climat):
    """
    Function that calculates 19 bioclimatic variables
    based on monthly climatologic data, for every horizontal grid point.
    
    Parameters
    ----------
    tmax_monthly_climat : numpy.ndarray
          Array containing the monthly climatologic maximum temperature data.
    tmin_monthly_climat : numpy.ndarray
          Array containing the monthly climatologic minimum temperature data.
    precip_dataset : numpy.ndarray
          Array containing the monthly climatologic precipitation data.
    
    Returns
    -------
    p : numpy.ndarray
          Array containing the bioclimatic data for the considered period.
          structured as (biovariable, lat, lon).
    """

    dimensions = tmax_monthly_climat.shape
    bioclim_var_array = np.zeros((19, dimensions[1], dimensions[2]))
     
    # tavg = (tmin_monthly_climat + tmax_monthly_climat) / 2
    tavg = np.mean((tmax_monthly_climat, tmin_monthly_climat), axis=0)
    range_temp = tmax_monthly_climat - tmin_monthly_climat
      
    # P1. Annual Mean Temperature
    bioclim_var_array[0] = np.mean(tavg, axis=0)
      
    # P2. Mean Diurnal Range(Mean(period max-min))
    bioclim_var_array[1] = np.mean(range_temp, axis=0)
      
    # P4. Temperature Seasonality (standard deviation)
    bioclim_var_array[3] = np.std(tavg, axis=0) # * 100
      
    # P5. Max Temperature of Warmest Period 
    bioclim_var_array[4] = np.max(tmax_monthly_climat, axis=0)
     
    # P6. Min Temperature of Coldest Period
    bioclim_var_array[5] = np.min(tmin_monthly_climat, axis=0)
      
    # P7. Temperature Annual Range (P5 - P6)
    bioclim_var_array[6] = bioclim_var_array[4] - bioclim_var_array[5]
      
    # P3. Isothermality ((P2 / P7) * 100)
    bioclim_var_array[2] = bioclim_var_array[1] / bioclim_var_array[6] * 100
      
    # P12. Annual Precipitation
    bioclim_var_array[11] = np.sum(prec_monthly_climat, axis=0)
      
    # P13. Precipitation of Wettest Period
    bioclim_var_array[12] = np.max(prec_monthly_climat, axis=0)
      
    # P14. Precipitation of Driest Period
    bioclim_var_array[13] = np.min(prec_monthly_climat, axis=0)
    
    # P15. Precipitation Seasonality(Coefficient of Variation) 
    # the "+1" is to avoid strange CVs for areas where the mean rainfall is < 1 mm)
    bioclim_var_array[14] = ss.variation(prec_monthly_climat+1, axis=0) * 100
    
    # precipitation by quarters (window of 3 months)
    wet = window_sum(prec_monthly_climat, N=3)
    # P16. Precipitation of Wettest Quarter
    bioclim_var_array[15] = np.max(wet, axis=0)
      
    # P17. Precipitation of Driest Quarter 
    bioclim_var_array[16] = np.min(wet, axis=0)
      
    # temperature by quarters (window of 3 months)
    tmp_qrt = window_sum(tavg, N=3) / 3
      
    # P8. Mean Temperature of Wettest Quarter
    wet_qrt = np.argmax(wet, axis=0)
    for i in range(dimensions[1]):
        for j in range(dimensions[2]):
            bioclim_var_array[7,i,j] = tmp_qrt[wet_qrt[i,j],i,j]
      
    # P9. Mean Temperature of Driest Quarter
    dry_qrt = np.argmin(wet, axis=0)
    for i in range(dimensions[1]):
        for j in range(dimensions[2]):
            bioclim_var_array[8,i,j] = tmp_qrt[dry_qrt[i,j],i,j]
    
    # P10 Mean Temperature of Warmest Quarter 
    bioclim_var_array[9] = np.max(tmp_qrt, axis=0)
      
    # P11 Mean Temperature of Coldest Quarter
    bioclim_var_array[10] = np.min(tmp_qrt, axis=0)
          
    # P18. Precipitation of Warmest Quarter 
    hot_qrt = np.argmax(tmp_qrt, axis=0)
    for i in range(dimensions[1]):
        for j in range(dimensions[2]):
            bioclim_var_array[17,i,j] = wet[hot_qrt[i,j],i,j]
     
    # P19. Precipitation of Coldest Quarter 
    cold_qrt = np.argmin(tmp_qrt, axis=0)
    for i in range(dimensions[1]):
        for j in range(dimensions[2]):
            bioclim_var_array[18,i,j] = wet[cold_qrt[i,j],i,j]
    
    print("Biovariables have been successfully computed.")
    return bioclim_var_array
