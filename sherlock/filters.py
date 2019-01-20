#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# filters -- collection of basic filter implementations
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

from sherlock.filter import Filter
import datetime


class Lasthours(Filter):

    '''
    Filter parser_results for records from last X hours given as "lasth"
    keyword argument
    '''

    argument = 'lasth'

    def setup(self):
        '''
        check arguments and prepare filtering
        '''
        assert 'lasth' in self.kwargs, 'lasth argument needed!'
        self.lasth = int(self.kwargs['lasth'])
        self.hours_ago = datetime.datetime.now() - datetime.timedelta(hours=self.lasth)

    def run(self, results):
        '''
        run filter against parser_results
        '''
        return [
            item for item in results
            if item['datetime'] > self.hours_ago
        ]


class Keyword(Filter):

    '''
    Filter parser_results for records having "keyword" argument in raw_line
    '''

    argument = 'keyword'

    def setup(self):
        '''
        check arguments and prepare filtering
        '''
        assert 'keyword' in self.kwargs, 'keyword argument needed!'
        self.keyword = str(self.kwargs['keyword'])

    def run(self, results):
        '''
        run filter against parser_results
        '''
        return [
            item for item in results
            if self.keyword in item['raw_line']
        ]
