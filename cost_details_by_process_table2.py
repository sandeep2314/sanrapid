# cost_details_by_process_table2.py
import pandas as pd
import numpy as np
from pandas.core.arrays.string_ import StringDtype
from pandas.core.indexes.base import Index

import util as u


cost_single_df= pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\RAPID.xlsb', 'CostSingle')
yields_df = pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\RAPID.xlsb', 'Yields')
prices_df= pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\RAPID.xlsb', 'Prices')
lists_df = pd.read_excel('C:\\Users\\HP\\Desktop\\Rapid\\lists2.xlsb', 'lists2')

cost_details_unit_factor = 10.0

def get_data_from_cost_single(sction, pid, mid, vid, qtr):
    """
    helper function to get data from Cost Single Tab in RAPID excel workbook
    given section, processid, material id, locationId, Period
    """
    val = -1
    val = cost_single_df[  (cost_single_df['Year']==qtr) 
                            & (cost_single_df['VID']==vid)
                            & (cost_single_df['MID']==mid)
                            & (cost_single_df['PID']==pid)
                        ].head(1)
    
    result = val[[sction]]
    return result[sction].to_string(index=False)

#print(get_data_from_cost_single('Capacity', 237, 674, 1, 'Q3-20'))

def get_table2(pid, vid, qtr):

    """
    this is main function produces data for Cost Details By Process 
    for Overall Cost Structure
    
    """

    

    section = ['Capacity'
                , 'Investment (US$ Million)' 
                , 'Investment (US$ Million)', 'Investment (US$ Million)'
                , 'Production Costs (US$/ton)', 'Production Costs (US$/ton)', 'Production Costs (US$/ton)', 'Production Costs (US$/ton)'
                , 'Variable Costs', 'Variable Costs', 'Variable Costs', 'Variable Costs', 'Variable Costs', 'Variable Costs'
                , 'Total Direct Costs', 'Total Direct Costs', 'Total Direct Costs'
                , 'Plant Cash Costs', 'Plant Cash Costs'
                , 'Plant Gate Cost', 'Plant Gate Cost'
                , 'Production Costs'
                , 'Cash Margin'
                ]

    components = ['Capacity (Thous. ton/yr)', 'Battery Limits'
        , 'Off Sites', 'Investment (US$ Million)'
        , 'Raw Materials'
        , 'By Product Credits'
        , 'Utilities'
        , 'Carbon'
        , 'Variable Costs'
        , 'Maintenance Materials'
        , 'Operating Supplies'
        , 'Operating Labor'
        , 'Maintenance Labor'
        , 'Control Laboratory'
        , 'Total Direct Costs'
        , 'Plant Overhead'
        , 'Taxes And Insurance'
        , 'Plant Cash Costs'
        , 'Depreciation'
        , 'Plant Gate Cost'
        , 'G + A, Sales, Res.'
        , 'Production Costs'
        , 'Cash Margin'
        ]
    
    mid = u.get_mid_from_yield_pid(yields_df, pid)

    # capsity = get_data_from_cost_single(cmpnts[0], pid, mid, vid, qtr)
    capsity = get_data_from_cost_single('Capacity', pid, mid, vid, qtr)
    capsity_full = -1
    
    if u.is_numeric(capsity):
        capsity_full = np.float32(capsity)
    
    capsity_half = capsity_full * 0.5
    capsity_double = capsity_full * 2.0

    # 888
    # Battery Limits Investment get directly from cost details
    battery_limits =  get_data_from_cost_single('Battery Limits Investment', pid, mid, vid, qtr)
    battery_limits_full =  battery_limits
    
    # for half capacity:
    #  Cost Summary [Battery Limits Investment] * (half capacity/ IHS capacity) ^ yield[BLI Scaled Down]  

    # 888 yield[BLI Scaled Down] = 0.620 'Battery Limits, Down'
    #bli_scaled_down = 0.620
    #bli_scaled_down = get_value_from_yield(pid, 'Battery Limits, Down')
    bli_scaled_down = u.get_consumption_from_yield(yields_df, pid, 'Battery Limits, Down')
    bli_scaled_up = u.get_consumption_from_yield(yields_df, pid, 'Battery Limits, Up')

    if u.is_numeric(battery_limits):
        battery_limits_full = np.float32(battery_limits)
    
    battery_limits_half = (battery_limits_full*(pow((capsity_half/capsity_full), bli_scaled_down)))
    battery_limits_double = (battery_limits_full*(pow((capsity_double/capsity_full), bli_scaled_up)))

   
    offsites_str = get_data_from_cost_single('Offsites Investment', pid, mid, vid, qtr)
    if u.is_numeric(offsites_str):
        offsites_full = np.float32(offsites_str)

    #Investment 
    # for half capacity: 
    # Cost Summary [Battery Limits Investment] * (half capacity/ IHS capacity) ^ yield[BLI Scaled Down]  
    
    #Cost Summary [Battery Limits Investment] * (half capacity/ IHS capacity) ^ yield[BLI Scaled Down]
    
    investment_full = (battery_limits_full + offsites_full)
    #  87.0 * pow(260.8156128/521.6312256, .570)
    tfc_down = u.get_consumption_from_yield(yields_df, pid, 'Total Fixed Capital, Down')
    tfc_up = u.get_consumption_from_yield(yields_df, pid, 'Total Fixed Capital, Up')
    investment_half = (investment_full) * (pow((capsity_half/capsity_full), tfc_down))
    investment_double = (investment_full)* (pow((capsity_double/capsity_full), tfc_up))
    
    offsites_half = investment_half - battery_limits_half 
    offsites_double = investment_double - battery_limits_double


