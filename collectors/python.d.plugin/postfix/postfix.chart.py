# -*- coding: utf-8 -*-
# Description: postfix netdata python.d module
# Author: Pawel Krupa (paulfantom)
# SPDX-License-Identifier: GPL-3.0-or-later

from bases.FrameworkServices.ExecutableService import ExecutableService

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
        'options': [None, 'Postfix Queue Emails Avg Delay', 'seconds', 'queue', 'postfix.qsize', 'area'],
        'lines': [
            ['seconds', None, 'increment']
        ]
    }
}


class Service(ExecutableService):
    def __init__(self, configuration=None, name=None):
        ExecutableService.__init__(self, configuration=configuration, name=name)
        self.order = ORDER
        self.definitions = CHARTS
        self.command = POSTQUEUE_COMMAND

    def _get_data(self):
        """
        Format data received from shell command
        :return: dict
        """
        try:
            return {
                    'emails': 10,
                    'size': 10,
                    'seconds': 10
                }
            raw = self._get_raw_data()
            if not raw:
                return {
                    'emails': 0,
                    'size': 0,
                    'seconds': 0
                }
            raws = raw[-1].split(' ')
            lines = 0
            data = {'seconds': 0}
            for line in raw:
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

            return {
                'emails': raws[4] if raws else 0,
                'size': raws[1] if raws else 0,
                'seconds': data.get("seconds", 0)
            }
        except (ValueError, AttributeError):
            return None
