# cost_single.py

import pandas as pd
import numpy as np
from pandas.core.arrays.string_ import StringDtype
from pandas.core.indexes.base import Index

import util as u
from  util import is_numeric,  get_column_no_yield, get_all_processids, get_all_vids, get_all_processids, get_pct_from_lists


yields_df = pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\RAPID.xlsb', 'Yields')
prices_df = pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\RAPID.xlsb', 'Prices')
lists_df = pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\lists2.xlsb', 'lists2')

cost_details_unit_factor = 10.0




def get_row_num_of_components(colNum, colValue):

    rw = -1
    col = yields_df.iloc[:, colNum:colNum+1]

    for v in col.values:
        #v = ['Process ID']
        #v = ['Process Name']
        s = str(v[0]).strip()
        rw += 1
        if s == colValue:
            return rw
    return rw
  
# Utilities starts from row 38 and till 47
utilities_rownum_starts =   get_row_num_of_components(1, 'Utilities (per unit of capacity)')
# Raw Material Starts From row 47 till 468
raw_material_rownum_starts = get_row_num_of_components(1, 'Feedstocks (per unit of capacity)')   
# By Products starts from row 469
by_products_rownum_starts = get_row_num_of_components(1, 'Products (per unit of capacity)')   


# 1. identify raw materials, utilities, and by products used in this pid

themid = -1
the_product_name = ''


def get_material_used_from_yield(yields_df, prices_df, pid, material_type, vid, qtr):

    rm = ''
    
    rm_unit_price_list = []
    rm_names = []
    rm_consumption = []

    rm_list = []

    colNum = get_column_no_yield(yields_df, pid)
    #print('colNum ', colNum)

    col = yields_df.iloc[:, colNum-1:colNum]
    rw = 0
    for v in col.values:

        rw+=1
        val = str(v[0])

        # the_product_name
        if is_numeric(val) and np.float32(val) == 1.0 :
            global the_product_name 
            the_product_name = yields_df.iloc[rw-1,1]
            global themid 
            themid = yields_df.iloc[rw-1,0] 

        # raw material   
        if is_numeric(val) and np.float32(val) != 1 and  np.float32(val) > 0  and material_type == 'raw material' and rw > raw_material_rownum_starts and rw < by_products_rownum_starts: 
            
            rm_name = yields_df.iloc[rw-1,1]
            compid = yields_df.iloc[rw-1,0]
            unit_price = u.get_unit_price(prices_df, compid, vid, qtr)
            
            consumption = v[0]
            rm = v[0] * unit_price
            rm_list.append(rm)

            # By Products
            #rw > by_products_rownum_starts and np.float32(val) != 1 
        if (is_numeric(val) and np.float32(val) != 1 and (np.float32(val) > 0 or np.float32(val) < 0) ) and material_type == 'by product' and rw > by_products_rownum_starts:
                
            by_product_name = yields_df.iloc[rw-1,1]
            compid = yields_df.iloc[rw-1,0]
            unit_price = u.get_unit_price(prices_df, compid, vid, qtr)
            consumption = v[0]
            rm = consumption * unit_price
            rm_list.append(rm)
    
        # By Utilities
        # rw > utilities_rownum_starts and rw < raw_material_rownum_starts:                
        if (is_numeric(val) and np.float32(val) != 1 and (np.float32(val) > 0 or np.float32(val) < 0) ) and material_type == 'utilities' and rw > utilities_rownum_starts and rw < raw_material_rownum_starts:
                
            by_product_name = yields_df.iloc[rw-1,1]
            compid = yields_df.iloc[rw-1,0]
            unit_price = u.get_unit_price(prices_df, compid, vid, qtr)
            consumption = v[0]
            rm = consumption * unit_price
            rm_list.append(rm)
    
    return sum(rm_list)