# Production Costs   get from table1
    # 777 Raw Materials SUM(Raw Materials)
    # By Product - Sum(By Product)
    # Utilities  - SUM(utilities)
    # Carbon = 0

    # RAW MATERIAL, Utilities, By Product Credit
    #get_sum_section(pid, section, qtr, vid, df)
    #raw_material = get_sum_section(pid, 'RAW MATERIAL', qtr, vid, table1_df)
    raw_material = u.get_material_used_from_yield(yields_df, prices_df, pid, 'raw material', vid, qtr)
    raw_material_full = raw_material
    raw_material_half = raw_material
    raw_material_double = raw_material
    
    #by_product_credits = get_sum_section(pid, 'By Product Credit', qtr, vid, table1_df) * -1.0
    by_product_credits = u.get_material_used_from_yield(yields_df, prices_df, pid, 'by product', vid, qtr) * -1.0
    by_product_credits_full = by_product_credits
    by_product_credits_half = by_product_credits
    by_product_credits_double = by_product_credits
       
    utilities = -1
    #utilities_full = get_sum_section(pid, 'Utilities', qtr, vid, table1_df)
    utilities_full = u.get_material_used_from_yield(yields_df, prices_df, pid, 'utilities', vid, qtr) 
    utilities_half = utilities_full
    utilities_double = utilities_full

    carbon = 0
    carbon_full = carbon
    carbon_half = carbon
    carbon_double = carbon

