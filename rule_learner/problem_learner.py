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
from symblearn.fitness import FitnessFunctionLibrary
from knowledge_base import KnowledgeBase
from symbolic_learner import RuleEvolver, RuleOptimiser
from geometric_learner import GeometricLearner
from delta_memory.memory import DeltaMemory

kb_db_name = 'knowledge_base'
kb = KnowledgeBase(kb_db_name)

dm_db_name = 'delta_memory'
dm = DeltaMemory(dm_db_name, kb)

keys_file = file('keys.txt', 'r')
object_key = keys_file.readline().rstrip('\n\r')
instance_key = keys_file.readline().rstrip('\n\r')
keys_file.close()

data = np.genfromtxt('data/' + object_key + '_' + instance_key + '.log')

rule_optimiser = RuleOptimiser(FitnessFunctionLibrary.vector_fitness_positive, restart_count=10, max_iterations=200)
precondition_vector = rule_optimiser.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values, global_utils.predicate_names)

static_obj_predicates, static_predicate_idx = rule_optimiser.get_preconditions_static(precondition_vector, global_utils.get_object_entry_list)
manipulated_obj_predicates, manipulated_predicate_idx = rule_optimiser.get_preconditions_manipulated(precondition_vector, global_utils.get_object_entry_list)

geom_learner = GeometricLearner(global_utils.predicate_names, manipulated_obj_predicates, manipulated_predicate_idx)
geom_data_save_dir = 'data/learned_mappings/' + object_key + '_' + instance_key
data_pointers = geom_learner.learn_geometric_predicates(geom_data_save_dir, object_key, instance_key, data, global_utils.extract_objects, global_utils.calculate_predicate_values, global_utils.extract_geometric_mapping_data, global_utils.get_object_entry_list)

########################
# saving data to memory
########################
dm.add_object(object_key)

#######################
# saving symbolic data
#######################
symb_data_delta = ''
for p in static_obj_predicates:
    if p:
        symb_data_delta += '1'
    else:
        symb_data_delta += '0'

symb_data_full = ''
for p in precondition_vector:
    if p:
        symb_data_full += '1'
    else:
        symb_data_full += '0'

dm.add_symbolic_data(object_key, instance_key, symb_data_delta, symb_data_full)

########################
# saving geometric data
########################
geom_data_file_names = list()
geom_data_object_mappings = list()
if data_pointers is not None:
    geom_data_file_names = data_pointers[0] + data_pointers[1]
    geom_data_object_mappings = data_pointers[2]

geom_data = list()
objects = global_utils.extract_objects(data[0])
if len(objects) > 2:
    p_data = data[np.where(data[:,-1]>0)[0]]
    rel_dist = np.zeros((p_data.shape[0],2))
    orientations = np.zeros((p_data.shape[0],3))

    left_object_idx = -1
    right_object_idx = -1
    objects = global_utils.extract_objects(p_data[0])
    if objects[1].init_position.x < objects[2].init_position.x:
        left_object_idx = 1
        right_object_idx = 2
    else:
        right_object_idx = 1
        left_object_idx = 2

    behind_object_idx = -1
    in_front_of_object_idx = -1
    if objects[1].init_position.y < objects[2].init_position.y:
        behind_object_idx = 1
        in_front_of_object_idx = 2
    else:
        in_front_of_object_idx = 2
        behind_object_idx = 1

    for i in xrange(p_data.shape[0]):
        objects = global_utils.extract_objects(p_data[i])
        rel_dist[i,0] = objects[right_object_idx].init_bounding_box.max.x - objects[left_object_idx].init_bounding_box.min.x
        rel_dist[i,1] = objects[in_front_of_object_idx].init_position.y - objects[behind_object_idx].init_position.y
    geom_data = list(np.mean(rel_dist, axis=0))
elif len(objects) == 2:
    p_data = data[np.where(data[:,-1]>0)[0]]
    bounding_box_sizes = np.zeros((p_data.shape[0],2))
    orientations = np.zeros((p_data.shape[0],3))

    for i in xrange(p_data.shape[0]):
        objects = global_utils.extract_objects(p_data[i])
        bounding_box_sizes[i,0] = objects[1].init_bounding_box.max.x - objects[1].init_bounding_box.min.x
        bounding_box_sizes[i,1] = objects[1].init_bounding_box.max.y - objects[1].init_bounding_box.min.y
    geom_data = list(np.mean(bounding_box_sizes, axis=0))

dm.add_geometric_data(object_key, instance_key, geom_data, geom_data_file_names, geom_data_object_mappings)
