# -*- coding: utf-8 -*-
"""

Extrapolate the reV/NRWAL cost modelling output into future years, using an assumed learning curve.
More specifically, extrapolate lcoe, capex, opex only (the only parameters we have cost reduction values for) and save to gpkg data for 2040-2050.

Created on Mon Aug  7 13:51:27 2023

@author: rrolph
"""



#### Note:  lines with !!! still need editing

import geopandas as gpd
import yaml

### Read in input data
gpkg_filepath = r'C:\\Users\\rrolph\\OneDrive - NREL\\Projects\\BOEM_IAA_NationalLCOE\\analyzing_results\\outfiles_from_eagle\\'
gpkg_filepath_reduced_costs = r'C:\Users\rrolph\OneDrive - NREL\Projects\BOEM_IAA_NationalLCOE\analyzing_results\new_gpkg_files_with_cost_reductions_applied\\'



### Read in learning curves from NRWAL
# remote: https://github.com/NREL/NRWAL/blob/main/NRWAL/analysis_library/osw_2023/cost_reductions.yaml
# local: Projects/BOEM_IAA_NationalLCOE/analyzing_results
cost_reductions_yaml = r'C:\\Users\\rrolph\\OneDrive - NREL\\Projects\\BOEM_IAA_NationalLCOE\\analyzing_results\\cost_reductions.yaml'
with open(cost_reductions_yaml, 'r') as stream:
    cost_reductions_dict = yaml.safe_load(stream)
# data['fixed']['capex_2030']



### Apply cost reductions by looping through domains and nested loop of years
domains = ['gulf',  'hi', 'ma', 'na', 'sa', 'wc']
#domains = ['na'] # for debugging !!!
rating = '2_20MW' # Apply cost reduction to most recent available rating
projected_years = ['2040', '2045', '2050']

for domain in domains:
    print(domain)
    if domain == 'gulf':
        rating = '2_17MWlowSP_gulf_35'
        ifile = gpkg_filepath + rating + '.gpkg'
    else:
        ifile = gpkg_filepath + rating + '_' + domain + '.gpkg'
    data = gpd.read_file(ifile)
    
    
    ## Apply reductions to LCOE, CapEx, and OpEx
    for year in projected_years:
        
        data_cost_reduction_applied = data.copy(deep=True) # initialize new data  
        
        
        ## Read cost reduction values for current year
        # CapEx
        capex_cost_reduction_fixed = cost_reductions_dict['fixed']['capex_' + year]
        capex_cost_reduction_floating = cost_reductions_dict['floating']['capex_' + year]
        # OpEx
        opex_cost_reduction_fixed = cost_reductions_dict['fixed']['opex_' + year]
        opex_cost_reduction_floating = cost_reductions_dict['floating']['opex_' + year]
            
        
        ### Reduce capex and opex
        ## CapEx            
        # fixed 
        data_cost_reduction_applied.loc[data_cost_reduction_applied.depth < 60, 'capex_kw'] = data.loc[data.depth < 60, 'capex_kw'] * (1 - capex_cost_reduction_fixed)
        # floating
        data_cost_reduction_applied.loc[data_cost_reduction_applied.depth > 60, 'capex_kw'] = data.loc[data.depth > 60, 'capex_kw'] * (1 - capex_cost_reduction_floating)
            
        ## Opex
        # fixed
        data_cost_reduction_applied.loc[data_cost_reduction_applied.depth < 60, 'opex_kw'] = data.loc[data.depth < 60, 'opex_kw'] * (1 - opex_cost_reduction_fixed)
        # floating
        data_cost_reduction_applied.loc[data_cost_reduction_applied.depth > 60, 'opex_kw'] = data.loc[data.depth > 60, 'opex_kw'] * (1 - opex_cost_reduction_floating)
            
            
        ### Calculate new LCOE using the newly reduced capex and opex values
        ## !!!lcoe_fcr: (capex * fixed_charge_rate + opex) / (cf_mean * 1000 * 8760) # opex is 1GW plant cost, AEP is now 1GW
        fixed_charge_rate = 0.0767 # div by 100. e.g. 7.67 prcnt = 0.0767 here.
        # ($/kW)*(1e3 kW/ 1 MW) --> $/MW
        data_cost_reduction_applied['lcoe'] = 1e3*(data_cost_reduction_applied['capex_kw'] * fixed_charge_rate + data_cost_reduction_applied['opex_kw']) / (data_cost_reduction_applied['mean_cf'] * 8760 )
            
        # Save dataframe with reduced costs to file. note that capex, opex and lcoe no longer correspond with some other outdata of reV now (e.g. export)
        data_cost_reduction_applied.to_file(gpkg_filepath_reduced_costs + domain + '_' + rating + '_' + year + '.gpkg', driver='GPKG')
            



