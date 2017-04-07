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

from collections import OrderedDict


from cm import CM
from singleframe import SF


class CMSF(SF, CM):
    cache = OrderedDict()

    def __init__(self, nameA, *_):

        self.nameA = nameA
        self.data = []
        self.interpolated = set()
        self.indices = slice(2,4)

        # in cache?
        if self.nameA in CMSF.cache:
            self.__dict__ = CMSF.cache[self.nameA]
            return

        # processing data from arena frame
        with open(self.nameA, "r") as infile:
            self.width = 60
            self.centerAngle = 0
            self._processHeader(infile)
            self._processRoomFile(infile)

        # discards missing points from beginning of self.data
        self._correctMissingFromBeginning()
          
        # exception used for example when all lines are wrong (all positions are 0, 0)
        if not self.data:
            raise Exception("Failure in data initialization.")

        # caching
        CMSF.cache[self.nameA] = self.__dict__
        if len(CMSF.cache) > 15:
            CMSF.cache.popitem(last = False)

   
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
        if self.nameA in CMSF.cache:
            CMSF.cache.pop(self.nameA) 

    def removeReflections(self, *args, bothframes = False, **kwargs):
        super().removeReflections(*args, bothframes = bothframes, **kwargs)
