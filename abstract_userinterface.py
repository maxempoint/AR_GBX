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


class GameCheat:
    #TODO ID for easier reference
    def __init__(self):
        #str
        self.gameName = ''
        #list of str
        self.cheatCodesName = []
        #dict with {cheatCodesName[i]: [list of str]}
        self.cheatCodeAddresses = {}
    
    def set_gameName(self, name):
        self.gameName = name
    
    def set_cheatCodeName(self, cheatName):
        if cheatName is not self.cheatCodesName:
            self.cheatCodesName.append(cheatName)
        else:
            print("Cheat Code Name already exists!")
    
    def set_cheatCodeAddresses(self,cheatName, addresses):
        if cheatName in self.cheatCodesName:
            self.cheatCodeAddresses[cheatName] = addresses
        else:
            print("Cheat Code Name is not set!")
    
    def get_gameName(self):
        return self.gameName
    
    def get_cheatCodeNames(self):
        return self.cheatCodesName
    
    def get_cheatCodeAddresses(self):
        return self.cheatCodeAddresses

class GameCheatData:
    def __init__(self, export_filename):
        self.gameCheats = []
        self.SOURCE_FILENAME = "imported_data.dat"
        self.EXPORT_FILENAME = "new_mod_data.dat"

        self.games_and_cheatcodes = {}
    
    def get_num_of_games(self):
        return len(self.gameCheats)

    #write data in bytes format to file
    def write_data_to_file(self):
        file_handler = open(self.EXPORT_FILENAME, "wb")
        for cheatcode in self.gameCheats:
            file_handler.write( pack("<i", len(cheatcode.get_cheatCodeNames()) ) )
            file_handler.write( bytes(cheatcode.get_gameName().decode(),'utf-8') )
            for c in cheatcode.get_cheatCodeAddresses():
                #print(c)
                arr_of_addr = cheatcode.get_cheatCodeAddresses()[c]
                file_handler.write( pack("<i", len(arr_of_addr)) )
                file_handler.write( bytes(c.decode(),'utf-8') )
               
                for addr in arr_of_addr:
                    addr_as_bytes = pack(">I", int(addr[2:],16) )
                    #print(addr_as_bytes)
                    file_handler.write( addr_as_bytes )

        file_handler.close()
    
    def does_GameExist(self,gameName):
        ret = False
        for g in self.gameCheats:
            if str(g.get_gameName()) == gameName:
                ret = True
        return ret
    
    def get_Game(self,gameName):
        for g in self.gameCheats:
            if g.get_gameName() == gameName:
                return g


    def transform_address_bytes_to_string(self, raw_address_bytes):
        addresses_array = []
        iu = iter_unpack(">I", raw_address_bytes)
        for char in iu:
            a = [hex(h) for h in char]
            addresses_array += a

        return addresses_array

    def __org_transform_address_bytes_to_string(self,raw_address_bytes):
        PART_LEN = 4
        num_addresses = int( len(raw_address_bytes) / PART_LEN )
        addresses_array = []
        for i in range(num_addresses):
            address_as_string = ''
            raw_address_bytes_part = raw_address_bytes[PART_LEN*i:PART_LEN*(i+1)]
            for byte in raw_address_bytes_part[::-1]:
                char = hex(byte)[2:]
                address_as_string += char
            addresses_array.append(address_as_string)
        return addresses_array


    #[GameName]
    #TODO ViewReturnValues umbennen und hier integrieren
    def parse_model_data(self,data_file):
        try:
            file_handler = open(data_file,'rb')
        except Exception as e:
            print(e)
            return ParsingReturnValues.FILENAME_ERROR

        #read games and cheatcodes
        while (True):
            #read num of cheatcodes (per game)
            try:
                num_of_cheatcodes = file_handler.read(4)[0]
                
                #read Game Name (5 * 4 bytes (buffered up with 0x20s))
                GAME_NAME = file_handler.read(5 * 4)

                cheatname_addressstring = {}
                ###Loop reading addresses
                for _ in range(num_of_cheatcodes):
                    #read name of cheat code -> 5 * 4 bytes (buffered up with 0x20s)
                    len_of_address = file_handler.read(4)[0]
                    NAME_CHEATCODE = file_handler.read(5 * 0x4)

                    #read addresses -> 4 bytes + len from previos read
                    raw_address_bytes = file_handler.read(4 * len_of_address)
                    #transform addresses from hex to ascii (little-endian)
                    address_as_string_array = self.transform_address_bytes_to_string(raw_address_bytes)
                    cheatname_addressstring[NAME_CHEATCODE] = address_as_string_array

                self.games_and_cheatcodes[GAME_NAME] = cheatname_addressstring
            except:
                break

        #print(self.games_and_cheatcodes)
        file_handler.close()

        #Parse Data into individual GameCheat Objects <-- TODO necessary?? (maybe do the parsing in the for-loop above and not here again..)
        for game_name in self.games_and_cheatcodes:
            gameCheat = GameCheat()
            gameCheat.set_gameName(game_name)
            for cheat in self.games_and_cheatcodes[game_name]:
                gameCheat.set_cheatCodeName(cheat)
                gameCheat.set_cheatCodeAddresses(cheat,self.games_and_cheatcodes[game_name][cheat])
            self.gameCheats.append(gameCheat)

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
    


class ConcreteUserInterface(UserInterface):
    
    def __init__(self, view):
        self.view = view

    def get_user_action(self) -> UserAction:
        return self.view.get_user_action()

    def update_view(self, data, mode: ViewModes):
        return self.view.update_view(data, mode)

    
    def ask_input(self,text):
        return self.view.ask_input(text)
    
    def print_error(self, text):
        self.view.print_error(text)
    