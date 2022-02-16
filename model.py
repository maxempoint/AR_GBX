from abstract_classes import *
import driverAR

class Model:
    def __init__(self, export_filename, import_filename, mock):
        self.SOURCE_FILENAME = import_filename
        self.EXPORT_FILENAME = export_filename
        print("Export in Model " + self.EXPORT_FILENAME)
        print("Import in Model " + self.SOURCE_FILENAME)

        #Note: driver has to be initalized before gameCheatData parses the data
        self.driver = self.__init_driver(export_filename, import_filename, use_mock_data=mock)


        self.gameCheatData = GameCheatData(export_filename=self.EXPORT_FILENAME, import_filename=self.SOURCE_FILENAME)
        self.gameCheatData.parse_model_data()
    
    def get_gamecheatdata(self):
        return self.gameCheatData
    
    def add_gamecheat(self, game_name, games_and_cheatcodes):
        self.gameCheatData.set_Game(game_name, games_and_cheatcodes)
    
    #write data in bytes format to file
    def write_data_to_file(self):
        print("In model.write_data_to_file. This is the filename the data is written to: " + self.EXPORT_FILENAME)
        file_handler = open(self.EXPORT_FILENAME, "wb")
        for cheatcode in self.gameCheatData.gameCheats:
            file_handler.write( pack("<i", len(cheatcode.get_cheatCodeNames()) ) )
            file_handler.write( bytes(cheatcode.get_gameName().decode(),'utf-8') )
            for c in cheatcode.get_cheatCodeAddresses():
                #print("In model.write_data_to_file: " + str(c))
                arr_of_addr = cheatcode.get_cheatCodeAddresses()[c]
                file_handler.write( pack("<i", len(arr_of_addr)) )
                file_handler.write( bytes(c.decode(),'utf-8') )
               
                for addr in arr_of_addr:
                    addr_as_bytes = pack(">I", int(addr[2:],16) )
                    #print(addr_as_bytes)
                    file_handler.write( addr_as_bytes )

        file_handler.close()
    
    def write_data_to_device(self):
        self.write_data_to_file()
        self.driver.write_data_to_device(self.gameCheatData.get_num_of_games())

    def read_data_from_device(self):
        self.driver.read_data() #writes to file imported_data.dat
        self.gameCheatData.delete_current_gamecheats()
        self.gameCheatData.parse_model_data()

    def __init_driver(self, EXPORT_FILENAME, IMPORT_FILENAME, use_mock_data=True):
        if use_mock_data:
            driver = driverAR.PythonDriver(EXPORT_FILENAME, IMPORT_FILENAME, mock=True)
        else:
            print("Model: in init_driver")
            driver = driverAR.PythonDriver(EXPORT_FILENAME, IMPORT_FILENAME, mock=False)
            driver.read_data() #TODO parametrize driver.DATA_FILE
            #TODO find out why driver.read_data() interferes with the write-operation...
            #TODO interprocess communication (e.g. queue) instead of these files
        return driver

    def tear_down(self):
        self.gameCheatData.delete_current_gamecheats()
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
            print("Cheat Code Name already exists!")
    
    def set_cheatCodeAddresses(self, cheatName, addresses):
        if cheatName in self.cheatCodesName:
            self.cheatCodeAddresses[cheatName] = addresses
        else:
            print("Cheat Code Name is not set!")
    
    def get_gameName(self):
        return self.gameName
    
    def get_cheatCodeNames(self):
        return self.cheatCodesName
    
    def get_cheatCodeAddresses(self):
        return self.cheatCodeAddresses#
    
    def delete_current_cheats(self):
        self.cheatCodesName = []
        self.cheatCodeAddresses = {}

class GameCheatData:
    def __init__(self, export_filename="new_mod_data.dat", import_filename="imported_data.dat"):
        self.gameCheats = []
        self.SOURCE_FILENAME = import_filename
        self.EXPORT_FILENAME = export_filename

        self.games_and_cheatcodes = {}
    
    def delete_current_gamecheats(self):
        self.gameCheats = []
        self.games_and_cheatcodes = {}

    def get_num_of_games(self):
        return len(self.gameCheats)
    
    def does_GameExist(self,gameName):
        ret = False
        for g in self.gameCheats:
            if str(g.get_gameName()) == gameName:
                ret = True
        return ret
    
    def stringify_data(self, data):
        #remove bystring marks
        if str(data)[0] == 'b':
            stringified = str(data)[2:-1]
        else:
            stringified = str(data)
        #remove unnecessary newlines
        no_newlines = stringified.replace('\n', '')
        no_parenth = no_newlines.replace('\'', '')
        return no_parenth.strip() + "\n"
        
    def get_Game(self,gameName):
        for g in self.gameCheats:
            if self.stringify_data(g.get_gameName())== self.stringify_data(gameName):
                return g

    def set_Game(self, game_name, games_and_cheatcodes):
        gameCheat = GameCheat()
        gameCheat.set_gameName(game_name)
        print(games_and_cheatcodes)
        for cheat in games_and_cheatcodes:
            cheatname, addresses = list(cheat.items())[0]
            gameCheat.set_cheatCodeName(cheatname)
            gameCheat.set_cheatCodeAddresses(cheatname, addresses)

        self.gameCheats.append(gameCheat)
        return


    def transform_address_bytes_to_string(self, raw_address_bytes):
        addresses_array = []
        iu = iter_unpack(">I", raw_address_bytes)
        for char in iu:
            a = [hex(h) for h in char]
            addresses_array += a

        return addresses_array

    #[GameName]
    #TODO ViewReturnValues umbennen und hier integrieren
    def parse_model_data(self):
        try:
            file_handler = open(self.SOURCE_FILENAME,'rb')
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