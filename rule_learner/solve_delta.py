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

import os.path
import numpy as np
from sklearn.externals import joblib

import global_utils
import density_optimisation.optimisation_utils as optimisation
from utils.object import ObjectData
from knowledge_base import KnowledgeBase
from delta_memory.memory import DeltaMemory
from delta_memory.matches import GeometricMatchDescriptions

import transformations as tf

path = 'path to rule_learner'

keys_file = file(path + 'keys.txt', 'r')
object_key = keys_file.readline().rstrip('\n\r')
instance_key = keys_file.readline().rstrip('\n\r')
instance_object_count = int(keys_file.readline().rstrip('\n\r'))
keys_file.close()

kb_db_name = 'knowledge_base'
kb = KnowledgeBase(kb_db_name)

dm_db_name = 'delta_memory'
dm = DeltaMemory(dm_db_name, kb)

initial_data = np.genfromtxt(path + 'initial_guess.log')
bad_guesses_euler = np.genfromtxt(path + 'bad_guesses.log')
if len(bad_guesses_euler.shape) == 1 and bad_guesses_euler.shape[0] != 0:
    bad_guesses_euler = bad_guesses_euler[np.newaxis]
bad_guesses = list()
for i, guess in enumerate(bad_guesses_euler):
    bad_guess_q = np.zeros(7)
    bad_guess_q[0:3] = guess[0:3]
    q = tf.quaternion_from_euler(np.radians(guess[3]), np.radians(guess[4]), np.radians(guess[5]))
    bad_guess_q[3:] = np.array([q[0], q[1], q[2], q[3]])
    bad_guesses.append(bad_guess_q)
bad_guesses = np.array(bad_guesses)

file_names = dm.get_data_file_names(object_key, instance_key)
mapping_file_names = [x for x in file_names if x.find('pkl') != -1]
mapping_data_file_names = [x for x in file_names if x.find('npy') != -1]
pos_mappings = list()
pos_mapping_data = list()
neg_mappings = list()
neg_mapping_data = list()

predicate_object_mappings = dm.get_data_object_mappings(object_key, instance_key)
object_mappings = list()
for pred, obj_mapping in predicate_object_mappings.iteritems():
    for m in obj_mapping:
        object_mappings.append(m)
        for x in mapping_file_names:
            if ('_' + pred + '_') in x:
                if not 'not' in x:
                    pos_mappings.append(joblib.load(path + x))
                else:
                    if os.path.isfile(path + x):
                        neg_mappings.append(joblib.load(path + x))
                    else:
                        neg_mappings.append(None)

        for x in mapping_data_file_names:
            if ('_' + pred + '_') in x:
                if not 'not' in x:
                    pos_mapping_data.append(np.load(path + x))
                else:
                    if os.path.isfile(path + x):
                        neg_mapping_data.append(np.load(path + x))
                    else:
                        neg_mapping_data.append(None)

#we divide by twelve because we have both initial pose and bounding box data;
#we subtract one after the division because we don't want to count the manipulated object
static_objects_count = len(initial_data) / 12 - 1
static_objects = list()
symb_dict = dict()

for i in xrange(static_objects_count):
    start_idx = (i+1) * 12

    obj = ObjectData(initial_data[start_idx], initial_data[start_idx+1], initial_data[start_idx+2], \
    initial_data[start_idx+3], initial_data[start_idx+4], initial_data[start_idx+5], \
    initial_data[start_idx+6], initial_data[start_idx+7], initial_data[start_idx+8], \
    initial_data[start_idx+9], initial_data[start_idx+10], initial_data[start_idx+11])

    static_objects.append(obj)

if instance_object_count > 1:
    for i in xrange(static_objects_count):
        for j in xrange(static_objects_count):
            if i != j:
                symb = global_utils.vector_to_string(global_utils.calculate_predicate_values([static_objects[i], static_objects[j]]))
                symb_dict[(i,j)] = symb

symb_matches, geom_matches = dm.find_matches(object_key, instance_key, static_objects, symb_dict)
geom_data = dm.get_geometric_data(object_key, instance_key)

#a list of all initial guesses (in case we have multiple matchings)
guess_list = dict()

