#import xlwt
import openpyxl
import pandas
import re
import sys
import datetime
import random as rn
#TODO
# Change the way debt is accumulated so its a what they paid credited currently, no carrying over
# and add a sum function that sums all the cash sales or all total sales minus the credits

PRICE = 90
# TODO


def create_dfs():
    '''
    Creates 2 DataFrames and return them
    '''
    sales_heading = [
        "Date",
        "Name",
        "Number",
        "Nature",
        "Rand",
        "Status"
    ]
    costs_headings = [
        "Date",
        "Items",
        "Number",
        "Unit",
        "Cost"
    ]
    sales_df, costs_df = pandas.DataFrame(columns=sales_heading), pandas.DataFrame(columns=costs_headings)
    return sales_df, costs_df


def assign_status(nature:str, number:int):
    assert nature == "credit" or nature == "cash"
    if nature == "credit": return -(number * PRICE)
    else: return 0

def del_byIndex(idx:str, df:callable):
    '''
    Deletes a row by index
    '''
    df = df.drop([int(idx)])
    return df
    


def pay_debt(name:str, amount:int, sdf:callable):
    # Get the index of where the name occurs
    idx = sdf.index[sdf["Name"] == name]
    #Then we update the latest Status value at the given index
    if idx.empty:
        raise RuntimeError(f"{name} does not exist!")
    sdf.at[idx[-1], "Status"] += amount
    # we us


def gen_fill(df:callable, sheet:str, num=None):
    '''
    Auto generate random data to fill sales dataframe
    '''
    if sheet == "s":
        names = ['Kudzi', 'Tate', 'Chandi', 'Amai', 'Veronica', 'Silas', 'Jongwe', 'Hama', 'Pastor']
        number = ['1', '1', '1', '1','1','2','2','2','2','2',]
        nature = ['cash', 'credit']
        for _ in range(num):
            df = append_sales_df(rn.choice(names), rn.choice(number), rn.choice(nature), df)
        return df
    else:
        df = append_cost_df("feed", "6", "50kg/bag", "3405", df)
        df = append_cost_df("labour", "1", "n/a", "500", df)
        df = append_cost_df("sawdust", "6", "50kg/bag", "200", df)
        df = append_cost_df("transport", "1", "n/a", "500", df)
        df = append_cost_df("mortalities", "10", "chicks", "900", df)
        return df

def debt_check(name:str, nature:str, number:int, sdf:callable):
    '''
    Check for the latest debt of name given and carry their debt over to their current purchase. Returns a number, negative number mean in-debt and 0 is no debt
    '''
    # here i did a .loc search for the name given which returns a dataframe
    # I chained another loc search to get status columns that are in the negatives
    # NOTE: Result could be empty if name doesnt have a debt
    # TRY see what that would be like to have an empty response
    # the sdf could be empty and therefore we do not need to check debt
    def _credit_filter():
        if number > 2 and nature == 'credit':
            raise RuntimeError("No credit for more than 2 chickens")
        else:
            pass
    if sdf.empty:
        _credit_filter()
        return assign_status(nature, number)
    result_df = sdf.loc[sdf["Name"] == name].loc[sdf["Status"] < 0]
    if not (result_df.empty):
        # grabs the latest debt and returns it
        latest_debt = result_df.iloc[-1]["Status"]
        # if nature is credit we add (but since it - we subtract to add) their latest debt to the amount they now owe, i.e number*Price
        if latest_debt <= -180:
            raise RuntimeError(f"Person, {name} Has Exceeded The Debit Quoter, DO NOT SELL TO THEM!")
        if nature == "credit":
            # You can only purchase 1 chicken on credit
            _credit_filter()
            return (latest_debt - number*PRICE)
        return latest_debt
    else:
        _credit_filter() 
        return assign_status(nature, number)
    

def date_check(date):
    regx_pattern = r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"
    #converting datetime object to string
    date = str(date)
    #making sure that the date is in the right format YYY-MM-DD with regx
    final_date = re.search(regx_pattern, date)
    if final_date == None:
        raise ValueError("The date is in the wrong format, make sure it is YYYY-MM-DD")
    return date

def append_sales_df(name:str, number:str, nature:str,sales_df:callable, date=datetime.date.today()):
    number = int(number)
    try:
        status = debt_check(name, nature, number, sales_df)
        if nature == 'credit':
            status = number*PRICE
            rand = 0
        else: rand, status = number*PRICE, 0
    except RuntimeError as e:
        raise RuntimeError(e)
        #return sales_df
    date = date_check(date)
    data = [date, name, number, nature, rand, status]
    sales_df.loc[len(sales_df)] = data # append the data via an index that is dependant on the length of the dataframe. So 0 len we place it at 0 index
    return sales_df

def append_cost_df(item:str, num:str, unit:str, cost:str, cost_df:callable,date=datetime.date.today()):
    try:
    # convert to int
        num, cost = int(num), int(cost)
        date = date_check(date)
        data = [date, item, num, unit, cost]
        #append to index
        cost_df.loc[len(cost_df)] = data
        return cost_df
    except:
        raise RuntimeError('[!] Check the input or format of data given. Or no data loaded!')

    


#an alternative func that loads the excel sheet straight into a dataframe
def load_dfs(fname:str):
    if (".xlsx" not in fname):
        fname += ".xlsx"
    return pandas.read_excel(fname, sheet_name="Sales"), pandas.read_excel(fname, sheet_name="Costs")
#Save dataframes to excel
def save_dfs(fname:str, sales_df:callable, costs_df:callable):
    try:
        if ".xlsx" not in fname:
            fname += ".xlsx"
        with pandas.ExcelWriter(fname) as writer:
            sales_df.to_excel(writer, "Sales", index=False)
            costs_df.to_excel(writer, "Costs", index=False)
    except PermissionError:
        return PermissionError("[!] Permission Error: Make Sure that the file is close in another window!!")
        
#A search func, that goes over the names in the spreadsheet an
def name_search_df(name:str, df:callable):
    '''
    We search the given dataframe for the name and return a dataframe
    '''
    return df.loc[df["Name"] == name]


def get_total(df:callable, column:str):
    '''
    Gets the total of the dataframe from a specific column
    '''
    res = df.get(column).sum()
    return res



                
