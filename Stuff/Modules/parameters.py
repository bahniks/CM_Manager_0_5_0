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


from collections import OrderedDict, namedtuple
import os



Par = namedtuple("Par", ["method", "group", "options"])
Opt = namedtuple("Opt", ["name", "default", "types"])


class ParametersCM(OrderedDict):
    "class containing list of parameters, their methods and options"
    def __init__(self):
        super().__init__()
        self["Total distance"] = Par("getDistance", "basic", {
            "skip": (Opt('StrideParTotalDistance', 25, 'int'),
                     "Computed from every [in rows]"),
            "minDifference": (Opt('MinDiffParTotalDistance', 0, ['int', 'float']),
                              "Minimal distance counted [in pixels]")
            })
        self["Maximum time avoided"] = Par("getMaxT", "basic", {})
        self["Entrances"] = Par("getEntrances", "basic", {})
        self["Time to first"] = Par("getT1", "basic", {})
        self["Shocks"] = Par("getShocks", "basic", {})
        self["Time in target sector"] = Par("getTimeInTarget", "basic", {})
        self["Time in opposite sector"] = Par("getTimeInOpposite", "basic", {})
        self["Time in chosen sector"] = Par("getTimeInChosenSector", "advanced", {
            "width": (Opt('WidthParTimeInChosen', 'default', ['int', 'float']),
                      "Width of sector ('default' if same as target) [in degrees]"),
            "center": (Opt('AngleParTimeInChosen', 0, ['int', 'float']),
                       "Center of sector relative to the target [in degrees]")
            })
        self["Time in sectors"] = Par("getAngleBoxes", "advanced", {
            "width": (Opt('WidthParTimeInSectors', 'default', ['int', 'float']),
                      "Width of sector ('default' if same as target) [in degrees]")
            })
        self["Thigmotaxis"] = Par("getThigmotaxis", "advanced", {
            "percentSize": (Opt('ThigmotaxisPercentSize', 20, ['int', 'float']),
                            "Annulus width [in percents]")
            })
        self["Directional mean"] = Par("getDirectionalMean", "advanced", {})
        self["Circular variance"] = Par("getCircularVariance", "advanced", {})                
        self["Maximum time of immobility"] = Par("getMaxTimeOfImmobility", "experimental", {
            "minSpeed": (Opt('MinSpeedMaxTimeImmobility', 10, ['int', 'float']),
                         "Minimum speed counted [in cm/s]"),
            "skip": (Opt('SkipMaxTimeImmobility', 12, ['int']),
                     "Computed from every [in rows]"),
            "smooth": (Opt('SmoothMaxTimeImmobility', 2, ['int']),
                       "Averaged across [in intervals]")
            })                
        self["Periodicity"] = Par("getPeriodicity", "experimental", {
            "minSpeed": (Opt('MinSpeedPeriodicity', 10, ['int', 'float']),
                         "Minimum speed counted [in cm/s]"),
            "skip": (Opt('SkipPeriodicity', 12, ['int']),
                     "Computed from every [in rows]"),
            "smooth": (Opt('SmoothPeriodicity', 2, ['int']),
                       "Averaged across [in intervals]"),
            "minTime": (Opt('MinTimePeriodicity', 9, ['int', 'float', 'list']),
                        "Minimum time of interval [in seconds]")
            })   
        self["Proportion of time moving"] = Par("getPercentOfMobility", "experimental", {
            "minSpeed": (Opt('MinSpeedPercentMobility', 5, ['int', 'float']),
                         "Minimum speed counted [in cm/s]"),
            "skip": (Opt('SkipPercentMobility', 12, ['int']),
                     "Computed from every [in rows]"),
            "smooth": (Opt('SmoothPercentMobility', 2, ['int']),
                       "Averaged across [in intervals]")
            })    
        self["Mean distance from center"] = Par("getMeanDistanceFromCenter", "advanced", {}) 
        self["Median speed after shock"] = Par("getSpeedAfterShock", "experimental", {
            "after": (Opt('SkipSpeedAfterShock', 25, ['int']),
                      "Computed from every [in rows]"),
            "absolute": (Opt('AbsoluteSpeedAfterShock', False, 'bool'),
                         "Computed from absolute values")
            })    
        self["Angle of target sector"] = Par("getCenterAngle", "info", {})
        self["Width of target sector"] = Par("getWidth", "info", {})
        self["Real minimum time"] = Par("realMinimumTime", "info", {})
        self["Real maximum time"] = Par("realMaximumTime", "info", {})
        self["Room frame filename"] = Par("getRoomName", "info", {})
        self["Strategies"] = Par("getStrategies", "experimental", {
            "rows": (Opt('rowsStrategies', 25, 'int'),
                     "Length of time bins [in rows]"),
            "minSpeed": (Opt('minSpeedStrategies', 10, ['int', 'float']),
                         "Minimum speed counted [in cm/s]"),
            "minAngle": (Opt('minAngleStrategies', 7, ['int', 'float']),
                         "Minimum angle counted (after shock) [in °/s]"),
            "borderPercentSize": (Opt('borderPercentSizeStrategies', 50, ['int', 'float']),
                                  "Annulus width [in percents]")
            })
        self["Percent bad points"] = Par("countBadPoints", "info", {})
        self["Reflections"] = Par("countReflections", "info", {})
        self["Outside points"] = Par("countOutsidePoints", "info", {
            "distance": (Opt('OutsidePointsDistance', 1, 'int'),
                     "Distance from margin counted [in pixels]"),
            })
        self["Rotation speed"] = Par("getRotationSpeed", "info", {})

        self.noBatch = ["Real minimum time", "Real maximum time", "Room frame filename",
                        "Angle of target sector", "Width of target sector"]


        #self.findParameters()
        
    '''
    def findParameters(self):
        "finds custom written parameters"
        for file in os.listdir(os.path.join(os.getcwd(), "Stuff", "Parameters")):
            splitted = os.path.splitext(file)
            omit = ["__init__", "template"]
            if len(splitted) > 1 and splitted[1] == ".py" and splitted[0] not in omit:
                exec("from Stuff.Parameters import {}".format(splitted[0]))
                option = "DefParCustom{}".format(
                    eval("{}.name".format(splitted[0])).strip().replace(" ", ""))
                newParameter = [eval("{}.name".format(splitted[0])),
                                "{}.parameter(cm, time = time, startTime = startTime)".format(
                                    splitted[0]), "custom", optionGet(option, False, "bool"),
                                option, splitted[0]]
                self.parameters.append(newParameter)
    ''' # TODO


