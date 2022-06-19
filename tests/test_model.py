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
        MOCK_DATA_FILENAME = "all_test_data.dat"
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
        test_byte_data = [1, 0, 0, 0, 65, 32, 76, 97, 110, 100, 32, 66, 101, 102, 111, 114, 101, 32, 84, 105, 109, 101, 32, 32, 4, 0, 0, 0, 40, 109, 41, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 32, 45, 99, 180, 189, 171, 43, 127, 99, 160, 89, 247, 31, 72, 69, 21, 39]
        self.model.add_gamecheat("A Land Before Time",
                                                    {"(m)":
                                                            ["0x2d63b4bd",
                                                            "0xab2b7f63",
                                                            "0xa059f71f",
                                                            "0x48451527"],
                                                            
                                                            })
        self.model.write_data_to_file()

        file_handler = open(self.model.EXPORT_FILENAME, 'rb')
        export_bytes_list = list(file_handler.read())
        file_handler.close()        

        self.assertEqual(test_byte_data, export_bytes_list)
    
    def test_len(self):
        self.model.add_gamecheat("A Land Before Time",
                                                    {"(m)":
                                                            ["0x2d63b4bd",
                                                            "0xab2b7f63",
                                                            "0xa059f71f",
                                                            "0x48451527"],
                                                      "NewCheat":
                                                            ["0x12345678"]
                                                            
                                                            })
        self.assertEqual(self.model.get_num_of_games(), 1) 
        
if __name__ == '__main__':
    unittest.main()