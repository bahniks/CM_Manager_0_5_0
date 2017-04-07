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
from time import time, localtime, strftime
from operator import methodcaller
from collections import OrderedDict
import os.path
import os
import csv


from commonframes  import TimeFrame, SaveToFrame, returnName
from filestorage import FileStorageFrame
from optionget import optionGet
from optionwrite import optionWrite
from version import version
from window import placeWindow
from tools import SetBatchTime
import mode as m


class Processor(ttk.Frame):
    "represents 'Process' page in the main window notebook"
    def __init__(self, root):
        super().__init__(root)

        self["padding"] = (10, 10, 12, 12)
        self.root = root
        self.fileStorage = self.root.fileStorage
        self.selectedBatchTime = optionGet("LastBatchTime", [(0, 20)], "list") # zkontrolovat ""

        # variables    
        self.status = StringVar()
        self.useBatchTimeVar = BooleanVar()
              
        # frames
        self.parametersF = ParameterFrame(self)
        self.fileStorageFrame= FileStorageFrame(self)
        self.saveToFrame = SaveToFrame(self, parent = "processor")
        self.optionFrame = OptionFrame(self, text = "Options")
        self.timeLabFrame = ttk.Labelframe(self, text = "Time")
        self.timeLabFrame.root = self
        self.timeFrame = TimeFrame(self.timeLabFrame)
        
        # buttons
        self.process = ttk.Button(self, text = "Process Files", command = self.processFun,
                                  state = "disabled")
        self.useBatchTime = ttk.Checkbutton(self.timeLabFrame, text = "Use batch time",
                                            variable = self.useBatchTimeVar,
                                            command = self.toggledUseBatchTime)
        self.setBatchTimeBut = ttk.Button(self.timeLabFrame, text = "Set", width = 3,
                                          command = self.setBatchTime)

        # labels
        self.statusBar = ttk.Label(self, textvariable = self.status)
        self.modeLab = ttk.Label(self, text = m.fullname[m.mode], font = ("Helvetica", "16"))
       
        # adding to grid
        self.parametersF.grid(column = 0, row = 3, columnspan = 4, sticky = (N, W), padx = 4)
        self.fileStorageFrame.grid(column = 3, row = 0, pady = 5, padx = 4)
        self.timeLabFrame.grid(column = 1, row = 5, padx = 30, sticky = (N, W))
        self.timeFrame.grid(column = 0, row = 0, columnspan = 2, sticky = (E, W))
        
        self.process.grid(column = 3, row = 7, sticky = (S, E), padx = 4, pady = 3)
        self.useBatchTime.grid(column = 0, row = 1, pady = 5)
        self.setBatchTimeBut.grid(column = 1, row = 1, pady = 5)

        self.statusBar.grid(column = 0, row = 7, columnspan = 3, sticky = (N, S, E, W), padx = 6,
                            pady = 3)
        self.modeLab.grid(column = 0, row = 0)
       
        self.saveToFrame.grid(column = 1, row = 1, columnspan = 3, sticky = (N, S, E, W),
                              padx = 6, pady = 2)

        self.optionFrame.grid(column = 0, row = 5, sticky = (N, E), padx = 6)
  
        # what should be enlarged
        self.columnconfigure(2, weight = 1)
        self.rowconfigure(2, weight = 3)
        self.rowconfigure(4, weight = 2)
        self.rowconfigure(6, weight = 2)


    def processCheck(self):
        "checks whether all inputs are valid - helper function for processFun"

        if self.saveToFrame.saveToVar.get() == "":
            raise Exception("You have to choose an output file!")
        
        if len(self.fileStorage) == 0:
            raise Exception("You haven't chosen any file!")

        try:
            startTime = float(self.timeFrame.startTimeVar.get())
        except Exception:
            raise Exception("Start time has to be a number!")
        try:
            time = float(self.timeFrame.timeVar.get())
        except Exception:
            raise Exception("Stop time has to be a number!")
        
        if startTime >= time:
            raise Exception("Start time must be smaller than stop time!")

        if time < 0 or startTime < 0:
            raise Exception("Time has to be set to a positive value")

        if not os.path.exists(os.path.split(self.saveToFrame.saveToVar.get())[0]):
            if os.path.split(self.saveToFrame.saveToVar.get())[0]:
                raise Exception("Pathname of the output file doesn't exist!")
            
        if len(self.filesToProcess) == 0:
            raise Exception("There is no file selected for processing!")
      
        
    def processFun(self):
        "processes chosen files and saves the results in the save-to file"
        # files to be processed
        self.filesToProcess = [file for file in self.fileStorage if \
                               self.optionFrame.processFile(file)]

        # checking for mistakes
        try:
            self.processCheck()
        except Exception as e:
            self.bell()
            self.status.set(e)
            return                   

        # progressWindow
        if len(self.filesToProcess) > 1:
            self.stoppedProcessing = False
            self.progressWindow = ProgressWindow(self, len(self.filesToProcess))     

        # initializations
        output = self.saveToFrame.saveToVar.get()
        if not os.path.splitext(output)[1]:
            output = output + optionGet("DefProcessOutputFileType", ".txt", "str", True)
        if not os.path.dirname(output):
            output = os.path.join(optionGet("ResultDirectory", os.getcwd(), "str", True), output)
        startTime = float(self.timeFrame.startTimeVar.get())
        time = float(self.timeFrame.timeVar.get())
        separator = optionGet("ResultSeparator", ",", "str", True)
        batchTime = self.selectedBatchTime if self.useBatchTimeVar.get() else None
        self.someProblem = False
        developer = optionGet("Developer", False, 'bool', True)

        # selected methods          
        methods = OrderedDict()
        parameters = m.parameters
        for name, par in parameters.items():
            if eval("self.parametersF.%sVar.get()" % (name.replace(" ", ""))):
                options = {name: optionGet(*option[0]) for name, option in par.options.items()}
                if not self.useBatchTimeVar.get():
                    methods[name] = [methodcaller(par.method, startTime = startTime,
                                                  time = time, **options)]
                elif name not in parameters.noBatch:
                    methods[name] = [methodcaller(par.method, startTime = times[0],
                                                  time = times[1], **options)
                                     for times in batchTime]
                else:
                    methods[name] = [methodcaller(par.method, **options)]

        # log
        self.log = Log(methods, startTime, time, self.filesToProcess, self.fileStorage,
                       self.optionFrame.removeReflectionsWhere.get(), output,
                       batchTime = batchTime)
                    
        # results header
        if self.useBatchTimeVar.get():
            results = ["File"]
            for method in methods:
                if method in parameters.noBatch:
                    results.append(method)
                else:
                    results.extend([method + " ({}-{})".format(start, end) for
                                    start, end in self.selectedBatchTime])
            results = separator.join(results)
        else:
            results = separator.join(["File"] + [method for method in methods])
        if self.optionFrame.saveTags.get():
            results += separator + "Tag"
        if self.optionFrame.saveComments.get():
            results += separator + "Comment"
        
        # computing of results
        for file in self.filesToProcess:
            # loading of cm object
            if methods:
                try:
                    if file in self.fileStorage.pairedfiles:
                        cm = m.CL(file, self.fileStorage.pairedfiles[file])
                    else:
                        cm = m.CL(file, "auto")

                    if self.optionFrame.removeReflections(file):
                        cm.removeReflections(points = self.fileStorage.reflections.get(file,
                                                                                            None))
                except Exception as e:
                    if developer:
                        print(e)   
                    filename = returnName(filename = file, allFiles =
                                          self.fileStorage.arenafiles) 
                    results += "\n" + filename + "{}NA".format(separator) * len(methods)
                    self.log.failedToLoad.append(file)
                    self.someProblem = True
                    continue
                                
            result = []

            for name, funcs in methods.items():
                for func in funcs:                        
                    try:
                        #if method[2] == "custom":
                            #exec("from Stuff.Parameters import {}".format(method[5]))               
                        result.append(func(cm))
                    except Exception as e:
                        if developer:
                            print(e)   
                        result.append("NA")
                        self.log.methodProblems[name].append(file)
                        self.someProblem = True

            result = separator.join(map(str, result))
            if methods:
                result = separator + result               
            filename = returnName(filename = file, allFiles = self.fileStorage.arenafiles)      
            results += "\n" + filename + result
            
            # tag inclusion in results
            if self.optionFrame.saveTags.get(): 
                if file in self.fileStorage.tagged:
                    results += separator + "1"
                else:
                    results += separator + "0"

            # comment inclusion in results
            if self.optionFrame.saveComments.get():
                results += separator + self.fileStorage.comments[file]
                    
            # progress window update
            if len(self.filesToProcess) > 1:
                if self.stoppedProcessing:
                    writeResults(output, results)
                    self.log.stopped = file
                    self.log.writeLog()
                    self.status.set("Processing stopped")
                    return
                else:
                    self.progressWindow.addOne()

        # results and log writing, ending of processing
        writeResults(output, results)
        self.log.writeLog()
        self._setStatusEndProgressWindow()

        if self.someProblem:
            ProcessingProblemDialog(self, self.log.filename, output)
        elif self.optionFrame.showResults.get():
            os.startfile(output)   

            
    def _setStatusEndProgressWindow(self):
        if len(self.filesToProcess) > 1:
            if self.someProblem:
                self.status.set("Files were processed.")
            else:
                self.status.set("Files were processed successfully.")
            self.progressWindow.destroy()
        else:
            if self.someProblem:
                self.status.set("File was processed.")
            else:
                self.status.set("File was processed successfully.")        


    def toggledUseBatchTime(self):
        "called when batch time checkbutton is toggled; disables or enables changing time"
        if self.useBatchTimeVar.get():
            self.timeFrame.totalTime.state(["disabled"])
            self.timeFrame.startTime.state(["disabled"])
        else:
            self.timeFrame.totalTime.state(["!disabled"])
            self.timeFrame.startTime.state(["!disabled"])


    def setBatchTime(self):
        SetBatchTime(self)
        if not self.useBatchTimeVar.get():
            self.useBatchTimeVar.set(True)
            self.toggledUseBatchTime()        

                
    def checkProcessing(self):
        "method updating page after change of notebook tab"
        if self.fileStorage.arenafiles and self.saveToFrame.saveToVar.get():
            self.process.state(["!disabled"])
        else:
            self.process.state(["disabled"])

        if self.fileStorage.arenafiles or self.fileStorage.wrongfiles:
            self.fileStorageFrame.removeFiles.state(["!disabled"])
        else:
            self.fileStorageFrame.removeFiles.state(["disabled"])        

        self.fileStorageFrame.chosenVar.set(len(self.fileStorage))
        self.fileStorageFrame.nonMatchingVar.set(len(self.fileStorage.wrongfiles))



