from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, UserAction, ViewTypes
from model import GameCheatData, GameCheat
import queue
import logging
import time


class CommandLineInterface(UserInterface):

    def __init__(self, callback, model):
        self.type = ViewTypes.COMMAND_LINE
        self.actionDict = { "A": UserAction.SHOW_ALL_DATA_FROM_AR, 
                            "M": UserAction.MODIFY_DATA,
                            "E": UserAction.EXPORT_ALL_DATA,
                            "D": UserAction.DELETE_SINGLE_GAME,
                            "q": UserAction.END_PROGRAM}
        self.callback = callback
        self.model = model
        self.state = UserAction.NO_ACTION

    def interact(self):
        while True:
            self.get_user_action()
            self.fetch_model_data()
    
    def parse_user_input(self, user_input):
        if len(user_input) == 1:
            return (user_input, '')
        return (user_input[0], user_input[1:])
            
    def get_user_action(self):
        print("Input an action\nType \'h\' for help")
        i = input()
        action, data = self.parse_user_input(i)
        #logging.info(i)
        if action == "h":
            print("A: Print all data from Replay")
            print("I: Import all data to an xpc file")
            print("E: Export data from xpc file")
            print("D: Delete a Game and its Cheatcodes")
            print("M: Modify a Cheatcode entry -> M N <Cheat Code Name> C <Cheatcode> No <number of address> D <data>")
            print("q: end program")
            self.callback( UserInput(UserAction.NO_ACTION,[data]) )
        else:
            try:
                action = self.actionDict[action]
                self.state = action
                userinput = UserInput(action,[data])
                self.callback( userinput )
            except KeyError:
                print("No such action")
                self.callback( UserInput(UserAction.NO_ACTION,[]) )
    
    #TODO pretty print <- depends on Data format 
    def fetch_model_data(self):
        mode = self.state
        gameCheatData = self.model.get_gamecheatdata()
        if mode == UserAction.END_PROGRAM:
            exit(0)
        elif mode == UserAction.SHOW_ALL_DATA_FROM_AR:
            for game in gameCheatData.gameCheats:
                print("--------------- All names ---------------")
                print(game.get_gameName())
                print("\n")
                print("--------------- Cheat Codes ---------------")
                #print(game.get_cheatCodeName())
                print(game.get_cheatCodeAddresses())
        elif mode == UserAction.PRINT_GAME:
            for cheat in gameCheatData.gameCheats:
                try:
                    print(cheat.get_gameName())
                except Exception as e:
                    print("Exception: " + e)
        elif mode == UserAction.ERROR_MSG:
            #TODO
            pass
        elif mode == UserAction.NO_ACTION:
            pass
        else:
            pass
            