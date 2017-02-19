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

import global_utils
from knowledge_base import KnowledgeBase
from delta_memory.memory import DeltaMemory

def get_left_right_obj_idx(objects):
    left_obj_idx = right_obj_idx = -1
    if objects[1].init_position.x < objects[2].init_position.x:
        left_obj_idx = 1
        right_obj_idx = 2
    else:
        left_obj_idx = 2
        right_obj_idx = 1
    return left_obj_idx, right_obj_idx

def get_below_above_obj_idx(objects):
    below_obj_idx = above_obj_idx = -1
    if objects[1].init_bounding_box.min.y < objects[2].init_bounding_box.min.y:
        below_obj_idx = 1
        above_obj_idx = 2
    else:
        below_obj_idx = 2
        above_obj_idx = 1
    return below_obj_idx, above_obj_idx

kb_db_name = 'knowledge_base'
kb = KnowledgeBase(kb_db_name)

dm_db_name = 'delta_memory'
dm = DeltaMemory(dm_db_name, kb)

keys_file = file('keys.txt', 'r')
object_key = keys_file.readline().rstrip('\n\r')
instance_key = keys_file.readline().rstrip('\n\r')
gsm_resolution = float(keys_file.readline().rstrip('\n\r'))
keys_file.close()

x_gsm_distribution = None
y_gsm_distribution = None
x_gsm_boundaries = None
y_gsm_boundaries = None

data = np.genfromtxt('data/' + object_key + '_' + instance_key + '.log')
objects = global_utils.extract_objects(data[0])
if len(objects) > 2:
    gsm_data = np.genfromtxt('data/' + object_key + '_' + instance_key + '_gsm.log')

    objects = global_utils.extract_objects(data[0])
    left_obj_idx, right_obj_idx = get_left_right_obj_idx(objects)
    delta_obj_x_diff = objects[right_obj_idx].init_bounding_box.min.x - objects[left_obj_idx].init_bounding_box.max.x
    delta_left_x = objects[left_obj_idx].init_bounding_box.max.x

    objects = global_utils.extract_objects(gsm_data[0])
    left_obj_idx, right_obj_idx = get_left_right_obj_idx(objects)
    x_obj_diff = objects[right_obj_idx].init_bounding_box.min.x - objects[left_obj_idx].init_bounding_box.max.x
    left_x = objects[left_obj_idx].init_bounding_box.max.x

    #######################
    # creating model for X
    #######################
    diff = [list(), list()]
    success = [list(), list()]
    for i in xrange(gsm_data.shape[0]):
        objects = global_utils.extract_objects(gsm_data[i])
        x_diff = objects[0].init_position.x - objects[left_obj_idx].init_bounding_box.max.x
        diff[0].append(x_diff)
        success[0].append(gsm_data[i,-1])

    bin_count = int(abs(np.ceil(x_obj_diff / gsm_resolution)))
    hist = np.histogram(diff[0], bins=bin_count, weights=success[0])
    x_gsm_distribution = list(hist[0] / (np.sum(hist[0]) * 1.))
    x_distribution_boundaries = hist[1]

    gamma_x = x_obj_diff / (delta_obj_x_diff + 1e-5)
    x_gsm_boundaries = list()
    for x in x_distribution_boundaries:
        actual_x = left_x + x
        gsm_boundary = (actual_x - left_x + gamma_x * delta_left_x) / gamma_x - delta_left_x
        x_gsm_boundaries.append(gsm_boundary)

    #######################
    # creating model for Y
    #######################
    objects = global_utils.extract_objects(data[0])
    below_obj_idx, above_obj_idx = get_below_above_obj_idx(objects)
    delta_obj_y_diff = objects[above_obj_idx].init_position.y - objects[below_obj_idx].init_position.y
    delta_below_y = objects[below_obj_idx].init_position.y

    objects = global_utils.extract_objects(gsm_data[0])
    below_obj_idx, above_obj_idx = get_below_above_obj_idx(objects)
    y_obj_diff = objects[above_obj_idx].init_position.y - objects[below_obj_idx].init_position.y
    below_y = objects[below_obj_idx].init_position.y

    for i in xrange(gsm_data.shape[0]):
        objects = global_utils.extract_objects(gsm_data[i])
        y_diff = objects[0].init_position.y - objects[below_obj_idx].init_position.y
        diff[1].append(y_diff)
        success[1].append(gsm_data[i,-1])

    bin_count = int(abs(np.ceil(y_obj_diff / gsm_resolution)))
    if bin_count == 0:
        bin_count = 1
    hist = np.histogram(diff[1], bins=bin_count, weights=success[1])
    y_gsm_distribution = list(hist[0] / (np.sum(hist[0]) * 1.))
    y_distribution_boundaries = hist[1]

    gamma_y = y_obj_diff / (delta_obj_y_diff + 1e-5)
    if gamma_y < 1e-5:
        gamma_y = 1e5
    y_gsm_boundaries = list()
    for y in y_distribution_boundaries:
        actual_y = below_y + y
        gsm_boundary = (actual_y - below_y + gamma_y * delta_below_y) / gamma_y - delta_below_y
        y_gsm_boundaries.append(gsm_boundary)
elif len(objects) == 2:
    objects = global_utils.extract_objects(data[0])
    bb_sizes = [objects[1].init_bounding_box.max.x - objects[1].init_bounding_box.min.x, \
    objects[1].init_bounding_box.max.y - objects[1].init_bounding_box.min.y]

    #################
    # creating model
    #################
    diff = [list(), list()]
    success = [list(), list()]
    for i in xrange(data.shape[0]):
        objects = global_utils.extract_objects(data[i])
        x_diff = objects[0].init_position.x - objects[1].init_bounding_box.min.x
        y_diff = objects[0].init_position.y - objects[1].init_bounding_box.min.y

        diff[0].append(x_diff)
        success[0].append(data[i,-1])

        diff[1].append(y_diff)
        success[1].append(data[i,-1])

    bin_count = int(np.ceil(bb_sizes[0] / gsm_resolution))
    hist = np.histogram(diff[0], bins=bin_count, weights=success[0])
    x_gsm_distribution = list(hist[0] / (np.sum(hist[0]) * 1.))
    x_gsm_boundaries = list(hist[1])

    bin_count = int(np.ceil(bb_sizes[1] / gsm_resolution))
    hist = np.histogram(diff[1], bins=bin_count, weights=success[1])
    y_gsm_distribution = list(hist[0] / (np.sum(hist[0]) * 1.))
    y_gsm_boundaries = list(hist[1])

##############
# saving data
##############
gsm_distribution = [x_gsm_distribution, y_gsm_distribution]
gsm_boundaries = [x_gsm_boundaries, y_gsm_boundaries]
dm.add_gsm(object_key, instance_key, gsm_distribution, gsm_boundaries)
