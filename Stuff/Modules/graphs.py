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
from math import degrees, atan2, floor, ceil

from optionget import optionGet
import mode as m


def getGraphTypes():
    "returns types of graphs used in Processor class as a list (with their respective methods)"
    types = [["Angle", "AngleGraph(self)"],
             ["Distance from center", "DistanceFromCenterGraph(self)"],
             ["Speed", "SpeedGraph(self)"]             
             ]
    if m.mode == "OF":
        types[1] = ["Proximity to side", "DistanceFromCenterGraph(self)"]
    elif m.mode == "MWM":
        types.insert(2, ["Distance from platform", "DistanceFromPlatformGraph(self)"])
    elif m.mode == "RA":
        types.insert(2, ["Distance from robot", "DistanceFromRobotGraph(self)"])
    return types



class Graphs(Canvas):
    "parent class for all 'wide' graphs in Explore page"
    def __init__(self, parent, width = 600, height = 120, **kwargs):
        super().__init__(parent)
        self["width"] = width
        self["height"] = height
        self["background"] = "white"
        self.height = height
        self.width = width
        self.drawnParameter = None    
        self.parent = parent
        

    def changedTime(self, newTime):
        "changes position of a time measure on a graph"
        x = (newTime - self.minTime) * self.width / (self.maxTime - self.minTime)
        if x < 2:
            x = 2
        self.coords("timeMeasure", (x, 0, x, self.height))


    def CM_loaded(self, CM, minTime, maxTime, initTime):
        "basic method called when a file is loaded"
        # time measure
        self.create_line((2, 0, 2, self.height), fill = "red", tags = "timeMeasure")

        # maximum time in miliseconds
        if maxTime == "max":
            self.maxTime = CM.data[-1][1]
        else:
            self.maxTime = maxTime

        if minTime == "min":
            self.minTime = CM.data[0][1]
        else:
            self.minTime = minTime

        # set time measure
        self.changedTime(initTime)

        self.drawParameter(cm = CM, parameter = self.drawnParameter)


    def drawParameter(self, cm, parameter, purpose = "graph"):
        "computes selected parameter to be drawn on top of the graph"
        if self.drawnParameter and purpose == "graph":
            self.delete("parameter")

        self.drawnParameter = parameter

        if parameter == "periodicity":
            periodicity = cm.getPeriodicity(forGraph = True, time = self.maxTime / 60000,
                                            startTime = self.minTime / 60000,
                                            minSpeed = optionGet('MinSpeedPeriodicity',
                                                                 10, ['int', 'float']),
                                            skip = optionGet('SkipPeriodicity', 12, ['int']),
                                            smooth = optionGet('SmoothPeriodicity', 2, ['int']),
                                            minTime = optionGet('MinTimePeriodicity', 9,
                                                                ['int', 'float', 'list']))
            return self.drawPeriods(periodicity)
        elif parameter == "immobility":
            immobility = cm.getMaxTimeOfImmobility(forGraph = True,
                                                   time = self.maxTime / 60000,
                                                   startTime = self.minTime / 60000,
                                                   minSpeed = optionGet('MinSpeedMaxTimeImmobility',
                                                                        10, ['int', 'float']),
                                                   skip = optionGet('SkipMaxTimeImmobility',
                                                                    12, 'int'),
                                                   smooth = optionGet('SmoothMaxTimeImmobility',
                                                                      2, 'int'))
            return self.drawPeriods(immobility)
        elif parameter == "mobility":
            immobility = cm.getMaxTimeOfImmobility(forGraph = True, time = self.maxTime / 60000,
                                                   startTime = self.minTime / 60000,
                                                   minSpeed = optionGet('MinSpeedPercentMobility',
                                                                        5, ['int', 'float']),
                                                   skip = optionGet('SkipPercentMobility', 12,
                                                                    'int'),
                                                   smooth = optionGet('SmoothPercentMobility', 2,
                                                                      'int'))
            mobility = []
            t0 = self.minTime
            for times in immobility:
                t1 = times[0]
                mobility.append((t0, t1))
                t0 = times[1]
            return self.drawPeriods(mobility)
        elif parameter == "thigmotaxis":
            percentSize = optionGet("ThigmotaxisPercentSize", 20, ["int", "float"])
            start = cm.findStart(self.minTime / 60000)
            periods = []
            outside = False
            t0 = self.minTime
            border = cm.radius * (1 - (percentSize / 100))           
            if m.mode == "OF":
                x0, x1 = cm.radius - cm.centerX, cm.centerX + cm.radius
                y0, y1 = cm.radius - cm.centerY, cm.centerY + cm.radius
                def distance(line):
                    return cm.radius - min([line[2] - x0, x1 - line[2], line[3] - y0, y1 - line[3]])
            else:
                def distance(line):
                    x, y = line[cm.indices]
                    return ((x - cm.centerX)**2 + (y - cm.centerY)**2)**0.5
            for content in cm.data[start:]:
                if content[1] <= self.maxTime: 
                    if distance(content) >= border:
                        if not outside:
                            t0 = content[1]
                        outside = True
                    elif outside:
                        outside = False
                        periods.append((t0, content[1]))
                else:
                    break
            if outside:
                periods.append((t0, self.maxTime))
            return self.drawPeriods(periods)
        elif parameter == "shocks":
            shocks = []
            prev = 0
            for content in cm.data:
                if content[5] != 2 and prev != 2:
                    continue
                elif content[5] != 2 and prev == 2:
                    if content[5] != 5:
                        prev = content[5]
                elif content[5] == 2 and prev == 2:
                    continue
                elif content[5] == 2 and prev != 2:
                    shocks.append(content[1])
                    prev = 2
            return self.drawTimes(shocks)
        elif parameter == "entrances":
            entrances = []
            prev = 0
            for content in cm.data:
                if content[5] != 2 and prev != 2:
                    continue
                elif content[5] != 2 and prev == 2:
                    if content[5] == 0: 
                        prev = 0
                elif content[5] == 2 and prev == 2:
                    continue
                elif content[5] == 2 and prev != 2:
                    entrances.append(content[1])
                    prev = 2
            return self.drawTimes(entrances)
        elif parameter == "passes":
            passes = []
            prev = 0
            for content in cm.data:
                if content[5] == 0 and prev != 2:
                    continue
                elif content[5] == 0 and prev == 2:
                    if content[5] == 0: 
                        prev = 0
                elif content[5] > 0 and content[5] != 5 and prev == 2:
                    continue
                elif content[5] > 0 and content[5] != 5 and prev != 2:
                    passes.append(content[1])
                    prev = 2
            return self.drawTimes(passes)
        elif parameter == "bad points":
            if cm.interpolated:
                sortd = sorted(cm.interpolated)
                wrongs = []              
                prev = sortd[0]
                start = sortd[0]                
                for wrong in sortd[1:]:
                    if wrong != prev + 1:
                        wrongs.append((start, prev))
                        start = wrong
                    prev = wrong
                wrongs.append((start, prev))
                bps = [(cm.data[wrong[0] - 1][1], cm.data[wrong[1] - 1][1]) for wrong in wrongs]
                return self.drawPeriods(bps)
        elif parameter == "strategies":
            rows = optionGet('rowsStrategies', 25, 'int')
            minSpeed = optionGet('minSpeedStrategies', 10, ['int', 'float'])
            minAngle = optionGet('minAngleStrategies', 15, ['int', 'float'])
            borderPercentSize = optionGet('borderPercentSizeStrategies', 20, ['int', 'float'])
            strategies = cm.getStrategies(time = self.maxTime / 60000,
                                          startTime = self.minTime / 60000,
                                          rows = rows, minSpeed = minSpeed, minAngle = minAngle,
                                          borderPercentSize = borderPercentSize, summary = False)
            colors = {"counterclockwise": "green",
                      "clockwise": "dodger blue",
                      "no_reaction": "deep pink",
                      "immobile": "white",
                      "reaction_counterclockwise": "red",
                      "reaction_clockwise": "goldenrod1",
                      "center": "wheat4"}
            if purpose == "graph":
                for strategy, periods in strategies.items():
                    self.drawPeriods(periods, color = colors[strategy], width = 240)
                self.lower("parameter")
            else:
                for strategy, periods in strategies.items():
                    if strategy == "immobile":
                        continue
                    self.drawPeriods(periods, color = colors[strategy].replace(" ", "").rstrip("14"),
                                     width = 240, toReturn = False)
                return self.returnPeriods()
                

    def drawPeriods(self, periods, color = "red", width = 3):
        "draws selected parameter on top of the graph" 
        if not periods:
            return
        timeSpread = (self.maxTime - self.minTime)
        for period in periods:
            if period[0] > self.minTime and period[1] < self.maxTime:
                begin = period[0]
                end = period[1]
            elif self.minTime < period[1] < self.maxTime:
                begin = self.minTime
                end = period[1]
            elif self.minTime < period[0] < self.maxTime:
                begin = period[0]
                end = self.maxTime
            else:
                continue
            self.create_line(((begin - self.minTime) * self.width / timeSpread,
                              0.03 * self.height,
                              (end - self.minTime) * self.width / timeSpread,
                              0.03 * self.height),
                             fill = color, width = width, tags = "parameter")


    def drawTimes(self, times):
        "draws selected parameter on top of the graph"
        if not times:
            return
        timeSpread = (self.maxTime - self.minTime)
        for time in times:
            if self.minTime < time < self.maxTime:
                x = (time - self.minTime) * self.width / timeSpread
                self.create_line((x, 0.01 * self.height, x, 0.07 * self.height),
                                 fill = "red", width = 1, tags = "parameter")
       
           
    def drawGraph(self, maxY, valueList):
        """draws lines on a canvas based on maxY and valueList parameters
        maxY parameter sets maximum value at y-axis
        valueList parameter must be a list containing successive values depicted in the graph
        """
        maxX = len(valueList)
        for i in range(maxX - 1):
            x0 = (i / (maxX - 1)) * self.width
            x1 = ((i + 1) / (maxX - 1)) * self.width
            y0 = (1 - (valueList[i] / maxY)) * self.height
            y1 = (1 - (valueList[i + 1] / maxY)) * self.height
            self.create_line((x0, y0, x1, y1))
        self.lift("timeMeasure")
 


