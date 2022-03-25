# functions : this_is_a_func()
# vars      : thisIsAVar
# classes   : ThisIsAClass


from abstract_classes import UserAction
from abstract_classes import ParsingReturnValues
from model import Model
from abstract_classes import UserInput
import threading
import argparse
import logging

class Control:
    def __init__(self, mock: bool, import_file: str, view_opt: str):
        #logging.basicConfig(level=logging.INFO)
        self.mock = mock
        EXPORT_FILENAME = "new_mod_data.dat"  
        IMPORT_FILENAME = import_file
        logging.info("Export in Control " + EXPORT_FILENAME)
        logging.info("Import in Control " + IMPORT_FILENAME)
        self.model = Model(EXPORT_FILENAME, IMPORT_FILENAME, mock)

        self.view = self.select_view(view_opt)
        self.gui_thread = threading.Thread(target=self.view.interact)
        self.gui_thread.start()

    def select_view(self, view_opt: str):
        if "view_commandline" == view_opt:
            import view_commandline
            return view_commandline.CommandLineInterface(self.get_user_input, self.model)
        elif "tk_gui" == view_opt:
            import tk_gui
            return tk_gui.GUI(self.get_user_input, self.model)
        else:
            raise ValueError
    

    def check_hex_data(self, data):
        try:
            int(data, 16)
        except:
            raise ValueError()
        if len(data) != 10:
            raise ValueError()
    
    #TODO Check this:
    # {String : {String : [HexStrings]}}
    # {GameName : { Cheat00: [addr1, addr2, ...], Cheat01 : [...], ...} }
    def check_data_from_UI(self, additional_data):
        for game_name in additional_data:
            #Check length of game names
            if len(game_name) > 20:
                raise ValueError()

            #Check game_cheat names
            for cc in additional_data[game_name]:
                if len(cc) > 20:
                    raise ValueError()
                for addresses in additional_data[game_name][cc]:
                    map(lambda addr: self.check_hex_data(addr), addresses)

        return True

    def get_user_input(self, userInput: UserInput):
        user_input = userInput.get_action_and_data()

        userAction = user_input["useraction"]
        additional_data = user_input["data"]

        if userAction == UserAction.NO_ACTION:
            return
        elif userAction == UserAction.MODIFY_DATA:
            self.check_data_from_UI(additional_data)

            logging.info("Ctrl: " + str(additional_data))
            g = self.model.get_game(list(additional_data)[0])

            game_name = list(additional_data)[0]
            games_and_cheatcodes = additional_data[game_name]

            self.model.modify_gamecheat(game, games_and_cheatcodes[game.get_sanitized_game_name()])

        elif userAction == UserAction.EXPORT_ALL_DATA:
            if not self.mock:
                self.model.write_data_to_device()
                self.model.driver.read_data()
            else:
                self.model.write_data_to_file()
        #TODO DELETE_SINGLE_GAME
        elif userAction == UserAction.END_PROGRAM:
            self.model.tear_down()
            exit(0)
        elif userAction == UserAction.ADD_NEW_CHEAT:
            #parse data:
            self.check_data_from_UI(additional_data)

            game_name = list(additional_data)[0]
            games_and_cheatcodes = additional_data[game_name]

            #add new game
            self.model.add_gamecheat(game_name, games_and_cheatcodes[game_name])
            pass
        else:
            logging.info("Control says: Action is not possible")

if __name__ == "__main__":
    #get commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', dest='mock', action='store_true', help="use real device or mock data")
    parser.add_argument('--if', type=str, dest='importfilename', default='imported_data.dat', help='File for saving device data')
    parser.add_argument('--view', type=str, dest='viewopt',default='tk_gui', help="select view options")
    args = parser.parse_args()
    if args.mock:
        control = Control(True, args.importfilename, args.viewopt)
    else:
        control = Control(False, args.importfilename, args.viewopt)