class Log():
    "class representing log of processing"
    def __init__(self, methods, startTime, stopTime, files, fileStorage, removeReflections,
                 saveTo, batchTime = None):
        self.failedToLoad = []
        self.methods = methods
        self.methodProblems = {method: [] for method in self.methods}
        self.startTime = startTime
        self.stopTime = stopTime
        self.files = files
        self.stopped = False
        self.fileStorage = fileStorage
        self.removeReflections = removeReflections
        self.saveTo = saveTo
        self.batchTime = batchTime
    
    def writeLog(self):
        "writes the log"
        filepath = optionGet("LogDirectory", os.path.join(os.getcwd(), "Stuff", "Logs"),
                             "str", True)
        writeTime = localtime()
        self.filename = os.path.join(filepath, strftime("%y_%m_%d_%H%M%S", writeTime) + ".txt")

        self.problem = False
        for method in self.methods:
            if self.methodProblems[method]:
                self.problem = True           
            
        with open(self.filename, mode = "w") as logfile:
            logfile.write("CM Manager version " + ".".join(version()) + "\n\n")
            logfile.write("Task: " + m.fullname[m.mode] + "\n\n")
            logfile.write("Date: " + strftime("%d %b %Y", writeTime) + "\n")
            logfile.write("Time: " + strftime("%H:%M:%S", writeTime) + "\n\n\n")
            self._writeProblems(logfile)
            self._writeMethods(logfile)
            self._writeTime(logfile)
            self._writeSaveIn(logfile)
            logfile.write("Reflections removed in:\n\t" + self.removeReflections + "\n\n\n")
            self._writeFiles(logfile)
            self._writeAddedReflections(logfile)

    def _writeProblems(self, logfile):
        "writes information about all problems in a logfile"
        if self.failedToLoad or self.problem or self.stopped:
            logfile.write("Errors:\n" + "-" * 20 + "\n")
            if self.stopped:
                logfile.write("Processing stopped after: " + file + "\n\n")
            if self.failedToLoad:
                logfile.write("Failed to load:\n\t")
                logfile.write("\n\t".join(self.failedToLoad))
                logfile.write("\n\n")
            if self.problem:
                logfile.write("Failed to compute:\n")
                for method in self.methods:
                    if self.methodProblems[method]:
                        logfile.write("\t" + method + ":\n\t\t")
                        logfile.write("\n\t\t".join(self.methodProblems[method]))
                        logfile.write("\n")
                logfile.write("\n")
            logfile.write("-" * 20 + "\n\n")

    def _writeMethods(self, logfile):
        "writes information about used methods in a logfile"
        logfile.write("Methods used:")
        if self.methods:
            for method in self.methods:
                logfile.write("\n\t" + method)
                if m.parameters[method].options:
                    for option in m.parameters[method].options.values():
                        logfile.write("\n\t\t" + option[1] + ": " + str(optionGet(*option[0])))
        else:
            logfile.write("\n\tNone")
        logfile.write("\n\n\n")

    def _writeTime(self, logfile):
        "writes information about set time in a logfile"
        logfile.write("Time set:\n")
        if not self.batchTime:
            logfile.write("\tStart: " + "{:5.1f}".format(self.startTime) + " minutes\n")
            logfile.write("\tStop : " + "{:5.1f}".format(self.stopTime) + " minutes\n")
        else:
            batchTime = ["{}-{}".format(start, end) for start, end in self.batchTime]
            logfile.write("\tBatch time [start-end minutes]: " + ", ".join(batchTime) + "\n") 
        logfile.write("\n\n")

    def _writeSaveIn(self, logfile):
        "writes information about file where the results were saved in a logfile"
        file = self.saveTo
        if not os.path.splitext(file)[1]:
            file += optionGet("DefProcessOutputFileType", ".txt", "str", True)
        logfile.write("Results saved in:\n\t" + os.path.abspath(file) + "\n\n\n")
            
    def _writeFiles(self, logfile):
        "writes information about processed files in a logfile"
        logfile.write("Files processed:")
        if self.stopped:
            index = self.files.index(self.stopped)
            if index == len(self.files):
                for file in self.files[:index]:
                    self._writeOneFile(file, logfile)     
                logfile.write("\nStopped before processing following files:\n\t")
                for file in self.files[(index + 1):]:
                    self._writeOneFile(file, logfile)
            else:
                for file in self.files:
                    self._writeOneFile(file, logfile)    
        else:
            for file in self.files:
                self._writeOneFile(file, logfile)   

    def _writeOneFile(self, file, logfile):
        "writes information about one file in a logfile"
        logfile.write("\n\t" + file)
        if file in self.fileStorage.tagged:
            logfile.write("\tTagged")
        if self.fileStorage.comments[file]:
            logfile.write("\n\t\tComment: " + self.fileStorage.comments[file])
        if file in self.fileStorage.pairedfiles:
            logfile.write("\n\t\tPaired with: " +
                          self.fileStorage.pairedfiles[file])

    def _writeAddedReflections(self, logfile):
        if self.fileStorage.addedReflections and any(self.fileStorage.addedReflections.values()):
            logfile.write("\n\nAdded reflections:")
            for file in self.files:
                if file in self.fileStorage.addedReflections:
                    if self.fileStorage.addedReflections[file]:
                        logfile.write("\n\t" + file + "\n\t\t")
                        added = ",".join(str(p) for p in
                                         sorted(self.fileStorage.addedReflections[file]))
                        logfile.write(added)
                    