class ParametersMWM(OrderedDict):
    def __init__(self):
        super().__init__()
        mwm = {"Total distance",
               "Time to first",
               "Time in target sector",
               "Time in opposite sector",
               "Time in chosen sector",
               "Time in sectors",
               "Thigmotaxis",
               "Directional mean",
               "Circular variance",
               "Maximum time of immobility",
               "Proportion of time moving",
               "Mean distance from center",
               "Real minimum time",
               "Real maximum time",
               "Bad points",
               "Reflections",
               "Outside points"}
        for name, parameter in ParametersCM().items():
            if name in mwm:
                self[name] = parameter
                
        widths = {"Time in target sector": 'WidthParTimeInTarget',
                  "Time in opposite sector": 'WidthParTimeInOpposite',
                  "Time in chosen sector": 'WidthParTimeInChosen',
                  "Time in sectors": 'WidthParTimeInSectors'}
        for method, option in widths.items():
            newOpt = (Opt(option, 90, ['int', 'float']), "Width of sector [in degrees]")
            newOptions = self[method].options["width"] = newOpt
            self[method]._replace(options = newOptions)

        self["Time to first pass"] = Par("getT1Pass", "basic", {})
        self["Passes"] = Par("getPasses", "basic", {})
        self["Average distance from target"] = Par("getAvgDistance", "advanced", {
            "removeBeginning": (Opt('RemoveBeginningAvgDistance', False, 'bool'),
                                "Remove minimal time needed to reach target"),
            "skip": (Opt('StrideParAvgDistance', 1, 'int'),
                     "Computed from every [in rows]"),
            "minDifference": (Opt('MinDiffParAvgDistance', 0, ['int', 'float']),
                              "Minimal distance counted [in pixels]")
            })
        self["Time to first stay"] = Par("getT1Stay", "experimental", {
            "platformAdjustment": (Opt('platformAdjustmentT1Stay', 2, ['int', 'float']),
                                   "Platform adjustment")
            })
        self["Average distance from chosen"] = Par("getAvgDistanceChosen", "advanced", {
            "angle": (Opt('angleParAvgDistanceCustom', 180, ['int', 'float', 'list']),
                      "Angle of chosen location relative to the target [in degrees]"),
            "removeBeginning": (Opt('RemoveBeginningAvgDistanceCustom', False, 'bool'),
                                "Remove minimal time needed to reach target"),
            "skip": (Opt('StrideParAvgDistanceCustom', 1, 'int'),
                     "Computed from every [in rows]"),
            "minDifference": (Opt('MinDiffParAvgDistanceCustom', 0, ['int', 'float']),
                              "Minimal distance counted [in pixels]")
            })
        self["Angle of the platform"] = ParametersCM()["Angle of target sector"]

        self.noBatch = ParametersCM().noBatch + ["Angle of the platform"]
        
        

