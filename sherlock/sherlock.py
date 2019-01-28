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
import sherlock.outputs as outputs


# builtin
import os
import importlib.util
import sys

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
    'measure': parsers.Measure_Parser,
    'auth': parsers.Auth_Parser,
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

OUTPUTS_HELP = '''
CURRENTLY DISABLED!
OUTPUTS
:: display-name: DisplayClass
display-name is references via display string in config.py, it is used to build
display instance after result sorting

'''
OUTPUTS = {
    'simple': outputs.SimplePager,
    'stdout': outputs.StdOut,
    'table': outputs.Tablepager,
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
    res += OUTPUTS_HELP
    res += u'\n'.join('%s %s' % (key, value) for key, value in OUTPUTS.items())
    res += FILTERS_HELP
    res += u'\n'.join('%s %s' % (key, value) for key, value in FILTERS.items())
    return res


class Sherlock(object):

    '''
    Main class of pf_sherlock.
    Builds datasource instances and sort their output by datetime
    '''

    def __init__(self, logfile_map, shellcmd_map, output_name, filter_map=None):
        '''
        check args and call initialization methods
        '''
        self.logfile_map = logfile_map
        self.shellcmd_map = shellcmd_map

        assert output_name in OUTPUTS, 'Unknown output %s' % output_name
        self.output_name = output_name
        self.output = OUTPUTS[output_name]()

        if not filter_map:
            self.filter_map = {}
        else:
            self.filter_map = filter_map

        self.setup()

    def setup(self):
        '''
        Called after populating sherlock instance
        '''

        self.build_filter()

        self.datasources = {}
        for parser, path in self.logfile_map:
            assert parser in PARSERS, 'Unknown parser: %s' % parser
            source = DATASOURCES['logfile'](
                PARSERS[parser](),
                self.filters,
                path=path
            )
            self.datasources[path] = source.run()

        for parser, command in self.shellcmd_map:
            assert parser in PARSERS, 'Unknown parser: %s' % parser
            source = DATASOURCES['shellcommand'](
                PARSERS[parser](),
                self.filters,
                command=command
            )
            self.datasources[command] = source.run()

    def build_filter(self):
        '''
        called during setup method
        build filters defined in filter_map
        '''
        self.filters = []
        for fkey, argument in self.filter_map.items():
            assert fkey in FILTERS, 'Unknown filter %s' % fkey
            f_class = FILTERS[fkey]
            f_instance = f_class(**{
                f_class.argument: argument
            })
            f_instance.setup()
            self.filters.append(f_instance)

    def run(self):
        '''
        method called from executable. runs main loop on datasources.
        - initialize buffer dict
        - run mainloop (as long as data available)
          - fill buffer
          - remove empty datasources
          - find and pop line having the lowest datetime entry from buffer
        '''

        self.buffer = {}
        self.output.setup()

        while self.datasources:

            # poplist is used to pop empty datasources
            poplist = []

            # fetch buffer items from datasources, memorize empty ones
            for key, iterator in self.datasources.items():
                if key not in self.buffer or not self.buffer[key]:
                    try:
                        self.buffer[key] = iterator.send(None)
                    except StopIteration:
                        poplist.append(key)
                    except Exception:
                        raise

            # remove empty datasources
            for key in poplist:
                self.datasources.pop(key)

            # find and memorize buffer key to pop by finding earliest datetime
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

            # throw popkey line from buffer, remove popkey from buffer
            if popkey and popkey in self.buffer:
                popline = self.buffer.pop(popkey)
                self.output.write(popline)

        # close output stream and call optional run method
        self.output.close()
        self.output.run()

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

        if args.output:
            output_name = args.output
        else:
            output_name = config.output

        return Sherlock(
            logfile_map=config.logfile_map,
            shellcmd_map=config.shellcmd_map,
            output_name=output_name,
            filter_map=filter_map
        )
