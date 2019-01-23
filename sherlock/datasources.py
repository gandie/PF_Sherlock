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

    def run(self):
        '''
        read file bytes, decode and return
        '''

        assert 'path' in self.kwargs, 'Needs path argument!'
        path = self.kwargs['path']
        assert os.path.isfile(path), 'Path must be a valid file: %s' % path

        logfile = open(path, 'r', encoding='utf-8')
        while True:
            line = logfile.readline()
            if line:
                line_d = self.parser.run(line)
                if not line_d:
                    continue
                for lfilter in self.filters:
                    if not lfilter.run(line_d):
                        break
                else:  # nobreak - all filters returned True
                    yield line_d
            else:
                logfile.close()
                break


class Shellcommand(Datasource):

    '''
    Fetch data from shell command. Very dangerous.
    '''

    def run(self):
        '''
        - call shell command and return decoded result
        - ATTENTION! shell=True is activated to leverage shell tools like pipes
        '''
        assert 'command' in self.kwargs, 'Needs command argument!'
        cmd = self.kwargs['command']

        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True
        )
        while True:
            # returns None while subprocess is running
            retcode = proc.poll()
            line = proc.stdout.readline().decode('utf-8')
            if line:
                line_d = self.parser.run(line)
                if not line_d:
                    continue
                for lfilter in self.filters:
                    if not lfilter.run(line_d):
                        break
                else:
                    yield line_d
            if retcode is not None and not line:
                break
