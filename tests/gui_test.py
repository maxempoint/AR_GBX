import unittest
import sys
from io import StringIO

sys.path.append('../')
import view_commandline
import control
from abstract_classes import CtrlMsg, UserAction, UserInput
from model import GameCheatData

class TestGUI(unittest.TestCase):

    def tearDown(self):
        self.queue_updateview.put((self.mock_gameCheatData, CtrlMsg.END_GUI))
        self.gui_thread.join()

    def setUp(self):
        MOCK_DATA_FILENAME = "test_data.dat"
        EXPORT_FILENAME = "test_export_file_for_gamecheatdata_class.dat"
        self.mock_gameCheatData = GameCheatData(EXPORT_FILENAME, MOCK_DATA_FILENAME, )
        self.mock_gameCheatData.parse_model_data()
        self.gui_class, self.gui_thread, self.queue_useraction, self.queue_updateview = control.init_gui_and_queues()

    #For simulation std input() see: https://napsterinblue.github.io/notes/python/development/sim_stdin/
    def test01_get_user_action(self):
        for test_action in self.gui_class.actionDict:
            is_user_input_needed = UserInput(self.gui_class.actionDict[test_action],[]).is_user_input_needed()
            if is_user_input_needed:
               # print("Additional data needed")
                string = test_action + "\nAdditionalData"
            else:
                string = test_action
            with StringIO(string) as f:
                stdin = sys.stdin
                sys.stdin = f
                self.queue_updateview.put((self.mock_gameCheatData, CtrlMsg.READY_FOR_INPUT))
                userInput = self.queue_useraction.get()
                if is_user_input_needed:
                    self.queue_updateview.put((self.mock_gameCheatData, CtrlMsg.READY_FOR_ADDITIONAL_DATA))
                    additional_input = self.queue_useraction.get()
                    userInput.set_data([additional_input.get_data()])
                    print(userInput.get_data())
                sys.stdin = stdin
                actual_action, data = userInput.get_action_and_data()
                self.assertEqual(actual_action, self.gui_class.actionDict[test_action])
                
            
    
    def test02_update_view(self):
        gameCheatData = self.mock_gameCheatData
        for modes in CtrlMsg:
            self.queue_updateview.put((gameCheatData, modes))
    
    

if __name__ == '__main__':
    unittest.main()