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

from tkinter.filedialog import askdirectory
from tkinter import *
from tkinter import ttk, messagebox, colorchooser
import os


from optionwrite import optionWrite
from optionget import optionGet
from processor import ParameterFrame, OptionFrame
from commonframes  import TimeFrame
from window import placeWindow
import mode as m
    

class RadioFrame(ttk.Labelframe):
    "class containing radiobuttons for setting options"
    def __init__(self, root, text, optionName, default, options):
        super().__init__(root, text = text)
        self.optionName = optionName
        self.variable = StringVar()
        self.variable.set(optionGet(optionName, default, "str"))
        for count, option in enumerate(options):
            exec("self.{}RB = ttk.Radiobutton(self, text = '{}', variable = self.variable, \
                 value = '{}')".format(option.replace(" ", "_"), option, option))
            exec("self.{}RB.grid(row = count, column = 0, padx = 2, pady = 2, sticky = W)".format(
                 option.replace(" ", "_")))

    def get(self):
        "called when options are saved by root (i.e. Option Toplevel)"
        return "'" + self.variable.get() + "'"


class ChooseDirectoryFrame(ttk.Labelframe):
    "represents frame for selection of directory"
    def __init__(self, root, text, optionName, default, general):
        super().__init__(root, text = text)
        
        self.root = root
        self.currentDir = os.path.normpath(optionGet(optionName, default, "str",
                                                     general = general))

        self.directory = StringVar()
        self.directory.set(self.currentDir)

        self.button = ttk.Button(self, text = "Choose", command = self.chooseFun)
        self.button.grid(column = 1, row = 0, padx = 3, pady = 1)

        self.entry = ttk.Entry(self, textvariable = self.directory, width = 70)
        self.entry.grid(column = 0, row = 0, padx = 3, pady = 1, sticky = (E, W))

        self.columnconfigure(0, weight = 1)

    def chooseFun(self):
        "opens dialog for directory selection"
        newDirectory = askdirectory(parent = self.root, initialdir = self.currentDir,
                                    title = "Choose a directory")
        if newDirectory:
            self.directory.set(os.path.normpath(newDirectory))

    def get(self):
        "returns chosen directory"
        return self.directory.get()
        
        

class OptionsCM(Toplevel):
    "options window reachable from menu"
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.title(m.fullname[m.mode] + " options")
        self.grab_set()
        self.focus_set()
        self.resizable(FALSE, FALSE)
        placeWindow(self, 720, 350)
        self["padx"] = 10
        self["pady"] = 10
        
        self.parametersF = ParameterFrame(self, "Default parameters")

        # selection of directories
        self.fileDirectory = ChooseDirectoryFrame(self, "Default directory for file selection",
                                                  "FileDirectory", r'{}'.format(os.getcwd()),
                                                  False)

        # default time
        self.timeLabFrame = ttk.Labelframe(self, text = "Default time")
        self.timeFrame = TimeFrame(self.timeLabFrame, observe = False, loadtime = False)
        self.timeFrame.grid(row = 0, column = 0)
    
        # buttons
        self._createButtons()

        # grid of self contents        
        self.parametersF.grid(row = 0, column = 0, columnspan = 2, sticky = (N, W), padx = 4,
                              pady = 2)
        self.buttonFrame.grid(row = 3, column = 0, columnspan = 2, padx = 3, pady = 6,
                              sticky = (E, W, N, S))
        self.timeLabFrame.grid(row = 1, column = 1, padx = 6, pady = 4, sticky = (N, W, E))
        self.fileDirectory.grid(row = 1, column = 0, pady = 2, padx = 2, sticky = (E, W))
        
                                   
    def _createButtons(self):
        # buttons
        self.buttonFrame = ttk.Frame(self)
        self.buttonFrame.columnconfigure(0, weight = 3)
        self.buttonFrame.columnconfigure(2, weight = 1)
        self.buttonFrame.columnconfigure(4, weight = 3)

        self.okBut = ttk.Button(self.buttonFrame, text = "Ok", command = self.okFun)
        self.cancelBut = ttk.Button(self.buttonFrame, text = "Cancel", command = self.cancelFun)

        self.okBut.grid(column = 1, row = 0, padx = 3, pady = 2)
        self.cancelBut.grid(column = 3, row = 0, padx = 3, pady = 2, sticky = (E))

        
    def saveFun(self):
        "saves all options"
        self.parametersF.saveSelectedParametersAsDefault()
        optionWrite("DefStartTime", self.timeFrame.startTimeVar.get(), False)
        optionWrite("DefStopTime", self.timeFrame.timeVar.get(), False)
        directory = self.fileDirectory.get().rstrip("\/")
        if os.path.exists(directory):
            optionWrite("FileDirectory", "r'" + directory  + "'", False)
        else:
            messagebox.showinfo(message = "Directory " + directory + " does not exist.",
                                icon = "error", parent = self, title = "Error",
                                detail = "Choose an existing directory.")
            return False
        return True


    def okFun(self):
        "saves options and exits"
        if self.saveFun():
            self.destroy()


    def cancelFun(self):
        "destroys the window"
        self.destroy()     



