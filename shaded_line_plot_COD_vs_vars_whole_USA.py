# -*- coding: utf-8 -*-
"""
Created on Mon Aug 14 10:33:44 2023

Create a shaded line plot of min/max values for LCOE, CapEx, OpEx with some solid lines of representative case study sites.

@author: rrolph
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
from osgeo_utils.ogrmerge import process as ogr_merge



## Specify sitenames for line plots of case studies
sites = ['Morro_Bay', 'VineyardWind1']  # 'Morro_Bay' or 'VineyardWind1'
site_labels = ['Morro Bay', 'Vineyard Wind 1']


## Datapaths
basepath = 'C:/Users/rrolph/OneDrive - NREL/Projects/BOEM_IAA_NationalLCOE/analyzing_results/'
timeseries_filepath = basepath + 'timeseries_data_files/'
# 2025, 2030, 2035
datapath_ofiles_eagle = basepath + 'outfiles_from_eagle/'
# 2040, 2045, 2050
datapath_2040_thru_2050 = basepath + 'new_gpkg_files_with_cost_reductions_applied/'
# national_filepath
national_filepath = basepath + 'national_merged_files/'
# figpath
figpath = basepath + 'figures/timeseries/all_sites_one_fig_ts_sep_by_var/'


### Merge all regions and save a national gpkg one file per each year
# !!! Commented below because files already generated
#year_range = np.array([2025, 2030, 2035, 2040, 2045, 2050])
year_range = np.array([2025, 2030]) # !!! for debug
runs = ['0_', '1_', '2_']

# year_range_from_eagle = np.array([2025, 2030, 2035]) # helps define which ifilepath to use
# for ind, year in enumerate(year_range):
#     if year in year_range_from_eagle:
#         datapath = datapath_ofiles_eagle
#         ifiles = datapath + runs[ind] + '*.gpkg'
#     else:
#         datapath = datapath_2040_thru_2050  
#         ifiles = datapath_2040_thru_2050 + '*_' + str(year) + '.gpkg'
#     # concatenate the data into one gdf and then save to one gpkg file
#     print(ifiles)
#     ofile = national_filepath + str(year) + '_national.gpkg'
#     ogr_merge(['-single', '-f', 'GPKG', '-o', ofile, ifiles, '-overwrite_ds']) # https://gdal.org/programs/ogrmerge.html



### Create a layer from the merged file that was created above that just includes the lcoe, capex, and opex
# !!! in qgis via GUI, can put call here later. (right click layer, then 'export features as', then you select which fields you want to export into a new renamed layer.)



### Create shaded line plots of data spread, spread on each year (x-axis: year COD, y-axis: LCOE/CapEx/OpEx). Plot max and min of each variable for each year, create 2 lines through those across years, and shade the middle. You end up with 3 plots.


# Calculate min and max of vars from the merged datafile
# do not take min and max because it just depends on thresholds since there is such a high range (LCOE > 10000)
# varnames = ['lcoe', 'capex_kw', 'opex_kw']
# var_thresholds = np.array([400, 4000, 300]) # !!! can implement thresholds later
# var_max = np.empty((len(varnames), len(year_range)))
# var_min = np.empty((len(varnames), len(year_range)))
# for ind, var in enumerate(varnames):
#     for idx, year in enumerate(year_range):
#         ifile = national_filepath + str(year) + '_national_selected_vars.gpkg'
#         data = gpd.read_file(ifile) # !!! This takes a long time
#         # get max, min for each variable for each year
#         var_max[ind, idx] = max(data[var])
#         var_min[ind, idx] = min(data[var])
#         # save var_min and var_max
#         data = {'var_name': var, 'year_range': year_range, 'var_min': var_min, 'var_max': var_max}
#         df = pd.DataFrame(data=data)
#     df.to_pickle(national_filepath + 'processed_datasets/' + var + '_national_timeseries_yrs_min_max.pkl') 
      


### Make plots
# Read the timeseries data for now.
var_list = ['lcoe', 'capex_kw', 'opex_kw']
var_labels = ['LCOE [$/MWh]', 'CapEx [$/kW]', 'OpEx [$/kW]']
ymax = np.empty((len(sites), len(var_list)))
ymin = np.empty((len(sites), len(var_list)))

for idx, site in enumerate(sites):
    ifile_ts_sel_loc = timeseries_filepath + site + '_lcoe_capex_opex_2025_thru_2050.pkl'
    timeseries_df = pd.read_pickle(ifile_ts_sel_loc)
    for ind, var in enumerate(var_list):
        # Calculate min and max for y-labels
        ymax[idx, ind] = timeseries_df.loc[var].max() # this is the max for each variable, one row for each site [lcoe, capex, opex]
        ymin[idx, ind] = timeseries_df.loc[var].min()
       
# fig, axs = plt.subplots(3,1, sharex=True)
# for ind, var in enumerate(var_list):
#     #fig, ax = plt.subplots(1,1)
#     for idx, site in enumerate(sites):
#         ifile_ts_sel_loc = timeseries_filepath + site + '_lcoe_capex_opex_2025_thru_2050.pkl'
#         timeseries_df = pd.read_pickle(ifile_ts_sel_loc)
#         # Plot
#         axs[ind].plot(timeseries_df.keys().values, timeseries_df.loc[var].values, label=site_labels[idx])
#         #ax.fill_between(min_max_df['year_range'], min_max_df['var_min'], min_max_df['var_max'], alpha=0.2)
#     axs[2].set_xlabel('COD [Year]')
#     axs[ind].set_ylabel(var_labels[ind])
#     axs[ind].set_ylim([0.9*ymin[:,ind].min(), 1.1*ymax[:,ind].max()])
#     axs[ind].legend()
#     plt.savefig(figpath + var + '_rep_sites_2025thru2050.png', bbox_inches='tight')


for ind, var in enumerate(var_list):
    fig, ax = plt.subplots(1,1)
    for idx, site in enumerate(sites):
        ifile_ts_sel_loc = timeseries_filepath + site + '_lcoe_capex_opex_2025_thru_2050.pkl'
        timeseries_df = pd.read_pickle(ifile_ts_sel_loc)
        # Plot
        ax.plot(timeseries_df.keys().values, timeseries_df.loc[var].values, label=site_labels[idx])
        #ax.fill_between(min_max_df['year_range'], min_max_df['var_min'], min_max_df['var_max'], alpha=0.2)
    ax.set_xlabel('COD [Year]')
    ax.set_ylabel(var_labels[ind])
    ax.set_ylim([0.9*ymin[:,ind].min(), 1.1*ymax[:,ind].max()])
    ax.legend()
    plt.savefig(figpath + var + '_rep_sites_2025thru2050.png', bbox_inches='tight')

 
    
    
