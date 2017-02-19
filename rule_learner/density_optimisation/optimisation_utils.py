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
from scipy.optimize import minimize

'''Implements the geometric pose optimisation algorithm described in
R. Dearden and C. Burbridge, "Manipulation planning using learned symbolic state abstractions," Robotics and Autonomous Systems, vol. 62, no. 3, pp. 355-365, 2014.

Author -- Alex Mitrevski

'''
def convert_to_predicate_mapping(x, current_obj_mappings, obj_count):
    '''Extracts the elements from 'x' that correspond to the predicate
    currently considered by the optimisation algorithm.

    Keyword arguments:
    x -- A one-dimensional array storing object data.
    current_obj_mappings -- A one- or two-element array or tuple that stores
                            the object mapping of the current predicate.
    obj_count -- Number of objects in a given configuration.

    Returns:
    v -- Object data corresponding to the predicate.
    indices -- Indices of 'x' from which 'v' originates.

    '''
    v = np.zeros(mapping_vector_length)
    indices = dict()

    size_start_idx = 0
    pos_start_idx = obj_count * 3
    rotation_start_idx = 2 * obj_count * 3
    if len(current_obj_mappings) == 1:
        size_idx = size_start_idx + current_obj_mappings[0] * 3
        pos_idx = pos_start_idx + current_obj_mappings[0] * 3
        rotation_idx = rotation_start_idx + current_obj_mappings[0] * 4
        v[0:3] = x[size_idx:size_idx+3]
        v[3:6] = x[pos_idx:pos_idx+3]
        v[6:] = x[rotation_idx:rotation_idx+3]

        element_counter = 0
        for i in xrange(size_idx, size_idx+3):
            indices[i] = element_counter
            element_counter += 1
        for i in xrange(pos_idx, pos_idx+3):
            indices[i] = element_counter
            element_counter += 1
        for i in xrange(rotation_idx, rotation_idx+4):
            indices[i] = element_counter
            element_counter += 1
    elif len(current_obj_mappings) == 2:
        size1_idx = size_start_idx + current_obj_mappings[0] * 3
        size2_idx = size_start_idx + current_obj_mappings[1] * 3
        pos1_idx = pos_start_idx + current_obj_mappings[0] * 3
        pos2_idx = pos_start_idx + current_obj_mappings[1] * 3
        rotation1_idx = rotation_start_idx + current_obj_mappings[0] * 4
        rotation2_idx = rotation_start_idx + current_obj_mappings[1] * 4
        v[0:3] = x[size1_idx:size1_idx+3]
        v[3:6] = x[size2_idx:size2_idx+3]
        v[6:9] = x[pos1_idx:pos1_idx+3] - x[pos2_idx:pos2_idx+3]
        v[9:13] = x[rotation1_idx:rotation1_idx+4]
        v[13:] = x[rotation2_idx:rotation2_idx+4]

        element_counter = 0
        for i in xrange(size1_idx, size1_idx+3):
            indices[i] = element_counter
            element_counter += 1
        for i in xrange(size2_idx, size2_idx+3):
            indices[i] = element_counter
            element_counter += 1
        for i in xrange(pos1_idx, pos1_idx+3):
            indices[i] = element_counter
            element_counter += 1
        for i in xrange(rotation1_idx, rotation1_idx+4):
            indices[i] = element_counter
            element_counter += 1
        for i in xrange(rotation2_idx, rotation2_idx+4):
            indices[i] = element_counter
            element_counter += 1

    return v, indices