class ProgressWindow(Toplevel):
    "opens new window with progressbar and disables actions on other windows"
    def __init__(self, root, number, text = "processed"):
        super().__init__(root)
        
        self.root = root
        self.number = number
        self.title("Progress")
        self.focus_set()
        self.grab_set()
        placeWindow(self, 404, 80)
        self.text = text
        self.resizable(FALSE, FALSE)

        # progressbar
        self.progress = ttk.Progressbar(self, orient = HORIZONTAL, length = 400,
                                        mode = "determinate")
        self.progress.configure(maximum = number)
        self.progress.grid(column = 0, row = 1, columnspan = 2, pady = 3, padx = 2)

        # cancel button
        self.cancel = ttk.Button(self, text = "Cancel", command = self.close)
        self.cancel.grid(column = 0, columnspan = 2, row = 2, pady = 2)

        # number of files label
        self.numFiles = StringVar()
        self.processed = 0
        self.processedFilesText = "{} out of {} files {}".format("{}", self.number, self.text)
        self.numFiles.set(self.processedFilesText.format(self.processed))
        self.numFilesLab = ttk.Label(self, textvariable = self.numFiles)
        self.numFilesLab.grid(row = 0, column = 1, sticky = E, pady = 2, padx = 2)

        # expected time label
        self.begintime = time()
        self.timeText = "Remaining time: {}"
        self.timeVar = StringVar()
        self.timeLab = ttk.Label(self, textvariable = self.timeVar)
        self.timeLab.grid(row = 0, column = 0, sticky = W, pady = 2, padx = 2)        

        
        self.protocol("WM_DELETE_WINDOW", lambda: self.close())


    def addOne(self):
        "called after one file is processed"
        self.progress.step(1)
        self.processed += 1
        self.numFiles.set(self.processedFilesText.format(self.processed))
        expectedTime = round((self.number - self.processed) *\
                             ((time() - self.begintime) / self.processed))
        self.timeVar.set(self.timeText.format(self.formatTime(expectedTime)))
        self.update()


    def formatTime(self, seconds):
        "returns string with the remaining time given the number of seconds left as attribute"
        if seconds > 60:
            minutes = seconds // 60
            seconds = seconds % 60
            if minutes > 5:
                return "{} minutes".format(minutes)
            elif minutes == 1:
                return "1 minute {} seconds".format(min([int(round(seconds, -1)), 55]))
            else:
                return "{} minutes {} seconds".format(int(minutes),
                                                      min([int(round(seconds, -1)), 55]))
        else:
            if seconds < 5:
                return "5 seconds"
            else:
                return "{} seconds".format(min([int(round(seconds * 2, -1) / 2), 55]))


    def close(self):
        "called to cancel or exit"
        self.root.stoppedProcessing = True
        self.destroy()
                    



