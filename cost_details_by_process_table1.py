# cost_details_by_process_table1.py
"""
Aim: Develop a python module to produce the data for the 
Cost_Details_by_Process  in RAPID V4 (1)

Table 1: Cost of Raw Material, By-product, and Utilities

"""

import pandas as pd
import numpy as np

import util as u


yields_df = pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\RAPID.xlsb', 'Yields')
unitprice_df= pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\RAPID.xlsb', 'Prices')
lists_df = pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\lists2.xlsb', 'lists2')


  
# Utilities starts from row 38 and till 47
utilities_rownum_starts =   u.get_row_num_of_components(yields_df, 1, 'Utilities (per unit of capacity)')
# Raw Material Starts From row 47 till 468
raw_material_rownum_starts = u.get_row_num_of_components(yields_df, 1, 'Feedstocks (per unit of capacity)')   
# By Products starts from row 469
by_products_rownum_starts = u.get_row_num_of_components(yields_df, 1, 'Products (per unit of capacity)')   


def get_table1(pid, vid, qtr):

    r = u.get_column_no_yield(yields_df, pid)    
    col = yields_df.iloc[:, r-1:r]

    rw = 0
    
    section = []
    components = []
    unit_cost = []
    units_m2 = []
    units_m1 = []
    unit_consumption = []
    net_cost = []
    processIds = []
    locations = []
    qtrs = []
    basis = []
    products = []

    # raw material col = 1 row no from 50 to 470
    rm_names = []
    rm_consumption=[]
    rm_unit_price_list = []
    rm_consumption_unit = []

    # utilities row from 40 to 48
    utl_names = []
    utl_consumption = []
    utl_unit_price_list = []
    utl_unit = []

    # by product row no > 470
    by_product_names = []
    by_product_consumption=[]
    by_product_unit_price_list = []
    by_product_unit = []

    for v in col.values:
        
        rw+=1
        val = str(v[0])
            
        if  u.is_numeric(val) and (np.float32(val) > 0 or np.float32(val) < 0 ):
            
            # raw material
            #if rw > 48 and rw < 468: 
            if rw > raw_material_rownum_starts and rw < by_products_rownum_starts: 
                rm_name = yields_df.iloc[rw-1,1]
                compId = yields_df.iloc[rw-1,0]
                #mid[compId] = rm_name
                #get_unit_price(pricedf, mid, vid, period)
                rm_unit_price_list.append(u.get_unit_price(unitprice_df, compId, vid, qtr))
                rm_names.append(rm_name)
                rm_consumption.append(v[0])

                unit = yields_df.iloc[rw-1,2]
                unit = unit[:-5]
                rm_consumption_unit.append(unit)
                
            # get by products startts from row 467 and consumption is not 1    
            elif rw > by_products_rownum_starts and np.float32(val) != 1 :
                rm_name = yields_df.iloc[rw-1,1]
                compId = yields_df.iloc[rw-1,0]
                #mid[compId] = rm_name
                by_product_unit_price_list.append(u.get_unit_price(unitprice_df, compId, vid, qtr))
                by_product_names.append(rm_name)
                by_product_consumption.append(v[0]*-1)
                unit = yields_df.iloc[rw-1,2]
                unit = unit[:-5]
                by_product_unit.append(unit)
            
            # utilities    
            #elif rw > 37 and rw < 47: # utilities
            elif rw > utilities_rownum_starts and rw < raw_material_rownum_starts: 
                #print(rw, v[0])
                rm_name = yields_df.iloc[rw-1,1]
                #print(rm_name)
                compId = yields_df.iloc[rw-1,0]
                #mid[compId] = rm_name
                utl_unit_price_list.append(u.get_unit_price(unitprice_df, compId, vid, qtr))
                utl_names.append(rm_name)
                utl_consumption.append(v[0])
                unit = yields_df.iloc[rw-1,2]
                unit = unit[:-5]
                utl_unit.append(unit)


    section = ['RAW MATERIAL' for i in range(len(rm_names)) ]  + ['By Product Credit' for i in range(len(by_product_names)) ]   + ['Utilities' for i in range(len(utl_names)) ] 
    components = rm_names + by_product_names + utl_names 
    unit_cost = rm_unit_price_list + by_product_unit_price_list + utl_unit_price_list 
    units_m2 = rm_consumption_unit + by_product_unit + utl_unit
    units_m1 = ['US$/'+k for k in units_m2]
    unit_consumption = rm_consumption + by_product_consumption + utl_consumption
    net_cost = [a*b for a,b in zip(unit_cost,unit_consumption)]
    processIds = [pid for k in section]
    vids = [vid for k in section]
    locations = [u.get_location_from_vid(lists_df, vid) for k in section]
    qtrs = [qtr for k in section]
    basis = ['IHSM' for k in section]
    products = [u.get_product_name_from_pid(yields_df, pid) for k in section]

    table1 = pd.DataFrame({
                    'PRODUCT': products,
                    'BASIS': basis, 
                    'PROCESSID': processIds,
                    'PERIOD': qtrs, 
                    'VID': vids,
                    'LOCATION': locations, 
                    
                    'SECTION': section,
                    'COMPONENTS': components,
                    'UNIT_COST': unit_cost,
                    'M-1': units_m1,
                    'UNIT_CONSUMPTION(PER TON)': unit_consumption,
                    'M-2': units_m2,
                    'COST(US$/TON)': net_cost
                        })

    return table1


pids = u.get_all_processids(yields_df)
pids2 = [237]
# for test only take 6 pids replace pids2 with pids in production
nos = 0
for p in pids:
    nos +=1
    pids2.append(p)
    if nos > 3:
        break

vids = u.get_all_vids(unitprice_df)
periods = u.get_all_periods(unitprice_df)

small_dfs = []

for the_pid in pids2:
    for the_vid in vids:
        for the_qtr in periods:
            tbl = get_table1(the_pid, the_vid, the_qtr)
            small_dfs.append(tbl)

large_df = pd.concat(small_dfs, ignore_index=True)
large_df.to_csv("C:\\Users\\HP\\Desktop\\Rapid\\costDetails_table1.csv", index=False)
print('Done')

