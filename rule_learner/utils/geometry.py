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

import numpy as np

class Vector(object):
    '''3D vector.

    Author -- Alex Mitrevski

    '''
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

class Rotator(object):
    '''3D rotation expressed in Euler angles.

    Author -- Alex Mitrevski

    '''
    def __init__(self, roll, pitch, yaw):
        self.roll = roll
        self.pitch = pitch
        self.yaw = yaw

class Box(object):
    '''Bounding box of a 3D object.

    Author -- Alex Mitrevski

    '''
    def __init__(self, min_x, min_y, min_z, max_x, max_y, max_z):
        self.min = Vector(min_x, min_y, min_z)
        self.max = Vector(max_x, max_y, max_z)
