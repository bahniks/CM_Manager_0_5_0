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

# probably delete
from math import degrees, atan2, sin, cos, pi, radians, sqrt, ceil
from collections import deque, OrderedDict, defaultdict
import os
from funcs import median


from collections import OrderedDict


from cmsf import CMSF




class KT(CMSF):
    """
    each row of self.data contains following information:
    FrameCount(0) msTimeStamp(1) RoomX(2) RoomY(3) Sectors(4) State(5) CurrentLevel(6)...
        ...ArenaX(7) ArenaY(8) Sectors(9) State(10) CurrentLevel(11)
        - indexes are in parentheses
        - first two items are relevant to both arena and room frame
            following 5 items are related to room frame and final 5 items are related
            to arena frame
        - state info: OutsideSector = 0, EntranceLatency = 1, Shock = 2,
                      InterShockLatency = 3, OutsideRefractory = 4, BadSpot = 5
        - RoomX/Y, ArenaX/Y are coordinates in respective frames (in pixels)
        - sectors: 0 - no, 1 - room, 2 - arena, 3 - both
        - current level is in miliamperes
        - time stamp is in miliseconds
    """
    cache = OrderedDict()

    def __init__(self, nameA, *_):

        self.nameA = nameA
        self.data = []
        self.interpolated = set()
        self.indices = slice(2,4)
        self.processArena = False

        # in cache?
        if self.nameA in KT.cache:
            self.__dict__ = KT.cache[self.nameA]
            return

        # processing data from arena frame
        with open(self.nameA, "r") as infile:
            self.width = 60
            self.centerAngle = 0
            self._processHeader(infile)
            self._processRoomFile(infile)

        if self.processArena:
            with open(self.nameA, "r") as infile:
                self._processArenaFile(infile)

        # discards missing points from beginning of self.data
        self._correctMissingFromBeginning()
          
        # exception used for example when all lines are wrong (all positions are 0, 0)
        if not self.data:
            raise Exception("Failure in data initialization.")

        # caching
        KT.cache[self.nameA] = self.__dict__
        if len(KT.cache) > 15:
            KT.cache.popitem(last = False)

     

    def _cacheRemoval(self):
        if self.nameA in KT.cache:
            KT.cache.pop(self.nameA) 


  
    def _processHeader(self, file):
        for line in file:
            if "TrackerVersion" in line:
                if "iTrack" in line:
                    self.tracker = "iTrack"
                elif "Kachna" in line:
                    self.tracker = "Kachna"
                elif "Tracker" in line:
                    self.tracker = "Tracker"
                else:
                    self.tracker = "Unknown"
            elif "ArenaCenterXY" in line:
                strg = line.split()
                for i in range(len(strg)):
                    if strg[i] == "(":
                        pos = i
                self.centerX = eval(strg[pos+1])      
                self.centerY = eval(strg[pos+2])
            elif "TrackerResolution_PixPerCM" in line:
                strg = line.split()
                for i in range(len(strg)):
                    if strg[i] == "(":
                        pos = i
                self.trackerResolution = eval(strg[pos+1])  
            elif "%ArenaZone" in line and "//" not in line:
                strg = line.split()
                for i in range(len(strg)):
                    if strg[i] == "(":
                        pos = i
                self._addReinforcedSector(strg, pos)
            elif "ArenaDiameter" in line:
                strg = line.split()
                for i in range(len(strg)):
                    if strg[i] == "(":
                        pos = i
                self.arenaDiameter = eval(strg[pos+1])
            elif "Row" in line and "RatArenaX" in line:
                self.processArena = True
                self.indicesA = slice(12, 14) #
                self.indices = slice(7,9) #
            elif "END_HEADER" in line:
                break
            
        self.radius = self.trackerResolution * self.arenaDiameter * 100 / 2
        self.minX = self.centerX - self.radius
        self.minY = self.centerY - self.radius
        self.innerRadius = 0
        self.outerRadius = self.radius
        self.centerX = int(self.centerX - self.minX)
        self.centerY = int(self.centerY - self.minY)
        self.radius = int(self.radius)
        self.shockIndex = 4
             

    def _addReinforcedSector(self, string, position):
        self.centerAngle = eval(string[position+3]) + 90
        self.width = eval(string[position+4])         


    def _processRoomFile(self, infile, endsplit = 7):
        self.inArena = False
        super()._processRoomFile(infile, endsplit)


    def _processArenaFile(self, infile):
        self.inArena = True
        super()._processArenaFile(infile)


    def _evaluateLine(self, line, endsplit):
        line = list(map(float, line.replace("-1", "0").split()))
        if self.inArena:
            line[2:4] = line[self.indicesA]
        line = line[:endsplit]
        if line[2] != 0:
            line[2] = line[2] - self.minX
            line[3] = line[3] - self.minY
        line = list(map(int, line))
        return line
        

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
        if self.nameA in KT.cache:
            KT.cache.pop(self.nameA)      
    def removeReflections(self, *args, bothframes = False, **kwargs):
        super().removeReflections(*args, bothframes = bothframes, **kwargs)


    



            
        

            


def main():
    filename = os.path.join(r"C:\Users\Štěpán\Desktop\CM Manager\CM_Manager_0_5_0\New data", "d37rat14_ARENA.dat")
    kt = KT(filename)
    for i in range(10):
        print(kt.data[i])
    print(max([x[3] for x in kt.data]))

        
    

                                       
if __name__ == "__main__": main()                       



