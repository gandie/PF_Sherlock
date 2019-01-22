#!/usr/bin/env python
# Copyright (c) 2019 Lars Bergmann
#
# sherlock -- main class calling parser modules
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

# custom
import sherlock.parsers as parsers
import sherlock.datasources as datasources
import sherlock.filters as filters
import sherlock.pager as pager


# builtin
import os
import importlib.util

# module maps
PARSERS_HELP = '''
PARSERS

:: parser-name: ParserClass
parser-name is referenced from config.py, ParserClass instances are built during
sherlock startup.

'''
PARSERS = {
    'postgresql': parsers.Psql_Parser,
    'apache2-error': parsers.Apache2_Error_Parser,
    'apache2-access': parsers.Apache2_Access_Parser,
    'journal': parsers.Journal_Parser,
}

DATASOURCES_HELP = '''
DATASOURCES

:: datasource-name: DatasourceClass
datasource-name is indirectly referenced via logfile_map and shellcmd_map
in config.py, DatasourceClass instances are built during parser building

'''
DATASOURCES = {
    'logfile': datasources.Logfile,
    'shellcommand': datasources.Shellcommand,
}

DISPLAYS_HELP = '''

DISPLAYS
:: display-name: DisplayClass
display-name is references via display string in config.py, it is used to build
display instance after result sorting

'''
DISPLAYS = {
    'simple': pager.SimplePager,
    'table': pager.Tablepager
}

FILTERS_HELP = '''

FILTERS
:: filter-shortcut: FilterClass
filter-shortcut and arguments may be used in config.py "filter_map" or as
arguments on pf_sherlock call. Filters are applied sequential on parser results.

'''
FILTERS = {
    'lh': filters.Lasthours,
    'kw': filters.Keyword,
}


def show_help():
    '''
    show module variables and help texts
    '''
    res = ''''''
    res += PARSERS_HELP
    res += u'\n'.join('%s %s' % (key, value) for key, value in PARSERS.items())
    res += DATASOURCES_HELP
    res += u'\n'.join('%s %s' % (key, value) for key, value in DATASOURCES.items())
    res += DISPLAYS_HELP
    res += u'\n'.join('%s %s' % (key, value) for key, value in DISPLAYS.items())
    res += FILTERS_HELP
    res += u'\n'.join('%s %s' % (key, value) for key, value in FILTERS.items())
    return res


class Sherlock(object):

    '''
    Main class of pf_sherlock. Builds parser instances from modules available
    and runs them against corresponding logfiles. Then apply filters to parser
    resuslts and present them in display.
    '''

    def __init__(self, logfile_map, shellcmd_map, display_name, filter_map=None):
        '''
        check and apply configpath
        call initialization methods
        '''
        self.logfile_map = logfile_map
        self.shellcmd_map = shellcmd_map

        assert display_name in DISPLAYS, 'Unknown display %s' % display_name
        self.display_name = display_name

        if not filter_map:
            self.filter_map = {}
        else:
            self.filter_map = filter_map

        self.build_parser()

    def build_parser(self):
        '''
        called when instance is populated
        build parser defined logfile_map and shellcmd_map
        '''
        self.parsers = []
        for parser, path in self.logfile_map.items():
            assert parser in PARSERS, 'Unknown parser: %s' % parser
            p = PARSERS[parser](DATASOURCES['logfile'], path=path)
            p.setup()
            parser_d = {
                'type': 'logfile',
                'path': path,
                'instance': p,
            }
            self.parsers.append(parser_d)

        for parser, command in self.shellcmd_map.items():
            assert parser in PARSERS, 'Unknown parser: %s' % parser
            p = PARSERS[parser](DATASOURCES['shellcommand'], command=command)
            p.setup()
            parser_d = {
                'type': 'shellcommand',
                'command': command,
                'instance': p,
            }
            self.parsers.append(parser_d)

    def build_filter(self):
        '''
        called when results from parsers are available
        build filters defined filter_map
        '''
        self.filters = []
        for fkey, argument in self.filter_map.items():
            assert fkey in FILTERS, 'Unknown filter %s' % fkey
            f_class = FILTERS[fkey]
            kwargs = {
                f_class.argument: argument
            }
            f = f_class(**kwargs)
            f.setup()
            filter_d = {
                'type': fkey,
                'arg': argument,
                'instance': f
            }
            self.filters.append(filter_d)

    def build_display(self):
        '''
        prepare display to show results
        '''
        self.display = DISPLAYS[self.display_name](self.results)
        self.display.setup()

    def run(self):
        '''
        method called from executable
        - call all parsers previously built
        - add meta data and safe result
        - prepare and apply filters
        - sort results by datetime
        - call display building and run it showing results
        '''

        self.results = []
        for parser_d in self.parsers:
            p = parser_d['instance']
            result = p.run()
            result_meta = {
                key: value for key, value in parser_d.items()
                if key != 'instance'
            }
            for item in result:
                item.update(result_meta)

            self.results.extend(result)

        self.build_filter()
        for filter_d in self.filters:
            self.results = filter_d['instance'].run(self.results)

        self.results.sort(key=lambda x: x['datetime'])

        self.build_display()

        self.display.run()

    @staticmethod
    def load_config(configpath):
        '''
        called for instance building
        load config from path as python module
        '''

        spec = importlib.util.spec_from_file_location(
            'config', configpath
        )
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        return config

    @staticmethod
    def from_args(args):
        '''
        build and return Sherlock instance from argparse args object
        - check and load config
        - check config for filter_map, merge with filter map from args
        '''

        assert os.path.isfile(args.config), 'Invalid configpath: %s' % args.config
        config = Sherlock.load_config(args.config)

        if hasattr(config, 'filter_map') and isinstance(config.filter_map, dict):
            filter_map = config.filter_map
        else:
            filter_map = {}

        if (args.filter and args.args):
            assert len(args.filter) == len(args.args), 'Each filter needs argument!'
            args_filter_map = {
                name: arg for name, arg in zip(args.filter, args.args)
            }
            filter_map.update(args_filter_map)

        return Sherlock(
            logfile_map=config.logfile_map,
            shellcmd_map=config.shellcmd_map,
            display_name=config.display,
            filter_map=filter_map
        )
