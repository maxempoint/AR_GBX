import unittest
import sys
from io import StringIO

sys.path.append('../')
import view_commandline
import control
from abstract_classes import CtrlMsg, UserAction, UserInput, ViewTypes
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

    def simulate_user(self, test_action) -> (UserAction, str):
        view_type = self.view.type

        if view_type == ViewTypes.COMMAND_LINE:
            #For simulation std input() see: https://napsterinblue.github.io/notes/python/development/sim_stdin/
            with StringIO(test_action) as f:
                stdin = sys.stdin
                sys.stdin = f
                self.view.get_user_action()
                sys.stdin = stdin
                actual_action, data = self.callback_ret.get_action_and_data()
        elif view_type == ViewTypes.TKINTER_GUI:
            #TODO
            pass

    
    #Test if the mapping between userinput and action in self.view.actionDict is correct
    def test01_get_user_action(self):
        for test_action in self.view.actionDict:
            self.simulate_user(test_action)
            actual_action, data = self.callback_ret.get_action_and_data()
            self.assertEqual(actual_action, self.view.actionDict[test_action])
            
    
    #test if all ctrl messages are handled
    def test02_update_view(self):
        gameCheatData = self.mock_gameCheatData
        for modes in CtrlMsg:
            if modes == CtrlMsg.END_GUI:
                continue
            try:
                self.view.handle_ctrl_msg(gameCheatData, modes)
            except ValueError:
                self.assertTrue(False)
            

    
    

if __name__ == '__main__':
    unittest.main()