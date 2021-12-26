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

class CtrlMsg(Enum):
    PRINT_ALL = 0
    PRINT_GAME = 1
    ERROR_MSG = 2
    END_GUI = 3
    READY_FOR_INPUT = 4
    READY_FOR_ADDITIONAL_DATA = 4

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

class UserInput():
    def __init__(self, useraction: UserAction, data: list[str]):
        self.useraction_with_data = [UserAction.MODIFY_DATA,
                                    UserAction.DELETE_SINGLE_GAME,
                                    UserAction.MOD_ADDRESS]
        self.useraction = useraction
        self.data = data
    
    def is_user_input_needed(self):
        return self.useraction in self.useraction_with_data
    
    def set_data(self, data: list[str]):
        self.data += data
    
    def get_data(self):
        return self.data
    
    def get_action(self):
        return self.useraction
    
    def get_action_and_data(self):
        return (self.get_action(), self.get_data())


class UserInterface(ABC):
    
    @abstractmethod
    def get_user_action(self) -> UserInput:
        pass
    
    @abstractmethod
    def update_view(self, data, mode):
        pass
