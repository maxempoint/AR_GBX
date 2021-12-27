# functions : this_is_a_func()
# vars      : thisIsAVar
# classes   : ThisIsAClass

import view_commandline
from abstract_classes import UserAction
from abstract_classes import ParsingReturnValues
from model import GameCheatData
from abstract_classes import CtrlMsg, UserInput
import threading
import queue


class Control:
    def __init__(self):
        self.ctrl_msg_queue = queue.Queue(maxsize=-1)
        self.view = view_commandline.CommandLineInterface(self.get_user_input, self.ctrl_msg_queue)
        self.gui_thread = threading.Thread(target=self.view.interact)
        self.gui_thread.start()

        EXPORT_FILENAME = "new_mod_data.dat"  
        IMPORT_FILENAME = "imported_data.dat" 
        self.model = self.__init_model(EXPORT_FILENAME, IMPORT_FILENAME)
        

    def get_user_input(self, userInput: UserInput):
        userAction, additional_data = userInput.get_action_and_data()

        if userAction == UserAction.NO_ACTION:
            pass
        elif userAction == UserAction.SHOW_ALL_DATA_FROM_AR:
            #TODO request data from model
            pass
        elif userAction == UserAction.MODIFY_DATA:
            #TODO check if additional data is correct
            #TODO set values in model
            pass
        elif userAction == UserAction.EXPORT_ALL_DATA:
            #TODO call model
            #       to call driver
            #           to write data of model to device
            pass
        #TODO DELETE_SINGLE_GAME
        elif userAction == UserAction.END_PROGRAM:
            self.ctrl_msg_queue.put((self.model, CtrlMsg.END_GUI))
            self.model.tear_down()
            exit(0)
        else:
            print("Action is not possible")


    def __init_model(self, EXPORT_FILENAME, IMPORT_FILENAME):
        gameCheatData = GameCheatData(EXPORT_FILENAME, IMPORT_FILENAME) #TODO GameCheatData() should get the ref to the DAT file at its init
        #imports all data as [GameCheatData] 
        gameCheatData.parse_model_data()
        return gameCheatData

if __name__ == "__main__":
    control = Control()