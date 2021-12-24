import unittest
import sys
from io import StringIO

sys.path.append('../')
import view_commandline
import control
from abstract_classes import ViewModes, UserAction, UserInput
from model import GameCheatData

class TestGUI(unittest.TestCase):

    def tearDown(self):
        control.stop_threads = True
        self.gui_thread.join()

    def setUp(self):
        #TODO mock data
        MOCK_DATA_FILENAME = "test_data.dat"
        EXPORT_FILENAME = "test_export_file_for_gamecheatdata_class.dat"
        self.mock_gameCheatData = GameCheatData(EXPORT_FILENAME, MOCK_DATA_FILENAME, )
        self.mock_gameCheatData.parse_model_data()
        self.gui_class, self.gui_thread, self.queue_useraction, self.queue_updateview = control.init_gui_and_queues()

    #For simulation std input() see: https://napsterinblue.github.io/notes/python/development/sim_stdin/
    def test01_get_user_action(self):
        for action in self.gui_class.actionDict:
            #TODO adapt for Addtional Data Requests
            if UserInput(action,[]).is_user_input_needed():
                string = action + "\nAdditionalData"
            else:
                string = action
            with StringIO(string) as f:
                stdin = sys.stdin
                sys.stdin = f
                userInput = self.queue_useraction.get()
                action, data = userInput.get_action_and_data()
                sys.stdin = stdin
            
    
    def test02_update_view(self):
        print(self.mock_gameCheatData.gameCheats)
        gameCheatData = self.mock_gameCheatData
        for modes in ViewModes:
            self.queue_updateview.put((gameCheatData, modes))
    
    

if __name__ == '__main__':
    unittest.main()