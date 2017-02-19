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

class StatLearn(object):
    '''Implements a statistical symbolic learner; assumes discrete predicates.
    More details about this method can be found in the following papers:

    - S. Ekvall and D. Kragic, "Learning task models from multiple human demonstrations," in Robot and Human Interactive Communication, 2006. ROMAN 2006. 15th IEEE Int. Symp., pp. 358-363, Sept. 2006
    - N. Abdo et al., "Learning manipulation actions from a few demonstrations," in Robotics and Automation (ICRA), 2013 IEEE Int. Conf., pp. 1268-1275, May 2013.
    - R. Toris et al., "Unsupervised learning of multi-hypothesized pick-and-place task templates via crowdsourcing," in Robotics and Automation (ICRA), 2015 IEEE Int. Conf., pp. 4504-4510, May 2015.

    Author -- Alex Mitrevski

    '''
    def extract_rules(self, data, acceptance_threshold=0.9):
        '''Extracts a precondition set from 'data'.

        Keyword arguments:
        data -- A 2D 'numpy' array of symbolic relations. Each row of the array should be a separate training example.
        acceptance_threshold -- Threshold that controls the acceptance of the potential preconditions (default 0.9).

        Returns:
        precondition_vector -- A binary 'numpy' integer array of length 'data.shape[1]'; a value of 1 at a given index indicates that the predicate is a precondition of the respective action.
        precondition_values -- A 'numpy' integer array of length 'data.shape[1]' storing the values of the preconditions; the value of the predicates that are not preconditions will always be 0.

        '''
        precondition_vector = np.zeros(data.shape[1], dtype=np.int32)
        precondition_values = np.zeros(data.shape[1], dtype=np.int32)
        for i in xrange(data.shape[1]):
            predicate_value_prob = self._calculate_prob(data[:,i])
            predicate_entropy = self._entropy(predicate_value_prob)
            if predicate_entropy < acceptance_threshold:
                precondition_value = self._max_prob_value(predicate_value_prob)
                if precondition_value != 0:
                    precondition_vector[i] = 1
                    precondition_values[i] = precondition_value
        return precondition_vector, precondition_values

    def _calculate_prob(self, data):
        '''Calculates the probabilities of the individual values of a given predicate.

        Keyword arguments:
        data -- A one-dimensional 'numpy' array storing the observed values of a given predicate.

        Returns:
        prob -- A dictionary in which the keys represent predicate values and the values are the probabilities of the predicate values.

        '''
        prob = dict()
        values = dict()
        for d in data:
            if d in values:
                values[d] += 1
            else:
                values[d] = 1

        for k,v in values.iteritems():
            prob[k] = v / (len(data) * 1.)

        return prob

    def _entropy(self, value_prob):
        '''Calculates the entropy of the input probability distribution.

        Keyword arguments:
        value_prob -- A dictionary in which the keys represent predicate values and the values are the probabilities of the predicate values.

        '''
        entropy = 0.
        for v in value_prob:
            entropy = entropy + value_prob[v] * np.log2(value_prob[v])
        return -entropy

    def _max_prob_value(self, value_prob):
        '''Returns the key of the input dictionary with the maximum value.

        Keyword arguments:
        value_prob -- A dictionary in which the keys represent predicate values and the values are the probabilities of the predicate values.

        '''
        max_prob = -1.
        max_value = -1
        for v, prob in value_prob.iteritems():
            if prob > max_prob:
                max_prob = prob
                max_value = v
        return max_value
