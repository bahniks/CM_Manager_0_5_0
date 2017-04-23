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
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter import messagebox
from decimal import Decimal

import pickle
import os
import os.path

from optionget import optionGet
from window import placeWindow
from optionwrite import optionWrite
from commonframes import TimeFrame
import mode as m


def saveFileStorage(root, mode, file = None):
    "saves pickled fileStorage"
    initialdir = optionGet("SelectedFilesDirectory", os.path.join(os.getcwd(), "Stuff",
                                                                  "Selected files"), "str", True)
    if not file:
        file = asksaveasfilename(filetypes = [("Filestorage", "*.files")], initialdir = initialdir)
    if file:
        if os.path.splitext(file)[1] != ".files":
            file = file + ".files"
        with open(file, mode = "wb") as infile:
            m.fs[mode].lastSave = file
            pickle.dump(m.fs[mode], infile)


def loadFileStorage(root, file = None):
    "loads pickled fileStorage"
    initialdir = optionGet("SelectedFilesDirectory", os.path.join(os.getcwd(), "Stuff",
                                                                  "Selected files"), "str", True)
    if not file:
        file = askopenfilename(filetypes = [("Filestorage", "*.files")], initialdir = initialdir)
    else:
        if not os.path.exists(file):
            return
    if file:
        with open(file, mode = "rb") as infile:
            loaded = pickle.load(infile).__dict__
            current = root.selectFunction.fileStorage.__dict__
            if "mode" not in loaded or m.mode != loaded["mode"]:
                answ = messagebox.askyesno(message = ("Current mode does not correspond "
                                                      "with the loaded files.\n"
                                                      "Do you want to still load the files?"),
                                           icon = "question", title = "Proceed?")
                if not answ:
                    return
            for key in loaded:
                if key in current:
                    current[key] = loaded[key]
            current["lastSave"] = file
        root.checkProcessing()


def doesFileStorageRequiresSave(root, mode):
    """checks whether last save of filestorage is the same as current filestorage and whether
        filestorage contains anything for saving"""
    for key, value in m.fs[mode].__dict__.items():
        if value and key != "mode":
            break
    else:
        return False
    lastSave = m.fs[mode].lastSave
    if lastSave:
        with open(lastSave, mode = "rb") as infile:
            return m.fs[mode].__dict__ != pickle.load(infile).__dict__
    else:
        return True
    

