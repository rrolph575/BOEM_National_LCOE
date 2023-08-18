# -*- coding: utf-8 -*-
"""

Extrapolate the reV/NRWAL cost modelling output into future years, using an assumed learning curve.
More specifically, extrapolate lcoe, capex, opex only (the only parameters we have cost reduction values for) and save to gpkg data for 2040-2050. Also calculates new lcoe, capex, and opex values based on different learning curve scenarios.

# Conservative:  most expensive scenario
# Mid: middle (baseline)
# Advanced: least expensive scenario

Created on Mon Aug  7 13:51:27 2023

@author: rrolph
"""



import geopandas as gpd
import yaml
import numpy as np

### Read in input data
gpkg_filepath = r'C:\\Users\\rrolph\\OneDrive - NREL\\Projects\\BOEM_IAA_NationalLCOE\\analyzing_results\\outfiles_from_eagle\\'
gpkg_filepath_reduced_costs = r'C:\Users\rrolph\OneDrive - NREL\Projects\BOEM_IAA_NationalLCOE\analyzing_results\new_gpkg_files_with_cost_reductions_applied\\'



### Read in learning curves from NRWAL
# remote: https://github.com/NREL/NRWAL/blob/main/NRWAL/analysis_library/osw_2023/cost_reductions.yaml
# local: Projects/BOEM_IAA_NationalLCOE/analyzing_results
cost_reductions_yaml = r'C:\\Users\\rrolph\\OneDrive - NREL\\Projects\\BOEM_IAA_NationalLCOE\\analyzing_results\\cost_reductions.yaml'
with open(cost_reductions_yaml, 'r') as stream:
    cost_reductions_dict = yaml.safe_load(stream)
# data['fixed_mid_scenario']['capex_2030'] # fixed_advanced_scenario and fixed_conservative_scenario (also replace the word 'fixed' with 'floating' for the floating learning curve values)



# Adjust the cost reductions so that they are applicable to apply to output of mid scenario, which is the only scenario run by reV/NRWAL.  The cost reudctions for the mid scenario have also only been run through 2035, so the 2040, 2045, and 2050 will need to be applied also to the mid scenario but placeholders of 0 should be in cost_reduction_floating/fixed for 2025, 2030, and 2035 years for mid scenario (as to not change the results from reV which has already applied those cost reductions).





### Apply cost reductions by looping through domains and nested loop of years
domains = ['gulf',  'hi', 'ma', 'na', 'sa', 'wc']
year_range = np.arange(2025,2055,5)
projected_years = np.arange(2040, 2055, 5)
scenarios = ['conservative', 'mid', 'advanced']

for domain in domains:
   
    for ind, year in enumerate(year_range):
        
        ## Read in mid scenarios cost reduction values.  These will be used to calculate the cost reductions applied, which are relative to these mid scenario values.
        # CapEx
        capex_cost_reduction_fixed_mid = cost_reductions_dict['fixed_mid_scenario']['capex_' + str(year)]
        capex_cost_reduction_floating_mid = cost_reductions_dict['floating_mid_scenario']['capex_' + str(year)]
        # OpEx
        opex_cost_reduction_fixed_mid = cost_reductions_dict['fixed_mid_scenario']['opex_' + str(year)]
        opex_cost_reduction_floating_mid = cost_reductions_dict['floating_mid_scenario']['opex_' + str(year)]
        
        
        ### Identify ifile data based on year (ind) and domain
        print(domain)
        if domain == 'gulf': # Apply cost reduction to most recent available rating
            strings = ['0_12MW_gulf', '1_17MWlowSP_gulf_30', '2_17MWlowSP_gulf_35', '2_17MWlowSP_gulf_35', '2_17MWlowSP_gulf_35', '2_17MWlowSP_gulf_35'] # the ifiles for projected years are applied to the last rating (2_17MW)
            ifile = gpkg_filepath + strings[ind] + '.gpkg'
        else:
            strings = ['0_12MW', '1_15MW', '2_20MW', '2_20MW', '2_20MW', '2_20MW']
            ifile = gpkg_filepath + strings[ind] + '_' + domain + '.gpkg'
                
        ### Read data
        print("Input file to be modified: " + ifile)
        data = gpd.read_file(ifile)
        data_cost_reduction_applied = data.copy(deep=True) # initialize new dataset to be modified

           
        for scenario in scenarios:
            
            ## Define ofile where the modified costs will be written based on scenario, year, and domain
            ofile = gpkg_filepath_reduced_costs + domain + '_' + str(year) + '_' + scenario + '.gpkg'
            print('Output file to be saved with modified costs based on scenario: ' + ofile)
            
            
            ## Calculate the RELATIVE cost reduction value (relative to mid scenario)
            if scenario == 'mid':
                if year in projected_years:
                    # CapEx
                    capex_cost_reduction_fixed = capex_cost_reduction_fixed_mid
                    capex_cost_reduction_floating = capex_cost_reduction_floating_mid
                    # OpEx
                    opex_cost_reduction_fixed = opex_cost_reduction_fixed_mid
                    opex_cost_reduction_floating = opex_cost_reduction_floating_mid
                else: 
                    capex_cost_reduction_fixed = 0 
                    capex_cost_reduction_floating = 0 
                    opex_cost_reduction_fixed = 0
                    opex_cost_reduction_floating = 0
            
            if scenario == 'conservative' or 'advanced':
                # CapEx
                capex_cost_reduction_fixed = capex_cost_reduction_fixed_mid - cost_reductions_dict['fixed_' + scenario + '_scenario']['capex_' + str(year)]
                capex_cost_reduction_floating = capex_cost_reduction_floating_mid - cost_reductions_dict['floating_' + scenario + '_scenario']['capex_' + str(year)]
                # OpEx
                opex_cost_reduction_fixed = opex_cost_reduction_fixed_mid - cost_reductions_dict['fixed_' + scenario + '_scenario']['opex_' + str(year)]
                opex_cost_reduction_floating = opex_cost_reduction_floating_mid - cost_reductions_dict['floating_' + scenario + '_scenario']['opex_' + str(year)]
        

            
            ### Modify capex and opex data
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
            ## lcoe = (capex * fixed_charge_rate + opex) / (cf_mean * 1000 * 8760) # opex is 1GW plant cost, AEP is now 1GW
            fixed_charge_rate = 0.0767 # div by 100. e.g. 7.67 prcnt = 0.0767 here.
            # ($/kW)*(1e3 kW/ 1 MW) --> $/MW
            data_cost_reduction_applied['lcoe'] = 1e3*(data_cost_reduction_applied['capex_kw'] * fixed_charge_rate + data_cost_reduction_applied['opex_kw']) / (data_cost_reduction_applied['mean_cf'] * 8760)
                
            # Save dataframe with reduced costs to file. note that capex, opex and lcoe no longer correspond with some other outdata of reV now (e.g. export)
            data_cost_reduction_applied.to_file(ofile, driver='GPKG')
                
    
    
    