class SvgGraph():
    "represents graph to be saved in .svg file"
    def __init__(self, parent, cm, width = 600, height = 120): 
        self.height = height
        self.width = width
        self.drawnParameter = None    
        self.parent = parent
        self.periodText = ""
        self.__class__.__bases__ = (self.__class__.__bases__[1], self.__class__.__bases__[0])        

    def __del__(self):
        self.__class__.__bases__ = (self.__class__.__bases__[1], self.__class__.__bases__[0])
            
    
    def saveGraph(self, cm):
        "returns information about graph for saving in .svg file"
        self.maxTime = eval(self.parent.timeFrame.timeVar.get()) * 60000
        self.minTime = eval(self.parent.timeFrame.startTimeVar.get()) * 60000
        self.compute(cm)
        self.writeFurtherText()
        return self.points, self.maxY, self.furtherText


    def drawPeriods(self, periods, color = "red", width = 8, toReturn = True):
        "draws selected parameter on top of the graph" 
        if not periods:
            return ""
        timeSpread = (self.maxTime - self.minTime)
        text = ""
        line = '<line x1="{0}" y1="{1}" x2="{2}" y2="{1}" stroke="{3}" stroke-width="{4}"/>\n'
        for period in periods:
            if period[0] > self.minTime and period[1] < self.maxTime:
                begin = period[0]
                end = period[1]
            elif self.minTime < period[1] < self.maxTime:
                begin = self.minTime
                end = period[1]
            elif self.minTime < period[0] < self.maxTime:
                begin = period[0]
                end = self.maxTime
            else:
                continue
            text += line.format((begin - self.minTime) * self.width / timeSpread,
                                (width/480) * self.height,
                                (end - self.minTime) * self.width / timeSpread,
                                color, width/2)
        self.periodText += text
        if toReturn:
            return self.periodText


    def returnPeriods(self):
        return self.periodText        


    def drawTimes(self, times):
        "draws selected parameter on top of the graph"
        if not times:
            return ""
        timeSpread = (self.maxTime - self.minTime)
        text = ""
        for time in times:
            if self.minTime < time < self.maxTime:
                x = (time - self.minTime) * self.width / timeSpread
                text += '<line x1="{0}" y1="0" x2="{0}" y2="5" stroke="red"/>\n'.format(x)
        return text


        
