# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""


def decode(human_said, response, recorder=None):
    answer = response['completion_message']['content']['text']
    if recorder:
        machine_answered = dict(role='assistant',
                                content=answer,
                                stop_reason = response['completion_message']['stop_reason'])
        events = [human_said, machine_answered]
        recorder.log_it(events)
        initial_text = human_said['content']
        records = [dict(Human=initial_text), dict(machine=answer)]
        recorder.record_it(records)
    return answer


def encode(records, recorder=None):
    log = []
    for record in records:
        keys = record.keys()
        key = next(iter(record.keys()))
        if key == 'Human':
            user_said = dict(role='user', content=record['Human'])
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
            machine_said = dict(role='assistant', content=utterance, stop_reason='stop')
            log.append(machine_said)
        elif key == 'Deus':
            deus_said = dict(role='system', content=record['Deus'])  # θεός
            log.append(deus_said)
        else:
            print('unknown record type')
    if recorder:
        recorder.log_it(log)
    return log
