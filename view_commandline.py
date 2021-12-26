from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, CtrlMsg
from model import GameCheatData, GameCheat
import queue
import logging
import time

class CommandLineInterface(UserInterface):

    def __init__(self, queue_useraction, queue_updateview):
        self.actionDict = { "A": UserAction.SHOW_ALL_DATA_FROM_AR, 
                            "M": UserAction.MODIFY_DATA,
                            "E": UserAction.EXPORT_ALL_DATA,
                            "D": UserAction.DELETE_SINGLE_GAME,
                            "q": UserAction.END_PROGRAM}
        self.queue_useraction = queue_useraction
        self.queue_updateview = queue_updateview

    def interact(self):
        while True:
            if not self.queue_updateview.empty():
                gameCheatData, mode = self.queue_updateview.get()
                if mode == CtrlMsg.END_GUI:
                    exit(0)
                elif mode == CtrlMsg.READY_FOR_INPUT:
                    self.queue_useraction.put( self.get_user_action() )
                elif mode == CtrlMsg.READY_FOR_ADDITIONAL_DATA:
                    self.queue_useraction.put( self.get_additional_data() )
                else:
                    self.update_view(gameCheatData, mode)

    def get_additional_data(self):
        i = input()
        return i
            
    def get_user_action(self) -> UserInput:
        print("Input an action\nType \'h\' for help")
        i = input()
        #logging.info(i)
        if i == "h":
            print("A: Print all data from Replay")
            print("I: Import all data to an xpc file")
            print("E: Export data from xpc file")
            print("D: Delete a Game and its Cheatcodes")
            print("M: Modify a Cheatcode entry")
            print("q: end program")
            return UserInput(UserAction.NO_ACTION,[])
        else:
            try:
                action = self.actionDict[i]
                userinput = UserInput(action,[])
                return userinput
            except KeyError:
                print("No such action")
                return UserInput(UserAction.NO_ACTION,[])
    
    #TODO pretty print <- depends on Data format 
    def update_view(self, data: GameCheatData, mode: CtrlMsg):
        if mode == CtrlMsg.PRINT_ALL:
            for game in data.gameCheats:
                print("--------------- All names ---------------")
                print(game.get_gameName())
                print("\n")
                print("--------------- Cheat Codes ---------------")
                #print(game.get_cheatCodeName())
                print(game.get_cheatCodeAddresses())
        elif mode == CtrlMsg.PRINT_GAME:
            try:
                print(data.gameCheats[0].get_gameName())
            except Exception as e:
                print("Exception: " + e)
        else:
            print("This should never be reached")