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

class KnowledgeBase(object):
    '''
    Author -- Alex Mitrevski
    '''
    def __init__(self, db_name):
        self.db_name = db_name
        self.db_server = couchdb.Server()
        if self.db_name not in self.db_server:
            self._create_db()
        self.kb = self.db_server[self.db_name]

    def _create_db(self):
        db = self.db_server.create(self.db_name)

        db['kb'] = { 'bottle' : ['ketchup_bottle'], \
        'book' : ['hardcover', 'paperback'], \
        'planar_surface' : ['table', 'shelf', 'fridge_door'] }

    def get_parent_key(self, key):
        parent = None

        doc = self.kb['kb']
        for k,v in doc.iteritems():
            if key in v:
                parent = k
                break

        return parent