if instance_object_count > 1:
    #we create a list that stores the positions of the manipulated object and all static objects
    #(the position of the manipulated object is just a guess for initialising the optimisation)
    initial_guess = np.zeros(9)

    gsm_distribution = np.array(geom_data[2])
    gsm_cumsum_x = np.cumsum(gsm_distribution[0])
    gsm_cumsum_y = np.cumsum(gsm_distribution[1])
    gsm_boundaries = np.array(geom_data[3])

    for key, matches in geom_matches.iteritems():
        if len(matches) == 1:
            if matches[0].match_description == GeometricMatchDescriptions.DANGEROUS:
                continue

            left_object = None
            right_object = None
            guess_obj_key = None
            if static_objects[key[0]].init_position.x < static_objects[key[1]].init_position.x:
                left_object = static_objects[key[0]]
                right_object = static_objects[key[1]]
                guess_obj_key = tuple((key[1], key[0]))
            else:
                right_object = static_objects[key[0]]
                left_object = static_objects[key[1]]
                guess_obj_key = tuple((key[0], key[1]))

            #enlarging the geometric sampling distribution so that it covers the region between the current objects
            left_x = left_object.init_bounding_box.max.x
            delta_diff_x = abs(dm.get_geometric_data(object_key, matches[0].match_index)[0])
            obj_diff_x = right_object.init_bounding_box.min.x - left_object.init_bounding_box.max.x
            gamma = obj_diff_x / delta_diff_x
            distribution_boundaries_x = np.zeros(len(gsm_boundaries[0]))
            for i, x in enumerate(gsm_boundaries[0]):
                boundary = gamma * x + left_x
                distribution_boundaries_x[i] = boundary

            #importance sampling from the geometric sampling model; this should give us
            #an initial guess that maximises the probability of execution success
            r = np.random.uniform()
            r_greater = np.where(r > gsm_cumsum_x)[0]
            guess_bin_x = 0
            if len(r_greater) > 0:
                guess_bin_x = r_greater[-1] + 1


            below_object = None
            above_object = None
            if static_objects[key[0]].init_position.y < static_objects[key[1]].init_position.y:
                below_object = static_objects[key[0]]
                above_object = static_objects[key[1]]
            else:
                above_object = static_objects[key[0]]
                below_object = static_objects[key[1]]

            #enlarging the geometric sampling distribution so that it covers the region between the current objects
            below_y = below_object.init_position.y
            delta_diff_y = abs(dm.get_geometric_data(object_key, matches[0].match_index)[1])
            obj_diff_y = above_object.init_position.y - below_object.init_position.y
            if abs(delta_diff_y) < 1e-100:
                delta_diff_y = 1.
            gamma = obj_diff_y / delta_diff_y
            distribution_boundaries_y = np.zeros(len(gsm_boundaries[1]))
            for i, y in enumerate(gsm_boundaries[1]):
                boundary = gamma * y + below_y
                distribution_boundaries_y[i] = boundary

            #importance sampling from the geometric sampling model; this should give us
            #an initial guess that maximises the probability of execution success
            r = np.random.uniform()
            r_greater = np.where(r > gsm_cumsum_y)[0]
            guess_bin_y = 0
            if len(r_greater) > 0:
                guess_bin_y = r_greater[-1] + 1

            #shifting the objects to positions around the guess such that the distance
            #between the new positions will match the training data distance
            if matches[0].match_description == GeometricMatchDescriptions.FARTHER:
                left_object.init_bounding_box.max.x = distribution_boundaries_x[guess_bin_x] - gsm_boundaries[0][guess_bin_x]
                right_object.init_bounding_box.min.x = left_object.init_bounding_box.max.x + delta_diff_x

            initial_guess[0] = np.random.uniform(distribution_boundaries_x[guess_bin_x], distribution_boundaries_x[guess_bin_x+1])
            initial_guess[1] = np.random.uniform(distribution_boundaries_y[guess_bin_y], distribution_boundaries_y[guess_bin_y+1])
            initial_guess[2] = initial_data[2]

            initial_guess[3] = right_object.init_bounding_box.min.x
            initial_guess[4] = right_object.init_position.y
            initial_guess[5] = right_object.init_position.z

            initial_guess[6] = left_object.init_bounding_box.max.x
            initial_guess[7] = left_object.init_position.y
            initial_guess[8] = left_object.init_position.z

            guess_list[guess_obj_key] = np.array(initial_guess)
        else:
            #take the most appropriate match from the list of matches
            pass