#Variable Costs
#    Variable Costs - SUM of -
#               "SUM(Raw Materials)
#                SUM(By Product Credits)
#                SUM(Utilities)
#                SUM(Carbon)"
#               Control Laboratory
#    Maintenance Materials
#    Operating Supplies
#    Operating Labor
#    Maintenance Labor
#    Control Laboratory

    variable_cost = raw_material_full + by_product_credits_full +utilities_full + carbon_full

    # 777
    # if capacity = 0 then 0 else 
    # ((Battery Limits*yields[Maintenance Materials]) / (Capacity))  *  Cost Details[Unit Factor] & Cost Summary[Maintenance Materials]
    #yields_maintenance_materials = 0.024
    yields_maintenance_materials = u.get_consumption_from_yield(yields_df, pid, 'Maintenance Materials')
    #cost_details_unit_factor_str = get_data_from_cost_single(['Unit Factor'], pid, mid, vid, qtr)
    cost_details_unit_factor_str = 10.0
    
  
    #cost_details_unit_factor = -1
    #if is_numeric(cost_details_unit_factor_str):
    #    cost_details_unit_factor = np.float32(cost_details_unit_factor_str)

    cmp = ['Maintenance Materials']
    cost_summary_maintenance_materials_str = get_data_from_cost_single(cmp[0], pid, mid, vid, qtr)
  
    cost_summary_maintenance_materials = -1    
    if u.is_numeric(cost_summary_maintenance_materials_str):
        cost_summary_maintenance_materials = np.float32(cost_summary_maintenance_materials_str)

    #battery_limits_full = battery_limits
    #yields_maintenance_materials
    #yields_maintenance_materials = 0.024 # value to be get from Yield Sheet
    ####

   # maintenance_materials_full = ((battery_limits_full * yields_maintenance_materials)/capsity_full) * cost_details_unit_factor &  cost_summary_maintenance_materials
    #maintenance_materials_full = ((battery_limits_full 
    # * yields_maintenance_materials)/capsity_full) 
    # * cost_details_unit_factor *  cost_summary_maintenance_materials

    #yields_maintenance_materials

    maintenance_materials_full = cost_summary_maintenance_materials
    maintenance_materials_half = ((battery_limits_half 
                    * np.float32(yields_maintenance_materials))/capsity_half) * cost_details_unit_factor 
    maintenance_materials_double = ((battery_limits_double 
                    * np.float32(yields_maintenance_materials))/capsity_double) * cost_details_unit_factor 
        
    # operating Labor(2.64) * Cost details [OS_PCT] & Cost Summary [Operating Supplies](0.26)
    # 2.64
    # Cost details [OS_PCT]?

    cmp = ['Operating Labor', 'Operating Supplies']

    operating_labor_str = get_data_from_cost_single(cmp[0], pid, mid, vid, qtr)
    operating_labor = -1.0
    if u.is_numeric(operating_labor_str):
        operating_labor = np.float32(operating_labor_str)

    cost_summary_operating_supplies_str = get_data_from_cost_single(cmp[1], pid, mid, vid, qtr)
    cost_summary_operating_supplies = -1.0
    if u.is_numeric(cost_summary_operating_supplies_str):
        cost_summary_operating_supplies = np.float32(cost_summary_operating_supplies_str)
    
    #operating_supplies_full = operating_labor * cost_summary_operating_supplies
    operating_supplies_full =  cost_summary_operating_supplies
    operating_supplies_half = operating_supplies_full * 2.0
    operating_supplies_double = operating_supplies_full * 0.5

    # Operating Labor
    # if capacity = 0 then 0 else 
    # (Cost Details[NumOps]*0.876*Cost Details[LaborRate])/Capacity)*Cost Detsils [Unitfactor] & Cost Summary [Operating Labor]
    
    cost_details_NumOps = -1.0 # 11
    cost_details_labor_rate = -1.0
    #operating_labor_full2 = ((cost_details_NumOps * 0.876 * cost_details_labor_rate)/capsity_full) * cost_details_unit_factor * operating_labor  
    operating_labor_full2 = operating_labor
    operating_labor_half2 = operating_labor_full2 * 2.0
    operating_labor_double2 = operating_labor_full2 * 0.5

    # 777 Maintenance Labor
    # ((Battery Limits * Cost Details[ML_PCT])/Capacity) * Cost Details[Units Factor]
    # to get Cost Details[ML_PCT] = 0.02, 
    #cost_details_ml_pct = 0.016
    cost_details_ml_pct = u.get_consumption_from_yield(yields_df, pid, 'Maintenance Labor')
    
    cost_summary_maintainence_labor_str = get_data_from_cost_single('Maintenance Labor', pid, mid, vid, qtr)
    cost_summary_maintainence_labor = -1.0
    if u.is_numeric(cost_summary_maintainence_labor_str):
        cost_summary_maintainence_labor = np.float32(cost_summary_maintainence_labor_str)
    
    maintenance_labor_full = cost_summary_maintainence_labor
    maintenance_labor_half = ((battery_limits_half * cost_details_ml_pct ) /capsity_half) * cost_details_unit_factor
    maintenance_labor_double = ((battery_limits_double * cost_details_ml_pct ) /capsity_double) * cost_details_unit_factor

    #777 'Control Laboratory'
    control_laboratory_str = get_data_from_cost_single('Control Laboratory', pid, mid, vid, qtr)
    control_laboratory = -1.0
    if u.is_numeric(control_laboratory_str):
        control_laboratory = np.float32(control_laboratory_str)
    
    control_laboratory_full = control_laboratory
    control_laboratory_half = control_laboratory_full * 2.0
    control_laboratory_double = control_laboratory_full * 0.5

    # 777 'Total Direct Costs'
    # sum of  operating_labor_full2 + maintenance_labor_full + control_laboratory_full
    total_direct_cost_full =  variable_cost + maintenance_materials_full + operating_supplies_full + operating_labor_full2 + maintenance_labor_full + control_laboratory_full
    total_direct_cost_half =  variable_cost + maintenance_materials_half + operating_supplies_half + operating_labor_half2 + maintenance_labor_half + control_laboratory_half
    total_direct_cost_double = variable_cost + maintenance_materials_double + operating_supplies_double + operating_labor_double2 + maintenance_labor_double + control_laboratory_double
    
    # , 'Plant Overhead'

    plant_overhead_str = get_data_from_cost_single('Plant Overhead', pid, mid, vid, qtr)
    plant_overhead = -1.0
    if u.is_numeric(plant_overhead_str):
        plant_overhead = np.float32(plant_overhead_str)
    
    plant_overhead_full = plant_overhead
    #plant_overhead_half = (operating_labor_half2 + maintenance_labor_half + control_laboratory_half)*Lists[oh]
    # 333
    #list_oh = 0.8
    # the_pct = get_pct_from_lists(6, 'cd_ospct')

    list_oh = u.get_pct_from_lists(lists_df, vid, 'cd_ohpct')
    plant_overhead_half = (operating_labor_half2 
                    + maintenance_labor_half + control_laboratory_half)* list_oh
    plant_overhead_double = (operating_labor_double2 
                    + maintenance_labor_double + control_laboratory_double)* list_oh

    #  , 'Taxes And Insurance
    # (Investment* Cost Details [TI_PCT])/Capacity) * Cost Details[Unit factor] * 100
    # (58.60488723 * 0.02)/260.815 * 10.0 * 100
    # get from lists tab - 0.02
    #cost_details_ti_pct = 0.02
    
    cost_details_ti_pct = u.get_pct_from_lists(lists_df, vid, 'cd_tipct')
    taxes_and_insurance_str = get_data_from_cost_single('Taxes And Insurance', pid, mid, vid, qtr)
    taxes_and_insurance = -1.0
    if u.is_numeric(taxes_and_insurance_str):
        taxes_and_insurance = np.float32(taxes_and_insurance_str)
    
    taxes_and_insurance_full = taxes_and_insurance
    taxes_and_insurance_half = (investment_half * cost_details_ti_pct)/capsity_half * cost_details_unit_factor * 100
    taxes_and_insurance_double = (investment_double * cost_details_ti_pct)/capsity_double * cost_details_unit_factor * 100

    #, 'Plant Cash Costs'
    # SUM(Total Direct Costs + Plant Overhead + Taxes and Insurance)

    plant_cash_costs_full = total_direct_cost_full + plant_overhead_full + taxes_and_insurance_full
    plant_cash_costs_half = total_direct_cost_half + plant_overhead_half + taxes_and_insurance_half
    plant_cash_costs_double = total_direct_cost_double + plant_overhead_double + taxes_and_insurance_double

    #, 'Depreciation'
    # if capacity = 0 then 0 else ((Investment*10)/Capacity) * Cost Details[unit factor]

    depreciation_full = ((investment_full * 10)/capsity_full) * cost_details_unit_factor
    depreciation_half = ((investment_half * 10)/capsity_half) * cost_details_unit_factor
    depreciation_double = ((investment_double * 10)/capsity_double) * cost_details_unit_factor

    #, 'Plant Gate Cost'
    # Deprication + Plant Cash Cost -  from costDetailsByProcess Tab
    plant_gate_cost_str = get_data_from_cost_single('Plant Gate Cost', pid, mid, vid, qtr)
    plant_gate_cost = -1.0
    if u.is_numeric(taxes_and_insurance_str):
        plant_gate_cost = np.float32(plant_gate_cost_str)
      
    plant_gate_cost_full = plant_gate_cost
    plant_gate_cost_half =  plant_cash_costs_half + depreciation_half
    plant_gate_cost_double = plant_cash_costs_double + depreciation_double

    # , 'G + A, Sales, Res.'  G&A, Sales, Research

    #if Cost Details[MID] = -1 then 
    # Cost Summary[GA, Sales, Res.] 
    # else { if capacity = 0 then 0 else 
    # PRODUCT((Cost Details[gsa_pct]/(100 - Cost Details[gsa_pct])), 
    # SUM(((Investment*15)/Capacity)* Cost Details[unit factor]) + Plant Gate Cost)
    # From lists Tab
    # 888 Cost Details[gsa_pct] = 0.030

    # 333
    cost_details_gsa_pct = 0.03

    g_a_sales_res_str = get_data_from_cost_single('G&A, Sales, Research', pid, mid, vid, qtr)
    g_a_sales_res = -1.0
    cost_details_gsa_pct = u.get_consumption_from_yield(yields_df, pid, 'G+A, Sales, Res.')
    
    if u.is_numeric(g_a_sales_res_str):
        g_a_sales_res = np.float32(g_a_sales_res_str)
    
    m1_half = cost_details_gsa_pct/(100 - cost_details_gsa_pct)
    # SUM(((Investment*15)/Capacity)* Cost Details[unit factor]) + Plant Gate Cost)
    m2_half = ((( investment_half * 15) / capsity_half) * cost_details_unit_factor) + plant_gate_cost_half

    m1_double = cost_details_gsa_pct/(100 - cost_details_gsa_pct)
    m2_double = ((( investment_double * 15) / capsity_double) * 10.0) + plant_gate_cost_double

    g_a_sales_res_full = g_a_sales_res
    g_a_sales_res_half = m1_half * m2_half
    g_a_sales_res_double = m1_double * m2_double

    # , 'Production Costs'
    # Cost Summary [ Production Costs] 
    # & ROUND(Varaible Costs + SUM(Maintennace Materials 
    # + Operating Supplies + Operating Labor + Maintenanace Labor 
    # + Control Laboratory + Plant Overhead +Taxes and Insurance
    #  + Depreciation +GA,Sales,Res.)/1,2)


    production_costs_full = round(variable_cost + maintenance_materials_full 
    + operating_supplies_full + operating_labor_full2 + maintenance_labor_full + control_laboratory_full
    + plant_overhead_full + taxes_and_insurance_full + depreciation_full + g_a_sales_res_full,2)
    
    production_costs_half = round(variable_cost + maintenance_materials_half 
    + operating_supplies_half + operating_labor_half2 + maintenance_labor_half 
    + control_laboratory_half
    + plant_overhead_half + taxes_and_insurance_half + depreciation_half + g_a_sales_res_half,2)
    
    production_costs_double = round(variable_cost + maintenance_materials_double 
    + operating_supplies_double + operating_labor_double2 + maintenance_labor_double + control_laboratory_double
    + plant_overhead_double + taxes_and_insurance_double + depreciation_double + g_a_sales_res_double,2)

    # , 'Cash Margin'
    # Cost Summary [Price] - Plant Cash Costs

    price_str = get_data_from_cost_single('Price', pid, mid, vid, qtr)
    price = -1.0
    if u.is_numeric(price_str):
        price = np.float32(price_str)

    cash_margin_full = price - plant_cash_costs_full
    #cash_margin_half = cash_margin_full * 1.03  # ratio for half/full = 1.03
    cash_margin_half = price - plant_cash_costs_half
    cash_margin_double = price - plant_cash_costs_double
    
    #full_capacity = [capsity, 51.50097196, 35.49936449,87.00033645]
    full_capacity = [] 
    full_capacity.append(capsity_full)
    full_capacity.append(battery_limits_full)
    full_capacity.append(offsites_full)
    full_capacity.append(investment_full)
    full_capacity.append(raw_material_full)
    full_capacity.append(by_product_credits_full)
    full_capacity.append(utilities_full)
    full_capacity.append(carbon_full)
    full_capacity.append(variable_cost)
    full_capacity.append(maintenance_materials_full)
    full_capacity.append(operating_supplies_full)
    full_capacity.append(operating_labor_full2)
    full_capacity.append(maintenance_labor_full)
    full_capacity.append(control_laboratory_full)
    full_capacity.append(total_direct_cost_full)
    full_capacity.append(plant_overhead_full)
    full_capacity.append(taxes_and_insurance_full)
    full_capacity.append(plant_cash_costs_full)
    full_capacity.append(depreciation_full)
    full_capacity.append(plant_gate_cost_full)
    full_capacity.append(g_a_sales_res_full)
    full_capacity.append(production_costs_full)
    full_capacity.append(cash_margin_full)

   
    #half_capacity = [capsity*0.5, 51.50097196*.5, 35.49936449*.5,87.00033645*.5]
    half_capacity = []
    half_capacity.append(capsity_half)
    half_capacity.append(battery_limits_half)
    half_capacity.append(offsites_half)
    half_capacity.append(investment_half)
    half_capacity.append(raw_material_half)
    half_capacity.append(by_product_credits_half)
    half_capacity.append(utilities_half)
    half_capacity.append(carbon_half)
    half_capacity.append(variable_cost)
    half_capacity.append(maintenance_materials_half)
    half_capacity.append(operating_supplies_half)
    half_capacity.append(operating_labor_half2)
    half_capacity.append(maintenance_labor_half)
    half_capacity.append(control_laboratory_half)
    half_capacity.append(total_direct_cost_half)
    half_capacity.append(plant_overhead_half)
    half_capacity.append(taxes_and_insurance_half)
    half_capacity.append(plant_cash_costs_half)
    half_capacity.append(depreciation_half)
    half_capacity.append(plant_gate_cost_half)
    half_capacity.append(g_a_sales_res_half)
    half_capacity.append(production_costs_half)
    half_capacity.append(cash_margin_half)
    
    #double_capacity = [capsity*2, 51.50097196*2, 35.49936449*2,87.00033645*2]

    double_capacity = []
    double_capacity.append(capsity_double)
    double_capacity.append(battery_limits_double)
    double_capacity.append(offsites_double)
    double_capacity.append(investment_double)
    double_capacity.append(raw_material_double)
    double_capacity.append(by_product_credits_double)
    double_capacity.append(utilities_double)
    double_capacity.append(carbon_double)
    double_capacity.append(variable_cost)
    double_capacity.append(maintenance_materials_double)
    double_capacity.append(operating_supplies_double)
    double_capacity.append(operating_labor_double2)
    double_capacity.append(maintenance_labor_double)
    double_capacity.append(control_laboratory_double)
    double_capacity.append(total_direct_cost_double)
    double_capacity.append(plant_overhead_double)
    double_capacity.append(taxes_and_insurance_double)
    double_capacity.append(plant_cash_costs_double)
    double_capacity.append(depreciation_double)
    double_capacity.append(plant_gate_cost_double)
    double_capacity.append(g_a_sales_res_double)
    double_capacity.append(production_costs_double)
    double_capacity.append(cash_margin_double)

    products = [u.get_product_name_from_yield(yields_df ,mid) for k in section]
    processIds = [pid for k in section]
    #locations = [vid for k in section]
    locations = [u.get_location_from_vid(lists_df, vid) for k in section]
     
    qtrs = [qtr for k in section]
    basis = ['IHSM' for k in section]
    
    table1 = pd.DataFrame({
                    'PRODUCT': products,
                    'BASIS': basis, 
                    'PROCESSID': processIds,
                    'PERIOD': qtrs, 
                    'LOCATION': locations, 
                    
                    'SECTION': section,
                    'COMPONENTS': components,
                    'HALF IHSM CAPACITY': half_capacity,
                    'IHSM ACTUAL CAPACITY': full_capacity,
                    'IHSM TWICE CAPACITY': double_capacity,
                    })

    return table1



