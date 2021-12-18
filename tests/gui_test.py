import unittest
import sys
from io import StringIO

sys.path.append('../')
import view_commandline
from abstract_userinterface import GameCheatData, ViewModes, UserAction

class TestGUI(unittest.TestCase):

    #Note: tearDown() is not necessary here
    def setUp(self):
        #TODO mock data
        MOCK_DATA_FILENAME = "test_data.dat"
        EXPORT_FILENAME = "test_export_file_for_gamecheatdata_class.dat"
        self.mock_gameCheatData = GameCheatData(EXPORT_FILENAME, MOCK_DATA_FILENAME, )
        self.mock_gameCheatData.parse_model_data()
        self.gui = view_commandline.CommandLineInterface()

    #For simulation std input() see: https://napsterinblue.github.io/notes/python/development/sim_stdin/
    def test01_get_user_action(self):
        for action in self.gui.actionDict:
            with StringIO(action) as f:
                stdin = sys.stdin
                sys.stdin = f
                self.gui.get_user_action()
                sys.stdin = stdin
            
    
    def test02_update_view(self):
        print(self.mock_gameCheatData.gameCheats)
        for modes in ViewModes:
            self.gui.update_view(self.mock_gameCheatData, modes)
            
    
    def test03_ask_input(self):
        with StringIO("test string") as f:
                stdin = sys.stdin
                sys.stdin = f
                self.gui.ask_input("TEST TEST")
                sys.stdin = stdin
        

    def test04_print_error(self):
        self.gui.print_error("TEST ERROR")
        

if __name__ == '__main__':
    unittest.main()