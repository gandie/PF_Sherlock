#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# output -- base class for parser result outputs
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
import os


class Output(ABC):

    '''
    Base class for output implementations of sherlock results.

    Basically a file-like object wrapper
    '''

    def setup(self):
        '''called before sherlock main loop. set up output stream'''
        pass

    def write(self, line_d):
        '''called during sherlock main loop. compute line_d and write'''
        pass

    def close(self):
        '''called after sherlock main loop. tell stream to close'''
        pass

    def run(self):
        '''
        called after sherlock main loop.
        method to keep output running after sherlock has finished
        '''
        pass
