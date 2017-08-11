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
from time import time
from math import cos, sin, radians, degrees, atan2, floor


import os
import os.path


from showtracks import ShowTracks
from filestorage import FileStorageFrame
from commonframes import TimeFrame, returnName
from image import svgSave, ImagesOptions
from processor import ProgressWindow
from optionget import optionGet
from graphs import getGraphTypes, Graphs, SvgGraph, SpeedGraph, DistanceFromCenterGraph
from graphs import AngleGraph, DistanceFromPlatformGraph, DistanceFromRobotGraph
from comment import Comment, commentColor
import mode as m


class Explorer(ttk.Frame):
    "represents ''Explore' page in the main window notebook"
    def __init__(self, root):
        super().__init__(root)

        self["padding"] = (10, 10, 12, 12)

        self.animate = "stop"
        self.initialized = False
        self.root = root
        self.fileStorage = self.root.fileStorage

        # variables
        self.status = StringVar()
        self.curTime = DoubleVar()
        self.speed = DoubleVar()
        self.graphTypeVar = StringVar()
        self.distanceVar = StringVar()
        self.entrancesVar = StringVar()
        self.selectedPVar = StringVar()
        self.selectedParameter = StringVar()
        self.graphParameter = StringVar()
        self.timeVar = StringVar()
        self.totDistanceVar = StringVar()
        self.totEntrancesVar = StringVar()
        self.totSelectedPVar = StringVar()
        self.showTrackVar = BooleanVar()
        self.removeReflectionsVar = BooleanVar()
        self.showShocksVar = BooleanVar()
        self.showTailVar = BooleanVar()
        self.saveWhatVar = StringVar()
        self.saveWhichFilesVar = StringVar()

        self.curTime.set(0)
        self.speed.set(1.0)
        self.graphTypeVar.set("SpeedGraph(self)")
        self.showTrackVar.set(False)
        self.removeReflectionsVar.set(False)
        self.showShocksVar.set(True)
        self.showTailVar.set(False)
        self.saveWhatVar.set("all")
        self.saveWhichFilesVar.set("current")
        self.selectedParameter.set("")
        self.graphParameter.set("nothing")
        
        
        # frames
        self.controlsLF = ttk.Labelframe(self, text = "Controls")
        self.graphLF = ttk.Labelframe(self, text = "Graph")
        self.fileStorageFrame = FileStorageFrame(self, parent = "explorer")
        self.fileFrame = FileFrame(self)
        self.parametersLF = ttk.LabelFrame(self, text = "Parameters")
        self.timeLabFrame = ttk.Labelframe(self, text = "Time")
        self.timeLabFrame.root = self
        self.timeFrame = TimeFrame(self.timeLabFrame, onChange = True)
        if m.mode in ("CM", "KT"):
            arenaText = "Arena frame"
        elif m.mode == "RA":
            arenaText = "Room frame"
        else:
            arenaText = "Animation"
        self.arenaFrame = ttk.LabelFrame(self, text = arenaText)
        if m.mode in ("CM", "KT"):
            roomText = "Room frame"
        elif m.mode == "RA":
            roomText = "Robot frame"
        else:
            roomText = "Track"
        self.roomFrame = ttk.LabelFrame(self, text = roomText)
        self.speedScaleFrame = ttk.Frame(self)
        self.speedScaleFrame.rowconfigure(0, weight = 1)
        self.optionsLF = ttk.LabelFrame(self, text = "Options")
        self.saveImagesLF = ttk.LabelFrame(self, text = "Save image(s)")
        
        # canvases
        self.arenaCanv = Canvas(self.arenaFrame, background = "white", height = 300, width = 300)
        self.roomCanv = Canvas(self.roomFrame, background = "white", height = 300, width = 300)

        # buttons
        self.playBut = ttk.Button(self.controlsLF, text = "Play", command = self.playFun,
                                  state = "disabled")
        self.pauseBut = ttk.Button(self.controlsLF, text = "Pause", command = self.pauseFun,
                                   state = "disabled")
        self.stopBut = ttk.Button(self.controlsLF, text = "Stop", command = self.stopFun,
                                  state = "disabled")
        self.saveBut = ttk.Button(self.saveImagesLF, text = "Save", command = self.saveImages,
                                  state = "disabled")
        self.optionBut = ttk.Button(self.saveImagesLF, text = "Options",
                                    command = self.imagesOptions)

        # checkbuttons
        self.removeReflections = ttk.Checkbutton(self.optionsLF, text = "Remove reflections",
                                                 variable = self.removeReflectionsVar,
                                                 command = self.toggleReflections)       
        self.showShocks = ttk.Checkbutton(self.optionsLF, text = "Show shocks",
                                          variable = self.showShocksVar,
                                          command = self.toggleShocks)
        self.showTail = ttk.Checkbutton(self.optionsLF, text = "Show tail",
                                        variable = self.showTailVar, command = self.toggleTail)

        # radiobutton
        self.showTrack = ttk.Radiobutton(self.optionsLF, text = "Show track",
                                         variable = self.showTrackVar, value = True,
                                         command = self.toggleAnimation)
        self.showAnimation = ttk.Radiobutton(self.optionsLF, text = "Show animation",
                                             variable = self.showTrackVar, value = False,
                                             command = self.toggleAnimation)
        
        
        # label
        self.statusBar = ttk.Label(self, textvariable = self.status)
        self.distance = ttk.Label(self.parametersLF, textvariable = self.distanceVar, width = 10,
                                  anchor = "e")
        self.entrances = ttk.Label(self.parametersLF, textvariable = self.entrancesVar, width = 13,
                                   anchor = "e")
        self.selectedP = ttk.Label(self.parametersLF, textvariable = self.selectedPVar, width = 13,
                                   anchor = "e")
        self.timePar = ttk.Label(self.parametersLF, textvariable = self.timeVar, width = 13,
                                 anchor = "e")
        self.totDistance = ttk.Label(self.parametersLF, textvariable = self.totDistanceVar,
                                     width = 10, anchor = "e")
        self.totEntrances = ttk.Label(self.parametersLF, textvariable = self.totEntrancesVar,
                                     width = 10, anchor = "e")
        self.totSelectedP = ttk.Label(self.parametersLF, textvariable = self.totSelectedPVar,
                                     width = 10, anchor = "e")
        self.distanceLab = ttk.Label(self.parametersLF, text = "Distance [m]", width = 11,
                                     anchor = "w")
        self.entrancesLab = ttk.Label(self.parametersLF, text = "Entrances", width = 11,
                                      anchor = "w")
        self.selectedPLab = ttk.Label(self.parametersLF, text = "Selected", width = 11,
                                      anchor = "w")
        self.timeLab = ttk.Label(self.parametersLF, text = "Time", width = 11, anchor = "w")
        self.currentLab = ttk.Label(self.parametersLF, text = "Current", width = 10,
                                    anchor = "e")
        self.totalLab = ttk.Label(self.parametersLF, text = "Total", width = 10,
                                  anchor = "e")
        self.saveWhatLab = ttk.Label(self.saveImagesLF, text = "Save")
        self.saveWhichFilesLab = ttk.Label(self.saveImagesLF, text = "File(s)")

        # scales
        self.timeSc = ttk.Scale(self, orient = HORIZONTAL, from_ = 0, to = 100,
                                variable = self.curTime, command = self.changedTime)
        self.speedSc = ttk.Scale(self.speedScaleFrame, orient = VERTICAL, from_ = 50, to = 0.5,
                                 variable = self.speed, command = self.changedSpeed)
        
        # entry
        self.speedEntry = ttk.Entry(self.speedScaleFrame, textvariable = self.speed, width = 4,
                                    justify = "right", state = "readonly")
        
        # graph
        self.graph = eval(self.graphTypeVar.get())
        self.graph.bind("<Button-1>", self.graphClick)
        self.graph.bind("<Button-3>", self.graphPopUp)

        # combobox
        self.saveWhatCombo = ttk.Combobox(self.saveImagesLF, textvariable = self.saveWhatVar,
                                          justify = "center", width = 15, state = "readonly")
        self.saveWhatCombo["values"] = ("arena frame", "room frame", "both frames",
                                        "graph", "all")
        self.saveWhichFilesCombo = ttk.Combobox(self.saveImagesLF, textvariable =
                                                self.saveWhichFilesVar, justify = "center",
                                                width = 15, state = "readonly")
        self.saveWhichFilesCombo["values"] = ("current", "tagged", "untagged", "all")

        # adding to grid        
        self.controlsLF.grid(column = 0, row = 3, columnspan = 2, sticky = (N, W), pady = 2,
                             padx = 2)
        self.graphLF.grid(column = 0, row = 5, columnspan = 1, pady = 2, padx = 2, sticky = (N, W))
        self.fileStorageFrame.grid(column = 8, row = 0, pady = 2, padx = 3, sticky = (N, E))
        self.fileFrame.grid(column = 8, row = 1, rowspan = 4, padx = 3, sticky = (N, S))
        self.parametersLF.grid(column = 3, row = 3, columnspan = 4, sticky = (E, W))
        self.timeLabFrame.grid(column = 1, row = 5, columnspan = 4, sticky = (N, W),
                               pady = 2, padx = 2)        
        self.timeFrame.grid(column = 0, row = 0)
        self.arenaFrame.grid(column = 0, row = 0, rowspan = 2, columnspan = 3,
                             sticky = (N, S, W), padx = 2, pady = 2)
        self.roomFrame.grid(column = 3, row = 0, rowspan = 2, columnspan = 4,
                            sticky = (N, S, E), padx = 2, pady = 2)
        self.speedScaleFrame.grid(column = 7, row = 0, rowspan = 2, sticky = (N, S), padx = 4,
                                  pady = 2)
        self.optionsLF.grid(column = 5, row = 5, columnspan = 2, sticky = (N), padx = 2)
        self.saveImagesLF.grid(column = 8, row = 5, sticky = (S), pady = 5)
        
        self.arenaCanv.grid(column = 0, row = 0, padx = 1, pady = 1)
        self.roomCanv.grid(column = 0, row = 0, padx = 1, pady = 1)
        self.graph.grid(column = 0, row = 4, columnspan = 7, padx = 2, pady = 5)
        
        self.playBut.grid(column = 0, row = 0, sticky = (N, S), padx = 2, pady = 2)
        self.pauseBut.grid(column = 1, row = 0, sticky = (N, S), padx = 2, pady = 2)
        self.stopBut.grid(column = 2, row = 0, sticky = (N, S), padx = 2, pady = 2)
        self.saveBut.grid(column = 2, row = 2, sticky = E)
        self.optionBut.grid(column = 0, row = 2, sticky = W, columnspan = 2)

        self.removeReflections.grid(column = 1, row = 0, padx = 3, pady = 2, sticky = (N, W))
        self.showTail.grid(column = 1, row = 2, padx = 3, pady = 2, sticky = (N, W))

        if m.files == "pair" or m.mode == "KT":
            self.showShocks.grid(column = 1, row = 1, padx = 3, pady = 2, sticky = (N, W))
            self.showAnimation.grid(column = 0, row = 0, padx = 2, pady = 1, sticky = (N, W))
            self.showTrack.grid(column = 0, row = 1, padx = 2, pady = 1, sticky = (N, W))
        
        self.speedEntry.grid(column = 0, row = 1)

        self.statusBar.grid(column = 0, row = 6, columnspan = 9, sticky = (S, E, W), padx = 2,
                       pady = 4)
        self.distance.grid(column = 1, row = 1, sticky = E)
        self.entrances.grid(column = 1, row = 2, sticky = E)
        self.timePar.grid(column = 1, row = 4, sticky = E, padx = 2)
        self.selectedP.grid(column = 1, row = 3, sticky = E)
        self.totDistance.grid(column = 2, row = 1, sticky = E, padx = 4)
        self.totEntrances.grid(column = 2, row = 2, sticky = E, padx = 4)
        self.totSelectedP.grid(column = 2, row = 3, sticky = E, padx = 4)
        self.distanceLab.grid(column = 0, row = 1, sticky = E)
        self.entrancesLab.grid(column = 0, row = 2, sticky = E)
        self.selectedPLab.grid(column = 0, row = 3, sticky = E)
        self.timeLab.grid(column = 0, row = 4, sticky = E)
        self.currentLab.grid(column = 1, row = 0, sticky = E, padx = 2, pady = 2)
        self.totalLab.grid(column = 2, row = 0, sticky = E, padx = 4, pady = 2)
        self.saveWhatLab.grid(column = 0, row = 0, padx = 2, sticky = E)
        self.saveWhichFilesLab.grid(column = 0, row = 1, padx = 2, sticky = E)

        self.timeSc.grid(column = 0, row = 2, columnspan = 7, sticky = (E, W), pady = 4, padx = 2)
        self.speedSc.grid(column = 0, row = 0, sticky = (N, S, E, W), pady = 3)

        self.saveWhatCombo.grid(column = 1, row = 0, columnspan = 2)
        self.saveWhichFilesCombo.grid(column = 1, row = 1, columnspan = 2)

        # statusBar binding
        self.statusBar.bind("<Double-1>", self._statusBarDoubleclick)

        # parametersLF popUp menu bindings
        self.parametersLF.bind("<Button-3>", self.parametersPopUp)
        for child in self.parametersLF.winfo_children():
            child.bind("<Button-3>", self.parametersPopUp)       

        # checkbuttons for graph
        for number, gType in enumerate(getGraphTypes()):
            ttk.Radiobutton(self.graphLF, text = gType[0], variable = self.graphTypeVar,
                            command = self.changedGraph, value = gType[1])\
                            .grid(row = number, pady = 1, padx = 1, sticky = (W))

        # bindings
        self.bind("<Down>", lambda e: self.fileFrame.nextFun())
        self.bind("<Right>", lambda e: self.fileFrame.nextFun())
        self.bind("<Left>", lambda e: self.fileFrame.previousFun())
        self.bind("<Up>", lambda e: self.fileFrame.previousFun())
        self.bind("<x>", lambda e: self.playBut.invoke())
        self.bind("<c>", lambda e: self.pauseBut.invoke())
        self.bind("<v>", lambda e: self.stopBut.invoke())
        for child in self.controlsLF.winfo_children():
            child.bind("<x>", lambda e: self.playBut.invoke())
            child.bind("<c>", lambda e: self.pauseBut.invoke())
            child.bind("<v>", lambda e: self.stopBut.invoke())            
        

    def imagesOptions(self):
        ImagesOptions(self)


    def saveImages(self):
        "saves images for selected files"
        files = self._returnSelectedFiles()

        if len(files) > 1:
            progress = ProgressWindow(self, len(files), text = "saved")
        elif len(files) == 1 and files[0]:
            self.root.config(cursor = m.wait)
            self.root.update()
        else:
            self.status.set("No file selected.")
            self.bell()
            return
       
        problems = 0
        for filename in files:
            #try:
            if filename in self.fileStorage.pairedfiles:
                cm = m.CL(filename, self.fileStorage.pairedfiles[filename])
            else:
                cm = m.CL(filename, "auto")
            if self.removeReflectionsVar.get():
                cm.removeReflections(points = self.fileStorage.reflections.get(filename, None))
            svgSave(cm, filename, self.saveWhatVar.get(), self)
            #except Exception:
            #    problems += 1

            if len(files) > 1:
                progress.addOne()

        if len(files) > 1:
            progress.destroy()
            if problems > 1:
                self.status.set("{} problems occured!".format(problems))
                self.bell()
            elif problems == 1:
                self.status.set("One problem occured!")
                self.bell()
            else:
                self.status.set("Images were saved.")
        else:
            if problems:
                self.status.set("A problem occured!")
                self.bell()
            else:
                self.status.set("Image was saved.")
            self.root.config(cursor = "")


    def _returnSelectedFiles(self):
        "returns files that are chosen for creating of images"
        which = self.saveWhichFilesVar.get()
        
        files = []
        if which == "all":
            files.extend(self.fileStorage.arenafiles)
        elif which == "tagged":
            files.extend(self.fileStorage.tagged)
        elif which == "untagged":
            files.extend([file for file in self.fileStorage if file not in
                          self.fileStorage.tagged])
        elif which == "current":
            files = [self.fileFrame.selected]

        return files
            

    def toggleAnimation(self):
        "called when checkbutton for showing tracks is toggled"
        if self.initialized:          
            self.initializeFile(self.fileFrame.selected, new = False, timeReset = False)
            if not self.showTrackVar.get():
                self.changedTime(value = self.curTime.get(), unit = "0-100")


    def toggleReflections(self):
        "called when reflections removal is changed - just refreshes canvases"
        if self.initialized:          
            if self.removeReflectionsVar.get():
                self.cm.removeReflections(points = self.fileStorage.reflections.get(self.cm.nameA,
                                                                                    None))
                self.initializeFile(self.fileFrame.selected, new = False, timeReset = False)
            else:
                self.initializeFile(self.fileFrame.selected, new = True, timeReset = False)
            if not self.showTrackVar.get():
                self.changedTime(value = self.curTime.get(), unit = "0-100")


    def toggleShocks(self):
        "called when checkbutton for showing shocks is toggled"
        if self.initialized and self.showTrackVar.get():
            self.initializeFile(self.fileFrame.selected, new = False, timeReset = False)


    def toggleTail(self):
        "called when checkbutton for showing tail is toggled"
        if self.initialized and not self.showTrackVar.get():
            if self.showTailVar.get():
                self.initializeFile(self.fileFrame.selected, new = False, timeReset = False)
                self.changedTime(value = self.curTime.get(), unit = "0-100")
            else:
                self.arenaCanv.delete("trailA")
                self.roomCanv.delete("trailR")            


    def playFun(self):
        "starts animation"        
        self.timeFrame.changeState("disabled")
        self.showTrack["state"] = "disabled"
        self.saveBut.state(["disabled"])
            
        self.animate = "" # status of the animation - '', 'pause', 'stop'
        
        prevTime = time()
        while not self.animate:
            # finds current time
            nowTime = time()
            difTime = (nowTime - prevTime) * 1000
            playTime = difTime * self.speed.get() + (
                self.curTime.get() * (self.maxTime - self.minTime) / 100) + self.minTime

            if playTime > self.maxTime:
                self.curTime.set(100)
                self.timeVar.set(self._timeFormat(self.maxTime))  
                self.animate = "stop"
                self.timeFrame.changeState("!disabled")
                self.showTrack["state"] = "!disabled"
                self.saveBut.state(["!disabled"])
                break

            self.changedTime(playTime, unit = "ms")

            prevTime = nowTime


    def changedTime(self, value, unit = "0-100"):
        "called when time is changed"
        if not self.initialized or self.minTime > self.maxTime or self.maxTime < self.minTime:
            return
        
        if unit == "ms":
            value = value
        else:
            value = ((float(value) * (self.maxTime - self.minTime)) / 100) + self.minTime
                  
        curLine = self._updateDefaultParameters(value)
        self._updateSelectedParameter(value)

        if self.showTailVar.get():
            self._createTail(curLine)                      

        Ax, Ay = curLine[self.cm.indices]
        Ax *= self.scale
        Ay *= self.scale

        if m.mode in ("CM", "KT"):
            Rx, Ry = curLine[2:4]
            Rx *= self.scale
            Ry *= self.scale
            self.roomCanv.coords("ratR", (Rx + 16, Ry + 16, Rx + 24, Ry + 24))
            self.roomCanv.lift("ratR")
        elif m.mode == "RA":
            Rx, Ry = curLine[2:4]
            Rx *= self.scale
            Ry *= self.scale
            self.arenaCanv.coords("robotA", (Rx + 12, Ry + 12, Rx + 28, Ry + 28))   
            self.roomCanv.coords("ratR", ((Ax - Rx)/2 + 146, (Ay - Ry)/2 + 146,
                                          (Ax - Rx)/2 + 154, (Ay - Ry)/2 + 154))
            r = self.cm.sectorRadius * self.scale
            self.arenaCanv.coords("shockZoneA", (Rx + 20 - r, Ry + 20 - r, Rx + 20 + r, Ry + 20 + r))
            self.arenaCanv.lift("robotA")
            self.arenaCanv.lift("shockZoneA")
            self.roomCanv.lift("ratR")

        self.arenaCanv.coords("ratA", (Ax + 16, Ay + 16, Ax + 24, Ay + 24))   
        self.arenaCanv.lift("ratA")

        self._setShockColor(curLine)

        self.graph.changedTime(value)

        # changes position of a time scale               
        if value < self.maxTime:
            self.curTime.set(((value - self.minTime) * 100) / (self.maxTime - self.minTime))
            self.timeVar.set(self._timeFormat(value))  
        else:
            self.curTime.set(100)
            self.timeVar.set(self._timeFormat(self.maxTime))          

        self.update()


    def _updateDefaultParameters(self, time):
        indices = self.cm.indices
        x0, y0 = self.cm.data[0][indices] 
        dist = 0
        entrances = 0
        prev = 0
        skip = 25 # z options
        start = self.cm.findStart(self.minTime / 60000)
        for row, content in enumerate(self.cm.data[start:]):
            if content[1] < time:
                # distance
                if row % skip == 0:
                    x1, y1 = content[indices]
                    diff = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
                    dist += diff
                    x0, y0 = x1, y1
                # entrances
                if content[5] != 2 and prev != 2:
                    continue
                elif content[5] != 2 and prev == 2:
                    if content[5] == 0: 
                        prev = 0
                    continue
                elif content[5] == 2 and prev == 2:
                    continue
                elif content[5] == 2 and prev != 2:
                    entrances += 1
                    prev = 2
                    continue
            else:
                curLine = content
                break
        dist = dist / (self.cm.trackerResolution * 100) # conversion from pixels to metres
        self.distanceVar.set("{:.1f}".format(dist))
        self.entrancesVar.set(entrances)
        return curLine


    def _updateSelectedParameter(self, time):
        if self.selectedParameter.get():
            time /= 60000
            startTime = self.minTime / 60000
            try:
                self.selectedPVar.set(self.computeSelected(self.cm, startTime, time))
            except Exception:
                self.selectedPVar.set("-")


    def _createTail(self, curLine):
        self.arenaCanv.delete("trailA")
        self.roomCanv.delete("trailR")
        if curLine[0] >= 10:
            end = curLine[0]
            adjust = 150 - self.cm.radius * self.scale
            start = end - 500 if end > 500 else 0
            start = round(start*2, -1) // 2
            if m.mode in ("CM", "KT"):
                trail = [tuple(content[2:4] + content[7:9]) for content in
                         self.cm.data[start:end:5]]
                arena = []
                room = []
                for rx, ry, ax, ay in trail:
                    arena.append((ax*self.scale + adjust, ay*self.scale + adjust))
                    room.append((rx*self.scale + adjust, ry*self.scale + adjust))
                arena.append((curLine[7]*self.scale + adjust, curLine[8]*self.scale + adjust))
                room.append((curLine[2]*self.scale + adjust, curLine[3]*self.scale + adjust))
                self.arenaCanv.create_line((arena), fill = "blue", width = 2, tag = "trailA")
                self.roomCanv.create_line((room), fill = "blue", width = 2, tag = "trailR")
            elif m.mode == "RA":
                self.arenaCanv.delete("trailRobot")
                trail = [tuple(content[2:4] + content[7:9]) for content in
                         self.cm.data[start:end:5]]
                ratA = []
                ratR = []
                robotA = []
                for rx, ry, ax, ay in trail:
                    ratA.append((ax*self.scale + adjust, ay*self.scale + adjust))
                    robotA.append((rx*self.scale + adjust, ry*self.scale + adjust))
                    ratR.append(((ax - rx)*self.scale / 2 + 150,
                                 (ay - ry)*self.scale / 2 + 150))
                ratA.append((curLine[7]*self.scale + adjust, curLine[8]*self.scale + adjust))
                robotA.append((curLine[2]*self.scale + adjust, curLine[3]*self.scale + adjust))
                ratR.append(((curLine[7] - curLine[2])*self.scale / 2 + 150,
                             (curLine[8] - curLine[3])*self.scale / 2 + 150))
                self.arenaCanv.create_line((ratA), fill = "blue", width = 2, tag = "trailA")
                self.roomCanv.create_line((ratR), fill = "blue", width = 2, tag = "trailR")
                self.arenaCanv.create_line((robotA), fill = "green", width = 2, tag = "trailRobot")
            else:
                trail = [tuple(content[2:4]) for content in self.cm.data[start:end:5]]
                arena = []
                for ax, ay in trail:
                    arena.append((ax*self.scale + adjust, ay*self.scale + adjust))
                arena.append((curLine[2]*self.scale + adjust, curLine[3]*self.scale + adjust))
                self.arenaCanv.create_line((arena), fill = "blue", width = 2, tag = "trailA")


    def _setShockColor(self, curLine):
        if (m.mode in ("CM", "KT") and curLine[6] > 0) or (m.mode == "MWM" and curLine[-1] > 0):
            self.roomCanv.itemconfigure("ratR", fill = "red", outline = "red")
            self.shock = True
        elif m.mode == "RA":
            if curLine[6] > 0:
                self.arenaCanv.itemconfigure("ratA", fill = "red", outline = "red")
                self.roomCanv.itemconfigure("ratR", fill = "red", outline = "red")
                self.shock = True
            else:
                self.arenaCanv.itemconfigure("ratA", fill = "black", outline = "black")
                self.roomCanv.itemconfigure("ratR", fill = "black", outline = "black")
                self.shock = False                
        else:
            self.roomCanv.itemconfigure("ratR", fill = "black", outline = "black")
            self.shock = False
            
            
    def setTime(self):
        "called when maximum or minimum time is set"
        if self.initialized:
            nowTime = (self.curTime.get() / 100) * (self.maxTime - self.minTime) + self.minTime
            self.initializeFile(self.fileFrame.selected, new = False)
            if self.minTime <= nowTime <= self.maxTime:
                self.graph.changedTime(nowTime)
                self.changedTime(nowTime, unit = "ms")
            elif self.minTime > nowTime:
                self.graph.changedTime(self.minTime)
                self.changedTime(self.minTime, unit = "ms")
            else:
                self.graph.changedTime(self.maxTime)
                self.changedTime(self.maxTime, unit = "ms")
            

    def pauseFun(self):
        "pauses and unpauses animation"
        if self.animate == "pause":
            self.timeFrame.changeState("disabled")
            self.showTrack["state"] = "disabled"
            self.saveBut.state(["disabled"])
            self.playFun()
        else:
            self.animate = "pause"
            self.timeFrame.changeState("!disabled")        
            self.showTrack["state"] = "!disabled"
            self.saveBut.state(["!disabled"])
            

    def stopFun(self):
        "stops animation"
        self.animate = "stop"
        self.changedTime(0)
        self.timeFrame.changeState("!disabled")          
        self.showTrack["state"] = "!disabled"
        self.saveBut.state(["!disabled"])
        

    def initializeFile(self, filename, new = True, timeReset = True):
        "initializes canvases, graph, etc."
        if new:
            successful = self._loadData(filename)
            if not successful:
                return

        self.scale = 130 / self.cm.radius
        self.shock = False

        self.arenaCanv.delete("all")
        self.roomCanv.delete("all")
        if m.mode != "OF":
            self.arenaCanv.create_oval(20, 20, 280, 280, outline = "black",
                                       width = 2, tags = "arenaAF")
            self.roomCanv.create_oval(20, 20, 280, 280, outline = "black",
                                      width = 2, tags = "arenaRF")
        else:
            self.arenaCanv.create_rectangle(20, 20, 280, 280, outline = "black",
                                            width = 2, tags = "arenaAF")
            self.roomCanv.create_rectangle(20, 20, 280, 280, outline = "black",
                                           width = 2, tags = "arenaRF")            

        if self.cm.centerAngle or m.mode == "RA":
            self._createShockSector()

        self.maxTime = min([self.cm.data[-1][1], eval(self.timeFrame.timeVar.get()) * 60000])
        self.minTime = max([self.cm.data[0][1], eval(self.timeFrame.startTimeVar.get()) * 60000])

        if self.showTrackVar.get() or (m.files != "pair" and m.mode != "KT"):
            self._drawTrack()
            
        if not self.showTrackVar.get() or (m.files != "pair" and m.mode != "KT"):
            self._initializeAnimation()

        self._setParameterDisplays(timeReset)

        self.graph.delete("all")
        if timeReset:
            self.graph.CM_loaded(self.cm, minTime = self.minTime, maxTime = self.maxTime)
        else:
            self.graph.CM_loaded(self.cm, minTime = self.minTime, maxTime = self.maxTime,
                                 initTime = (self.curTime.get() * (self.maxTime - self.minTime) /
                                             100 + self.minTime))

        self._changeButtonStatuses()
        self._showComment(filename)
        self.initialized = True       
        
        if new and timeReset:
            self.curTime.set(0)
            self.timeVar.set(self._timeFormat(self.minTime))  


    def _showComment(self, filename):
        if self.fileStorage.comments[filename]:
            comment = self.fileStorage.comments[filename].replace("\n", "\t")
            if len(comment) > 150:
                comment = comment[:149] + "(...)"
            self.status.set(comment)
        else:
            self.status.set("")


    def _statusBarDoubleclick(self, e):
        "opens comment window after doubleclick to status bar"
        if self.fileFrame.selected:
            Comment(self.fileFrame, self.fileFrame.selected, True)
            

    def _loadData(self, filename):
        try:
            if filename in self.fileStorage.pairedfiles:
                self.cm = m.CL(filename, self.fileStorage.pairedfiles[filename])
            else:
                self.cm = m.CL(filename, "auto")
            if self.removeReflectionsVar.get():
                self.cm.removeReflections(points = self.fileStorage.reflections.get(filename,
                                                                                    None))
        except Exception as e:
            if optionGet("Developer", False, 'bool', True):
                print(e)
            self.status.set("File failed to load!")
            self.bell()
            return False
        else:
            return True


    def _createShockSector(self):     
        if m.mode == "MWM":
            x = self.cm.platformX * self.scale + 20
            y = self.cm.platformY * self.scale + 20
            r = self.cm.platformRadius * self.scale
            self.arenaCanv.create_oval(x - r, y - r, x + r, y + r, outline = "red",
                                       width = 2, tags = "platformAF")
            self.roomCanv.create_oval(x - r, y - r, x + r, y + r, outline = "red",
                                      width = 2, tags = "platformRF")
        elif m.mode == "RA":
            r = self.cm.sectorRadius * self.scale / 2
            self.roomCanv.create_oval(150 - r, 150 - r, 150 + r, 150 + r, outline = "red",
                                      width = 2, tags = "shockZoneR")
            self.roomCanv.create_oval(142, 142, 158, 158, outline = "green3", fill = "green3",
                                      width = 2, tags = "robotR")            
        else:        
            self.angle = self.cm.centerAngle
            self.width = self.cm.width
            a1 = radians(self.angle - (self.width / 2))
            a2 = radians(self.angle + (self.width / 2))
            Sx1, Sy1 = 150 + (cos(a1) * 130), 150 - (sin(a1) * 130)
            Sx2, Sy2 = 150 + (cos(a2) * 130), 150 - (sin(a2) * 130)      
            self.roomCanv.create_line((Sx1, Sy1, 150, 150, Sx2, Sy2), fill = "red", width = 2,\
                                       tags = "shockZone")               

            
    def _drawTrack(self):
        if m.mode in ("CM", "RA", "KT"):
            data = [line[2:4] + line[6:9] for line in self.cm.data if
                    self.minTime <= line[1] <= self.maxTime]
            arena = []
            room = []
            prev = [-100, -100, 0, -100, -100]
            last = 0
            for count, line in enumerate(data):
                if abs(line[0] - prev[0]) + abs(line[1] - prev[1]) > 2 or count - last == 25 or\
                   line[2] > 0:
                    room.append(line[0:2])
                    arena.append(line[3:5])
                    last = count
                prev = line

            if m.mode in ("CM", "KT"):
                self.roomCanv.create_line(([i * self.scale + 20 for line in room for i in line]),
                                          fill = "black", width = 2)
            else:
                self.arenaCanv.create_line(([i * self.scale + 20 for line in room for i in line]),
                                           fill = "green", width = 2)
                self.roomCanv.create_line(([(i[0] - i[1]) * self.scale / 2 + 150 for line in
                                            zip(arena, room) for i in zip(line[0], line[1])]),
                                          fill = "black", width = 2)
                
            self.arenaCanv.create_line(([i * self.scale + 20 for line in arena for i in line]),
                                       fill = "black", width = 2)      
        else:
            displayThreshold = floor(3/self.scale)
            data = [line[2:4] for line in self.cm.data if self.minTime <= line[1] <= self.maxTime]
            points = []
            prev = [-100, -100, 0, -100, -100]
            last = 0
            for count, line in enumerate(data):
                if abs(line[0] - prev[0]) + abs(line[1] - prev[1]) > displayThreshold or count - last == 10:
                    points.append(line)
                    last = count
                prev = line
            self.roomCanv.create_line(([item*self.scale + 20 for line in points for item in line]),
                                      fill = "black", width = 2)
        if m.mode in ("CM", "RA", "KT"):
            if self.showShocksVar.get():
                indices = slice(2,4) if m.mode in ("CM", "KT") else slice(7,9)
                fun = self.roomCanv.create_oval if m.mode in ("CM", "KT") else self.arenaCanv.create_oval
                
                shocks = [line[indices] for count, line in enumerate(self.cm.data) if
                          self.minTime <= line[1] <= self.maxTime and line[self.cm.shockIndex] > 0 and
                          self.cm.data[count - 1][self.cm.shockIndex] <= 0]
                for shock in shocks:
                    fun(shock[0]*self.scale + 16, shock[1]*self.scale + 16,
                        shock[0]*self.scale + 24, shock[1]*self.scale + 24,
                        outline = "red", width = 3)   
            

    def _initializeAnimation(self):
        # initial position
        for line in self.cm.data:
            if line[1] < self.minTime:
                continue                       
            else:
                curLine = line
                break
        else:
            self.status.set("Invalid start time set.")
            self.bell()
            return
        
        # makes 'the rat' (i.e. two black points)
        if m.files == "pair" or m.mode == "KT":            
            Rx, Ry = curLine[2:4]
            Rx *= self.scale
            Ry *= self.scale
            
        Ax, Ay = curLine[self.cm.indices]
        Ax *= self.scale
        Ay *= self.scale

        if self.showTailVar.get():
            self.arenaCanv.create_line((Ax + 19, Ay + 19, Ax + 21, Ay + 21), fill = "blue",
                                       width = 2, tag = "trailA")
            
        if m.mode in ("CM", "KT"):
            if self.showTailVar.get():
                self.roomCanv.create_line((Rx + 19, Ry + 19, Rx + 21, Ry + 21),
                                          fill = "blue", width = 2, tag = "trailR")   
            self.roomCanv.create_oval(Rx + 16, Ry + 16, Rx + 24, Ry + 24,
                                       fill = "black", tags = "ratR")
        elif m.mode == "RA":
            self.roomCanv.create_oval((Ax - Rx)/2 + 146, (Ay - Ry)/2 + 146,
                                      (Ax - Rx)/2 + 154, (Ay - Ry)/2 + 154,
                                       fill = "black", tags = "ratR")            
            self.arenaCanv.create_oval(Rx + 12, Ry + 12, Rx + 28, Ry + 28, outline = "green3",
                                       fill = "green3", tags = "robotA")
            r = self.cm.sectorRadius * self.scale
            self.arenaCanv.create_oval(Rx + 20 - r, Ry + 20 - r, Rx + 20 + r, Ry + 20 + r,
                                       outline = "red", tags = "shockZoneA", width = 2)
            
        self.arenaCanv.create_oval(Ax + 16, Ay + 16, Ax + 24, Ay + 24,
                                   fill = "black", tags = "ratA")
                                             
        self._setShockColor(curLine)
                

    def _setParameterDisplays(self, timeReset):
        self.totDistanceVar.set(self.cm.getDistance(time = self.maxTime / 60000,
                                                    startTime = self.minTime / 60000))
        self.totEntrancesVar.set(self.cm.getEntrances(time = self.maxTime / 60000,
                                                      startTime = self.minTime / 60000))

        if self.selectedParameter.get():
            time = self.maxTime / 60000
            startTime = self.minTime / 60000
            self.totSelectedPVar.set(self.computeSelected(self.cm, startTime, time))
        else:
            self.totSelectedPVar.set("-")

        if timeReset:
            self.distanceVar.set("0.0")
            self.entrancesVar.set("0")
            self.selectedPVar.set("-")


    def _changeButtonStatuses(self):
        if not self.showTrackVar.get():
            self.playBut.state(["!disabled"])
            self.pauseBut.state(["!disabled"])
            self.stopBut.state(["!disabled"])
            self.timeSc.state(["!disabled"])
        else:
            self.playBut.state(["disabled"])
            self.pauseBut.state(["disabled"])
            self.stopBut.state(["disabled"])
            self.timeSc.state(["disabled"])

       
    def changedGraph(self):
        "called when the graph is changed"
        self.graph.delete("all")
        drawnParameter = self.graph.drawnParameter
        self.graph = eval(self.graphTypeVar.get())
        self.graph.drawnParameter = drawnParameter
        self.graph.grid(column = 0, row = 4, columnspan = 7, padx = 2, pady = 5)
        self.graph.bind("<Button-1>", self.graphClick)
        self.graph.bind("<Button-3>", self.graphPopUp)
        if self.initialized:
            self.graph.CM_loaded(self.cm, minTime = self.minTime, maxTime = self.maxTime,
                                 initTime = ((self.curTime.get() * (self.maxTime - self.minTime) /
                                              100) + self.minTime))
            

    def graphClick(self, event):
        "changes time when the graph is clicked upon"
        if self.initialized and not self.showTrackVar.get():
            self.graph.coords("timeMeasure", (event.x, 0, event.x, self.graph.height))
            time = (event.x * 100) / self.graph.width
            if time > 100:
                time = 100           
            self.changedTime(time)


    def graphPopUp(self, event):
        "shows menu for selection of parameter to be shown in graph"
        if not self.initialized:
            return
        
        menu = Menu(self, tearoff = 0)
        parameters = {"CM": ("periodicity", "mobility", "immobility", "entrances", "shocks",
                             "bad points", "thigmotaxis", "strategies"),
                      "MWM": ("mobility", "immobility", "bad points", "thigmotaxis", "passes"),
                      "OF": ("mobility", "immobility", "bad points", "thigmotaxis"),
                      "RA": ("mobility", "immobility", "entrances", "shocks", "bad points",
                             "thigmotaxis"),
                      "KT": ("periodicity", "mobility", "immobility", "entrances", "shocks",
                             "bad points", "thigmotaxis", "strategies")}
        parameters["CMSF"] = parameters["CM"]

        for parameter in parameters[m.mode]:
            menu.add_radiobutton(label = "Show {}".format(parameter),
                                 variable = self.graphParameter, value = parameter,
                                 command = lambda: self.graph.drawParameter(
                                     self.cm, self.graphParameter.get()))
        
        menu.add_separator()
        menu.add_radiobutton(label = "Don't show anything",
                             variable = self.graphParameter, value = "nothing",
                             command = lambda: self.graph.drawParameter(self.cm, ""))
        menu.post(event.x_root, event.y_root)        


    def parametersPopUp(self, event):
        "shows menu for selection of parameters to be shown in parameters frame"      
        menu = Menu(self, tearoff = 0)
        notAvailable = ["Total distance", "Entrances", "Time in sectors", "Time in quadrants",
                        "Strategies"]
        available = ["Bad points", "Outside points", "Reflections"]
        menu.add_radiobutton(label = "Don't show anything",
                             variable = self.selectedParameter, value = "nothing",
                             command = self._changedSelectedParameter)
        menu.add_separator()
        for name, par in m.parameters.items():
            if par.group not in ["info", "custom"] and name not in notAvailable or name in available:
                menu.add_radiobutton(label = 'Show {}'.format(name.lower()),
                                     variable = self.selectedParameter, value = name,
                                     command = self._changedSelectedParameter)
        menu.post(event.x_root, event.y_root)


    def _changedSelectedParameter(self):
        "called when selected parameter is changed"
        if self.selectedParameter.get() == "nothing":
            self.selectedParameter.set("")
            self.totSelectedPVar.set("-")
            self.selectedPVar.set("-")
            self.note.unbind_widget(self.selectedPLab)           
        else:
            selected = self.selectedParameter.get()
            name = selected
            if len(name) > 13:
                mapping = {"Maximum": "Max.",
                           "Mean": "M",
                           "Time": "t.",
                           "time": "t.",
                           "Circular": "Circ.",
                           "variance": "var.",
                           "points": "pts."
                           }
                for key, value in mapping.items():
                    name = name.replace(key, value)
                if len(name) > 13:
                    name = name[:10] + "..."
            self.selectedPLab["text"] = name
            
            def createSelectedFun(method, **options):
                def selectedFun(obj, start, stop):
                    return getattr(obj, method)(startTime = start, time = stop, **options)
                return selectedFun

            par = m.parameters[selected]
            options = {name: optionGet(*option[0]) for name, option in par.options.items()}
            self.computeSelected = createSelectedFun(par.method, **options)
            
            if self.initialized:
                time = self.maxTime / 60000
                startTime = self.minTime / 60000
                self.totSelectedPVar.set(self.computeSelected(self.cm, startTime, time))
                nowTime = (self.curTime.get() / 100) * (self.maxTime - self.minTime) + self.minTime
                time = nowTime / 60000
                try:
                    self.selectedPVar.set(self.computeSelected(self.cm, startTime, time))
                except Exception:
                    self.selectedPVar.set("-")
        

    def unDraw(self):
        "clears canvases, graph etc."
        if self.initialized:
            self.arenaCanv.delete("all")
            self.roomCanv.delete("all")
            self.graph.delete("all")
            self.initialized = False
            self.playBut.state(["disabled"])
            self.pauseBut.state(["disabled"])
            self.stopBut.state(["disabled"])
            self.fileFrame.previousBut.state(["disabled"])
            self.fileFrame.nextBut.state(["disabled"])
            self.fileFrame.tagBut.state(["disabled"])
            self.saveBut.state(["disabled"])
            

    def checkProcessing(self):
        "called when content of fileStorage is changed"
        if self.fileStorage.arenafiles or self.fileStorage.wrongfiles:
            self.fileStorageFrame.removeFiles.state(["!disabled"])
        else:
            self.fileStorageFrame.removeFiles.state(["disabled"])
        self.fileStorageFrame.chosenVar.set(len(self.fileStorage))
        self.fileStorageFrame.nonMatchingVar.set(len(self.fileStorage.wrongfiles))

        self.fileFrame.files = [] + self.fileStorage.arenafiles
        
        if not self.fileFrame.files or not self.fileFrame.selected in self.fileFrame.files:
            self.unDraw()

        if self.fileFrame.files:
            self.fileFrame.previousBut.state(["!disabled"])
            self.fileFrame.nextBut.state(["!disabled"])
            self.fileFrame.tagBut.state(["!disabled"])
            self.saveBut.state(["!disabled"])
            if not self.fileFrame.selected in self.fileFrame.files:
                self.fileFrame.selected = None
        else:
            self.fileFrame.selected = None

        self.setTime()
            
        self.fileFrame.drawTree(self.fileFrame.selected)


    def initialize(self):
        """initializes the canvases etc. if files were added to fileStorage and file from
            fileStorage is not initialized"""
        if self.fileFrame.files:
            if not self.fileFrame.selected in self.fileFrame.files:
                self.initializeFile(self.fileFrame.files[0])
                self.fileFrame.selected = self.fileFrame.files[0]


    def _timeFormat(self, time):
        "formats time from miliseconds to minutes:seconds"
        minutes = time // 60000
        seconds = (time % 60000) // 1000
        return "{:d}:{:0>2d}".format(int(minutes), int(seconds))

         
    def changedSpeed(self, value):
        "rounds speed set by scale"
        if eval(value) <= 1.0:
            self.speed.set(round(self.speed.get(), 1))
        elif eval(value) < 2.0:
            self.speed.set(round(self.speed.get() * 5, 0) / 5)
        elif eval(value) < 5.0:
            self.speed.set(round(self.speed.get() * 2, 0) / 2)
        elif eval(value) < 10.0:
            self.speed.set(round(self.speed.get(), 0))
        else:
            self.speed.set(round(self.speed.get() * 5, -1) / 5)
        

                

