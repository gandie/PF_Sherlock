#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# pager -- simple display implementation using standard pager
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

from sherlock.display import Display
import pydoc


class SimplePager(Display):

    '''
    Only display raw lines in standard pager fetched via pydoc, most likely
    "less"
    '''

    def setup(self):
        self.display_text = '\n'.join([
            item['raw_line'] for item in self.parser_results
        ])

    def run(self):
        pydoc.pager(self.display_text)


class Tablepager(Display):

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
            fields = [str(d.get(c, "")).ljust(cell_widths[c]) for c in columns]
            row = row_template.format(*fields)
            rows.append(row)

        return "\n".join([header, sep] + rows)

    def setup(self):
        self.display_text = self.make_table(['datetime', 'code',  'type', 'raw_line'], self.parser_results)

    def run(self):
        pydoc.pager(self.display_text)
