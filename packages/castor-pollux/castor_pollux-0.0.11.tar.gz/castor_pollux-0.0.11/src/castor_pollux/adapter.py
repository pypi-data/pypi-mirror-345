# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""


def encoder(records):
    log = []
    for record in records:
        keys = record.keys()
        key = next(iter(record.keys()))
        if key == 'Human':
            user_said = dict(role='user', parts=[dict(text=record['Human'])])
            log.append(user_said)
        elif key == 'machine':
            text = record['machine']
            if isinstance(text, str):
                utterance = text
            elif isinstance(text, list):
                utterance = text[0]
            else:
                utterance = ''
                print('unknown record type')
            machine_said = dict(role='model', parts=[dict(text=utterance)])
            log.append(machine_said)
        else:
            print('unknown record type')
    return log