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

class FitnessFunctionLibrary(object):
    '''Interface to various static fitness functions.

    Author -- Alex Mitrevski

    '''
    @staticmethod
    def gene_fitness_positive(pos_data, neg_data, genes):
        max_errors = pos_data.shape[0] * pos_data.shape[1] * 1.
        gene_fitness = np.zeros(genes.shape[0])
        for idx,gene in enumerate(genes):
            cost = np.sum(np.abs(gene - pos_data))
            gene_fitness[idx] = 1. - (cost / max_errors)
        return gene_fitness

    @staticmethod
    def vector_fitness_sum(pos_data, neg_data, v, eta=0.1):
        max_pos_errors = pos_data.shape[0] * pos_data.shape[1] * 1.
        max_neg_errors = 1.
        positive_errors = np.sum(np.abs(v - pos_data))
        negative_agreements = 0.
        if neg_data is not None:
            negative_agreements = np.sum(np.array(v == neg_data, dtype=np.int32))
            max_neg_errors = neg_data.shape[0] * neg_data.shape[1] * 1.
        fitness = 1. - (1-eta) * (positive_errors / max_pos_errors) - eta * (negative_agreements / max_neg_errors)
        return fitness

    @staticmethod
    def vector_fitness_positive(pos_data, neg_data, v):
        max_errors = pos_data.shape[0] * pos_data.shape[1] * 1.
        cost = np.sum(np.abs(v - pos_data))
        fitness = 1. - (cost / max_errors)
        return fitness
