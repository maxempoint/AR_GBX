import tkinter as tk

from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, CtrlMsg, ViewTypes
from model import GameCheatData, GameCheat
import queue
#partial to invoke callback with arguments
from functools import partial


class GUI(UserInterface):
    def __init__(self, callback, ctrl_msg_queue):
        self.type = ViewTypes.TKINTER_GUI

        self.root = None
        #TODO Define different Text Fields for different data (game name, cheatname, etc.)
        self.names_text = None
        self.cheatcode_text = None
        self.addresses_text = None

        self.ctrl_msg_queue = ctrl_msg_queue
        self.callback = callback
    
    def create_info_text_field(self, height, width):
        T = tk.Text(self.root, height=height, width=width)
        T.insert(tk.END,"")
        T.pack()
        return T

    def interact(self):
        self.root = tk.Tk()

        self.names_text = self.create_info_text_field(9,30)
        self.cheatcode_text = self.create_info_text_field(9,30)
        self.addresses_text = self.create_info_text_field(9,30)

        frame = tk.Frame(self.root)
        frame.pack()

        end = tk.Button(frame, 
                        text="QUIT", 
                        fg="red",
                        command=partial(self.callback, UserInput(UserAction.END_PROGRAM,[])))
        end.pack(side=tk.LEFT)

        show_all = tk.Button(frame,
                        text="Print Games",
                        width=25,
                        command=partial(self.callback, UserInput(UserAction.SHOW_ALL_DATA_FROM_AR,[])))
        show_all.pack(side=tk.LEFT)
        show_all.config(font=("Courier", 33))

        self.root.after(0, self.get_ctrl_msg) #checks ctrl_msg_queue
        self.root.mainloop()
    
    
    def get_ctrl_msg(self):
        if not self.ctrl_msg_queue.empty():
            (data, mode) = self.ctrl_msg_queue.get()
            self.handle_ctrl_msg(data, mode)
        self.root.after(10, self.get_ctrl_msg) #re-register callback
    
    def get_user_action(self):
        #TODO
        pass
    
    def handle_ctrl_msg(self, data, mode: CtrlMsg):
        if mode == CtrlMsg.END_GUI:
            self.root.quit()
        elif mode == CtrlMsg.PRINT_ALL:
            
            for game in data.gameCheats:
            
                self.names_text.insert(tk.END, str(game.get_gameName()) )
                self.names_text.update()

                self.cheatcode_text.insert(tk.END, str(game.get_cheatCodeNames()) )
                self.cheatcode_text.update()

                self.addresses_text.insert(tk.END, str(game.get_cheatCodeAddresses()) )
                self.addresses_text.update()
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