def convert_bad_guess_to_mapping(x, guess, current_obj_mappings, obj_count):
    '''Converts 'guess' to an appropriate object mapping for the predicate
    that is currently considered by the algorithm.

    Keyword arguments:
    x -- A one-dimensional array storing object data.
    guess -- A 7D object pose (3D position and a quaternion rotation).
    current_obj_mappings -- A one- or two-element array or tuple that stores
                            the object mapping of the current predicate.
    obj_count -- Number of objects in a given configuration.

    Returns:
    v -- Object data corresponding to the predicate.
    indices -- Indices of 'x' from which 'v' originates.

    '''
    v = np.zeros(mapping_vector_length)

    size_start_idx = 0
    pos_start_idx = obj_count * 3
    rotation_start_idx = 2 * obj_count * 3
    if len(current_obj_mappings) == 1:
        size_idx = size_start_idx + current_obj_mappings[0] * 3
        v[0:3] = x[size_idx:size_idx+3]
        v[3:6] = guess[0:3]
        v[6:] = guess[3:]
    elif len(current_obj_mappings) == 2:
        size1_idx = size_start_idx + current_obj_mappings[0] * 3
        size2_idx = size_start_idx + current_obj_mappings[1] * 3
        pos2_idx = pos_start_idx + current_obj_mappings[1] * 3
        rotation2_idx = rotation_start_idx + current_obj_mappings[1] * 4
        v[0:3] = x[size1_idx:size1_idx+3]
        v[3:6] = x[size2_idx:size2_idx+3]
        v[6:9] = guess[0:3] - x[pos2_idx:pos2_idx+3]
        v[9:13] = guess[3:]
        v[13:] = x[rotation2_idx:rotation2_idx+4]

    return v


def f(x, state_given_geom, state_data, state_given_not_geom, not_state_data, object_mappings, non_constant_elements, bad_guesses, sign=1.0):
    '''Function whose value is being optimised.

    Keyword arguments:
    x -- A one-dimensional array storing object data.
    state_given_geom -- A list of 'sklearn.neighbors.KernelDensity' objects.
    state_data -- A list of 2D 'numpy' arrays in which the i-th element stores the data encoded by 'state_given_geom[i]'.
    state_given_not_geom -- A list of 'sklearn.neighbors.KernelDensity' objects.
    not_state_data -- A list of 2D 'numpy' arrays in which the i-th element stores the data encoded by 'state_given_not_geom[i]'.
    object_mappings -- A list of one- or two-dimensional lists or tuples in which the i-th element
                       stores the indices of the objects to which 'state_given_geom[i]' corresponds.
    non_constant_elements -- Indices of the elements in 'x' that can be modified.
    bad_guesses -- A 2D 'numpy' array of object poses that should be avoided by the optimisation algorithm.
    sign -- If equal to 1, the function will be minimised; if equal to -1, the function will be maximised (default 1.0).

    '''
    obj_count = len(np.unique(np.concatenate(object_mappings)))
    guess_mask_values = list()
    p = 0.
    for i in xrange(len(state_given_geom)):
        current_obj_mappings = object_mappings[i]
        v,_ = convert_to_predicate_mapping(x, current_obj_mappings, obj_count)
        p_temp = state_given_geom[i].score_samples(v)
        p_not_temp = -1e100
        if state_given_not_geom[i] is not None:
            p_not_temp = state_given_not_geom[i].score_samples(v)
        else:
            p_not_temp = np.log(1. - np.exp(p_temp))

        if bad_guesses.shape[0] == 0:
            d = np.exp(p_temp) + np.exp(p_not_temp)
            if d < 1e-100:
                d = 1e-100
            p += (p_temp - np.log(d))
        else:
            p_temp = np.exp(p_temp) / (np.exp(p_temp) + np.exp(p_not_temp))
            for g in bad_guesses:
                v_guess = convert_bad_guess_to_mapping(x, g, current_obj_mappings, obj_count)
                mask_value = np.exp(-0.5 * v.dot(v_guess))
                guess_mask_values.append(mask_value)
            p_temp -= max(guess_mask_values)
            p += np.log(p_temp)

    return sign * p


