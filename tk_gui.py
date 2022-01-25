import tkinter as tk

from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, ViewTypes
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

        self.state = UserAction.NO_ACTION
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

        self.root.mainloop()
    
    
    
    def get_user_action(self):
        #TODO
        pass
    
    def fetch_model_data(self):
        mode = self.state
        if mode == UserAction.END_PROGRAM:
            self.root.quit()
        elif mode == UserAction.SHOW_ALL_DATA_FROM_AR:
            
            for game in data.gameCheats:
            
                self.names_text.insert(tk.END, str(game.get_gameName()) )
                self.names_text.update()

                self.cheatcode_text.insert(tk.END, str(game.get_cheatCodeNames()) )
                self.cheatcode_text.update()

                self.addresses_text.insert(tk.END, str(game.get_cheatCodeAddresses()) )
                self.addresses_text.update()
        elif mode == UserAction.PRINT_GAME:
            for cheat in data.gameCheats:
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
            raise ValueError
            print("No Such UserAction")

