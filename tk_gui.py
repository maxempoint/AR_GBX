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
        self.text_field = None

        self.ctrl_msg_queue = ctrl_msg_queue
        self.callback = callback
    
    def create_info_text_field(self):
        T = tk.Text(self.root, height=9, width=30)
        T.insert(tk.END,"")
        T.pack()
        return T

    def interact(self):
        self.root = tk.Tk()

        self.text_field = self.create_info_text_field()

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
            print("in handle ctrl!!")
            for game in data.gameCheats:
                text = "--------------- All names ---------------\n" + str(game.get_gameName()) + "\n" +   "--------------- Cheat Codes ---------------\n" + str(game.get_cheatCodeAddresses())
                self.text_field.insert(tk.END,text)
                self.text_field.update()
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