class GeneralOptions(OptionsCM, Toplevel):
    def __init__(self, root):
        super(OptionsCM, self).__init__(root)
        self.root = root
        self.title("General options")
        self.grab_set()
        self.focus_set()
        self.resizable(FALSE, FALSE)
        placeWindow(self, 554, 499)
        self["padx"] = 10
        self["pady"] = 10

        # default filetype of processor output
        self.fileTypeVar = StringVar()
        self.fileTypeVar.set(optionGet("DefProcessOutputFileType", ".txt", "str", True))

        self.fileTypeFrame = ttk.Labelframe(self, text = "Default output filetype")

        self.txtRadioBut = ttk.Radiobutton(self.fileTypeFrame, text = ".txt",
                                           variable = self.fileTypeVar, value = ".txt")
        self.csvRadioBut = ttk.Radiobutton(self.fileTypeFrame, text = ".csv",
                                           variable = self.fileTypeVar, value = ".csv")
        
        self.txtRadioBut.grid(row = 1, column = 0, padx = 2, pady = 2, sticky = W)
        self.csvRadioBut.grid(row = 0, column = 0, padx = 2, pady = 2, sticky = W)


        # output separator
        self.separatorVar = StringVar()
        self.separatorVar.set(optionGet("ResultSeparator", ",", "str", True))

        self.separatorFrame = ttk.Labelframe(self, text = "Result separator")

        self.commaRadioBut = ttk.Radiobutton(self.separatorFrame, text = "Comma",
                                             variable = self.separatorVar, value = ",")
        self.semicolonRadioBut = ttk.Radiobutton(self.separatorFrame, text = "Semicolon",
                                                 variable = self.separatorVar, value = ";")        
        self.tabRadioBut = ttk.Radiobutton(self.separatorFrame, text = "Tab",
                                           variable = self.separatorVar, value = "\t")
        
        self.commaRadioBut.grid(row = 0, padx = 2, pady = 2, sticky = W)
        self.semicolonRadioBut.grid(row = 1, padx = 2, pady = 2, sticky = W)
        self.tabRadioBut.grid(row = 2, padx = 2, pady = 2, sticky = W)

        # selection of directories
        self.directoriesFrame = ttk.Frame(self)
        self.directoriesFrame.columnconfigure(0, weight = 1)
        self.directoryOptions = [
            ("Default directory for results", "ResultDirectory", os.getcwd(), True),
            ("Directory for saving of processing logs", "LogDirectory",
             os.path.join(os.getcwd(), "Stuff", "Logs"), True),
            ("Directory for images", "ImageDirectory", os.getcwd(), True),
            ("Directory for saving of selected files", "SelectedFilesDirectory",
             os.path.join(os.getcwd(), "Stuff", "Selected files"), True)]
        for count, option in enumerate(self.directoryOptions):
            exec("""self.{1} = ChooseDirectoryFrame(self.directoriesFrame, '{0}', '{1}', \
                 r'{2}', {3})""".format(*option))
            exec("self.{}.grid(row = {}, column = 0, pady = 2, padx = 2, sticky = (E, W))".format(
                option[1], count))

        # save filename as full path
        self.saveFilenameAs = RadioFrame(self, text = "Save (show) filename as:",
                                         optionName = "SaveFullPath", default = "Basename",
                                         options = ["Basename", "Full path", "Unique path"])

        # processor options
        self.processorOptions = OptionFrame(self, text = "Default process options")


        self._createButtons()
        self.commentColor = ttk.Button(self, text = "Comment color",
                                       command = self.chooseCommentColor)

        self.commentColor.grid(column = 2, row = 0, padx = 2, pady = 2)
        self.fileTypeFrame.grid(row = 0, column = 0, padx = 3, pady = 4,
                                sticky = (W, N, E, S))
        self.buttonFrame.grid(row = 3, column = 0, columnspan = 3, padx = 3, pady = 6,
                              sticky = (E, W, N, S))
        self.separatorFrame.grid(row = 1, column = 0, padx = 3, pady = 4,
                                 sticky = (W, N, E))
        self.saveFilenameAs.grid(row = 0, column = 1, padx = 3, pady = 4, sticky = (N, W, E))
        self.processorOptions.grid(row = 1, column = 1, pady = 4, padx = 4, sticky = (N, W))
        self.directoriesFrame.grid(row = 2, column = 0, columnspan = 3, padx = 3, pady = 4)


    def saveFun(self):
        "saves all options"
        optionWrite("DefProcessOutputFileType", "'" + self.fileTypeVar.get() + "'", True)
        optionWrite("SaveFullPath", self.saveFilenameAs.get(), True)
        optionWrite("ResultSeparator", "'" + self.separatorVar.get() + "'", True)
        optionWrite("ProcessWhat", "'" + self.processorOptions.processWhat.get() + "'", True)
        optionWrite("RemoveReflectionsWhere",
                    "'" + self.processorOptions.removeReflectionsWhere.get() + "'", True)
        optionWrite("DefSaveTags", self.processorOptions.saveTags.get(), True)
        optionWrite("DefSaveComments", self.processorOptions.saveComments.get(), True)
        optionWrite("DefShowResults", self.processorOptions.showResults.get(), True)
        for option in self.directoryOptions:
            directory = eval("self.{}.get()".format(option[1])).rstrip("\/")
            if os.path.exists(directory):
                optionWrite(option[1], "r'" + directory  + "'", option[3])
            else:
                messagebox.showinfo(message = "Directory " + directory + " does not exist.",
                                    icon = "error", parent = self, title = "Error",
                                    detail = "Choose an existing directory.")
                return False
        return True

    def chooseCommentColor(self):
        "opens dialog for choosing color of comments and immediately saves the selected color"
        color = colorchooser.askcolor(initialcolor = optionGet("CommentColor", "grey90",
                                                               'str', True), parent = self)
        if color and len(color) > 1 and color[1]:
            selected = color[1]
            optionWrite("CommentColor", "'" +  selected + "'", True)
            self.root.explorer.fileFrame.tree.tag_configure("comment", background = selected)
            self.root.controller.contentTree.tag_configure("comment", background = selected)


        
