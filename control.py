# functions : this_is_a_func()
# vars      : thisIsAVar
# classes   : ThisIsAClass


from abstract_classes import UserAction
from abstract_classes import ParsingReturnValues
from model import Model
from abstract_classes import CtrlMsg, UserInput
import threading
import queue
import argparse

class Control:
    def __init__(self, mock: bool, import_file: str, view_opt: str):
        EXPORT_FILENAME = "new_mod_data.dat"  
        IMPORT_FILENAME = import_file
        self.model = Model(EXPORT_FILENAME, IMPORT_FILENAME, mock)

        self.ctrl_msg_queue = queue.Queue(maxsize=-1)
        #self.view = view_commandline.CommandLineInterface(self.get_user_input, self.ctrl_msg_queue)
        self.view = self.select_view(view_opt)
        self.gui_thread = threading.Thread(target=self.view.interact)
        self.gui_thread.start()

       
    
    def select_view(self, view_opt: str):
        if "view_commandline" == view_opt:
            import view_commandline
            return view_commandline.CommandLineInterface(self.get_user_input, self.ctrl_msg_queue)
        elif "tk_gui" == view_opt:
            import tk_gui
            return tk_gui.GUI(self.get_user_input, self.ctrl_msg_queue)
        else:
            raise ValueError

    def get_user_input(self, userInput: UserInput):
        userAction, additional_data = userInput.get_action_and_data()

        if userAction == UserAction.NO_ACTION:
            pass
        elif userAction == UserAction.SHOW_ALL_DATA_FROM_AR:
            #request data from model
            gameCheatData = self.model.get_gamecheatdata()
            #send gamecheatdata to view
            self.ctrl_msg_queue.put((gameCheatData, CtrlMsg.PRINT_ALL))
            return
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
    parser.add_argument('--mock', type=str, dest='mock', default="true", help="use real device or mock data")
    parser.add_argument('--if', type=str, dest='importfilename', default='imported_data.dat', help='File for saving device data')
    parser.add_argument('--view', type=str, dest='viewopt',default='view_commandline', help="select view options")
    args = parser.parse_args()
    if args.mock == "false":
        control = Control(False, args.importfilename, args.viewopt)
    else:
        control = Control(True, args.importfilename, args.viewopt)