def get_table2(pid, vid, qtr):

    """
    this is main function produces data for Cost Detail
    given a processid - pid  237, location - vid 1, period - qtr Q3-20
    """
    
    #get_product_name_from_yield(yields_df, mid)

    #mid = ut.get_mid_from_yield(yields_df, pid, 'Ethylbenzene')
    #product_name = ut.get_product_name_from_yield(yields_df,  mid)

    processIds = []
    processIds.append(pid)

    locations = []
    locations.append(vid)

    qtrs = []
    qtrs.append(qtr)
    
    
    capasity = u.get_consumption_from_yield(yields_df, pid, 'Capacity')
    capsity_list = []
    capsity_list.append(capasity)

    #Yield[BLI]/Yield[Capital Index Basis]*Prices[0]*Prices[10]
    bli_yield = u.get_consumption_from_yield(yields_df, pid, 'Battery Limits Investment')
    capital_index = u.get_consumption_from_yield(yields_df, pid, 'Capital Index Basis')
    prices_0 = u.get_unit_price(prices_df, 0, vid, qtr)
    prices_10 = u.get_unit_price(prices_df, 10, vid, qtr)

    bli = bli_yield/capital_index * prices_0 * prices_10
    battery_limit_nvestment_list = [] 
    battery_limit_nvestment_list.append(bli)

    # Total Fixed Capital
    # Yield[TFC]/Yield[Capital Index Basis]*Prices[0]*Prices[10]
    yield_tfc = u.get_consumption_from_yield(yields_df, pid, 'Total Fixed Capital')
    tfc =  yield_tfc/capital_index * prices_0 * prices_10   
    total_fixed_capital_list = [tfc]


    # Offsites Investment
    #   BLI - TFC
    off_site = bli - tfc
    off_site_list = []
    off_site_list.append(abs(off_site))
    
    # Raw Material
    # MMULT(Yield[Feedstocks],Prices), you map them by using their MID's
    # 1. identify raw material used in this pid
    # 2. get their respective mids
    # 3. get unit price from mid
    # 4. get consumption from yied
    # 5. cost = consumption * price for each raw material
    # 6. Sum of all raw material costs


    raw_material_list = []
    #sum_m = get_material_used_from_yield(pid, 'raw material')
    sum_m = get_material_used_from_yield(yields_df, prices_df, pid, 'raw material', vid, qtr)
    raw_material_list.append(sum_m)

    by_product__credit_list = []
    #sum_p = get_material_used_from_yield(pid, 'by product') * -1.0
    sum_p = get_material_used_from_yield(yields_df, prices_df, pid, 'by product', vid, qtr)* -1.0
    by_product__credit_list.append(sum_p)

    utilities_list = []
    #sum_u = get_material_used_from_yield(pid, 'utilities')
    sum_u = get_material_used_from_yield(yields_df, prices_df, pid, 'utilities', vid, qtr)
    utilities_list.append(sum_u)

    # variable costs
    # Raw Materials + By Products + Utilities + Emission Costs
    emission_costs = 0.0

    variable_costs = np.float32(sum_m) + np.float32(sum_p) + np.float32(sum_u) + emission_costs
    variable_costs_list = []
    variable_costs_list.append(variable_costs)


    #Maintenance Materials
    # (costplant[BLI]/Cost_Summary[capacity])*Yield[Maintenance Materials]*1000
    # yield_mm = 0.024
    #get_consumption_from_yield(yields_df, pid, material_name)
    yield_mm = u.get_consumption_from_yield(yields_df, pid, 'Maintenance Materials')
    mm = (bli/capasity)  * yield_mm * 1000
    maintenance_materials_list = []
    maintenance_materials_list.append(mm)

    # Operating Labor
    #(Yield[Operators]* 0.876 * Prices[9]) / Capacity] *( 10/mydivisor)
    yield_operators = u.get_consumption_from_yield(yields_df, pid, 'Operators')
    prices_9 = u.get_unit_price(prices_df, 9, vid, qtr)
    mydivisor = 1000
    ol = ((yield_operators * 0.876 * prices_9)/capasity) * (10 / 1)
    operating_labor_list=[]
    operating_labor_list.append(ol)

    # Operating Supplies
    # Lists[Country][OS]*Operating Labor
    list_country_os = get_pct_from_lists(lists_df, vid, 'cd_ospct')
    ops = list_country_os * ol
    operating_supplies_list = []
    operating_supplies_list.append(ops)

    #Maintenanace Labor
    # (BLI/Cost_single[Capacity])*Yield[Maintenance Labor]*10
    yield_ml = u.get_consumption_from_yield(yields_df, pid, 'Maintenance Labor')
    mt_labor = (bli / capasity) * yield_ml * 1000
    mt_labor_list = []
    mt_labor_list.append(mt_labor)

    # Control Laboratary
    # Operating Labor * Lists[Country][CL]
    lists_country_cl = get_pct_from_lists(lists_df, vid, 'cd_clpct')
    control_laboratary = ol  * lists_country_cl
    control_laboratary_list = []
    control_laboratary_list.append(control_laboratary)

    # Total Direct Costs
    # Variable Costs + Maintenance Materials + Operating Labor + Operating Supplies + Maintenance Labor +Control Laboratory
    total_direct_cost = variable_costs + mm + ol + ops + mt_labor + control_laboratary
    total_direct_cost_list = []
    total_direct_cost_list.append(total_direct_cost)

    #Plant Overhead
    # (Operating Labor + Maitenance Labor + Control Laboratory) * Lists[Country][OH]
    lists_country_oh = get_pct_from_lists(lists_df, vid, 'cd_ohpct')
    plant_overhead = (ol + mt_labor + control_laboratary) * lists_country_oh
    plant_overhead_list = []
    plant_overhead_list.append(plant_overhead)

    # Taxes and Insurance 
    # (costsingle[TFC]/yieldplant[Capacity])*Lists[Country][TI]*(1000/mydivisor)
    lists_country__ti = get_pct_from_lists(lists_df, vid, 'cd_tipct')
    taxes_and_insurance = (tfc/capasity)  * lists_country__ti * (1000)
    taxes_and_insurance_list = []
    taxes_and_insurance_list.append(taxes_and_insurance)

    # Plant Cash Costs
    # Total Direct Costs + Plant Overhead + Taxes and Insurance

    plant_cash_costs = total_direct_cost + plant_overhead + taxes_and_insurance
    plant_cash_costs_list = []
    plant_cash_costs_list.append(plant_cash_costs)

    # Depreciation
    # ((Costsingle[TFC]*10)/(Costsingle[Capacity])*10
    
    depriciation = ((tfc * 10)/capasity) * 10
    depriciation_list = []
    depriciation_list.append(depriciation)

    # Plant Gate Cost
    # Plant Cash Costs + Depreciation
    
    plant_gate_cost = plant_cash_costs + depriciation
    plant_gate_cost_list = []
    plant_gate_cost_list.append(plant_gate_cost)

    # G&A, Sales, Research
    # costsingle[Price]*yield(G&A, Sales, Research)
    # get price for productid  ethyline = 674 from price tab
    # todo

    cost_single_price = u.get_unit_price(prices_df, themid, vid, qtr)
    yield_gsa = u.get_consumption_from_yield(yields_df, pid, 'G+A, Sales, Res.')

    gsa =  cost_single_price * yield_gsa
    gsa_list = []
    gsa_list.append(gsa)

    # Production Cost
    # Plant Gate Cost + G&A, Sales, Research

    production_cost = plant_gate_cost + gsa
    production_cost_list = []
    production_cost_list.append(production_cost)

    # Price  476.86
    # it is nothing but the material in byproduct 
    # that has volume 1. as it is the final product of the process
    price = u.get_unit_price(prices_df, themid, vid, qtr)
    price_list =[]
    price_list.append(price)

    # Cash Margin
    # Price - Plant Cash Costs
    cash_margin = price - plant_cash_costs
    cash_margin_list = []
    cash_margin_list.append(cash_margin)

    # RawsMM$
    # (Raw Materials * yieldplant[Capacity])/1000
    raw_mms = (sum_m * capasity)/1000
    raw_mms_list = []
    raw_mms_list.append(raw_mms)

    # ByProdMM$
    # (By Products * Cost_Single[Capacity])/1000
    by_product_mms = (sum_p * capasity)/1000
    by_product_mms_list = []
    by_product_mms_list.append(by_product_mms)

    # UtilMM$
    # (Utilities * yieldplant[Capacity])/1000

    util_mms = (sum_u * capasity)/1000
    util_mms_list = []
    util_mms_list.append(util_mms)

    # RevMM$
    # (Price * yieldplant[Capacity])/1000
    rev_mms = (price * capasity)/1000
    rev_mms_list = []
    rev_mms_list.append(rev_mms)

    # FixedMM$
    # ((Plant Cash Costs - Varaiable Costs)*costsingle[Capacity])/1000
    fixed_mms = ((plant_cash_costs - variable_costs)*capasity)/1000
    fixed_mms_list = []
    fixed_mms_list.append(fixed_mms)

    # GSAMM$
    # (G&A, Sales, Research * costsingle[Capacity])/1000
    gsa_mms = (gsa * capasity)/1000
    gsa_mms_list = []
    gsa_mms_list.append(gsa_mms)

    # COGSMM$
    # (-1 * RawsMM$) - UtilMM$ - FixMM$ - GSAMM$
    cog_mms = (-1 * raw_mms) - util_mms - fixed_mms-gsa_mms
    cog_mms_list =[]
    cog_mms_list.append(cog_mms)

    # ProdRevMM$
    # RevMM$ - ByProdMM$
    prod_rev_mms = rev_mms - by_product_mms
    prod_rev_mms_list = []
    prod_rev_mms_list.append(prod_rev_mms)

    # WC
    # RawsMM$+UtilMM$+FixMM$+RevMM$-ByProdMM$

    wc = raw_mms + util_mms + fixed_mms + rev_mms - by_product_mms 
    wc_list = []
    wc_list.append(wc)

    # Total Fixed Capital (w/ Owners Costs)
    # TFC * (1+ Yield[Owners Costs])
    yield_owners_cost = u.get_consumption_from_yield(yields_df, pid, 'Owners Costs')
    total_fixed_capital_with_owners_cost = tfc * (1 + yield_owners_cost)
    total_fixed_capital_with_owners_cost_list=[]
    total_fixed_capital_with_owners_cost_list.append(total_fixed_capital_with_owners_cost)




    

    units = ['ton']
    products = []
    products.append(the_product_name)

    mids = []
    mids.append(themid)

    table1 = pd.DataFrame({
                    'product': products,
                    'pid': processIds,
                    'VID': locations, 
                    'year': qtrs, 
                    'unit': units, 
                    'MID': mids,
                    
                    'Capacity': capsity_list
                    , 'Battery Limit Investment': battery_limit_nvestment_list
                    , 'Total Fixed Capital': total_fixed_capital_list
                    , 'Offsites Investment': off_site_list
                    , 'Raw Materials': raw_material_list
                    , 'By Product Credits': by_product__credit_list
                    , 'Utilities': utilities_list
                    , 'Variable Costs': variable_costs_list
                    , 'Maintenance Materials' : maintenance_materials_list
                    , 'Operating Labor': operating_labor_list
                    , 'Operating Supplies': operating_supplies_list
                    , 'Maintenanace Labor': mt_labor_list
                    , 'Control Laboratary':control_laboratary_list
                    , 'Total Direct Costs':total_direct_cost_list
                    , 'Plant Overhead':plant_overhead_list
                    , 'Taxes and Insurance ': taxes_and_insurance_list
                    , 'Plant Cash Costs':plant_cash_costs_list
                    , 'Depreciation':depriciation_list
                    , 'Plant Gate Cost':plant_gate_cost_list
                    , 'G&A, Sales, Research': gsa_list
                    , 'Production Cost': production_cost_list
                    , 'Price': price_list
                    , 'Cash Margin': cash_margin_list
                    , 'RawsMM$' : raw_mms_list
                    , 'ByProdMM$' : by_product_mms_list
                    , 'UtilMM$' : util_mms_list
                    , 'RevMM$' : rev_mms_list
                    , 'FixedMM$': fixed_mms_list
                    , 'GSAMM$' : gsa_mms_list
                    , 'COGSMM$':cog_mms_list
                    , 'ProdRevMM$': prod_rev_mms_list
                    , 'WC': wc_list
                    , 'Total Fixed Capital (w Owners Costs)':total_fixed_capital_with_owners_cost_list

                    })

    return table1


small_dfs = []

process_ids = [237, 238, 1797]
# all processes from yield
#process_ids = yields_df.iloc[4-2,4:]
process_ids2 = get_all_processids(yields_df)
#print(list(process_ids2))

vids = [1]
# region in prices get all the rows of 3 rd column
#vids = get_all_vids(prices_df)

periods = ['Q3-20', 'Q4-20']
#periods = get_all_periods(prices_df)

count = 0
for pid in process_ids:
    for vid in vids:
        for period in periods:
            count += 1
            tbl = get_table2(pid, vid, period)
            small_dfs.append(tbl)

large_df = pd.concat(small_dfs, ignore_index=True)
large_df.to_csv("C:\\Users\\HP\\Desktop\\Rapid\\costSingle_table1.csv", index=False)
print('Done')








