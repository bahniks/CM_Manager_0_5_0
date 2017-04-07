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

from math import radians, cos, sin
from tkinter import *


import os
import webbrowser # for testing


from optionget import optionGet
from optionwrite import optionWrite
from graphs import getGraphTypes, Graphs, SvgGraph, SpeedGraph, DistanceFromCenterGraph
from graphs import AngleGraph, DistanceFromPlatformGraph, DistanceFromRobotGraph
from window import placeWindow
import mode as m


def svgSave(cm, filename, what, root):
    "saves image for one file"
    directory = optionGet("ImageDirectory", os.getcwd(), "str", True)

    if what == "both frames":
        components = ["arena", "room"]
    elif what == "arena frame":
        components = ["arena"]
    elif what == "room frame":
        components = ["room"]
    elif what == "graph":
        components = ["graph"]
    elif what == "all":
        components = ["arena", "room", "graph"]

    svg = SVG(cm, components, root)
    file = os.path.splitext(os.path.basename(filename))[0] + "_" + what.replace(" ", "_") + ".svg"
    svg.save(os.path.join(directory, file))
    #webbrowser.open_new(os.path.join(directory, file)) # for testing

        

class ImagesOptions(Toplevel):
    def __init__(self, root):
        super().__init__(root)
        self.root = root
        placeWindow(self, 598, 208)
        self.title("Images options")
        self.grab_set()
        self.focus_set()     
        self.resizable(False, False)

        self.oFrame = ttk.Frame(self)
        self.oFrame.grid(column = 0, columnspan = 3, row = 0)

        options = (("Scale", ("LastImageScale", 1, ["int", "float"])),
                   ("Main title ('default' for filename)", ("LastImageMain", "default", "str")),
                   ("Horizontal gap", ("LastImageXgap", 10, ["int", "float"])),
                   ("Vertical gap", ("LastImageYgap", 10, ["int", "float"])),
                   ("x-axis title", ("LastImageXlab", "Time", "str")),
                   ("y-axis title (smart 'default')", ("LastImageYlab", "default", "str")),
                   ("x-axis ticks", ("LastImageXticks", True, "bool")),
                   ("y-axis ticks", ("LastImageYticks", True, "bool")))
        self.options = options

        self.opts = []
        entryWidth = 10

        for row, option in enumerate(options):
            self.opts.append({})
            var = BooleanVar if option[1][2] == 'bool' else StringVar
            self.opts[row]["variable"] = var()
            current = optionGet(*option[1])
            if type(current) == str:
                current = "'" + current + "'"
            self.opts[row]["variable"].set(current)
            self.opts[row]["label"] = ttk.Label(self.oFrame, text = option[0])
            self.opts[row]["label"].grid(column = 0, row = row, pady = 2, sticky = E)
            if option[1][2] == 'bool':
                self.opts[row]["input"] = ttk.Checkbutton(self.oFrame, onvalue = True,
                                                          offvalue = False,
                                                          variable = self.opts[row]["variable"])
            else:
                self.opts[row]["input"] = ttk.Entry(self.oFrame, width = entryWidth,
                                                    justify = 'right',
                                                    textvariable = self.opts[row]["variable"])
            self.opts[row]["input"].grid(column = 1, row = row, padx = 2, pady = 2)
            
        self.okBut = ttk.Button(self, text = "Ok", command = self.okFun)
        self.okBut.grid(column = 2, row = 1, padx = 3, pady = 4)
        self.cancelBut = ttk.Button(self, text = "Cancel", command = self.cancelFun)    
        self.cancelBut.grid(column = 1, row = 1, padx = 3, pady = 4)
        self.resetBut = ttk.Button(self, text = "Reset", command = self.resetFun)
        self.resetBut.grid(column = 0, row = 1, padx = 3, pady = 4)


    def okFun(self):
        for row, option in enumerate(self.options):
            value = str(self.opts[row]["variable"].get())
            if option[1][2] == "bool":
                value = bool(eval(value))
            elif option[1][2] != "str":
                value = eval(value)
            else:
                if not value:
                    value = ""
                else:
                    value.replace('"', "'")
                    if not value.endswith("'"):
                        value += "'"
                    if not value.startswith("'"):
                        value = "'" + value
            optionWrite(option[1][0], value)
        self.destroy()


    def resetFun(self):
        for count, option in enumerate(self.options):
            optionWrite(option[1][0], option[1][1])
            self.opts[count]["variable"].set(option[1][1])


    def cancelFun(self):
        self.destroy()

        

