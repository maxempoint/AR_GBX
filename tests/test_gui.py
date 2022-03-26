import unittest
import sys
from io import StringIO
import logging

sys.path.append('../')
import tk_gui
import control
from abstract_classes import UserAction, UserInput, ViewTypes
from model import Model

class TestGUI(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.WARNING)
        MOCK_DATA_FILENAME = "test_data.dat"#"test_all_games.dat"#"## #
        EXPORT_FILENAME = "test_export_file_for_gamecheatdata_class.dat"

        self.model = Model(EXPORT_FILENAME, MOCK_DATA_FILENAME, mock=True)
        self.view = tk_gui.GUI(self.mock_callback, self.model, test=True)
        self.view.init_for_interaction()

        self.callback_ret = None
    
    def mock_callback(self, userinput: UserInput):
        self.callback_ret = userinput.get_action_and_data()

    def stringify(self, string):
        return string.rstrip().decode()

    #test if all ctrl messages are handled
    def test01_user_actions_present_data(self):
        #Select game
        gameCheats = self.model.game_cheats

        for cheat in gameCheats:
            game_name = cheat.get_sanitized_game_name()
            cheatcodes = cheat.get_sanitized_cheatCodeNames()
            addresses = cheat.get_sanitized_cheatCodeAddresses()

            self.view.select_game_menu.set(game_name)
            self.view.get_user_action(UserAction.SHOW_ALL_DATA_FROM_AR)

            #Check data if UserInput data in callback_ret is correct
            self.assertEqual(game_name, list( self.callback_ret["data"] )[0])

    def test02_correct_data_is_presented(self):
        gameCheats = self.model.game_cheats

        for cheat in gameCheats:
            game_name = cheat.get_sanitized_game_name()
            cheatcodes = cheat.get_sanitized_cheatCodeNames()
            num_cheatcodes = len (cheatcodes)
            addresses = cheat.get_sanitized_cheatCodeAddresses()

            self.view.select_game_menu.set(game_name)
            gui_data = self.view.get_user_action(UserAction.SHOW_ALL_DATA_FROM_AR)

            #check if number of cheatcodes presented in GUI is the same as in the model:
            self.assertEqual(len(gui_data), num_cheatcodes)

            #check if correct data is presented after fetch_model_data() (via humble object pattern)
            for insert in gui_data:
                #correct cheatcode
                self.assertIn(  insert["cheatcodes"], 
                                cheatcodes )

                for cc in addresses:
                    if cc == insert["cheatcodes"]:
                        self.assertEqual(addresses[cc], insert["addresses"])

    def test03_modify_data(self):
        gameCheats = self.model.game_cheats
        gui_data = []
        test_game_name = "test"

        self.view.clear_gui()
        #
        #Insert mutltiple cheatcodes+addresses with the same game name
        gui_data.append(self.view.insert_into_gui(test_game_name, "my_cheat_code00", ["0x0","0x1","0x2"]))
        gui_data.append(self.view.insert_into_gui(test_game_name, "my_cheat_code01", ["0x3","0x4","0x5"]))
        gui_data.append(self.view.insert_into_gui(test_game_name, "my_cheat_code02", ["0x4","0x7","0x8"]))

        #Trigger the modify data action
        self.view.get_user_action(UserAction.MODIFY_DATA)

        #extract the data that was given to the insert_function
        gui_cheatcodes = []
        gui_addresses = []
        gui_game_name = test_game_name
        for d in gui_data:
            gui_cheatcodes.append(d["cheatcodes"])
            gui_addresses.append(d["addresses"])

        callback_game_name = list( self.callback_ret["data"] )[0]
        callback_cheatcodes = list(self.callback_ret["data"][callback_game_name].keys())
        callback_addresses = list(self.callback_ret["data"][callback_game_name].values())

        self.assertEqual(gui_game_name, callback_game_name)
        self.assertEqual(gui_cheatcodes, callback_cheatcodes)
        self.assertEqual(gui_addresses, callback_addresses)

        #TODO check if those are in fact correct (according to the spec control.py accepts)
        

    #TODO test-case for adding a new game
    def test04_add_new_game(self):
        gameCheats = self.model.game_cheats

        g = self.model.get_games_as_json()
       # print(g)
        pass

if __name__ == '__main__':
    unittest.main()