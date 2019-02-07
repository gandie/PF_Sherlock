#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# parsers -- collection of basic parsers from different datasources
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

from sherlock.parser import Parser
import datetime
import dateutil.parser


class Auth_Parser(Parser):
    '''
    Parser for auth logfiles
    '''

    def run(self, line):
        tokens = line.split()
        if not tokens or not tokens[0] or len(tokens[0]) == 0:
            return
        if len(tokens) == 1 or not tokens[1][0].isdigit():
            return
        datestring = ' '.join(tokens[:3])
        dateobj = dateutil.parser.parse(datestring, ignoretz=True)
        assert dateobj, 'Unable to build date from %s' % datestring
        line_d = {
            'code': tokens[4],
            'datetime': dateobj,
            'raw_line': line
        }
        return line_d


class Measure_Parser(Parser):
    '''
    Parser for measure logfiles
    '''
    def run(self, line):
        tokens = line.split()
        if not tokens or not tokens[0] or len(tokens[0]) == 0:
            return
        if not tokens[0][0].isdigit() or len(tokens) == 1:
            return
        datestring = tokens[0]
        dateobj = dateutil.parser.parse(datestring, ignoretz=True)
        assert dateobj, 'Unable to build date from %s' % datestring
        line_d = {
            'code': tokens[1],
            'datetime': dateobj,
            'raw_line': line
        }
        return line_d


class Psql_Parser(Parser):
    '''
    Parser for psql logfiles
    '''

    def run(self, line):
        tokens = line.split()
        if not tokens or not tokens[0] or len(tokens[0]) == 0:
            return
        if not tokens[0][0].isdigit() or len(tokens) == 1 or not tokens[1][0].isdigit():
            return
        datestring = ' '.join(tokens[:2])
        dateobj = dateutil.parser.parse(datestring, ignoretz=True)
        assert dateobj, 'Unable to build date from %s' % datestring
        line_d = {
            'code': tokens[3],
            'datetime': dateobj,
            'raw_line': line
        }
        return line_d


class Apache2_Error_Parser(Parser):
    '''
    Parser for apache2 error logfiles
    '''

    def run(self, line):
        tokens = line.split()
        if not tokens or not tokens[0] or len(tokens[0]) == 0 or not tokens[0].startswith(u'['):
            return
        datestring = ' '.join(tokens[:5])[1:-1]
        dateobj = dateutil.parser.parse(datestring, ignoretz=True)
        assert dateobj, 'Unable to build date from %s' % datestring
        line_d = {
            'code': tokens[5][1:-1],
            'datetime': dateobj,
            'raw_line': line
        }
        return line_d


class Apache2_Access_Parser(Parser):
    '''
    Parser for apache2 access logfiles
    '''

    def run(self, line):
        tokens = line.split()
        if not tokens or not tokens[0] or len(tokens[0]) == 0:
            return
        datestring = tokens[3][1:]
        try:
            dateobj = dateutil.parser.parse(datestring, ignoretz=True)
        except ValueError:
            dateobj = datetime.datetime.strptime(
                datestring,
                '%d/%b/%Y:%X'
            )
        except Exception:
            raise

        import string
        assert dateobj, 'Unable to build date from %s' % datestring
        line_d = {
            'code': tokens[8],
            'datetime': dateobj,
            'raw_line': ''.join(char for char in line if char in string.printable)
        }
        return line_d


class Journal_Parser(Parser):
    '''
    Parser for journal log
    '''

    def run(self, line):
        tokens = line.split()
        if not tokens or not tokens[0] or len(tokens[0]) == 0 or tokens[0] == '--':
            return
        datestring = tokens[0]
        datestring = datestring.replace(u',', u'.')
        if not datestring[0].isdigit():
            return
        dateobj = dateutil.parser.parse(datestring, ignoretz=True)
        assert dateobj, 'Unable to build date from %s' % datestring
        line_d = {
            'code': tokens[1] if tokens[1].endswith(u':') else tokens[2][:-1],
            'datetime': dateobj,
            'raw_line': line
        }

        return line_d