def writeResults(file, results):
    "writes 'results' in a 'file'"
    if not os.path.splitext(file)[1]:
        file = file + optionGet("DefProcessOutputFileType", ".txt", "str", True)
    if not os.path.dirname(file):
        file = os.path.join(optionGet("ResultDirectory", os.getcwd(), "str", True), file)
    if os.path.splitext(file)[1] == ".csv":
        results = [[item for item in line.split(",")] for line in results.split("\n")]
        with open(file, mode = "w", newline = "") as f:
            writer = csv.writer(f, dialect = "excel")
            writer.writerows(results)
            f.close()    
    else:
        outfile = open(file, "w")
        outfile.write(results)
        outfile.close()



class ParameterFrame(ttk.Labelframe):
    "helper class for Options representing frame containing default settings of parameters"
    def __init__(self, root, text = "Parameters"):
        super().__init__(root, text = text)

        basic = ttk.Labelframe(self, text = "Basic")
        advanced = ttk.Labelframe(self, text = "Advanced")
        double = ttk.Labelframe(self, text = "Double Avoidance")
        info = ttk.Labelframe(self, text = "Information")
        experimental = ttk.Labelframe(self, text = "Experimental")
        custom = ttk.Labelframe(self, text = "Custom Written")
        basic.grid(column = 0, row = 0, sticky = (N, S, W), padx = 3, pady = 4)
        advanced.grid(column = 1, row = 0, sticky = (N, S, W), padx = 3, pady = 4)
        double.grid(column = 2, row = 0, sticky = (N, S, W), padx = 3, pady = 4)
        info.grid(column = 3, row = 0, sticky = (N, S, W), padx = 3, pady = 4)
        experimental.grid(column = 4, row = 0, sticky = (N, S, W), padx = 3, pady = 4)
        custom.grid(column = 5, row = 0, sticky = (N, S, W), padx = 3, pady = 4)

        basicNum = 0
        advancedNum = 0
        doubleNum = 0
        infoNum = 0
        experimentalNum = 0
        customNum = 0
        for name, parameter in m.parameters.items():
            if parameter.group == "basic":
                 rowNum = basicNum
                 basicNum += 1
            elif parameter.group == "advanced":
                 rowNum = advancedNum
                 advancedNum += 1
            elif parameter.group == "double":
                 rowNum = doubleNum
                 doubleNum += 1
            elif parameter.group == "info":
                 rowNum = infoNum
                 infoNum += 1
            elif parameter.group == "experimental":
                 rowNum = experimentalNum
                 experimentalNum += 1                       
            elif parameter.group == "custom":
                 rowNum = customNum
                 customNum += 1
            label = name.replace(" ", "")
            exec("self.%s = BooleanVar()" % (label + "Var"))
            exec("self.%sVar.set(%s)" % (label, optionGet("Def" + label, False, 'bool')))
            exec("""self.%sBut = ttk.Checkbutton(%s, text = '%s', variable = self.%sVar,
                 onvalue = True)""" % (label, parameter.group, name, label))
            exec("self.%sBut.grid(column = 0, row = %i, sticky = (S, W), padx = 1, pady = 2)" %\
                 (label, rowNum))

        self.bind("<Button-3>", lambda e: self.popUp(e, "all"))
        basic.bind("<Button-3>", lambda e: self.popUp(e, "basic"))
        advanced.bind("<Button-3>", lambda e: self.popUp(e, "advanced"))
        double.bind("<Button-3>", lambda e: self.popUp(e, "double"))
        info.bind("<Button-3>", lambda e: self.popUp(e, "info"))
        experimental.bind("<Button-3>", lambda e: self.popUp(e, "experimental"))
        custom.bind("<Button-3>", lambda e: self.popUp(e, "custom"))


    def popUp(self, event, category):
        "popUp menu for selecting and unselecting all parameters within a category"
        menu = Menu(self, tearoff = 0)
        menu.add_command(label = "Select all", command = lambda: self._selectAll(category))
        menu.add_command(label = "Unselect all", command = lambda: self._unselectAll(category))
        if category == "all":
            menu.add_separator()
            menu.add_command(label = "Save selected parameters as default",
                             command = lambda: self.saveSelectedParametersAsDefault())
        menu.post(event.x_root, event.y_root)

    def _selectAll(self, category):
        "selects all parameters in a category"
        for name, parameter in m.parameters.items():
            if parameter.group == category or category == "all":
                exec("self.%sVar.set(True)" % (name.replace(" ", "")))

    def _unselectAll(self, category):
        "unselects all parameters in a category"
        for name, parameter in m.parameters.items():
            if parameter.group == category or category == "all":
                exec("self.%sVar.set(False)" % (name.replace(" ", "")))

    def saveSelectedParametersAsDefault(self):
       for name, parameter in m.parameters.items():
           label = name.replace(" ", "")
           optionWrite("Def" + label, bool(eval(("self." + label + "Var.get()"))))        


