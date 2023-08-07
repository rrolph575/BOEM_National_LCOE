# -*- coding: utf-8 -*-
"""
Created on Tue Jul 25 12:09:09 2023

@author: rrolph
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import pylab
from mpl_toolkits import mplot3d



#### !!! Convert this to reading the gpkg file instead of this exported csv in case files change.  The gpkg are the updated ofiles. (didn't have access to eagle at time, that is why script was written this way).

datapath = 'C:/Users/rrolph/OneDrive - NREL/Projects/BOEM_IAA_NationalLCOE/analyzing_results/230717_supply_curves/230717_supply_curves/'
# all cost components in the results csv are reported for a 600 MW plant; but CapEx, OpEx, LCOE are reported for a 1,000 MW plant (i.e., the latter should be divided by 1000x1000 for a $/kW value). 

call_areas_only = False
domain_names = ['gulf', 'hi', 'ma', 'na', 'sa', 'wc']
run_names = ['0_12MW', '1_15MW', '2_17MWlowSP', '2_20MW']

#for run in run_names:
    #for domain in domain_names:
run = '0_12MW'
domain = 'wc'

# filter the domains further by selected lat/lon box
if domain == 'gulf':
    if call_areas_only == True:
        # lat lon bounds of call areas NH15-10
        lat_UR_NH1510 = 28.93571
        lon_UR_NH1510 = -94.47527
        lat_LL_NH1510 = 28.49277
        lon_LL_NH1510 = -94.71072
        # lat lon bounds of call area NH15-08
        lat_UR_NH1508 = 29.24981
        lon_UR_NH1508 = -93.28495
        lat_LL_NH1508 = 29.01739
        lon_LL_NH1508 = -93.49982 
if domain == 'wc':
    if call_areas_only == True:
        ## lat lon bounds of selected call areas
        # Call area NK10-01
        lat_UR_NK10_01 = 43.9529
        lon_UR_NK10_01 = -124.4148
        lat_LL_NK10_01 = 43.2549
        lon_LL_NK10_01 = -125.1619
        # Call area NK10-04
        lat_UR_NK10_04 = 42.4807
        lon_UR_NK10_04 = -124.6518
        lat_LL_NK10_04 = 41.9662
        lon_LL_NK10_04 = -125.1097
        # Call area Humboldt
        lat_UR_humboldt = 41.1488
        lon_UR_humboldt = -124.5263
        lat_LL_humboldt = 40.7545
        lon_LL_humboldt = -124.8034
        # Call area Morro Bay
        lat_UR_Morro = 35.70231
        lon_UR_Morro = -121.63510
        lat_LL_Morro = 35.44670
        lon_LL_Morro = -122.02668

        
# Read in ifile
ifile = datapath + run + '_' + domain + '_supply-curve-aggregation.csv'
data = pd.read_csv(ifile)



# print the min and max lcoe
print('Min LCOE: ' + str(min(data['mean_lcoe'])))
print('Max LCOE: ' + str(max(data['mean_lcoe'])))

# Select vars from ifile
df = data[['mean_cf', 'mean_lcoe', 'latitude', 'longitude', 'state', 'mean_dist_s_to_l', 'mean_dist_l_to_ts', 'mean_dist_p_to_s', 'mean_depth', 'mean_export', 'mean_capex', 'mean_opex', 'mean_install', 'mean_hs_average', 'mean_gcf']]

# check for gaussian to see if you can exclude standard deviations
# stats.probplot(df['mean_capex'], dist='norm', plot=pylab)


# filter the lat/lon boxes of the datafram
if domain == 'gulf':
    if call_areas_only == True:
        # first calculate the mean of call areas NH15-10
        df_NH1510 = df.loc[(df['latitude'] < lat_UR_NH1510) & (df['latitude'] > lat_LL_NH1510)]
        df_NH1510 = df_NH1510.loc[(df_NH1510['longitude'] < lon_UR_NH1510) & (df_NH1510['longitude'] > lon_LL_NH1510)]
        # then calculate the mean of call area NH15-08
        df_NH1508 = df.loc[(df['latitude'] < lat_UR_NH1508) & (df['latitude'] > lat_LL_NH1508)]
        df_NH1508 = df_NH1508.loc[(df_NH1508['longitude'] < lon_UR_NH1508) & (df_NH1508['longitude'] > lon_LL_NH1508)]
        # combine the call areas into one dataframe
        df_all_call_areas_gulf = pd.concat([df_NH1510, df_NH1508])
        print('Gulf of Mexico: mean of all call areas for a 1 GW plant ($/kW)')
        print(df_all_call_areas_gulf.mean())
    
if domain == 'wc':
    
    if call_areas_only == True:
        lat_UR_list = np.array([lat_UR_NK10_01, lat_UR_NK10_04, lat_UR_humboldt, lat_UR_Morro])
        lon_UR_list = np.array([lon_UR_NK10_01, lon_UR_NK10_04, lon_UR_humboldt, lon_UR_Morro])
        lat_LL_list = np.array([lat_LL_NK10_01, lat_LL_NK10_04, lat_LL_humboldt, lat_LL_Morro])
        lon_LL_list = np.array([lon_LL_NK10_01, lon_LL_NK10_04, lon_LL_humboldt, lon_LL_Morro])
        df_empty = pd.DataFrame()
        for idx, lat in enumerate(lat_UR_list):
            print(idx)
            # filter by lat
            df1 = df.loc[(df['latitude'] < lat_UR_list[idx]) & (df['latitude'] > lat_LL_list[idx])]
            # filter the filtered lat now by lon
            df1 = df1.loc[(df1['longitude'] < lon_UR_list[idx]) & (df1['longitude'] > lon_LL_list[idx])]
            
            df_all_call_areas = pd.concat([df_empty, df1])
        df = df_all_call_areas
       
        print('West Coast: mean of all call areas for a 1 GW plant ($/kW)')
        print(df_all_call_areas.mean())


# Take average of east coast
if domain == 'sa':
    print('mean of all points in south atlantic ')
    df.mean()
    print(df)
    # df_south_atlantic['latitude'].min()
    # Out[68]: 24.179

    # df_mid_atlantic['latitude'].min()
    # Out[69]: 37.22
    # Truncate the south atlantic latitudes so that the values do not overlap with the mid-atlantic ones
    #df = df.loc[(df['latitude'] < 37.22)]
    #print('mean of points in south atlantic, truncated to not include overlapping latitudes with mid-atlantic dataset')
    #print(df)
    #print(df.mean())
    
    
if domain == 'ma':
    print('mean of all points in mid atlantic ')
    print(df.mean())
    
if domain == 'na':
    print('mean of all points in north atlantic')
    print(df.mean())

# Filter out rows where LCOE > 400, etc.
#df = df.loc[(df['mean_lcoe'] < 400)]
  
# Differentiate the data between fixed and floating depth thresholds
df_up_to_60m= df.loc[(df['mean_depth'] < 60)] 
df_60m_and_deeper = df.loc[(df['mean_depth'] > 60)]

## concatentate into one dataframe separating fixed and floating
df_in_depth_bands = pd.concat([df_up_to_60m, df_60m_and_deeper], axis=1, keys = ['up to 60m', '60m and deeper'])



### Plot LCOE as a function of various variables
def plot_LCOE_as_function(df, substructure_type, varname, domain, run):
    ''' args:
    df: dataframe separated by depth bands (df_in_depth_bands as defined above)
    substructure_type: str, 'fixed' or 'floating'
    varname: str, as defined in reV, EXCEPT for distance to POI which is 'dist_to_POI'
    domain: str, the domain where the ifile comes from
    run: str, indicates turbine rating & run number in reV
    '''
    # Extract data
    if substructure_type == 'fixed':
        depth_inc = 'up to 60m'
    if substructure_type == 'floating':
        depth_inc = '60m and deeper'
    if varname == 'dist_to_POI':
        indep_var = df[depth_inc].mean_dist_s_to_l + df[depth_inc].mean_dist_l_to_ts
    else:
        indep_var = df[depth_inc][varname]
    
    
    fig, ax = plt.subplots()
    ax.scatter(indep_var, df[depth_inc].mean_lcoe)
    ax.set_title(substructure_type)
    ax.set_xlabel(varname)
    ax.set_ylabel('LCOE [$/MWh]')
    plt.savefig('figures/lcoe_vs_' + varname + '/lcoe_vs_' + varname + '_' + run + '_' + domain + '_' + substructure_type + '.png', bbox_inches='tight')
    


### Plot LCOE as a function of vars listed below
for sub_type in ['fixed', 'floating']:
    for var in ['dist_to_POI', 'mean_dist_p_to_s', 'mean_depth', 'mean_cf']:
        plot_LCOE_as_function(df_in_depth_bands, sub_type, var, domain, run)



### Take the mean of the depth bands ###
# concat all with column names as distance bands
df_mean_in_depth_bands_mean = pd.concat([df_up_to_60m.mean(), df_60m_and_deeper.mean()], axis=1, keys = ['up to 60m', '60m and deeper'])
print(df_mean_in_depth_bands_mean)
# calculate selected variables per kW
print('Mean values per kW:')
df_dollar_per_kW_selected_vars_mean = df_mean_in_depth_bands_mean.loc[['mean_capex', 'mean_opex']]/1e6    
print(df_dollar_per_kW_selected_vars_mean)



### Explain why the regions show different LCOE CapEx OpEx values: 
## Explain driving factors of CapEx
# x-axis: water depth
# y-axis: distance to POI
# z (or color): CapEx value

def plot_CapEx_as_function(df, substructure_type, domain, run):
    ''' args:
    df: dataframe separated by depth bands (df_in_depth_bands as defined above)
    substructure_type: str, 'fixed' or 'floating'
    domain: str, the domain where the ifile comes from
    run: str, indicates turbine rating & run number in reV
    '''
    # Extract data
    if substructure_type == 'fixed':
        depth_inc = 'up to 60m'
    if substructure_type == 'floating':
        depth_inc = '60m and deeper'
    dist_to_POI = df[depth_inc].mean_dist_s_to_l + df[depth_inc].mean_dist_l_to_ts
    capex = df[depth_inc]['mean_capex']/1e6 # conversion of total $ for 1 GW farm to $/kW  ($ for 1 GW * (1e3 MW/1 GW) * (1e3 kW/1 MW)) = 1e6 kW
    depth = df[depth_inc]['mean_depth']
        
    fig = plt.figure()
    ax = plt.axes(projection = '3d')
    ax.view_init(azim=30)
    ax.scatter3D(depth, dist_to_POI, capex)
    ax.set_title(substructure_type)
    ax.set_xlabel('Water depth [m]')
    ax.set_ylabel('Distance to POI [km]')
    ax.set_zlabel('CapEx [$/kW]')
    #ax.dist=13
    #plt.gcf().subplots_adjust(left=0.1, top=0.5)
    plt.savefig('figures/capex_vs_WaterDepth_and_distPOI/capex' + '_' + run + '_' + domain + '_' + substructure_type + '.png', bbox_inches='tight')
    # https://stackoverflow.com/questions/31621431/move-3d-plot-to-avoid-clipping-by-margins
    #plt.clf()


for sub_type in ['fixed', 'floating']:
    print(sub_type)
    df = data[['mean_cf', 'mean_lcoe', 'latitude', 'longitude', 'state', 'mean_dist_s_to_l', 'mean_dist_l_to_ts', 'mean_dist_p_to_s', 'mean_depth', 'mean_export', 'mean_capex', 'mean_opex', 'mean_install', 'mean_hs_average', 'mean_gcf']]
    # Filter out rows where e.g. CapEx > 8000
    #df = df.loc[(df['mean_lcoe']/1e6 < 8000)]
      
    # Differentiate the data between fixed and floating depth thresholds
    df_up_to_60m= df.loc[(df['mean_depth'] < 60)] 
    df_60m_and_deeper = df.loc[(df['mean_depth'] > 60)]

    ## concatentate into one dataframe separating fixed and floating
    df_in_depth_bands = pd.concat([df_up_to_60m, df_60m_and_deeper], axis=1, keys = ['up to 60m', '60m and deeper'])
    plot_CapEx_as_function(df_in_depth_bands, sub_type, domain, run)


### Reproduce figures e.g. Fig 44 from  from Background_reading/ ORCA_Spatial_Economic_CostReductionPathway_2015thru2030_Beiter2016.pdf


