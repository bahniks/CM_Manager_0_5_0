"""
Copyright 2013 Štěpán Bahník

This file is part of Carousel Maze Manager.

Carousel Maze Manager is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Carousel Maze Manager is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Carousel Maze Manager.  If not, see <http://www.gnu.org/licenses/>.
"""

from tkinter import *
from tkinter import ttk

from commonframes  import TimeFrame, returnName
from optionget import optionGet
from comment import Comment, commentColor
import mode as m


class ShowTracks(Toplevel):
    "displays Canvases with trajectory of a selected track"
    def __init__(self, root, tracks, nameA, controlled = False):
        super().__init__(root)
        self["padx"] = 4
        self["pady"] = 4
        self.title("Track images")
        self.grab_set()
        self.focus_set()
        self.resizable(FALSE, FALSE)
        self.geometry("+8+40")

        self.controlled = controlled
        self.tracks = tracks
        self.root = root
        self.fileStorage = m.fs[m.mode]
        self.index = self.tracks.index(nameA)
        self.enabledManualReflectionsRemoval = False
        self.size = 6 # size of a mouse circle for reflection removal


        # number of canvases
        self.columns = ((self.winfo_screenwidth() - 515) // 290) or 1
        self.rows = ((self.winfo_screenheight() - 50 )// 290) or 1
        self.numberOfCanvases = self.columns * self.rows
        
        # canvases
        self.canvasFrame = ttk.Frame(self)
        self.canvasFrame.grid(column = 0, row = 0)
        self.canvasFrame.root = self

        for canvasNumber in range(0, self.numberOfCanvases):
            exec("self.canvas{} = TrackCanvas(self.canvasFrame)".format(canvasNumber))
            exec("self.canvas{}.grid(column = {}, row = {}, padx = 2, pady = 2)"\
                 .format(canvasNumber, canvasNumber % self.columns, canvasNumber // self.columns))

        # fileTree (the entire right part)
        self.fileTree = FileTree(self, files = self.tracks, controlled = controlled)
        self.fileTree.grid(column = 1, row = 0, sticky = (N, S, E, W), padx = 3, pady = 3) 
        
        # initialization of selected track
        self.drawTracks(new = True)

        # event binding
        self.bind("<Up>", lambda e: self.fileTree.previousFun())
        self.bind("<Left>", lambda e: self.fileTree.previousFun())
        self.bind("<Down>", lambda e: self.fileTree.nextFun())
        self.bind("<Right>", lambda e: self.fileTree.nextFun())
        self.bind("<Return>", lambda e: self.drawTracks(new = False))
        self.bind("<MouseWheel>", lambda e: self.mouseWheel(e))

        self.canvasFrame.bind("<3>", lambda e: self.popUp(e))

        # on exit
        self.protocol("WM_DELETE_WINDOW", lambda: self.closeFun())


    def popUp(self, event, canvas = None):
        "makes pop-up menu with options related to manual reflection removal"
        menu = Menu(self, tearoff = 0)
        if not self.enabledManualReflectionsRemoval:
            label = "Enable manual reflection removal"
        else:
            label = "Disable manual reflection removal"
        menu.add_command(label = label, command = self.toggleManualReflectionRemoval)
        menu.add_separator()
        if canvas:
            if canvas.addedReflections:
                menu.add_command(label = "Undo manual changes", command = canvas.undoChanges)
            else:
                menu.add_command(label = "Undo manual changes", command = canvas.undoChanges,
                                 state = "disabled")
        for canvasNumber in range(0, self.numberOfCanvases):
            if eval("self.canvas{}.addedReflections".format(canvasNumber)):
                menu.add_command(label = "Undo all manual changes", command = self.undoChanges)
                break
        else:
            menu.add_command(label = "Undo all manual changes", command = self.undoChanges,
                             state = "disabled")
        menu.post(event.x_root, event.y_root)


    def undoChanges(self):
        "removes all manually added reflections"
        self._initializeCM(self.cm.nameA)
        reflections = self.cm.findReflections(results = "indices")
        self.fileStorage.reflections[self.cm.nameA] = set(reflections[0] + reflections[1])
        self.fileStorage.addedReflections[self.cm.nameA] = set()
        self.drawTracks(new = True)


    def mouseWheel(self, event):
        "changes size of a mouse circle used for reflection removal"
        if self.enabledManualReflectionsRemoval:
            if event.num == 5 or event.delta == - 120:
                if self.size > 2:
                    self.size -= 1
            elif event.num == 4 or event.delta == 120:
                self.size += 1


    def toggleManualReflectionRemoval(self):
        "enables or disables manual reflection removal"
        if not self.fileTree.removeReflectionsVar.get():
            self.fileTree.removeReflectionsVar.set(True)
            self.fileTree.toggleReflections()
        self.enabledManualReflectionsRemoval = not self.enabledManualReflectionsRemoval
        for canvasNumber in range(0, self.numberOfCanvases):
            exec("self.canvas{}.toggleReflectionRemoval()".format(canvasNumber))
            

    def setTime(self):
        "redraws tracks when time is changed"
        self.drawTracks(new = False)


    def closeFun(self):
        "closes the window"
        if self.controlled:
            self.root.checkProcessing()
        else:
            self.root.root.checkProcessing()

        self.destroy()


    def _initializeCM(self, file):
        "initializes self.cm"
        if file in self.fileStorage.pairedfiles:
            self.cm = m.CL(file, self.fileStorage.pairedfiles[file])
        else:
            self.cm = m.CL(file, "auto")                     
        
                        
    def drawTracks(self, new = True):
        "draws selected track"
        if new:
            file = self.fileTree.files[self.fileTree.index]
            self._initializeCM(file)
            
        if self.fileTree.removeReflectionsVar.get():
            if self.cm.nameA not in self.fileStorage.reflections:
                reflections = self.cm.findReflections(results = "indices")
                self.fileStorage.reflections[self.cm.nameA] = set(reflections[0] + reflections[1])
                
            self.cm.removeReflections(points = self.fileStorage.reflections[self.cm.nameA],
                                      deleteSame = True)               
            
        self.scale = 136 / self.cm.radius
        r = self.cm.radius * self.scale
    
        stopTime = int(self.fileTree.timeFrame.timeVar.get()) * 60000
        startTime = int(self.fileTree.timeFrame.startTimeVar.get()) * 60000
        timeRange = stopTime - startTime
       
        # draws the track divided in equal time intervals 
        for canvasNumber in range(0, self.numberOfCanvases):
            rangeBegin = startTime + timeRange * canvasNumber / self.numberOfCanvases
            rangeEnd = startTime + timeRange * (canvasNumber + 1) / self.numberOfCanvases
            if self.fileTree.frameVar.get() == "arena":
                selectData = [[line[7]*self.scale, line[8]*self.scale, line[0]] for line in self.cm.data if \
                              rangeBegin <= line[1] <= rangeEnd]
            if self.fileTree.frameVar.get() == "room":
                selectData = [[line[2]*self.scale, line[3]*self.scale, line[0]] for line in self.cm.data if \
                              rangeBegin <= line[1] <= rangeEnd]
            exec("self.canvas{}.drawTrack(r, data = selectData)".format(canvasNumber))


class TrackCanvas(Canvas):
    "canvas depicting arena and part of a track"
    def __init__(self, root):
        super().__init__(root, background = "white", height = 280, width = 280)
        self.root = root.root
        self.toggleReflectionRemoval()
        self.removed = set()
        self.addedReflections = set()
        self.data = []
        self.r = None
        self.bind("<3>", lambda e: self.root.popUp(e, canvas = self))


    def toggleReflectionRemoval(self):
        "enables or disables manual reflection removal"
        if self.root.enabledManualReflectionsRemoval:
            self.bind('<Leave>', lambda e: self.leave(e))
            self.bind('<Motion>', lambda e: self.motion(e))
            self.bind('<1>', lambda e: self.click(e))
        else:
            self.unbind('<Leave>')
            self.unbind('<Motion>')
            self.unbind('<1>')

            
    def undoChanges(self):
        "removes all manually added reflections in the TrackCanvas"
        self.root.fileStorage.removeReflections(self.root.cm.nameA, self.addedReflections)
        if self.addedReflections:
            self.delete("removedInfo")
        self.removed = set()
        self.addedReflections = set()
        self.root.drawTracks(new = True)


    def drawTrack(self, radius, data):
        "draws an arena and track"
        self.delete("all")
        self.data = data
        self.removed = set()
        
        if len(data) > 1:
            self.r = radius
            fun = self.create_rectangle if m.mode == "OF" else self.create_oval
            fun(140 - self.r, 140 - self.r, 140 + self.r, 140 + self.r,
                outline = "black", width = 2)
            lines = [item + 140 - self.r for row in self.data for item in row[0:2]]
            self.create_line((lines), fill = "black", width = 2, tag = "trajectory")
            
        if self.data:
            begin = self.data[0][2]
            end = self.data[-1][2]
            if self.root.cm.nameA in self.root.fileStorage.addedReflections:
                self.addedReflections = {point for point in
                                         self.root.fileStorage.addedReflections[self.root.cm.nameA]
                                         if begin <= point <= end}
            else:
                self.addedReflections = set()
        else:
            self.addedReflections = set()
            
        if self.addedReflections:
            self.create_oval(3, 3, 16, 16, fill = "red", tag = "removedInfo", outline = "red")


    def motion(self, event):
        "called on mouse movement"
        self.delete("mouse")
        self.create_oval(event.x - self.root.size, event.y - self.root.size,
                         event.x + self.root.size, event.y + self.root.size,
                         outline = "red", width = 2, tag = "mouse")


    def leave(self, event):
        "called when mouse leaves the TrackCanvas"
        self.delete("mouse")


    def click(self, event):
        "called on mouse click - removes reflections"
        x, y = event.x - 140 + self.r, event.y - 140 + self.r
        newlyRemoved = {row[2] for row in self.data if row[2] not in self.removed and
                             ((row[0] - x)**2 + (row[1] - y)**2)**0.5 < self.root.size}

        if newlyRemoved:
            self.delete("trajectory")

            if not self.addedReflections:
                self.create_oval(3, 3, 16, 16, fill = "red", tag = "removedInfo", outline = "red")

            self.root.fileStorage.addReflections(self.root.cm.nameA, newlyRemoved)
            self.addedReflections.update(newlyRemoved)
            
            for point in sorted(self.root.cm.interpolated):
                if point in newlyRemoved or point - 2 in newlyRemoved:
                    newlyRemoved.add(point)
            self.removed.update(newlyRemoved)
                       
            lines = [item + 140 - self.r for row in self.data for item in row[0:2] if not
                     row[2] in self.removed]
            if len(lines) >= 4: 
                self.create_line((lines), fill = "black", width = 2, tag = "trajectory")      



class FileTree(ttk.Frame):
    "displays files in ShowTracks class"
    def __init__(self, root, files, controlled = False):
        super().__init__(root)

        self.rowconfigure(0, weight = 1)

        self.allFiles = files # used when un-selecting files
        self.files = files # currently diplayed files
        self.controlled = controlled # True if FileTree called from controller
        self.root = root
        self.fileStorage = self.root.fileStorage
        self.index = self.root.index # which file is selected when the FileTree is initialized
        self.usedProblemOrder = -1 # by which method is the tree ordered (index)

        # tree
        self.treeFrame = ttk.Frame(self)
        self.treeFrame.grid(column = 0, row = 0, columnspan = 3, sticky = (N, S, E, W))
        self.treeFrame.rowconfigure(0, weight = 1)
        self.treeFrame.columnconfigure(0, weight = 1)
        
        self.tree = ttk.Treeview(self.treeFrame, selectmode = "browse", height = 20)
        self.tree.grid(column = 0, row = 0, sticky = (N, S, E, W))
        
        if self.controlled:
            columns = ("problem", "tag")
        else:
            columns = ("tag")
        self.tree["columns"] = columns

        self.tree.column("#0", width = 240, anchor = "w")        
        self.tree.heading("#0", text = "File", command = self.orderByNames)

        self.tree.column("tag", width = 40, anchor = "center")
        self.tree.heading("tag", text = "Tag", command = self.orderByTag)
        
        if self.controlled:
            self.tree.column("problem", width = 160, anchor = "e")
            self.tree.heading("problem", text = "Problems", command = self.orderByProblem)
            
        self.scrollbar = ttk.Scrollbar(self.treeFrame, orient = VERTICAL,
                                       command = self.tree.yview)
        self.scrollbar.grid(column = 1, row = 0, sticky = (N, S, E))
        self.tree.configure(yscrollcommand = self.scrollbar.set)

        self.tree.bind("<1>", lambda e: self.click(e))
        self.tree.bind("<Double-1>", lambda e: self.doubleclick(e))
        self.tree.bind("<3>", lambda e: self.popUp(e))

        self.tree.tag_configure("comment", background = commentColor())

        self.drawTree()

        # bottom frame
        self.bottomFrame = ttk.Frame(self)
        self.bottomFrame.grid(column = 0, row = 1, columnspan = 2)
        self.bottomFrame.columnconfigure(3, weight = 1)
        self.bottomFrame.rowconfigure(1, weight = 1)

        # previous and next buttons
        self.fileLabFrame = ttk.Labelframe(self.bottomFrame, text = "File")
        self.fileLabFrame.grid(column = 0, row = 0, sticky = (N, W), pady = 3, padx = 1)
        
        self.previousBut = ttk.Button(self.fileLabFrame, text = "Previous",
                                      command = self.previousFun)
        self.previousBut.grid(column = 0, row = 0, padx = 3)
        
        self.nextBut = ttk.Button(self.fileLabFrame, text = "Next", command = self.nextFun)
        self.nextBut.grid(column = 1, row = 0, padx = 3)

        # tag buttons
        self.tagLabFrame = ttk.Labelframe(self.bottomFrame, text = "Tagging")
        self.tagLabFrame.grid(column = 0, row = 1, sticky = (N, W), rowspan = 2,
                              padx = 1, pady = 4)
        
        self.tagBut = ttk.Button(self.tagLabFrame, text = "Tag file", command = self.tagFun)
        self.tagBut.grid(column = 1, row = 1, padx = 3)
        self.checkTag()

        self.tagAllBut = ttk.Button(self.tagLabFrame, text = "Tag all", command = self.tagAllFun)
        self.tagAllBut.grid(column = 2, row = 1, padx = 3)

        self.untagAllBut = ttk.Button(self.tagLabFrame, text = "Remove all tags",
                                      command = self.untagAllFun)
        self.untagAllBut.grid(column = 3, row = 1, padx = 3)

        # time frame
        self.timeLabFrame = ttk.Labelframe(self.bottomFrame, text = "Time")
        self.timeLabFrame.grid(column = 3, row = 0, rowspan = 2, sticky = N, pady = 3)
        self.timeLabFrame.root = self.root
    
        self.timeFrame = TimeFrame(self.timeLabFrame, onChange = True, observe = False)
        self.timeFrame.grid(column = 0, row = 0)
        self.timeFrame.timeVar.set(TimeFrame.stop[m.mode])
        self.timeFrame.startTimeVar.set(TimeFrame.start[m.mode])

        # remove reflections checkbutton
        self.removeReflectionsVar = BooleanVar()
        self.removeReflectionsVar.set(False)
        self.removeReflections = ttk.Checkbutton(self.bottomFrame, text = "Remove reflections",
                                                 variable = self.removeReflectionsVar,
                                                 command = self.toggleReflections)
        self.removeReflections.grid(column = 2, row = 2, padx = 7, pady = 5, sticky = (N, W),
                                    columnspan = 2)

        # frame radiobuttons       
        self.frameVar = StringVar()
        
        if m.files == "pair":
            self.frameVar.set("arena")
        else:
            self.frameVar.set("room")
        
        if m.files == "pair":
            self.frameFrame = ttk.Labelframe(self.bottomFrame, text = "Frame")
            self.frameFrame.grid(column = 2, row = 0, padx = 5, rowspan = 2, pady = 3, sticky = N)
            
            self.arenaFrameRB = ttk.Radiobutton(self.frameFrame, text = m.pairing[m.mode][0],
                                                variable = self.frameVar, value = "arena",
                                                command = self.toggleFrame)
            self.arenaFrameRB.grid(column = 0, row = 0, pady = 2, sticky = W)
            
            self.roomFrameRB = ttk.Radiobutton(self.frameFrame, text = m.pairing[m.mode][1],
                                               variable = self.frameVar, value = "room",
                                               command = self.toggleFrame)
            self.roomFrameRB.grid(column = 0, row = 1, pady = 2, sticky = W)



    def toggleFrame(self):
        "called when frame is changed - just refreshes canvases"
        self.root.drawTracks(new = False)


    def toggleReflections(self):
        "called when reflections removal is changed - just refreshes canvases"
        if self.removeReflectionsVar.get():
            self.root.drawTracks(new = False)
        else:
            self.root.drawTracks(new = True)            
        

    def tagAllFun(self):
        "tags all displayed files"
        for file in self.files:
            self.fileStorage.tag(file)
        self.drawTree()
        self.tagBut["text"] = "Remove tag"
        self.tagBut["command"] = self.untagFun

    def untagAllFun(self):
        "untags all displayed files"
        for file in self.files:
            if file in self.fileStorage.tagged:
                self.fileStorage.tagged.remove(file)
        self.drawTree()
        self.tagBut["text"] = "Tag file"
        self.tagBut["command"] = self.tagFun        

    def tagFun(self, index = "none"):
        "tags the selected file"
        selected = self.files[eval(self.tree.selection()[0])]
        if index != "none":
            self.index = index
        else:
            self.tagBut["text"] = "Remove tag"
            self.tagBut["command"] = self.untagFun
        self.fileStorage.tag(self.files[self.index])
        self.drawTree(selected = selected)

    def untagFun(self, index = "none"):
        "untags the selected file"
        selected = self.files[eval(self.tree.selection()[0])]
        if index != "none":
            self.index = index
        else:
            self.tagBut["text"] = "Tag file"
            self.tagBut["command"] = self.tagFun 
        self.fileStorage.tagged.remove(self.files[self.index])
        self.drawTree(selected = selected)              

    def checkTag(self):
        "checks the state of tag button"
        if self.files[self.index] in self.fileStorage.tagged:
            command = self.untagFun
            text = "Remove tag"
        else:
            command = self.tagFun
            text = "Tag file"            
        self.tagBut["text"] = text
        self.tagBut["command"] = command


    def click(self, event):
        "called when item in tree is clicked"
        item = self.tree.identify("item", event.x, event.y)
        if item:
            self.tree.selection_set(item)
            self.index = int(item)
            self.root.drawTracks(new = True)
            self.checkTag()


    def doubleclick(self, event):
        "called when item in tree is clicked"
        item = self.tree.identify("item", event.x, event.y)
        if item and self.index == int(item):
            Comment(self, self.files[eval(self.tree.selection()[0])])
            
        
    def previousFun(self):
        "shows previous file"
        if self.index != 0:
            self.prevIndex = self.index
            self.index -= 1
            self.root.drawTracks(new = True)
            self.tree.selection_set(str(self.index))
            self.tree.see(str(self.index))
            self.checkTag()

    def nextFun(self):
        "shows next file"
        if self.index != len(self.files) - 1:
            self.prevIndex = self.index
            self.index += 1
            self.root.drawTracks(new = True)
            self.tree.selection_set(str(self.index))
            self.tree.see(str(self.index))
            self.checkTag()


    def orderByNames(self):
        "orders files by names"
        selected = self.files[eval(self.tree.selection()[0])]
        self.files.sort()
        self.drawTree(selected = selected)

    def orderByTag(self):
        "order files by tags"
        selected = self.files[eval(self.tree.selection()[0])]
        self.files.sort(key = lambda i: (i in self.fileStorage.tagged),
                        reverse = True)
        self.drawTree(selected = selected)

    def orderByProblem(self):
        """orders files by problem - which is displayed (the problem by which files are ordered
            changes when the function is used again)"""
        selected = self.files[eval(self.tree.selection()[0])]
        self.usedProblemOrder = (self.usedProblemOrder + 1) % \
                                len(self.root.root.controlReport.controls)
        method = self.root.root.controlReport.controls[self.usedProblemOrder]
        results = self.root.root.controlReport.results[method]
        values = {tup[0]: tup[3] for tup in results}
        self.tree.heading("problem", text = ("Problems (by {})".format(method)))
        
        self.files.sort(key = lambda i: values[i], reverse = True)
        self.drawTree(selected = selected)


    def drawTree(self, selected = None):
        "initializes (or refreshes) tree"
        for child in self.tree.get_children():
            self.tree.delete(child)
            
        for count, file in enumerate(self.files):
            tag = "x" if file in self.fileStorage.tagged else ""
                
            if self.controlled:
                problemKey = {"Problem": "P", "Warning": "W", "Concern": "C", "OK": "O"}
                methodKey = {"Reflections": "Ref", "Bad Points": "BP", "Outside Points": "OP"}
                problem = ""
                for method in self.root.root.controlReport.results:
                    importance = [i[2] for i in self.root.root.controlReport.results[method] if\
                                  i[0] == file]
                    problem = problem + methodKey[method] + ": " + problemKey[importance[0]] + ", "
                problem = problem[:-2]                  
                values = (problem, tag)
            else:
                values = (tag)
                
            comment = "comment" if self.fileStorage.comments[file] else "withoutComment"   
            self.tree.insert("", "end", str(count), text = returnName(file, self.files),
                             values = values, tag = comment)

        if selected:
            self.index = self.files.index(selected)

        if self.files:
            self.tree.selection_set(str(self.index))            
            self.tree.see(str(self.index))


    def refresh(self):
        "refreshes the tree after adding a comment"
        selected = self.files[eval(self.tree.selection()[0])]
        self.drawTree(selected = selected)
        

    def popUp(self, event):
        "called when tree item is clicked on"
        item = self.tree.identify("item", event.x, event.y)
        menu = Menu(self, tearoff = 0)
        if item:
            file = self.files[int(item)]
            if int(item) == self.index:
                menu.add_command(label = "Add comment", command = lambda: Comment(self, file))
            else:
                menu.add_command(label = "Add comment", command = lambda: Comment(self, file, False))
            if file in self.fileStorage.tagged:
                menu.add_command(label = "Remove tag", command = lambda: self.untagFun(index =
                                                                                       int(item)))
            else:
                menu.add_command(label = "Add tag", command = lambda: self.tagFun(index =
                                                                                  int(item)))
        elif self.controlled:
            menu.add_command(label = 'Leave only Bad Points', command = lambda:
                                 self.leaveOnlyFun("Bad Points"))        
            menu.add_command(label = 'Leave only Reflections', command = lambda:
                                 self.leaveOnlyFun("Reflections"))
            menu.add_command(label = 'Leave only Outside Points', command = lambda:
                                 self.leaveOnlyFun("Outside Points"))
            menu.add_separator()
            menu.add_command(label = "Return all", command = lambda: self.leaveOnlyFun("all"))
        menu.post(event.x_root, event.y_root)


    def leaveOnlyFun(self, problem):
        "leaves only files with some problem; or show all files again if problem == 'all'"
        if self.files:
            currentFile = self.files[self.index]
        else:
            currentFile = None
        
        if problem != "all":
            self.files = [file for file in self.files if file in 
                          [i[0] for i in self.root.root.controlReport.results[problem] if
                           i[2] != "OK"]]
        else:
            self.files = self.allFiles
            
        if currentFile in self.files:
            self.index = self.files.index(currentFile)
        else:    
            self.index = 0
            
        self.drawTree()
        
        if self.files:
            self.root.drawTracks()
            self.tree.selection_set(str(self.index))
            self.checkTag()


