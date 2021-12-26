import tkinter as tk

def createToolTip(widget, text):
    widget.bind('<Enter>', lambda _: showtip(widget, text))

def showtip(widget, text, bg="#ffffe0", fg="#000", justify="left", font=("", "10", ""), highlightcolor="#000"):
    x = widget.winfo_rootx() + widget.winfo_width()
    y = widget.winfo_rooty() + widget.winfo_height()

    tipwindow = tk.Toplevel(widget)
    tipwindow.wm_overrideredirect(True)
    tipwindow.wm_geometry(f"+{x}+{y}")

    label = tk.Label(tipwindow,
            text = text,
            background = bg,
            foreground = fg,
            borderwidth=1,
            highlightcolor = highlightcolor,
            relief = "solid",
            justify = justify,
            font = font
            )
    label.grid(row = 0, column = 0, sticky = "n")
    widget.bind('<Leave>', lambda _: tipwindow.destroy())


if __name__=="__main__":
    root = tk.Tk()
    frame = tk.Frame(root, width = 100, height = 70, bg = "#ffffe0")
    frame.place(x = 100, y = 50)

    createToolTip(frame, 
            text = "Hello World\n"
                    "This is how tip looks like. "
                    "Best part is, it's not a menu.\n"
                    "Purely tipbox.")

    tk.mainloop()