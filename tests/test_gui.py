import unittest
import sys
from io import StringIO
import logging
import json

sys.path.append('../')
import tk_gui
import control
from abstract_classes import UserAction, UserInput, ViewTypes
from model import Model

class TestGUI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.WARNING)
        MOCK_DATA_FILENAME = "test_data.dat"#"test_all_games.dat"#
        EXPORT_FILENAME = "test_export_file_for_gamecheatdata_class.dat"

        self.model = Model(EXPORT_FILENAME, MOCK_DATA_FILENAME, mock=True)
        self.view = tk_gui.GUI(self.mock_callback, self.model, test=True)
        self.view.init_for_interaction()

        self.callback_ret = None
    
    def mock_callback(self, userinput: UserInput):
        self.callback_ret = userinput.get_action_and_data()

    #test if all ctrl messages are handled
    def test01_user_actions_present_data(self):
        #Select game
        gameCheats = self.model.game_cheats

        for cheat in gameCheats:
            game_name = cheat.get_sanitized_game_name()
            cheatcodes = cheat.get_sanitized_cheatCodeNames()
            addresses = cheat.get_sanitized_cheatCodeAddresses()

            self.view.select_game_menu.set(game_name)
            self.view.prepare_and_exec_callback(UserAction.SHOW_ALL_DATA_FROM_AR)
            #Check data if UserInput data in callback_ret is correct
            self.assertEqual(game_name, self.callback_ret)

    
    def test02_correct_data_is_presented(self):
        gameCheats = self.model.game_cheats

        for cheat in gameCheats:
            game_name = cheat.get_sanitized_game_name()
            cheatcodes = cheat.get_sanitized_cheatCodeNames()
            num_cheatcodes = len (cheatcodes)
            addresses = cheat.get_sanitized_cheatCodeAddresses()

            self.view.select_game_menu.set(game_name)
            gui_data = self.view.prepare_and_exec_callback(UserAction.SHOW_ALL_DATA_FROM_AR)

            #check if number of cheatcodes presented in GUI is the same as in the model
            #the number of cheatcodes equals the number of entries in the cheatcode option menu
            self.assertEqual(len(gui_data), len( self.view.cheatcode_opt_menu.winfo_children() ))

            #check if correct data is presented after fetch_model_data() (via humble object pattern)
            for insert in gui_data:
                #correct cheatcode
                self.assertIn(  insert["cheatcodes"], 
                                cheatcodes )

                for cc in addresses:
                    if cc == insert["cheatcodes"]:
                        self.assertEqual(addresses[cc], insert["addresses"])

    #TODO setup cheat data which can be modified
    def test03_modify_data(self):
        gameCheats = self.model.game_cheats
        gui_data = []
        test_game_name = list(json.loads( self.model.get_games_as_json() ).items())[0][0]

        self.view.clear_gui()

        #>GUI gets data
        #print(list(json.loads( self.model.get_games_as_json() ).items())[0][0])
        #Insert mutltiple cheatcodes+addresses with the same game name
        gui_data.append(self.view.insert_into_gui(test_game_name, "my_cheat_code00", ["0x0","0x1","0x2"]))

        #Trigger the modify data action
        self.view.prepare_and_exec_callback(UserAction.MODIFY_DATA)

        #extract the data that was given to the insert_function
        gui_cheatcodes = []
        gui_addresses = []
        gui_game_name = test_game_name
        for d in gui_data:
            gui_cheatcodes.append(d["cheatcodes"])
            gui_addresses.append(d["addresses"])

        #<GUI returns data in the form {String : {String : [HexStrings]}}
        print(self.callback_ret["data"])
        callback_game_name = list( self.callback_ret["data"] )[0]
        callback_cheatcodes = list(self.callback_ret["data"][callback_game_name].keys())
        callback_addresses = list(self.callback_ret["data"][callback_game_name].values())

        #Check type
        self.assertEqual(type( {"test" : {"c0" : ["1","2"]}} ),
                        type( self.callback_ret["data"][callback_game_name] ))

        self.assertEqual(gui_game_name, callback_game_name)
        self.assertEqual(gui_cheatcodes, callback_cheatcodes)
        self.assertEqual(gui_addresses, callback_addresses)


if __name__ == '__main__':
    unittest.main()