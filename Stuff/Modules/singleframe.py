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

class SF:
    "class representing methods shared by tasks which data are from a single frame"
    def _correctMissingFromBeginning(self):
        beginMiss = 0
        
        for line in self.data:
            if (line[2] == 0 and line[3] == 0):
                beginMiss += 1
            else:
                if beginMiss != 0:
                    self.data = self.data[beginMiss:]
                    for i in range(len(self.data)):
                        self.data[i][0] -= beginMiss
                    self.interpolated = {p - beginMiss for p in self.interpolated}
                break


    def _computeSpeed(self, row1, row2):
        speed = ((row1[2] - row2[2])**2 + (row1[3] - row2[3])**2)**0.5 / \
                ((abs(row2[1] - row1[1]) / 1000) * self.trackerResolution)
        return speed # cm/s

    def _returnSame(self, missing):
        toDeleteRoom = self._findSame(slice(2,4), missing)
        addMissing = {row[0] - 1 for row in self.data if tuple(row[2:4]) in toDeleteRoom}
        return addMissing


