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

from symblearn.local_search import Evolver, RuleFinder
from symblearn.stat_learn import StatLearn
from symblearn.perceptron import VotedPerceptron, DataContainer

class RuleLearner(object):
    '''
    Author -- Alex Mitrevski
    '''
    def __init__(self, training_fitness_cb, vector_fitness_cb, predicate_acceptance_p, debug):
        self.training_fitness_cb = training_fitness_cb
        self.vector_fitness_cb = vector_fitness_cb
        self.predicate_acceptance_p = predicate_acceptance_p
        self.object_count = -1
        self.object_names = list()
        self.debug = debug

    def learn_rules(self, data, object_extraction_cb, predicate_calculation_cb, gt_data=None):
        pass

    def _convert_data(self, data, object_extraction_cb, predicate_calculation_cb):
        p_data = data[np.where(data[:,-1]>0)]
        n_data = data[np.where(np.abs(data[:,-1])<1e-10)]

        p_predicate_vectors = list()
        n_predicate_vectors = list()
        for i in xrange(p_data.shape[0]):
            objects = object_extraction_cb(p_data[i])
            p_predicate_vectors.append(predicate_calculation_cb(objects))

        for i in xrange(n_data.shape[0]):
            objects = object_extraction_cb(n_data[i])
            n_predicate_vectors.append(predicate_calculation_cb(objects))

        self.object_count = len(objects)
        p_predicate_vectors = np.array(p_predicate_vectors)
        n_predicate_vectors = np.array(n_predicate_vectors)
        return p_predicate_vectors, n_predicate_vectors

    def _get_object_names(self):
        object_names = ['x']
        object_counter = 1
        for _ in xrange(self.object_count-1):
            object_names.append('s' + str(object_counter))
            object_counter += 1
        return object_names

    def extract_positive_preconditions(self, precondition_vector, predicates, entry_mapping_cb, numeric=False):
        objects = self._get_object_names()
        predicate_count = len(predicates)
        object_entry_list = entry_mapping_cb(len(objects))
        preconditions = list()
        for i, x in enumerate(precondition_vector):
            if x:
                predicate_idx = i % predicate_count
                obj1_idx = object_entry_list[i][0]
                obj2_idx = object_entry_list[i][1]

                precondition = predicates[predicate_idx] + '('
                precondition += objects[obj1_idx] + ', ' + objects[obj2_idx]
                precondition += ')'
                preconditions.append(precondition)

        return preconditions

    def _get_full_precondition_vector(self, rule_candidates):
        precondition_prob = np.sum(rule_candidates, axis=0) / (rule_candidates.shape[0] * 1.)
        precondition_vector = np.array(precondition_prob > self.predicate_acceptance_p, dtype=np.int32)
        return precondition_vector

    def get_preconditions_static(self, precondition_vector, entry_mapping_cb):
        object_entry_list = entry_mapping_cb(self.object_count)
        preconditions = list()
        precondition_idx = list()
        for i, x in enumerate(precondition_vector):
            obj1_idx = object_entry_list[i][0]
            obj2_idx = object_entry_list[i][1]

            if obj1_idx != 0 and obj2_idx != 0:
                preconditions.append(x)
                precondition_idx.append(i)

        return np.array(preconditions), np.array(precondition_idx)

    def get_preconditions_manipulated(self, precondition_vector, entry_mapping_cb):
        object_entry_list = entry_mapping_cb(self.object_count)
        preconditions = list()
        precondition_idx = list()
        for i, x in enumerate(precondition_vector):
            obj1_idx = object_entry_list[i][0]
            obj2_idx = object_entry_list[i][1]

            if obj1_idx == 0 or obj2_idx == 0:
                preconditions.append(x)
                precondition_idx.append(i)

        return np.array(preconditions), np.array(precondition_idx)


