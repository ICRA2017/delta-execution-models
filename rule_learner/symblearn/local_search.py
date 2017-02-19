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

class Evolver(object):
    '''Implements a simple evolutionary algorithm for symbolic learning.

    Author -- Alex Mitrevski

    '''
    def __init__(self, pos_fitness_data, neg_fitness_data, population_count, gene_length, object_count, pos_fitness_gt_data=None, neg_fitness_gt_data=None):
        '''
        Keyword arguments:
        pos_fitness_data -- A 2D binary integer 'numpy' array with positive symbolic training data.
        neg_fitness_data -- A 2D binary integer 'numpy' array with negative symbolic training data.
        population_count -- An integer denoting the size of the population that the algorithm should preserve.
        gene_length -- An integer denoting the size of a single gene (the expected length should be equal to pos_fitness_data.shape[1]).
        object_count -- The number of distinct objects whose relations are encoded by the training data.
        pos_fitness_gt_data -- A 2D binary integer 'numpy' array with positive symbolic training data; used for the purpose of comparison if the training data are noisy.
        neg_fitness_gt_data -- A 2D binary integer 'numpy' array with negative symbolic training data; used for the purpose of comparison if the training data are noisy.

        '''
        self.population = None
        self.pos_fitness_data = np.array(pos_fitness_data)
        self.neg_fitness_data = np.array(neg_fitness_data)

        self.noisy_data = False
        self.pos_fitness_gt_data = None
        self.neg_fitness_gt_data = None

        if pos_fitness_gt_data is not None:
            self.pos_fitness_gt_data = np.array(pos_fitness_gt_data)
            self.neg_fitness_gt_data = np.array(neg_fitness_gt_data)
            self.noisy_data = True

        self.population_count = population_count
        self.gene_length = gene_length
        self.gene_segment_count = object_count
        self.gene_segment_size = self.gene_length / self.gene_segment_count
        self.gene_fitness = np.zeros(self.population_count)
        self.mutation_probability = -1.
        self.mutation_max_element_count = 0

    def evolve(self, fitness_callback, max_iterations=100, mutation_probability=-1, mutation_max_element_count=0):
        '''Runs an evolutionary algorithm for learning a population of symbolic models covering the training data.

        Keyword arguments:
        fitness_callback -- A fitness function that should be used by the algorithm.
        max_iterations -- Maximum number of generations (default 100).
        mutation_probability -- Mutation probability for each individual bit (default -1, which means that the genes will not be mutated).
        mutation_max_element_count -- Maximum number of bits that are allowed to change in a single gene (default 0).

        Returns:
        population -- A 2D 'numpy' array of trained symbolic models.
        fitness_per_iteration -- A one-dimensional 'numpy' array that stores the population's fitness at each generation.
        gt_fitness_per_iteration -- A one-dimensional 'numpy' array that stores the noise-free population's fitness at each generation (only returned if the training data are noisy).

        '''
        self.mutation_probability = mutation_probability
        self.mutation_max_element_count = mutation_max_element_count
        fitness_per_iteration = np.zeros(max_iterations)
        gt_fitness_per_iteration = np.zeros(max_iterations)

        self._generate_initial_population()
        for i in xrange(max_iterations):
            total_fitness = self._calculate_fitness(fitness_callback)
            fitness_per_iteration[i] = total_fitness
            if self.noisy_data:
                total_fitness = self._calculate_gt_fitness(fitness_callback)
                gt_fitness_per_iteration[i] = total_fitness

            self._crossover()
            if self.mutation_probability > 0:
                self._mutate()

        if not self.noisy_data:
            return np.array(self.population), fitness_per_iteration
        else:
            return np.array(self.population), fitness_per_iteration, gt_fitness_per_iteration

    def _generate_initial_population(self):
        '''Generates a random initial population of genes.
        '''
        self.population = np.random.randint(0, 2, (self.population_count, self.gene_length))        

    def _calculate_fitness(self, fitness_callback):
        self.gene_fitness = fitness_callback(self.pos_fitness_data, self.neg_fitness_data, self.population)
        total_fitness = np.sum(self.gene_fitness) / len(self.gene_fitness)
        self.gene_fitness = self.gene_fitness / np.sum(self.gene_fitness)
        return total_fitness

    def _calculate_gt_fitness(self, fitness_callback):
        gene_fitness = fitness_callback(self.pos_fitness_gt_data, self.neg_fitness_gt_data, self.population)
        total_fitness = np.sum(gene_fitness) / len(gene_fitness)
        return total_fitness

    def _crossover(self):
        population_copy = np.array(self.population)
        sampling_array = self._create_sampling_array()
        for i in xrange(self.population_count):
            gene1_index, gene2_index = self._choose_individuals(sampling_array)
            gene = population_copy[i]
            for j in xrange(self.gene_segment_count):
                segment_left_index = self.gene_segment_size * j
                segment_right_index = self.gene_segment_size * (j+1) - 1
                crossover_index = np.random.randint(segment_left_index, segment_right_index)
                gene[segment_left_index:crossover_index] = self.population[gene1_index, segment_left_index:crossover_index]
                gene[crossover_index+1:segment_right_index+1] = self.population[gene2_index, crossover_index+1:segment_right_index+1]
            population_copy[i] = gene
        self.population = population_copy

    def _mutate(self):
        for i in xrange(self.population_count):
            mutate_prob = np.random.uniform()
            if mutate_prob < self.mutation_probability:
                mutation_element_count = np.random.randint(0, self.mutation_max_element_count+1)
                mutated_elements = list()
                for i in xrange(mutation_element_count):
                    selected = False
                    element_index = -1
                    while not selected:
                        element_index = np.random.randint(0, self.gene_length)
                        if element_index not in mutated_elements:
                            selected = True
                    mutated_elements.append(element_index)
                    self.population[i, element_index] = 1 - self.population[i, element_index]

    def _create_sampling_array(self):
        '''Returns a cumulative gene fitness sum.
        '''
        sampling_array = np.zeros(self.population_count + 1)
        sampling_array[1:] = np.cumsum(self.gene_fitness)
        return sampling_array

    def _choose_individuals(self, sampling_array):
        '''Returns two gene indices sampled according to the distribution encoded by 'sampling_array'.

        Keyword arguments:
        sampling_array -- A cumulative array encoding a gene fitness distribution.

        '''
        sampling_p = np.random.uniform(0, sampling_array[-1])
        gene1 = np.argmin(sampling_array < sampling_p) - 1

        sampling_p = np.random.uniform(0, sampling_array[-1])
        gene2 = np.argmin(sampling_array < sampling_p) - 1

        return gene1, gene2