else:
    delta_bb_size_x = geom_data[0]
    delta_bb_size_y = geom_data[1]

    gsm_distribution_x = np.array(geom_data[2][0])
    gsm_distribution_y = np.array(geom_data[2][1])
    gsm_cumsum_x = np.cumsum(gsm_distribution_x)
    gsm_cumsum_y = np.cumsum(gsm_distribution_y)
    gsm_boundaries_x = np.array(geom_data[3][0])
    gsm_boundaries_y = np.array(geom_data[3][1])

    for k, obj in enumerate(static_objects):
        #enlarging the geometric sampling distribution so that it covers the region between the current objects
        min_x = obj.init_bounding_box.min.x
        min_y = obj.init_bounding_box.min.y

        bb_size_x = obj.init_bounding_box.max.x - obj.init_bounding_box.min.x
        bb_size_y = obj.init_bounding_box.max.y - obj.init_bounding_box.min.y

        gamma_x = bb_size_x / delta_bb_size_x
        gamma_y = bb_size_y / delta_bb_size_y

        distribution_boundaries_x = np.zeros(len(gsm_boundaries_x))
        for i, x in enumerate(gsm_boundaries_x):
            boundary = gamma_x * x + min_x
            distribution_boundaries_x[i] = boundary

        distribution_boundaries_y = np.zeros(len(gsm_boundaries_y))
        for i, y in enumerate(gsm_boundaries_y):
            boundary = gamma_y * y + min_y
            distribution_boundaries_y[i] = boundary

        #importance sampling from the geometric sampling model; this should give us
        #an initial guess that maximises the probability of execution success
        r = np.random.uniform()
        r_greater = np.where(r > gsm_cumsum_x)[0]
        guess_bin_x = 0
        if len(r_greater) > 0:
            guess_bin_x = r_greater[-1] + 1

        r = np.random.uniform()
        r_greater = np.where(r > gsm_cumsum_y)[0]
        guess_bin_y = 0
        if len(r_greater) > 0:
            guess_bin_y = r_greater[-1] + 1

        initial_guess = np.zeros(6)
        initial_guess[0] = np.random.uniform(distribution_boundaries_x[guess_bin_x], distribution_boundaries_x[guess_bin_x+1])
        initial_guess[1] = np.random.uniform(distribution_boundaries_y[guess_bin_y], distribution_boundaries_y[guess_bin_y+1])
        initial_guess[2] = initial_data[2]

        initial_guess[3] = initial_data[9]
        initial_guess[4] = initial_data[10]
        initial_guess[5] = initial_data[23]

        guess_list[k] = np.array(initial_guess)

