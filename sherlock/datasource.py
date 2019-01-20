#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# datasource -- base class for datasources
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from abc import ABC  # abstract base class


class Datasource(ABC):

    '''
    Base class for all data source implementations. Methods not implemented but
    defined here are meant as abstract methods to be implemented in subclasses.
    '''

    def __init__(self, **kwargs):
        '''
        - safe unknown arguments
        '''
        self.kwargs = kwargs

    def setup(self):
        '''
        - validate datasource arguments, prepare execution
        '''
        pass

    def run(self):
        '''
        - fetch data, return to parser
        '''
        pass
