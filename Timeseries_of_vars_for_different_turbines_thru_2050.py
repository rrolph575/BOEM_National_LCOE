# -*- coding: utf-8 -*-

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D


"""
Created on Wed Jul 19 13:29:59 2023

For selected lat/lons and turbine ratings (which correspond to assumed years), make a line plot of selected variables (LCOE, CapEx, OpEx, net capacity factor)

### Rerun this script if it doesn't run the first time -- time to debug later... 

@author: rrolph
"""

#### Inputs 
basepath = 'C:/Users/rrolph/OneDrive - NREL/Projects/BOEM_IAA_NationalLCOE/analyzing_results/'
datapath = basepath + 'outfiles_from_eagle/'
figpath = basepath + 'figures/timeseries/'
ofilepath = basepath + 'timeseries_data_files/'
gpkg_filepath_reduced_costs = basepath + 'new_gpkg_files_with_cost_reductions_applied/'

# Specify region from filenames in above datapath
sitenames = ['Morro_Bay', 'VineyardWind1'] # str as in filename
labels_for_sitenames = ['Morro Bay', 'Vineyard Wind 1'] # str for plot
sitename = 'VineyardWind1'  # 'Morro_Bay' or 'VineyardWind1'
use_mid_atlantic_data = False

if sitename == 'Morro_Bay':
    region_filename_ending = '_wc.gpkg' 
    lat = 35.58
    lon = -121.83
    ofilename_ext = '_'
    domain = 'wc'

if sitename == 'VineyardWind1':
    region_filename_ending = '_na.gpkg' 
    domain = 'na'
    lat = 41.07031
    lon = -70.50910
    ofilename_ext = 'using_NorthAtlantic_data'
    if use_mid_atlantic_data == True:
        region_filename_ending = '_ma.gpkg' 
        lat = 41.07031
        lon = -70.50910
        ofilename_ext = 'using_MidAtlantic_data'
        # Site 2: Vineyard Wind 1 call area https://www.boem.gov/renewable-energy/state-activities/vineyard-wind-1 
        # and shapefile https://www.boem.gov/renewable-energy/mapping-and-data/renewable-energy-gis-data 
    
if sitename == 'Site1':
    

# Commented because already ran
# ### Find closest point by using representative ifile
# selected_data_closest_all = pd.Series({'lcoe': 5, 'capex_kw': 5, 'opex_kw': 5, 'mean_cf': 5}) # initialize series
# year = 2025
# scenario = 'mid'
# ifile = gpkg_filepath_reduced_costs + domain + '_' + str(year) + '_' + scenario + '.gpkg' 
# ### Read files
# data_gdf = gpd.read_file(ifile)
# # Create selected lat lon geodataframe
# site_lat_lon_df = pd.DataFrame({'Latitude':[lat], 'Longitude': [lon]})
# site_lat_lon_gdf = gpd.GeoDataFrame(site_lat_lon_df, geometry=gpd.points_from_xy(site_lat_lon_df.Longitude, site_lat_lon_df.Latitude), crs='epsg:4326')
# site_lat_lon_gdf = site_lat_lon_gdf.to_crs(crs=data_gdf.crs)
# # join dataframes based on distance
# gdf_with_distances_to_sel_point = data_gdf.sjoin_nearest(site_lat_lon_gdf, how='inner', distance_col = 'distance')
# # find index with minimum distance to the selected point
# idx_closest = gdf_with_distances_to_sel_point['distance'].idxmin()


    
### Read in data
years = np.array([2025, 2030, 2035, 2040, 2045, 2050])
scenarios = ['conservative', 'mid', 'advanced'] # filenames
scenario_labels = ['Conservative', 'Mid', 'Advanced']

# Commented because already ran
# for scenario in scenarios:
#     selected_data_closest_all = pd.Series({'lcoe': 5, 'capex_kw': 5, 'opex_kw': 5, 'mean_cf': 5}) # initialize series
#     for ind, year in enumerate(years):
#         print(year)
#         ifile = gpkg_filepath_reduced_costs + domain + '_' + str(year) + '_' + scenario + '.gpkg'
#         ### Read files
#         data_gdf = gpd.read_file(ifile)
        
#         ### Extract values you want from that point
#         data_closest = data_gdf.iloc[idx_closest]
#         selected_data_closest = data_closest.loc(axis=0)['lcoe', 'capex_kw', 'opex_kw', 'mean_cf']
#         # add year to the dataset
#         selected_data_closest['year'] = year
#         ### Concat to the data from other turbine ratings
#         selected_data_closest_all = pd.concat([selected_data_closest_all, selected_data_closest],axis=1)
        
#     # rename the columns to the years
#     selected_data_closest_all.columns = selected_data_closest_all.loc['year']
    
#     # drop the first column
#     selected_data_closest_all = selected_data_closest_all.iloc[:-1, 1:]
    
#     # Save the data
#     selected_data_closest_all.to_pickle(ofilepath + sitename + '_' + scenario +  '_lcoe_capex_opex_2025_thru_2050.pkl')



### Make one plot per cost parameter, but different colors showing the regions. The scenarios are differnt line types (solid, dot, dashed)


def plot_diff_scenarios_and_sites(var, varlabel, sitenames, scenarios, scenario_labels):
    fig1, ax1 = plt.subplots(figsize=(8,6))
    linetypes = ['dotted', 'solid', 'dashdot']
    colors = ['k', 'b']
    linecolors_for_sitenames = []
    
    for idx, sitename in enumerate(sitenames):
        for ind, scenario in enumerate(scenarios):
            ifile = ofilepath + sitename + '_' + scenario +  '_lcoe_capex_opex_2025_thru_2050.pkl'
            df = pd.read_pickle(ifile)
            print(ifile)
            # LCOE for each scenario and sitename
            ax1.plot(df.keys().values, df.loc[var].values, linestyle = linetypes[ind], color = colors[idx])
        
        # Color for each site
        linecolors_for_sitenames.append(Line2D([0,1],[0,1],linestyle='solid', color=colors[idx]))
            
    ax1.set_ylabel(varlabel,size=20)
    ax1.set_xlabel('COD (Year)', size=20)
    xlabels = ax1.get_xticklabels()
    ax1.set_xticklabels(xlabels, size=20)
    y_labels = ax1.get_yticklabels()
            
    # set legend lines
    linestyles = []
    for ind, scenario in enumerate(scenarios):
        linestyles.append(Line2D([0,1],[0,1],linestyle=linetypes[ind], color='g'))
               
    ax1.legend(linestyles + linecolors_for_sitenames, scenario_labels + labels_for_sitenames)
            
    ax1.set_yticklabels(y_labels, size=20)
    plt.savefig(figpath + '/' + var + '_' + sitename + '_2025_thru_2050.png', bbox_inches='tight')
   
    

### Call the plotting function
cost_components = ['lcoe', 'capex_kw', 'opex_kw', 'mean_cf']  # strings as defined from output of reV
labels = ['LCOE [$/MWh]', 'CapEx [$/kW]', 'OpEx [$/kW]', 'Net capacity factor [%]']

for ind, component in enumerate(cost_components):
    plot_diff_scenarios_and_sites(component, labels[ind], sitenames, scenarios, scenario_labels)

    
    
    
    
    
    
    