class FileFrame(ttk.Frame):
    "displays files in ShowTracks class"
    def __init__(self, root):
        super().__init__(root)

        self.rowconfigure(0, weight = 1)

        self.root = root
        self.fileStorage = self.root.fileStorage
        self.index = 0 # which file is selected when the FileTree is initialized
        self.files = []
        self.selected = None


        # tree
        self.treeFrame = ttk.Frame(self)
        self.treeFrame.grid(column = 0, row = 0, columnspan = 3, sticky = (N, S, E, W))
        self.treeFrame.rowconfigure(0, weight = 1)
        self.treeFrame.columnconfigure(0, weight = 1)
        
        self.tree = ttk.Treeview(self.treeFrame, selectmode = "browse", height = 20)
        self.tree.grid(column = 0, row = 0, sticky = (N, S, E, W))
        
        columns = ("tag")
        self.tree["columns"] = columns

        self.tree.column("#0", width = 250, anchor = "w")        
        self.tree.heading("#0", text = "File", command = self.orderByNames)

        self.tree.column("tag", width = 40, anchor = "center")
        self.tree.heading("tag", text = "Tag", command = self.orderByTag)
            
        self.scrollbar = ttk.Scrollbar(self.treeFrame, orient = VERTICAL,
                                       command = self.tree.yview)
        self.scrollbar.grid(column = 1, row = 0, sticky = (N, S, E))
        self.tree.configure(yscrollcommand = self.scrollbar.set)

        self.tree.bind("<1>", lambda e: self.click(e))
        self.tree.bind("<3>", lambda e: self.popUp(e))
        self.tree.bind("<Double-1>", lambda e: self.doubleclick(e))

        self.tree.tag_configure("comment", background = commentColor())
        # previous and next buttons
        self.fileLabFrame = ttk.Labelframe(self, text = "File")
        self.fileLabFrame.grid(column = 0, row = 1, columnspan = 3, sticky = (N, W, E), pady = 2)
        self.fileLabFrame.columnconfigure(2, weight = 1)
        
        self.previousBut = ttk.Button(self.fileLabFrame, text = "Previous",
                                      command = self.previousFun, state = "disabled")
        self.previousBut.grid(column = 0, row = 0, padx = 2)
        
        self.nextBut = ttk.Button(self.fileLabFrame, text = "Next", command = self.nextFun,
                                  state = "disabled")
        self.nextBut.grid(column = 1, row = 0, padx = 2)
        
        # tag buttons       
        self.tagBut = ttk.Button(self.fileLabFrame, text = "Tag file", command = self.tagFun,
                                 state = "disabled")
        self.tagBut.grid(column = 3, row = 0, padx = 2)

        # bindings
        for child in self.winfo_children():
            for grandchild in child.winfo_children():
                grandchild.bind("<Down>", lambda e: self.nextFun())
                grandchild.bind("<Right>", lambda e: self.nextFun())
                grandchild.bind("<Left>", lambda e: self.previousFun())
                grandchild.bind("<Up>", lambda e: self.previousFun())
                

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
            self.checkTag()
            self.selected = self.files[self.index]
            self.root.initializeFile(self.files[self.index])
            if not self.root.animate:
                self.root.stopFun()
                self.root.playFun()


    def doubleclick(self, event):
        "called when item in tree is doubleclicked"
        item = self.tree.identify("item", event.x, event.y)
        file = self.files[int(item)]
        if file == self.selected:
            Comment(self, file, True)            
                    
        
    def previousFun(self):
        "shows previous file"
        if self.index != 0 and self.files:
            self.prevIndex = self.index
            self.index -= 1
            self.tree.selection_set(str(self.index))
            self.tree.see(str(self.index))
            self.selected = self.files[self.index]
            self.checkTag()
            self.root.initializeFile(self.files[self.index])
            if not self.root.animate:
                self.root.stopFun()
                self.root.playFun()


    def nextFun(self):
        "shows next file"
        if self.index != len(self.files) - 1 and self.files:
            self.prevIndex = self.index
            self.index += 1
            self.tree.selection_set(str(self.index))
            self.tree.see(str(self.index))
            self.selected = self.files[self.index]
            self.checkTag()
            self.root.initializeFile(self.files[self.index])
            if not self.root.animate:
                self.root.stopFun()
                self.root.playFun()           
            

    def orderByNames(self):
        "orders files by names"
        if self.files:
            self.files.sort()
            self.drawTree(selected = self.selected)

    def orderByTag(self):
        "order files by tags"
        if self.files:
            self.files.sort(key = lambda i: (i in self.fileStorage.tagged), reverse = True)
            self.drawTree(selected = self.selected)


    def drawTree(self, selected = None):
        "initializes (or refreshes) tree"
        for child in self.tree.get_children():
            self.tree.delete(child)
            
        for count, file in enumerate(self.files):
            tag = "x" if file in self.fileStorage.tagged else ""             
            values = (tag)
            comment = "comment" if self.fileStorage.comments[file] else "withoutComment"
            self.tree.insert("", "end", str(count), text = returnName(file, self.files),
                             values = values, tag = comment)

        if selected:
            self.index = self.files.index(selected)
        elif self.files:
            self.index = 0            

        if self.files:
            self.tree.selection_set(str(self.index))            
            self.tree.see(str(self.index))


    def refresh(self):
        "refreshes the tree after adding a comment"
        self.root._showComment(self.selected)
        self.drawTree(selected = self.selected)


    def _showTrack(self, file):
        "opens ShowTracks; accessed by right click on file"
        ShowTracks(self, self.fileStorage.arenafiles, file)
            

    def popUp(self, event):
        "called when tree item is clicked on"
        item = self.tree.identify("item", event.x, event.y)
        menu = Menu(self, tearoff = 0)
        file = self.files[int(item)]
        if item:
            correct = True if file == self.selected else False         
            menu.add_command(label = "Add comment", command = lambda: Comment(self, file, correct))
            if file in self.fileStorage.tagged:
                menu.add_command(label = "Remove tag", command = lambda: self.untagFun(index =
                                                                                       int(item)))
            else:
                menu.add_command(label = "Add tag", command = lambda: self.tagFun(index =
                                                                                  int(item)))
            menu.add_command(label = "Show track", command = lambda: self._showTrack(file))

            menu.post(event.x_root, event.y_root)