class RuleEvolver(RuleLearner):
    '''
    Author -- Alex Mitrevski
    '''
    def __init__(self, training_fitness_cb, population_size=500, generation_count=100, population_count=5, \
    predicate_acceptance_p=0.9, mutation_probability=-1, mutation_max_element_count=0, debug=False, vector_fitness_cb=None):
        super(RuleEvolver, self).__init__(training_fitness_cb, vector_fitness_cb, predicate_acceptance_p, debug)

        self.population_size = population_size
        self.generation_count = generation_count
        self.population_count = population_count
        self.mutation_probability = mutation_probability
        self.mutation_max_element_count = mutation_max_element_count

    def learn_rules(self, data, object_extraction_cb, predicate_calculation_cb, gt_data=None):
        p_predicate_vectors, n_predicate_vectors = self._convert_data(data, object_extraction_cb, predicate_calculation_cb)
        predicate_vector_length = p_predicate_vectors.shape[1]

        rule_evolver = Evolver(p_predicate_vectors, n_predicate_vectors, self.population_size, predicate_vector_length, self.object_count)
        fitness_per_iteration = np.zeros((self.population_count, self.generation_count))
        population_preconditions = np.zeros((self.population_count, predicate_vector_length))
        for i in xrange(self.population_count):
            print i+1
            rule_population, fitness = rule_evolver.evolve(self.training_fitness_cb, self.generation_count)
            population_preconditions[i] = self._get_full_precondition_vector(rule_population)
            fitness_per_iteration[i] = fitness

        mean_fitness_per_iteration = np.mean(fitness_per_iteration, axis=0)
        std_fitness_per_iteration = np.std(fitness_per_iteration, axis=0, ddof=1)

        precondition_prob = np.sum(population_preconditions, axis=0) / (population_preconditions.shape[0] * 1.)
        full_precondition_vector = np.array(precondition_prob > self.predicate_acceptance_p)

        if not self.debug:
            return full_precondition_vector
        else:
            fitness = self.vector_fitness_cb(p_predicate_vectors, n_predicate_vectors, np.array(full_precondition_vector, dtype=np.int32))
            if gt_data is None:
                return full_precondition_vector, fitness
            else:
                gt_p_predicate_vectors, gt_n_predicate_vectors = self._convert_data(gt_data, object_extraction_cb, predicate_calculation_cb)
                gt_fitness = self.vector_fitness_cb(gt_p_predicate_vectors, gt_n_predicate_vectors, np.array(full_precondition_vector, dtype=np.int32))
                return full_precondition_vector, fitness, gt_fitness

class RuleOptimiser(RuleLearner):
    '''
    Author -- Alex Mitrevski
    '''
    def __init__(self, vector_fitness_cb, predicate_acceptance_p=0.9, restart_count=10, \
    max_iterations=1000, initial_guess=None, vectors_to_avoid=None, eta=0.1, evaluation_fitness_cb=None, debug=False):
        super(RuleOptimiser, self).__init__(None, vector_fitness_cb, predicate_acceptance_p, debug)
        self.restart_count = restart_count
        self.max_iterations = max_iterations
        self.initial_guess = initial_guess
        self.vectors_to_avoid = vectors_to_avoid
        self.eta = eta
        self.evaluation_fitness_cb = evaluation_fitness_cb

    def learn_rules(self, data, object_extraction_cb, predicate_calculation_cb, gt_data=None):
        p_predicate_vectors, n_predicate_vectors = self._convert_data(data, object_extraction_cb, predicate_calculation_cb)
        predicate_vector_length = p_predicate_vectors.shape[1]

        precondition_candidates = np.zeros((self.restart_count, predicate_vector_length))
        rule_finder = RuleFinder(p_predicate_vectors, n_predicate_vectors)
        for i in xrange(self.restart_count):
            print i+1
            precondition_vector,_ = rule_finder.learn_precondition_vector(self.vector_fitness_cb, self.max_iterations, initial_guess=self.initial_guess, vectors_to_avoid=self.vectors_to_avoid, eta=self.eta, evaluation_fitness_cb=self.evaluation_fitness_cb)
            precondition_candidates[i] = precondition_vector

        precondition_prob = np.sum(precondition_candidates, axis=0) / (precondition_candidates.shape[0] * 1.)
        precondition_vector = np.array(precondition_prob > self.predicate_acceptance_p)

        if not self.debug:
            return precondition_vector
        else:
            fitness = self.vector_fitness_cb(p_predicate_vectors, n_predicate_vectors, np.array(precondition_vector, dtype=np.int32))
            if gt_data is None:
                return precondition_vector, fitness
            else:
                gt_p_predicate_vectors, gt_n_predicate_vectors = self._convert_data(gt_data, object_extraction_cb, predicate_calculation_cb)
                gt_fitness = self.vector_fitness_cb(gt_p_predicate_vectors, gt_n_predicate_vectors, np.array(precondition_vector, dtype=np.int32))
                return precondition_vector, fitness, gt_fitness


class RuleStatLearner(RuleLearner):
    '''
    Author -- Alex Mitrevski
    '''
    def __init__(self, predicate_acceptance_p=0.9, debug=False, vector_fitness_cb=None):
        super(RuleStatLearner, self).__init__(None, vector_fitness_cb, predicate_acceptance_p, debug)

    def learn_rules(self, data, object_extraction_cb, predicate_calculation_cb, gt_data=None):
        p_predicate_vectors, n_predicate_vectors = self._convert_data(data, object_extraction_cb, predicate_calculation_cb)
        rule_learner = StatLearn()
        precondition_vector,_ = rule_learner.extract_rules(p_predicate_vectors, self.predicate_acceptance_p)

        if not self.debug:
            return precondition_vector
        else:
            fitness = self.vector_fitness_cb(p_predicate_vectors, n_predicate_vectors, np.array(precondition_vector, dtype=np.int32))
            if gt_data is None:
                return precondition_vector, fitness
            else:
                gt_p_predicate_vectors, gt_n_predicate_vectors = self._convert_data(gt_data, object_extraction_cb, predicate_calculation_cb)
                gt_fitness = self.vector_fitness_cb(gt_p_predicate_vectors, gt_n_predicate_vectors, np.array(precondition_vector, dtype=np.int32))
                return precondition_vector, fitness, gt_fitness


