# functions : this_is_a_func()
# vars      : thisIsAVar
# classes   : ThisIsAClass

import view_commandline
import abstract_userinterface
from abstract_userinterface import UserAction
from abstract_userinterface import ParsingReturnValues
from abstract_userinterface import GameCheatData
from abstract_userinterface import ViewModes
import driverAR


def validate_addr():
    #TODO
    return True


def handle_mod_data(game, gui, driver):
    while(True):
        userAction = gui.get_user_action()
        if userAction == UserAction.NO_ACTION:
            continue
        elif userAction == UserAction.ADD_NEW_CHEAT:
            new_cheat_name = gui.ask_input("Enter new cheat name")
            #add many cheat codes
            while(True):
                new_addr = gui.ask_input("Enter new Address")
                if new_addr == "q":
                    break
                if validate_addr(new_addr):
                    game.set_cheatCodeAddresses(new_cheat_name,new_addr)
                else:
                    gui.print_error("Incorrect cheat address")
        elif userAction == UserAction.MOD_ADDRESS:
            pass #TODO
        elif userAction == UserAction.END_PROGRAM:
            break
        else:
            gui.print_error("Action is not possible")

EXPORT_FILENAME = "new_mod_data.dat"
#Init driver
use_mock_data = False
if use_mock_data:
    driver = driverAR.PythonDriver(EXPORT_FILENAME, mock=use_mock_data)
else:
    driver = driverAR.PythonDriver(EXPORT_FILENAME, mock=use_mock_data)
    driver.read_data() #TODO parametrize driver.DATA_FILE
    #TODO find out why driver.read_data() interferes with the write-operation...
    #TODO interprocess communication (e.g. queue) instead of these files


gameCheatData = GameCheatData(EXPORT_FILENAME) #TODO GameCheatData() should get the ref to the DAT file at its init
#imports all data as [GameCheatData] 
gameCheatData.parse_model_data(driver.DATA_FILE) #   driver.DATA_FILE "org_gba_import.dat" "gba_import.dat"


#Init User-Interface/GUI -- TODO Vereinfachen mit nur einer abstrakten Klasse
gui = abstract_userinterface.ConcreteUserInterface(view_commandline.CommandLineInterface())

while(True):
    userAction = gui.get_user_action()
    if userAction == UserAction.NO_ACTION:
        continue
    elif userAction == UserAction.SHOW_ALL_DATA_FROM_AR:
        driver.read_data()
        gameCheatData.parse_model_data(driver.DATA_FILE)
        gui.update_view(gameCheatData, ViewModes.PRINT_ALL)
    elif userAction == UserAction.MODIFY_DATA:
        gui.update_view(gameCheatData, ViewModes.PRINT_ALL)
        gameName = gui.ask_input("Enter existing Game Name")
        if gameCheatData.does_GameExist(gameName):
            game = gameCheatData.get_Game(gameName)
            handle_mod_data(game, gui, driver)
        elif gameName != "q":
            gui.print_error("Game does not exist")
        else:
            continue
    elif userAction == UserAction.EXPORT_ALL_DATA:
        gameCheatData.write_data_to_file()
        driver.write_data_to_device(gameCheatData.get_num_of_games())

    #TODO DELETE_SINGLE_GAME
    elif userAction == UserAction.END_PROGRAM:
        break
    else:
        gui.print_error("Action is not possible")


driver.exit_driver()