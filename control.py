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
import os

class Control:
    def __init__(self, mock: bool, import_file: str, export_file: str, view_opt: str):
        logging.basicConfig(level=logging.INFO)
        self.mock = mock
        EXPORT_FILENAME = export_file
        IMPORT_FILENAME = import_file
        self.check_file_exists(export_file)
        self.check_file_exists(import_file)
        logging.info("Export in Control " + EXPORT_FILENAME)
        logging.info("Import in Control " + IMPORT_FILENAME)
        self.model = Model(EXPORT_FILENAME, IMPORT_FILENAME, mock)

        self.view = self.select_view(view_opt)
        self.gui_thread = threading.Thread(target=self.view.interact)
        self.gui_thread.start()
    
    def check_file_exists(self, filename: str):
        if not os.path.exists(filename):
            raise ValueError(f"File '{filename}' does not exist or path is incorrect")

    def select_view(self, view_opt: str):
        if "tk_gui" == view_opt:
            import tk_gui
            return tk_gui.GUI(self.get_user_input, self.model)
        else:
            raise ValueError(f"View Option {view_opt} not recognised!")
    

    @staticmethod
    def check_hex_data(data: str):
        try:
            int(data, 16)
        except Exception as e:
            raise ValueError(f"Hex Data {data} is not valid hex: {e}")
        if len(data) != 10:
            raise ValueError(f"Hex Data {data} length {len(data)} is not correct")
    
    # This format is checked:
    # {String : {String : [HexStrings]}}
    # {GameName : { Cheat00: [addr1, addr2, ...], Cheat01 : [...], ...} }
    @staticmethod
    def check_data_from_UI(additional_data: dict):
        # check types
        if type(additional_data) is not dict:
            raise ValueError(f"Wrong data type of additional_data: {type(additional_data)} (should be dict)")
        for game_name in additional_data:
            # Check length of game names
            if len(game_name) > 20:
                raise ValueError(f"Game name {game_name} too long! (is: {len(game_name)}, max: 20)")
            # Check type
            if type(additional_data[game_name]) is not dict:
                raise ValueError(f"Wrong data type of additional_data[game_name]: {type(additional_data[game_name])}")
            # Check game_cheat names
            for cc in additional_data[game_name]:
                if len(cc) > 20:
                    raise ValueError(f"Cheat name {cc} too long! (is: {len(cc)}, max: 20)")
                for address in additional_data[game_name][cc]:
                    # check type
                    if type(address) is not str:
                        raise ValueError(f"Wrong data type of address {address}: {type(address)} (should be str)")
                    # Check if address have the correct hex data format
                    Control.check_hex_data(address)


        return True

    def get_user_input(self, userInput: UserInput):
        user_input = userInput.get_action_and_data()

        userAction = user_input["useraction"]
        additional_data = user_input["data"]


        # TODO: switch to match clause if Python >= 3.10 is used
        if userAction == UserAction.NO_ACTION:
            return
        elif userAction == UserAction.MODIFY_DATA:
            self.check_data_from_UI(additional_data)

            logging.info("Ctrl: " + str(additional_data))
            game = self.model.get_game(list(additional_data)[0])

            game_name = list(additional_data)[0]
            games_and_cheatcodes = additional_data[game_name]
            self.model.modify_gamecheat(game, game_name, games_and_cheatcodes)

        elif userAction == UserAction.EXPORT_ALL_DATA:
            if not self.mock:
                self.model.write_data_to_device()
                self.model.driver.read_data()
            else:
                self.model.write_data_to_file()
        # TODO DELETE_SINGLE_GAME
        elif userAction == UserAction.END_PROGRAM:
            self.model.tear_down()
            exit(0)
        elif userAction == UserAction.ADD_NEW_GAME:
            # parse data:
            self.check_data_from_UI(additional_data)

            game_name = list(additional_data)[0]
            games_and_cheatcodes = additional_data[game_name]

            # add new game
            self.model.add_gamecheat(game_name, games_and_cheatcodes)
            pass
        else:
            logging.info("Control says: Action is not possible")

if __name__ == "__main__":
    # get commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--mock', dest='mock', action='store_true', help="use real device or mock data")
    parser.add_argument('--if', type=str, dest='importfilename', default='imported_data.dat', help='File Model reads from (if not defautlt: Driver writes to)')
    parser.add_argument('--ef', type=str, dest='exportfilename', default='new_mod_data.dat', help='File Model writes to and Driver reads from')
    parser.add_argument('--view', type=str, dest='viewopt',default='tk_gui', help="select view options")
    args = parser.parse_args()
    control = Control(args.mock, args.importfilename, args.exportfilename, args.viewopt)