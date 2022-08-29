import dearpygui.dearpygui as dpg
from util import *
import ctypes


# TOOOODDDDOOOO:

# get native screensize
user32 = ctypes.windll.user32
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)

dpg.create_context()
dpg.create_viewport(title='SIMEKA', width=WIDTH,height=HEIGHT)
dpg.show_font_manager()
dpg.show_style_editor()
dpg.show_debug()
dpg.show_metrics()

# CONSTANTS
# dbug = dpg.show_item_debug
tag_file = 'file_dialog_1' # Tag name for file dialog window to open file
tag_saveFile = 'file_save_1' # Tag name for save as file name
APP_DESCRIPTION= '''
SIMEKA POULTRY APPLICATION
'''
Descrp_width = 500
Descrp_height = 50
SALES_INPUT = 'tag_sales_input'
COST_INPUT = 'tag_costs_input'
SEARCH_INPUT = 'tag_search_input'
Search_hint = 'Kudzai'
Costs_hint = '<Date> <name-of-item/s> <number-of-items> <units> <cost>'
Sales_hint = '2022-08-16 <Name-of-Person> <Number-of-sales> <Nature>'
Input_width = 500
Input_height = 20
DEL_INPUT = 'tag_del_item'
Del_hint = 'Enter the index of the item you wamt to delete: E.G 10'
DIS_WIDTH = 600
DIS_HEIGHT = 300
DIS_DATAFRAME = 'tag_display_data'
Save_button = 'tag_save_button'
Exit_button = 'tag_exit_button'
WIN_TITLE = 'tag_win_title'
debugging = True
DIS_TOTAL = 'tag_display_total'

#Constants that change
CONST = {
    'CURRENT_FILE': None,
    'SAVED_FILENAME': None,
    'SALES_DF': None,
    'COSTS_DF': None,
    'SELECTED_DF': 'Sales',
    'Save_button_status': False,
    'SALES_TOTALS': None,
    'COSTS_TOTAL': None,
}


def df_display():
    '''
    Puts the currently selected Dataframe on display
    '''
    if CONST['SELECTED_DF'] == 'Sales': 
        dpg.set_value(DIS_DATAFRAME, CONST['SALES_DF'])
        num = get_total(CONST['SALES_DF'], 'Number')
        rand = get_total(CONST['SALES_DF'], 'Rand')
        credit = get_total(CONST['SALES_DF'], 'Status')
        total = f'Chickens Sold: {num}\nCash Sales: R{rand}\nCredit: R{credit}'
        dpg.set_value(DIS_TOTAL, total)
    else: 
        dpg.set_value(DIS_DATAFRAME, CONST['COSTS_DF'])
        cost = get_total(CONST['COSTS_DF'], 'Cost')
        total = f'Total Cost: R{cost}'
        dpg.set_value(DIS_TOTAL, total)

def _display_msg(msg):
    dpg.set_value(DIS_DATAFRAME,msg)

def new_file(sender,data):
    '''
    loads a new dataframe to variables SALES_DF, COSTS_DF
    '''
    CONST['SALES_DF'], CONST['COSTS_DF'] = create_dfs()
    #print(SALES_DF)
    df_display()
    CONST['Save_button_status'] = True

def openFile(sender, data):
    # dict comprehension to get the key for the selections dict, which is the file name
    # Stuct: {<file-name>:<full-path>}
    # we want the file name
    res = {k for k in data['selections'].keys()}
    # res is now a "set"
    CONST['CURRENT_FILE'] = res.pop()
    # loading dataframe from given file name
    CONST['SALES_DF'], CONST['COSTS_DF'] = load_dfs(CONST['CURRENT_FILE'])
    # Check which radio button is set and display the required dataframe
    df_display()
    CONST['Save_button_status'] = True