class SpeedGraph(Graphs, SvgGraph):
    "graph depicting speed during the session"
    def __init__(self, parent, cm = None, purpose = "graph", width = 600):
        self.primaryParent = Graphs if purpose == "graph" else SvgGraph
        self.primaryParent.__init__(self, parent, cm = cm, width = width)
        

    def writeFurtherText(self):
        "makes text for svg file representing horizontal lines for every 10cm/s"
        self.furtherText = ""
        for y in range(1, floor(self.maxY / 10)):
            text = '<line stroke="lightgray" stroke-width="0.5" ' +\
                   'x1="0" y1="{0}" x2="{1}" y2="{0}"/>\n'.format(y * 10 * 120 / self.maxY,
                                                                  self.width)
            self.furtherText += text       


    def compute(self, cm, skip = 12, smooth = 2):
        """computes speeds
           parameter skip controls how many lines should be skipped when computing speed
           parameter smooth controls how many speed data points should be averaged
           e.g. when skip = 12 and smooth = 2, speed is computed as an average of two speeds
               computed from lines separated by 11 lines
        """
        indices = cm.indices
        resolution = cm.trackerResolution

        # saving speed between every 'skip' data point ... in centimeters per second
        start = cm.findStart(self.minTime / 60000)
        self.speed = []
        x0, y0 = cm.data[start][indices]
        t0 = cm.data[start][1]
        for line in cm.data[(start + skip)::skip]:
            x1, y1 = line[indices]
            t1 = line[1]
            speed = ((((x1 - x0)**2 + (y1 - y0)**2)**0.5) / resolution) / ((t1 - t0) / 1000)
            self.speed.append(speed)
            if t1 >= self.maxTime:
                break
            x0, y0, t0 = x1, y1, t1

        # averaging speed across 'smooth' speed data points
        self.points = []
        avgSpeed = 0
        for smoothCounter, point in enumerate(self.speed, 1):
            avgSpeed += point
            if smoothCounter % smooth == 0:
                self.points.append((avgSpeed / smooth))
                avgSpeed = 0
        else:
            if avgSpeed != 0:
                self.points.append((avgSpeed / (smoothCounter % smooth)))

        # computing maximum speed depicted on y-axis
        self.maxY = ceil(max(self.points) / 10) * 10


    def CM_loaded(self, cm, initTime = 0, minTime = 0, maxTime = "max"):
        """creates graph when CM file is loaded
           parameter initTime is the time of the player when the graph is initialized
        """
        super().CM_loaded(cm, minTime, maxTime, initTime)
        self.compute(cm)

        for y in range(1, floor(self.maxY / 10)):
            self.create_line((0, y*10 * self.height / self.maxY, self.width,
                              y*10 * self.height / self.maxY),  fill = "gray86")
        
        self.drawGraph(maxY = self.maxY, valueList = self.points)


    def addYticks(self):
        at = []
        labels = []
        for i in range((self.maxY // 20) + 1):
            at.append(i*20 / self.maxY)
            labels.append(str(i*20))
        return at, labels


    def getYlabel(self):
        return "Speed [m/s]"


class DistanceFromCenterGraph(Graphs, SvgGraph):
    "graph depicting distance from center of arena during the session"
    def __init__(self, parent, cm = None, purpose = "graph", width = 600):
        self.primaryParent = Graphs if purpose == "graph" else SvgGraph
        self.primaryParent.__init__(self, parent, cm = cm, width = width)


    def writeFurtherText(self):
        "makes text for svg file containing info about line representing border of the arena"
        y = ((self.maxY - self.radius) / self.maxY) * 120
        self.furtherText = '<line stroke="gray" stroke-width="0.5" x1="0" ' +\
                           'y1="{0}" x2="{1}" y2="{0}"/>\n'.format(y, self.width)


    def compute(self, cm, smooth = 10):
        """computes distances from center of the graph
           parameter smooth controls how many data points should be averaged
        """
        start = cm.findStart(self.minTime / 60000)

        self.radius = cm.radius
        self.resolution = cm.trackerResolution
        Cx, Cy = cm.centerX, cm.centerY

        if m.mode == "RA":
            dists = [((line[7] - Cx)**2 + (line[8] - Cy)**2)**0.5 for line in cm.data[start:] if
                     line[1] <= self.maxTime]
        elif m.mode == "OF":
            r = self.radius
            lb, tb, rb, bb = Cx - r, Cy + r, Cx + r, Cy - r 
            dists = [r - min([line[2]-lb, rb-line[2], line[3]-bb, tb-line[3]]) for line in
                     cm.data[start:] if line[1] <= self.maxTime]    
        else:
            dists = [((line[2] - Cx)**2 + (line[3] - Cy)**2)**0.5 for line in cm.data[start:] if
                     line[1] <= self.maxTime]

        self.maxY = self.radius + 10
        self.points = dists
        

    def CM_loaded(self, cm, initTime = 0, minTime = 0, maxTime = "max"):
        """creates graph when CM file is loaded
           parameter initTime is the time of the player when the graph is initialized
        """
        super().CM_loaded(cm, minTime, maxTime, initTime)
        self.compute(cm)
        
        self.create_line((0, 10, self.width, 10), fill = "grey")

        self.drawGraph(maxY = self.maxY, valueList = self.points)


    def addYticks(self):
        at = []
        labels = []
        maxYcm = self.maxY / self.resolution
        for i in range((int(maxYcm) // 20) + 1):
            at.append(i*20 / maxYcm)
            labels.append(str(i*20))
        return at, labels


    def getYlabel(self):
        return "Distance [cm]"
    


class DistanceFromPlatformGraph(Graphs, SvgGraph):
    "graph depicting distance from platform during the MWM session"
    def __init__(self, parent, cm = None, purpose = "graph", width = 600):
        self.primaryParent = Graphs if purpose == "graph" else SvgGraph
        self.primaryParent.__init__(self, parent, cm = cm, width = width)


    def writeFurtherText(self):
        "makes text for svg file containing info about line representing border of the platform"
        self.furtherText = '<line stroke="gray" stroke-width="0.5" x1="0" ' +\
                           'y1="{0}" x2="{1}" y2="{0}"/>\n'.format(self.platformRadius, self.width)


    def compute(self, cm, smooth = 10):
        """computes distances from center of the graph
           parameter smooth controls how many data points should be averaged
        """
        start = cm.findStart(self.minTime / 60000)

        Cx, Cy = cm.centerX, cm.centerY
        Px, Py = cm.platformX, cm.platformY
        self.radius = cm.platformRadius
           
        self.points = [((line[2] - Px)**2 + (line[3] - Py)**2)**0.5 for line in cm.data[start:] if
                       line[1] <= self.maxTime]

        self.maxY = cm.radius + ((Px - Cx)**2 + (Py - Cy)**2)**0.5
        

    def CM_loaded(self, cm, initTime = 0, minTime = 0, maxTime = "max"):
        """creates graph when CM file is loaded
           parameter initTime is the time of the player when the graph is initialized
        """
        super().CM_loaded(cm, minTime, maxTime, initTime)
        self.compute(cm)

        y = self.height * (1 - self.radius/self.maxY)
        color = "grey" if m.mode == "MWM" else "red"
        self.create_line((0, y, self.width, y), fill = color)

        self.drawGraph(maxY = self.maxY, valueList = self.points)

    

class DistanceFromRobotGraph(DistanceFromPlatformGraph):
    "graph depicting distance from the robot during the RA session"
    def __init__(self, parent, cm = None, purpose = "graph", width = 600):
        self.primaryParent = Graphs if purpose == "graph" else SvgGraph
        self.primaryParent.__init__(self, parent, cm = cm, width = width)      

        
    def compute(self, cm, smooth = 10):
        start = cm.findStart(self.minTime / 60000)

        self.radius = cm.sectorRadius
           
        self.points = [((line[7] - line[2])**2 + (line[8] - line[3])**2)**0.5
                       for line in cm.data[start:] if line[1] <= self.maxTime]

        self.maxY = cm.radius * 2
    


class AngleGraph(Graphs, SvgGraph):
    "graph depicting angle relative to the center of shock zone during the session"
    def __init__(self, parent, cm = None, purpose = "graph", width = 600):
        self.primaryParent = Graphs if purpose == "graph" else SvgGraph
        self.primaryParent.__init__(self, parent, cm = cm, width = width)
        
        self.maxTime = eval(self.parent.timeFrame.timeVar.get()) * 60000
        self.minTime = eval(self.parent.timeFrame.startTimeVar.get()) * 60000
            

    def compute(self, cm):
        "computes angles of position relative to center"        
        start = cm.findStart(self.minTime / 60000)
        Cx, Cy = cm.centerX, cm.centerY
        CA = cm.centerAngle

        # saving angles to a list        
        self.angles = []
        nxt = False
        prev = 180
        self.crosses = 0
        for line in cm.data[start:]:
            if line[1] > self.maxTime:
                break
            else:
                if m.mode == "RA":
                    angle = (degrees(atan2(line[8] - line[3],
                                           line[2] - line[7] + 0.000001)) + 540) % 360
                else:
                    angle = (degrees(atan2(Cy - line[3], line[2] - Cx + 0.000001)) + 720 - CA) % 360
                if prev > 270 and angle < 90:
                    self.angles.append(360)
                    self.angles.append(0)
                    self.crosses += 1
                elif prev < 90 and angle > 270:
                    self.angles.append(0)
                    self.angles.append(360)
                    self.crosses += 1
                else:
                    self.angles.append(angle)                
                prev = angle        


    def CM_loaded(self, cm, initTime = 0, minTime = 0, maxTime = "max"):
        """creates graph when CM file is loaded
           parameter initTime is the time of the player when the graph is initialized
        """
        super().CM_loaded(cm, minTime, maxTime, initTime)
        
        self.compute(cm)

        # drawing lines representing the sector
        if "CM" in m.mode or "KT" in m.mode:
            wid = cm.width   
            y1 = ((360 - (wid / 2)) / 360) * self.height
            y2 = ((wid / 2) / 360) * self.height
            self.create_line((0, y1, self.width, y1), fill = "red")
            self.create_line((0, y2, self.width, y2), fill = "red")

        # drawing the graph
        maxX = len(self.angles) - self.crosses

        i = 0
        prev = self.angles[0]
        for angle in self.angles[1:]:
            x0 = (i / (maxX - 1)) * self.width
            x1 = ((i + 1) / (maxX - 1)) * self.width
            y0 = (1 - (prev / 360)) * self.height
            y1 = (1 - (angle / 360)) * self.height
            if (prev == 0 and angle == 360) or (prev == 360 and angle == 0):
                prev = angle
                continue
            prev = angle
            self.create_line((x0, y0, x1, y1))
            i += 1
            
        self.lift("timeMeasure")


    def saveGraph(self, cm):
        "returns information about graph for saving to .svg file"
        self.compute(cm)
        wid = cm.width

        size = (self.width, self.height)

        maxX = len(self.angles) - self.crosses
        text = ""
        for i in (360 - (wid / 2), wid / 2):
            text += '<line stroke="red" stroke-width="0.5" ' +\
                    'x1="0" y1="{1}" x2="{0}" y2="{1}"/>\n'.format(size[0], i * size[1] / 360)
        
        points = []
        width = size[0]
        height = size[1]
        i = 0
        prev = self.angles[0]
        x0 = (i / (maxX - 1)) * width        
        y0 = (1 - (prev / 360)) * height
        points.append((x0, y0))
        for angle in self.angles[1:]:
            x0 = (i / (maxX - 1)) * width
            x1 = ((i + 1) / (maxX - 1)) * width
            y0 = (1 - (prev / 360)) * height
            y1 = (1 - (angle / 360)) * height
            if (prev == 0 and angle == 360) or (prev == 360 and angle == 0):
                prev = angle
                text += self._addLine(points)
                points = []
                points.append((x1, y1))
                continue
            prev = angle
            points.append((x1, y1))
            i += 1
        text += self._addLine(points)

        return None, None, text


    def _addLine(self, points):
        "returns line in a svg format joining points given as an argument"
        text = '<polyline points="'
        for pair in points:
            text += ",".join(map(str, pair)) + " "      
        text += '" style = "fill:none;stroke:black"/>\n'
        return text


    def addYticks(self):
        at = [0, 0.5, 1]
        labels = ["0", "180", "360"]
        return at, labels


    def getYlabel(self):
        return "Angle [deg]"
