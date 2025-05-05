# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""


def decode(human_says, output, recorder=None):
    if len(output['candidates']) == 1:
        if output['candidates'][0]['finishReason'] == 'SAFETY':
            raise Exception('Answer censored by Google.')
        answer = output['candidates'][0]['content']['parts'][0]['text']
        if recorder:
            machine_answered = dict(role='model', parts=[dict(text=answer)])
            events = [human_says, machine_answered]
            recorder.log_it(events)
            initial_text = human_says['parts'][0]['text']
            records = [dict(Human=initial_text), dict(machine=answer)]
            recorder.record_it(records)
        return answer
    elif len(output['candidates']) > 1:
        candidates = output['candidates']
        answers = []
        for candidate in candidates:
            if candidate['finishReason'] == 'SAFETY':
                text = 'Answer censored by Google.'
            else:
                text = candidate['content']['parts'][0]['text']
            answers.append(text)
        if recorder:
            # only the first answer is logged (because of continuations)
            # make your own logger if you will be choosing after every turn;
            # I edit records manually and overwrite log with the help of Scribe
            # see the Grammateus package.
            machine_answer = dict(role='model', parts=[dict(text=answers[0])])
            events = [human_says, machine_answer]
            recorder.log_it(events)
            initial_text = human_says['parts'][0]['text']
            records = [dict(Human=initial_text), dict(machine=answers)]
            recorder.record_it(records)
        return answers
    else:
        raise Exception('No candidates in response')


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
        elif key == 'instruction':
            instruction = dict(role='system', parts=[dict(text=record['instruction'])])
            log.append(instruction)
        else:
            print('unknown record type')
    return log