class RuleFinder(object):
    '''Implements a hill climbing algorithm for symbolic learning.

    Author -- Alex Mitrevski

    '''
    def __init__(self, pos_fitness_data, neg_fitness_data):
        '''
        Keyword arguments:
        pos_fitness_data -- A 2D binary integer 'numpy' array with positive symbolic training data.
        neg_fitness_data -- A 2D binary integer 'numpy' array with negative symbolic training data.

        '''
        self.pos_fitness_data = np.array(pos_fitness_data)
        self.neg_fitness_data = np.array(neg_fitness_data)

    def learn_precondition_vector(self, fitness_callback, max_iterations, initial_guess=None, vectors_to_avoid=None, eta=0.1, evaluation_fitness_cb=None):
        '''Runs hill climbing for learning a symbolic model covering the training data.

        Keyword arguments:
        fitness_callback -- The fitness function that should be used by the algorithm.
        max_iterations -- Maximum number of hill climbing iterations.
        initial_guess -- A one-dimensional 'numpy' array of the same length as the training data
                         that the algorithm should use as an initial guess (default None).
        vectors_to_avoid -- A 2D 'numpy' array of vectors that the algorithm should try to avoid (default None).
        eta -- The value of eta used when there are vectors that should be avoided (default 0.1).
        evaluation_fitness_cb -- A fitness function that can be used for comparison when there are vectors that should be avoided (default None).

        '''
        current_p = self._get_initial_state(initial_guess)
        fitness = self._calculate_fitness(fitness_callback, current_p, vectors_to_avoid, eta)
        current_fitness = fitness
        fitness_per_iteration = list()
        if evaluation_fitness_cb is not None:
            fitness_per_iteration.append(evaluation_fitness_cb(self.pos_fitness_data, vectors_to_avoid, current_p))
        else:
            fitness_per_iteration.append(current_fitness)

        iteration_counter = 0
        while iteration_counter < max_iterations:
            #we generate a random neighbour of the current state
            neighbour = self._generate_neighbour(current_p)
            neighbour_fitness = self._calculate_fitness(fitness_callback, neighbour, vectors_to_avoid, eta)
            delta_fitness = neighbour_fitness - current_fitness

            #we move to the neighbour only if it improves the fitness
            if delta_fitness > 0:
                current_p = np.array(neighbour)
                current_fitness = neighbour_fitness

            if evaluation_fitness_cb is not None:
                fitness_per_iteration.append(evaluation_fitness_cb(self.pos_fitness_data, vectors_to_avoid, neighbour))
            else:
                fitness_per_iteration.append(current_fitness)
            iteration_counter += 1

        return current_p, fitness_per_iteration

    def _get_initial_state(self, initial_guess):
        '''Returns a one-dimensional 'numpy' array representing the initial guess where the optimisation process should start.

        Keyword arguments:
        initial_guess -- A one-dimensional 'numpy' array that the algorithm should use as an initial guess.

        '''
        p = None
        if initial_guess is None:
            p = np.random.randint(0, 2, self.pos_fitness_data.shape[1])
        else:
            p = np.array(initial_guess)
        return p

    def _generate_neighbour(self, p):
        '''Chooses a random element in 'p' and flips its state.

        Keyword arguments:
        p -- A one-dimensional 'numpy' array representing the symbolic model at the current iteration of the algorithm.

        '''
        neighbour = np.array(p)
        bit_idx = np.random.randint(0, self.pos_fitness_data.shape[1])
        neighbour[bit_idx] = 1 - neighbour[bit_idx]
        return neighbour

    def _calculate_fitness(self, fitness_callback, p, vectors_to_avoid, eta):
        if vectors_to_avoid is None:
            return fitness_callback(self.pos_fitness_data, None, p)
        return fitness_callback(self.pos_fitness_data, vectors_to_avoid, p, eta=eta)
