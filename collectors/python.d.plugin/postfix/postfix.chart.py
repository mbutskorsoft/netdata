# -*- coding: utf-8 -*-
# Description: postfix netdata python.d module
# Author: Pawel Krupa (paulfantom)
# SPDX-License-Identifier: GPL-3.0-or-later
import copy
import re
from bases.FrameworkServices.LogService import LogService
from bases.FrameworkServices.ExecutableService import ExecutableService
from bases.loggers import PythonDLogger

DELAY_REGEX = 'delay=([-+]?[0-9]*\.?[0-9]+),'

POSTQUEUE_COMMAND = 'postqueue -p'

ORDER = [
    'qemails',
    'qsize',
    'qdelay',
]

CHARTS = {
    'qemails': {
        'options': [None, 'Postfix Queue Emails', 'emails', 'queue', 'postfix.qemails', 'line'],
        'lines': [
            ['emails', None, 'absolute']
        ]
    },
    'qsize': {
        'options': [None, 'Postfix Queue Emails Size', 'KiB', 'queue', 'postfix.qsize', 'area'],
        'lines': [
            ['size', None, 'absolute']
        ]
    },
    'qdelay': {
        'options': [None, 'Postfix Queue Emails Avg Delay', 'seconds', 'queue', 'postfix.qdelay', 'line'],
        'lines': [
            ['seconds', None, 'absolute']
        ]
    }
}


class Service(ExecutableService):
    def __init__(self, configuration=None, name=None):
        self.configuration_ = copy.deepcopy(configuration)
        ExecutableService.__init__(self, configuration=configuration, name=name)
        self.logs = PythonDLogger()
        self.log_service = LogService(configuration=self.configuration_, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.command = POSTQUEUE_COMMAND
        self.re = DELAY_REGEX

    def _get_data(self):
        """
        Format data received from shell command
        :return: dict
        """
        try:
            raw = self._get_raw_data(command=self.command)
            log_data_raw = self.log_service._get_raw_data()
            if not raw:
                return {
                    'emails': 0,
                    'size': 0,
                    'seconds': 0
                }
            raws = raw[-1].split(' ')
            lines = 0
            data = {'seconds': 0}
            try:
                self.re = re.compile(self.re)
            except Exception as err:
                self.logs.warning("1. check postfix logs: check failed {0}".format(err))
            for line in log_data_raw:
                match = self.re.search(line)
                if match:
                    lines += 1
                    delay = match.group(1)
                    data['seconds'] += float(delay)
            if lines > 0:
                data['seconds'] = data['seconds'] / lines
            if raws[0] == 'Mail' and raws[1] == 'queue':
                return {
                    'emails': 0,
                    'size': 0,
                    'seconds': 0
                }
            response = {
                'emails': raws[4] if raws else 0,
                'size': raws[1] if raws else 0,
                'seconds': data.get("seconds", 0)
            }
            return response
        except Exception as err:
            self.logs.warning("main exception postfix logs: check failed {0}".format(err))
            return None
