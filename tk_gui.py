import tkinter as tk
from tkinter import StringVar

import traceback

from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, ViewTypes
from model import GameCheatData, GameCheat
import queue
#partial to invoke callback with arguments
from functools import partial


class GUI(UserInterface):
    def __init__(self, callback, model):
        self.type = ViewTypes.TKINTER_GUI
        self.CCN = "CCN "

        self.root = None
        #TODO Define different Text Fields for different data (game name, cheatname, etc.)
        self.cheatcode_text = None
        self.cheatcode_text = None
        self.addresses_text = None

        self.state = UserAction.NO_ACTION
        self.callback = callback
        self.model = model
    
    def create_info_text_field(self, height, width):
        T = tk.Text(self.root, height=height, width=width)
        T.insert(tk.END,"")
        T.pack()
        return T
    
    def create_option_menu(self):
        variable = StringVar(self.root)
        variable.set("Select Game")
        names = []
        for game in self.model.get_gamecheatdata().gameCheats:
            names.append( game.get_gameName() )
        O = tk.OptionMenu(self.root, variable, *names)
        O.pack()
        return variable, O

    def interact(self):
        self.root = tk.Tk()

        self.cheatcode_text = self.create_info_text_field(50,50)
        self.new_game_name_text = self.create_info_text_field(1, 50)
        self.select_game_menu, self.opt_menu = self.create_option_menu()

        frame = tk.Frame(self.root)
        frame.pack()

        end = tk.Button(frame, 
                        text="QUIT", 
                        fg="red",
                        command=partial(self.get_user_action, UserAction.END_PROGRAM) )
        end.pack(side=tk.LEFT)

        show_all = tk.Button(frame,
                        text="Print Games",
                        width=10,
                        command=partial(self.get_user_action, UserAction.SHOW_ALL_DATA_FROM_AR) )
        show_all.pack(side=tk.LEFT)
        show_all.config(font=("Courier", 22))

        show_all = tk.Button(frame,
                        text="Modify",
                        width=10,
                        command=partial(self.get_user_action, UserAction.MODIFY_DATA) )
        show_all.pack(side=tk.LEFT)
        show_all.config(font=("Courier", 22))

        add_game = tk.Button(frame,
                        text="Add Game",
                        width=10,
                        command=partial(self.get_user_action, UserAction.ADD_NEW_CHEAT) )
        add_game.pack(side=tk.BOTTOM)
        add_game.config(font=("Courier", 22))

        self.root.mainloop()
    
    
    def get_user_action(self, useraction : UserAction):
        self.state = useraction
        data = self.get_userdata_input()
        try:
            self.callback( UserInput(useraction,data) )
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            self.state = UserAction.ERROR_MSG
            self.fetch_model_data()
            return
        self.fetch_model_data()
    
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
    
    def get_userdata_input(self):
        raw_text = self.cheatcode_text.get("1.0",tk.END + '-1c')
        lines = raw_text.splitlines()
        #Get game name from current OptionMenu Selection
        if self.new_game_name_text.get("1.0",tk.END + '-1c') == '':
            cheatcodes = [self.stringify_data( self.select_game_menu.get())[:-1]]
        else:
            cheatcodes = [self.stringify_data( self.new_game_name_text.get("1.0",tk.END + '-1c'))[:-1]]
        
        for line in lines:
            if line == '':
                continue
            if line.startswith(self.CCN):
                cheatcodes.append("|")
                cheatcodes.append(line[4:])
            else:
                cheatcodes.append(line[1:-1])

        return cheatcodes

    def fetch_model_data(self):
        mode = self.state
        data = self.model.get_gamecheatdata()

        if mode == UserAction.END_PROGRAM:
            self.root.quit()
        elif mode == UserAction.SHOW_ALL_DATA_FROM_AR:
            
            #remove previous text
            self.cheatcode_text.delete("1.0",tk.END)
            self.cheatcode_text.update()

            game_name = self.select_game_menu.get()
            game = data.get_Game(game_name)
            
            for cc in game.get_cheatCodeNames():
                self.cheatcode_text.insert(tk.END, self.CCN + self.stringify_data(cc) )
                self.cheatcode_text.insert(tk.END, self.stringify_data(game.get_cheatCodeAddresses()[cc]) )
                self.cheatcode_text.insert(tk.END, "\n\n")
                
            self.cheatcode_text.update()

        elif mode == UserAction.PRINT_GAME:
            for cheat in data.gameCheats:
                try:
                    print("Tk model.fetch_model_data(): " + cheat.get_gameName())
                except Exception as e:
                    print("Exception: " + e)
        elif mode == UserAction.ERROR_MSG:
            self.cheatcode_text.delete("1.0",tk.END)
            self.cheatcode_text.update()
            self.cheatcode_text.insert(tk.END, "You fucked up")
            pass
        elif mode == UserAction.NO_ACTION:

            pass
        elif mode == UserAction.EXPORT_ALL_DATA:
            pass
        elif mode == UserAction.MODIFY_DATA:
            pass
        elif mode == UserAction.ADD_NEW_CHEAT:
            self.opt_menu.destroy()
            self.select_game_menu, self.opt_menu = self.create_option_menu()
            pass
        else:
            print("View says: No Such UserAction")
            raise ValueError
            

