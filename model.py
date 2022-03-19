from abstract_classes import *
import driverAR
import logging
import json

class Model:
    def __init__(self, export_filename, import_filename, mock):
        self.SOURCE_FILENAME = import_filename
        self.EXPORT_FILENAME = export_filename
        logging.info("Export in Model " + self.EXPORT_FILENAME)
        logging.info("Import in Model " + self.SOURCE_FILENAME)

        #Note: driver has to be initalized before gameCheatData parses the data
        self.driver = self.__init_driver(export_filename, import_filename, use_mock_data=mock)

        self.game_cheats = []
        self.parse_model_data()
    
###--Getter--##
        
    def get_game(self, game_name):
        for g in self.game_cheats:
            if g.get_sanitized_game_name() == game_name:
                return g
        raise ValueError()
    
    def get_games_as_json(self):
        all_games = {}
        for g in self.game_cheats:
            all_games |= g.get_sanitized_game_data()
        return json.dumps(all_games)

    def get_num_of_games(self):
        return len(self.gameCheats)

###--Manipulate-Internal-Data--###    
    
    def add_gamecheat(self, game_name, games_and_cheatcodes):
        #TODO Checks + sanitation einbauen
        gameCheat = GameCheat()
        gameCheat.set_gameName(game_name)
        logging.info(games_and_cheatcodes)
        for cheat in games_and_cheatcodes:
            cheatname, addresses = list(cheat.items())[0]
            gameCheat.set_cheatCodeName(cheatname)
            gameCheat.set_cheatCodeAddresses(cheatname, addresses)

        self.game_cheats.append(gameCheat)
        return

    
    def delete_current_gamecheats(self):
        self.gameCheats = []

###--I/O--###    
    # internal_data -> file; write data in bytes format to file
    def write_data_to_file(self):
        logging.info("In model.write_data_to_file. This is the filename the data is written to: " + self.EXPORT_FILENAME)
        file_handler = open(self.EXPORT_FILENAME, "wb")
        for cheatcode in self.game_cheats:
            file_handler.write( pack("<i", len(cheatcode.get_cheatCodeNames()) ) )
            file_handler.write( bytes(cheatcode.get_gameName().decode(),'utf-8') )
            for c in cheatcode.get_cheatCodeAddresses():
                #logging.info("In model.write_data_to_file: " + str(c))
                arr_of_addr = cheatcode.get_cheatCodeAddresses()[c]
                file_handler.write( pack("<i", len(arr_of_addr)) )
                file_handler.write( bytes(c.decode(),'utf-8') )
               
                for addr in arr_of_addr:
                    addr_as_bytes = pack(">I", int(addr[2:],16) )
                    #logging.info(addr_as_bytes)
                    file_handler.write( addr_as_bytes )

        file_handler.close()

    def transform_address_bytes_to_string(self, raw_address_bytes):
        addresses_array = []
        iu = iter_unpack(">I", raw_address_bytes)
        for char in iu:
            a = [hex(h) for h in char]
            addresses_array += a

        return addresses_array
    
    # file -> internal_data; parsing data from file
    def parse_model_data(self):
        games_and_cheatcodes = {}
        try:
            file_handler = open(self.SOURCE_FILENAME,'rb')
        except Exception as e:
            logging.info(e)
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

                games_and_cheatcodes[GAME_NAME] = cheatname_addressstring
            except:
                break

        #logging.info(self.games_and_cheatcodes)
        file_handler.close()

        #Parse Data into individual GameCheat Objects <-- TODO necessary?? (maybe do the parsing in the for-loop above and not here again..)
        for game_name in games_and_cheatcodes:
            gameCheat = GameCheat()
            gameCheat.set_gameName(game_name)
            for cheat in games_and_cheatcodes[game_name]:
                gameCheat.set_cheatCodeName(cheat)
                gameCheat.set_cheatCodeAddresses(cheat, games_and_cheatcodes[game_name][cheat])
            self.game_cheats.append(gameCheat)
    
  
    def write_data_to_device(self):
        self.write_data_to_file()
        self.driver.write_data_to_device(self.gameCheatData.get_num_of_games())

    def read_data_from_device(self):
        self.driver.read_data() #writes to file imported_data.dat
        self.delete_current_gamecheats()
        self.parse_model_data()

###--Driver-Stuff--###
    def __init_driver(self, EXPORT_FILENAME, IMPORT_FILENAME, use_mock_data=True):
        if use_mock_data:
            driver = driverAR.PythonDriver(EXPORT_FILENAME, IMPORT_FILENAME, mock=True)
        else:
            logging.info("Model: in init_driver")
            driver = driverAR.PythonDriver(EXPORT_FILENAME, IMPORT_FILENAME, mock=False)
            driver.read_data() #TODO parametrize driver.DATA_FILE
            #TODO find out why driver.read_data() interferes with the write-operation...
            #TODO interprocess communication (e.g. queue) instead of these files
        return driver

    def tear_down(self):
        self.delete_current_gamecheats()
        self.driver.exit_driver()


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
            logging.warning("Cheat Code Name already exists!")
    
    def set_cheatCodeAddresses(self, cheatName, addresses):
        if cheatName in self.cheatCodesName:
            self.cheatCodeAddresses[cheatName] = addresses
        else:
            logging.warning("Cheat Code Name is not set!")

    def __stringify_data(self, data):
        #remove bystring marks
        if str(data)[0] == 'b':
            stringified = str(data)[2:-1]
        else:
            stringified = str(data)
        #remove unnecessary newlines
        no_newlines = stringified.replace('\n', '')
        no_parenth = no_newlines.replace('\'', '')
        return no_parenth.strip()
    
    def get_sanitized_game_data(self):
        game = {}
        san_cheatCodeAddresses = {}
        for cc in self.cheatCodeAddresses:
            san_cc = self.__stringify_data(cc) 
            san_cheatCodeAddresses[san_cc] = self.cheatCodeAddresses[cc]
        san_gameName = self.__stringify_data(self.gameName)
        game[san_gameName] = san_cheatCodeAddresses
        return game
    
    def get_sanitized_game_name(self):
        return self.__stringify_data(self.gameName)

    def get_sanitized_cheatCodeNames(self):
        san_cheatcode_names = []
        for cc in self.cheatCodesName:
            san_cheatcode_names.append(self.__stringify_data(cc))
        return san_cheatcode_names

    def get_sanitized_cheatCodeAddresses(self):
        san_cheatCodeAddresses = {}
        for cc in self.cheatCodeAddresses:
            san_cc = self.__stringify_data(cc) 
            san_cheatCodeAddresses[san_cc] = self.cheatCodeAddresses[cc]
        return san_cheatCodeAddresses

    def get_gameName(self):
        return self.gameName
    
    def get_cheatCodeNames(self):
        return self.cheatCodesName
    
    def get_cheatCodeAddresses(self):
        return self.cheatCodeAddresses