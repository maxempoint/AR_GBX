import tkinter as tk
from tkinter import StringVar
from tkinter.messagebox import askyesno
from tkinter import messagebox

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
        self.error = None
        self.traceback = None

        self.root = None
        #TODO Define different Text Fields for different data (game name, cheatname, etc.)
        self.cheatcode_text = None
        self.addresses_entries_frame = None
        self.select_game_menu = None

        self.select_cheatcode = None
        self.cheatcode_opt_menu = None

        self.state = UserAction.NO_ACTION
        self.callback = callback
        self.model = model
        self.model_data = json.loads(model.get_games_as_json())

        self.no_data_actions = [UserAction.SHOW_ALL_DATA_FROM_AR,
                                UserAction.PRINT_GAME,
                                UserAction.NO_ACTION,
                                UserAction.END_PROGRAM]
    
    def create_info_field(self, height, width, row, column):
        T = tk.Entry(self.root, width=width)
        T.insert(tk.END,"")
        T.grid(row=row,column=column)
        return T
    
    def create_cheatcodes_frame(self, master, row, column):
        frame = tk.Frame(master=master)
        frame.grid(row=row, column=column)
        for num_of_entry in range(10): #TODO define constant?
            entry = tk.Entry(master=frame, width=50)
            entry.insert(tk.END, "")
            entry.pack()
        return frame
    
    def create_cheatcode_option_menu(self, master, row, column):
        variable = StringVar(master)
        #Get currently selected game
        game_name = self.select_game_menu.get()
        cheat_names = self.model_data[game_name]
        variable.set(list(cheat_names)[0])
        names = []
        for cheat in cheat_names:
            names.append( cheat )
        O = tk.OptionMenu(  self.root,
                            variable,
                            *names)
        O.grid(row=row, column=column)

        return variable, O
    
    def create_games_option_menu(self, row, column):
        variable = StringVar(self.root)
        gameCheats = self.model_data
        variable.set(list(gameCheats)[0])
        names = []
        for game in gameCheats:
            names.append( game )
        O = tk.OptionMenu(  self.root,
                            variable,
                            *names)
        O.grid(row=row, column=column)
        return variable, O
    
    def create_buttons(self, row, column):
        frame = tk.Frame(self.root)
        frame.grid(row=row, column=column)

        end = tk.Button(frame, 
                        text="QUIT", 
                        fg="red",
                        command=partial(self.get_user_action, UserAction.END_PROGRAM) )
        end.pack(side=tk.TOP)

        show_all = tk.Button(frame,
                        text="Print Games",
                        width=10,
                        command=partial(self.get_user_action, UserAction.SHOW_ALL_DATA_FROM_AR) )
        show_all.pack(side=tk.TOP)
        show_all.config(font=("Courier", 22))

        show_all = tk.Button(frame,
                        text="Modify",
                        width=10,
                        command=partial(self.get_user_action, UserAction.MODIFY_DATA) )
        show_all.pack(side=tk.TOP)
        show_all.config(font=("Courier", 22))

        add_game = tk.Button(frame,
                        text="Add Game",
                        width=10,
                        command=partial(self.get_user_action, UserAction.ADD_NEW_CHEAT) )
        add_game.pack(side=tk.BOTTOM)
        add_game.config(font=("Courier", 22))

    def init_for_interaction(self):
        self.root = tk.Tk()

        self.addresses_entries_frame = self.create_cheatcodes_frame(master=self.root, row=2,column=2)

        #TODO maybe instead of OptionMenu for the Games use ListBox?
        self.new_game_name_entry = self.create_info_field(1, 50, row=1, column=1)
        self.select_game_menu, self.opt_menu = self.create_games_option_menu(row=1, column=0)
        self.create_buttons(row=0, column=0)
        self.select_cheatcode, self.cheatcode_opt_menu = self.create_cheatcode_option_menu(self.root, row=2, column=2)
        

    def interact(self):
        self.init_for_interaction()
        self.root.mainloop()

    #Error Message Pop up
    def error_msg_dialog(self):
        messagebox.showerror("ERROR", "An error occurred:\n" +
                            str(self.error) +
                            "\n\n" +
                            "Traceback\n" +
                            str(self.traceback) )

    #Adds confirmation dialog before every action
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
        #Check if data is needed for the useraction
        if self.state in self.no_data_actions:
            data = None
        elif self.state == UserAction.ADD_NEW_CHEAT:
            #TODO implement
            data = None
        else: #
            data = self.get_userdata_input()
        if not self.confirmation_dialog(useraction, data):
            return
        try:
            self.callback( UserInput(useraction, data) )
        except Exception as e:
            self.traceback = traceback.format_exc()
            self.error = e
            self.state = UserAction.ERROR_MSG
            self.fetch_model_data()
            return
        return self.fetch_model_data()