class SVG():
    "represents .svg file - text of the file is stored in self.content"
    def __init__(self, cm, components, root):
        self.start = int(root.timeFrame.startTimeVar.get())
        self.end = int(root.timeFrame.timeVar.get())
        self.parameter = root.graphParameter.get()
        if self.parameter == "nothing":
            self.parameter = ""

        self.cm = cm
        self.components = components
        self.scale = optionGet("LastImageScale", 1, ["int", "float"])
        self.main = optionGet("LastImageMain", "default", "str")
        self.xgap = optionGet("LastImageXgap", 10, ["int", "float"])
        self.ygap = optionGet("LastImageYgap", 10, ["int", "float"])
        self.xlab = optionGet("LastImageXlab", "Time", "str")
        self.ylab = optionGet("LastImageYlab", "default", "str")
        self.xticks = optionGet("LastImageXticks", True, "bool")
        self.yticks = optionGet("LastImageYticks", True, "bool")

        self.addComponents()
        self.computeSize()
        self.addIntro()

        graphWidth = self.x[5] - self.x[2]
        self.graph = eval(root.graphTypeVar.get()[:-5] +
                          'root, cm, purpose = "svg", width = graphWidth)')

        for component in self.components:           
            if component in ["xgap", "ygap"]:
                continue
            elif component == "main":
                self.addMain()
            elif component == "arena":
                self.addArena()
            elif component == "room":
                self.addRoom()
            elif component == "graph":
                self.addGraph()
            elif component == "xticks" and "graph" in self.components:
                self.addXticks()
            elif component == "yticks" and "graph" in self.components:
                self.addYticks()
            elif component == "xlab" and "graph" in self.components:
                self.addXlab()
            elif component == "ylab" and "graph" in self.components:
                self.addYlab()
                

    def addComponents(self):
        if self.main:
            self.components.append("main")
            if self.main == "default":
                self.main = os.path.basename(self.cm.nameA)
        if self.xgap and "room" in self.components and "arena" in self.components:
            self.components.append("xgap")
        if self.ygap and "graph" in self.components and "arena" in self.components:
            self.components.append("ygap")
        if self.xticks and "graph" in self.components:
            self.components.append("xticks")
        if self.yticks and "graph" in self.components:
            self.components.append("yticks")
        if self.xlab.strip() and "graph" in self.components:
            self.components.append("xlab")
        if self.ylab.strip() and "graph" in self.components:
            self.components.append("ylab")


    def computeSize(self):
        x = [0] * 6
        y = [0] * 7
        # sizes [(x.size, column, columnspan), (y.size, row)]
        sizes = {"main": [(0, 0), (25, 1)],
                 "arena": [(300, 3), (300, 2)],
                 "room": [(300, 5), (300, 2)],
                 "graph": [(600, 5, 3), (120, 4)],
                 "xgap": [(self.xgap, 4), (0, 0)],
                 "ygap": [(0, 0), (self.ygap, 3)],
                 "xticks": [(0, 0), (10, 5)],
                 "yticks": [(20, 2), (0, 0)],
                 "xlab": [(0, 0), (15, 6)],
                 "ylab": [(30, 1), (0, 0)]
                 }
        for component in self.components:
            xs, ys = sizes[component]
            xlen = xs[2] if len(xs) == 3 else 1 
            difx = (x[max((xs[1] - xlen, 0))] + xs[0]) - x[xs[1]]
            dify = (y[max((ys[1]-1, 0))] + ys[0]) - y[ys[1]]
            for i in range(max((1, xs[1])), len(x)):
                x[i] += difx
            for i in range(max((1, ys[1])), len(y)):
                y[i] += dify
        self.x = x
        self.y = y


    def addIntro(self):
        t1 = '<svg viewbox = "0 0 {} {}" xmlns="http://www.w3.org/2000/svg">\n'
        self.content = t1.format(self.x[-1] * self.scale, self.y[-1] * self.scale)
        self.content += '<g transform="scale({0},{0})">\n'.format(self.scale)
        self.content += '<rect style="stroke:white;fill:none" x="0" y="0" ' + \
                        'width="{}" height="{}" />\n'.format(self.x[-1], self.y[-1])

    def add(self, new, x, y):
        self.content += '<g transform="translate({0},{1})">\n'.format(self.x[x],
                                                                      self.y[y])
        self.content += new + "\n"
        self.content += '</g>\n'        


    def addMain(self):
        x = (self.x[5] - self.x[2]) / 2
        main = ('<text x="{0}" y="18" font-size="15" text-anchor="middle" '
                'fill="black">{1}</text>'.format(x, self.main))
        self.add(main, 2, 0)


    def addArena(self):
        self.add(self.addTrack(slice(7,9), places = False), 2, 1)


    def addRoom(self):
        self.add(self.addTrack(slice(2,4), shocks = True), 4, 1)


    def addTrack(self, indices, places = True, shocks = False):
        "adds text into sefl.content corresponding to track from one frame of AAPA"

        track = '<rect style="stroke:black;fill:none" x="0" y="0" width="300" height="300" />\n'

        start = self.cm.findStart(self.start)
        time = self.end * 60000

        if "CM" in m.mode:
            r = self.cm.radius
            track += '<g transform="translate({0},{0})">\n'.format(150 - r)

        if places:
            track += self.addPlaces()

        track += '<polyline points="'        

        prev = (0, 0)
        shock = False
        shockPositions = []
        for line in self.cm.data[start:]:
            if line[1] > time:
                break
            positions = line[indices]
            if positions != prev:
                track += ",".join(map(str, positions)) + " "
            if line[6] > 0:
                if not shock:
                    shock = True
                    shockPositions.append(positions)
            else:
                shock = False                        
            prev = positions

        track += '" style = "fill:none;stroke:black"/>\n'

        if shocks and shockPositions:
            track += self.addShocks(shockPositions)

        track += self.addBoundary()

        if "CM" in m.mode:
            track += '</g>\n'
            
        return track


    def addPlaces(self):
        angle = self.cm.centerAngle
        width = self.cm.width
        r = self.cm.radius
        a1 = radians(angle - (width / 2))
        a2 = radians(angle + (width / 2))
        Sx1, Sy1 = r + (cos(a1) * r), r - (sin(a1) * r)
        Sx2, Sy2 = r + (cos(a2) * r), r - (sin(a2) * r)
        places = '<polyline fill="none" stroke="red" stroke-width="1.5" ' +\
                 'points="{},{} {},{} {},{}"/>\n'.format(Sx1, Sy1, r, r, Sx2, Sy2)
        return places


    def addShocks(self, positions):
        shocks = ""
        for position in positions:
            shocks += '<circle fill="none" stroke="red" stroke-width="1.5" ' +\
                     'cx="{}" cy="{}" r="3" />\n'.format(*position)
        return shocks


    def addBoundary(self):
        r = self.cm.radius
        bound = '<circle fill="none" stroke="black" cx="{0}" cy="{0}" r="{0}" />\n'.format(r) 
        return bound    


    def addGraph(self):
        size = (self.x[5] - self.x[2], 120)
        yCoordinates, maxY, furtherText = self.graph.saveGraph(self.cm)
        
        graph = ""
        graph += self.addParameter()
        graph += ('<rect style="stroke:black;fill:none" x="0" y="0" '
                  'width="{0}" height="{1}" />\n'.format(size[0], size[1]))
        graph += furtherText

        points = []
        if yCoordinates:
            length = len(yCoordinates) - 1
            for count, y in enumerate(yCoordinates):       
                points.append(((count * size[0]) / length, size[1] - ((y * size[1]) / maxY)))

        if points:
            graph += '<polyline points="'
            for pair in points:
                graph += ",".join(map(str, pair)) + " "      
            graph += '" style = "fill:none;stroke:black"/>\n'

        self.add(graph, 2, 3)


    def addParameter(self):
        if not self.parameter:
            return ""
        else:
            text = self.graph.drawParameter(self.cm, self.parameter, purpose = "svg")
            return text


    def addXticks(self):
        unit = "min"
        time = self.end - self.start
        if time < 3:
            time *= 60
            unit = "s"
        for div in [5, 4, 7, 6, 3]:
            if time % div == 0:
                break
        else:
            div = 4
        ticks = [(time*i / div) + self.start for i in range(div + 1)]
        ticks = [int(tick) if abs(tick - int(tick)) < 0.01 else round(tick, 2) for tick in ticks]
        labels = [str(tick) + " " + unit for tick in ticks]

        text = ""
        for tick, label in zip(ticks, labels):
            x = (tick - self.start)/time * (self.x[5] - self.x[2])
            text += ('<text x="{0}" y="10" font-size="12" text-anchor="middle" '
                     'fill="black">{1}</text>\n'.format(x, label))
            text += '<line x1="{0}" y1="{1}" x2="{0}" y2="{2}" stroke="black"/>\n'.format(x, -4, -10)                            

        self.add(text, 2, 5)
        

    def addYticks(self):
        at, labels = self.graph.addYticks()
        tick = '<line x1="{0}" y1="{1}" x2="{2}" y2="{1}" stroke="black"/>\n'
        label = '<text x="{}" y="{}" font-size="12" text-anchor="end" fill="black">{}</text>\n'
        xdif = self.x[2] - self.x[1]
        ydif = self.y[3] - self.y[4]
        yticks = ""
        for y, lab in zip(at, labels):
            yticks += tick.format(xdif, y*ydif - ydif, xdif - 6)
            yticks += label.format(xdif - 10, y*ydif - ydif + 4, lab)
        self.add(yticks, 1, 3)


    def addXlab(self):
        x = (self.x[5] - self.x[2]) / 2
        xlab = ('<text x="{0}" y="15" font-size="15" text-anchor="middle" '
                'fill="black">{1}</text>'.format(x, self.xlab))
        self.add(xlab, 2, 6)


    def addYlab(self):
        if self.ylab == "default":
            self.ylab = self.graph.getYlabel()
        y = (self.y[4] - self.y[3]) / 2 
        ylab = ('<text x="0" y="{0}" font-size="15" text-anchor="middle" fill="black" '
                'transform="translate({1},{0}) rotate(270)">{2}</text>'.format(y, -y+15, self.ylab))
        self.add(ylab, 0, 3)
    

    def save(self, file):
        "closes tags and saves self.content into a file"
        self.content += '</g>\n'
        self.content += "</svg>"
        infile = open(file, mode = "w")
        infile.write(self.content)
        infile.close()        



def main():
    pass


if __name__ == "__main__": main()
