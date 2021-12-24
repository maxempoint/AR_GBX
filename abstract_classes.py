from enum import Enum
from abc import ABC, abstractmethod
from struct import pack, iter_unpack

class UserAction(Enum):
    NO_ACTION = -1
    SHOW_ALL_DATA_FROM_AR = 0
    IMPORT_ALL_DATA = 1
    EXPORT_ALL_DATA = 2
    DELETE_SINGLE_GAME = 3
    END_PROGRAM = 4
    MODIFY_DATA = 5
    ADD_NEW_CHEAT = 6
    MOD_ADDRESS = 7

class ViewModes(Enum):
    PRINT_ALL = 0
    PRINT_GAME = 1

#TODO diese values integrieren (-> in GameCheatData.parse_model_data)
class ParsingReturnValues(Enum):
    MODEL_DATA_ERROR = 0
    MODEL_DATA_CORRECT = 1
    FILENAME_ERROR = 2

class AbstractDriverAR(ABC):
    
    @abstractmethod
    def exit_driver(self):
        pass
    
    @abstractmethod
    def read_data(self):
        pass
    
    @abstractmethod
    def write_data_to_device(self):
        pass
    



############--View--############

class UserInterface(ABC):
    
    @abstractmethod
    def get_user_action(self) -> UserAction:
        pass
    
    @abstractmethod
    def update_view(self, data, mode):
        pass
    
    @abstractmethod
    def ask_input(self,text):
        pass
    
    @abstractmethod
    def print_error(self, text):
        pass
    
