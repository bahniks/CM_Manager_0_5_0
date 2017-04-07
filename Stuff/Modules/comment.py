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


from window import placeWindow
from optionget import optionGet


class Comment(Toplevel):
    "class used to adding and viewing comments"
    def __init__(self, root, files, correct = True):
        super().__init__(root)
               
        self.root = root
        self.fileStorage = self.root.fileStorage
        placeWindow(self, 574, 215)
        self.title("Comment")
        self.grab_set()
        self.focus_set()     

        if type(files) is str:
            files = [files]
        self.files = files
        if len(self.files) == 1:
            filename = self.files[0]
            self.comment = self.fileStorage.comments[filename]
            self.name = ttk.Label(self, text = filename)
        else:
            self.comment = ""
            self.name = ttk.Label(self, text = "{} files selected".format(len(self.files)))
        
        self.okBut = ttk.Button(self, text = "Ok", command = self.okFun)
        self.closeBut = ttk.Button(self, text = "Close", command = self.destroy)
        self.text = Text(self, height = 8, wrap = "word", width = 70)

        self.okBut.grid(column = 2, row = 3, pady = 2, padx = 10)
        self.closeBut.grid(column = 1, row = 3, pady = 2, padx = 10)
        self.name.grid(column = 0, row = 0, columnspan = 4, pady = 3, padx = 5)
        self.text.grid(column = 0, row = 2, columnspan = 4, pady = 2, padx = 5,
                       sticky = (N, S, E, W))

        if not correct:
            warning = "Warning: This file is not the one currently displayed!"
            self.warning = ttk.Label(self, text = warning)
            self.warning.grid(column = 0, row = 1, columnspan = 4, pady = 3, padx = 5)

        self.columnconfigure(0, weight = 1)
        self.columnconfigure(3, weight = 1)
        self.rowconfigure(2, weight = 1)
        
        self.text.insert("1.0", self.comment)
        self.text.bind("<3>", lambda e: self.popUp(e))
        self.text.focus_set()

    def okFun(self):
        "saves the comment in filestorage"
        comment = self.text.get("1.0", "end").strip()
        for file in self.files:
            if self.fileStorage.comments[file] and len(self.files) > 1:
                self.fileStorage.comments[file] += "\n" + comment
            else:
                self.fileStorage.comments[file] = comment
        self.root.refresh()
        self.destroy()

    def popUp(self, event):
        "pop-up menu for text widget"
        menu = Menu(self, tearoff = 0)
        menu.add_command(label = "Reset to the original comment", command = self.reset)
        menu.post(event.x_root, event.y_root)

    def reset(self):
        "resets the text to the original comment"
        self.text.delete("1.0", "end")
        self.text.insert("1.0", self.comment)


def commentColor():
    return optionGet("CommentColor", "grey90", 'str')





