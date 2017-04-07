"""
This file is a template for writing custom parameters.
template.py itself won't load. All other .py files in the Parameters directory will. However, the
files have to be properly named (one word names without special characters should work).

This file is automatically replaced when CMM is updated.
Therefore, DO NOT STORE IMPORTANT CHANGES DIRECTLY IN THIS FILE!

Python tutorial can be found here: http://docs.python.org/3.2/tutorial/index.html
Python library reference can be found here: http://docs.python.org/3.2/library/index.html

The function must have CM object as the first argument. Two other arguments are provided during
processing. Namely, time and startTime, which represent Stop and Start time respectively. While
they may not be used in the body of the function, they must be included. Usually, other arguments
are not needed since they won't be provided during processing.

CM object has several important parameters:
CM.data - contains data obtained from the arena and room .dat files
CM.centerX - x coordinate of center position
CM.centerY - y coordinate of center position
CM.width - width of the sector
CM.arenaDiameter - diameter of the arena in meters
CM.trackerResolution - reolution of the tracker in pixels / centimeter
... 'CM' should be exchenged by the name of the first argument in the body of the function (e.g.
by 'cm' in the template example).

CM.data are represented as a list of lists. 
    Each row of a data file is represented by a list within the returned list.
    Each row contains following information:
        FrameCount(0) msTimeStamp(1) RoomX(2) RoomY(3) Sectors(4) State(5) CurrentLevel(6)...
            ...ArenaX(7) ArenaY(8) Sectors(9) State(10) CurrentLevel(11)
            - indexes are in parentheses
            - the first two items are relevant to both arena and room frame
            - the following 5 items are related to the room frame and final 5 items are related
                to the arena frame
            - State is coded as: OutsideSector = 0, EntranceLatency = 1, Shock = 2,
                InterShockLatency = 3, OutsideRefractory = 4, BadSpot = 5
            - RoomX/Y, ArenaX/Y are coordinates in respective frames (in pixels)
            - Sectors: 0 - no, 1 - room, 2 - arena, 3 - both
            - Current level is in miliamperes
            - Time stamp is in miliseconds

Additionaly, CM object has CM.findStart method that will be often usable. The method returns index
of the position where computation of the parameter should start given the startTime agrument. The
method takes one argument - starting time in minutes.
"""


name = "Total distance" # name of the parameter that will be shown in Process section of CMM


def parameter(cm, time = 20, startTime = 0): # the function must have name 'parameter'
    "computes total distance travelled by an animal between startTime and time"
    time = time * 60000 # conversion from minutes to miliseconds
    start = cm.findStart(startTime) # the method exmplained above
    skip = 25 # represents number of skipped rows
    minDifference = 2 # minimum difference in pixels between the positions that will be used
    x0, y0 = cm.data[0][7:9] # x and y positions in arena frame
    dist = 0 # contains cumulative distance

    for content in cm.data[(start + skip)::skip]:
        # content is a list containing one row of the data file
        if content[1] <= time: # content[1] represents the Time stamp
            x1, y1 = content[7:9] # content[7:9] represents x and y positions in arena frame
            diff = ((x1 - x0)**2 + (y1 - y0)**2)**0.5
            if diff > minDifference:
                dist += diff # equivalent to dist = dist + diff
            x0, y0 = x1, y1 # it's possible to use multiple assignment in Python
            
    dist = dist / (cm.trackerResolution * 100) # conversion from pixels to metres
    
    return format(dist, "0.2f")


"""
Notes:
Indentation is important in Python.
Return statement must be included at the end of the function.
List indexing starts from 0. Indexing using colon is left inclusive, right exclusive.
    I.e. [7:9] is [7, 8]. Number after second colon is optional and represents stride.
    E.g. [1:11:2] is [1, 3, 5, 7, 9]. [3:] represents whole list from the fourth position.
    [-1] represents last list item.
"""


    
