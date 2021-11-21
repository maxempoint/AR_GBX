import tkinter as tk
from tkinter.messagebox import askyesno




root = tk.Tk()
frame = tk.Frame(root)
frame.pack()

button = tk.Button(frame, 
                   text="QUIT", 
                   fg="red",
                   command=quit)
button.pack(side=tk.LEFT)

show_all = tk.Button(frame,
                   text="Scannen",
                   width=25,
                   command=scanning)
show_all.pack(side=tk.LEFT)
show_all.config(font=("Courier", 33))

slogan = tk.Button(frame,
                   text="Scannen mit Mail",
                   width=25,
                   command=scanningMitMailAnhang)
slogan.pack(side=tk.LEFT)
slogan.config(font=("Courier", 33))

root.mainloop()