# Function to save file as a given name
def saveAsFile(sender, data):
    # data format:
    # Data: {'file_path_name': 'C:\\Users\\User\\Desktop\\Chickens\\testing.*', 'file_name': 'testing.*', 'current_path': #'C:\\Users\\User\\Desktop\\Chickens', 'current_filter': '.*', 'min_size': [100.0, 100.0], 'max_size': [30000.0, 30000.0], 'selections': {}}
    CONST['SAVED_FILENAME'] = data['file_name']
    # SAVED_FILENAME = res.pop()
    try:
        if CONST['SAVED_FILENAME'] != '':
            save_dfs(CONST['SAVED_FILENAME'], CONST['SALES_DF'], CONST['COSTS_DF'])
            CONST['CUR_FILENAME'] = CONST['SAVED_FILENAME']
            _display_msg('[*] File saved!')
    except PermissionError as e:
        _display_msg(e)

def saveFile(sender, data):
    try:
        if type(CONST['SALES_DF']) == type(None):
            save_dfs(CONST['CURRENT_FILE'], CONST['SALES_DF'], CONST['COSTS_DF'])
            _display_msg("[!] File saved.")
        else: _display_msg('[!] No File Loaded!')
    except PermissionError as e:
        _display_msg(e)

# A function that makes the sale
def enterInput(sender, data):
    '''
    A function that takes input from either the sales input or cost input
    '''
    if type(CONST['SALES_DF']) == type(None):
        _display_msg('[!] Load or create a new file')
    else:
        try:
            if sender == SALES_INPUT:
                if len(data.split(' ')) == 3:
                    # split data into its vars
                    name, num, nature = [it for it in data.split(' ')]
                    # capitalize first letter
                    name = name.capitalize()
                    CONST['SALES_DF'] = append_sales_df(name,num,nature, CONST['SALES_DF'])
                elif len(data.split(' ')) == 4:
                    date, name, num, nature = [it for it in data.split(' ')]
                    # capitalize first letter
                    name = name.capitalize()
                    CONST['SALES_DF'] = append_sales_df(name, num, nature,CONST['SALES_DF'], date=date)

            elif sender == COST_INPUT:
                if len(data.split(' ')) == 4:
                    # split data into its vars
                    item, num, unit, cost = [it for it in data.split(' ')]
                    # capitalize first letter
                    item = item.capitalize()
                    CONST['COSTS_DF'] = append_cost_df(item, num, unit, cost,CONST['COSTS_DF'])
                elif len(data.split(' ')) == 5:
                    # split data into its vars
                    date, item, num, unit, cost = [it for it in data.split(' ')]
                    # capitalize first letter
                    item = item.capitalize()
                    CONST['COSTS_DF'] = append_cost_df(item, num, unit, cost,CONST['COSTS_DF'], date=date)
            df_display()
        except ValueError as e:
            if debugging:
                _display_msg(e)
            else: _display_msg('[!] Make sure the input is the right order!')
        except RuntimeError as r:
            _display_msg(f'[!] {r}')

def delIndex(sender, data):
    '''
    Deletes an items from a particular item
    '''
    try:
        idx = int(data)
        if CONST['SELECTED_DF'] == 'Sales':
            CONST['SALES_DF'] = del_byIndex(idx, CONST['SALES_DF'])
        else: CONST['COSTS_DF'] = del_byIndex(idx, CONST['COSTS_DF'])
        df_display()
    except (KeyError, ValueError) as e:
        if debugging:
            _display_msg(e)
        _display_msg('[!] Enter a value that exists!')

def check_df():
    '''
    Checks if there are dataframes loaded, if so it display them to DIS_DATAFRAME tag
    '''
    if type(CONST['SALES_DF']) == type(None):
        _display_msg('[!] No file loaded!')
    else: df_display()

def select_radio(sender, data):
    '''
    A callback func that toggles the Const that indicates which dataframe to delete from
    '''
    CONST['SELECTED_DF'] = data
    check_df()
    
    #print(f'Selecting Dataframe: {data}')

