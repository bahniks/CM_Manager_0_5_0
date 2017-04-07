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
from tkinter import ttk, messagebox
from urllib.request import urlopen
import webbrowser
import os


from controller import Controller
from explorer import Explorer
from processor import Processor
from options import OptionsCM, AdvancedOptions, GeneralOptions
from optionwrite import optionWrite
from optionget import optionGet
from helpcmm import HelpCM
from tools import saveFileStorage, loadFileStorage, addTags
from showtracks import ShowTracks
from window import placeWindow
from filestorage import FileStorage, ShowFiles
import version
import mode as m



class MenuCM(Menu):
    "menu of main window"
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        self.task = StringVar()
        self.task.set(optionGet("DefaultTask", "CM", 'str', general = True))
        self.changedTask()

        self.menu_file = Menu(self)
        self.menu_options = Menu(self)
        self.menu_tools = Menu(self)
        self.menu_show = Menu(self)
        self.menu_task = Menu(self)
        self.menu_help = Menu(self)
        
        menuWidth = 8
        self.add_cascade(menu = self.menu_file, label = "{:^{}}".format("File", menuWidth))
        self.add_cascade(menu = self.menu_options, label = "{:^{}}".format("Options", menuWidth))
        self.add_cascade(menu = self.menu_tools, label = "{:^{}}".format("Tools", menuWidth))
        self.add_cascade(menu = self.menu_show, label = "{:^{}}".format("Show", menuWidth))
        self.add_cascade(menu = self.menu_task, label = "{:^{}}".format("Task", menuWidth))
        self.add_cascade(menu = self.menu_help, label = "{:^{}}".format("Help", menuWidth))

        self.menu_file.add_command(label = "Load selected files", command = self.loadSavedFiles)
        self.menu_file.add_command(label = "Save selected files", command = self.saveLoadedFiles)
        self.menu_file.add_separator()
        self.menu_file.add_command(label = "Exit", command = self.exitCM)
        self.menu_options.add_command(label = m.fullname[m.mode] + " options",
                                      command = self.options)
        self.menu_options.add_command(label = "Parameter settings (" + m.fullname[m.mode] + ")",
                                      command = self.advOptions)
        self.menu_options.add_separator()
        self.menu_options.add_command(label = "General options", command = self.generalOptions)
        self.menu_options.add_separator()
        self.menu_options.add_command(label = "Reset all options", command = self.resetOptions)
        self.menu_tools.add_command(label = "Add tags", command = self.addTagsHelper)
        self.menu_show.add_command(label = "Show files", command = self.showFiles)
        self.menu_show.add_command(label = "Show tracks", command = self.showTracks)
        for task, name in m.fullname.items():
            self.menu_task.add_radiobutton(label = name, variable = self.task, value = task,
                                           command = self.changedTask)
        self.menu_help.add_command(label = "About", command = self.about)
        self.menu_help.add_command(label = "Citation", command = self.citation)
        self.menu_help.add_separator()
        self.menu_help.add_command(label = "Check for updates", command = self.checkUpdates)
        self.menu_help.add_separator()        
        self.menu_help.add_command(label = "Help", command = self.helpCM)

    def exitCM(self):
        self.root.closeFun()

    def checkUpdates(self):
        Updates(self)

    def citation(self):
        Citation(self)

    def options(self):
        OptionsCM(self.root)

    def advOptions(self):
        AdvancedOptions(self.root)

    def generalOptions(self):
        GeneralOptions(self.root)

    def saveLoadedFiles(self):
        saveFileStorage(self.root, m.mode)
        
    def loadSavedFiles(self):
        loadFileStorage(self.root)

    def addTagsHelper(self):
        try:
            addTags(self.root)
        except Exception as e:
            messagebox.showinfo(message = "Sorry, something went wrong.", detail = e,
                                title = "Error", icon = "error")

    def showFiles(self):
        tabid = self.root.selectFunction.index(self.root.selectFunction.select())
        ShowFiles(m.slaves[m.mode][0][tabid].fileStorageFrame, "arenafiles")

    def showTracks(self):
        if m.fs[m.mode]:
            tabid = self.root.selectFunction.index(self.root.selectFunction.select())
            root = m.slaves[m.mode][0][tabid].fileStorageFrame
            ShowTracks(root, m.fs[m.mode].arenafiles, m.fs[m.mode].arenafiles[0])
        else:
            messagebox.showinfo(message = "You have not selected any files.",
                                title = "No files selected", icon = "info")

    def resetOptions(self):
        text = ("Are you sure that you want to reset all options (including parameter settings)"
                " to default settings?")
        answ = messagebox.askyesno(message = text, title = "Reset options?", icon = "question",
                                   default = "no")
        filename = os.path.join(os.getcwd(), "Stuff", "Options.txt")
        if answ and os.path.exists(filename):
            os.remove(filename)     

    def helpCM(self):
        try:
            HelpCM(self.root)
        except Exception as e:
            messagebox.showinfo(message = e, title = "Error", icon = "error")
            
    def about(self):
        AboutCM(self.root)
        
    def changedTask(self):
        """called when mode is changed
            changes names in Options menu
            exchanges Process, Explore, Control notepages
            calls m.changeMode
            puts old filestorage in m.fs[m.mode] and the self.root.[...].fileStorage is reassigned
            saves old slaves of GUI's notebook and loads new
            renames GUI and saves the mode selection to options
        """
        if self.task.get() != m.mode:
            if m.mode:
                oldname = m.fullname[m.mode]
                newname = m.fullname[self.task.get()]
                self.menu_options.entryconfigure("Parameter settings (" + oldname + ")",
                                                 label = "Parameter settings (" + newname + ")")
                self.menu_options.entryconfigure(oldname + " options",
                                                 label = newname + " options")
            
            if m.mode in m.slaves:
                m.slaves[m.mode][1] = self.root.selectFunction.select()
            
            m.changeMode(self.task.get())
            
            if m.mode not in m.fs:
                m.fs[m.mode] = FileStorage()
            self.root.selectFunction.fileStorage = m.fs[m.mode]
            
            if m.mode not in m.slaves:
                m.slaves[m.mode] = [m.Slaves(Processor(self.root.selectFunction),
                                             Explorer(self.root.selectFunction),
                                             Controller(self.root.selectFunction)
                                             ),
                                    None
                                    ]
            self.root.processor = m.slaves[m.mode][0].processor
            self.root.explorer = m.slaves[m.mode][0].explorer
            self.root.controller = m.slaves[m.mode][0].controller            
            self.root.changeSlaves()
            if m.slaves[m.mode][1]:
                self.root.selectFunction.select(m.slaves[m.mode][1])

            self.root.changeTitle(m.name)
            
            optionWrite("DefaultTask", "'" + self.task.get() + "'", general = True)   
        

