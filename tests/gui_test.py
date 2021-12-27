import unittest
import sys
from io import StringIO

sys.path.append('../')
import view_commandline
import control
from abstract_classes import CtrlMsg, UserAction, UserInput
from model import GameCheatData
import queue

class TestGUI(unittest.TestCase):

    def setUp(self):
        MOCK_DATA_FILENAME = "test_data.dat"
        EXPORT_FILENAME = "test_export_file_for_gamecheatdata_class.dat"
        self.mock_gameCheatData = GameCheatData(EXPORT_FILENAME, MOCK_DATA_FILENAME, )
        self.mock_gameCheatData.parse_model_data()

        self.ctrl_msg_queue = queue.Queue(maxsize=-1)
        self.view = view_commandline.CommandLineInterface(self.mock_callback, self.ctrl_msg_queue)

        self.callback_ret = []
    
    def mock_callback(self, userinput: UserInput):
        self.callback_ret = userinput

    #For simulation std input() see: https://napsterinblue.github.io/notes/python/development/sim_stdin/
    def test01_get_user_action(self):
        for test_action in self.view.actionDict:
            with StringIO(test_action) as f:
                stdin = sys.stdin
                sys.stdin = f
                self.view.get_user_action()
                sys.stdin = stdin
                actual_action, data = self.callback_ret.get_action_and_data()
            self.assertEqual(actual_action, self.view.actionDict[test_action])
            
    
    def test02_update_view(self):
        gameCheatData = self.mock_gameCheatData
        for modes in CtrlMsg:
            try:
                self.view.handle_ctrl_msg(gameCheatData, modes)
            except ValueError:
                self.assertEqual(1,2)
            

    
    

if __name__ == '__main__':
    unittest.main()