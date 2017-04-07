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


def optionWrite(option, newValue, general = False):
    """writes newValue as an option into file Option.txt located in directory 'Stuff' in working
    directory"""
    if not os.path.exists(os.path.join(os.getcwd(), "Stuff")):
        raise Exception("Working directory doesn't contain Stuff directory")

    optionFile = os.path.join(os.getcwd(), "Stuff", "Options.txt")

    if not os.path.exists(optionFile):
        open(optionFile, mode = "w").close()

    if not general:
        option = m.mode + option
    optString = "%|" + option + "|%"
    outfile = open(optionFile, mode = "r")
    tempfile = open(os.path.join(os.getcwd(), "Stuff", "~Options.txt"), mode = "w")

    optionExists = False
    for line in outfile:
        if optString in line:
            tempfile.write(optString + " " + str(newValue) + "\n")
            optionExists = True
        else:
            tempfile.write(line)
    if not optionExists:
        tempfile.write(optString + " " + str(newValue) + "\n")

    outfile.close()
    tempfile.close()
    os.remove(optionFile)
    os.rename(os.path.join(os.getcwd(), "Stuff", "~Options.txt"), optionFile)
