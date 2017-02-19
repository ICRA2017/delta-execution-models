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

class Types(object):
    BOOL = 0
    INT = 1

class TypeConverter(object):
    '''An interface to various static type converions methods.

    Author -- Alex Mitrevski

    '''
    @staticmethod
    def bool_to_int(x):
        '''Converts a boolean to an integer value.

        Keyword arguments:
        x -- A boolean variable.

        '''
        if x:
            return 1
        else:
            return 0

    @staticmethod
    def return_correct_type(x, return_type):
        '''Returns the value of 'x' in the type 'return_type'.
        Doesn't return anything if 'return_type' is not 'Types.BOOL' or 'Types.INT'.

        Keyword arguments:
        x -- A boolean or integer variable.
        return_type -- A value of type 'Types'.

        '''
        if return_type == Types.BOOL:
            return x
        elif return_type == Types.INT:
            return TypeConverter.bool_to_int(x)
