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

from utils.geometry import Vector, Rotator, Box
from utils.predicates import PredicateLibrary
from utils.object import ObjectData
from utils.conversion import TypeConverter, Types

import transformations as tf

predicates = [PredicateLibrary.on, PredicateLibrary.leftOf, PredicateLibrary.rightOf, PredicateLibrary.above, \
PredicateLibrary.below, PredicateLibrary.behind, PredicateLibrary.inFrontOf, PredicateLibrary.ntpp, \
PredicateLibrary.ntppi, PredicateLibrary.ec, PredicateLibrary.dc, PredicateLibrary.eq, PredicateLibrary.po]

predicate_names = ['on', 'leftOf', 'rightOf', 'above', 'below', \
'behind', 'inFrontOf', 'ntpp', 'ntppi', 'ec', 'dc', 'eq', 'po']

object_item_count = 24
predicate_acceptance_threshold = 0.9
bit_noise_probability = 0.1


def extract_objects(data):
    object_count = len(data) / object_item_count

    manip_obj = ObjectData(data[0], data[1], data[2], data[3], data[4], data[5], \
    data[12], data[13], data[14], data[15], data[16], data[17], \
    data[6], data[7], data[8], data[9], data[10], data[11], \
    data[18], data[19], data[20], data[21], data[22], data[23])

    objects = [manip_obj]
    if object_count == 2:
        obj2 = ObjectData(data[24], data[25], data[41], data[27], data[28], data[29], \
        data[36], data[37], data[38], data[39], data[40], data[41], \
        data[30], data[31], data[32], data[33], data[34], data[35], \
        data[42], data[43], data[44], data[45], data[46], data[47])

        objects.append(obj2)
    elif object_count == 3:
        obj2 = None
        obj3 = None

        #we compare the maximum x of the first object's bounding box
        #to the minimum x of the second object's bounding box in order to
        #which one of the objects is to the left/right;
        #we then take the left-most point of the right object as its x coordinate
        #and the right-most point of the left object as its x coordinate
        if data[39] < data[60]:
            obj2 = ObjectData(data[39], data[25], data[26], data[27], data[28], data[29], \
            data[36], data[37], data[38], data[39], data[40], data[41], \
            data[30], data[31], data[32], data[33], data[34], data[35], \
            data[42], data[43], data[44], data[45], data[46], data[47])

            obj3 = ObjectData(data[60], data[49], data[50], data[51], data[52], data[53], \
            data[60], data[61], data[62], data[63], data[64], data[65], \
            data[54], data[55], data[56], data[57], data[58], data[59], \
            data[66], data[67], data[68], data[69], data[70], data[71])
        else:
            obj2 = ObjectData(data[60], data[49], data[50], data[51], data[52], data[53], \
            data[60], data[61], data[62], data[63], data[64], data[65], \
            data[54], data[55], data[56], data[57], data[58], data[59], \
            data[66], data[67], data[68], data[69], data[70], data[71])

            obj3 = ObjectData(data[39], data[25], data[26], data[27], data[28], data[29], \
            data[36], data[37], data[38], data[39], data[40], data[41], \
            data[30], data[31], data[32], data[33], data[34], data[35], \
            data[42], data[43], data[44], data[45], data[46], data[47])

        objects.append(obj2)
        objects.append(obj3)

    return objects

def calculate_predicate_values(objects):
    predicate_vector = list()
    object_count = len(objects)

    for i in xrange(object_count):
        for j in xrange(i+1, object_count):
            for p in predicates:
                predicate_vector.append(p(objects[i].init_bounding_box, objects[j].init_bounding_box, return_type=Types.INT))

    return np.array(predicate_vector)

def get_object_entry_list(object_count):
    entries = list()
    for i in xrange(object_count):
        for j in xrange(i+1, object_count):
            for p in predicates:
                entries.append((i, j))
    return entries

def vector_to_string(v):
    symb = ''.join([str(x) for x in v])
    return symb

def calculate_final_predicate_values(objects):
    predicate_vector = list()
    object_count = len(objects)

    for i in xrange(object_count):
        for j in xrange(i+1, object_count):
            for p in predicates:
                predicate_vector.append(p(objects[i].bounding_box, objects[j].bounding_box, return_type=Types.INT))

    return np.array(predicate_vector)

def add_noise(predicate_vector, bit_noise_probability):
    noisy_predicates = np.array(predicate_vector)
    for i in xrange(len(predicate_vector)):
        p = np.random.uniform()
        if p < bit_noise_probability:
            noisy_predicates[i] = 1 - predicate_vector[i]
    return noisy_predicates

def extract_geometric_mapping_data(*args):
    data = list()
    if len(args) == 1:
        obj = args[0]
        b_box_size_x = obj.init_bounding_box.max.x - obj.init_bounding_box.min.x
        b_box_size_y = obj.init_bounding_box.max.y - obj.init_bounding_box.min.y
        b_box_size_z = obj.init_bounding_box.max.z - obj.init_bounding_box.min.z
        pos_x = obj.init_position.x
        pos_y = obj.init_position.y
        pos_z = obj.init_position.z
        q = tf.quaternion_from_euler(np.radians(obj.init_rotation.roll), np.radians(obj.init_rotation.pitch), np.radians(obj.init_rotation.yaw))

        data = [b_box_size_x, b_box_size_y, b_box_size_z, pos_x, pos_y, pos_z, q.w, q.x, q.y, q.z]
    elif len(args) == 2:
        obj1 = args[0]
        obj2 = args[1]

        b_box1_size_x = obj1.init_bounding_box.max.x - obj1.init_bounding_box.min.x
        b_box1_size_y = obj1.init_bounding_box.max.y - obj1.init_bounding_box.min.y
        b_box1_size_z = obj1.init_bounding_box.max.z - obj1.init_bounding_box.min.z
        q1 = tf.quaternion_from_euler(np.radians(obj1.init_rotation.roll), np.radians(obj1.init_rotation.pitch), np.radians(obj1.init_rotation.yaw))#euler_to_quaternion(obj1.init_rotation)

        b_box2_size_x = obj2.init_bounding_box.max.x - obj2.init_bounding_box.min.x
        b_box2_size_y = obj2.init_bounding_box.max.y - obj2.init_bounding_box.min.y
        b_box2_size_z = obj2.init_bounding_box.max.z - obj2.init_bounding_box.min.z
        q2 = tf.quaternion_from_euler(np.radians(obj2.init_rotation.roll), np.radians(obj2.init_rotation.pitch), np.radians(obj2.init_rotation.yaw))#euler_to_quaternion(obj2.init_rotation)

        t_rel = obj1.init_position - obj2.init_position

        data = [b_box1_size_x, b_box1_size_y, b_box1_size_z, b_box2_size_x, b_box2_size_y, b_box2_size_z, \
        t_rel.x, t_rel.y, t_rel.z, \
        q1[0], q1[1], q1[2], q1[3], q2[0], q2[1], q2[2], q2[3]]

    return np.array(data)
