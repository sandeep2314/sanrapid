#util.py

import numpy as np


"""
This util.py module contains common utility helper functions
"""


def get_location_from_vid(listsdf, vid):

    """
    print(get_location_from_vid(lists_df, 6)) - Saudi Arabia
    """

    location=''
    df = listsdf.iloc[:,1]
    
    rw=0
    for col in df.values:
        rw +=1
        if str(col).strip() == str(vid):
            break
    
    location =  listsdf.iloc[rw-1,0]       
    return location




def get_unit_price(pricedf, mid, vid, period):
    """
    get_unit_price(prices_df, 674, 1, 'Q3-20') = 476.833
    """
    prc =  1
    val = pricedf[(pricedf['Period']== period)       
                &  (pricedf['Region']== vid)       
                        
                    ].head()   
    
    prc = list(val[mid])[0]

    return prc



def get_all_processids(yield_df):

    """
    process ids row num is 4-2 and columns starts from 4
    """
    process_ids = yield_df.iloc[4-2,4:]
    return list(process_ids)

def get_all_periods(prices_df):
    
    """
    returns ['Q3-20', 'Q4-20']
    """

    periods = prices_df.iloc[:,1]
    periods =  remove_duplicates(periods)
    return periods

def get_all_vids(prices_df):

    vids =  prices_df.iloc[:,2]
    vids =  remove_duplicates(vids)
    return vids 




def get_column_no_yield(yielddf, pid):
           
    col = 0
    df = yielddf.iloc[4-2, :]
    for c in df.values:
        col +=1
        if str(c).strip() == str(pid):
            break
    return col 


def remove_duplicates(lst):
    """
    removes duplicates from a list
    """
    new_lst = list(set(lst))
    return new_lst

def is_numeric(s):
    """ Returns True if string is a number. """
    try:
        float(s)
        return True
    except ValueError:
        return False





def get_pct_from_lists(listdf, vid, pct_name):

    """
    the_pct = get_pct_from_lists(lsitdf, 6, 'cd_ospct')
    """
    pct = 0

    # get column no.
    # 
    col = 0
    df =  listdf.iloc[0,  :]
    for colmn in listdf.columns:
        col +=1
        if str(colmn).strip() == pct_name:
            break
        
    # country = row = 2 get rwo no.
    # 
    rw = 0

    df_country =  listdf.iloc[1,:]
    for cntry in df_country.values:
        rw +=1
        if cntry == vid:
            break
    pct = listdf.iloc[rw-1, col-1]
    return pct


def get_pct_from_listsOld(lists_df, vid, pct_name):

    """
    helper function to get values from lists worksheet
    print(get_pct_from_lists(1, 'cd_clpct'))
    """
    pct = 0
    val = lists_df[(lists_df['Volume']== vid)
                    ].head()   

    pct = np.float32(val[pct_name][0])
    return pct

def get_sum_section(pid, section, qtr, vid, df):

    """
    helper function reads costs for Raw Materials, Utilities and By-Products to 
    and resturs their respective sum group by section components
    """
   
    sm = 0
    val = df[   (df['PROCESSID']== pid)
                        &  (df['PERIOD']== qtr)       
                        &  (df['LOCATION']== vid)       
                        &  (df['SECTION']== section)       
                    ].head()   
    
    sm = sum(val['COST(US$/TON)'])
    return sm


def get_consumption_from_yield(yields_df, pid, material_name):
    # 888 yield[BLI Scaled Down] 'Battery Limits, Down'

    # get row num of material and get col num of pid
    # use df.iloc[rwno, colNo] 
   
    rw = 1
    df = yields_df.iloc[:, 1:2]
    for r in df.values:
        rw +=1
        val = str(r[0])
        if val.strip() == material_name:
            break
    
    col = 0

    df = yields_df.iloc[4-2, :]
    for c in df.values:
        col +=1
        
        if str(c).strip() == str(pid):
            break
    
    the_data = yields_df.iloc[rw-2, col-1]
    return the_data 


def get_row_num_of_components(yields_df, colNum, colValue):

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



def get_material_used_from_yield(yields_df, prices_df, pid, material_type, vid, qtr):


    # Utilities starts from row 38 and till 47
    utilities_rownum_starts =   get_row_num_of_components(yields_df, 1, 'Utilities (per unit of capacity)')
    # Raw Material Starts From row 47 till 468
    raw_material_rownum_starts = get_row_num_of_components(yields_df, 1, 'Feedstocks (per unit of capacity)')   
    # By Products starts from row 469
    by_products_rownum_starts = get_row_num_of_components(yields_df, 1, 'Products (per unit of capacity)')   


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
            unit_price = get_unit_price(prices_df, compid, vid, qtr)
            
            consumption = v[0]
            rm = v[0] * unit_price
            rm_list.append(rm)

            # By Products
            #rw > by_products_rownum_starts and np.float32(val) != 1 
        if (is_numeric(val) and np.float32(val) != 1 and (np.float32(val) > 0 or np.float32(val) < 0) ) and material_type == 'by product' and rw > by_products_rownum_starts:
                
            by_product_name = yields_df.iloc[rw-1,1]
            compid = yields_df.iloc[rw-1,0]
            unit_price = get_unit_price(prices_df, compid, vid, qtr)
            consumption = v[0]
            rm = consumption * unit_price
            rm_list.append(rm)
    
        # By Utilities
        # rw > utilities_rownum_starts and rw < raw_material_rownum_starts:                
        if (is_numeric(val) and np.float32(val) != 1 and (np.float32(val) > 0 or np.float32(val) < 0) ) and material_type == 'utilities' and rw > utilities_rownum_starts and rw < raw_material_rownum_starts:
                
            by_product_name = yields_df.iloc[rw-1,1]
            compid = yields_df.iloc[rw-1,0]
            unit_price = get_unit_price(prices_df, compid, vid, qtr)
            consumption = v[0]
            rm = consumption * unit_price
            rm_list.append(rm)
    
    return sum(rm_list)




def get_product_name_from_yield(yields_df, mid):

    """
    helper function to get product name from Yield sheet,
    given its materialId - mid -  674

    """
    product_name = ''
    rw = 1
    df = yields_df.iloc[:, 0:1]
    for r in df.values:
        rw +=1
        val = r[0]
        if val == mid:
            break

    product_name = yields_df.iloc[rw-2, 1]
    return product_name



def get_mid_from_yield_pid(yields_df, pid):


    # Utilities starts from row 38 and till 47
    utilities_rownum_starts =   get_row_num_of_components(yields_df, 1, 'Utilities (per unit of capacity)')
    # Raw Material Starts From row 47 till 468
    raw_material_rownum_starts = get_row_num_of_components(yields_df, 1, 'Feedstocks (per unit of capacity)')   
    # By Products starts from row 469
    by_products_rownum_starts = get_row_num_of_components(yields_df, 1, 'Products (per unit of capacity)')   

    colNum = get_column_no_yield(yields_df, pid)
    #print('colNum ', colNum)

    col = yields_df.iloc[:, colNum-1:colNum]
    rw = 0
    for v in col.values:

        rw+=1
        val = str(v[0])

        # the_product_name
        if is_numeric(val) and np.float32(val) == 1.0 :
            the_product_name = yields_df.iloc[rw-1,1]
            themid = yields_df.iloc[rw-1,0] 
    return themid

def get_product_name_from_pid(yielddf, pid):

    product_name = ''
    mid = get_mid_from_yield_pid(yielddf, pid)
    product_name = get_product_name_from_yield(yielddf, mid)

    return product_name


