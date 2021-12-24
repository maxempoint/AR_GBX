from abstract_classes import UserInterface, UserAction, ParsingReturnValues, ViewModes
from model import GameCheatData, GameCheat

class CommandLineInterface(UserInterface):

    def __init__(self):
        self.actionDict = {"A": UserAction.SHOW_ALL_DATA_FROM_AR, "M": UserAction.MODIFY_DATA, "E": UserAction.EXPORT_ALL_DATA, "D": UserAction.DELETE_SINGLE_GAME, "q": UserAction.END_PROGRAM}

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
        else:
            try:
                action = self.actionDict[i]
                return action
            except KeyError:
                print("No such action")
                return UserAction.NO_ACTION
    
    #TODO pretty print <- depends on Data format 
    def update_view(self, data: GameCheatData, mode):
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
                print(data.gameCheats[0].get_gameName())
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