optimised_data = list()
for key, guess in guess_list.iteritems():
    if instance_object_count > 1:
        non_constant_elements = np.array([9,10,11,18,19,20,21])
        x0 = np.zeros(30)

        data_idx = np.random.randint(0, len(pos_mapping_data))
        initial_guess_idx = np.random.randint(0, pos_mapping_data[data_idx].shape[0])

        static_z = guess[5]
        guess[2] = pos_mapping_data[data_idx][initial_guess_idx,8] + static_z

        #bounding boxes
        x0[0:3] = [initial_data[6] - initial_data[3], initial_data[7] - initial_data[4], initial_data[8] - initial_data[5]]
        x0[3:6] = [static_objects[key[0]].init_bounding_box.max.x - static_objects[key[0]].init_bounding_box.min.x, \
        static_objects[key[0]].init_bounding_box.max.y - static_objects[key[0]].init_bounding_box.min.y, \
        static_objects[key[0]].init_bounding_box.max.z - static_objects[key[0]].init_bounding_box.min.z]
        x0[6:9] = [static_objects[key[1]].init_bounding_box.max.x - static_objects[key[1]].init_bounding_box.min.x, \
        static_objects[key[1]].init_bounding_box.max.y - static_objects[key[1]].init_bounding_box.min.y, \
        static_objects[key[1]].init_bounding_box.max.z - static_objects[key[1]].init_bounding_box.min.z]

        #positions
        x0[9:12] = guess[0:3]
        x0[12:15] = guess[3:6]
        x0[15:18] = guess[6:]

        #orientations
        x0[18:22] = pos_mapping_data[data_idx][initial_guess_idx][9:13]
        x0[22:26] = tf.quaternion_from_euler(static_objects[key[0]].init_rotation.roll, static_objects[key[0]].init_rotation.pitch, static_objects[key[0]].init_rotation.yaw)
        x0[26:] = tf.quaternion_from_euler(static_objects[key[1]].init_rotation.roll, static_objects[key[1]].init_rotation.pitch, static_objects[key[1]].init_rotation.yaw)

        #we swap the positions of the static objects if they are not in the order preserved by the training data
        if (object_mappings[0][1] == 1 and int(np.sign(guess[0] - guess[3])) != int(np.sign(pos_mapping_data[data_idx][initial_guess_idx][6]))) \
        or (object_mappings[0][1] == 2 and int(np.sign(guess[0] - guess[6])) != int(np.sign(pos_mapping_data[data_idx][initial_guess_idx][6]))):
            x0[3:6] = [static_objects[key[1]].init_bounding_box.max.x - static_objects[key[1]].init_bounding_box.min.x, \
            static_objects[key[1]].init_bounding_box.max.y - static_objects[key[1]].init_bounding_box.min.y, \
            static_objects[key[1]].init_bounding_box.max.z - static_objects[key[1]].init_bounding_box.min.z]
            x0[6:9] = [static_objects[key[0]].init_bounding_box.max.x - static_objects[key[0]].init_bounding_box.min.x, \
            static_objects[key[0]].init_bounding_box.max.y - static_objects[key[0]].init_bounding_box.min.y, \
            static_objects[key[0]].init_bounding_box.max.z - static_objects[key[0]].init_bounding_box.min.z]

            x0[12:15] = guess[6:]
            x0[15:18] = guess[3:6]

            x0[22:26] = tf.quaternion_from_euler(static_objects[key[1]].init_rotation.roll, static_objects[key[1]].init_rotation.pitch, static_objects[key[1]].init_rotation.yaw)
            x0[26:] = tf.quaternion_from_euler(static_objects[key[0]].init_rotation.roll, static_objects[key[0]].init_rotation.pitch, static_objects[key[0]].init_rotation.yaw)

        x_opt = optimisation.find_geometric_state(x0, pos_mappings, pos_mapping_data, neg_mappings, neg_mapping_data, object_mappings, non_constant_elements, bad_guesses, sign=-1.)
        r = np.array(tf.euler_from_quaternion(np.array([x_opt[18], x_opt[19], x_opt[20], x_opt[21]])))

        data = np.zeros(6)
        data[0:3] = x_opt[9:12]
        data[3] = np.degrees(r[0])
        data[4] = np.degrees(r[1])
        data[5] = np.degrees(r[2])
        optimised_data.append(data)
    else:
        non_constant_elements = np.array([6,7,8,12,13,14,15])
        x0 = np.zeros(20)

        data_idx = np.random.randint(0, len(pos_mapping_data))
        initial_guess_idx = np.random.randint(0, pos_mapping_data[data_idx].shape[0])

        static_z = guess[5]
        guess[2] = pos_mapping_data[data_idx][initial_guess_idx,8] + static_z

        #bounding boxes
        x0[0:3] = [initial_data[6] - initial_data[3], initial_data[7] - initial_data[4], initial_data[8] - initial_data[5]]
        x0[3:6] = [static_objects[key].init_bounding_box.max.x - static_objects[key].init_bounding_box.min.x, \
        static_objects[key].init_bounding_box.max.y - static_objects[key].init_bounding_box.min.y, \
        static_objects[key].init_bounding_box.max.z - static_objects[key].init_bounding_box.min.z]

        #positions
        x0[6:9] = guess[0:3]
        x0[9:12] = guess[3:6]

        #orientations
        x0[12:16] = pos_mapping_data[data_idx][initial_guess_idx][9:13]
        x0[16:] = tf.quaternion_from_euler(static_objects[key].init_rotation.roll, static_objects[key].init_rotation.pitch, static_objects[key].init_rotation.yaw)

        x_opt = optimisation.find_geometric_state(x0, pos_mappings, pos_mapping_data, neg_mappings, neg_mapping_data, object_mappings, non_constant_elements, bad_guesses, sign=-1.)
        r = np.array(tf.euler_from_quaternion(np.array([x_opt[12], x_opt[13], x_opt[14], x_opt[15]])))

        data = np.zeros(6)
        data[0:3] = x_opt[6:9]
        data[3] = np.degrees(r[0])
        data[4] = np.degrees(r[1])
        data[5] = np.degrees(r[2])
        optimised_data.append(data)

optimised_data = np.array(optimised_data)
np.savetxt(path + 'optimised_guess.log', optimised_data)
