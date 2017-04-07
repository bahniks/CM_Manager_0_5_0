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

from tkinter.filedialog import askopenfilenames, asksaveasfilename, askopenfilename, askdirectory
from tkinter import *
from os.path import basename
from tkinter import ttk, messagebox

import os.path
import os


from window import placeWindow


class HelpCM(Toplevel):
    "help window reachable from menu"
    def __init__(self, root):
        if not os.path.exists(os.path.join(os.getcwd(), "Stuff", "Help")):
            messagebox.showinfo(message = "Folder 'Help' doesn't exist in the " + 
                                "'Stuff' directory!", title = "Error", icon = "error")
            return
        
        super().__init__(root)
        self["padx"] = 7
        self["pady"] = 7
        
        self.title("Help")
        placeWindow(self, 806, 699)
        self.resizable(FALSE, FALSE)

        self.goneThrough = [[""], 0] # variable containing lists of items gone through and their
                                     # position (e.g. [["", 0], ["Parameters", 1], ["Shocks", 2]])
        self.linkMapping = {} # variable containing texts and items that the texts refer to

        # widgets                                    
        self.text = Text(self, width = 70, height = 40, wrap = "word", cursor = "")
        self.text.grid(column = 1, row = 1, pady = 4)

        self.scroll = ttk.Scrollbar(self, orient = VERTICAL, command = self.text.yview)
        self.scroll.grid(column = 2, row = 1, pady = 4, sticky = (N, S, W))
        self.text.configure(yscrollcommand = self.scroll.set)

        self.buttonBar = ttk.Frame(self)
        self.buttonBar.grid(column = 1, row = 0, pady = 4, sticky = (N, S, E, W))
        self.buttonBar.columnconfigure(2, weight = 1)

        self.searchBut = ttk.Button(self.buttonBar, text = "Search", command = self.searchFun)
        self.searchBut.grid(column = 4, row = 0)

        self.searchTerm = StringVar()
        self.searchEntry = ttk.Entry(self.buttonBar, width = 30, justify = "left",
                                     textvariable = self.searchTerm)
        self.searchEntry.grid(column = 3, row = 0, padx = 4)

        self.returnBut = ttk.Button(self.buttonBar, text = "Return", command = self.returnFun)
        self.returnBut.grid(column = 0, row = 0, padx = 4)

        self.forwardBut = ttk.Button(self.buttonBar, text = "Forward", command = self.forwardFun)
        self.forwardBut.grid(column = 1, row = 0, padx = 4)       

        self.tree = ttk.Treeview(self, selectmode = "browse")
        self.tree.grid(column = 0, row = 0, rowspan = 2, pady = 4, padx = 4,
                       sticky = (N, S, E, W))

        self.makeTree()
        self.makeText("Help") # initial text is from file 'Help'

        self.tree.bind("<1>", self.treeSelect)


    def makeTree(self):
        "makes tree of existing help pages"
        files = os.listdir(os.path.join(os.getcwd(), "Stuff", "Help"))

        items = []
        for file in sorted(files):
            if file == "Help":
                continue                
            filename = os.path.join(os.getcwd(), "Stuff", "Help", file)
            infile = open(filename, mode = "r")
            parent = infile.readline()[1:].rstrip()
            if parent:
                items.append([parent, os.path.splitext(file)[0]])
        branches = []

        # if parent of item is a number, item is inserted in the top level of the tree  
        for item in items:
            if 47 < ord(item[0][0]) < 58:
                self.tree.insert("", item[0], item[1], text = item[1].replace("_", " "))
                branches.append(item[1])
                
        # inserts children of every already inserted parent
        for rep in range(6): # maximal number of levels of the tree
            level = []
            for item in items:
                if item[1] in branches:
                    continue
                elif item[0] in branches:
                    self.tree.insert(item[0], "end", item[1], text = item[1].replace("_", " "))
                    level.append(item[1])
                else:
                    pass
            branches = branches + level                        


    def searchFun(self, word = "noWord"):
        """searches for a word set in self.searchTerm variable
            word parameter is important only for walk through pages that were already accessed
                - which is for functions 'returnFun' and 'forwardFun'"""
        
        files = os.listdir(os.path.join(os.getcwd(), "Stuff", "Help"))

        # searched contains full search term, searchedWords contains separated words
        if word != "noWord":
            searched = word.lower()             
        else:
            searched = self.searchTerm.get().lower()                
            self.goneThrough[0].append("$Search$" + searched)
            self.goneThrough[1] += 1
        searchedWords = searched.split()

        self.text["state"] = "normal"
        self.text.delete("1.0", "end")

        self.text.insert("end", "\n")

        # searched term must have at least 3 characters
        if len(searched) < 3:
            self.text.insert("end", " Search term is too short.")
            self.text["state"] = "disabled"
            return              

        found = [] # which items contain searched term (appended in form: [item, weight])

        # search in files
        for file in sorted(files):
            filename = os.path.join(os.getcwd(), "Stuff", "Help", file)
            infile = open(filename, mode = "r")
            inText = False # is file (i.e. item) already in 'found' variable
            maxLength = max([len(l) for l in searchedWords]) # maximum word length
            
            for searchedWord in searchedWords:
                # if a word is shorter than 3 characters, it doesn't count (prepositions etc.)
                if len(searchedWord) < 3 and maxLength > 2:
                    continue
                # if a word is in item name, 2 is added to weight
                if searchedWord in file.lower() and len(searchedWord) > 2:
                    if inText:
                        found[-1][1] = found[-1][1] + 2
                    else:
                        inText = True
                        found.append([os.path.splitext(file)[0], 2])                                

                for count, line in enumerate(infile):
                    # skips the first two lines (header)
                    if count < 2:
                        continue
                    # if searched term contains 2 and more words and they are in line
                    # positioned one after another, 1 is added to weight (in fact this is done
                    # for every word, consequently, 1 is added to weight for every word in
                    # searched term)
                    if len(searchedWords) > 1 and searched in line:
                        if inText:
                            found[-1][1] = found[-1][1] + 1
                        else:
                            inText = True
                            found.append([os.path.splitext(file)[0], 1])
                            
                    for word in line.split():
                        # if a word is marked, it is processed accordingly
                        if len(word) and word[0] == "$":
                            splitted = word.split("$")
                            if len(splitted) > 2:
                                word = splitted[2].replace("_", " ")
                            else:
                                continue
                        # 1 is addded to weight if a searched word is contained in word
                        if searched in word.lower():
                            if inText:
                                found[-1][1] = found[-1][1] + 1
                            else:
                                inText = True
                                found.append([os.path.splitext(file)[0], 1])
                
        found.sort(key = lambda e: e[1], reverse = True) #sorts items according to their weight

        if len(found) == 0:
            self.text.insert("end", " No match found.")

        # if searched term is in item name, it is in top position
        for count, file in enumerate(found):
            if searched in file[0].lower():
                self.text.insert("end", " ")
                self.text.insert("end", file[0].replace("_", " "), ("link"))
                self.text.insert("end", "\n\n")                    
                found.pop(count)
                
        for file in found:
            self.text.insert("end", " ")
            self.text.insert("end", file[0].replace("_", " "), ("link"))
            self.text.insert("end", "\n\n")
            
        self.text["state"] = "disabled"
            
        self.text.tag_configure("link", foreground = "blue")
        self.text.tag_bind("link", "<1>", link)                


    def returnFun(self):
        "makes a step back in items gone through"
        if self.goneThrough[1] != 0: 
            self.goneThrough[1] -= 1
            item = self.goneThrough[0][self.goneThrough[1]]
            if item == "":
                self.makeText("Help")
                self.tree.selection_set(item)
            # show search results if last item accessed was search
            elif len(item) > 8 and item[0:8] == "$Search$":
                self.searchFun(word = item[8:])
            else:
                self.makeText(item)           
                self.tree.selection_set(item)


    def forwardFun(self):
        "makes a step forward in items gone through"
        if self.goneThrough[1] != len(self.goneThrough[0]) - 1:
            self.goneThrough[1] += 1
            item = self.goneThrough[0][self.goneThrough[1]]
            if len(item) > 8 and item[0:8] == "$Search$":
                self.searchFun(word = item[8:])
            else:
                self.tree.selection_set(item)
                self.makeText(item)                


    def makeText(self, item):
        "takes text from a file and displays it in a 'text' widget (takes care of formatting)"
        file = os.path.join(os.getcwd(), "Stuff", "Help", item.replace(" ", "_") + ".txt")

        self.text["state"] = "normal"

        self.text.delete("1.0", "end")
        
        infile = open(file, mode = "r")
        
        content = []
        for count, line in enumerate(infile):
            if count < 2:
                continue
            words = line.rstrip().split(" ")
            content = content + words

        self.text.insert("end", item.replace("_", " ") + "\n", ("header"))
        
        for word in content:
            if len(word) and word[0] == "$":
                divided = word.split("$")
                if divided[1][0] == "n": # $nn - adds new lines
                    self.text.insert("end", "\n" * divided[1].count("n"))
                elif divided[1] and divided[1][0] in ".,';:-": # interpunctions
                    self.text.insert("end", divided[1])
                elif divided[1] == "s": # $s$See_also: - makes subheader and new line
                    self.text.insert("end", divided[2], ("subheader"))
                    self.text.insert("end", "\n")
                elif divided[1] == "b": # $b$Bold_text - bold formating
                    self.text.insert("end", divided[2], ("bold"))
                    self.text.insert("end", " ")
                elif divided[1] == "l": # $l$link$Linked_item - $Linked_item not needed if
                                        # link corresponds to linked item
                    self.text.insert("end", divided[2].replace("_", " "), ("link"))
                    if len(divided) == 4:
                        self.linkMapping[divided[2].replace(" ", "_").capitalize()]\
                        = divided[3]
                    self.text.insert("end", " ")
            else:
                word = word + " "
                self.text.insert("end", word)

        # 'See also:' is automatically added to the end
        self.text.insert("end", "\n\n")                
        self.text.insert("end", "See also:", ("subheader"))

        # first the parent is added as a link
        if item != "Help":
            parent = self.tree.parent(item)
            if parent:
                self.text.insert("end", "\n")
                self.text.insert("end", "- ")
                self.text.insert("end", parent.replace("_", " "), ("link"))
        # next childen are added as links
            children = self.tree.get_children(item)
            if children:
                for child in children:
                    self.text.insert("end", "\n")
                    self.text.insert("end", "+ ")
                    self.text.insert("end", child.replace("_", " "), ("link"))

        # configuration of tagged text
        self.text.tag_configure("header", font = "TkDefaultFont 10 bold")
        self.text.tag_configure("subheader", font = "TkDefaultFont 9 bold")
        self.text.tag_configure("link", foreground = "blue")
        self.text.tag_configure("bold", font = "TkDefaultFont 9 bold")

        self.text.tag_bind("link", "<1>", self.link)
            
        self.text["state"] = "disabled"                    

             
    def treeSelect(self, event):
        "called when tree item is clicked on"
        item = self.tree.identify("item", event.x, event.y)
        if item:
            self.makeText(item)
            if self.tree.get_children(item):
                self.tree.see(self.tree.get_children(item)[0])
            self.goneThrough[0] = self.goneThrough[0][:self.goneThrough[1] + 1]
            self.goneThrough[0].append(item)
            self.goneThrough[1] += 1


    def link(self, event):
        "function that is called when linked term is clicked on"
        item = self.text.get(self.text.tag_prevrange("link", "current")[0],
                             self.text.tag_prevrange("link",
                                                     "current")[1]).replace(" ",
                                                                            "_").capitalize()
        # needed for mapped links (i.e. those in format: $l$distance$Total_distance)
        if item in self.linkMapping.keys(): 
            item = self.linkMapping[item]
        self.makeText(item)
        self.goneThrough[0] = self.goneThrough[0][:self.goneThrough[1] + 1]
        self.goneThrough[0].append(item)
        self.goneThrough[1] += 1
        self.tree.selection_set(item)
        self.tree.see(item)






def main():
    os.chdir("\\".join(os.getcwd().split("\\")[:-2]))
    testGUI = Tk()
    HelpCM(testGUI)
    testGUI.mainloop()    

if __name__ == "__main__": main()
