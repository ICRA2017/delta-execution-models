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

from geometry import Vector, Rotator, Box
from copy import deepcopy

class ObjectData(object):
    '''Represents a model of a 3D object before and after an action execution.

    Author -- Alex Mitrevski

    '''
    def __init__(self, init_x, init_y, init_z, init_roll, init_pitch, init_yaw,\
    init_min_x, init_min_y, init_min_z, init_max_x, init_max_y, init_max_z,\
    x=0., y=0., z=0., roll=0., pitch=0., yaw=0.,\
    min_x=0., min_y=0., min_z=0., max_x=0., max_y=0., max_z=0.):
        '''The variables whose names start with the prefix 'init_' represent
        the pose and the bounding box of an object before an action execution;
        all the others represent the object's pose and bounding box after an execution.

        '''
        self.init_position = Vector(init_x, init_y, init_z)
        self.init_rotation = Rotator(init_roll, init_pitch, init_yaw)
        self.init_bounding_box = Box(init_min_x, init_min_y, init_min_z, init_max_x, init_max_y, init_max_z)
        self.position = Vector(x, y, z)
        self.rotation = Rotator(roll, pitch, yaw)
        self.bounding_box = Box(min_x, min_y, min_z, max_x, max_y, max_z)

    def __deepcopy__(self, memo):
        return ObjectData(self.init_position.x, self.init_position.y, self.init_position.z,\
        self.init_rotation.roll, self.init_rotation.pitch, self.init_rotation.yaw,\
        self.init_bounding_box.min.x, self.init_bounding_box.min.y, self.init_bounding_box.min.z,\
        self.init_bounding_box.max.x, self.init_bounding_box.max.y, self.init_bounding_box.max.z,\
        self.position.x, self.position.y, self.position.z,\
        self.rotation.roll, self.rotation.pitch, self.rotation.yaw,
        self.bounding_box.min.x, self.bounding_box.min.y, self.bounding_box.min.z,\
        self.bounding_box.max.x, self.bounding_box.max.y, self.bounding_box.max.z)
