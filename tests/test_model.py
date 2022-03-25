import unittest
import sys
import os
import logging

sys.path.append('../')
import control
from abstract_classes import UserAction, UserInput, ViewTypes
from model import Model

class TestModel(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.WARNING)
        MOCK_DATA_FILENAME = "model_test_data.dat"
        EXPORT_FILENAME = "model_test_export.dat"

        self.model = Model(EXPORT_FILENAME, MOCK_DATA_FILENAME, mock=True)

        self.callback_ret = None
    
    def tearDown(self):
        os.system(f"rm {self.model.EXPORT_FILENAME}")

    def parse_for_model(self, data):
        b_data = data.ljust(20).encode()
        return b_data

    #test if all ctrl messages are handled
    def test01_model_data_is_written_to_file(self):
        self.model.add_gamecheat("A Land Before Time",
                                                    {"(m)":
                                                            ["0x2d63b4bd",
                                                            "0xab2b7f63",
                                                            "0xa059f71f",
                                                            "0x48451527"],
                                                            
                                                            })
        self.model.write_data_to_file()

        file_handler = open(self.model.EXPORT_FILENAME, 'rb')
        file_handler.close()        

        os.system(f"xxd {self.model.EXPORT_FILENAME}")
        
if __name__ == '__main__':
    unittest.main()