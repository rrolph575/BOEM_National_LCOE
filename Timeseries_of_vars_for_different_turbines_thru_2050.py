# -*- coding: utf-8 -*-

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np

"""
Created on Wed Jul 19 13:29:59 2023

For selected lat/lons and turbine ratings (which correspond to assumed years), make a line plot of selected variables (LCOE, CapEx, OpEx, net capacity factor)

### Rerun this script if it doesn't run teh first time -- time to debug later... 

@author: rrolph
"""

#### Inputs 
basepath = 'C:/Users/rrolph/OneDrive - NREL/Projects/BOEM_IAA_NationalLCOE/analyzing_results/'
datapath = basepath + 'outfiles_from_eagle/'
figpath = basepath + 'figures/timeseries/'
ofilepath = basepath + 'timeseries_data_files/'

# Specify region from filenames in above datapath
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



### Find closest point
selected_data_closest_all = pd.Series({'lcoe': 5, 'capex_kw': 5, 'opex_kw': 5, 'mean_cf': 5, 'rating': 5}) # initialize series
rating = '0_12MW'
ifile = datapath + rating + region_filename_ending    
### Read files
data_gdf = gpd.read_file(ifile)
# Create selected lat lon geodataframe
site_lat_lon_df = pd.DataFrame({'Latitude':[lat], 'Longitude': [lon]})
site_lat_lon_gdf = gpd.GeoDataFrame(site_lat_lon_df, geometry=gpd.points_from_xy(site_lat_lon_df.Longitude, site_lat_lon_df.Latitude), crs='epsg:4326')
site_lat_lon_gdf = site_lat_lon_gdf.to_crs(crs=data_gdf.crs)
# join dataframes based on distance
gdf_with_distances_to_sel_point = data_gdf.sjoin_nearest(site_lat_lon_gdf, how='inner', distance_col = 'distance')
# find index with minimum distance to the selected point
idx_closest = gdf_with_distances_to_sel_point['distance'].idxmin()


    
### Read in data from all ratings
ratings_gulf =  ['0_12MW_gulf', '1_17MWlowSP_gulf_30', '2_17MWlowSP_gulf_35']
ratings = ['0_12MW', '1_15MW', '2_20MW']
years = np.array([2025, 2030, 2035, 2040, 2045, 2050])
for ind, year in enumerate(years):
#for rating in ratings:
    print(year)
    #rating = '0_12MW'
    if year in np.array([2025, 2030, 2035]):
        if domain == 'gulf':
            ifile = ratings_gulf[ind] + '.gpkg'
        else:
            ifile = datapath + ratings[ind] + region_filename_ending
    if year in np.array([2040, 2045, 2050]):
        if domain == 'gulf':
            ifile = basepath + 'new_gpkg_files_with_cost_reductions_applied/gulf_2_17MWlowSP_gulf_35_' + str(year) + '.gpkg'
        else:
            ifile= basepath + 'new_gpkg_files_with_cost_reductions_applied/' + domain + '_' + '2_20MW_' + str(year) + '.gpkg'
    print(ifile)
    ### Read files
    data_gdf = gpd.read_file(ifile)
    
    ### Extract values you want from that point
    data_closest = data_gdf.iloc[idx_closest]
    selected_data_closest = data_closest.loc(axis=0)['lcoe', 'capex_kw', 'opex_kw', 'mean_cf']
    selected_data_closest['rating']=rating
    ### Concat to the data from other turbine ratings
    selected_data_closest_all = pd.concat([selected_data_closest_all, selected_data_closest],axis=1)
    
### Create a dataframe with data from all ratings 
selected_data_closest_all = selected_data_closest_all.drop(columns=0)
# add turbine rating to the dataframe
selected_data_closest_all.columns = years



### Make plots of data

# Save the data
selected_data_closest_all.to_pickle(ofilepath + sitename + '_lcoe_capex_opex_2025_thru_2050.pkl')

# LCOE
fig, ax = plt.subplots()
#ax.set_title(sitename)
selected_data_closest_all.loc['lcoe'].plot(color='k')
ax.set_ylabel('LCOE [$/MWh]',size=20)
ax.set_xlabel('COD (Year)', size=20)
labels = [item.get_text() for item in ax.get_xticklabels()]
#indices = [1,5,9]
#replacements = ['12 MW', '15 MW', '20 MW']
#replacements = ['2025', '2030', '2035', '2040', '2045', '2050']
#for (index, replacement) in zip(indices, replacements):
#    labels[index] = replacement
ax.set_xticklabels(labels, size=20)
y_labels = ax.get_yticklabels()
ax.set_yticklabels(y_labels, size=20)
plt.savefig(figpath + '/lcoe_' + sitename + '_' + ofilename_ext + '_2025_thru_2050.png', bbox_inches='tight')

# CapEx and OpEx
fig, ax = plt.subplots()
#ax.set_title(sitename)
ax = selected_data_closest_all.loc['capex_kw'].plot(color='k', marker='*')
ax.set_ylabel('CapEx [$/kW]', size=20)
y_labels = ax.get_yticklabels()
ax.set_yticklabels(y_labels, size=20)
ax.set_xticklabels(labels, size=20)
ax2 = ax.twinx()
selected_data_closest_all.loc['opex_kw'].plot(ax=ax2, color='b', marker='o')
ax2.set_ylabel('OpEx [$/kW]', size=20)
ax2.yaxis.label.set_color('b')
ax2.tick_params(axis='y', colors='b')
ax2.set_xticklabels(labels, size=20)
ylabels_ax2 = ax2.get_yticklabels()
ax2.set_yticklabels(ylabels_ax2, size=20)
ax.set_xlabel('COD (Year)', size=20)
plt.savefig(figpath + 'capex_and_opex_' + sitename + '_' + ofilename_ext + '_2025_thru_2050.png', bbox_inches='tight')

# Net Capacity factor
fig, ax = plt.subplots()
#ax.set_title(sitename)
ax.set_ylabel('Net capacity factor [%]', size=20)
ncf = selected_data_closest_all.loc['mean_cf']*100
ncf.plot(color='k')
ax.set_xticklabels(labels, size=20)
y_labels = ax.get_yticklabels()
ax.set_yticklabels(y_labels, size=20)
ax.set_xlabel('COD (Year)', size=20)
plt.savefig(figpath + 'ncf_' + sitename + '_' + ofilename_ext + '_2025_thru_2050.png', bbox_inches='tight')








