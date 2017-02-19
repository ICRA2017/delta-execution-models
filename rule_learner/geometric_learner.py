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
from sklearn.neighbors import KernelDensity
from sklearn.grid_search import GridSearchCV
from sklearn.externals import joblib

from os import makedirs
from os.path import isdir

class GeometricLearner(object):
    '''
    Author -- Alex Mitrevski
    '''
    def __init__(self, predicates, manipulated_obj_predicates, manipulated_predicate_idx):
        self.predicates = list(predicates)
        self.manipulated_obj_predicates = np.array(manipulated_obj_predicates)
        self.manipulated_predicate_idx = np.array(manipulated_predicate_idx)

        self.object_count = -1
        self.predicate_count = len(self.predicates)

    def learn_geometric_predicates(self, save_dir, object_key, instance_key, data, object_extraction_cb, predicate_calculation_cb, geometric_data_extraction_cb, entry_mapping_cb):
        dir_created = self._create_directory(save_dir)
        if not dir_created:
            return None

        mapping_file_names = list()
        data_file_names = list()

        all_objects = list()
        predicate_vectors = list()
        labels = np.zeros(data.shape[0], dtype=bool)
        for i in xrange(data.shape[0]):
            objects = object_extraction_cb(data[i])
            predicate_vectors.append(predicate_calculation_cb(objects))
            all_objects.append(objects)
            labels[i] = data[i,-1] > 0.
        predicate_vectors = np.array(predicate_vectors)
        self.object_count = len(objects)
        pos_labels_set = np.where(labels)[0]

        manipulated_pos_predicate_idx = self.manipulated_predicate_idx[np.where(self.manipulated_obj_predicates==True)[0]]
        object_mappings = entry_mapping_cb(self.object_count)
        data_object_mappings = dict()

        predicate_mapping_dict = dict()
        distinct_predicates = list()

        for idx in manipulated_pos_predicate_idx:
            predicate_idx = idx % self.predicate_count
            if predicate_idx in distinct_predicates:
                predicate_mapping_dict[predicate_idx].append(idx)
            else:
                predicate_mapping_dict[predicate_idx] = [idx]
                distinct_predicates.append(predicate_idx)

        for predicate_idx in predicate_mapping_dict:
            positive_data_idx = list()
            negative_data_idx = list()
            positive_data_object_mapping = list()
            negative_data_object_mapping = list()

            for idx in predicate_mapping_dict[predicate_idx]:
                obj1_idx = object_mappings[idx][0]
                obj2_idx = object_mappings[idx][1]

                #we only take those data items where both the current predicate and the label are true
                positive_data_idx.append(np.intersect1d(pos_labels_set, np.where(predicate_vectors[:,idx]==1)[0]))
                positive_data_object_mapping.append((obj1_idx, obj2_idx))

                for manipulated_idx in self.manipulated_predicate_idx:
                    pred_idx = manipulated_idx % self.predicate_count
                    if pred_idx == predicate_idx:
                        obj1_idx = object_mappings[manipulated_idx][0]
                        obj2_idx = object_mappings[manipulated_idx][1]
                        negative_data_idx.append(np.where(predicate_vectors[:,manipulated_idx]==0)[0])
                        negative_data_object_mapping.append((obj1_idx, obj2_idx))

            positive_data = list()
            for i, obj_mapping_idx in enumerate(positive_data_object_mapping):
                for j in positive_data_idx[i]:
                    positive_data.append(geometric_data_extraction_cb(all_objects[j][obj_mapping_idx[0]], all_objects[j][obj_mapping_idx[1]]))
            positive_data = np.array(positive_data)

            negative_data = list()
            for i, obj_mapping_idx in enumerate(negative_data_object_mapping):
                for j in negative_data_idx[i]:
                    negative_data.append(geometric_data_extraction_cb(all_objects[j][obj_mapping_idx[0]], all_objects[j][obj_mapping_idx[1]]))
            negative_data = np.array(negative_data)

            grid = GridSearchCV(KernelDensity(), {'bandwidth': np.linspace(0.01, 5.0, 150)}, cv=min(10, positive_data.shape[0]))
            grid.fit(positive_data)
            geom_given_positive = grid.best_estimator_

            geom_given_negative = None
            if negative_data.shape[0] > 0:
                grid = GridSearchCV(KernelDensity(), {'bandwidth': np.linspace(0.01, 5.0, 150)}, cv=min(10, negative_data.shape[0]))
                grid.fit(negative_data)
                geom_given_negative = grid.best_estimator_

            mapping_file_name = save_dir + '/geom_given_' + self.predicates[predicate_idx] + '_' + str(idx) + '.pkl'
            data_file_name = save_dir + '/moving_' + self.predicates[predicate_idx] + '_' + str(idx) + '.npy'
            mapping_file_names.append(mapping_file_name)
            data_file_names.append(data_file_name)
            joblib.dump(geom_given_positive, mapping_file_name)
            np.save(data_file_name, positive_data)

            mapping_file_name = save_dir + '/geom_given_not_' + self.predicates[predicate_idx] + '_' + str(idx) + '.pkl'
            data_file_name = save_dir + '/moving_not_' + self.predicates[predicate_idx] + '_' + str(idx) + '.npy'
            mapping_file_names.append(mapping_file_name)
            data_file_names.append(data_file_name)
            if geom_given_negative is not None:
                joblib.dump(geom_given_negative, mapping_file_name)
                np.save(data_file_name, negative_data)

        for idx in manipulated_pos_predicate_idx:
            predicate_idx = idx % self.predicate_count
            obj1_idx = object_mappings[idx][0]
            obj2_idx = object_mappings[idx][1]
            if self.predicates[predicate_idx] not in data_object_mappings:
                data_object_mappings[self.predicates[predicate_idx]] = list()
            data_object_mappings[self.predicates[predicate_idx]].append((obj1_idx, obj2_idx))

        return mapping_file_names, data_file_names, data_object_mappings

    def _create_directory(self, dir_name):
        if isdir(dir_name):
            return True
        else:
            try:
                makedirs(dir_name)
                return True
            except OSError:
                return False
