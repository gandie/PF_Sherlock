#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# outputs -- collection of output implementations
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

from sherlock.output import Output
import subprocess
import sys
import pydoc


class SimplePager(Output):

    '''
    Only display raw lines in "less" pager
    '''

    def setup(self):
        '''call less with stdin pipe set'''
        self.proc = subprocess.Popen('less', stdin=subprocess.PIPE)
        self.alive = True

    def write(self, line_d):
        '''take raw_line from line_d, write to and flush proc.stdin'''
        try:
            self.proc.stdin.write(line_d['raw_line'].encode(encoding='utf_8'))
            self.proc.stdin.flush()
        except BrokenPipeError:
            print('Pager closed.')
            sys.exit(0)
        except:
            raise

    def close(self):
        '''close pipe so less knows there is no more incoming data'''
        if self.alive:
            self.proc.stdin.close()

    def run(self):
        '''wait until user quits "less" '''
        while self.alive:
            retcode = self.proc.poll()
            if retcode is not None:
                self.alive = False


class StdOut(Output):

    '''
    well, this is stdout. not much to see here.
    '''

    def write(self, line_d):
        '''take raw_line from line_d, write to and flush proc.stdin'''
        sys.stdout.write(line_d['raw_line'])


class Tablepager(Output):

    '''
    Display full result in table
    '''

    def make_table(self, columns, data):
        '''
        stolen from:
        https://stackoverflow.com/questions/5909873/how-can-i-pretty-print-ascii-tables-with-python

        need a version NOT having any dependencies
        '''
        """Create an ASCII table and return it as a string.

        Pass a list of strings to use as columns in the table and a list of
        dicts. The strings in 'columns' will be used as the keys to the dicts in
        'data.'

        Not all column values have to be present in each data dict.

        >>> print(make_table(["a", "b"], [{"a": "1", "b": "test"}]))
        | a | b    |
        |----------|
        | 1 | test |
        """
        # Calculate how wide each cell needs to be
        cell_widths = {}
        for c in columns:
            values = [str(d.get(c, "")) for d in data]
            cell_widths[c] = len(max(values + [c]))

        # Used for formatting rows of data
        row_template = "|" + " {} |" * len(columns)

        # CONSTRUCT THE TABLE

        # The top row with the column titles
        justified_column_heads = [c.ljust(cell_widths[c]) for c in columns]
        header = row_template.format(*justified_column_heads)
        # The second row contains separators
        sep = "|" + "-" * (len(header) - 2) + "|"
        # Rows of data
        rows = []
        for d in data:
            fields = [str(d.get(c, "")).strip().ljust(cell_widths[c]) for c in columns]
            row = row_template.format(*fields)
            rows.append(row)

        return "\n".join([header, sep] + rows)

    def setup(self):
        self.parser_results = []

    def write(self, line_d):
        '''memorize hole line'''
        self.parser_results.append(line_d)

    def close(self):
        '''build display_text using make_table'''
        self.display_text = self.make_table(
            ['datetime', 'code', 'raw_line'],
            self.parser_results
        )

    def run(self):
        '''we may use the pydoc.pager shorthand here'''
        pydoc.pager(self.display_text)
