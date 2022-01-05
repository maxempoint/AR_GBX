import tkinter as tk
from tkinter.messagebox import askyesno

from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, CtrlMsg, ViewTypes
from model import GameCheatData, GameCheat
import queue


class GUI(UserInterface):
    def __init__(self, callback, ctrl_msg_queue):
        self.type = ViewTypes.TKINTER_GUI
        self.ctrl_msg_queue = ctrl_msg_queue
        self.callback = callback
    
    def interact(self):
        root = tk.Tk()
        frame = tk.Frame(root)
        frame.pack()

        button = tk.Button(frame, 
                        text="QUIT", 
                        fg="red",
                        command=quit)
        button.pack(side=tk.LEFT)

        show_all = tk.Button(frame,
                        text="Print Games",
                        width=25,
                        command=self.callback(UserInput(UserAction.SHOW_ALL_DATA_FROM_AR,[])))
        show_all.pack(side=tk.LEFT)
        show_all.config(font=("Courier", 33))

        slogan = tk.Button(frame,
                        text="Print help",
                        width=25,
                        command=self.callback(UserInput(UserAction.SHOW_ALL_DATA_FROM_AR,[])))
        slogan.pack(side=tk.LEFT)
        slogan.config(font=("Courier", 33))

        root.mainloop()
    
    def get_user_action(self):
        #TODO
        pass
    
    def handle_ctrl_msg(self, data, mode: CtrlMsg):
        #TODO
        pass

