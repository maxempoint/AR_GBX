from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, CtrlMsg, ViewTypes
from model import GameCheatData, GameCheat
import queue
import logging
import time


class CommandLineInterface(UserInterface):

    def __init__(self, callback, ctrl_msg_queue):
        self.type = ViewTypes.COMMAND_LINE
        self.actionDict = { "A": UserAction.SHOW_ALL_DATA_FROM_AR, 
                            "M": UserAction.MODIFY_DATA,
                            "E": UserAction.EXPORT_ALL_DATA,
                            "D": UserAction.DELETE_SINGLE_GAME,
                            "q": UserAction.END_PROGRAM}
        self.ctrl_msg_queue = ctrl_msg_queue
        self.callback = callback

    def interact(self):
        while True:
            if not self.ctrl_msg_queue.empty():
                (data, mode) = self.ctrl_msg_queue.get()
                self.handle_ctrl_msg(data, mode)
            else:
                self.get_user_action()
    
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
                userinput = UserInput(action,[data])
                self.callback( userinput )
            except KeyError:
                print("No such action")
                self.callback( UserInput(UserAction.NO_ACTION,[]) )
    
    #TODO pretty print <- depends on Data format 
    def handle_ctrl_msg(self, data, mode):
        if mode == CtrlMsg.END_GUI:
            exit(0)
        elif mode == CtrlMsg.PRINT_ALL:
            for game in data.gameCheats:
                print("--------------- All names ---------------")
                print(game.get_gameName())
                print("\n")
                print("--------------- Cheat Codes ---------------")
                #print(game.get_cheatCodeName())
                print(game.get_cheatCodeAddresses())
        elif mode == CtrlMsg.PRINT_GAME:
            for cheat in data.gameCheats:
                try:
                    print(cheat.get_gameName())
                except Exception as e:
                    print("Exception: " + e)
        elif mode == CtrlMsg.ERROR_MSG:
            #TODO
            pass
        else:
            raise ValueError
            print("No Such CtrlMsg")