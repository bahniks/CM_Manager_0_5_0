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

import os

import mode as m


def optionGet(option, default, valueType, general = False):
    """returns option if it exists and has right type (as specified by valueType parameter),
    otherwise returns default value
    valueType can be specified either as a name of a type (e.g. "str") or as a list of types
    """
    try:
        if not general:
            option = m.mode + option
        optString = "%|" + option + "|%"
        infile = open(os.path.join(os.getcwd(), "Stuff", "Options.txt"), mode = "r")

        for line in infile:
            if optString in line:
                result = line[len(optString):].strip(" \t\n")
                if type(valueType) == list:
                    if ["float", "int"] == sorted(valueType):                       
                        try:
                            if "." in str(result):
                                return float(result)
                            else:
                                return int(result)
                        except Exception:
                            pass
                    else:            
                        for typ in valueType:
                            try:
                                return eval("%s(%s)" % (typ, result))
                            except Exception:
                                pass
                else:
                    try:
                        return eval("%s(%s)" % (valueType, result))
                    except Exception:                     
                        pass
        else:
            return default
    except Exception:
        return default