class AdvancedOptions(Toplevel):
    "parameter settings window reachable from menu"
    def __init__(self, root):
        super().__init__(root)
        self.title("Parameter settings (" + m.fullname[m.mode] + ")")
        self.grab_set()
        self.focus_set()
        self.resizable(FALSE, FALSE)
        self.minsize(410, 300)
        height = 382 if m.mode == "OF" else 800
        placeWindow(self, 410, height)
        self.columnconfigure(0, weight = 3)
        self.columnconfigure(1, weight = 1)
        self.columnconfigure(2, weight = 1)
        self.columnconfigure(3, weight = 3)
        self["padx"] = 10
        self["pady"] = 10

         
        self.okBut = ttk.Button(self, text = "Ok", command = self.okFun)
        self.okBut.grid(column = 1, row = 1, padx = 3, pady = 4)
        self.cancelBut = ttk.Button(self, text = "Cancel", command = self.cancelFun)    
        self.cancelBut.grid(column = 2, row = 1, padx = 3, pady = 4)

        self.settingsFrame = ttk.Frame(self)
        self.settingsFrame2 = ttk.Frame(self)
        
        self.optionFrames = []
        
        mapping = {"degrees": "°", "seconds": "s", "percents": "%"}
        numFrames = sum([1 for par in m.parameters.values() if par.options])
        split = numFrames > 7

        count = 0
        for name, par in sorted(m.parameters.items()):
            if not par.options:
                continue
            options = []
            for option in sorted(par.options.values(), key = lambda opt: opt[0].types == "bool"):
                strings = option[1].split(" [in ")
                if len(strings) == 2:
                    text, unit = strings
                    unit = unit.rstrip("]")
                    unit = mapping[unit] if unit in mapping else unit
                else:
                    text, unit = strings[0], None
                text = text.strip()
                opt = option[0]
                options.append((text + ": ", (opt.name, opt.default, opt.types), unit))
            if split and count >= (numFrames // 2):
                frame = self.settingsFrame2
            else:
                frame = self.settingsFrame
            self.optionFrames.append(ParameterOptionFrame(frame, name, options))
            count += 1

        if numFrames > 7:
            self.settingsFrame.grid(row = 0, column = 0, columnspan = 2, padx = 3, pady = 4,
                                    sticky = (N, W, E))
            self.settingsFrame2.grid(row = 0, column = 2, columnspan = 2, padx = 3, pady = 4,
                                     sticky = (N, W, E))
        else:
            self.settingsFrame.grid(row = 0, column = 0, columnspan = 4, padx = 3, pady = 4,
                                    sticky = (N, W, E))

        self.settingsFrame.columnconfigure(0, weight = 1)
        self.settingsFrame2.columnconfigure(0, weight = 1)        

        for row, frame in enumerate(self.optionFrames):
            frame.grid(column = 0, row = row, pady = 3, padx = 3, sticky = (W, E))
                                                               

    def okFun(self):
        for frame in self.optionFrames:
            frame.save()
        self.destroy()


    def cancelFun(self):
        self.destroy()




class ParameterOptionFrame(ttk.Labelframe):
    """
    frame with options for one parameter
        options = ((text, option, sign), (...)), where option = (option name, default, types)
    """
    def __init__(self, root, name, options):
        super().__init__(root, text = name)
        
        self.options = options
        self.opts = []
        
        entryWidth = 10
        rightLabWidth = 8

        for row, option in enumerate(options):
            self.opts.append({})
            var = BooleanVar if option[1][2] == 'bool' else StringVar
            self.opts[row]["variable"] = var()
            current = optionGet(*option[1])
            if type(current) == str:
                current = "'" + current + "'"
            self.opts[row]["variable"].set(current)
            self.opts[row]["label"] = ttk.Label(self, text = option[0])
            self.opts[row]["label"].grid(column = 0, row = row, pady = 2, sticky = E)
            if option[1][2] == 'bool':
                self.opts[row]["input"] = ttk.Checkbutton(self, onvalue = True, offvalue = False,
                                                          variable = self.opts[row]["variable"])
            else:
                self.opts[row]["input"] = ttk.Entry(self, width = entryWidth, justify = 'right',
                                                    textvariable = self.opts[row]["variable"])
            self.opts[row]["input"].grid(column = 1, row = row, padx = 2, pady = 2)
            self.opts[row]["sign"] = ttk.Label(self, text = option[2], width = rightLabWidth)
            self.opts[row]["sign"].grid(column = 2, row = row, pady = 2, sticky = W)

        self.columnconfigure(0, weight = 1)


    def save(self):
        for row, option in enumerate(self.options):
            value = str(self.opts[row]["variable"].get())
            value = bool(eval(value)) if option[1][2] == 'bool' else eval(value)       
            optionWrite(option[1][0], value)

        
