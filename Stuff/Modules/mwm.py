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

from math import degrees, sqrt, cos, sin, radians


from cm import CM
from singleframe import SF


class MWM(SF, CM):
    def __init__(self, nameA, *_):

        self.nameA = nameA
        self.data = []
        self.interpolated = set()
        self.indices = slice(2,4)

        # processing data from arena frame
        with open(self.nameA, "r") as infile:
            self._processHeader(infile)
            self.centerAngle = (degrees(self._angle(self.platformX, self.platformY)) + 360) % 360
            endsplit = 6 if self.tracker == "Tracker" else 7
            self._processRoomFile(infile, endsplit = endsplit)

        # discards missing points from beginning of self.data
        self._correctMissingFromBeginning()
          
        # exception used for example when all lines are wrong (all positions are 0, 0)
        if not self.data:
            raise Exception("Failure in data initialization.")


    def _addReinforcedSector(self, string, position):
        self.platformX = eval(string[position+1])   
        self.platformY = eval(string[position+2])         
        self.platformRadius = eval(string[position+3])



    def getT1(self, time = 1, startTime = 0, lastTime = "fromParameter"):
        """computes time to get to the platform and stay there (in seconds),
        argument 'time' is time of the session
        argument 'lastTime' decides whether the last time point is obtained from 'time' parameter
            or data
        """
        start = self.findStart(startTime)
        time *= 60000 # conversion from minutes to miliseconds
        startTime *= 60000
        T1 = 0
        for content in self.data[start:]:
            if content[5] < 2:
                continue
            elif content[5] in [2, 3]:
                T1 = content[1] - startTime
                break
            
        if T1 == 0 or T1 > time - startTime:
            if lastTime == "fromData": # not used - may be added as an option in the future
                T1 = min(time, self.data[-1][1]) - startTime
            elif lastTime == "fromParameter":
                T1 = time - startTime
                
        T1 = T1 / 1000 # conversion from miliseconds to seconds
        return format(T1, "0.1f")



    def getT1Pass(self, time = 1, startTime = 0, lastTime = "fromParameter"):
        """computes time to first pass through the platform (in seconds),
        argument 'time' is time of the session
        argument 'lastTime' decides whether the last time point is obtained from 'time' parameter
            or data
        """
        time = time * 60000 # conversion from minutes to miliseconds
        start = self.findStart(startTime)
        T1 = 0
        for content in self.data[start:]:
            if content[5] == 0:
                continue
            elif content[5] > 0 and content[5] != 5:
                T1 = content[1] - startTime
                break
            
        if T1 == 0 or T1 > time - startTime:
            if lastTime == "fromData": # not used - may be added as an option in the future
                T1 = min(time, self.data[-1][1]) - startTime
            elif lastTime == "fromParameter":
                T1 = time - startTime
                
        T1 = T1 / 1000 # conversion from miliseconds to seconds
        return format(T1, "0.1f")


    def getT1Stay(self, time = 1, startTime = 0, platformAdjustment = 2, lastTime = "fromParameter"):
        """computes time to first stay in the vicinity of the platform (in seconds),
        argument 'time' is time of the session
        argument 'lastTime' decides whether the last time point is obtained from 'time' parameter
            or data
        """
        time = time * 60000 # conversion from minutes to miliseconds
        start = self.findStart(startTime)
        T1 = 0
        x, y = self.platformX, self.platformY
        passTime = None
        for content in self.data[start:]:
            if content[5] == 0:
                if passTime:
                    distanceToTarget = sqrt((content[2] - x)**2 + (content[3] - y)**2)
                    if distanceToTarget < self.platformRadius * platformAdjustment:
                        if content[1] - passTime >= self.entranceLatency:               
                            T1 = content[1] - startTime                
                            break
                    else:
                        passTime = None
            elif content[5] in [2, 3]:
                T1 = content[1] - startTime
                break
            elif content[5] == 1:
                if not passTime:
                    passTime = content[1]
                elif content[1] - passTime >= self.entranceLatency:               
                    T1 = content[1] - startTime                
                    break
            
        if T1 == 0 or T1 > time - startTime:
            if lastTime == "fromData": # not used - may be added as an option in the future
                T1 = min(time, self.data[-1][1]) - startTime
            elif lastTime == "fromParameter":
                T1 = time - startTime
                
        T1 = T1 / 1000 # conversion from miliseconds to seconds
        return format(T1, "0.1f")


    def getPasses(self, time = 1, startTime = 0):
        """computes number of entrances,
        argument 'time' is time of the session
        """
        time *= 60000
        start = self.findStart(startTime)
        passes = 0
        prev = 0
        for content in self.data[start:]:
            if content[5] == 0 and prev != 2 and content[1] <= time:
                continue
            elif content[5] == 0 and prev == 2 and content[1] <= time:
                if content[5] == 0: 
                    prev = 0
                continue
            elif content[5] > 0 and content[5] != 5 and prev == 2 and content[1] <= time:
                continue
            elif content[5] > 0 and content[5] != 5 and prev != 2 and content[1] <= time:
                passes += 1
                prev = 2
                continue
            elif content[1] > time:
                break
        return passes


    def getAvgDistance(self, time = 1, startTime = 0, x = "platform", y = "platform",
                       removeBeginning = False, skip = 1, minDifference = 0):

        time *= 60000 # conversion from minutes to miliseconds
        start = self.findStart(startTime)

        x = self.platformX if x == "platform" else x
        y = self.platformY if y == "platform" else y

        if removeBeginning:
            # pravdepodobne muze pouzivat time to first pass
            T1 = 0
            for content in self.data[start:]:
                if not 0 < content[5] < 3:
                    continue
                else:
                    T1 = content[1] - startTime
                    break
            if T1 == 0 or T1 > time - startTime:
                T1 = min(time, self.data[-1][1]) - startTime
            beginning = self.realMinimumTime() / 60000 # min
            t = min([time, T1]) # ms
            distance = self.getDistance(skip = skip, time = t / 60000, startTime = beginning,
                                        minDifference = minDifference) # m
            speed = float(distance) * self.trackerResolution * 100 / (t - beginning*60000) # pix/ms
            distanceToTarget = sqrt((self.data[0][2] - x)**2 + (self.data[0][3] - y)**2)
            distanceToTarget -=  self.platformRadius # pix
            timeToReachTarget = distanceToTarget / (speed * 60000) # min
            start = self.findStart(max([timeToReachTarget + beginning, startTime]))
            
        sumDistance = 0
        
        for content in self.data[start:]:
            if content[1] > time:
                break
            currentDistance = sqrt((content[2] - x)**2 + (content[3] - y)**2) - self.platformRadius
            if currentDistance > 0:
                sumDistance += currentDistance
                
        if not self.data[start:]:
            return "NA"
        
        averageDistance = sumDistance / (content[0] - start)       
        averageDistance /= self.trackerResolution # conversion to centimetres
        
        return format(averageDistance, "0.2f")


    def getAvgDistanceChosen(self, time = 1, startTime = 0, angle = 180, **kwargs):
        if isinstance(angle, list):
            results = [self.getAvgDistanceChosen(time, startTime, a, **kwargs) for a in angle]
            return "|".join(results)
        angle += self.centerAngle
        angle = radians(angle)        
        dist = sqrt((self.centerX - self.platformX)**2 + (self.centerY - self.platformY)**2)
        x = self.centerX + cos(angle)*dist 
        y = self.centerY - sin(angle)*dist
        return self.getAvgDistance(time = time, startTime = startTime, x = x, y = y, **kwargs)
        

    def getCenterAngle(self, **_):
        return format(self.centerAngle, "0.1f")

   
    def _removalCondition(self, row, i, before, reflection):
        """conditions in order of appearance:
            large speed between the row and before row
            same position as in the reflection row
            we should expect the position to be closer to before row than to the
            reflection row - determined by speed
            wrong points in the row
        """
        return any((self._computeSpeed(self.data[row + i], before) > 50,
                    self.data[row + i][2:4] == self.data[row][2:4],
                    self._computeSpeed(reflection, self.data[row + i]) * 30 <
                    self._computeSpeed(before, self.data[row + i]),
                    row + i in self.interpolated))
    

    def _cacheRemoval(self):
        "overrides CM method, MWM has no cache"
        pass

    def removeReflections(self, *args, bothframes = False, **kwargs):
        super().removeReflections(*args, bothframes = bothframes, **kwargs)
        
