import tkinter as tk
from tkinter import filedialog
import shutil
import os
from PIL import Image, ImageTk, ImageOps
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
        # self.master.deiconify()

        self.largeButtonHeight = 80
        self.largeButtonWidth = 350
        self.charsPerLine = 38
        # self.charWidth = 8
        # self.charsPerLine = self.largeButtonWidth//self.charWidth - 1 if self.largeButtonWidth % self.charWidth == 0 else self.largeButtonWidth//self.charWidth

        self.largeImageSize = self.largeButtonHeight-10
        self.mediumImageSize = self.largeButtonHeight//2
        self.smallImageSize = 18

        self.headLineFontSize = "15"
        self.normalFontSize = "12"

        self.loadIcons()
        self.puzzleImages = {}

        self.pointCoordPrecision = 3

        self.showToolTips = True
        self.activeWindow = "savedPuzzles"
        self.coordSystemAxis = {"cartesian":["x","y","z"], "cylindrical":["ρ","φ","h"], "spherical":["r","ϑ","φ"]}

        self.colors = ["#f00", "#f93", "#fd0", "#8f5", "#0d0", "#3f8", "#3ee", "#58f", "#35f", "#63f", "#a2f", "#f2d"]

        self.savedPuzzleWindow()


    def loadIcons(self):
        """
        loads Icons from "Icons" folder
        """
        self.cross           = self.loadImage("cross.png",        size = (self.smallImageSize+10, self.smallImageSize+10))
        self.addIcon         = self.loadImage("add.png",          size = (self.mediumImageSize-10, self.mediumImageSize-10))
        self.smallAddIcon    = self.loadImage("add.png",          size = (self.smallImageSize,self.smallImageSize))
        self.smallMinusIcon  = self.loadImage("substract.png",    size = (self.smallImageSize,self.smallImageSize))
        self.saveIcon        = self.loadImage("save.png",         size = (self.mediumImageSize-10, self.mediumImageSize-10))
        self.smallSaveIcon   = self.loadImage("save.png",         size = (self.smallImageSize, self.smallImageSize))
        self.smallDeleteIcon = self.loadImage("delete.png",       size = (self.smallImageSize, self.smallImageSize))
        self.smallEditIcon   = self.loadImage("editIcon.png",     size = (self.smallImageSize, self.smallImageSize))
        self.smallMenuBars   = self.loadImage("menuBars.png",     size = (self.smallImageSize, self.smallImageSize))
        self.openFile        = self.loadImage("open_file.png",    size = (self.largeButtonHeight-20, self.largeButtonHeight-20))
        self.smallLoadIcon   = self.loadImage("open_file.png",    size = (self.smallImageSize, self.smallImageSize))
        self.imageUpload     = self.loadImage("image upload.png", size = (self.mediumImageSize, self.mediumImageSize))
        self.defaultCube     = self.loadImage("default cube.png", size = (self.largeImageSize, self.largeImageSize))

        # self.rightArrow      = self.loadImage("right arrow.png")
        # self.leftArrow       = self.loadImage("right arrow.png", mirrored=True)

        self.cartesianCoords   = self.loadImage("cartesianCoords.png",   size = (self.smallImageSize+10,self.smallImageSize+10))
        self.cylindricalCoords = self.loadImage("cylindricalCoords.png", size = (self.smallImageSize+10,self.smallImageSize+10))
        self.sphericalCoords   = self.loadImage("sphericalCoords.png",   size = (self.smallImageSize+10,self.smallImageSize+10))

        self.smallReloadIcon      = self.loadImage("reloadArrow.png",  size = (self.smallImageSize, self.smallImageSize))
        self.reloadIcon      = self.loadImage("reloadArrow.png",  size = (self.smallImageSize+10, self.smallImageSize+10))
        self.rightPlayIcon   = self.loadImage("playButton.png",   size = (self.smallImageSize+10, self.smallImageSize+10))
        self.leftPlayIcon    = self.loadImage("playButton.png",   size = (self.smallImageSize+10, self.smallImageSize+10), mirrored=True)
        self.doubleLeftPlayIcon = self.loadImage("doublePlayButton.png", size = (self.smallImageSize+10, self.smallImageSize+10), mirrored=True)
        self.pauseIcon       = self.loadImage("pauseButton.png",  size = (self.smallImageSize+10, self.smallImageSize+10))


    def loadImage(self, imageName, folder="icons", fileFormat=".png", mirrored=False, size=None):
        """
        opens the image with the given name in the given folder/directory
        """
        if "." in imageName:
            if mirrored == True:
                image = ImageOps.mirror( Image.open(folder+"/"+imageName) )
            else:
                image = Image.open(folder+"/"+imageName)
        else:
            if mirrored == True:
                image = ImageOps.mirror( Image.open(folder+"/"+imageName+fileFormat) )
            else:
                image = Image.open(folder+"/"+imageName+fileFormat)
        if size!=None:
            image = image.resize(size)#, Image.ANTIALIAS)
        return ImageTk.PhotoImage(image)


    def sizedButton(self, master, height=None, width=None, bg="#88ff55", style = "secondary"):
        """
        creates a button of the given sive with the given master by creating a frame that's filled with the button.
        returns frame and button as they are not placed yet.
        """
        if height == None:
            height = self.largeButtonHeight-10
        if width == None:
            width = self.largeButtonHeight-10
        Frame = tk.Frame(master, 
                height = height,
                width = width,
                bg = bg)
        Frame.pack_propagate(0)
        button = tk.Button(Frame)
        self.addButtonStyle(button, style = style)

        return Frame, button


    def generateSpacer(self, master, bg = "#f0f", width = "350"):
        horizontalSpacer = tk.Frame(master, 
                bg = bg,
                width = width,
                height = 1)
        horizontalSpacer.grid_propagate(False)
        horizontalSpacer.pack_propagate(False)
        return horizontalSpacer

    def sizedTextField(self, master, minheight = 2, style = "primary"):
        """
        generates a tkinter text widget with the given minimum height and master which automatically increases in height to fit it's text
        returns the text widget
        the text widget must be packed/grided to fill it's parent in horizontal direction
        """
        if style == "primary":
            textBox = tk.Text(master,
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    selectbackground = self.highlightcolor,
                    selectforeground = self.highlighttextcolor,
                    insertbackground = self.primarytextcolor,
                    relief = "flat",
                    width = 1,
                    height = minheight,
                    font = ("",self.normalFontSize,""))
        textBox.bind("<Any-KeyPress>", lambda _, textBox = textBox: self.__updateTextBox(textBox, minheight))
        textBox.bind("<Any-KeyRelease>", lambda _, textBox = textBox: self.__updateTextBox(textBox, minheight))

        return textBox

    def __updateTextBox(self, textBox, minheight):
        """
        updates the height of a given text widget based on it's contents
        """
        textBoxContents = textBox.get("1.0","end").splitlines()
        lineCount = len(textBoxContents)
        for line in textBoxContents:
            lineCount += len(line)//self.charsPerLine
        # print(f"linecount = {lineCount}")
        if lineCount>=minheight and lineCount != textBox.cget("height"):
            textBox.config(height = lineCount)


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
        button.bind("<Enter>", lambda _: self.__on_enter(button, style = style))
        button.bind("<Leave>", lambda _: self.__on_leave(button, style = style))


    def makeFrameToButton(self,frame):
        """
        adds highlighting to a frame and all it's children when hovered over with mouse
        """
        frame.config(
                bg = self.primarycolor,
                relief = "flat",
                bd = 0,
                cursor = "hand2"
                )
        frame.bind("<Enter>", lambda _: self.__on_enter(frame, changeForeground=False), add="+")
        frame.bind("<Leave>", lambda _: self.__on_leave(frame, changeForeground=False), add="+")


    def __on_enter(self, widget, changeForeground=True, style = "secondary"):
        """
        changes the color of the given widget when hovered over with mouse
        """
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
                self.__on_enter(child, changeForeground=False, style = style)
            elif type(child) == tk.Toplevel:
                pass
            else:
                self.__on_enter(child, style = style)

    def __on_leave(self, widget, changeForeground=True, style = "secondary"):
        """
        changes the color of the given widget when mouse leaves the widget
        """
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
                self.__on_leave(child, changeForeground=False, style = style)
            elif type(child) == tk.Toplevel:
                pass
            else:
                self.__on_leave(child, style = style)


    def addLabelStyle(self, label, style="primary"):
        """
        adds styling to a given label.
        availiable styles: 'primary', 'primaryHeadline', 'secondary', 'secondaryHeadline'
        """
        if style == "primary":
            label.config(
                    bg = self.bgcolor,
                    fg = self.primarytextcolor,
                    font = ("", self.normalFontSize, "")
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
        elif style == "secondaryHeadline":
            label.config(
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    font = ("", self.normalFontSize, "bold underline"),
            )


    def addEntryStyle(self, Entry, style = "primary", justify = None):
        """
        adds styling to a given Entry.
        availiable styles: 'primary', 'primaryHeadline', 'secondary'
        """
        if style == "primary":
            if justify == None:
                justify = "right"
            Entry.config(
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    selectforeground = self.highlighttextcolor,
                    selectbackground = self.highlightcolor,
                    insertbackground = self.primarytextcolor,
                    justify = justify,
                    relief = "flat",
                    font = ("", self.normalFontSize,"")
            )
        elif style == "primaryHeadline":
            if justify == None:
                justify = "center"
            Entry.config(
                    bg = self.primarycolor,
                    fg = self.primarytextcolor,
                    selectforeground = self.highlighttextcolor,
                    selectbackground = self.highlightcolor,
                    insertbackground = self.primarytextcolor,
                    justify = justify,
                    relief = "flat",
                    font = ("", self.headLineFontSize,"bold underline")
            )
        elif style == "secondary":
            if justify == None:
                justify = "right"
            Entry.config(
                    bg = self.secondarycolor,
                    fg = self.secondarytextcolor,
                    selectforeground = self.highlighttextcolor,
                    selectbackground = self.highlightcolor,
                    insertbackground = self.primarytextcolor,
                    justify = justify,
                    relief = "flat"
            )


    def addCheckbuttonStyle(self, checkbutton, style = "secondary"):
        """
        adds styling to a given checkbutton.
        availiable styles: 'secondary'
        """
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
        """
        adds a tooltip to the given widget showing the given text. This tooltip shows whenever hovered over with mouse.
        styling of the tooltip is according to the keyword arguments.

        """
        if self.showToolTips:
            widget.bind('<Enter>', lambda _: self.__showtip(widget, text, bg=bg, fg=fg, justify=justify, font=font, highlightcolor=highlightcolor), add="+")


    def __showtip(self, widget, text, bg="#ffffe0", fg="#000", justify="left", font=("", "10", ""), highlightcolor="#000"):
        """
        adding the tooltip
        """
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
        """
        returns contents of the folder with the specified path
        """
        # try:
        return os.listdir(path)
        # except NotADirectoryError:
        #     return []


    def goToWindow(self, window, puzzle = "new", algorithm = "new"):
        """
        creates the specified frame and deletes all (unnecessary) widgets of the previous frame.
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
                self.puzzleCreationWindow(puzzle)
            elif window == "algorithmOverview":
                self.activeWindow = "algorithmOverview"
                self.algorithmOverviewWindow(puzzle)
            elif window == "solvingStrategy":
                self.activeWindow = "solvingStrategy"
                self.solvingStrategyWindow(puzzle)
            elif window == "showAlgorithm":
                self.activeWindow = "showAlgorithm"
                self.showAlgorithmWindow(puzzle, algorithm)
            elif window == "algorithmCreation":
                self.activeWindow = "algorithmCreation"
                self.algorithmCreationWindow(puzzle)





    def savedPuzzleWindow(self):
        """
        creates a window showing all saved puzzles
        """
        self.activePuzzleInfos = {"points":dict(), "moves":dict(), "imagePath":str(), "image":None, "colors":list()}
        # points    is a list of dictionaries: i.e.: [ {"index":0, "coords": (1.0,0.0,0.0), "colorIndex":4}, ...]
        # moves     is a list of lists: i.e.: [ ["r", [(0,1,2,3), (4,5,6,7), ...]], ...]
        # imagePath is a string: i.e.: "D:/Freizeit/Mathematik/twisty puzzle analysis/images/geared-mixup.png"
        # image     is a tk-Photoimage object ready to be displayed in any widget
        # colors    is a list of all colors availiable in the current puzzle

        self.savedPuzzleFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.savedPuzzleFrame.pack(fill="both", expand=True)

        savedPuzzleHeadline = tk.Label(self.savedPuzzleFrame, text="saved puzzles")
        self.addLabelStyle(savedPuzzleHeadline, style="primaryHeadline")
        savedPuzzleHeadline.grid(row = 0, column = 0, pady = 10, sticky="ns")

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
                self.puzzleImages[puzzleFolder] = self.loadImage("icon.png",folder="puzzles/"+puzzleFolder, size=(self.largeImageSize, self.largeImageSize))
                puzzleImageLabel.config(image = self.puzzleImages[puzzleFolder])
            puzzleImageLabel.grid(row = 0, column = 0, rowspan = 2, padx = 5, pady = 5, sticky = "w")

            puzzleNameLabel = tk.Label(puzzleFrame, text = puzzleFolder)
            self.addLabelStyle(puzzleNameLabel, style="secondaryHeadline")
            puzzleNameLabel.grid(row = 0, column = 1, pady = 2, sticky="sw")

            if "algorithms" in self.getFolderContents("puzzles/" + puzzleFolder):
                savedAlgorithms = len( self.getFolderContents("puzzles/" + puzzleFolder + "/algorithms") )
            else:
                savedAlgorithms = 0

            puzzleAlgorithmLabel = tk.Label(puzzleFrame, text = 
                    f"saved algorithms: {savedAlgorithms}"
                    )
            self.addLabelStyle(puzzleAlgorithmLabel,style="secondary")
            puzzleAlgorithmLabel.grid(row = 1, column = 1, pady = 2, sticky="nw")

            puzzleFrame.grid_columnconfigure(1, weight = 1)

            frame, button = self.sizedButton(puzzleFrame)
            frame.grid(row = 0, column = 3, rowspan = 2, padx = 5, pady = 5, sticky = "e")
            button.config(image = self.openFile, command = lambda puzzleName=puzzleFolder: self.goToWindow("algorithmOverview", puzzle=puzzleName))
            button.pack(fill="both", expand=True)

            puzzleEditFrame, puzzleEditButton = self.sizedButton(puzzleFrame, height = self.largeButtonHeight//2, width = self.largeButtonHeight//2)
            puzzleEditFrame.grid(row = 0, column = 4, sticky = "ne")
            puzzleEditButton.config(image = self.smallEditIcon, command = lambda puzzleName = puzzleFolder: self.goToWindow("puzzleCreation", puzzleName))
            puzzleEditButton.pack(fill="both", expand=True)

            puzzleDeleteFrame, puzzleDeleteButton = self.sizedButton(puzzleFrame, height = self.largeButtonHeight//2, width = self.largeButtonHeight//2)
            puzzleDeleteFrame.grid(row = 1, column = 4, sticky = "se")
            puzzleDeleteButton.config(image = self.smallDeleteIcon, command = lambda puzzleName = puzzleFolder, frame = puzzleFrame: self.deletePuzzle(puzzleName, frame))
            puzzleDeleteButton.pack(fill="both", expand=True)


        puzzleAddFrame = tk.Frame(self.savedPuzzleFrame, bg = self.primarycolor)
        puzzleAddFrame.grid(row = i+2, column = 0, pady = 5, sticky = "n")

        puzzleAddImage = tk.Label(puzzleAddFrame, image=self.addIcon)
        self.addLabelStyle(puzzleAddImage,style="secondary")
        puzzleAddImage.grid(row = 0, column = 0, padx = (10,5), pady = 5, sticky = "w")

        puzzleAddLabel = tk.Label(puzzleAddFrame, text = "add puzzle")
        self.addLabelStyle(puzzleAddLabel, style="secondary")
        puzzleAddLabel.grid(row = 0, column = 1, padx = (5,10), sticky = "w")

        self.makeFrameToButton(puzzleAddFrame)
        puzzleAddFrame.bind( "<Button-1>", func = lambda _: self.goToWindow("puzzleCreation", puzzle="new") )
        for child in puzzleAddFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.goToWindow("puzzleCreation", puzzle="new") )

        self.savedPuzzleFrame.grid_columnconfigure(0, weight = 1)
        self.savedPuzzleFrame.grid_propagate(0)
    
    
    def deletePuzzle(self, puzzleName, frame):
        """
        deletes the folder with the given puzzle Name from the "puzzles" folder
        """
        shutil.rmtree("puzzles/" + puzzleName)
        frame.destroy()





    def puzzleCreationWindow(self, puzzle = "new"):
        """
        creates a window allowing the user to create a new puzzle and it's legal moves as well as save all of it
        """
        coordEntryVarList = []
        colorIndexVar = tk.IntVar(value = 4)
        if puzzle != "new":
            #load puzzle from file
            self.loadPuzzleInfos(puzzle)

        self.puzzleCreationFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.puzzleCreationFrame.pack(fill="both", expand=True)
        self.puzzleCreationFrame.grid_propagate(0)
        self.puzzleCreationFrame.grid_columnconfigure(1,weight=1)
        self.puzzleCreationFrame.grid_columnconfigure(0, minsize = self.largeButtonHeight)
        self.puzzleCreationFrame.grid_columnconfigure(2, minsize = self.largeButtonHeight)
        

        puzzleName = tk.StringVar(value="puzzle name")
        if puzzle == "new":
            i = 1
            while puzzleName.get() in self.getFolderContents("puzzles"):
                puzzleName.set( "puzzle name #" + str(i) )
                i+=1
        else:
            puzzleName.set(puzzle)

        puzzleCreationHeadline = tk.Entry(self.puzzleCreationFrame,
                textvariable = puzzleName)
        self.addEntryStyle(puzzleCreationHeadline, style="primaryHeadline")
        puzzleCreationHeadline.grid(row = 0, column = 1, sticky = "n", padx = 10, pady = 10)

        returnButton = tk.Button(self.puzzleCreationFrame, 
                image = self.cross, 
                command = lambda: self.goToWindow("savedPuzzles"))
        self.addButtonStyle(returnButton, style = "primary")
        returnButton.grid(row = 0, column = 2, sticky = "ne", padx = 10, pady = 10)

        if puzzle != "new" and self.activePuzzleInfos["image"] != None:
            image = self.activePuzzleInfos["image"]
        else:
            image = self.imageUpload

        uploadImageButton = tk.Button(self.puzzleCreationFrame,
                image = image)
        uploadImageButton.config(command = lambda: self.fileDialog(uploadImageButton))
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

        pointIndexVar = tk.IntVar(value = 0)

        addPointEntry = tk.Entry(puzzlePointsFrame, 
                width = 3, 
                textvariable = pointIndexVar)
        pointIndexVar.trace("w", lambda *_: self.loadPoint(pointIndexVar, coordEntryVarList, colorIndexVar))
        self.addEntryStyle(addPointEntry, style="secondary")
        addPointEntry.grid(row = 0, column = 1, sticky = "w")

        addPointButton = tk.Button(puzzlePointsFrame, 
                image = self.smallAddIcon, 
                command = lambda: self.addPoint(pointIndexVar))
        self.addButtonStyle(addPointButton)
        addPointButton.grid(row = 0, column = 2, sticky = "w", padx = 2)
        
        deletePointLabel = tk.Label(puzzlePointsFrame, text = "delete point:")
        self.addLabelStyle(deletePointLabel, style = "secondary")
        deletePointLabel.grid(row = 0, column = 3, sticky = "e")

        deletePointButton = tk.Button(puzzlePointsFrame, image = self.smallDeleteIcon)
        self.addButtonStyle(deletePointButton)
        deletePointButton.grid(row = 0, column = 4, sticky = "e", padx = 5, pady = 5)


        pointInfoFrame = tk.Frame(puzzlePointsFrame, bg = self.primarycolor)
        pointInfoFrame.grid(row = 1, column = 0, columnspan = 5, sticky = "n")

        self.activeCoordSystem = "cartesian"

        coordSystemButton = tk.Button(pointInfoFrame)
        coordLabelList = []

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
        
        coordSystemButton.config(command = lambda button = coordSystemButton, labelList=coordLabelList, entryVarList=coordEntryVarList: self.changeCoordSystem(button, labelList, entryVarList), image = self.cartesianCoords)
        self.addButtonStyle(coordSystemButton)
        coordSystemButton.grid(row = 0, column = 0, padx = (0,10), pady = 10, sticky = "w")

        pointColorLabel = tk.Label(pointInfoFrame, text = "color:")
        self.addLabelStyle(pointColorLabel, style = "secondary")
        pointColorLabel.grid(row = 1, column = 0, columnspan = 2, sticky = "w")


        pointColorDisplay = tk.Label(pointInfoFrame, 
                bg = self.colors[colorIndexVar.get()], 
                width = 6, 
                height = 1,
                cursor = "hand2",
                takefocus = True)
        pointColorDisplay.grid(row = 1, column = 2, sticky = "w")

        pointColorDisplay.bind( "<MouseWheel>", func = lambda event, tkVar = colorIndexVar: 
                self.scrollColorchange(tkVar, event) )
        pointColorDisplay.bind( "<Button-1>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(tkVar, -1) )
        pointColorDisplay.bind( "<Button-3>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(tkVar, 1) )
        pointColorDisplay.bind( "<Down>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(tkVar, -1) )
        pointColorDisplay.bind( "<Up>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(tkVar, 1) )
        colorIndexVar.trace("w", lambda *_: self.changeColor(pointColorDisplay, colorIndexVar))

        self.addToolTip(pointColorDisplay, text = "scroll or click to change color", bg=self.bgcolor, fg=self.primarytextcolor)

        savePointFrame = tk.Frame(puzzlePointsFrame, bg = self.primarycolor)
        savePointFrame.grid(row = 2, column = 3, columnspan = 2, sticky = "e")

        savePointLabel = tk.Label(savePointFrame, text = "save point:")
        self.addLabelStyle(savePointLabel, style="secondary")
        savePointLabel.grid(row = 0, column = 0, sticky = "e", padx = (5,0), pady = 5)

        savePointImage = tk.Label(savePointFrame, image = self.smallSaveIcon)
        self.addLabelStyle(savePointImage, style = "secondary")
        savePointImage.grid(row = 0, column = 1, sticky = "e", padx = 5, pady = 5)

        self.makeFrameToButton(savePointFrame)

        savePointFrame.bind("<Button-1>", lambda _: self.savePoint(pointIndexVar, coordEntryVarList, colorIndexVar))
        for child in savePointFrame.winfo_children():
            child.bind( "<Button-1>", lambda _: self.savePoint(pointIndexVar, coordEntryVarList, colorIndexVar) )


        self.cycleEntryList = list()

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

        moveNameVar = tk.StringVar(value = "f")

        addMoveEntry = tk.Entry(puzzleMovesFrame, width = 3, textvariable = moveNameVar)
        self.addEntryStyle(addMoveEntry, style="secondary")
        addMoveEntry.grid(row = 0, column = 1, sticky = "w")

        addMoveButton = tk.Button(puzzleMovesFrame, image = self.smallAddIcon)
        self.addButtonStyle(addMoveButton)
        addMoveButton.grid(row = 0, column = 2, sticky = "w", padx = 2)
        
        deleteMoveLabel = tk.Label(puzzleMovesFrame, text = "delete move:")
        self.addLabelStyle(deleteMoveLabel, style = "secondary")
        deleteMoveLabel.grid(row = 0, column = 3, sticky = "e")

        deleteMoveButton = tk.Button(puzzleMovesFrame, image = self.smallDeleteIcon)
        self.addButtonStyle(deleteMoveButton)
        deleteMoveButton.grid(row = 0, column = 4, sticky = "e", padx = 5, pady = 5)


        moveInfoFrame = tk.Frame(puzzleMovesFrame,
                bg = self.primarycolor)
        moveInfoFrame.grid(row = 1, column = 0, columnspan = 5, sticky = "n")
        moveInfoFrame.grid_columnconfigure(11, weight = 1)

        addMoveButton.config(command = lambda: self.addMove(moveNameVar, moveInfoFrame))

        pointInfoFrame.update()
        horizontalSpacer = self.generateSpacer(moveInfoFrame, width = pointInfoFrame.winfo_width(), bg = self.primarycolor)
        horizontalSpacer.grid(row = 0, column = 0, columnspan = 12, sticky = "n")

        addCycleFrame = tk.Frame(moveInfoFrame, 
                bg = self.primarycolor)
        addCycleFrame.grid(row = 1, column = 0, columnspan = 6, sticky = "w")

        addCycleImage = tk.Label(addCycleFrame, image = self.smallAddIcon)
        self.addLabelStyle(addCycleImage, style="secondary")
        addCycleImage.grid(row = 1, column = 0, sticky = "w")

        addCycleLabel = tk.Label(addCycleFrame, text = "add cycle")
        self.addLabelStyle(addCycleLabel, style = "secondary")
        addCycleLabel.grid(row = 1, column = 1, sticky = "w")

        self.makeFrameToButton(addCycleFrame)

        addCycleFrame.bind( "<Button-1>", func = lambda _: self.addCycleInput(moveInfoFrame) )
        for child in addCycleFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.addCycleInput(moveInfoFrame) )

        removeCycleFrame = tk.Frame(moveInfoFrame, 
                bg = self.primarycolor)
        removeCycleFrame.grid(row = 1, column = 6, columnspan = 6, sticky = "e")

        removeCycleImage = tk.Label(removeCycleFrame, image = self.smallMinusIcon)
        self.addLabelStyle(removeCycleImage, style="secondary")
        removeCycleImage.grid(row = 1, column = 0, sticky = "e")

        removeCycleLabel = tk.Label(removeCycleFrame, text = "remove cycle")
        self.addLabelStyle(removeCycleLabel, style = "secondary")
        removeCycleLabel.grid(row = 1, column = 1, sticky = "e")

        self.makeFrameToButton(removeCycleFrame)

        removeCycleFrame.bind( "<Button-1>", func = lambda _: self.removeCycleInput(moveInfoFrame) )
        for child in removeCycleFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.removeCycleInput(moveInfoFrame) )


        self.addCycleInput(moveInfoFrame)

        #TODO: make better designed custom checkbuttons
        showCycleCheckbutton = tk.Checkbutton(puzzleMovesFrame, text = "show cycles")
        self.addCheckbuttonStyle(showCycleCheckbutton)
        showCycleCheckbutton.grid(row = 2, column = 0, sticky = "w", columnspan = 3)

        #TODO: make better designed custom checkbuttons
        showPointIndecesCheckbutton = tk.Checkbutton(puzzleMovesFrame, text = "show point indeces")
        self.addCheckbuttonStyle(showPointIndecesCheckbutton)
        showPointIndecesCheckbutton.grid(row = 3, column = 0, sticky = "w", columnspan = 3)


        horizontalSpacer2 = self.generateSpacer(puzzleMovesFrame, width = self.largeButtonWidth, bg = self.primarycolor)
        horizontalSpacer2.grid(row = 4, column = 0, columnspan = 5, sticky = "n")

        saveMoveFrame = tk.Frame(puzzleMovesFrame, bg = self.primarycolor)
        saveMoveFrame.grid(row = 5, column = 3, columnspan = 2, sticky = "e")

        saveMoveLabel = tk.Label(saveMoveFrame, text = "save move:")
        self.addLabelStyle(saveMoveLabel, style="secondary")
        saveMoveLabel.grid(row = 0, column = 0, sticky = "e", padx = (5,0), pady = 5)

        saveMoveImage = tk.Label(saveMoveFrame, image = self.smallSaveIcon)
        self.addLabelStyle(saveMoveImage, style = "secondary")
        saveMoveImage.grid(row = 0, column = 1, sticky = "e", padx = 5, pady = 5)

        self.makeFrameToButton(saveMoveFrame)

        saveMoveFrame.bind("<Button-1>", lambda _: self.saveMove(moveNameVar))
        for child in saveMoveFrame.winfo_children():
            child.bind( "<Button-1>", lambda _: self.saveMove(moveNameVar) )

        moveNameVar.trace("w", lambda *_: self.loadMove(moveNameVar, moveInfoFrame))

        savePuzzleFrame = tk.Frame(self.puzzleCreationFrame)
        self.makeFrameToButton(savePuzzleFrame)
        savePuzzleFrame.grid(row = 3, column = 1, sticky = "n")

        savePuzzleImage = tk.Label(savePuzzleFrame, image = self.saveIcon)
        self.addLabelStyle(savePuzzleImage, style="secondary")
        savePuzzleImage.grid(row = 0, column = 0, sticky = "w", padx = (10,5), pady = 5)

        savePuzzleLabel = tk.Label(savePuzzleFrame, text = "save puzzle")
        self.addLabelStyle(savePuzzleLabel, style = "secondary")
        savePuzzleLabel.grid(row = 0, column = 1, sticky = "w", padx = (5,10), pady = 5)
        
        savePuzzleFrame.bind( "<Button-1>", func = lambda _: self.savePuzzle(puzzleName.get(), puzzle = puzzle) )
        for child in savePuzzleFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.savePuzzle(puzzleName.get(), puzzle = puzzle) )
        
        savePuzzleFrame.bind("<Control-s>", func = lambda *_: self.savePuzzle(puzzleName.get(), puzzle = puzzle))
        for child in self.puzzleCreationFrame.winfo_children():
            child.bind("<Control-s>", func = lambda *_: self.savePuzzle(puzzleName.get(), puzzle = puzzle))


    def fileDialog(self, imageLabel):
        """
        opens the file explorer to let the user select an image.
        shows the chosen image in the given imageLabel
        saves the filepath in self.activePuzzleInfos
        """
        filePath = filedialog.askopenfilename(
                title = "select a puzzle image",
                initialdir =  "/",
                filetype = (("png files","*.png"), ("jpg files","*.jpg"), ("jpeg files","*.jpeg") )
                )
        self.activePuzzleInfos["imagePath"] = filePath
        fileName = ""
        i = 1
        while filePath[-i] != "/":
            fileName = filePath[-i] + fileName
            i+=1
        filePath = filePath[:-len(fileName)-1]
        print(fileName)
        print(filePath)
        self.activePuzzleInfos["image"] = self.loadImage(fileName, folder = filePath, size = (self.largeImageSize, self.largeImageSize))
        imageLabel.config( image = self.activePuzzleInfos["image"] )


    def changeCoordSystem(self, button, coordLabels, coordEntryVars):
        """
        changes the image shown on the button to depict the currently chosen coordinate system
        calculates the current point's coordinates in the new coordinate system and sets the given variables to those values
        """
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


    def scrollColorchange(self, colorIndexVar, event, limited = False):
        """
        upadtes the given color index variable
        """
        if event.delta < 0:
            if limited == True:
                colorIndexVar.set( self.getClosestColorIndex(colorIndexVar.get(), direction = "larger") )
            else:
                colorIndexVar.set( (colorIndexVar.get()+1) % len(self.colors) )
        elif event.delta > 0:
            if limited == True:
                colorIndexVar.set( self.getClosestColorIndex(colorIndexVar.get(), direction = "smaller") )
            else:
                colorIndexVar.set( (colorIndexVar.get()-1) % len(self.colors) )
    
    def clickColorchange(self, colorIndexVar, change, limited = False):
        """
        upadtes the given color index variable
        """
        if change < 0:
            if limited == True:
                colorIndexVar.set( self.getClosestColorIndex(colorIndexVar.get(), direction = "larger") )
            else:
                colorIndexVar.set( (colorIndexVar.get()+1) % len(self.colors) )
        elif change > 0:
            if limited == True:
                colorIndexVar.set( self.getClosestColorIndex(colorIndexVar.get(), direction = "smaller") )
            else:
                colorIndexVar.set( (colorIndexVar.get()-1) % len(self.colors) )

    def getClosestColorIndex(self, currentColor, direction = "larger"):
        print(currentColor, self.activePuzzleInfos["colors"])
        colorOptions = []
        if direction == "larger":
            if currentColor == max(self.activePuzzleInfos["colors"]):
                    return min(self.activePuzzleInfos["colors"])
            else:
                for colorIndex in self.activePuzzleInfos["colors"]:
                    if colorIndex > currentColor:
                        colorOptions.append(colorIndex)
                return min(colorOptions)
        else:
            if currentColor == min(self.activePuzzleInfos["colors"]):
                    return max(self.activePuzzleInfos["colors"])
            else:
                for colorIndex in self.activePuzzleInfos["colors"]:
                    if colorIndex < currentColor:
                        colorOptions.append(colorIndex)
                return max(colorOptions)


    def changeColor(self, widget, colorIndexVar):
        widget.config(bg = self.colors[colorIndexVar.get()])


    def addCycleInput(self, frame):
        """
        adds an input field for a new cycle of a move in the given frame.
        the input field consists of 3 widgets (Label-Entry-Label)
        """
        maxColumn = frame.grid_slaves()[0].grid_info()["column"]
        maxRow = frame.grid_slaves()[0].grid_info()["row"]
        if len(frame.grid_slaves()) < 6:
            maxRow = 2
            maxColumn = -1
        # print(maxRow, maxColumn)
        if maxColumn >= 11:
            maxColumn = -1
            maxRow += 1
            if maxRow >= 3:
                frame.master.grid_propagate(True)

        # for i in range(3):
        #     label = tk.Label(frame, text = str(maxColumn+i+1))
        #     label.grid(row = maxRow, column = maxColumn+i+1)

        leftBracketLabel = tk.Label(frame, width = 1, text = "(", anchor = "e", justify = "right")
        self.addLabelStyle(leftBracketLabel, style = "secondary")
        leftBracketLabel.grid(row = maxRow, column = maxColumn+1, sticky = "e")

        cycleEntry = tk.Entry(frame, width = 6)
        self.addEntryStyle(cycleEntry, style = "secondary")
        cycleEntry.grid(row = maxRow, column = maxColumn+2, sticky = "w")

        rightBracketLabel = tk.Label(frame, width = 1, text = ")", anchor = "w", justify = "left")
        self.addLabelStyle(rightBracketLabel, style = "secondary")
        rightBracketLabel.grid(row = maxRow, column = maxColumn+3, sticky = "w")

        self.cycleEntryList.append(cycleEntry)


    def removeCycleInput(self, frame):
        """
        deletes the last three widgets (= last cycle input) from the given frame
        """
        if len(frame.grid_slaves())<=6: #6 is the minimum number of widgets the frame must have
            return                      # this is to prevent deletion of other widgets in the frame
        else:
            maxColumn = frame.grid_slaves()[0].grid_info()["column"]
            maxRow = frame.grid_slaves()[0].grid_info()["row"]
            # print(maxRow, maxColumn)
            if maxColumn <= 3 and maxRow <= 1:
                return
            if maxColumn<=2:
                if maxRow==3:
                    frame.master.grid_propagate(False)
                for i in range(3):
                    frame.winfo_children()[-1].destroy()
                    # frame.grid_slaves()[0].grid_forget()
            else:
                for i in range(3):
                    frame.winfo_children()[-1].destroy()
                    # frame.grid_slaves()[0].grid_forget()
            self.cycleEntryList.pop() #deletes last element

    def addPoint(self, pointIndexVar):
        """
        creates a new point with the minimal availiable Index
        """
        i = 0
        while i in self.activePuzzleInfos["points"].keys():
            i += 1
        
        pointIndexVar.set(i)


    def savePoint(self, pointIndexVar, coordEntryVarList, colorIndexVar):
        """
        saves the current point to self.activePuzzleInfos["points"]
        """
        coords = tuple([entry.get() for entry in coordEntryVarList])
        if self.activeCoordSystem == "spherical":
            coords = (
                    round( coords[0] * np.sin(coords[1]) * np.cos(coords[2]), 3 ),
                    round( coords[0] * np.sin(coords[1]) * np.sin(coords[2]), 3 ),
                    round( coords[0] * np.cos(coords[1] ), 3 )
                    )
        elif self.activeCoordSystem == "cylindrical":
            coords = (
                    round( coords[0] * np.cos(coords[1]), 3 ),
                    round( coords[0] * np.sin(coords[1]), 3 ),
                    round( coords[2], 3 )
                    )
        self.activePuzzleInfos["points"][pointIndexVar.get()] = {"coords":coords, "colorIndex":colorIndexVar.get()}

    def loadPoint(self, pointIndexVar, coordEntryVarList, colorIndexVar):
        """
        loads the current point to self.activePuzzleInfos["points"]
        """
        try: 
            pointInfo = self.activePuzzleInfos["points"][pointIndexVar.get()]
            for i,entryVar in enumerate(coordEntryVarList):
                entryVar.set(pointInfo["coords"][i])
            colorIndexVar.set(pointInfo["colorIndex"])
        except KeyError:
            for entryVar in coordEntryVarList:
                entryVar.set(1)

    def addMove(self, moveNameVar, frame):
        """
        clears the move input interface
        """
        n = 97
        while chr(n) in self.activePuzzleInfos["moves"].keys():
            n += 1
        moveNameVar.set(chr(n))

    def saveMove(self, moveNameVar):
        """
        save move to self.activePuzzleInfos["moves"]
        """
        self.activePuzzleInfos["moves"][moveNameVar.get()] = [tuple(entry.get().split(",")) for entry in self.cycleEntryList]

    def loadMove(self, moveNameVar, frame):
        """
        loads the move with the given name
        """
        self.clearCycles(frame)
        try:
            move = self.activePuzzleInfos["moves"][moveNameVar.get()]
            for cycle in move:
                self.cycleEntryList[-1].delete(0,"end")
                cycleString = ""
                for i,pointIndex in enumerate(cycle):
                    cycleString += pointIndex
                    if not i == len(cycle)-1:
                        cycleString += ","
                self.cycleEntryList[-1].insert(0, cycleString )
                self.addCycleInput(frame)
            if move != []:
                self.removeCycleInput(frame)
        except KeyError:
            move = []

    def clearCycles(self, frame):
        """
        removes cycle-Inputs until only one remains
        """
        while len(frame.winfo_children())>6:
            for _ in range(3):
                frame.winfo_children()[-1].destroy()
            self.cycleEntryList.pop()
        self.cycleEntryList[0].delete(0,"end")

    def copyFileRename(self, oldPath, newPath, newName = "icon.png"):
        """
        copies a file from "oldPath" to "newPath" and renames it to "newName"
        """
        shutil.copy(oldPath, newPath + "/" + newName)

    def savePuzzle(self, puzzleName, puzzle = "new"):
        """
        creates a Folder with the puzzle name
        creates files in this Folder for the following:
            the chosen image,
            the saved Points and Moves
        """
        if not self.activePuzzleInfos["points"] == dict(): #saves only if the puzzle has at least one point
            if puzzle in self.getFolderContents("puzzles") and puzzleName != puzzle:
                os.rename("puzzles/" + puzzle, "puzzles/" + puzzleName)
            elif not puzzleName in self.getFolderContents("puzzles"):
                os.mkdir("puzzles/" + puzzleName)

            puzzleInfoFile = open("puzzles/" + puzzleName + "/puzzleDefinition.txt", "w")
            for pointIndex, pointInfo in zip(self.activePuzzleInfos["points"].keys(), self.activePuzzleInfos["points"].values()):
                puzzleInfoFile.write( str(pointIndex) + " | " + str(pointInfo["coords"]) + " | " + str(pointInfo["colorIndex"]) + "\n")

            puzzleInfoFile.write("\n#########################\n")

            for moveName, move in zip(self.activePuzzleInfos["moves"].keys(), self.activePuzzleInfos["moves"].values() ):
                print(move)
                moveCycles = ""
                for cycle in move:
                    moveCycles += "(" + str([int(pointIndex) for pointIndex in cycle])[1:-1] + ")"
                puzzleInfoFile.write( moveName + " | " + moveCycles + "\n" )

            puzzleInfoFile.close()
        #copy image file (if given) to the puzzle folder
        if self.activePuzzleInfos["imagePath"] != "":
            self.copyFileRename(self.activePuzzleInfos["imagePath"], "puzzles/" + puzzleName, newName = "icon.png")
        self.goToWindow("savedPuzzles")

    def loadPuzzleInfos(self, puzzle):
        """
        loads information for a given puzzle from the definition file to self.activePuzzleInfos
        """
        self.activePuzzleInfos["name"] = puzzle
        self.activePuzzleInfos["colors"] = list()
        file = open("puzzles/" + puzzle + "/puzzleDefinition.txt", "r")
        writeTo = "points"
        for line in file.readlines():
            if line == "\n":
                continue
            if line=="#########################\n":
                writeTo = "moves"
                continue
            blocks = line.split(" | ")
            if writeTo == "points":
                self.activePuzzleInfos["points"][int(blocks[0])] = {"colorIndex": int(blocks[2])}
                if not int(blocks[2]) in self.activePuzzleInfos["colors"]:
                    self.activePuzzleInfos["colors"].append( int(blocks[2]) )

                self.activePuzzleInfos["points"][int(blocks[0])]["coords"] = [float(elem) for elem in blocks[1][1:-1].split(",")]
            elif writeTo == "moves":
                self.activePuzzleInfos["moves"][blocks[0]] = [tuple(cycle[1:].split(",")) for cycle in blocks[1].split(")")[:-1]]
        
        self.activePuzzleInfos["image"] = self.loadImage("icon.png", folder = "puzzles/"+puzzle, size = (self.largeImageSize, self.largeImageSize))
        self.activePuzzleInfos["numberOfColors"] = len(self.activePuzzleInfos["colors"])





    def algorithmOverviewWindow(self, puzzle):
        """
        creates a window showing all saved algorithms for the chosen puzzle
        """
        self.loadPuzzleInfos(puzzle)

        self.algorithmOverviewFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.algorithmOverviewFrame.pack(fill="both", expand=True)
        # self.algorithmOverviewFrame.grid_propagate(0)
        self.algorithmOverviewFrame.grid_columnconfigure(1,weight=1)
        self.algorithmOverviewFrame.grid_columnconfigure(0, minsize = self.largeButtonHeight)
        self.algorithmOverviewFrame.grid_columnconfigure(2, minsize = self.largeButtonHeight)


        algorithmOverviewHeadline = tk.Label(self.algorithmOverviewFrame, text = puzzle + " algorithms")
        self.addLabelStyle( algorithmOverviewHeadline, style="primaryHeadline" )
        algorithmOverviewHeadline.grid(row = 0, column = 1, sticky = "n", padx = 10, pady = 10)

        returnButton = tk.Button(self.algorithmOverviewFrame, 
                image = self.cross, 
                command = lambda: self.goToWindow("savedPuzzles"))
        self.addButtonStyle(returnButton, style = "primary")
        returnButton.grid(row = 0, column = 2, rowspan = 2, sticky = "ne", padx = 10, pady = 10)

        puzzleImageLabel = tk.Label(self.algorithmOverviewFrame)

        #loading the puzzle image
        if not puzzle in self.puzzleImages.keys():
            try:
                self.puzzleImages[puzzle] = self.loadImage("icon.png", folder="puzzles/"+puzzle, size=(self.largeImageSize, self.largeImageSize))
                puzzleImageLabel.config( image = self.puzzleImages[puzzle] )
            except FileNotFoundError:
                puzzleImageLabel.config( image = self.imageUpload )
        else:
            puzzleImageLabel.config( image = self.puzzleImages[puzzle] )
        
        self.addLabelStyle(puzzleImageLabel, style = "primary")
        puzzleImageLabel.grid(row = 0, column = 0, rowspan = 2, sticky = "nw", padx = 10, pady = 10)

        #add Button to show the solving strategy
        solvingStrategyFrame = tk.Frame(self.algorithmOverviewFrame, bg = self.primarycolor)
        solvingStrategyFrame.grid(row = 1, column = 1, sticky = "n", padx = 10, pady = (0,10))

        solvingStrategyLabel = tk.Label(solvingStrategyFrame, text = "solving strategy")
        self.addLabelStyle(solvingStrategyLabel, style="secondary")
        solvingStrategyLabel.grid(row = 0, column = 0, sticky = "w", padx = 5, pady = 5)
        
        solvingStrategyImage = tk.Label(solvingStrategyFrame, image = self.smallMenuBars)
        self.addLabelStyle(solvingStrategyImage, style="secondary")
        solvingStrategyImage.grid(row = 0, column = 1, sticky = "w", padx = 5, pady = 5)

        self.makeFrameToButton(solvingStrategyFrame)

        solvingStrategyFrame.bind( "<Button-1>", lambda _, puzzleName = puzzle: self.goToWindow("solvingStrategy", puzzle = puzzleName) )
        for child in solvingStrategyFrame.winfo_children():
            child.bind( "<Button-1>", lambda _, puzzleName = puzzle: self.goToWindow("solvingStrategy", puzzle = puzzleName) )

        #create algorithm folder if not yet existent
        if not "algorithms" in self.getFolderContents("puzzles/" + puzzle):
            os.mkdir("puzzles/" + puzzle + "/algorithms")

        puzzleFolderContents = self.getFolderContents("puzzles/" + puzzle + "/algorithms")

        #load algorithms
        for i,algorithm in enumerate(puzzleFolderContents):
            algorithmFrame = tk.Frame(self.algorithmOverviewFrame, 
                    bg=self.primarycolor, 
                    height=self.largeButtonHeight, 
                    width=self.largeButtonWidth
                    )
            algorithmFrame.grid_propagate(0)
            algorithmFrame.grid_columnconfigure(0, weight = 1)
            algorithmFrame.grid(row = i+2, column = 0, padx = 5, pady = 5, columnspan = 3, sticky = "n")

            algorithmNameLabel = tk.Label(algorithmFrame, text = algorithm[:-4])
            self.addLabelStyle(algorithmNameLabel, style = "secondaryHeadline")
            algorithmNameLabel.grid(row = 0, column = 0, sticky = "w", padx = 5, pady = (5,0))

            # previewText = self.getAlgorithmPreview(puzzle, algorithm)

            algorithmPreviewLabel = tk.Label(algorithmFrame, text = algorithm[:-4])
            self.addLabelStyle(algorithmPreviewLabel, style = "secondary")
            algorithmPreviewLabel.grid(row = 1, column = 0, sticky = "w", padx = 5, pady = (0,5))

            frame, button = self.sizedButton(algorithmFrame)
            button.config(image = self.openFile, 
                    command = lambda puzzleName=puzzle, algorithmName=algorithm: 
                        self.goToWindow("showAlgorithm", puzzle=puzzleName, algorithm = algorithmName)
                    )
            frame.grid(row = 0, column = 1, rowspan = 2, padx = 5, pady = 5, sticky = "e")
            button.pack(fill="both", expand=True)

            
            algorithmEditFrame, algorithmEditButton = self.sizedButton(algorithmFrame, height = self.largeButtonHeight//2, width = self.largeButtonHeight//2)
            algorithmEditFrame.grid(row = 0, column = 4, sticky = "ne")
            algorithmEditButton.config(image = self.smallEditIcon, command = lambda algorithmName = algorithm: self.goToWindow("algorithmCreation", puzzle = puzzle, algorithm = algorithmName))
            algorithmEditButton.pack(fill="both", expand=True)

            algorithmDeleteFrame, algorithmDeleteButton = self.sizedButton(algorithmFrame, height = self.largeButtonHeight//2, width = self.largeButtonHeight//2)
            algorithmDeleteFrame.grid(row = 1, column = 4, sticky = "se")
            algorithmDeleteButton.config(image = self.smallDeleteIcon, command = lambda algorithmName = algorithm, frame = algorithmFrame: self.deleteAlgorithm(puzzle, algorithmName, frame))
            algorithmDeleteButton.pack(fill="both", expand=True)


        algorithmAddFrame = tk.Frame(self.algorithmOverviewFrame, bg = self.primarycolor)
        if len(puzzleFolderContents) > 0:
            algorithmAddFrame.grid(row = i+3, column = 1, pady = 5, sticky = "n")
        else:
            algorithmAddFrame.grid(row = 3, column = 1, pady = 5, sticky = "n")

        algorithmAddImage = tk.Label(algorithmAddFrame, image=self.addIcon)
        self.addLabelStyle(algorithmAddImage,style="secondary")
        algorithmAddImage.grid(row = 0, column = 0, padx = (10,5), pady = 5, sticky = "w")

        algorithmAddLabel = tk.Label(algorithmAddFrame, text = "add algorithm")
        self.addLabelStyle(algorithmAddLabel, style="secondary")
        algorithmAddLabel.grid(row = 0, column = 1, padx = (5,10), sticky = "w")

        self.makeFrameToButton(algorithmAddFrame)
        algorithmAddFrame.bind( "<Button-1>", func = lambda _: self.goToWindow("algorithmCreation", puzzle) )
        for child in algorithmAddFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.goToWindow("algorithmCreation", puzzle) )

    def deleteAlgorithm(self, puzzle, algorithm, frame):
        """
        deletes the file of the given algorithm
        """
        os.remove("puzzles/" + puzzle + "/algorithms/" + algorithm)
        frame.destroy()





    def solvingStrategyWindow(self, puzzle): #TODO: make the textboxFrame as a Canvas and allow scrolling if the content gets too large
        """
        creates a window allowing the user to create or edit a solving strategy guide for the chosen puzzle
        """
        self.solvingStrategyFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.solvingStrategyFrame.pack(fill="both", expand=True)
        self.solvingStrategyFrame.grid_columnconfigure(1,weight=1)
        self.solvingStrategyFrame.grid_columnconfigure(0, minsize = self.largeButtonHeight)
        self.solvingStrategyFrame.grid_columnconfigure(2, minsize = self.largeButtonHeight)

        returnButton = tk.Button(self.solvingStrategyFrame, 
                image = self.cross, 
                command = lambda puzzleName = puzzle: self.goToWindow("algorithmOverview", puzzle = puzzleName))
        self.addButtonStyle(returnButton, style = "primary")
        returnButton.grid(row = 0, column = 2, sticky = "ne", padx = 10, pady = 10)

        puzzleImageLabel = tk.Label(self.solvingStrategyFrame)

        if not puzzle in self.puzzleImages.keys():
            try:
                self.puzzleImages[puzzle] = self.loadImage("icon.png", folder="puzzles/"+puzzle, size=(self.largeImageSize, self.largeImageSize))
                puzzleImageLabel.config( image = self.puzzleImages[puzzle] )
            except FileNotFoundError:
                puzzleImageLabel.config( image = self.imageUpload )
        else:
            puzzleImageLabel.config( image = self.puzzleImages[puzzle] )
                    
        self.addLabelStyle(puzzleImageLabel, style = "primary")
        puzzleImageLabel.grid(row = 0, column = 0, sticky = "nw", padx = 10, pady = 10)

        solvingStrategyHeadline = tk.Label(self.solvingStrategyFrame, text = "solving strategy")
        self.addLabelStyle(solvingStrategyHeadline, style="primaryHeadline")
        solvingStrategyHeadline.grid(row = 0, column = 1, sticky = "ns", padx = 10, pady = 10)

        textBoxesFrame = tk.Frame(self.solvingStrategyFrame, bg = self.bgcolor)
        textBoxesFrame.grid(row = 1, column = 0, columnspan = 3, sticky = "n")

        horizontalSpacer = self.generateSpacer(textBoxesFrame, bg = self.bgcolor, width = self.largeButtonWidth)
        horizontalSpacer.grid(row = 0, column = 1, sticky = "n")

        self.paragraphWidgets = {"numberLabels":[], "textBoxes":[], "deleteButtons":[]}

        self.loadStrategy(puzzle, textBoxesFrame)
        # self.addParagraph(textBoxesFrame)

        paragraphAddFrame = tk.Frame(self.solvingStrategyFrame, bg = self.primarycolor)
        paragraphAddFrame.grid(row = 2, column = 0, columnspan = 3, pady = 5, sticky = "n")

        paragraphAddImage = tk.Label(paragraphAddFrame, image=self.addIcon)
        self.addLabelStyle(paragraphAddImage,style="secondary")
        paragraphAddImage.grid(row = 0, column = 0, padx = (10,5), pady = 5, sticky = "w")

        paragraphAddLabel = tk.Label(paragraphAddFrame, text = "add paragraph")
        self.addLabelStyle(paragraphAddLabel, style="secondary")
        paragraphAddLabel.grid(row = 0, column = 1, padx = (5,10), sticky = "w")

        self.makeFrameToButton(paragraphAddFrame)
        paragraphAddFrame.bind( "<Button-1>", func = lambda _: self.addParagraph(textBoxesFrame) )
        for child in paragraphAddFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.addParagraph(textBoxesFrame) )


        saveStrategyFrame = tk.Frame(self.solvingStrategyFrame)
        self.makeFrameToButton(saveStrategyFrame)
        saveStrategyFrame.grid(row = 3, column = 0, columnspan = 3, sticky = "n", pady = 5)

        saveStrategyImage = tk.Label(saveStrategyFrame, image = self.saveIcon)
        self.addLabelStyle(saveStrategyImage, style="secondary")
        saveStrategyImage.grid(row = 0, column = 0, sticky = "w", padx = (10,5), pady = 5)

        saveStrategyLabel = tk.Label(saveStrategyFrame, text = "save strategy")
        self.addLabelStyle(saveStrategyLabel, style = "secondary")
        saveStrategyLabel.grid(row = 0, column = 1, sticky = "w", padx = (5,10), pady = 5)
        
        saveStrategyFrame.bind( "<Button-1>", func = lambda _: self.saveStrategy(puzzle=puzzle) )
        for child in saveStrategyFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.saveStrategy(puzzle=puzzle) )


    def addParagraph(self, master):
        """
        adds a new text widget to the given Frame including a deletion button and a move button 
        (either drag and drop or two arrows to move the paragraph up and down, low priority)
        """
        textBox = self.sizedTextField(master, style = "primary")
        maxRow = len(master.winfo_children()) //3 + 2
        textBox.grid(row = maxRow, column = 1, sticky = "ew", pady = 5)

        paragraphNumberLabel = tk.Label(master, text = str(maxRow-1)+".)")
        self.addLabelStyle(paragraphNumberLabel, style = "primary")
        paragraphNumberLabel.grid(row = maxRow, column = 0, sticky = "e", padx = 5, pady = 5)

        deleteParagraphButton = tk.Button(master, image = self.smallDeleteIcon)
        self.addButtonStyle( deleteParagraphButton, style = "primary" )
        deleteParagraphButton.config( command = lambda: self.destroyParagraph( maxRow-2 ) )
        deleteParagraphButton.grid(row = maxRow, column = 2, sticky = "w", ipadx = 5, ipady = 5)

        self.paragraphWidgets["numberLabels"].append(paragraphNumberLabel)
        self.paragraphWidgets["textBoxes"].append(textBox)
        self.paragraphWidgets["deleteButtons"].append(deleteParagraphButton)

    def destroyParagraph(self, deleteIndex):
        """
        deletes the paragraph in the given Row(index) along with it's associated other widgets
        """
        self.paragraphWidgets["numberLabels"][-1].destroy()
        self.paragraphWidgets["textBoxes"][deleteIndex].destroy()
        self.paragraphWidgets["deleteButtons"][-1].destroy()

        self.paragraphWidgets["numberLabels"] = self.paragraphWidgets["numberLabels"][:-1]
        self.paragraphWidgets["textBoxes"] = self.paragraphWidgets["textBoxes"][:deleteIndex]+self.paragraphWidgets["textBoxes"][deleteIndex+1:]
        self.paragraphWidgets["deleteButtons"] = self.paragraphWidgets["deleteButtons"][:-1]
        
        for i,textBox in enumerate( self.paragraphWidgets["textBoxes"][deleteIndex:] ):
            textBox.grid_configure(row = deleteIndex+i+2)


    def saveStrategy(self, puzzle):
        """
        saves the inputs from all paragraphs to a file "solving strategy.txt"
        """
        file = open(f"puzzles/{puzzle}/solving strategy.txt", "w")
        for textBox in self.paragraphWidgets["textBoxes"]:
            paragraphText = textBox.get("1.0", "end-1c")
            file.write(paragraphText)
            if textBox != self.paragraphWidgets["textBoxes"][-1]:
                file.write("\n#########################\n")
        file.close()

    def loadStrategy(self, puzzle, textBoxesFrame):
        """
        loads the strategy for the given puzzle from "solving strategy.txt"
        """
        self.addParagraph(textBoxesFrame)
        if "solving strategy.txt" in self.getFolderContents(f"puzzles/{puzzle}"):
            file = open(f"puzzles/{puzzle}/solving strategy.txt", "r")
            for line in file.readlines():
                if line=="#########################\n":
                    self.paragraphWidgets["textBoxes"][-1].delete("end-1c", "end")
                    self.__updateTextBox(self.paragraphWidgets["textBoxes"][-1], 2)
                    self.addParagraph(textBoxesFrame)
                else:
                    self.paragraphWidgets["textBoxes"][-1].insert("end", line)
                    self.__updateTextBox(self.paragraphWidgets["textBoxes"][-1], 2)
            file.close()





    def algorithmCreationWindow(self, puzzle):
        """
        creates a window allowing the user to input and save a new algorithm for the chosen puzzle
        """
        self.algorithmCreationFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.algorithmCreationFrame.pack(fill="both", expand=True)
        self.algorithmCreationFrame.grid_columnconfigure(1,weight = 1)
        self.algorithmCreationFrame.grid_columnconfigure(0, minsize = self.largeButtonHeight)
        self.algorithmCreationFrame.grid_columnconfigure(2, minsize = self.largeButtonHeight)

        algorithmName = tk.StringVar(value="algorithm #1")
        i = 2
        while algorithmName.get()+".txt" in self.getFolderContents("puzzles/" + puzzle + "/algorithms"):
            algorithmName.set( "algorithm #" + str(i) )
            i+=1

        algorithmCreationHeadline = tk.Entry(self.algorithmCreationFrame,
                textvariable = algorithmName)
        self.addEntryStyle(algorithmCreationHeadline, style="primaryHeadline")
        algorithmCreationHeadline.grid(row = 0, column = 1, sticky = "n", padx = 10, pady = 10)

        returnButton = tk.Button(self.algorithmCreationFrame, 
                image = self.cross, 
                command = lambda puzzleName = puzzle: self.goToWindow("algorithmOverview", puzzle = puzzleName))
        self.addButtonStyle(returnButton, style = "primary")
        returnButton.grid(row = 0, column = 2, sticky = "ne", padx = 10, pady = 10)

        puzzleImageLabel = tk.Label(self.algorithmCreationFrame)

        if not puzzle in self.puzzleImages.keys():
            try:
                self.puzzleImages[puzzle] = self.loadImage("icon.png", folder="puzzles/"+puzzle, size=(self.largeImageSize, self.largeImageSize))
                puzzleImageLabel.config( image = self.puzzleImages[puzzle] )
            except FileNotFoundError:
                puzzleImageLabel.config( image = self.imageUpload )
        else:
            puzzleImageLabel.config( image = self.puzzleImages[puzzle] )
                    
        self.addLabelStyle(puzzleImageLabel, style = "primary")
        puzzleImageLabel.grid(row = 0, column = 0, sticky = "nw", padx = 10, pady = 10)


        algorithmDescriptionFrame = tk.Frame(self.algorithmCreationFrame, bg = self.bgcolor)
        algorithmDescriptionFrame.grid(row = 1, column = 0, columnspan = 3, sticky = "n")

        algorithmDescriptionLabel = tk.Label(algorithmDescriptionFrame, text = "Description:")
        self.addLabelStyle(algorithmDescriptionLabel, style = "primary")
        algorithmDescriptionLabel.grid(row = 0, column = 0, sticky = "nw")

        horizontalspacer = self.generateSpacer(algorithmDescriptionFrame, bg = self.bgcolor, width = self.largeButtonWidth)
        horizontalspacer.grid(row = 1, column = 0, sticky = "n")

        algorithmDescriptionBox = self.sizedTextField(algorithmDescriptionFrame)
        algorithmDescriptionBox.grid(row = 2, column = 0, sticky = "ew")

        algorithmStepsFrame = tk.Frame(self.algorithmCreationFrame, bg = self.bgcolor)
        algorithmStepsFrame.grid(row = 2, column = 0, columnspan = 3, sticky = "n")

        self.algorithmStepWidgets = {
                "loadAlgorithmButtons":[],
                "algorithmEntries":[],
                "repeatLabels":[],
                "repeatEntries":[],
                "xLabels":[],
                "deleteButtons":[] }

        addAlgorithmStepFrame = tk.Frame(self.algorithmCreationFrame)
        self.makeFrameToButton(addAlgorithmStepFrame)
        addAlgorithmStepFrame.grid(row = 3, column = 1, sticky = "n", pady = 10)

        addAlgorithmStepImage = tk.Label(addAlgorithmStepFrame, image = self.addIcon)
        self.addLabelStyle(addAlgorithmStepImage, style="secondary")
        addAlgorithmStepImage.grid(row = 0, column = 0, sticky = "w", padx = (10,5), pady = 5)

        addAlgorithmStepLabel = tk.Label(addAlgorithmStepFrame, text = "add step")
        self.addLabelStyle(addAlgorithmStepLabel, style = "secondary")
        addAlgorithmStepLabel.grid(row = 0, column = 1, sticky = "w", padx = (5,10), pady = 5)

        self.addAlgorithmStep(algorithmStepsFrame)

        addAlgorithmStepFrame.bind( "<Button-1>", func = lambda _: self.addAlgorithmStep(algorithmStepsFrame) )
        for child in addAlgorithmStepFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.addAlgorithmStep(algorithmStepsFrame) )


        restartAnimationFrame = tk.Frame(self.algorithmCreationFrame, bg = self.bgcolor)
        restartAnimationFrame.grid(row = 4, column = 0, columnspan = 3, sticky = "n")

        restartAnimationButton = tk.Button(restartAnimationFrame, image = self.smallReloadIcon)
        self.addButtonStyle(restartAnimationButton, style = "primary")
        restartAnimationButton.grid(row = 0, column = 0, sticky = "w", pady = 5)

        restartAnimationLabel = tk.Label(restartAnimationFrame, text = "restart animation from:")
        self.addLabelStyle(restartAnimationLabel, style = "primary")
        restartAnimationLabel.grid(row = 0, column = 1, sticky = "w", padx = 5, pady = 5)

        restartAnimationFromEntry = tk.Entry(restartAnimationFrame, width = 3)
        self.addEntryStyle( restartAnimationFromEntry, style = "primary" )
        restartAnimationFromEntry.grid(row = 0, column = 2, sticky = "w", pady = 5)

        restartAnimationToLabel = tk.Label(restartAnimationFrame, text = "to")
        self.addLabelStyle( restartAnimationToLabel, style = "primary" )
        restartAnimationToLabel.grid(row = 0, column = 3, sticky = "w", padx = 5, pady = 5)

        restartAnimationToEntry = tk.Entry(restartAnimationFrame, width = 3)
        self.addEntryStyle( restartAnimationToEntry, style = "primary" )
        restartAnimationToEntry.grid(row = 0, column = 4, sticky = "w", pady = 5)


        saveAlgorithmFrame = tk.Frame(self.algorithmCreationFrame)
        self.makeFrameToButton(saveAlgorithmFrame)
        saveAlgorithmFrame.grid(row = 5, column = 1, sticky = "n", pady = 10)

        savePuzzleImage = tk.Label(saveAlgorithmFrame, image = self.saveIcon)
        self.addLabelStyle(savePuzzleImage, style="secondary")
        savePuzzleImage.grid(row = 0, column = 0, sticky = "w", padx = (10,5), pady = 5)

        savePuzzleLabel = tk.Label(saveAlgorithmFrame, text = "save algorithm")
        self.addLabelStyle(savePuzzleLabel, style = "secondary")
        savePuzzleLabel.grid(row = 0, column = 1, sticky = "w", padx = (5,10), pady = 5)
        
        saveAlgorithmFrame.bind( "<Button-1>", func = lambda _: self.saveAlgorithm(puzzle, algorithmName.get(), algorithmDescriptionBox) )
        for child in saveAlgorithmFrame.winfo_children():
            child.bind( "<Button-1>", func = lambda _: self.saveAlgorithm(puzzle, algorithmName.get(), algorithmDescriptionBox) )


    def addAlgorithmStep(self, master):
        """
        adds all widgets to allow the user to input a new step for the algorithm
        """
        maxRow = len(master.winfo_children())//6

        loadAlgorithmImage = tk.Label(master, image = self.smallLoadIcon)
        self.addLabelStyle(loadAlgorithmImage, style = "primary")
        loadAlgorithmImage.grid(row = maxRow, column = 0, sticky = "e", pady = 5)

        algorithmStepEntry = tk.Entry(master, width = 20)
        self.addEntryStyle(algorithmStepEntry, style = "primary", justify = "left")
        algorithmStepEntry.grid(row = maxRow, column = 1, sticky = "w", padx = 5, pady = 5)

        algorithmRepeatLabel = tk.Label(master, text = "repeat")
        self.addLabelStyle(algorithmRepeatLabel, style = "primary")
        algorithmRepeatLabel.grid(row = maxRow, column = 2, sticky = "e", padx = (5,0), pady = 5)

        algorithmRepeatEntry = tk.Entry(master, width = 3)
        self.addEntryStyle(algorithmRepeatEntry, style = "primary", justify = "right")
        algorithmRepeatEntry.grid(row = maxRow, column = 3, sticky = "e", padx = 2, pady = 5)
        algorithmRepeatEntry.insert("end", "1")

        algorithmXLabel = tk.Label(master, text = "x")
        self.addLabelStyle(algorithmXLabel, style = "primary")
        algorithmXLabel.grid(row = maxRow, column = 4, sticky = "w", pady = 5)

        deleteAlgorithmStepButton = tk.Button(master, image = self.smallDeleteIcon)
        self.addButtonStyle( deleteAlgorithmStepButton, style = "primary" )
        deleteAlgorithmStepButton.config( command = lambda: self.destroyAlgorithmStep( maxRow ) )
        deleteAlgorithmStepButton.grid(row = maxRow, column = 5, sticky = "w", ipadx = 5, ipady = 5)

        self.algorithmStepWidgets["loadAlgorithmButtons"].append( loadAlgorithmImage )
        self.algorithmStepWidgets["algorithmEntries"].append( algorithmStepEntry )
        self.algorithmStepWidgets["repeatLabels"].append( algorithmRepeatLabel )
        self.algorithmStepWidgets["repeatEntries"].append( algorithmRepeatEntry )
        self.algorithmStepWidgets["xLabels"].append( algorithmXLabel )
        self.algorithmStepWidgets["deleteButtons"].append( deleteAlgorithmStepButton )


    def destroyAlgorithmStep(self, deleteIndex):
        """
        deletes the algorithm step in the given Row(index) along with it's associated other widgets
        """
        self.algorithmStepWidgets["loadAlgorithmButtons"][-1].destroy()
        self.algorithmStepWidgets["algorithmEntries"][deleteIndex].destroy()
        self.algorithmStepWidgets["repeatLabels"][-1].destroy()
        self.algorithmStepWidgets["repeatEntries"][deleteIndex].destroy()
        self.algorithmStepWidgets["xLabels"][-1].destroy()
        self.algorithmStepWidgets["deleteButtons"][-1].destroy()

        self.algorithmStepWidgets["loadAlgorithmButtons"] = self.algorithmStepWidgets["loadAlgorithmButtons"][:-1]
        self.algorithmStepWidgets["algorithmEntries"] = self.algorithmStepWidgets["algorithmEntries"][:deleteIndex] + self.algorithmStepWidgets["algorithmEntries"][deleteIndex+1:]
        self.algorithmStepWidgets["repeatLabels"] = self.algorithmStepWidgets["repeatLabels"][:-1]
        self.algorithmStepWidgets["repeatEntries"] = self.algorithmStepWidgets["repeatEntries"][:deleteIndex] + self.algorithmStepWidgets["repeatEntries"][deleteIndex+1:]
        self.algorithmStepWidgets["xLabels"] = self.algorithmStepWidgets["xLabels"][:-1]
        self.algorithmStepWidgets["deleteButtons"] = self.algorithmStepWidgets["deleteButtons"][:-1]
        
        for i, Entries in enumerate( zip(
                self.algorithmStepWidgets["algorithmEntries"][deleteIndex:], 
                self.algorithmStepWidgets["repeatEntries"][deleteIndex:] ) ):
            Entries[0].grid_configure(row = deleteIndex+i)
            Entries[1].grid_configure(row = deleteIndex+i)

    def saveAlgorithm(self, puzzle, algorithmName, textBox):
        """
        saves the current input in puzzles/[puzzle]/algorithms as a .txt file
        """
        print("save algorithm")
        file = open("puzzles/" + puzzle + "/algorithms/" + algorithmName + ".txt","w")
        file.write(textBox.get("1.0", "end-1c"))
        file.write("\n#########################\n")
        for algorithmStepEntry, repeatEntry in zip(self.algorithmStepWidgets["algorithmEntries"], self.algorithmStepWidgets["repeatEntries"]):
            if not repeatEntry.get() == "0" and not repeatEntry.get() == "":
                step = algorithmStepEntry.get().lower()
                if not repeatEntry.get() == "1":
                    step = repeatEntry.get() + " * (" + step + ")"
                file.write(step)
            if not algorithmStepEntry == self.algorithmStepWidgets["algorithmEntries"][-1]:
                file.write(" ")

        file.close()
        self.goToWindow("algorithmOverview", puzzle = puzzle)





    def showAlgorithmWindow(self, puzzle, algorithm):
        """
        creates a window allowing the user to view a saved algorithms and apply it to the puzzle
        """
        self.showAlgorithmFrame = tk.Frame(self.master, bg=self.bgcolor)
        self.showAlgorithmFrame.pack(fill="both", expand=True)
        self.showAlgorithmFrame.grid_columnconfigure(1,weight=1)
        self.showAlgorithmFrame.grid_columnconfigure(0, minsize = self.largeButtonHeight)
        self.showAlgorithmFrame.grid_columnconfigure(2, minsize = self.largeButtonHeight)

        algorithmHeadLine = tk.Label(self.showAlgorithmFrame, text = algorithm[:-4])
        self.addLabelStyle(algorithmHeadLine, style="primaryHeadline")
        algorithmHeadLine.grid(row = 0, column = 1, sticky = "n", padx = 10, pady = 10)

        returnButton = tk.Button(self.showAlgorithmFrame, 
                image = self.cross, 
                command = lambda puzzleName = puzzle: self.goToWindow("algorithmOverview", puzzle = puzzleName))
        self.addButtonStyle(returnButton, style = "primary")
        returnButton.grid(row = 0, column = 2, sticky = "ne", padx = 10, pady = 10)

        puzzleImageLabel = tk.Label(self.showAlgorithmFrame)

        if not puzzle in self.puzzleImages.keys():
            try:
                self.puzzleImages[puzzle] = self.loadImage("icon.png", folder="puzzles/"+puzzle, size=(self.largeImageSize, self.largeImageSize))
                puzzleImageLabel.config( image = self.puzzleImages[puzzle] )
            except FileNotFoundError:
                puzzleImageLabel.config( image = self.imageUpload )
        else:
            puzzleImageLabel.config( image = self.puzzleImages[puzzle] )
                    
        self.addLabelStyle(puzzleImageLabel, style = "primary")
        puzzleImageLabel.grid(row = 0, column = 0, sticky = "nw", padx = 10, pady = 10)


        algorithmDescriptionFrame = tk.Frame(self.showAlgorithmFrame, bg = self.bgcolor)
        algorithmDescriptionFrame.grid(row = 1, column = 0, columnspan = 3, sticky = "n")

        algorithmDescriptionLabel = tk.Label(algorithmDescriptionFrame, text = "Description:")
        self.addLabelStyle(algorithmDescriptionLabel, style = "primary")
        algorithmDescriptionLabel.grid(row = 0, column = 0, sticky = "nw")

        horizontalspacer = self.generateSpacer(algorithmDescriptionFrame, bg = self.bgcolor, width = self.largeButtonWidth)
        horizontalspacer.grid(row = 1, column = 0, sticky = "n")

        algorithmDescriptionBox = self.sizedTextField(algorithmDescriptionFrame)
        algorithmDescriptionBox.grid(row = 2, column = 0, sticky = "ew")

        animationControlLabel = tk.Label(algorithmDescriptionFrame, text = "Animation controls:")
        self.addLabelStyle(animationControlLabel, style = "primary")
        animationControlLabel.grid(row = 3, column = 0, sticky = "w", pady = (10,5))

        animationControlFrame = tk.Frame(self.showAlgorithmFrame, bg = self.primarycolor)
        animationControlFrame.grid(row = 2, column = 0, columnspan = 3, sticky = "n", pady = (0,15))

        animationPreviousFrame = tk.Frame(animationControlFrame, bg = self.primarycolor)
        animationPreviousFrame.grid(row = 0, column = 0, sticky = "e", padx = 5, pady = 5)

        animationFirstImage = tk.Button(animationControlFrame, image = self.doubleLeftPlayIcon, command = self.firstMove())
        self.addButtonStyle(animationFirstImage, style = "secondary")
        animationFirstImage.grid(row = 0, column = 0, sticky = "n", ipadx = 5, ipady = 5, padx = 5, pady = 5)

        animationPreviousImage = tk.Button(animationControlFrame, image = self.leftPlayIcon, command = self.previousMove())
        self.addButtonStyle(animationPreviousImage, style = "secondary")
        animationPreviousImage.grid(row = 0, column = 1, sticky = "n", ipadx = 5, ipady = 5, padx = 5, pady = 5)

        animationPauseImage = tk.Button(animationControlFrame, image = self.pauseIcon, command = self.pauseAnimation())
        self.addButtonStyle(animationPauseImage, style = "secondary")
        animationPauseImage.grid(row = 0, column = 2, sticky = "n", ipadx = 5, ipady = 5, padx = 5, pady = 5)

        animationNextImage = tk.Button(animationControlFrame, image = self.rightPlayIcon, command = self.nextMove())
        self.addButtonStyle(animationNextImage, style = "secondary")
        animationNextImage.grid(row = 0, column = 3, sticky = "n", ipadx = 5, ipady = 5, padx = 5, pady = 5)

        animationRepeatImage = tk.Button(animationControlFrame, image = self.reloadIcon, command = self.repeatMove())
        self.addButtonStyle(animationRepeatImage, style = "secondary")
        animationRepeatImage.grid(row = 0, column = 4, sticky = "n", ipadx = 5, ipady = 5, padx = 5, pady = 5)


        puzzleStateInputFrame = tk.Frame(self.showAlgorithmFrame, bg = self.primarycolor)
        puzzleStateInputFrame.grid(row = 3, column = 0, columnspan = 3, sticky = "n")

        puzzleStateInputLabel = tk.Label(puzzleStateInputFrame, text = "Input current puzzle state:")
        self.addLabelStyle(puzzleStateInputLabel, style = "secondary")
        puzzleStateInputLabel.grid(row = 0, column = 0, columnspan = 4, sticky = "nw", padx = 5, pady = 4)

        horizontalSpacer2 = self.generateSpacer(puzzleStateInputFrame, bg = self.primarycolor, width = self.largeButtonWidth)
        horizontalSpacer2.grid(row = 1, column = 0, columnspan = 4, sticky = "w")

        editPointlabel = tk.Label(puzzleStateInputFrame, text = "edit point:")
        self.addLabelStyle(editPointlabel, style = "secondary")
        editPointlabel.grid(row = 2, column = 0, sticky = "w", padx = (20,5), pady = 3)

        editPointEntry = tk.Entry(puzzleStateInputFrame, width = 3)
        self.addEntryStyle(editPointEntry, style="secondary")
        editPointEntry.grid(row = 2, column = 1, sticky = "w")

        pointColorLabel = tk.Label(puzzleStateInputFrame, text = "color:")
        self.addLabelStyle(pointColorLabel, style = "secondary")
        pointColorLabel.grid(row = 3, column = 0, sticky = "w", padx = (20,5), pady = 3)

        colorIndexVar = tk.IntVar(value = 4)

        pointColorDisplay = tk.Label(puzzleStateInputFrame, 
                bg = self.colors[colorIndexVar.get()], 
                width = 6, 
                height = 1,
                cursor = "hand2",
                takefocus = True)
        pointColorDisplay.grid(row = 3, column = 1, sticky = "w")

        pointColorDisplay.bind( "<MouseWheel>", func = lambda event, tkVar = colorIndexVar: 
                self.scrollColorchange(tkVar, event, limited = True) )
        pointColorDisplay.bind( "<Button-1>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(tkVar, -1, limited = True) )
        pointColorDisplay.bind( "<Button-3>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(tkVar, 1, limited = True) )
        pointColorDisplay.bind( "<Down>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(tkVar, -1, limited = True) )
        pointColorDisplay.bind( "<Up>", func = lambda event, tkVar = colorIndexVar:
                self.clickColorchange(tkVar, 1, limited = True) )
        colorIndexVar.trace("w", lambda *_: self.changeColor(pointColorDisplay, colorIndexVar))

        self.addToolTip(pointColorDisplay, text = "scroll or click to change color", bg=self.bgcolor, fg=self.primarytextcolor)




    def firstMove(self):
        pass

    def previousMove(self):
        pass
    
    def pauseAnimation(self):
        pass
    
    def nextMove(self):
        pass
    
    def repeatMove(self):
        pass


if __name__=="__main__":
    menu = twistyPuzzleMenu()
    tk.mainloop()
