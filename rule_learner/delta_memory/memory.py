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

import couchdb
from matches import SymbolicMatchLibrary, GeometricMatchLibrary, GeometricMatchDescriptions, GeometricMatchInfo

class MemoryDocumentKeys(object):
    OBJECTS = 'objects'
    SYMBOLIC_DATA = 'symbolic'
    GEOMETRIC_DATA = 'geometric'
    DATA = 'data'
    DELTA = 'delta'
    FULL = 'full'
    LINKS = 'links'
    DATA_FILE_NAMES = 'data_file_names'
    DATA_OBJECT_MAPPINGS = 'data_object_mappings'
    DELETED_INSTANCES = 'deleted_instances'
    TOTAL_RETRIEVALS = 'total_retrievals'
    SUCCESSFUL_RETRIEVALS = 'successful_retrievals'

class DeltaMemory(object):
    def __init__(self, db_name, knowledge_base):
        self.db_name = db_name
        self.kb = knowledge_base

        self.db_server = couchdb.Server()
        if self.db_name not in self.db_server:
            self._create_db()
        self.em = self.db_server[self.db_name]

    def _create_db(self):
        db = self.db_server.create(self.db_name)
        db[MemoryDocumentKeys.OBJECTS] = { MemoryDocumentKeys.OBJECTS : list() }
        db[MemoryDocumentKeys.SYMBOLIC_DATA] = dict()
        db[MemoryDocumentKeys.GEOMETRIC_DATA] = dict()

    def add_object(self, object_key):
        doc = self.em[MemoryDocumentKeys.OBJECTS]
        if object_key not in doc[MemoryDocumentKeys.OBJECTS]:
            doc[MemoryDocumentKeys.OBJECTS].append(object_key)
            self.em.save(doc)

        doc = self.em[MemoryDocumentKeys.SYMBOLIC_DATA]
        if object_key not in doc:
            doc[object_key] = { MemoryDocumentKeys.DATA : dict(), MemoryDocumentKeys.LINKS : dict(), MemoryDocumentKeys.DELETED_INSTANCES : dict() }
            self.em.save(doc)

        doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]
        if object_key not in doc:
            doc[object_key] = { MemoryDocumentKeys.DATA : dict(), MemoryDocumentKeys.DATA_FILE_NAMES : dict(), MemoryDocumentKeys.DATA_OBJECT_MAPPINGS : dict(), MemoryDocumentKeys.LINKS : dict(), MemoryDocumentKeys.DELETED_INSTANCES : dict() }
            self.em.save(doc)

    def add_symbolic_data(self, object_key, instance_key, symbolic_data, full_symbolic_data):
        doc = self.em[MemoryDocumentKeys.SYMBOLIC_DATA]
        if object_key not in doc:
            doc[object_key] = { MemoryDocumentKeys.DATA : dict(), MemoryDocumentKeys.LINKS : dict(), MemoryDocumentKeys.DELETED_INSTANCES : dict() }

        doc[object_key][MemoryDocumentKeys.DATA][instance_key] = dict()
        doc[object_key][MemoryDocumentKeys.DATA][instance_key][MemoryDocumentKeys.DELTA] = symbolic_data
        doc[object_key][MemoryDocumentKeys.DATA][instance_key][MemoryDocumentKeys.FULL] = full_symbolic_data

        doc[object_key][MemoryDocumentKeys.LINKS][instance_key] = dict()
        doc[object_key][MemoryDocumentKeys.LINKS][instance_key][object_key] = { MemoryDocumentKeys.TOTAL_RETRIEVALS : '0', MemoryDocumentKeys.SUCCESSFUL_RETRIEVALS : '0' }

        if instance_key not in doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES]:
            doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES][instance_key] = list()
        self.em.save(doc)

    def add_geometric_data(self, object_key, instance_key, geometric_data, data_file_names, data_object_mappings):
        doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]
        if object_key not in doc:
            doc[object_key] = { MemoryDocumentKeys.DATA : dict(), MemoryDocumentKeys.DATA_FILE_NAMES : dict(), MemoryDocumentKeys.DATA_OBJECT_MAPPINGS : dict(), MemoryDocumentKeys.LINKS : dict(), MemoryDocumentKeys.DELETED_INSTANCES : dict() }
        doc[object_key][MemoryDocumentKeys.DATA][instance_key] = geometric_data
        doc[object_key][MemoryDocumentKeys.DATA_FILE_NAMES][instance_key] = data_file_names
        doc[object_key][MemoryDocumentKeys.DATA_OBJECT_MAPPINGS][instance_key] = data_object_mappings

        doc[object_key][MemoryDocumentKeys.LINKS][instance_key] = dict()
        doc[object_key][MemoryDocumentKeys.LINKS][instance_key][object_key] = { MemoryDocumentKeys.TOTAL_RETRIEVALS : '0', MemoryDocumentKeys.SUCCESSFUL_RETRIEVALS : '0' }

        if instance_key not in doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES]:
            doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES][instance_key] = list()
        self.em.save(doc)

    def add_gsm(self, object_key, instance_key, pdf, boundaries):
        doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]
        doc[object_key][MemoryDocumentKeys.DATA][instance_key].append(pdf)
        doc[object_key][MemoryDocumentKeys.DATA][instance_key].append(boundaries)
        self.em.save(doc)

    def update_symbolic_link(self, object1_key, object2_key, instance_key, success):
        doc = self.em[MemoryDocumentKeys.SYMBOLIC_DATA]

        #use arbitrary precision arithmetic instead of integers
        total_retrievals = int(doc[object1_key][MemoryDocumentKeys.LINKS][instance_key][object2_key][MemoryDocumentKeys.TOTAL_RETRIEVALS])
        successful_retrievals = int(doc[object1_key][MemoryDocumentKeys.LINKS][instance_key][object2_key][MemoryDocumentKeys.SUCCESSFUL_RETRIEVALS])

        total_retrievals += 1
        if success:
            successful_retrievals += 1

        doc[object1_key][MemoryDocumentKeys.LINKS][instance_key][object2_key][MemoryDocumentKeys.TOTAL_RETRIEVALS] = str(total_retrievals)
        doc[object1_key][MemoryDocumentKeys.LINKS][instance_key][object2_key][MemoryDocumentKeys.SUCCESSFUL_RETRIEVALS] = str(successful_retrievals)

        self.em.save(doc)

    def update_geometric_link(self, object1_key, object2_key, instance_key, success):
        doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]

        #use arbitrary precision arithmetic instead of integers
        total_retrievals = int(doc[object1_key][MemoryDocumentKeys.LINKS][instance_key][object2_key][MemoryDocumentKeys.TOTAL_RETRIEVALS])
        successful_retrievals = int(doc[object1_key][MemoryDocumentKeys.LINKS][instance_key][object2_key][MemoryDocumentKeys.SUCCESSFUL_RETRIEVALS])

        total_retrievals += 1
        if success:
            successful_retrievals += 1

        doc[object1_key][MemoryDocumentKeys.LINKS][instance_key][object2_key][MemoryDocumentKeys.TOTAL_RETRIEVALS] = str(total_retrievals)
        doc[object1_key][MemoryDocumentKeys.LINKS][instance_key][object2_key][MemoryDocumentKeys.SUCCESSFUL_RETRIEVALS] = str(successful_retrievals)

        self.em.save(doc)

    def remove_symbolic_instance(self, object_key, instance_key):
        doc = self.em[MemoryDocumentKeys.SYMBOLIC_DATA]
        if object_key not in doc:
            return

        #adding the representation to the list of deleted ones in order to avoid learning it again
        if instance_key not in doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES]:
            doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES][instance_key] = list()
        doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES][instance_key].append(doc[object_key][MemoryDocumentKeys.DATA][instance_key][FULL])

        #removing the representation
        doc[object_key][MemoryDocumentKeys.DATA][instance_key][MemoryDocumentKeys.DELTA] = ''
        doc[object_key][MemoryDocumentKeys.DATA][instance_key][MemoryDocumentKeys.FULL] = ''
        doc[object_key][MemoryDocumentKeys.LINKS][instance_key] = dict()

        self.em.save(doc)

    def remove_geometric_instance(self, object_key, instance_key):
        doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]
        if object_key not in doc:
            return

        #adding the representation to the list of deleted ones in order to avoid learning it again
        if instance_key not in doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES]:
            doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES][instance_key] = list()
        doc[object_key][MemoryDocumentKeys.DELETED_INSTANCES][instance_key].append(doc[object_key][MemoryDocumentKeys.DATA][instance_key])

        #removing the representation
        doc[object_key][MemoryDocumentKeys.DATA][instance_key] = list()
        doc[object_key][MemoryDocumentKeys.LINKS][instance_key] = dict()

        self.em.save(doc)

    def get_symbolic_data(self, object_key, instance_key):
        doc = self.em[MemoryDocumentKeys.SYMBOLIC_DATA]
        data = doc[object_key][MemoryDocumentKeys.DATA][instance_key][MemoryDocumentKeys.DELTA]
        return data

    def get_full_symbolic_data(self, object_key, instance_key):
        doc = self.em[MemoryDocumentKeys.SYMBOLIC_DATA]
        data = doc[object_key][MemoryDocumentKeys.DATA][instance_key][MemoryDocumentKeys.FULL]
        return data

    def get_geometric_data(self, object_key, instance_key):
        doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]
        data = doc[object_key][MemoryDocumentKeys.DATA][instance_key]
        return data

    def get_data_file_names(self, object_key, instance_key):
        doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]
        data_file_names = doc[object_key][MemoryDocumentKeys.DATA_FILE_NAMES][instance_key]
        return data_file_names

    def get_data_object_mappings(self, object_key, instance_key):
        doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]
        data_object_mappings = doc[object_key][MemoryDocumentKeys.DATA_OBJECT_MAPPINGS][instance_key]
        return data_object_mappings

    def find_matches(self, obj, instance, new_objects, s):
        '''
        Keyword arguments:
        obj -- String description of a manipulated object.
        instance -- String description of a problem instance.
        new_objects -- A list of 'utils.object.ObjectData' objects.
        s -- A dictionary in which each key is a binary tuple of indices from 'new_objects';
             the value corresponding to each key is a string defining the symbolic relations between the two objects.
        '''

        symb_matches = self._find_symbolic_matches(obj, instance, s)
        if type(symb_matches) is list:
            return symb_matches, None

        geom_matches = self._find_geometric_matches(obj, instance, new_objects, symb_matches)
        return symb_matches, geom_matches

    def _find_symbolic_matches(self, obj, instance, s):
        '''Finds all matches between the symbolic representations in 's'
        and the memorised symbolic representations

        Keyword arguments:
        obj -- String description of a manipulated object.
        instance -- String description of a problem instance.
        s -- A dictionary in which each key is a binary tuple of object indices;
             the value corresponding to each key is a string defining the symbolic relations between the two objects.

        '''
        parent_instance = self.kb.get_parent_key(instance)
        symb_doc = self.em[MemoryDocumentKeys.SYMBOLIC_DATA]

        if not s:
            symb_matches = list()
            if obj in symb_doc:
                for symb_key,symb_instance in symb_doc[obj][MemoryDocumentKeys.DATA].iteritems():
                    if symb_key == instance or symb_key == parent_instance:
                        symb_matches.append(symb_key)

            for other_obj in symb_doc:
                if other_obj != '_id' and other_obj != '_rev' and other_obj != obj:
                    for symb_key,symb_instance in symb_doc[other_obj][MemoryDocumentKeys.DATA].iteritems():
                        if symb_key == instance or symb_key == parent_instance:
                            symb_matches.append(symb_key)

            return symb_matches

        symb_matches = dict()
        if obj in symb_doc:
            #we look for matches in the learned instances for 'obj'
            for key,new_instance in s.iteritems():
                symb_matches[key] = list()

                for symb_key,symb_instance in symb_doc[obj][MemoryDocumentKeys.DATA].iteritems():
                    if symb_key == instance or symb_key == parent_instance:
                        if SymbolicMatchLibrary.matches_instance(new_instance, symb_instance[MemoryDocumentKeys.DELTA]):
                            symb_matches[key].append(symb_key)

        #we look for matches in every other learned instance
        for other_obj in symb_doc:
            if other_obj != '_id' and other_obj != '_rev' and other_obj != obj:
                for key,new_instance in s.iteritems():
                    #we only use other models if we haven't found a match for the current object-instance combination
                    if len(symb_matches[key]) == 0:
                        for symb_key,symb_instance in symb_doc[other_obj][MemoryDocumentKeys.DATA].iteritems():
                            if symb_key == instance or symb_key == parent_instance:
                                if SymbolicMatchLibrary.matches_instance(new_instance, symb_instance[MemoryDocumentKeys.DELTA]):
                                    symb_matches[key].append(symb_key)

        return symb_matches

    def _find_geometric_matches(self, obj, instance, new_objects, symb_matches):
        '''Finds all matches between the memorised geometric representations
        and the objects for which the symbolic matches in 'symb_matches' hold.

        Keyword arguments:
        obj -- String description of a manipulated object.
        instance -- String description of a problem instance.
        new_objects -- A list of 'utils.object.ObjectData' objects.
        symb_matches -- A dictionary of symbolic matches returned by 'self._find_symbolic_matches'.

        '''
        parent_instance = self.kb.get_parent_key(instance)
        geom_doc = self.em[MemoryDocumentKeys.GEOMETRIC_DATA]
        geom_matches = dict()

        if obj in geom_doc:
            for key, instance_keys in symb_matches.iteritems():
                for geom_key in instance_keys:
                    #we check if we have a geometric match between the current two objects
                    #only if we are dealing with a known instance
                    if geom_key in geom_doc[obj][MemoryDocumentKeys.DATA]:
                        obj1 = new_objects[key[0]]
                        obj2 = new_objects[key[1]]
                        match = GeometricMatchLibrary.matches_instance((obj1, obj2), geom_doc[obj][MemoryDocumentKeys.DATA][geom_key])

                        #we check if there is a third object between the matched two in case we have a binary geometric match
                        for i,other_obj in enumerate(new_objects):
                            if i != key[0] and i != key[1]:
                                #declare the match as unsafe if there is a a third object between the matched two
                                if abs(obj1.init_bounding_box.min.z - other_obj.init_bounding_box.min.z) < 5 and abs(obj2.init_bounding_box.min.z - other_obj.init_bounding_box.min.z) < 5:
                                    if obj1.init_bounding_box.max.x < other_obj.init_bounding_box.min.x and obj2.init_bounding_box.min.x > other_obj.init_bounding_box.max.x:
                                        match = GeometricMatchDescriptions.DANGEROUS

                        if key not in geom_matches:
                            geom_matches[key] = list()
                        geom_matches[key].append(GeometricMatchInfo(geom_key, match))

        return geom_matches
