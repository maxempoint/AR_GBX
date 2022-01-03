# functions : this_is_a_func()
# vars      : thisIsAVar
# classes   : ThisIsAClass

import view_commandline
from abstract_classes import UserAction
from abstract_classes import ParsingReturnValues
from model import Model
from abstract_classes import CtrlMsg, UserInput
import threading
import queue
import argparse

class Control:
    def __init__(self, mock: bool, import_file: str):
        self.ctrl_msg_queue = queue.Queue(maxsize=-1)
        self.view = view_commandline.CommandLineInterface(self.get_user_input, self.ctrl_msg_queue)
        self.gui_thread = threading.Thread(target=self.view.interact)
        self.gui_thread.start()

        EXPORT_FILENAME = "new_mod_data.dat"  
        IMPORT_FILENAME = import_file
        self.model = Model(EXPORT_FILENAME, IMPORT_FILENAME, mock)
        

    def get_user_input(self, userInput: UserInput):
        userAction, additional_data = userInput.get_action_and_data()

        if userAction == UserAction.NO_ACTION:
            pass
        elif userAction == UserAction.SHOW_ALL_DATA_FROM_AR:
            #request data from model
            gameCheatData = self.model.get_gamecheatdata()
            #send gamecheatdata to view
            self.ctrl_msg_queue.put((gameCheatData, CtrlMsg.PRINT_ALL))
        elif userAction == UserAction.MODIFY_DATA:
            #TODO check if additional data is correct
            print("control " + str(additional_data))
            #TODO set values in model
            pass
        elif userAction == UserAction.EXPORT_ALL_DATA:
            self.model.write_data_to_device()
        #TODO DELETE_SINGLE_GAME
        elif userAction == UserAction.END_PROGRAM:
            self.ctrl_msg_queue.put((self.model, CtrlMsg.END_GUI))
            self.model.tear_down()
            exit(0)
        else:
            print("Action is not possible")

if __name__ == "__main__":
    #get commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', type=bool, dest='mock', default=True, help="use real device or mock data")
    parser.add_argument('--if', type=str, dest='importfilename', default='imported_data.dat', help='File for saving device data')

    args = parser.parse_args()
    control = Control(args.mock, args.importfilename)