def searchSales(sender, data):
    '''
    Searches the sales given name
    '''
    if type(CONST['SALES_DF']) == type(None):
        _display_msg('[!] No file loaded!')
    else: _display_msg(name_search_df(data, CONST['SALES_DF']))

def exitApp(sender, data):
    '''
    Saves before exiting app
    '''
    print("Exiting app...")

dpg.create_context()
dpg.create_viewport(title='Testing Main', width=WIDTH,height=HEIGHT)
dpg.show_debug()
dpg.show_metrics()

dpg.setup_dearpygui()
#dpg.set_viewport_vsync(True)
dpg.show_viewport()

# Register font
with dpg.font_registry():
    default_font = dpg.add_font('font/NotoSansMono-Medium.ttf',20)

with dpg.file_dialog(directory_selector=False, show=False, callback=openFile, tag=tag_file, height=500, width=500):
    dpg.bind_font(default_font)
    dpg.add_file_extension(".*")
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension(".py", color=(0, 255, 0, 255), custom_text="[Python]")

with dpg.file_dialog(directory_selector=False, show=False, callback=saveAsFile, tag=tag_saveFile, height=500, width=500):
    dpg.bind_font(default_font)
    dpg.add_file_extension(".xlsx")
    dpg.add_file_extension(".*")
    dpg.add_file_extension("", color=(150, 255, 150, 255))
    dpg.add_file_extension(".py", color=(0, 255, 0, 255), custom_text="[Python]")

with dpg.viewport_menu_bar():
    dpg.bind_font(default_font)
    with dpg.menu(label='File'):
        dpg.add_menu_item(label='New File', callback=new_file)
        dpg.add_menu_item(label='Save', callback=saveFile)
        dpg.add_menu_item(label='Open File', callback=lambda: dpg.show_item(tag_file))
        dpg.add_menu_item(label='Save As ', callback=lambda: dpg.show_item(tag_saveFile))

with dpg.window(label="App", width=WIDTH, height=HEIGHT, tag=WIN_TITLE):
    dpg.bind_font(default_font)
    
    # the top app intro part
    dpg.add_text(label='AppName', default_value=APP_DESCRIPTION)
    # SALES and COST inputs
    dpg.add_input_text(label='Sales Input', tag=SALES_INPUT, width=Input_width, height=Input_height, hint=Sales_hint, on_enter=True, callback=enterInput)
    # Cost input
    dpg.add_input_text(label='Costs Input', tag=COST_INPUT, width=Input_width, height=Input_height, hint=Costs_hint, on_enter=True, callback=enterInput)
    # Delete item from either costs or sales
    dpg.add_input_text(label='Delete Item', tag=DEL_INPUT, width=Input_width, height=Input_height, on_enter=True, hint=Del_hint, callback=delIndex)
    # Search for an name in sales dataframe
    dpg.add_input_text(label='Sales search', width=Input_width, height=Input_height, tag=SEARCH_INPUT, hint=Search_hint, on_enter=True, callback=searchSales)
    dpg.add_radio_button(label='Delete Toggle', items=['Sales', 'Costs'], before=DEL_INPUT, callback=select_radio, horizontal=True)
    with dpg.child_window(border=True, autosize_x=True, height=HEIGHT//2, tracked=True):
    # OUTPUT displays from selected dataframe
        dpg.add_text(label='Dataframes Display', indent=100, default_value='Displays the Dataframe',tag=DIS_DATAFRAME, color=(0, 255, 0, 255))
        dpg.add_text(label='Totals', indent=100, tag=DIS_TOTAL)
    # Save button
    with dpg.group(horizontal=True):
        dpg.add_button(label='Save', tag=Save_button, callback=saveFile)
        # Exit and save button
        dpg.add_button(label='Exit', tag=Exit_button, callback=lambda: dpg.stop_dearpygui())

# Creating a render loop to preserve my variables
#while dpg.is_dearpygui_running():
# creating a file dialog widget for opening a file
#    df_display()
#    dpg.render_dearpygui_frame()

    

    


dpg.start_dearpygui()
dpg.destroy_context()