components_in_costdetails = [
                            'Capacity', 'Battery Limits Investment'
                            , 'Offsites Investment'
                            , 'Investment (US$ Million)'
                            , 'Raw Materials'
                            , 'By Product Credits'
                            , 'Utilities'
                            , 'Carbon'
                            , 'Variable Costs'
                            , 'Maintenance Materials'
                            , 'Operating Supplies'
                            , 'Operating Labor'
                            , 'Maintenance Labor'
                            , 'Control Laboratory'
                            , 'Total Direct Costs'
                            , 'Plant Overhead'
                            , 'Taxes And Insurance'
                            , 'Plant Cash Costs'
                            , 'Depreciation'
                            , 'Plant Gate Cost'
                            , 'G + A, Sales, Res.'
                            , 'Production Costs'
                            , 'Cash Margin'
                            ]



pids = u.get_all_processids(yields_df)
pids2 = [237]
# for test only take 6 pids replace pids2 with pids in production
nos = 0
for p in pids:
    nos +=1
    pids2.append(p)
    if nos > 3:
        break

#vids = u.get_all_vids(prices_df)
vids = [1,2, 3]

periods = u.get_all_periods(prices_df)
periods = ['Q3-20']

small_dfs = []
for pid in pids2: # replace pids2 with pids in production
    for vid in vids:
        for period in periods:
            tbl = get_table2(pid, vid, period)
            small_dfs.append(tbl)

large_df = pd.concat(small_dfs, ignore_index=True)
large_df.to_csv("C:\\Users\\HP\\Desktop\\Rapid\\costDetails_table2.csv", index=False)
print('Done')








