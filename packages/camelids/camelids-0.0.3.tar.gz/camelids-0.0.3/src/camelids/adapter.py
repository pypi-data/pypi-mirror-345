# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""


def decode(human_said, response, recorder=None):
    answer = response['completion_message']['content']['text']
    # TODO: system_instruction
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