class OptionFrame(ttk.Labelframe):
    "contains options for processing"
    def __init__(self, root, text = "Options"):
        super().__init__(root, text = text)

        self.root = root
        if type(self.root) is Processor:
            self.fileStorage = self.root.root.fileStorage

        # variables
        self.processWhat = StringVar()
        self.removeReflectionsWhere = StringVar()
        self.saveTags = BooleanVar()
        self.saveComments = BooleanVar()
        self.showResults = BooleanVar()

        self.processWhat.set(optionGet("ProcessWhat", "all files", "str", True))
        self.removeReflectionsWhere.set(optionGet("RemoveReflectionsWhere", "no files",
                                                  "str", True))
        self.saveTags.set(optionGet("DefSaveTags", False, "bool", True))
        self.saveComments.set(optionGet("DefSaveComments", False, "bool", True))
        self.showResults.set(optionGet("DefShowResults", False, "bool", True))        

        # labels
        self.processLabel = ttk.Label(self, text = "Process")
        self.removeReflectionsLabel = ttk.Label(self, text = "Remove reflections in")
        self.saveTagsLabel = ttk.Label(self, text = "Save tags")
        self.saveCommentsLabel = ttk.Label(self, text = "Save comments")
        self.showResultsLabel = ttk.Label(self, text = "Show results after processing")

        self.processLabel.grid(column = 0, row = 0, sticky = E, padx = 3)
        self.removeReflectionsLabel.grid(column = 0, row = 1, sticky = E, padx = 3)
        self.saveTagsLabel.grid(column = 0, row = 2, sticky = E, padx = 3)
        self.saveCommentsLabel.grid(column = 0, row = 3, sticky = E, padx = 3)
        self.showResultsLabel.grid(column = 0, row = 5, sticky = E, padx = 3)

        # comboboxes
        self.processCombobox = ttk.Combobox(self, textvariable = self.processWhat,
                                            justify = "center", width = 15, state = "readonly")
        self.processCombobox["values"] = ("all files", "only tagged", "only untagged")

        self.removeReflectionsCombobox = ttk.Combobox(self, justify = "center", textvariable =
                                                      self.removeReflectionsWhere, width = 15,
                                                      state = "readonly")
        self.removeReflectionsCombobox["values"] = ("no files", "tagged files", "untagged files",
                                                    "all files")

        self.processCombobox.grid(column = 1, row = 0, sticky = W, padx = 2)
        self.removeReflectionsCombobox.grid(column = 1, row = 1, sticky = W, padx = 2)

        # checkbuttons
        self.saveTagsCheckbutton = ttk.Checkbutton(self, variable = self.saveTags, onvalue = True,
                                                   offvalue = False)
        self.saveTagsCheckbutton.grid(column = 1, row = 2)
        self.saveCommentsCheckbutton = ttk.Checkbutton(self, variable = self.saveComments,
                                                       onvalue = True, offvalue = False)
        self.saveCommentsCheckbutton.grid(column = 1, row = 3)
        self.showResultsCheckbutton = ttk.Checkbutton(self, onvalue = True, offvalue = False,
                                                      variable = self.showResults)
        self.showResultsCheckbutton.grid(column = 1, row = 5)
        

    def removeReflections(self, file):
        "returns True is reflections should be removed in the file in argument"
        where = self.removeReflectionsWhere.get()
        if where == "no files":
            return False
        elif where == "tagged files":
            if file in self.fileStorage.tagged:
                return True
            else:
                return False
        elif where == "untagged files":
            if file in self.fileStorage.tagged:
                return False
            else:
                return True
        elif where == "all files":
            return True


    def processFile(self, file):
        "returns True if the file in argument should be processed"
        if self.processWhat.get() == "all files":
            return True
        elif self.processWhat.get() == "only tagged":
            if file in self.fileStorage.tagged:
                return True
            else:
                return False
        elif self.processWhat.get() == "only untagged":
            if file in self.fileStorage.tagged:
                return False
            else:
                return True        



