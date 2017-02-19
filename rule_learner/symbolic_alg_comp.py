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
from symbolic_learner import RuleStatLearner, RuleLearnerOnline, RuleLearnerMourao, RuleEvolver, RuleOptimiser
from symblearn.fitness import FitnessFunctionLibrary

keys_file = file('keys.txt', 'r')
object_key = keys_file.readline().rstrip('\n\r')
keys_file.close()

data = np.genfromtxt('data/' + object_key + '.log')
is_noisy_data = object_key.lower().find('noise') != -1
if is_noisy_data:
    object_key = object_key[0:object_key.lower().find('_')]
    gt_data = np.genfromtxt('data/' + object_key + '.log')

############################
# Learning by demonstration
############################
rule_learner = RuleStatLearner(debug=True, vector_fitness_cb=FitnessFunctionLibrary.vector_fitness_positive)
if not is_noisy_data:
    precondition_vector, fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values)
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Demonstration: ', fitness
    print pos_preconditions
else:
    precondition_vector, fitness, gt_fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values, gt_data=gt_data)
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Demonstration: ', fitness, ' -- ', gt_fitness
    print pos_preconditions

##################
# Online learning
##################
rule_learner = RuleLearnerOnline(debug=True, vector_fitness_cb=FitnessFunctionLibrary.vector_fitness_positive)
if not is_noisy_data:
    precondition_vector, fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values)
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Online: ', fitness
    print pos_preconditions
else:
    precondition_vector, fitness, gt_fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values, gt_data=gt_data)
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Online: ', fitness, ' -- ', gt_fitness
    print pos_preconditions

####################
# Hypothesis search
####################
rule_learner = RuleLearnerMourao(debug=True, vector_fitness_cb=FitnessFunctionLibrary.vector_fitness_positive)
if not is_noisy_data:
    precondition_vector, fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values, global_utils.calculate_final_predicate_values)
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Hypothesis search: ', fitness
    print pos_preconditions
else:
    precondition_vector, fitness, gt_fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values, global_utils.calculate_final_predicate_values, gt_data=gt_data)
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Hypothesis search: ', fitness, ' -- ', gt_fitness
    print pos_preconditions

#########################
# Evolutionary algorithm
#########################
rule_learner = RuleEvolver(training_fitness_cb=FitnessFunctionLibrary.gene_fitness_positive, population_size=1000, generation_count=500, population_count=10, debug=True, vector_fitness_cb=FitnessFunctionLibrary.vector_fitness_positive)
if not is_noisy_data:
    fit = np.zeros(10)
    for i in xrange(10):
        precondition_vector, fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values)
        fit[i] = fitness
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Evolutionary: ', np.mean(fit), np.std(fit)
    print pos_preconditions
else:
    fit = np.zeros(10)
    gt_fit = np.zeros(10)
    for i in xrange(10):
        precondition_vector, fitness, gt_fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values, gt_data=gt_data)
        fit[i] = fitness
        gt_fit[i] = gt_fitness
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Evolutionary: ', np.mean(fit), np.std(fit), ' -- ', np.mean(gt_fit), np.std(gt_fit)
    print pos_preconditions

################
# Hill climbing
################
rule_learner = RuleOptimiser(FitnessFunctionLibrary.vector_fitness_positive, restart_count=10, max_iterations=1000, debug=True)
if not is_noisy_data:
    fit = np.zeros(10)
    for i in xrange(10):
        precondition_vector, fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values)
        fit[i] = fitness
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Hill climbing: ', np.mean(fit), np.std(fit)
    print pos_preconditions
else:
    fit = np.zeros(10)
    gt_fit = np.zeros(10)
    for i in xrange(10):
        precondition_vector, fitness, gt_fitness = rule_learner.learn_rules(data, global_utils.extract_objects, global_utils.calculate_predicate_values, gt_data=gt_data)
        fit[i] = fitness
        gt_fit[i] = gt_fitness
    pos_preconditions = rule_learner.extract_positive_preconditions(precondition_vector, global_utils.predicate_names, global_utils.get_object_entry_list)
    print 'Hill climbing: ', np.mean(fit), np.std(fit), ' -- ', np.mean(gt_fit), np.std(gt_fit)
    print pos_preconditions
