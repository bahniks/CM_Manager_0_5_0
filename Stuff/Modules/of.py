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

from collections import deque, OrderedDict
from math import degrees


from cm import CM
from singleframe import SF


class OF(SF, CM):
    cache = OrderedDict()
    
    def __init__(self, nameA, *_):

        self.nameA = nameA
        self.data = []
        self.interpolated = set()
        self.indices = slice(2,4)
       
        # in cache?
        if self.nameA in OF.cache:
            self.__dict__ = OF.cache[self.nameA]
            return

        # processing data from arena frame
        with open(self.nameA, "r") as infile:
            self._processHeader(infile)
            self.centerAngle = 0
            self._processRoomFile(infile)

        # discards missing points from beginning of self.data
        self._correctMissingFromBeginning()
          
        # exception used for example when all lines are wrong (all positions are 0, 0)
        if not self.data:
            raise Exception("Failure in data initialization.")

        # caching
        OF.cache[self.nameA] = self.__dict__
        if len(OF.cache) > 15:
            OF.cache.popitem(last = False)


    def countOutsidePoints(self, time = 20, startTime = 0, distance = 1):
        time *= 60000
        start = self.findStart(startTime)

        Cx, Cy = self.centerX, self.centerY        
        r = self.radius
        lb, tb, rb, bb = Cx - r, Cy + r, Cx + r, Cy - r
        distance = -distance

        outside = [1 for line in self.data[start:] if line[1] <= time and
                   min([line[2]-lb, rb-line[2], line[3]-bb, tb-line[3]]) < distance]  

        return sum(outside)


    def getThigmotaxis(self, time = 20, startTime = 0, percentSize = 20):
        time *= 60000
        start = self.findStart(startTime)
        if type(percentSize) != list:
            percentSize = [percentSize]

        results = []
        for width in percentSize:
            centerArea = (1 - width/100) * self.radius
            x0, x1 = self.centerX - centerArea, self.centerX + centerArea
            y0, y1 = self.centerY - centerArea, self.centerY + centerArea
            center = 0
            periphery = 0
            for content in self.data[start:]:
                if x0 < content[2] < x1 and y0 < content[3] < y1 and content[1] <= time:
                    center += 1                       
                elif content[1] <= time:
                    periphery += 1                       
                else:
                    break

            results.append(format(periphery / (center + periphery), "0.3f"))
                            
        if len(results) == 1:
            return results[0]
        else:
            return "|".join(results)          


    def getMeanDistanceFromSide(self, time = 20, startTime = 0):
        time *= 60000
        start = self.findStart(startTime)

        Cx, Cy = self.centerX, self.centerY        
        r = self.radius
        lb, tb, rb, bb = Cx - r, Cy + r, Cx + r, Cy - r

        dists = [max((min((line[2]-lb, rb-line[2], line[3]-bb, tb-line[3])), 0)) for line in
                 self.data[start:] if line[1] <= time]

        result = (sum(dists) / len(dists)) / self.trackerResolution
        
        return format(result, "0.2f")


    def getTimeInQuadrants(self, time = 20, startTime = 0, corner = True):
        time *= 60000
        start = self.findStart(startTime)
        sectorCenterAngle = 0 if not corner else 45
  
        angles = [0] * 4
        for content in self.data[start:]:
            if content[1] <= time:
                angle = (degrees(self._angle(content[2], content[3])) -
                         sectorCenterAngle + 405) % 360
                angles[int(angle // 90)] += 1

        boxes = [format((box / sum(angles)), "0.3f") for box in angles]

        return ("|".join(boxes))

  
    def _removalCondition(self, row, i, before, reflection):
        """conditions in order of appearance:
            large speed between the row and before row
            same position as in the reflection row
            we should expect the position to be closer to before row than to the
            reflection row - determined by speed
            wrong points in the row
        """
        return any((self._computeSpeed(self.data[row + i], before) > 250,
                    self.data[row + i][2:4] == self.data[row][2:4],
                    self._computeSpeed(reflection, self.data[row + i]) * 30 <
                    self._computeSpeed(before, self.data[row + i]),
                    row + i in self.interpolated))

    def _cacheRemoval(self):
        if self.nameA in OF.cache:
            OF.cache.pop(self.nameA) 


    def removeReflections(self, *args, bothframes = False, **kwargs):
        super().removeReflections(*args, bothframes = bothframes, **kwargs)


        

        