###|--HUMBLE-OBJECT--|###
    #TODO this should be outside of the humble object...
    #TODO This function assumes that the game already exists -> this must be assured
    def __merge_userinput_with_old_data(self, game_name, cheatcode_name, new_addresses):
        cheat_names = self.model_data[game_name]
        #Find changed cheat
        cheat_names[cheatcode_name] = new_addresses
        return cheat_names

    #This function should return a dict object, structured like this:
    # {String : {String : [HexStrings]}}
    # {GameName : { Cheat00: [addr1, addr2, ...], Cheat01 : [...], ...} }
    #
    #Note: this function should give back a whole games+cheatcodes
    def get_userdata_input(self):
        #Get game name from current OptionMenu Selection
        if self.new_game_name_entry.get() == '':
            game_name = self.select_game_menu.get()
        else:
            game_name = self.new_game_name_entry.get()

        cheatcodes = {}
        new_addresses = []

        #Note: Only the currently selected cheatcode and its addresses are pull from the GUI        
        cheatcode_entries = self.addresses_entries_frame.winfo_children()
        selected_cheat_code_name = self.select_cheatcode.get()

        for entry in cheatcode_entries:
            if entry.get() != '':
                new_addresses.append(entry.get())

        cheatcodes = self.__merge_userinput_with_old_data(game_name,
                                                        selected_cheat_code_name,
                                                        new_addresses)       
        
        return {game_name : cheatcodes}

    def clear_gui(self):
        for cheatcode_entry in self.addresses_entries_frame.winfo_children():
            cheatcode_entry.delete("0",tk.END)
            cheatcode_entry.update()

    def insert_into_gui(self, game_name, cheatcode_name, addresses):
        cheatcode_entries = self.addresses_entries_frame.winfo_children()
        number_of_entries = len(cheatcode_entries)
        for index, address in enumerate(addresses):
            if number_of_entries > index:
                cheatcode_entries[index].insert(tk.END, address)
                cheatcode_entries[index].update()
            else:
                logging.error("Too many cheatcodes for display!")
                raise IndexError()      

        self.new_game_name_entry.delete("0",tk.END)
        self.new_game_name_entry.update()
        self.new_game_name_entry.insert(tk.END, game_name)

        return {"game_name" : game_name, "cheatcodes" :  cheatcode_name, "addresses" : addresses}

###^--HUMBLE-OBJECT--^### 

    #TODO rename
    def fetch_model_data(self) -> []:
        mode = self.state

        #DELETE
        data_json = self.model.get_games_as_json()
        data_dict = json.loads(data_json)
        #^DELETE

        gui_data = []

        if mode == UserAction.END_PROGRAM:
            self.root.quit()
        elif mode == UserAction.SHOW_ALL_DATA_FROM_AR:

            selected_game_name = self.select_game_menu.get()
            #Update select_cheatcode for new game
            # grid_info = self.cheatcode_opt_menu.grid_info() 
            # self.cheatcode_opt_menu.destroy()
            # self.select_cheatcode, self.cheatcode_opt_menu = self.create_cheatcode_option_menu(
            #                                                     master=self.root,
            #                                                     row=grid_info["row"],
            #                                                     column=grid_info["column"]
            #                                                     )

            selected_cheat_code_name = self.select_cheatcode.get()
            cheat_codes = self.model_data[selected_game_name]

            #remove previous text
            self.clear_gui()        
            #TODO appending still nececessary?
            gui_data.append(
                self.insert_into_gui(
                    selected_game_name,
                    selected_cheat_code_name,
                    cheat_codes[selected_cheat_code_name]
                    )
            )

            return gui_data
        elif mode == UserAction.PRINT_GAME:
            for cheat in data.gameCheats:
                try:
                    print("Tk model.fetch_model_data(): " + cheat.get_gameName())
                except Exception as e:
                    print("Exception: " + e)
        elif mode == UserAction.ERROR_MSG:
            self.clear_gui()
            self.error_msg_dialog()
            pass
        elif mode == UserAction.NO_ACTION:
            pass
        elif mode == UserAction.EXPORT_ALL_DATA:
            pass
        elif mode == UserAction.MODIFY_DATA:
            pass
        elif mode == UserAction.ADD_NEW_CHEAT:
            grid_info = self.opt_menu.grid_info()
            self.opt_menu.destroy()
            self.select_game_menu, self.opt_menu = self.create_games_option_menu(row=grid_info["row"], column=grid_info["column"])
        else:
            print("View says: No Such UserAction")
            raise ValueError
