#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Josh Maine'
__copyright__ = '''Copyright (C) 2013-2014 Josh "blacktop" Maine
                   This file is part of Malice - https://github.com/blacktop/malice
                   See the file 'docs/LICENSE' for copying permission.'''

import tempfile
from os import unlink
from os.path import exists, isfile

from dateutil import parser

import envoy
from lib.common.abstracts import AntiVirus, L32_PLATFORM


# ignore_tags = ['Directory', 'File Name', 'File Permissions', 'File Modification Date/Time']

class AVG(AntiVirus):

    _name = 'AVG'
    _platform = L32_PLATFORM
    _engine_path = '/usr/bin/avgscan'
    _update_path = '/usr/bin/avgupdate'

    authors = ['blacktop']
    references = ['http://free.avg.com']

    def __init__(self, data):
        AntiVirus.__init__(self, data)
        self.data = data

    @property
    def is_installed(self):
        return isfile(self._engine_path) and isfile(self._update_path)

    @property
    def engine_path(self):
        return self._engine_path

    @property
    def update_path(self):
        return self._update_path

    @property
    def version(self):
        #: Get AVG version
        r = envoy.run(self._engine_path + ' --version', timeout=15)
        results = filter(None, r.std_out.splitlines())
        for result in results:
            if 'version' in result:
                return result.split(':')[1].strip()
        return 'Error: version failed to execute.'

    # @staticmethod
    def update_available(self):
        """ Check if an update is available.

        :return: bool - Update availabe or not.
        """
        r = envoy.run('sudo ' + self._update_path + ' -c', timeout=15)
        results = filter(None, r.std_out.splitlines())
        for result in results:
            if 'You are currently up-to-date' in result:
                return False
        return True

    # @staticmethod
    def update_definitions(self):
        """Update AVG signatures"""
        if self.update_available():
            r = envoy.run('sudo ' + self._update_path, timeout=15)
            #: return key, stdout as a dictionary
            results = filter(None, r.std_out.splitlines())
            for result in results:
                if 'Update was successfully completed.' in result:
                    return 'Update was successfully completed.'
            return 'Error: update failed to execute.'
        else:
            return 'You are currently up-to-date'

    def format_output(self, output):
        avg_tag = {}
        avg_results = output.split('\n')
        avg_results = filter(None, avg_results)
        avg_tag['av'] = 'AVG'
        avg_tag['infected'] = '1' in avg_results[11].strip().decode('utf-8')
        avg_tag['infected_string'] = avg_results[6].split()[-1].strip().decode('utf-8')
        tag_part = avg_results[2].split(':', 1)
        engine = tag_part[1].strip().decode('utf-8')
        tag_part = avg_results[3].split(':', 1)
        definitions = parser.parse(tag_part[1].strip().decode('utf-8'))
        # avg_tag['metadata'] = dict(engine=engine, definitions=definitions)
        avg_tag['metadata'] = dict(engine=engine, definitions='Problem')
        # for tag in avg_results:
        #     if 'Virus' in tag:
        #         tag_part = tag.split('Virus')
        #         if len(tag_part) == 2:
        #             avg_tag['infected_string'] = tag_part[1]
        #     tag_part = tag.split(':', 1)
        #     if len(tag_part) == 2:
        #         if 'Infections found' in tag_part[0].strip():
        #             avg_tag['infected'] = '1' in tag_part[1].strip().decode('utf-8')
        #         elif 'database version' in tag_part[0].strip():
        #             avg_tag['engine'] = tag_part[1].strip().decode('utf-8')
        #         elif 'database date' in tag_part[0].strip():
        #             avg_tag['definitions'] = tag_part[1].strip().decode('utf-8')
        #         else:
        #             avg_tag[tag_part[0].strip()] = tag_part[1].strip().decode('utf-8')
        return avg_tag

    def do_scan(self, file_object):
        if self.is_installed:
            #: create tmp file
            handle, name = tempfile.mkstemp(suffix=".data", prefix="avg_")
            #: Write data stream to tmp file
            with open(name, "wb") as f:
                f.write(self.data)
            #: Run AVG on tmp file
            r = envoy.run('/usr/bin/avgscan ' + name, timeout=15)
            #: delete tmp file
            unlink(name)
            exists(name)
            #: return key, stdout as a dictionary
            return 'AVG', self.format_output(r.std_out)
        else:
            return 'AVG', dict(error='AVG Engine is not installed.')

# myAVG = AVG(None)
# print myAVG.is_installed
# print myAVG.version
# print myAVG.update_definitions()
# print