class AboutCM(Toplevel):
    "about window reachable from menu"
    def __init__(self, root):
        super().__init__(root)
        self["padx"] = 4
        self["pady"] = 4

        self.version = ".".join(version.version())        
        self.title("About")
        self.resizable(FALSE, FALSE)
        placeWindow(self, 488, 303)
        
        text = ("Carousel Maze Manager\nVersion " + self.version + "\n" + version.date() + "\n\n"
                "Copyright "+ version.copyleft() + " Štěpán Bahník\nbahniks@seznam.cz\n\n"
                "This program comes with ABSOLUTELY NO WARRANTY.\nThis is free software, and "
                "you are welcome to redistribute\nit under certain conditions; click ")
        line10 = "here"
        line11 = " for details.\n\n"
        
        self.aboutText = Text(self, height = 15, width = 58, relief = "flat",
                              background = self.cget("background"))
        self.aboutText.grid(column = 0, row = 0, padx = 6, pady = 6)
       
        self.aboutText.insert("end", text)
        self.aboutText.insert("end", line10, "link")
        self.aboutText.insert("end", line11)

        self.aboutText.tag_configure("link", foreground = "blue")
        self.aboutText.tag_bind("link", "<1>", lambda e: self.link(e))
        self.aboutText.tag_bind("link", "<Enter>", lambda e: self._enter(e))
        self.aboutText.tag_bind("link", "<Leave>", lambda e: self._leave(e))

        filepath = os.path.join(os.getcwd(), "Stuff", "Modules", "GNUlogo.gif")
        self.logo = PhotoImage(file = filepath)
        self.aboutText.insert("end", " "*21)
        self.aboutText.image_create("end", image = self.logo)
        
        self.aboutExit = ttk.Button(self, text = "Close", command = self.aboutExit)
        self.aboutExit.grid(column = 0, row = 1, pady = 7)

    def aboutExit(self):
        self.destroy()

    def _enter(self, event):
        "changes cursor when entering link"
        self.aboutText.config(cursor = "hand2")

    def _leave(self, event):
        "changes cursor when leaving link"
        self.aboutText.config(cursor = "")
        
    def link(self, event):
        "opens browser with linked page"
        link = "http://www.gnu.org/licenses/gpl-3.0.html"
        try:
            webbrowser.open(link)
        except Exception:
            self.bell()



