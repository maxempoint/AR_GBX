import tkinter as tk
from tkinter import StringVar
from tkinter.messagebox import askyesno

import traceback
import json

from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, ViewTypes
from model import GameCheat
import queue
#partial to invoke callback with arguments
from functools import partial


class GUI(UserInterface):
    def __init__(self, callback, model, test=False):
        self.TEST = test
        self.type = ViewTypes.TKINTER_GUI
        self.CCN = "CCN "

        self.root = None
        #TODO Define different Text Fields for different data (game name, cheatname, etc.)
        self.cheatcode_text = None
        self.cheatcode_text = None
        self.addresses_text = None
        self.select_game_menu = None

        self.selected_option = None

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
        gameCheats = json.loads(self.model.get_games_as_json())
        variable.set(list(gameCheats)[0])
        names = []
        for game in gameCheats:
            names.append( game )
        O = tk.OptionMenu(  self.root,
                            variable,
                            *names)
        O.pack()
        return variable, O
    
    def init_for_interaction(self):
        self.root = tk.Tk()

        self.cheatcode_text = self.create_info_text_field(50,50)
        self.new_game_name_text = self.create_info_text_field(1, 50)
        self.select_game_menu, self.opt_menu = self.create_option_menu()
        

    def interact(self):
        self.init_for_interaction()
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
    
    #TODO add confirmation dialog before every action
    def confirmation_dialog(self, useraction: UserAction, data):
        if self.TEST:
            return True
        return askyesno(title=str(useraction),
                        message="Do you want to perform action: \n\n" +
                                str(useraction) + "\n\n" + 
                                "With data: \n\n" +
                                str(data))

    def get_user_action(self, useraction : UserAction):
        self.state = useraction
        data = self.get_userdata_input()
        if not self.confirmation_dialog(useraction, data):
            return
        try:
            self.callback( UserInput(useraction, data) )
        except Exception as e:
            print(traceback.format_exc())
            print(e)
            self.state = UserAction.ERROR_MSG
            self.fetch_model_data()
            return
        return self.fetch_model_data()

###|--HUMBLE-OBJECT--|###    

    #This function should return a dict object, structured like this:
    # {String : {String : [HexStrings]}}
    # {GameName : { Cheat00: [addr1, addr2, ...], Cheat01 : [...], ...} }
    def get_userdata_input(self):
        raw_text = self.cheatcode_text.get("1.0",tk.END + '-1c')
        lines = raw_text.splitlines()
        #Get game name from current OptionMenu Selection
        if self.new_game_name_text.get("1.0",tk.END + '-1c') == '':
            game_name = self.select_game_menu.get()
        else:
            game_name = self.new_game_name_text.get("1.0",tk.END + '-1c')

        cheatcodes = {}
        for line in lines:
            if line == '':
                continue
            if line.startswith(self.CCN):
                current_cheat_name = line[4:]
            else:
                cheatcodes[current_cheat_name] = [line[1:-1]]

        return {game_name : cheatcodes}

    def clear_gui(self):
        self.cheatcode_text.delete("1.0",tk.END)
        self.cheatcode_text.update()


    def insert_into_gui(self, game_name, cheatcode_name, addresses):

        self.new_game_name_text.delete("1.0",tk.END)
        self.new_game_name_text.update()
        self.new_game_name_text.insert(tk.END, game_name)

        self.cheatcode_text.insert(tk.END, self.CCN + cheatcode_name +"\n")
        self.cheatcode_text.insert(tk.END, ', '.join(addresses) +"\n")
        self.cheatcode_text.insert(tk.END, "\n\n")

        self.cheatcode_text.update()

        return {"game_name" : game_name, "cheatcodes" :  cheatcode_name, "addresses" : addresses}

###^--HUMBLE-OBJECT--^### 

    def fetch_model_data(self):
        mode = self.state
        data_json = self.model.get_games_as_json()
        data_dict = json.loads(data_json)
        gui_data = []

        if mode == UserAction.END_PROGRAM:
            self.root.quit()
        elif mode == UserAction.SHOW_ALL_DATA_FROM_AR:

            game_name = self.select_game_menu.get()
            cheat_codes = data_dict[game_name]

            #remove previous text
            self.clear_gui()        
            for cheatcode_name in cheat_codes:
               gui_data.append( self.insert_into_gui(game_name,
                                    cheatcode_name,
                                    cheat_codes[cheatcode_name])
               )

            return gui_data
        elif mode == UserAction.PRINT_GAME:
            for cheat in data.gameCheats:
                try:
                    print("Tk model.fetch_model_data(): " + cheat.get_gameName())
                except Exception as e:
                    print("Exception: " + e)
        elif mode == UserAction.ERROR_MSG:
            #TODO show Error Message as pop up box
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
            