class SetBatchTime(Toplevel):
    "toplevel window where time is chosen for batch processing of files with different times"
    def __init__(self, root):
        super().__init__(root)

        self.root = root
        placeWindow(self, 598, 208)
        self.title = "Set batch time"
        self.grab_set()
        self.focus_set()     
        self.resizable(False, False)

        self.batchTime = optionGet("LastBatchTime", "[(0, 20)]", "list")
        self.developer = optionGet("Developer", False, 'bool', True)
        self.manualChangeEnabled = self.developer

        # frames
        self.buttonFrame = ttk.Frame(self)
        self.splittingFrame = ttk.Frame(self)
        self.removeFrame = ttk.Frame(self)
        self.timeFrame = TimeFrame(self, observe = False)

        # buttons
        self.okBut = ttk.Button(self, text = "Ok", command = self.okFun)
        self.closeBut = ttk.Button(self, text = "Close", command = self.destroy)
        self.addBut = ttk.Button(self.buttonFrame, text = "Add", command = self.addFun, width = 8)
        self.removeLastBut = ttk.Button(self.removeFrame , text = "Remove last",
                                        command = self.removeLastFun)
        self.resetBut = ttk.Button(self.removeFrame , text = "Reset", command = self.resetFun)
        self.clearBut = ttk.Button(self.removeFrame , text = "Clear", command = self.clearFun)

        # splitting buttons
        self.split2 = ttk.Button(self.splittingFrame, text = "Split in 2",
                                 command = lambda: self.splitTime(2), width = 9)
        self.split3 = ttk.Button(self.splittingFrame, text = "Split in 3",
                                 command = lambda: self.splitTime(3), width = 9)
        self.split5 = ttk.Button(self.splittingFrame, text = "Split in 5",
                                 command = lambda: self.splitTime(5), width = 9)
        self.split2.grid(column = 0, row = 0)
        self.split3.grid(column = 0, row = 1)
        self.split5.grid(column = 0, row = 2)

        # text
        self.text = Text(self, height = 5, wrap = "word", width = 73)
        self.text.insert("1.0", str(self.batchTime))
        self.text.bind("<3>", lambda e: self.popUp(e))
        if not self.developer:
            self.text["state"] = "disabled"
            self.text["background"] = self._color()
        else:
            self.addBut["state"] = "disabled"
            self.split2["state"] = "disabled"
            self.split3["state"] = "disabled"
            self.split5["state"] = "disabled"
            self.removeLastBut["state"] = "disabled"
            
        # adding to grid
        self.buttonFrame.grid(column = 1, row = 0, sticky = W, pady = 2)
        self.splittingFrame.grid(column = 2, row = 0, pady = 2, sticky = W)
        self.removeFrame.grid(column = 3, row = 0, pady = 3)
        self.timeFrame.grid(column = 0, row = 0)
        
        self.okBut.grid(column = 3, row = 2, pady = 2)
        self.closeBut.grid(column = 2, row = 2, pady = 2)
        self.addBut.grid(column = 0, row = 2, columnspan = 2, sticky = EW)
        self.removeLastBut.grid(column = 0, row = 0, pady = 0)
        self.resetBut.grid(column = 0, row = 1, pady = 2)
        self.clearBut.grid(column = 0, row = 2, pady = 0)

        self.text.grid(column = 0, row = 1, columnspan = 4, pady = 5, padx = 5)

        # +x buttons
        ttk.Button(self.buttonFrame, text = "+1", command = lambda: self.addTime(1),
                   width = 4).grid(column = 0, row = 0)
        ttk.Button(self.buttonFrame, text = "+2", command = lambda: self.addTime(2),
                   width = 4).grid(column = 1, row = 0)
        ttk.Button(self.buttonFrame, text = "+5", command = lambda: self.addTime(5),
                   width = 4).grid(column = 0, row = 1)
        ttk.Button(self.buttonFrame, text = "+10", command = lambda: self.addTime(10),
                   width = 4).grid(column = 1, row = 1)
        

    def _color(self):
        return "grey94"
        
    def okFun(self):
        "closes the window and saves the selected batch time to root's batch time"
        if not self._checkText():
            return
        self.root.selectedBatchTime = self.batchTime
        optionWrite("LastBatchTime", self.batchTime)            
        self.destroy()

    def addFun(self):
        "adds selected time to the text widget as well as to the selected batch time"
        try:
            start = int(self.timeFrame.startTimeVar.get())
        except ValueError:
            start = float(self.timeFrame.startTimeVar.get())
        try:
            end = int(self.timeFrame.timeVar.get())
        except ValueError:
            end = float(self.timeFrame.timeVar.get())     
        newTime = (start, end)
        self.batchTime.append(newTime)
        self._updateText()

    def _updateText(self):
        "updates the text widget"
        state = self.text["state"]
        self.text["state"] = "normal"
        self.text.delete("1.0", "end")
        self.text.insert("1.0", str(self.batchTime))
        self.text["state"] = state

    def removeLastFun(self):
        "removes the last added time"
        if self.batchTime:
            self.batchTime.pop()
        self._updateText() 

    def resetFun(self):
        "resets the text to last batch time used (obtained from options)"
        self.batchTime = optionGet("LastBatchTime", "[(0, 20)]", "list")
        self._updateText()

    def clearFun(self):
        "clears the text"
        self.batchTime = []
        self._updateText()

    def popUp(self, event):
        "pop-up menu for text widget"
        menu = Menu(self, tearoff = 0)
        if self.manualChangeEnabled:
            menu.add_command(label = "Disable manual change", command = self.disableManualChange)
        else:
            menu.add_command(label = "Enable manual change", command = self.enableManualChange)
        menu.post(event.x_root, event.y_root)

    def enableManualChange(self):
        "enables manual text changes"
        self.manualChangeEnabled = True
        self.text["state"] = "normal"
        self.text["background"] = "white"
        self.addBut["state"] = "disabled"
        self.split2["state"] = "disabled"
        self.split3["state"] = "disabled"
        self.split5["state"] = "disabled"
        self.removeLastBut["state"] = "disabled"

    def _checkText(self):
        "checks whether the text is in right format"
        try:
            self.batchTime = eval(self.text.get('1.0', 'end'))
            if not isinstance(self.batchTime, list):
                raise Exception("Selected time must be a list.")
            for pair in self.batchTime:
                if not isinstance(pair, tuple):
                    raise Exception("{} is not a tuple.".format(pair))
                if len(pair) != 2:
                    raise Exception("{} has more than two items (needs exactly two).".format(pair))
                if not isinstance(pair[0], int) and not isinstance(pair[0], float):
                    raise Exception("{} is not an integer or float.".format(pair[0]))
                if not isinstance(pair[1], int) and not isinstance(pair[1], float):
                    raise Exception("{} is not an integer or float.".format(pair[1]))
                if pair[0] >= pair[1]:
                    raise Exception("The first item in every pair must be lower than the second.")
        except Exception as e:
            messagebox.showinfo(message = "There is an error in the selected batch time.\n"
                                "Correct it or use Reset or Clear buttons.", detail = e,
                                title = "Error in selected time", icon = "error")
            return False
        else:
            return True
        
    def disableManualChange(self):
        "disables manual text changes"
        if not self._checkText():
            return
        self.manualChangeEnabled = False
        self.text["state"] = "disabled"
        self.text["background"] = self._color()
        self.addBut["state"] = "normal"
        self.split2["state"] = "normal"
        self.split3["state"] = "normal"
        self.split5["state"] = "normal"
        self.removeLastBut["state"] = "normal"

    def addTime(self, x):
        "adds time to start and stop time in timeFrame"
        start = int(self.timeFrame.startTimeVar.get()) + x
        end = int(self.timeFrame.timeVar.get()) + x
        self.timeFrame.startTimeVar.set(str(start))
        self.timeFrame.timeVar.set(str(end))

    def splitTime(self, x):
        "splits all time bins in x new bins"
        newSlots = []
        for slot in self.batchTime:
            start = Decimal(slot[0])
            end = Decimal(slot[1])
            diff = (end - start) / x
            for i in range(x):
                newSlots.append((start + i*diff, start + (i+1)*diff))
        self.batchTime = [(self._roundDecimal(slot[0]),
                           self._roundDecimal(slot[1])) for slot in newSlots]
        self._updateText()

    def _roundDecimal(self, d):
        "helper function for splitTime"
        if d == round(d):
            return int(d)
        else:
            return round(float(d), 3)


def addTags(root):
    "adds tags to files loaded from a text file"
    # currently is not safe to possible problems
    infile = askopenfilename(filetypes = [("Text", "*.txt")], initialdir = os.getcwd())
    with open(infile) as f:
        for line in f:
            basename = os.path.basename(line.split()[0].strip())
            for arenafile in m.fs[m.mode]:
                if os.path.basename(arenafile) == basename:
                    if arenafile not in m.fs[m.mode].tagged:
                        m.fs[m.mode].tagged.append(arenafile)
                    break
    root.checkProcessing()
                    
        
       







    