class ParametersOF(OrderedDict):
    def __init__(self):
        super().__init__()
        of = {"Total distance",
              "Thigmotaxis",
              "Directional mean",
              "Circular variance",
              "Maximum time of immobility",
              "Proportion of time moving",
              "Mean distance from center",
              "Real minimum time",
              "Real maximum time",
              "Bad points",
              "Reflections",
              "Outside points"}
        for name, parameter in ParametersCM().items():
            if name in of:
                self[name] = parameter
                
        self["Time in quadrants"] = Par("getTimeInQuadrants", "advanced", {
            "corner": (Opt('CornerQuadrants', True, 'bool'),
                       "Corner quadrants (otherwise edge)")
            })
        self["Mean distance from side"] = Par("getMeanDistanceFromSide", "basic", {})

        self.noBatch = ParametersCM().noBatch
        


class ParametersCMSF(OrderedDict):
    def __init__(self):
        super().__init__()
        for name, parameter in ParametersCM().items():
            if name not in ("Room frame filename", "Rotation speed"):
                self[name] = parameter

        self.noBatch = ParametersCM().noBatch
        


class ParametersRA(OrderedDict):
    def __init__(self):
        super().__init__()
        ra = {"Total distance",
              "Maximum time avoided",
              "Time to first",
              "Entrances",
              "Shocks",
              "Thigmotaxis",
              "Directional mean",
              "Circular variance",
              "Mean distance from center",
              "Maximum time of immobility",
              "Proportion of time moving",
              "Real minimum time",
              "Real maximum time",
              "Bad points",
              "Reflections",
              "Outside points"}
        for name, parameter in ParametersCM().items():
            if name in ra:
                self[name] = parameter
        
        self["Time in sectors"] = Par("getAngleBoxes", "advanced", {
            "width": (Opt('WidthParTimeInSectors', 90, ['int', 'float']),
                      "Width of sector [in degrees]"),
            "center": (Opt('CenterParTimeInSectors', 0, ['int', 'float']),
                       "Center of sector [in degrees]")
            })

        self["Median speed after shock"] = Par("getSpeedAfterShock", "experimental", {
            "after": (Opt('SkipSpeedAfterShock', 25, ['int']),
                      "Computed from every [in rows]")
            })    

        self["Robot filename"] = Par("getRoomName", "info", {})

        self["Mean distance from robot"] = Par("getDistanceFromRobot", "basic", {})

        self["Time in distances"] = Par("getDistanceBoxes", "advanced", {
            "width": (Opt('WidthParTimeInDistances', 10, ['int', 'float']),
                      "Width of brackets [in cm]")
            })

        self.noBatch = ParametersCM().noBatch + ["Robot filename"]







