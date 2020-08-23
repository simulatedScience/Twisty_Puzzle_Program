import tkinter as tk
import time

def on_enter(Frame):
    Frame.config(bg="#333366")
    for widget in Frame.winfo_children():
        widget.config(bg="#333366")
    print("entered")

def on_leave(Frame):
    Frame.config(bg="#333333")
    for widget in Frame.winfo_children():
        widget.config(bg="#333333")
    print("left")

def on_click(Frame):
    Frame.config(bg="#6666aa")
    for widget in Frame.winfo_children():
        widget.config(bg="#6666aa")
    print("clicked")


master = tk.Tk()

Frame=tk.Frame(master, bg="#333333", height = 50, width = 100, takefocus = True)
Frame.place(relx=0.5, rely=0.5, anchor="c")
Frame.pack_propagate(0)

Label = tk.Label(Frame, bg="#333333", fg="#dddddd", text="test")
Label.pack()

Frame.bind("<Enter>", lambda _: on_enter(Frame))
Frame.bind("<Leave>", lambda _: on_leave(Frame))
Frame.bind("<Button-1>", lambda _: on_click(Frame))
Frame.bind("<ButtonRelease-1>", lambda _: on_enter(Frame))
for widget in Frame.winfo_children():
    widget.bind("<Button-1>", lambda _: on_click(Frame))
    widget.bind("<ButtonRelease-1>", lambda _: on_enter(Frame))

print(Frame.winfo_children())

tk.mainloop()