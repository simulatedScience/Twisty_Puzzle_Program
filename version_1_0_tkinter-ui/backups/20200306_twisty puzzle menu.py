import tkinter as tk
from PIL import Image, ImageTk
import os
import numpy as np

class twistyPuzzleMenu():
    def __init__(self):
        self.bgcolor = "#283035"
        self.primarycolor = "#40454e" # "#1d2326"
        self.primarytextcolor = "#dddddd"
        self.secondarycolor = "#60656e"
        self.secondarytextcolor = self.primarytextcolor
        self.highlightcolor = "#50555e"
        self.highlighttextcolor = self.primarytextcolor

        self.master = tk.Tk()
        self.master.title("twisty puzzle menu")
        self.master["bg"] = self.bgcolor
        self.master.minsize(450,500)

        self.largeButtonHeight = 80
        self.largeButtonWidth = 350

        self.largeImageSize = self.largeButtonHeight-10
        self.mediumImageSize = self.largeButtonHeight//2
        self.smallImageSize = 18

        self.headLineFontSize = "15"
        self.normalFontSize = "12"

        self.loadIcons()

        self.pointCoordPrecision = 3

        self.showToolTips = True
        self.activeWindow = "savedPuzzles"
        self.coordSystemAxis = {"cartesian":["x","y","z"], "cylindrical":["ρ","φ","h"], "spherical":["r","ϑ","φ"]}

        self.colors = ["#f00", "#f93", "#fd0", "#8f5", "#0d0", "#3f8", "#3ee", "#58f", "#35f", "#63f", "#a2f", "#f2d"]

        self.savedPuzzleWindow()


    def loadIcons(self):
        """
        loads Icons from "/Icons" folder
        """
        self.cross           = self.loadImage("cross.png",        size=(self.smallImageSize+10, self.smallImageSize+10))
        self.addIcon         = self.loadImage("add.png",          size=(self.mediumImageSize, self.mediumImageSize))
        self.smallAddIcon    = self.loadImage("add.png",          size=(self.smallImageSize,self.smallImageSize))
        self.saveIcon        = self.loadImage("save.png",         size=(self.mediumImageSize-10, self.mediumImageSize-10))
        self.smallSaveIcon   = self.loadImage("save.png",         size=(self.smallImageSize,self.smallImageSize))
        self.smallDeleteIcon = self.loadImage("delete.png",       size=(self.smallImageSize,self.smallImageSize))
        self.openFile        = self.loadImage("open_file.png",    size=(self.largeButtonHeight-20, self.largeButtonHeight-20))
        self.imageUpload     = self.loadImage("image upload.png", size=(self.mediumImageSize, self.mediumImageSize))
        self.defaultCube     = self.loadImage("default cube.png", size=(self.largeButtonHeight-10, self.largeButtonHeight-10))

        self.rightPlayIcon   = self.loadImage("playButton.png")
        self.leftPlayIcon    = self.loadImage("playButton.png", mirrored=True)
        self.pauseIcon       = self.loadImage("pauseButton.png")
        # self.rightArrow      = self.loadImage("right arrow.png")
        # self.leftArrow       = self.loadImage("right arrow.png", mirrored=True)

        self.cartesianCoords   = self.loadImage("cartesianCoords.png",   size=(self.smallImageSize+10,self.smallImageSize+10))
        self.cylindricalCoords = self.loadImage("cylindricalCoords.png", size=(self.smallImageSize+10,self.smallImageSize+10))
        self.sphericalCoords   = self.loadImage("sphericalCoords.png",   size=(self.smallImageSize+10,self.smallImageSize+10))


    def loadImage(self, imageName, folder="Icons/", fileFormat=".png", mirrored=False, size=None):
        """
        opens the image with the given name in the given folder/directory
        """
        if "." in imageName:
            if mirrored:
                image = Image.open(folder+"/"+imageName)
            else:
                image = Image.open(folder+"/"+imageName)
        else:
            if mirrored:
                image = Image.open(folder+"/"+imageName+fileFormat)
            else:
                image = Image.open(folder+"/"+imageName+fileFormat)
        if size!=None:
            image = image.resize(size)#, Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)


    def sizedButton(self, master, height=70, width=70, bg="#88ff55"):
        """
        creates a button of the given sive with the given master by creating a frame that's filled with the button.
        returns frame and button as they are not placed yet.
        """
        Frame = tk.Frame(master, 
                height = height,
                width = width,
                bg = bg)
        Frame.pack_propagate(0)
        button = tk.Button(Frame)
        self.addButtonStyle(button)

        return Frame, button

    def addButtonStyle(self, button, style = "secondary"):
        """
        adds styling to a button, including color change when hovered over with mouse.
        """
        if style == "primary":
            button.config(
                    bg = self.bgcolor,
                    fg = self.primarytextcolor,
                    activebackground = self.primarycolor,
                    activeforeground = self.primarytextcolor,
                    relief = "flat",
                    bd = 0,
                    cursor = "hand2"
                    )
        elif style == "secondary":
            button.config(
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    activebackground = self.secondarycolor,
                    activeforeground = self.secondarytextcolor,
                    relief = "flat",
                    bd = 0,
                    cursor = "hand2"
                    )
        button.bind("<Enter>", lambda _: self.on_enter(button, style = style))
        button.bind("<Leave>", lambda _: self.on_leave(button, style = style))
    
    def makeFrameToButton(self,frame):
        frame.config(
                bg = self.primarycolor,
                relief = "flat",
                bd = 0,
                cursor = "hand2"
                )
        frame.bind("<Enter>", lambda _: self.on_enter(frame, changeForeground=False), add="+")
        frame.bind("<Leave>", lambda _: self.on_leave(frame, changeForeground=False), add="+")

    def on_enter(self, widget, changeForeground=True, style = "secondary"):
        if style == "primary":
            bgColor = self.primarycolor
            fgColor = self.primarytextcolor
        elif style == "secondary":
            bgColor = self.highlightcolor
            fgColor = self.highlighttextcolor

        if changeForeground:
                widget.config(bg = bgColor,
                            fg = fgColor)
        else:
            widget.config(bg = bgColor)
        for child in widget.winfo_children():
            if type(child) == tk.Frame:
                self.on_enter(child, changeForeground=False, style = style)
            elif type(child) == tk.Toplevel:
                pass
            else:
                self.on_enter(child, style = style)

    def on_leave(self, widget, changeForeground=True, style = "secondary"):
        if style == "primary":
            bgColor = self.bgcolor
            fgColor = self.primarytextcolor
        elif style == "secondary":
            bgColor = self.primarycolor
            fgColor = self.primarytextcolor

        if changeForeground:
            widget.config(bg = bgColor,
                        fg = fgColor)
        else:
            widget.config(bg = bgColor)
        for child in widget.winfo_children():
            if type(child) == tk.Frame:
                self.on_leave(child, changeForeground=False, style = style)
            elif type(child) == tk.Toplevel:
                pass
            else:
                self.on_leave(child, style = style)


    def addLabelStyle(self, label, style="primary"):
        if style == "primary":
            label.config(
                    bg = self.bgcolor,
                    fg = self.primarytextcolor,
            )
        elif style == "primaryHeadline":
            label.config(
                    bg = self.bgcolor,
                    fg = self.primarytextcolor,
                    font = ("", self.headLineFontSize, "bold underline")
            )
        elif style == "secondary":
            label.config(
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    font = ("", self.normalFontSize, "")
            )
        elif style == "buttonHeadline":
            label.config(
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    font = ("", self.normalFontSize, "bold underline"),
            )

    def addEntryStyle(self, Entry, style="primary"):
        if style == "primaryHeadline":
            Entry.config(
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    selectforeground = self.highlighttextcolor,
                    selectbackground = self.highlightcolor,
                    insertbackground = self.primarytextcolor,
                    justify = "center",
                    relief = "flat",
                    font = ("", self.headLineFontSize,"bold underline")
            )
        elif style == "secondary":
            Entry.config(
                    bg = self.secondarycolor,
                    fg = self.secondarytextcolor,
                    selectforeground = self.highlighttextcolor,
                    selectbackground = self.highlightcolor,
                    insertbackground = self.primarytextcolor,
                    justify = "right",
                    relief = "flat"
            )

    def addCheckbuttonStyle(self, checkbutton, style = "secondary"):
        if style == "secondary":
            checkbutton.config(
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    activebackground = self.primarycolor,
                    activeforeground = self.primarytextcolor,
                    selectcolor = self.primarycolor,
                    relief = "flat",
                    bd = 0,
                    cursor = "hand2"
                    )


    def addToolTip(self,widget, text, bg="#ffffe0", fg="#000", justify="left", font=("", "10", ""), highlightcolor="#000"):
        if self.showToolTips:
            widget.bind('<Enter>', lambda _: self.showtip(widget, text, bg=bg, fg=fg, justify=justify, font=font, highlightcolor=highlightcolor), add="+")

    def showtip(self, widget, text, bg="#ffffe0", fg="#000", justify="left", font=("", "10", ""), highlightcolor="#000"):
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
        label.pack(ipadx = 3, ipady = 3)
        widget.bind('<Leave>', lambda _: tipwindow.destroy(), add="+")


    def getFolderContents(self,path=None):
        return os.listdir(path)


    def goToWindow(self, window, puzzle = None, algorithm = None):
        """
        creates the specified frame and deletes all unnecessary widgets of the previous frame.
        """
        # print("active:", self.activeWindow)
        if window != self.activeWindow: #may not be necessary unless this method is activated by a keyboard input
            for child in self.master.winfo_children():
                child.destroy()
            # print(window, puzzle, algorithm)
            if window == "savedPuzzles":
                self.activeWindow = "savedPuzzles"
                self.savedPuzzleWindow()
            elif window == "puzzleCreation":
                self.activeWindow = "puzzleCreation"
                self.puzzleCreationWindow()
            elif window == "showPuzzle":
                self.activeWindow = "showPuzzle"
                self.algorithmOverviewWindow(puzzle)
            elif window == "solvingStrategy":
                self.activeWindow = "solvingStrategy"
                self.solvingStrategyWindow()
            elif window == "showAlgorithm":
                self.activeWindow = "showAlgorithm"
                self.showAlgorithmWindow()
            elif window == "algorithmCreation":
                self.activeWindow = "algorithmCreation"
                self.algorithmCreationWindow(puzzle, algorithm)





    def savedPuzzleWindow(self):
        """
        creates a window showing all saved puzzles
        """
        self.savedPuzzleFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.savedPuzzleFrame.pack(fill="both", expand=True)

        savedPuzzleHeadline = tk.Label(self.savedPuzzleFrame, text="saved puzzles")
        self.addLabelStyle(savedPuzzleHeadline, style="primaryHeadline")
        savedPuzzleHeadline.grid(row = 0, column = 0, pady = 10, sticky="n")

        #checks if a "puzzles" folder exists, if not, create one.
        if not "puzzles" in self.getFolderContents():
            os.mkdir("puzzles")
        
        #loop through all puzzles in the puzzle folder
        for i,puzzleFolder in enumerate(self.getFolderContents("puzzles")):

            puzzleFolderContents = self.getFolderContents("puzzles/"+puzzleFolder)

            puzzleFrame = tk.Frame(self.savedPuzzleFrame, 
                    bg=self.primarycolor, 
                    height=self.largeButtonHeight, 
                    width=self.largeButtonWidth
                    )
            puzzleFrame.grid_propagate(0)
            puzzleFrame.grid(row = i+1, column = 0, padx = 5, pady = 5, sticky = "n")

            puzzleImageLabel = tk.Label(puzzleFrame)
            self.addLabelStyle(puzzleImageLabel, style="secondary")
            if not "icon.png" in puzzleFolderContents:
                puzzleImageLabel.config(image = self.defaultCube)
            else:
                puzzleImage = self.loadImage("icon",folder="puzzles/"+puzzleFolder)
                puzzleImageLabel.config(image = puzzleImage)
            puzzleImageLabel.grid(row = 0, column = 0, rowspan = 2, padx = 5, pady = 5, sticky = "w")

            puzzleNameLabel = tk.Label(puzzleFrame, text = puzzleFolder)
            self.addLabelStyle(puzzleNameLabel, style="buttonHeadline")
            puzzleNameLabel.grid(row = 0, column = 1, pady = 2, sticky="sw")

            puzzleAlgorithmLabel = tk.Label(puzzleFrame, text = 
                    "saved algorithms: {}".format(
                        len(puzzleFolderContents)-1
                        )
                    )
            self.addLabelStyle(puzzleAlgorithmLabel,style="secondary")
            puzzleAlgorithmLabel.grid(row = 1, column = 1, pady = 2, sticky="nw")

            puzzleFrame.grid_columnconfigure(1, weight = 1)

            frame, button = self.sizedButton(puzzleFrame)
            button.config(image = self.openFile, command = lambda puzzleName=puzzleFolder: self.goToWindow("showPuzzle", puzzle=puzzleName))
            frame.grid(row = 0, column = 3, rowspan = 2, padx = 5, pady = 5, sticky = "e")
            button.pack(fill="both", expand=True)


        puzzleAddFrame = tk.Frame(self.savedPuzzleFrame, bg = self.primarycolor)
        puzzleAddFrame.grid(row = i+2, column = 0, pady = 5, sticky = "n")

        puzzleAddImage = tk.Label(puzzleAddFrame, image=self.addIcon)
        self.addLabelStyle(puzzleAddImage,style="secondary")
        puzzleAddImage.grid(row = 0, column = 0, padx = (10,5), pady = 5, sticky = "w")

        puzzleAddLabel = tk.Label(puzzleAddFrame, text = "add puzzle")
        self.addLabelStyle(puzzleAddLabel, style="secondary")
        puzzleAddLabel.grid(row = 0, column = 1, padx = (5,10), sticky = "w")

        self.makeFrameToButton(puzzleAddFrame)
        puzzleAddFrame.bind("<Button-1>", func = lambda _: self.goToWindow("puzzleCreation"))
        for child in puzzleAddFrame.winfo_children():
            child.bind("<Button-1>", func = lambda _: self.goToWindow("puzzleCreation"))

        self.savedPuzzleFrame.grid_columnconfigure(0, weight = 1)
        self.savedPuzzleFrame.grid_propagate(0)
    
    
    # def on_click_puzzleAddButton(self):
    #     self.goToWindow("puzzleCreation")





    def puzzleCreationWindow(self):
        """
        creates a window allowing the user to create a new puzzle and it's legal moves
        """
        self.puzzleCreationFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.puzzleCreationFrame.pack(fill="both", expand=True)
        self.puzzleCreationFrame.grid_propagate(0)
        self.puzzleCreationFrame.grid_columnconfigure(1,weight=1)
        self.puzzleCreationFrame.grid_columnconfigure(0, minsize = self.largeButtonHeight)
        self.puzzleCreationFrame.grid_columnconfigure(2, minsize = self.largeButtonHeight)

        puzzleName = tk.StringVar(value="puzzle name")
        i = 1
        while puzzleName.get() in self.getFolderContents("puzzles"):
            puzzleName.set( "puzzle name #" + str(i) )
            i+=1

        puzzleCreationHeadline = tk.Entry(self.puzzleCreationFrame,
                textvariable = puzzleName)
        self.addEntryStyle(puzzleCreationHeadline, style="primaryHeadline")
        puzzleCreationHeadline.grid(row = 0, column = 1, sticky = "n", padx = 10, pady = 10)

        returnButton = tk.Button(self.puzzleCreationFrame, 
                image = self.cross, 
                command = lambda: self.goToWindow("savedPuzzles"))
        self.addButtonStyle(returnButton, style = "primary")
        returnButton.grid(row = 0, column = 2, sticky = "nw", padx = 10, pady = 10)

        uploadImageButton = tk.Button(self.puzzleCreationFrame,
                image = self.imageUpload)
        self.addButtonStyle(uploadImageButton, style = "primary")
        uploadImageButton.grid(row = 0, column = 0, sticky = "ne", padx = 10, pady = 10)


        puzzlePointsFrame = tk.Frame(self.puzzleCreationFrame, 
                bg = self.primarycolor, 
                width = self.largeButtonWidth, 
                height = 2*self.largeButtonHeight)
        puzzlePointsFrame.grid_columnconfigure(2, weight = 1)   #make column 2 fill all left over horizontal space
        puzzlePointsFrame.grid_rowconfigure(1, weight = 1)      #make row 1 fill all left over vertical space
        puzzlePointsFrame.grid_propagate(0)                     #prevent the frame from changing it's size to fit it's contents
        puzzlePointsFrame.grid(row = 1, column = 0, columnspan = 3, sticky = "n")

        addPointlabel = tk.Label(puzzlePointsFrame, text = "add point:")
        self.addLabelStyle(addPointlabel, style = "secondary")
        addPointlabel.grid(row = 0, column = 0, sticky = "w", padx = 5, pady = 5)

        addPointEntry = tk.Entry(puzzlePointsFrame, width = 3)
        self.addEntryStyle(addPointEntry, style="secondary")
        addPointEntry.grid(row = 0, column = 1, sticky = "w")

        addPointButton = tk.Button(puzzlePointsFrame, image = self.smallAddIcon)
        self.addButtonStyle(addPointButton)
        addPointButton.grid(row = 0, column = 2, sticky = "w")
        
        deletePointLabel = tk.Label(puzzlePointsFrame, text = "delete point:")
        self.addLabelStyle(deletePointLabel, style = "secondary")
        deletePointLabel.grid(row = 0, column = 3, sticky = "e")

        deletePointButton = tk.Button(puzzlePointsFrame, image = self.smallDeleteIcon)
        self.addButtonStyle(deletePointButton)
        deletePointButton.grid(row = 0, column = 4, sticky = "e", padx = 5, pady = 5)


        pointInfoFrame = tk.Frame(puzzlePointsFrame, bg = self.primarycolor)
        pointInfoFrame.grid(row = 1, column = 0, columnspan = 5, sticky = "n")

        self.activeCoordSystem = "cartesian"

        coordLabelList = []
        coordEntryVarList = []

        for i in range(3):
            coordLabel = tk.Label(pointInfoFrame, 
                    text = self.coordSystemAxis[self.activeCoordSystem][i]+":",
                    width = 2,
                    justify = "right",
                    anchor = "e")
            self.addLabelStyle(coordLabel, style="secondary")
            coordLabel.grid(row = 0, column = 2*i+1, sticky = "w")
            coordLabelList.append(coordLabel)

            coordEntryVar = tk.DoubleVar(value=1)
            coordEntryVarList.append(coordEntryVar)
            coordEntry = tk.Entry(pointInfoFrame, width = 6, textvariable = coordEntryVar)
            self.addEntryStyle(coordEntry, style="secondary")
            coordEntry.grid(row = 0, column = 2*i + 2, sticky = "e", padx = (1,15))
        
        coordSystemButton = tk.Button(pointInfoFrame)
        coordSystemButton.config(command = lambda button = coordSystemButton, labelList=coordLabelList, entryVarList=coordEntryVarList: self.changeCoordSystem(button, labelList, entryVarList), image = self.cartesianCoords)
        self.addButtonStyle(coordSystemButton)
        coordSystemButton.grid(row = 0, column = 0, padx = (0,10), pady = 10, sticky = "w")

        pointColorLabel = tk.Label(pointInfoFrame, text = "color:")
        self.addLabelStyle(pointColorLabel, style = "secondary")
        pointColorLabel.grid(row = 1, column = 0, columnspan = 2, sticky = "w")

        colorIndexVar = tk.IntVar(value = 6)

        pointColorDisplay = tk.Label(pointInfoFrame, 
                bg = self.colors[colorIndexVar.get()], 
                width = 6, 
                height = 1,
                cursor = "hand2")
        pointColorDisplay.grid(row = 1, column = 2, sticky = "w")

        pointColorDisplay.bind("<MouseWheel>", func = lambda event, tkVar = colorIndexVar: 
                self.scrollColorchange(pointColorDisplay, tkVar, event))
        pointColorDisplay.bind("<Button-1>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(pointColorDisplay, tkVar, -1))
        pointColorDisplay.bind("<Button-3>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(pointColorDisplay, tkVar, 1))

        self.addToolTip(pointColorDisplay, text = "scroll or click to change color", bg=self.bgcolor, fg=self.primarytextcolor)

        savePointLabel = tk.Label(puzzlePointsFrame, text = "save point:")
        self.addLabelStyle(savePointLabel, style="secondary")
        savePointLabel.grid(row = 2, column = 3, sticky = "e")

        savePointButton = tk.Button(puzzlePointsFrame, image = self.smallSaveIcon)
        self.addButtonStyle(savePointButton)
        savePointButton.grid(row = 2, column = 4, sticky = "e", padx = 5, pady = 5)


        puzzleMovesFrame = tk.Frame(self.puzzleCreationFrame, 
                bg = self.primarycolor,
                width = self.largeButtonWidth, 
                height = 2*self.largeButtonHeight)
        puzzleMovesFrame.grid_columnconfigure(2, weight = 1)   #make column 2 fill all left over horizontal space
        puzzleMovesFrame.grid_rowconfigure(1, weight = 1)      #make row 1 fill all left over vertical space
        puzzleMovesFrame.grid_propagate(0)                     #prevent the frame from changing it's size to fit it's contents
        puzzleMovesFrame.grid(row = 2, column = 0, columnspan = 3, sticky = "n", pady = 10)

        addMovelabel = tk.Label(puzzleMovesFrame, text = "add move:")
        self.addLabelStyle(addMovelabel, style = "secondary")
        addMovelabel.grid(row = 0, column = 0, sticky = "w", padx = 5, pady = 5)

        addMoveEntry = tk.Entry(puzzleMovesFrame, width = 3)
        self.addEntryStyle(addMoveEntry, style="secondary")
        addMoveEntry.grid(row = 0, column = 1, sticky = "w")

        addMoveButton = tk.Button(puzzleMovesFrame, image = self.smallAddIcon)
        self.addButtonStyle(addMoveButton)
        addMoveButton.grid(row = 0, column = 2, sticky = "w")
        
        deleteMoveLabel = tk.Label(puzzleMovesFrame, text = "delete move:")
        self.addLabelStyle(deleteMoveLabel, style = "secondary")
        deleteMoveLabel.grid(row = 0, column = 3, sticky = "e")

        deleteMoveButton = tk.Button(puzzleMovesFrame, image = self.smallDeleteIcon)
        self.addButtonStyle(deleteMoveButton)
        deleteMoveButton.grid(row = 0, column = 4, sticky = "e", padx = 5, pady = 5)


        moveInfoFrame = tk.Frame(puzzleMovesFrame,
                bg = self.primarycolor)
        moveInfoFrame.grid(row = 1, column = 0, columnspan = 5, sticky = "n")

        addCycleFrame = tk.Frame(moveInfoFrame, 
                bg = self.primarycolor)
        addCycleFrame.grid(row = 0, column = 0, columnspan = 5, sticky = "w")

        addCycleImage = tk.Label(addCycleFrame, image = self.smallAddIcon)
        self.addLabelStyle(addCycleImage, style="secondary")
        addCycleImage.grid(row = 0, column = 0, sticky = "w")

        addCycleLabel = tk.Label(addCycleFrame, text = "add cycle")
        self.addLabelStyle(addCycleLabel, style = "secondary")
        addCycleLabel.grid(row = 0, column = 1, sticky = "w")#, rowspan = 2)

        addCycleStateVar = tk.BooleanVar(value=True)
        self.toggleAddRemoveCycleInput(addCycleStateVar, addCycleFrame, moveInfoFrame)

        addCycleFrame.bind("<MouseWheel>", lambda _: self.toggleAddRemoveCycleInput(addCycleStateVar, addCycleFrame, moveInfoFrame))
        for child in addCycleFrame.winfo_children():
            child.bind("<MouseWheel>", lambda _: self.toggleAddRemoveCycleInput(addCycleStateVar, addCycleFrame, moveInfoFrame))

        self.addToolTip(addCycleFrame, text = "scroll to toggle between\nadd/ remove cycle", bg=self.bgcolor, fg=self.primarytextcolor)
        self.makeFrameToButton(addCycleFrame)

        self.addCycleInput(addCycleFrame, moveInfoFrame)

        showCycleCheckbutton = tk.Checkbutton(puzzleMovesFrame, text = "show cycles")
        self.addCheckbuttonStyle(showCycleCheckbutton)
        showCycleCheckbutton.grid(row = 2, column = 0, sticky = "w", columnspan = 3)

        showPointIndecesCheckbutton = tk.Checkbutton(puzzleMovesFrame, text = "show point indeces")
        self.addCheckbuttonStyle(showPointIndecesCheckbutton)
        showPointIndecesCheckbutton.grid(row = 3, column = 0, sticky = "w", columnspan = 3)


        horizontalSpacer = tk.Frame(puzzleMovesFrame, width = self.largeButtonWidth, bg = self.primarycolor)
        horizontalSpacer.grid_propagate(0)
        horizontalSpacer.grid(row = 4, column = 0, columnspan = 5, sticky = "n")

        saveMoveLabel = tk.Label(puzzleMovesFrame, text = "save move:")
        self.addLabelStyle(saveMoveLabel, style="secondary")
        saveMoveLabel.grid(row = 5, column = 3, sticky = "e")

        saveMoveButton = tk.Button(puzzleMovesFrame, image = self.smallSaveIcon)
        self.addButtonStyle(saveMoveButton)
        saveMoveButton.grid(row = 5, column = 4, sticky = "e", padx = 5, pady = 5)


        savePuzzleFrame = tk.Frame(self.puzzleCreationFrame)
        self.makeFrameToButton(savePuzzleFrame)
        savePuzzleFrame.bind("<Button-1>", func = lambda _: self.savePuzzle(savePuzzleFrame))
        for child in savePuzzleFrame.winfo_children():
            child.bind("<Button-1>", func = lambda _: self.savePuzzle(savePuzzleFrame))
        savePuzzleFrame.grid(row = 3, column = 1, sticky = "n")

        savePuzzleImage = tk.Label(savePuzzleFrame, image = self.saveIcon)
        self.addLabelStyle(savePuzzleImage, style="secondary")
        savePuzzleImage.grid(row = 0, column = 0, sticky = "w", padx = (10,5), pady = 5)

        savePuzzleLabel = tk.Label(savePuzzleFrame, text = "save puzzle")
        self.addLabelStyle(savePuzzleLabel, style = "secondary")
        savePuzzleLabel.grid(row = 0, column = 1, sticky = "w", padx = (5,10), pady = 5)



    def changeCoordSystem(self, button, coordLabels, coordEntryVars):
        if self.activeCoordSystem == "cartesian":
            self.activeCoordSystem = "cylindrical"
            a = round( np.sqrt( coordEntryVars[0].get()**2 + coordEntryVars[1].get()**2 ), self.pointCoordPrecision)
            b = round( np.arctan( coordEntryVars[1].get() / coordEntryVars[0].get() ), self.pointCoordPrecision)
            c = round( coordEntryVars[2].get(), self.pointCoordPrecision)
            button.config(image = self.cylindricalCoords)
        elif self.activeCoordSystem == "cylindrical":
            self.activeCoordSystem = "spherical"
            a = round( np.sqrt( coordEntryVars[0].get()**2 + coordEntryVars[2].get()**2 ), self.pointCoordPrecision)
            b = round( np.arctan( coordEntryVars[0].get() / coordEntryVars[2].get() ), self.pointCoordPrecision)
            c = round( coordEntryVars[1].get(), self.pointCoordPrecision)
            button.config(image = self.sphericalCoords)
        elif self.activeCoordSystem == "spherical":
            self.activeCoordSystem = "cartesian"
            a = round( coordEntryVars[0].get() * np.sin(coordEntryVars[1].get()) * np.cos(coordEntryVars[2].get()), self.pointCoordPrecision)
            b = round( coordEntryVars[0].get() * np.sin(coordEntryVars[1].get()) * np.sin(coordEntryVars[2].get()), self.pointCoordPrecision)
            c = round( coordEntryVars[0].get() * np.cos(coordEntryVars[1].get()), self.pointCoordPrecision)
            button.config(image = self.cartesianCoords)

        coordEntryVars[0].set(a)
        coordEntryVars[1].set(b)
        coordEntryVars[2].set(c)
        
        for i,label in enumerate(coordLabels):
            label.config(text = self.coordSystemAxis[self.activeCoordSystem][i]+":")


    def scrollColorchange(self, widget, colorIndexVar, event):
        if event.delta < 0:
            colorIndexVar.set( (colorIndexVar.get()+1) % len(self.colors) )
        elif event.delta > 0:
            colorIndexVar.set( (colorIndexVar.get()-1) % len(self.colors) )
        widget.config(bg = self.colors[colorIndexVar.get()])
    
    def clickColorchange(self, widget, colorIndexVar, change):
        if change < 0:
            colorIndexVar.set( (colorIndexVar.get()+1) % len(self.colors) )
        elif change > 0:
            colorIndexVar.set( (colorIndexVar.get()-1) % len(self.colors) )
        widget.config(bg = self.colors[colorIndexVar.get()])


    def addCycleInput(self, addCycleFrame, frame):
        maxColumn = addCycleFrame.grid_info()["column"]
        maxRow = addCycleFrame.grid_info()["row"]
        # print(maxRow, maxColumn)
        if maxColumn>=9:
            if maxRow==1:
                frame.master.grid_propagate(1)
            addCycleFrame.grid_configure(row = maxRow+1, column = 0)
        else:
            addCycleFrame.grid_configure(row = maxRow, column = maxColumn+3)

        leftBracketLabel = tk.Label(frame, width = 1, text = "(", anchor = "e", justify = "right")
        self.addLabelStyle(leftBracketLabel, style = "secondary")
        leftBracketLabel.grid(row = maxRow, column = maxColumn, sticky = "e")

        cycleEntry = tk.Entry(frame, width = 6)
        self.addEntryStyle(cycleEntry, style = "secondary")
        cycleEntry.grid(row = maxRow, column = maxColumn+1, sticky = "w")

        rightBracketLabel = tk.Label(frame, width = 1, text = ")", anchor = "w", justify = "left")
        self.addLabelStyle(rightBracketLabel, style = "secondary")
        rightBracketLabel.grid(row = maxRow, column = maxColumn+2, sticky = "w")


    def removeCycleInput(self, addCycleFrame, frame):
        maxColumn = addCycleFrame.grid_info()["column"]
        maxRow = addCycleFrame.grid_info()["row"]
        # print(maxRow, maxColumn)
        if maxColumn <= 3 and maxRow == 0:
            return
        if maxColumn<=2:
            if maxRow==3:
                frame.master.grid_propagate(False)
            for i in range(3):
                frame.grid_slaves(row = maxRow-1, column = 11-i)[0].grid_forget()
            addCycleFrame.grid_configure(row = maxRow-1, column = 9)
        else:
            for i in range(3):
                frame.grid_slaves(row = maxRow, column = maxColumn-i-1)[0].grid_forget()
            addCycleFrame.grid_configure(row = maxRow, column = maxColumn-3)

    def toggleAddRemoveCycleInput(self, tkStateVar, addCycleFrame, frame):
        # print(addCycleFrame.winfo_children())
        imageLabel, textLabel, *_= addCycleFrame.winfo_children()
        if tkStateVar.get()==True:
            tkStateVar.set(False)
            addCycleFrame.bind("<Button-1>", func = lambda _: self.addCycleInput(addCycleFrame, frame))
            for child in addCycleFrame.winfo_children():
                child.bind("<Button-1>", func = lambda _: self.addCycleInput(addCycleFrame, frame))
            textLabel.config(text = "add cycle")
            imageLabel.config(image=self.smallAddIcon)
        else:
            tkStateVar.set(True)
            addCycleFrame.bind("<Button-1>", func = lambda _: self.removeCycleInput(addCycleFrame, frame))
            for child in addCycleFrame.winfo_children():
                child.bind("<Button-1>", func = lambda _: self.removeCycleInput(addCycleFrame, frame))
            textLabel.config(text = "remove cycle")
            imageLabel.config(image=self.smallDeleteIcon)





    def algorithmOverviewWindow(self, puzzle):
        """
        creates a window showing all saved algorithms for the chosen puzzle
        """
        self.algorithmOverviewFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.algorithmOverviewFrame.pack(fill="both", expand=True)





    def solvingStrategyWindow(self):
        """
        creates a window allowing the user to create or edit a solving strategy guide for the chosen puzzle
        """
        self.solvingStrategyFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.solvingStrategyFrame.pack(fill="both", expand=True)





    def algorithmCreationWindow(self):
        """
        creates a window allowing the user to input and save a new algorithm for the chosen puzzle
        """
        self.algorithmCreationFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.algorithmCreationFrame.pack(fill="both", expand=True)





    def showAlgorithmWindow(self, puzzle, algorithm):
        """
        creates a window allowing the user to view a saved algorithms and apply it to the puzzle
        """
        self.showAlgorithmFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.showAlgorithmFrame.pack(fill="both", expand=True)

if __name__=="__main__":
    menu = twistyPuzzleMenu()
    tk.mainloop()
