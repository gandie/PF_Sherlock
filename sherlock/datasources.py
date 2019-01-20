#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# datasources -- collection of datasource implementations
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

from sherlock.datasource import Datasource
import os
import subprocess


class Logfile(Datasource):

    '''
    Simple Logfile datasource
    '''

    def setup(self):
        '''
        - check path argument
        '''
        assert 'path' in self.kwargs, 'Needs path argument!'

        path = self.kwargs['path']
        assert os.path.isfile(path), 'Path must be a valid file: %s' % path

        self.path = path

    def run(self):
        '''
        read file bytes, decode and return
        '''
        with open(self.path, 'rb') as myfile:
            text = myfile.read().decode('utf-8')
        return text


class Shellcommand(Datasource):

    '''
    Fetch data from shell command. Very dangerous.
    '''

    def setup(self):
        '''
        - check command argument
        '''
        assert 'command' in self.kwargs, 'Needs command argument!'

        cmd = self.kwargs['command']
        self.command = cmd

    def run(self):
        '''
        - call shell command and return decoded result
        - ATTENTION! shell=True is activated to leverage shell tools like pipes
        '''
        return subprocess.check_output(self.command, shell=True).decode('utf-8')