class RuleLearnerMourao(RuleLearner):
    '''
    Author -- Alex Mitrevski
    '''
    def __init__(self, predicate_acceptance_p=0.9, debug=False, vector_fitness_cb=None):
        super(RuleLearnerMourao, self).__init__(None, vector_fitness_cb, predicate_acceptance_p, debug)

    def learn_rules(self, data, object_extraction_cb, predicate_calculation_cb, final_predicate_calculation_cb, gt_data=None):
        p_predicate_vectors, n_predicate_vectors = self._convert_data(data, object_extraction_cb, predicate_calculation_cb)
        predicate_vectors = list()
        output_vectors = list()

        for i in xrange(data.shape[0]):
            objects = object_extraction_cb(data[i])
            predicate_vector = predicate_calculation_cb(objects)
            final_predicate_vector = final_predicate_calculation_cb(objects)

            predicate_vector[np.where(predicate_vector==0)[0]] = -1
            predicate_vectors.append(predicate_vector)

        predicate_vectors = np.array(predicate_vectors)
        labels = np.array(data[:,-1], dtype=np.int32)
        labels[np.where(labels==0)[0]] = -1

        perceptron_data_container = DataContainer(predicate_vectors, labels)
        perceptron = VotedPerceptron()
        perceptron.train(perceptron_data_container, iterations=1, kernel_k=3)
        rule = perceptron.extract_precondition_vector(kernel_k=3)
        full_precondition_vector = np.array(rule > self.predicate_acceptance_p)

        if not self.debug:
            return full_precondition_vector
        else:
            fitness = self.vector_fitness_cb(p_predicate_vectors, n_predicate_vectors, np.array(full_precondition_vector, dtype=np.int32))
            if gt_data is None:
                return full_precondition_vector, fitness
            else:
                gt_p_predicate_vectors, gt_n_predicate_vectors = self._convert_data(gt_data, object_extraction_cb, predicate_calculation_cb)
                gt_fitness = self.vector_fitness_cb(gt_p_predicate_vectors, gt_n_predicate_vectors, np.array(full_precondition_vector, dtype=np.int32))
                return full_precondition_vector, fitness, gt_fitness


class RuleLearnerOnline(RuleLearner):
    '''
    Author -- Alex Mitrevski
    '''
    def __init__(self, predicate_acceptance_p=0.9, debug=False, vector_fitness_cb=None):
        super(RuleLearnerOnline, self).__init__(None, vector_fitness_cb, predicate_acceptance_p, debug)

    def learn_rules(self, data, object_extraction_cb, predicate_calculation_cb, gt_data=None):
        objects = object_extraction_cb(data[0])
        self.object_count = len(objects)

        precondition_vector = None
        for i in xrange(data.shape[0]):
            objects = object_extraction_cb(data[i])
            predicates = predicate_calculation_cb(objects)

            if precondition_vector is not None:
                if data[i,-1] > 0:
                    for j,p in enumerate(predicates):
                        if (p != 1 and precondition_vector[j] == 1) or (p != 0 and precondition_vector[j] == 0):
                            precondition_vector[j] = -1
                else:
                    for j,p in enumerate(predicates):
                        if (p == 1 and precondition_vector[j] != 1):
                            precondition_vector[j] = 0
            else:
                if data[i,-1] > 0:
                    precondition_vector = np.array(predicates)
                    idx = np.where(predicates==0)
                    precondition_vector[idx] = -1

        precondition_vector[np.where(precondition_vector==-1)[0]] = 0

        if not self.debug:
            return precondition_vector
        else:
            p_predicate_vectors, n_predicate_vectors = self._convert_data(data, object_extraction_cb, predicate_calculation_cb)
            fitness = self.vector_fitness_cb(p_predicate_vectors, n_predicate_vectors, np.array(precondition_vector, dtype=np.int32))
            if gt_data is None:
                return precondition_vector, fitness
            else:
                gt_p_predicate_vectors, gt_n_predicate_vectors = self._convert_data(gt_data, object_extraction_cb, predicate_calculation_cb)
                gt_fitness = self.vector_fitness_cb(gt_p_predicate_vectors, gt_n_predicate_vectors, np.array(precondition_vector, dtype=np.int32))
                return precondition_vector, fitness, gt_fitness
