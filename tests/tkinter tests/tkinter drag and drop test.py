import tkinter as tk
from TkinterDnD2 import *

def drop(event):
    entry_sv.set(event.data)

root = TkinterDnD.Tk()
entry_sv = tk.StringVar()
entry = tk.Entry(root, textvar=entry_sv, width=80)
entry.pack(fill=tk.X)
entry.drop_target_register(DND_FILES)
entry.dnd_bind('<<Drop>>', drop)
root.mainloop()