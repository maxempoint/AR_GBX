from abstract_userinterface import UserAction, ParsingReturnValues, GameCheatData, GameCheat, ViewModes

class CommandLineInterface():

    def get_user_action(self) -> UserAction:
        print("What do you want?")
        print("type 'h' for help")
        i = input()
        if i == "h":
            print("A: Print all data from Replay")
            print("I: Import all data to an xpc file")
            print("E: Export data from xpc file")
            print("D: Delete a Game and its Cheatcodes")
            print("M: Modify a Cheatcode entry")
            print("q: end program")
            return UserAction.NO_ACTION
        elif i == "A":
            return UserAction.SHOW_ALL_DATA_FROM_AR
        elif i == "M":
            print("Entering Modifiyng Mode -- Type 'q' to quit")
            return UserAction.MODIFY_DATA
        elif i == "E":
            return UserAction.EXPORT_ALL_DATA
        elif i == "D":
            return UserAction.DELETE_SINGLE_GAME
        elif i == "q":
            return UserAction.END_PROGRAM
        else:
            return UserAction.NO_ACTION
    
    #TODO pretty print <- depends on Data format 
    def update_view(self, data, mode):
        if mode == ViewModes.PRINT_ALL:
            for game in data.gameCheats:
                print("--------------- All names ---------------")
                print(game.get_gameName())
                print("\n")
                print("--------------- Cheat Codes ---------------")
                #print(game.get_cheatCodeName())
                print(game.get_cheatCodeAddresses())
        elif mode == ViewModes.PRINT_GAME:
            try:
                print(data.get_gameName())
            except Exception as e:
                self.print_error("Exception: " + e)
        else:
            self.print_error("This should never be reached")
    
    def ask_input(self, text):
        print(text)
        i = input()
        return i
    
    
    def print_error(self,text):
        print("[!] " + text)
