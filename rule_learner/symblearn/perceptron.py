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
from scipy.misc import comb
from copy import deepcopy

class DataContainer(object):
    def __init__(self, data, labels):
        self.features = np.array(data)
        self.labels = np.array(labels)

    def __deepcopy__(self, memo):
        return DataContainer(self.features, self.labels)

class KernelFunctionsLibrary(object):
    @staticmethod
    def kDNF(x1, x2, k):
        same_bits_count = len(x1) - np.count_nonzero(x1 - x2)
        s = 0
        for i in xrange(k+1):
            s += comb(same_bits_count, i)
        return s

class VotedPerceptron(object):
    '''Implements a voted perceptron as described on/in
    - http://curtis.ml.cmu.edu/w/courses/index.php/Voted_Perceptron
    - K. Mourao, Learning Action Representations Using Kernel Perceptrons. PhD thesis, School of Informatics, Univ. of Edinburgh, 2012.

    Author -- Alex Mitrevski

    '''
    def __init__(self):
        self.misclassification_counters = None
        self.correct_prediction_counters = None
        self.data = None

    def train(self, data, iterations=1, kernel_k=2):
        '''Trains the voted perceptron using 'data'.

        Keyword arguments:
        data -- A 'DataContainer' object.
        iterations -- Number of times the algorithms should go through the training data.
        kernel_k -- The k value of the k-DNF kernel (default 2).

        '''
        self.data = deepcopy(data)
        self.misclassification_counters = np.zeros(data.features.shape[0], dtype=np.int32)
        self.correct_prediction_counters = np.zeros(data.features.shape[0], dtype=np.int32)

        k = 0
        training_vector_count = self.data.features.shape[0]
        for _ in xrange(iterations):
            for i in xrange(training_vector_count):
                s = 0
                for j in xrange(i+1):
                    if self.misclassification_counters[j] != 0:
                        s += (self.misclassification_counters[j] * self.data.labels[j] * KernelFunctionsLibrary.kDNF(self.data.features[j], self.data.features[i], kernel_k))
                prediction = np.sign(s)
                if prediction == self.data.labels[i]:
                    self.correct_prediction_counters[k] += 1
                else:
                    self.misclassification_counters[i] += 1
                    self.correct_prediction_counters[i] = 1
                    k = i

    def predict(self, x, kernel_k=2):
        '''Returns a predicted class for 'x'.

        Keyword arguments:
        x -- A one-dimensional 'numpy' array.
        kernel_k -- The k value of the k-DNF kernel (default 2).

        '''
        training_vector_count = self.data.features.shape[0]
        s = 0
        for i in xrange(training_vector_count):
            if self.correct_prediction_counters[i] > 0:
                s_internal = 0
                for j in xrange(i+1):
                    if self.misclassification_counters[j] > 0:
                        s_internal += (self.misclassification_counters[j] * self.data.labels[j] * KernelFunctionsLibrary.kDNF(self.data.features[j], x, kernel_k))
                s += (self.correct_prediction_counters[i] * np.sign(s_internal))
        prediction = np.sign(s)
        return prediction

    def _calculate_support(self, x, kernel_k):
        '''Returns the support of 'x' based on the training data.

        x -- A one-dimensional 'numpy' array representing a precondition rule.
        kernel_k -- The k value of the k-DNF kernel.

        '''
        training_vector_count = self.data.features.shape[0]
        s = 0
        for i in xrange(training_vector_count):
            if self.correct_prediction_counters[i] > 0:
                s_internal = 0
                for j in xrange(i+1):
                    if self.misclassification_counters[j] > 0:
                        s_internal += (self.misclassification_counters[j] * self.data.labels[j] * KernelFunctionsLibrary.kDNF(self.data.features[j], x, kernel_k))
                s += (self.correct_prediction_counters[i] * np.sign(s_internal))
        return s

    def _rule_covers_negative_examples(self, rule, kernel_k):
        '''Returns True if 'rule' predicts a negative data sample to be positive and False otherwise.

        Keyword arguments:
        rule -- A one-dimensional 'numpy' array representing a precondition rule.
        kernel_k -- The k value of the k-DNF kernel.

        '''
        for i,v in enumerate(self.data.features):
            prediction = np.sign(KernelFunctionsLibrary.kDNF(rule, v, kernel_k))
            actual_label = self.data.labels[i]
            if actual_label == -1 and prediction == 1:
                return True
        return False

    def extract_precondition_vector(self, kernel_k=2):
        '''Extracts a precondition vector using the perceptron's
        support vector with the highest support from the training data.

        Keyword arguments:
        kernel_k -- The k value of the k-DNF kernel.

        '''
        support_vectors = np.array(self.data.features[np.where(self.misclassification_counters>0)[0],:])
        rule_support = np.zeros(support_vectors.shape[0])
        print support_vectors.shape[0]
        for i,p in enumerate(support_vectors):
            print i
            rule_support[i] = self._calculate_support(p, kernel_k)

        prec_vector_len = support_vectors.shape[1]
        support_v = support_vectors[np.argmax(rule_support)]

        current_rule = np.array(support_v)
        current_rule_support = self._calculate_support(current_rule, kernel_k)
        rule_extracted = False
        while not rule_extracted:
            new_rule_count = np.count_nonzero(current_rule)
            new_rules = np.zeros((new_rule_count, prec_vector_len), dtype=np.int32)
            new_rule_counter = 0
            for i in xrange(prec_vector_len):
                if current_rule[i] == 0:
                    continue

                new_prec = np.array(current_rule)
                new_prec[i] = 0
                new_rules[new_rule_counter] = new_prec
                new_rule_counter += 1

            rule_support = np.zeros(new_rule_count)
            for i,p in enumerate(new_rules):
                rule_support[i] = self._calculate_support(p, kernel_k)

            support_delta = current_rule_support - rule_support
            argmin_delta = np.argmin(support_delta)
            new_rule = new_rules[argmin_delta]
            too_general = self._rule_covers_negative_examples(new_rule, kernel_k)
            if too_general:
                rule_extracted = True
            else:
                current_rule = new_rule
                current_rule_support = rule_support[argmin_delta]

        return current_rule