class Updates(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self["padx"] = 4
        self["pady"] = 4

        self.version = version.version()        
        self.title("Updates")
        self.resizable(FALSE, FALSE)
        placeWindow(self, 488, 127)

        try:
            newVersion = self.checkNewVersion()
            if newVersion:
                available = ("There is a new version ({}.{}.{}) available.\n".format(*newVersion) +
                             "Restart CMM to install the update.")
                optionWrite("DontShowVersion", self.version)
            else:
                available = "There is no new version available."
        except Exception:
            available = "Unable to get information about the newest version."

        text = "Your current version is {1}.{2}.{3}.\n\n{0}".format(available, *self.version)

        self.text = Text(self, height = 4, width = 58, relief = "flat",
                         background = self.cget("background"))
        self.text.grid(column = 0, row = 0, padx = 6, pady = 6)   
        self.text.insert("end", text)

        self.close = ttk.Button(self, text = "Close", command = self.destroy)
        self.close.grid(column = 0, row = 1, pady = 7)

    def returnSiteContent(self, link):
        "return text obtained from web site"
        site = urlopen(link)
        text = site.read()
        site.close()
        text = str(text)[2:-1]
        return text

    def checkNewVersion(self):
        "checks whether there is a new version available"
        url = "http://www.cmmanagerweb.appspot.com/version"
        newVersion = self.returnSiteContent(url).split(".")
        for i in range(3):
            if int(newVersion[i]) > int(self.version[i]):
                return newVersion
            elif int(newVersion[i]) < int(self.version[i]):
                return None
        else:
            return None


class Citation(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self["padx"] = 4
        self["pady"] = 4
      
        self.title("Citation")
        self.resizable(FALSE, FALSE)
        placeWindow(self, 488, 135)

        v = version.version()
        year = version.date().split()[2]
        url = "https://github.com/bahniks/CM_Manager_{}_{}_{}".format(*v)
        text = ("Please cite this software as:\n\n" +
                "Bahník, Š. ({}). Carousel Maze Manager (Version {}.{}.{}) ".format(year, *v) +
                "[Software]. Available from {}".format(url))

        self.text = Text(self, height = 5, width = 70, relief = "flat", wrap = "word",
                         background = self.cget("background"))
        self.text.grid(column = 0, row = 0, padx = 6, pady = 6)   
        self.text.insert("end", text)

        self.close = ttk.Button(self, text = "Close", command = self.destroy)
        self.close.grid(column = 0, row = 1, pady = 7)



def main():
    testGUI = Tk()
    testGUI["menu"] = MenuCM(testGUI)
    testGUI.mainloop()


if __name__ == "__main__": main()