def f_prime(x, state_given_geom, state_data, state_given_not_geom, not_state_data, object_mappings, non_constant_elements, bad_guesses, sign=1.0):
    '''Derivative of the function that is being optimised.

    Keyword arguments:
    x -- A one-dimensional array storing object data.
    state_given_geom -- A list of 'sklearn.neighbors.KernelDensity' objects.
    state_data -- A list of 2D 'numpy' arrays in which the i-th element stores the data encoded by 'state_given_geom[i]'.
    state_given_not_geom -- A list of 'sklearn.neighbors.KernelDensity' objects.
    not_state_data -- A list of 2D 'numpy' arrays in which the i-th element stores the data encoded by 'state_given_not_geom[i]'.
    object_mappings -- A list of one- or two-dimensional lists or tuples in which the i-th element
                       stores the indices of the objects to which 'state_given_geom[i]' corresponds.
    non_constant_elements -- Indices of the elements in 'x' that can be modified.
    bad_guesses -- A 2D 'numpy' array of object poses that should be avoided by the optimisation algorithm.
    sign -- If equal to 1, the function will be minimised; if equal to -1, the function will be maximised (default 1.0).

    '''
    predicate_count = len(state_given_geom)

    data_item_counts = np.zeros(predicate_count, dtype=np.int32)
    h_squared = np.ones(predicate_count)
    obj_count = len(np.unique(np.concatenate(object_mappings)))
    predicate_vs = list()
    predicate_index_mappings = list()
    predicate_eval = np.zeros(predicate_count)

    neg_data_item_counts = np.zeros(predicate_count, dtype=np.int32)
    not_h_squared = np.ones(predicate_count)
    not_predicate_eval = np.zeros(predicate_count)
    for i in xrange(predicate_count):
        #positive mappings
        data_item_counts[i] = state_given_geom[i].tree_.data.shape[0]
        h_squared[i] = state_given_geom[i].bandwidth**2

        current_obj_mappings = object_mappings[i]
        v, indices = convert_to_predicate_mapping(x, current_obj_mappings, obj_count)
        predicate_vs.append(v)
        predicate_index_mappings.append(indices)
        predicate_eval[i] = state_given_geom[i].score_samples(predicate_vs[i])

        #negative mappings
        if state_given_not_geom[i] is not None:
            neg_data_item_counts[i] = state_given_not_geom[i].tree_.data.shape[0]
            h_squared[i] = state_given_not_geom[i].bandwidth**2
            not_predicate_eval[i] = state_given_not_geom[i].score_samples(predicate_vs[i])
        else:
            not_predicate_eval[i] = np.log(1 - np.exp(state_given_geom[i].score_samples(predicate_vs[i])))

    kernels = list()
    not_kernels = list()
    for i in xrange(predicate_count):
        kernel = np.exp(-np.linalg.norm(state_data[i] - predicate_vs[i], axis=1)**2 / h_squared[i])
        kernels.append(kernel)

        if state_given_not_geom[i] is not None:
            not_kernel = np.exp(-np.linalg.norm(not_state_data[i] - predicate_vs[i], axis=1)**2 / not_h_squared[i])
            not_kernels.append(not_kernel)
        else:
            not_kernels.append(None)

    dim = len(x)
    derivatives = np.zeros(dim)
    for _,idx in enumerate(non_constant_elements):
        s = 0.
        for i in xrange(predicate_count):
            term_derivative = 0.
            not_term_derivative = 0.
            if idx in predicate_index_mappings[i]:
                j = predicate_index_mappings[i][idx]
                n = np.sum(kernels[i] * (state_data[i][:,j] - predicate_vs[i][j]))
                n_sum = np.sum(kernels[i])
                if n_sum < 1e-100:
                    n_sum = 1e-100

                term_derivative = n
                term_derivative /= n_sum

                if state_given_not_geom[i] is not None:
                    not_term_derivative = n
                    not_term_derivative += np.sum(not_kernels[i] * (not_state_data[i][:,j] - predicate_vs[i][j]))
                    not_term_derivative /= (n_sum + np.sum(not_kernels[i]))
                else:
                    not_term_derivative = n
                    not_term_derivative /= n_sum

            s += (term_derivative - not_term_derivative)
        derivatives[idx] = s

    return sign * np.array(derivatives)


def find_geometric_state(x0, state_given_geom, state_data, state_given_not_geom, not_state_data, object_mappings, non_constant_elements, bad_guesses, sign=1.0):
    r = minimize(f, x0, args=(state_given_geom, state_data, state_given_not_geom, not_state_data, object_mappings, non_constant_elements, bad_guesses, sign), method='BFGS', jac=f_prime, options={'disp': True})
    return r.x


mapping_vector_length = 17
