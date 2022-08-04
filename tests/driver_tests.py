import unittest
import sys

sys.path.append('../')
import driverAR

class TestDriver(unittest.TestCase):

    def setUp(self):
        EXPORT_FILENAME = "test_data.dat"
        use_mock_data = False
        self.driver = driverAR.PythonDriver(EXPORT_FILENAME, mock=use_mock_data)

    def tearDown(self):
        self.driver.exit_driver()

    def test01_write_data(self):
        self.driver.write_data_to_device(1) # test data should only have one game

    def test02_read_data(self):
        self.driver.read_data()
    
    def test03_read_then_write(self):
        self.driver.read_data()
        self.driver.write_data_to_device(1)

    def test04_write_then_read(self):
        self.driver.write_data_to_device(1)
        self.driver.read_data()
        

if __name__ == '__main__':
    unittest.main()