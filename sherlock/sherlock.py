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
        check args and call initialization methods
        '''
        self.logfile_map = logfile_map
        self.shellcmd_map = shellcmd_map

        assert display_name in DISPLAYS, 'Unknown display %s' % display_name
        self.display_name = display_name

        if not filter_map:
            self.filter_map = {}
        else:
            self.filter_map = filter_map

        self.setup()

    def setup(self):
        self.build_filter()

        self.datasources = {}
        for parser, path in self.logfile_map.items():
            assert parser in PARSERS, 'Unknown parser: %s' % parser
            source = DATASOURCES['logfile'](
                PARSERS[parser](),
                self.filters,
                path=path
            )
            self.datasources[path] = source.run()

        for parser, command in self.shellcmd_map.items():
            assert parser in PARSERS, 'Unknown parser: %s' % parser
            source = DATASOURCES['shellcommand'](
                PARSERS[parser](),
                self.filters,
                command=command
            )
            self.datasources[command] = source.run()

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
            self.filters.append(f)

    def run(self):
        '''
        method called from executable
        '''
        self.buffer = {}
        import time
        import pprint
        while self.datasources:
            poplist = []
            for key, iterator in self.datasources.items():
                if key not in self.buffer or not self.buffer[key]:
                    try:
                        self.buffer[key] = iterator.send(None)
                        # print('Filled buffer %s' % key)
                    except StopIteration:
                        poplist.append(key)
                    except:
                        raise

            # pprint.pprint(self.buffer)
            for key in poplist:
                self.datasources.pop(key)

            mindate = None
            popkey = None
            for key, line_d in self.buffer.items():
                if not mindate:
                    mindate = line_d['datetime']
                    popkey = key
                    continue
                if line_d['datetime'] < mindate:
                    mindate = line_d['datetime']
                    popkey = key

            if popkey and popkey in self.buffer:
                popline = self.buffer.pop(popkey)
                print(popline['raw_line'].strip())

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
