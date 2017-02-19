'''
    Copyright 2017 by Alex Mitrevski <aleksandar.mitrevski@h-brs.de>

    This file is part of delta-execution-models.

    delta-execution-models is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    delta-execution-models is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with delta-execution-models. If not, see <http://www.gnu.org/licenses/>.
'''

class GeometricMatchDescriptions(object):
    DANGEROUS = -1
    CLOSER = 0
    JUST_AS_FAR = 1
    FARTHER = 2

class GeometricMatchInfo(object):
    def __init__(self, match_index, match_description):
        self.match_index = match_index
        self.match_description = match_description

class SymbolicMatchLibrary(object):
    @staticmethod
    def matches_instance(symb_instance, instance):
        return symb_instance == instance

class GeometricMatchLibrary(object):
    @staticmethod
    def matches_instance(objects, instance, epsilon_dist=5.):
        x_dist = objects[0].init_bounding_box.max.x - objects[1].init_bounding_box.min.x
        y_dist = objects[0].init_bounding_box.max.y - objects[1].init_bounding_box.max.y

        if abs(x_dist) + epsilon_dist < abs(instance[0]) or abs(y_dist) + epsilon_dist < abs(instance[1]):
            return GeometricMatchDescriptions.CLOSER
        elif abs(x_dist - instance[0]) < epsilon_dist and abs(y_dist - instance[1]) < epsilon_dist:
            return GeometricMatchDescriptions.JUST_AS_FAR
        else:
            return GeometricMatchDescriptions.FARTHER
