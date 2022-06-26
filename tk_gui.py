import tkinter as tk
from tkinter import StringVar
from tkinter.messagebox import askyesno
from tkinter import messagebox
from tkinter import simpledialog

import traceback
import json

from abstract_classes import UserInterface, UserInput, UserAction, ParsingReturnValues, ViewTypes
from model import GameCheat
import queue
# partial to invoke callback with arguments
from functools import partial


class GUI(UserInterface):
    def __init__(self, callback, model, test=False):
        self.TEST = test
        self.type = ViewTypes.TKINTER_GUI
        self.error = None
        self.traceback = None

        self.root = None
        self.addresses_entries_frame = None
        self.select_game_menu = None
        self.opt_menu = None

        self.add_cheatcode_option_string = "--Add New Cheatcode--"
        self.add_game_option_string = "--Add Game--"

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
        for num_of_entry in range(10): # TODO define constant?
            entry = tk.Entry(master=frame, width=50)
            entry.insert(tk.END, "")
            entry.pack()
        return frame
    
    def get_userinput_string(self, string):
        new_name = ''
        while new_name == '':
            new_name = simpledialog.askstring("User Input", string)
        return new_name
    
    
    def adding_cheatcode_to_menu(self, cheatcodename):
        self.select_cheatcode.set(cheatcodename)
        self.cheatcode_opt_menu["menu"].add_command(
                                                label=cheatcodename,
                                                command=tk._setit(
                                                                self.select_cheatcode,
                                                                cheatcodename,
                                                                callback=partial(lambda x: self.__update_cheatcode_entries_on_select())
                                                                )
                                                )

    def adding_game_to_menu(self, gamename):
        self.clear_gui()
        self.select_game_menu.set(gamename)
        self.opt_menu["menu"].add_command(
                                        label=gamename,
                                        command=tk._setit(
                                                        self.select_game_menu,
                                                        gamename,
                                                        callback=self.update_cheatcode_menu # TODO replace with self.handle_game_option_selection
                                                        )
                                        )

    def __update_cheatcode_entries_on_select(self):
        self.clear_gui()
        selected_game_name = self.select_game_menu.get()
        selected_cheat_code_name = self.select_cheatcode.get()

        if selected_cheat_code_name == self.add_cheatcode_option_string:
            # pop dialog up for new cheat code name   
            selected_cheat_code_name = self.get_userinput_string("Type in the name of your new cheatcode")
            # Adding new cheatcode option to option menu
            self.adding_cheatcode_to_menu(selected_cheat_code_name)
            addresses = []
            # Note: If the new entry is not directly added to the model, a KeyValue Exception will be thrown
            # add directly to the model                                            
            self.prepare_and_exec_callback(UserAction.MODIFY_DATA)
        else:
            cheat_codes = self.model_data[selected_game_name]
            addresses = cheat_codes[selected_cheat_code_name]
        self.insert_into_gui(
                            selected_game_name,
                            selected_cheat_code_name,
                            addresses
                            )

    def handle_game_option_selection(self, option):
        game_name = self.select_game_menu.get()
        if game_name == self.add_game_option_string:
            game_name = self.get_userinput_string("Type in the name of your new game")
            self.adding_game_to_menu(game_name)
            self.prepare_and_exec_callback(UserAction.ADD_NEW_GAME)
            self.select_game_menu.set(game_name)
        self.update_cheatcode_menu(option)

    def create_cheatcode_option_menu(self, master, row, column):
        variable = StringVar(master)
        # Get currently selected game
        game_name = self.select_game_menu.get()
    
        cheat_names = self.model_data[game_name]
        if not list(cheat_names):
            raise ValueError("No Cheatcode Data for GUI")
        first_cheatcode_name = list(cheat_names)[0]
        first_cheat_addresses = cheat_names[first_cheatcode_name]
        
        variable.set(first_cheatcode_name)
        names = []
        
        # Adding '--Add New--' Option
        names.append(self.add_cheatcode_option_string)
        for cheat in cheat_names:
            names.append( cheat )
        O = tk.OptionMenu(  self.root,
                            variable,
                            *names,
                            command=partial(lambda x: self.__update_cheatcode_entries_on_select())
                        )
        O.grid(row=row, column=column)

        return variable, O

    # updates menu respective to currently selected game
    def update_cheatcode_menu(self, option):
        # Update select_cheatcode for new game
        grid_info = self.cheatcode_opt_menu.grid_info() 
        self.cheatcode_opt_menu.destroy()
        self.select_cheatcode, self.cheatcode_opt_menu = self.create_cheatcode_option_menu(
                                                            master=self.root,
                                                            row=grid_info["row"],
                                                            column=grid_info["column"]
                                                            )
        self.__update_cheatcode_entries_on_select()
    
    def create_games_option_menu(self, row, column):
        variable = StringVar(self.root)
        gameCheats = self.model_data
        variable.set(list(gameCheats)[0])
        names = []
        # Adding a 'new game' option
        names.append(self.add_game_option_string)

        for game in gameCheats:
            names.append( game )
        O = tk.OptionMenu(  self.root,
                            variable,
                            *names,
                            command=self.handle_game_option_selection)
        O.grid(row=row, column=column)
        self.select_game_menu = variable
        self.opt_menu = 0
        self.select_cheatcode, self.cheatcode_opt_menu = self.create_cheatcode_option_menu(self.root, row=row+1, column=column)
        return variable, O

    def create_buttons(self, row, column):
        frame = tk.Frame(self.root)
        frame.grid(row=row, column=column)

        show_all = tk.Button(frame,
                        text="Modify",
                        width=10,
                        command=partial(self.prepare_and_exec_callback, UserAction.MODIFY_DATA) )
        show_all.pack(side=tk.TOP)
        show_all.config(font=("Courier", 22))

        end = tk.Button(frame, 
                        text="QUIT",
                        width=25, 
                        fg="red",
                        command=partial(self.prepare_and_exec_callback, UserAction.END_PROGRAM) )
        end.pack(side=tk.BOTTOM)

        ex = tk.Button(frame, 
                        text="EXPORT",
                        width=25, 
                        fg="blue",
                        command=partial(self.prepare_and_exec_callback, UserAction.EXPORT_ALL_DATA) )
        ex.pack(side=tk.BOTTOM)

    def init_for_interaction(self):
        self.root = tk.Tk()

        self.addresses_entries_frame = self.create_cheatcodes_frame(master=self.root, row=2, column=1)

        # TODO maybe instead of OptionMenu for the Games use ListBox?
        self.select_game_menu, self.opt_menu = self.create_games_option_menu(row=0, column=0)
        self.create_buttons(row=2, column=0)
        

    def interact(self):
        self.init_for_interaction()
        self.root.mainloop()

    # Error Message Pop up
    def error_msg_dialog(self):
        messagebox.showerror("ERROR", "An error occurred:\n" +
                            str(self.error) +
                            "\n\n" +
                            "Traceback\n" +
                            str(self.traceback) )

    # Adds confirmation dialog before every action
    def confirmation_dialog(self, useraction: UserAction, data):
        if self.TEST:
            return True
        return askyesno(title=str(useraction),
                        message="Do you want to perform action: \n\n" +
                                str(useraction) + "\n\n" + 
                                "With data: \n\n" +
                                str(data))

    def prepare_and_exec_callback(self, useraction : UserAction):
        self.state = useraction
        # Check if data is needed for the useraction
        if self.state in self.no_data_actions:
            data = None
        elif self.state == UserAction.ADD_NEW_GAME:
            # create empty cheatcode list for the new game
            game_name = self.select_game_menu.get()
            data = {game_name: {'(m)':[]} }
            self.callback( UserInput(UserAction.ADD_NEW_GAME, data) )
        else:
            data = self.get_userdata_input()
        if not self.confirmation_dialog(useraction, data):
            return
        try:
            self.callback( UserInput(useraction, data) )
        except Exception as e:
            self.traceback = traceback.format_exc()
            self.error = e
            self.state = UserAction.ERROR_MSG
            self.update_gui()
            return
        self.update_gui()

