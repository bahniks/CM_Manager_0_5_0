#! python3
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
from tkinter import messagebox
from time import localtime, strftime

import traceback
import os
import sys


from menu import MenuCM
from filestorage import FileStorage
from optionget import optionGet
from version import version
from window import placeWindow
from tools import saveFileStorage, doesFileStorageRequiresSave, loadFileStorage
import mode as m


class GUI(Tk):
    "represents GUI"
    def __init__(self):
        super().__init__()
   
        self.option_add("*tearOff", FALSE)
        self.resizable(FALSE, FALSE)
        self.initialized = False
        
        '''
        # used when size of the window is changed for placeWindow arguments     
        self.after(250, lambda: print(self.winfo_width()))
        self.after(250, lambda: print(self.winfo_height()))
        '''
        x, y = 1000, 770
        placeWindow(self, x, y)

        self.selectFunction = ttk.Notebook(self)
        self.selectFunction.grid()

        self["menu"] = MenuCM(self)

        self.protocol("WM_DELETE_WINDOW", self.closeFun)

        self.initialized = True
        path = optionGet("SelectedFilesDirectory",
                         os.path.join(os.getcwd(), "Stuff", "Selected files"), "str", True)
        loadFileStorage(self, os.path.join(path, "~last.files"))
        self.mainloop()


    def changeSlaves(self):
        "creates notepages whenever mode is changed or GUI is initialized"
        for child in self.selectFunction.tabs():
            self.selectFunction.forget(child)
            
        notepageWidth = 20
        self.selectFunction.add(self.processor, text = "{:^{}}".format("Process", notepageWidth))
        self.selectFunction.add(self.explorer, text = "{:^{}}".format("Explore", notepageWidth))
        self.selectFunction.add(self.controller, text = "{:^{}}".format("Control", notepageWidth))

        self.selectFunction.bind("<<NotebookTabChanged>>", lambda e: self.checkProcessing())


    def _askForSave(self, mode):
        "helper for asking to save files on exit (i.e. closeFun)"
        text = "Do you want to save {} files before leaving?".format(m.fullname[mode])
        answ = messagebox.askyesno(message = text, icon = "question", title = "Save files?")
        if answ:
            saveFileStorage(self, mode)


    def closeFun(self):
        "ask for saving files on exit"
        if not optionGet("Developer", False, 'bool', True):
            if doesFileStorageRequiresSave(self, m.mode):
                self._askForSave(m.mode)
            for mode in m.fs:
                if mode != m.mode and doesFileStorageRequiresSave(self, mode):
                    self._askForSave(mode)
        path = optionGet("SelectedFilesDirectory",
                         os.path.join(os.getcwd(), "Stuff", "Selected files"), "str", True)
        saveFileStorage(self, m.mode, os.path.join(path, "~last.files"))
        self.destroy()


    def changeTitle(self, mode):
        "changes the title of the GUI"
        self.title("CM Manager " + ".".join(version()) + "  (mode: {})".format(mode))


    def checkProcessing(self):
        """checks whether it is possible for processor and controller to process files and change
        states of buttons accordingly"""
        self.processor.checkProcessing()
        self.controller.checkProcessing()
        self.explorer.checkProcessing()

     
            

def main():
    if optionGet("Developer", False, 'bool', True):
        GUI()
    else:
        for directory in ["Bugs", "Logs", "Selected files"]:
            dirname = os.path.join(os.getcwd(), "Stuff", directory)
            if not os.path.exists(dirname):
                os.mkdir(dirname)
        filepath = os.path.join(os.getcwd(), "Stuff", "Bugs")
        writeTime = localtime()
        filename = os.path.join(filepath, strftime("%y_%m_%d_%H%M%S", writeTime) +
                                "_bugs" + ".txt")
        with open(filename, mode = "w") as bugfile:
            sys.stderr = bugfile
            GUI()



if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.dirname(os.getcwd())))
    main()
