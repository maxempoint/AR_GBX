from abstract_classes import AbstractDriverAR
from model import GameCheatData

import usb.core
import usb.util
import sys
import time
from struct import *

class PythonDriver(AbstractDriverAR):
    def __init__(self, export_filename, mock=False):
        self.mock = mock
        if mock:
            self.DATA_FILE = "mock_data.dat"
            #TODO create driver self.dev stub 
        else:
            self.DATA_FILE = "store_data.dat" #TODO parametrize on init
            self.dev, self.cfg_desired = self.__init_driver()


        self.gameCheats = []

        self.ENDPOINT_ADDRESS_IN = 0x2
        self.ENDPOINT_ADDRESS_OUT = 0x81

        self.WRITE_CODE = b'\x43\x42\x57\x13\x00\x00\x00\x00'
        self.READ_CODE = b'\x43\x42\x57\x1c\x00\x00\x00\x00'
        self.END_WRITE_CODE = b'\x43\x42\x57\x1b\x00\x00\x00\x00'
        self.ZERO = b'\x00\x00\x00\x00\x00\x00\x00\x00'
        self.DONTKNOWYET = b'\x43\x42\x57\x12\x00\x00\x00\x00'

        
        self.SOURCE_FILENAME = export_filename

    def __init_driver(self):
        # find our device
        #Bus 002 Device 010: ID 05fd:daae InterAct, Inc. Game Shark
        dev = usb.core.find(idVendor=0x5fd, idProduct=0xdaae)
        if dev is None:
            raise ValueError('Device not found') 
        else:
            print("GBA Link found")

        #check if there is already a driver attached to the device
        i = dev[0].interfaces()[0].bInterfaceNumber
        if dev.is_kernel_driver_active(i):
            dev.detach_kernel_driver(i)
            print("Driver active!")

        #set appropriate config
        cfg_desired = usb.util.find_descriptor(dev, bConfigurationValue=1)
        dev.set_configuration(cfg_desired)
        try:
            cfg = dev.get_active_configuration()
        except usb.core.USBError:
            cfg = None
        if cfg is None or cfg.bConfigurationValue != cfg_desired:
            dev.set_configuration(cfg_desired)
        return (dev, cfg_desired)

    #From the libusb manual:
    #"get_active_configuration() will act as a lightweight device reset:
    # it will issue a SET_CONFIGURATION request using the current configuration,
    # causing most USB-related device state to be reset (altsetting reset to zero, endpoint halts cleared, toggles reset)."
    def __get_and_set_usb_config(self):
        usb.util.dispose_resources(self.dev)
        i = self.dev[0].interfaces()[0].bInterfaceNumber
        if self.dev.is_kernel_driver_active(i):
            self.dev.detach_kernel_driver(i)
            print("Driver active!")
        cfg_desired = usb.util.find_descriptor(self.dev, bConfigurationValue=1)
        self.dev.set_configuration(cfg_desired)
        try:
            cfg = self.dev.get_active_configuration()
        except usb.core.USBError:
            cfg = None
        if cfg is None or cfg.bConfigurationValue != cfg_desired:
            self.dev.set_configuration(cfg_desired)
        return
        try:
            cfg = self.dev.get_active_configuration()
            print(cfg)
        except usb.core.USBError:
            print("[!] USBError in get and set usb config")
            print(usb.core.USBError)
            cfg = None
        if cfg.bConfigurationValue != 0:
            self.cfg_desired.bConfigurationValue = 0
            print(self.cfg_desired)
            self.dev.set_configuration(self.cfg_desired)

    def __write_data_to_file(self,data):
        f = open(self.DATA_FILE,'wb')
        new = []
        for elem in data:
            for i in elem:
                new.append(i)
        f.write(bytes(new))
        f.close()
    
    def single_read_request(self):
        try:
            ret = self.dev.read(self.ENDPOINT_ADDRESS_OUT,8,1000)
            return ret.tolist()
        except Exception as e:
            print("Exception in single_read_request {0}".format(e))
            return [-1]
    
    def single_write_request(self, msg):
        ret = self.dev.write(self.ENDPOINT_ADDRESS_IN,msg,100)
        return ret

    def write_and_read_request(self, msg):
        retW = self.single_write_request(msg)
        retR = self.single_read_request()
        return (retW, retR)

    def read_data(self):
        dev = self.dev
        ENDPOINT_ADDRESS_IN = self.ENDPOINT_ADDRESS_IN
        RESULT = b''
        #initiate upload
        self.write_and_read_request(self.READ_CODE)
        
        #send zeros for some reason...
        self.write_and_read_request(self.ZERO)

        #TODO Find out the semantics of this code DONTKNOWYET...
        self.write_and_read_request(self.DONTKNOWYET)

        #send zeros for some reason again...
        self.write_and_read_request(self.ZERO)

        loop_condition = True
        data = []

        while loop_condition:
            msg = b'\x00\x00\x00\x00\x00\x00\x00\x00'
            ret = dev.write(ENDPOINT_ADDRESS_IN,msg,100) #here it is 100 wait time, before only 1 -> TODO new param for write_reat_request() ?
            ret = self.single_read_request()

            data.append(ret)

            #not nice: TODO change (maybe look at original driver/client?)
            if ret == [11,11,11,11,20,20,20,20] or ret == [255, 255, 255, 255, 255, 255, 255, 255] or ret == [0,0,0,0,0,0,0,0]:
                loop_condition = False
        
        #message to indicate the end of the import of data from device
        self.write_and_read_request(self.END_WRITE_CODE)
        self.__get_and_set_usb_config()
        #save cheat code data to a file
        self.__write_data_to_file(data)
    
    
    def write_data_to_device(self, num_of_games):
        usb.util.dispose_resources(self.dev)
        file_handler = open(self.SOURCE_FILENAME,'rb')
        data_to_send = file_handler.read()
        file_handler.close()

        NUM_OF_GAMES = pack("<B",num_of_games) #TODO parse number from SOURCE_FILENAME
        print(NUM_OF_GAMES)
        print("EXPORT CODES")
        print("-------------")

        #1
        self.single_write_request(self.WRITE_CODE)
        print(self.single_read_request())

        #2: send num of games
        self.single_write_request(NUM_OF_GAMES + b'\x00\x00\x00\x00\x00\x00\x00')
        result = self.single_read_request()
        print(result)
        if NUM_OF_GAMES[0] == 0:
            return

        #3: write games and codes in loop
        for i in range(int(len(data_to_send)/8)):
            #print(data_to_send[i*8:8*(i+1)])
            self.single_write_request(data_to_send[i*8:8*(i+1)])
            print(self.single_read_request())
        
        self.single_write_request(self.END_WRITE_CODE)

        print(self.single_read_request())
        

    def exit_driver(self):
        if not self.mock:
            print("Unloading Driver")
            usb.util.dispose_resources(self.dev)
