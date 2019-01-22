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


class Psql_Parser(Parser):
    '''
    Parser for psql logfiles
    '''

    def run(self):
        res = []
        for line in self.raw_data.split(u'\n'):
            tokens = line.split()
            if not tokens or not tokens[0] or len(tokens[0]) == 0:
                continue
            if not tokens[0][0].isdigit():
                continue
            datestring = ' '.join(tokens[:2])
            dateobj = dateutil.parser.parse(datestring, ignoretz=True)
            assert dateobj, 'Unable to build date from %s' % datestring
            line_d = {
                'code': tokens[5],
                'datetime': dateobj,
                'raw_line': line
            }
            res.append(line_d)
        return res


class Apache2_Error_Parser(Parser):
    '''
    Parser for apache2 error logfiles
    '''

    def run(self):
        res = []
        for line in self.raw_data.split(u'\n'):
            tokens = line.split()
            if not tokens or not tokens[0] or len(tokens[0]) == 0 or not tokens[0].startswith(u'['):
                continue
            datestring = ' '.join(tokens[:5])[1:-1]
            dateobj = dateutil.parser.parse(datestring, ignoretz=True)
            assert dateobj, 'Unable to build date from %s' % datestring
            line_d = {
                'code': tokens[5][1:-1],
                'datetime': dateobj,
                'raw_line': line
            }
            res.append(line_d)
        return res


class Apache2_Access_Parser(Parser):
    '''
    Parser for apache2 access logfiles
    '''

    def run(self):
        res = []
        for line in self.raw_data.split(u'\n'):
            tokens = line.split()
            if not tokens or not tokens[0] or len(tokens[0]) == 0:
                continue
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

            assert dateobj, 'Unable to build date from %s' % datestring
            line_d = {
                'code': tokens[8],
                'datetime': dateobj,
                'raw_line': line
            }
            res.append(line_d)
        return res


class Journal_Parser(Parser):
    '''
    Parser for journal log
    '''

    def run(self):
        res = []
        for line in self.raw_data.split(u'\n'):
            tokens = line.split()
            if not tokens or not tokens[0] or len(tokens[0]) == 0 or tokens[0] == '--':
                continue
            datestring = tokens[0]
            datestring = datestring.replace(u',', u'.')
            dateobj = dateutil.parser.parse(datestring, ignoretz=True)
            assert dateobj, 'Unable to build date from %s' % datestring
            line_d = {
                'code': tokens[1] if tokens[1].endswith(u':') else tokens[2][:-1],
                'datetime': dateobj,
                'raw_line': line
            }

            '''
            line_d = {
                'code': tokens[2],
                'datetime': datetime.datetime.strptime(
                    tokens[0][:19],
                    '%Y-%m-%dT%X'
                ),
                'raw_line': line
            }
            '''
            res.append(line_d)
        return res
