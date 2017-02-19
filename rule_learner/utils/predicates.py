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

from shapely.geometry import Polygon
from conversion import TypeConverter, Types

class PredicateLibrary(object):
    '''An interface to various static predicate functions.

    Author -- Alex Mitrevski

    '''
    @staticmethod
    def create_polygons(b_box1, b_box2):
        obj1 = Polygon(((b_box1.min.x, b_box1.min.y), (b_box1.max.x, b_box1.min.y),\
        (b_box1.max.x, b_box1.max.y), (b_box1.min.x, b_box1.max.y)))

        obj2 = Polygon(((b_box2.min.x, b_box2.min.y), (b_box2.max.x, b_box2.min.y),\
        (b_box2.max.x, b_box2.max.y), (b_box2.min.x, b_box2.max.y)))

        return obj1, obj2

    @staticmethod
    def on(b_box1, b_box2, return_type=Types.BOOL):
        return TypeConverter.return_correct_type(abs(b_box1.min.z - b_box2.max.z) < 1e-5, return_type)

    @staticmethod
    def onTable(b_box1, b_box2, return_type=Types.BOOL):
        return TypeConverter.return_correct_type(abs(b_box1.min.z - b_box2.min.z) < 5, return_type)

    @staticmethod
    def leftOf(b_box1, b_box2, return_type=Types.BOOL):
        return TypeConverter.return_correct_type(b_box1.max.x < b_box2.min.x, return_type)

    @staticmethod
    def rightOf(b_box1, b_box2, return_type=Types.BOOL):
        return TypeConverter.return_correct_type(b_box1.min.x > b_box2.max.x, return_type)

    @staticmethod
    def above(b_box1, b_box2, return_type=Types.BOOL):
        return TypeConverter.return_correct_type(b_box1.min.z > b_box2.max.z, return_type)

    @staticmethod
    def below(b_box1, b_box2, return_type=Types.BOOL):
        return TypeConverter.return_correct_type(b_box1.max.z < b_box2.min.z, return_type)

    @staticmethod
    def behind(b_box1, b_box2, return_type=Types.BOOL):
        return TypeConverter.return_correct_type(b_box1.max.y < b_box2.min.y, return_type)

    @staticmethod
    def inFrontOf(b_box1, b_box2, return_type=Types.BOOL):
        return TypeConverter.return_correct_type(b_box1.min.y > b_box2.max.y, return_type)

    @staticmethod
    def ntpp(b_box1, b_box2, return_type=Types.BOOL):
        obj1, obj2 = PredicateLibrary.create_polygons(b_box1, b_box2)
        return TypeConverter.return_correct_type(obj1.within(obj2) and not obj1.equals(obj2), return_type)

    @staticmethod
    def ntppi(b_box1, b_box2, return_type=Types.BOOL):
        obj1, obj2 = PredicateLibrary.create_polygons(b_box1, b_box2)
        return TypeConverter.return_correct_type(obj2.within(obj1) and not obj1.equals(obj2), return_type)

    @staticmethod
    def ec(b_box1, b_box2, return_type=Types.BOOL):
        obj1, obj2 = PredicateLibrary.create_polygons(b_box1, b_box2)
        return TypeConverter.return_correct_type(obj1.touches(obj2), return_type)

    @staticmethod
    def dc(b_box1, b_box2, return_type=Types.BOOL):
        obj1, obj2 = PredicateLibrary.create_polygons(b_box1, b_box2)
        return TypeConverter.return_correct_type(obj1.disjoint(obj2), return_type)

    @staticmethod
    def eq(b_box1, b_box2, return_type=Types.BOOL):
        obj1, obj2 = PredicateLibrary.create_polygons(b_box1, b_box2)
        return TypeConverter.return_correct_type(obj1.equals(obj2), return_type)

    @staticmethod
    def po(b_box1, b_box2, return_type=Types.BOOL):
        obj1, obj2 = PredicateLibrary.create_polygons(b_box1, b_box2)
        return TypeConverter.return_correct_type(obj1.intersects(obj2) and not obj1.within(obj2) and not obj2.within(obj1), return_type)
