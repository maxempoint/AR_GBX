# functions : this_is_a_func()
# vars      : thisIsAVar
# classes   : ThisIsAClass

import view_commandline
import abstract_classes
from abstract_classes import UserAction
from abstract_classes import ParsingReturnValues
from model import GameCheatData
from abstract_classes import CtrlMsg
import driverAR
import queue
import threading


def init_driver(EXPORT_FILENAME, IMPORT_FILENAME): 
    #Init driver
    use_mock_data = True
    if use_mock_data:
        driver = driverAR.PythonDriver(EXPORT_FILENAME, mock=use_mock_data)
    else:
        driver = driverAR.PythonDriver(EXPORT_FILENAME, mock=use_mock_data)
        driver.read_data() #TODO parametrize driver.DATA_FILE
        #TODO find out why driver.read_data() interferes with the write-operation...
        #TODO interprocess communication (e.g. queue) instead of these files
    return driver

def init_model(EXPORT_FILENAME, IMPORT_FILENAME):
    gameCheatData = GameCheatData(EXPORT_FILENAME, IMPORT_FILENAME) #TODO GameCheatData() should get the ref to the DAT file at its init
    #imports all data as [GameCheatData] 
    gameCheatData.parse_model_data()
    return gameCheatData

def init_gui_and_queues():

    #MAXSIZE == -1 means no limit for the queue
    MAXSIZE = -1
    #Producer Consumer for gui and control
    queue_useraction = queue.Queue(maxsize=MAXSIZE)
    queue_updateview = queue.Queue(maxsize=MAXSIZE)
    #Init User-Interface/GUI
    gui_class = view_commandline.CommandLineInterface(queue_useraction,queue_updateview)

    gui = threading.Thread(target=gui_class.interact)
    gui.start()

    return gui_class, gui, queue_useraction, queue_updateview


def main():
    EXPORT_FILENAME = "new_mod_data.dat"  
    IMPORT_FILENAME = "imported_data.dat" 

    driver = init_driver(EXPORT_FILENAME, IMPORT_FILENAME)

    gameCheatData = init_model(EXPORT_FILENAME, IMPORT_FILENAME)

    guit_class, gui_thread, queue_useraction, queue_updateview = init_gui_and_queues()
    
    while(True):
        queue_updateview.put((gameCheatData, CtrlMsg.READY_FOR_INPUT))
        userInput = queue_useraction.get()
        userAction, additional_data = userInput.get_action_and_data()

        if userAction == UserAction.NO_ACTION:
            continue
        elif userAction == UserAction.SHOW_ALL_DATA_FROM_AR:
            driver.read_data()
            gameCheatData.parse_model_data(driver.DATA_FILE)
            
        elif userAction == UserAction.MODIFY_DATA:
            queue_updateview.put((gameCheatData, CtrlMsg.PRINT_ALL))
            #TODO 
            pass
        elif userAction == UserAction.EXPORT_ALL_DATA:
            gameCheatData.write_data_to_file()
            driver.write_data_to_device(gameCheatData.get_num_of_games())

        #TODO DELETE_SINGLE_GAME
        elif userAction == UserAction.END_PROGRAM:
            queue_updateview.put((gameCheatData, CtrlMsg.END_GUI))
            gui_thread.join()
            break
        else:
            print("Action is not possible")


    driver.exit_driver()

    

if __name__ == "__main__":
    main()