###|--HUMBLE-OBJECT--|###
    # TODO this should be outside of the humble object...
    # TODO This function assumes that the game already exists -> this must be assured
    def __merge_userinput_with_old_data(self, game_name, cheatcode_name, new_addresses):
        cheat_names = self.model_data[game_name]
        # Find changed cheat
        cheat_names[cheatcode_name] = new_addresses
        return cheat_names

    # This function should return a dict object, structured like this:
    # {String : {String : [HexStrings]}}
    # {GameName : { Cheat00: [addr1, addr2, ...], Cheat01 : [...], ...} }
    #
    # Note: this function should give back a whole games+cheatcodes
    def get_userdata_input(self):
        # Get game name from current OptionMenu Selection
        game_name = self.select_game_menu.get()
        cheatcodes = {}
        new_addresses = []

        # Note: Only the currently selected cheatcode and its addresses are pull from the GUI        
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
        return {"game_name" : game_name, "cheatcodes" :  cheatcode_name, "addresses" : addresses}

###^--HUMBLE-OBJECT--^### 

    def update_gui(self):
        mode = self.state
        gui_data = []

        if mode == UserAction.END_PROGRAM:
            self.root.quit()
        elif mode == UserAction.SHOW_ALL_DATA_FROM_AR:
            pass
        elif mode == UserAction.PRINT_GAME:
            for cheat in data.gameCheats:
                try:
                    print("Tk model.update_gui(): " + cheat.get_gameName())
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
            self.model_data = json.loads(self.model.get_games_as_json())
        elif mode == UserAction.ADD_NEW_GAME:
            self.model_data = json.loads(self.model.get_games_as_json())
            grid_info = self.opt_menu.grid_info()
            self.cheatcode_opt_menu.destroy()
            self.opt_menu.destroy()
            self.select_game_menu, self.opt_menu = self.create_games_option_menu(row=grid_info["row"], column=grid_info["column"])
        else:
            print("View says: No Such UserAction")
            raise ValueError