class ProcessingProblemDialog(Toplevel):
    "showed when some problem occured during processing"
    def __init__(self, root, logfile, results = None):
        super().__init__(root)
        
        self.root = root
        self.title("Warning")
        self.grab_set()
        self.focus_set()
        placeWindow(self, 350, 100)
        self.resizable(False, False)
        self.logfile = logfile
        self.minsize(350, 100)
        
        # buttons
        self.cancelBut = ttk.Button(self, text = "Cancel", command = self.cancelFun)
        self.cancelBut.grid(column = 2, row = 2, pady = 2)
        self.showBut = ttk.Button(self, text = "Open log", command = self.showFun)
        self.showBut.grid(column = 1, row = 2, pady = 2)
        self.resultsBut = ttk.Button(self, text = "Show results", command = self.resultsFun)
        self.resultsBut.grid(column = 0, row = 2, pady = 2)
        if not results or not os.path.exists(results):
            self.resultsBut.state(["disabled"])

        # text
        self.label = ttk.Label(self, text = "Some problem occured during processing.\n" +\
                               "See log for details.", anchor = "center", justify = "center")
        self.label.grid(column = 0, columnspan = 3, row = 0, padx = 8, pady = 5,
                        sticky = (N, S, E, W))
      
        self.rowconfigure(0, weight = 1)
        self.columnconfigure(0, weight = 1)
        self.columnconfigure(1, weight = 2)
        self.columnconfigure(2, weight = 1)
        

    def cancelFun(self):
        "function of cancel button"
        self.destroy()

    def showFun(self):
        "function of open log button"
        os.startfile(self.logfile)

    def resultsFun(self):
        "opens a file with results"
        os.startfile(self.root.log.saveTo)
