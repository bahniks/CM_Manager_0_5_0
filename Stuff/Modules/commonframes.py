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

from tkinter.filedialog import asksaveasfilename
from tkinter import *
from os.path import basename
from tkinter import ttk
from collections import defaultdict
import os.path
import os


from optionget import optionGet
import mode as m


class TimeFrame(ttk.Frame):
    "frame containing entries for choosing starting and stopping time"
    instances = defaultdict(list)
    start = {}
    stop = {}
    
    def __init__(self, root, onChange = False, observe = True, loadtime = True):
        super().__init__(root)
        if m.mode not in TimeFrame.start:
            TimeFrame.start[m.mode] = optionGet("DefStartTime", 0, ['int', 'float'])
        if m.mode not in TimeFrame.stop:
            TimeFrame.stop[m.mode] = optionGet("DefStopTime", m.time[m.mode], ['int', 'float'])
        
        if observe:
            TimeFrame.instances[m.mode].append(self)
        self.observe = observe

        self.root = root
        self.onChange = onChange

        # variables
        self.timeVar = StringVar()
        self.startTimeVar = StringVar()

        if loadtime:
            self.startTimeVar.set(TimeFrame.start[m.mode])
            self.timeVar.set(TimeFrame.stop[m.mode])            
        else:
            self.startTimeVar.set(optionGet("DefStartTime", 0, ['int', 'float']))  
            self.timeVar.set(optionGet("DefStopTime", m.time[m.mode], ['int', 'float']))                  

        # labels
        self.startTimeLab = ttk.Label(self, text = "Start time:")
        self.timeLab = ttk.Label(self, text = "Stop time:")
        self.minutesLab = ttk.Label(self, text = "minutes")
        self.minutesLab2 = ttk.Label(self, text = "minutes")

        # entry validation
        vcmdTotal = (root.register(self.validateTotal), "%P")
        vcmdStart = (root.register(self.validateStart), "%P")

        # entries
        self.totalTime = ttk.Entry(self, textvariable = self.timeVar, width = 5, justify = "right",
                                   validate = "focusout", validatecommand = vcmdTotal)
        self.startTime = ttk.Entry(self, textvariable = self.startTimeVar, width = 5,
                                   justify = "right", validate = "focusout",
                                   validatecommand = vcmdStart)

        # adding to grid
        self.startTimeLab.grid(column = 0, row = 0, sticky = (N, S, E))
        self.timeLab.grid(column = 0, row = 1, sticky = (N, S, E))
        self.minutesLab.grid(column = 2, row = 0, sticky = (N, S, W))
        self.minutesLab2.grid(column = 2, row = 1, sticky = (N, S, W))

        self.totalTime.grid(column = 1, row = 1, sticky = (N, S, W), padx = 3, pady = 2)
        self.startTime.grid(column = 1, row = 0, sticky = (N, S, W), padx = 3, pady = 2)


    def _isfloat(self, value):
        "checks whether a value can be float"
        try:
            float(value)
            return True
        except Exeption:
            return False

    def validateTotal(self, newValue):
        "validation of total time - checks if new entry is digits only"
        if not self._isfloat(newValue) or eval(newValue) <= eval(self.startTimeVar.get()):
            t = max([optionGet("DefStopTime", m.time[m.mode], ['int', 'float']),
                     eval(self.startTimeVar.get()) + 1])
            self.timeVar.set(str(t))
            self.bell()
        elif self.onChange:
                self.root.root.setTime()
        if self.observe:
            for tf in TimeFrame.instances[m.mode]:
                tf.timeVar.set(self.timeVar.get())
            TimeFrame.stop[m.mode] = self.timeVar.get()
        return True

    def validateStart(self, newValue):
        "validation of start time - checks if new entry is digits only"
        if not self._isfloat(newValue) or eval(newValue) >= eval(self.timeVar.get()):
            t = min([optionGet("DefStartTime", 0, ['int', 'float']),
                     eval(self.timeVar.get()) - 1])
            self.startTimeVar.set(str(t))
            self.bell()
        elif self.onChange:
            self.root.root.setTime()
        if self.observe:
            for tf in TimeFrame.instances[m.mode]:
                tf.startTimeVar.set(self.startTimeVar.get())
            TimeFrame.start[m.mode] = self.startTimeVar.get()
        return True

    def changeState(self, state):
        "changes state for time entries"
        for child in (self.totalTime, self.startTime):
            child.configure(state = state)


class SaveToFrame(ttk.Frame):
    "frame containing save to entry, browse button, and optionaly 'Save results to:' label"
    def __init__(self, root, label = True, parent = None):
        super().__init__(root)

        self.root = root
        self.parent = parent
        self.saveToVar = StringVar()
        self.columnconfigure(1, weight = 1)
        
        vcmd = (root.register(self.processOn), "%P") # calls processOn method upon change of entry

        # widgets
        self.browse = ttk.Button(self, text = "Browse", command = self.saveAs)        
        self.saveTo = ttk.Entry(self, textvariable = self.saveToVar, validate = "all",\
                                validatecommand = vcmd)
        
        self.browse.grid(column = 2, row = 1, sticky = E, padx = 3)     
        self.saveTo.grid(column = 0, row = 1, columnspan = 2, sticky = (E, W), padx = 2, pady = 2)
        
        if label:
            self.saveToLab = ttk.Label(self, text = "Save results to:")
            self.saveToLab.grid(column = 0, row = 0, columnspan = 2, sticky = (S, W), padx = 2,
                                pady = 1)  
        
    def saveAs(self):
        "asks user to select file where to save output"
        self.saveToVar.set(asksaveasfilename(initialdir = optionGet("ResultDirectory", os.getcwd(),
                                                                    "str", True),
                                             defaultextension =
                                             optionGet("DefProcessOutputFileType", ".txt",
                                                       "str", True)[1:]))
        if self.parent == "processor":
            if self.root.root.fileStorage.arenafiles and self.saveToVar.get():
                self.root.process.state(["!disabled"])              


    def processOn(self, content):
        "decides whether it's possible to process file when changing output file with entry"
        if self.parent == "processor": 
            if content != "" and self.root.root.fileStorage.arenafiles != []:
                self.root.process.state(["!disabled"])               
            elif content == "":
                self.root.process.state(["disabled"])               
            
        return True
            



def returnName(filename, allFiles):
    "depending on option 'SaveFullPath' returns full name of basename"
    selected = optionGet("SaveFullPath", "Basename", "str", True)
    if selected == "Unique path":
        sharedName = os.path.split(os.path.commonprefix(allFiles))[0]
        return filename[len(sharedName):].lstrip("/\\")
    elif selected == "Full path":
        return filename
    else:
        return basename(filename)
