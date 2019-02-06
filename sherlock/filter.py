#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# filter -- base class for filter implementations
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


class Filter(ABC):

    '''
    Base class for filter implementations of sherlock results
    '''

    def __init__(self, **kwargs):
        '''
        safe arguments for processing
        '''
        self.kwargs = kwargs

    def run(self, line_d):
        '''
        run filter against line dictionary. must return boolean
        '''
        pass
