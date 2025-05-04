# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from os import environ
import requests


gemini_key              = environ.get('GOOGLE_API_KEY','') # GEMINI_KEY', '')
gemini_api_base         = environ.get('GEMINI_API_BASE','https://generativelanguage.googleapis.com/v1beta')
gemini_content_model    = environ.get('GEMINI_DEFAULT_CONTENT_MODEL', 'gemini-2.5-pro-exp-03-25')
gemini_embedding_model  = environ.get('GEMINI_DEFAULT_EMBEDDING_MODEL', 'text-embedding-004')

garbage = [
    {'category':'HARM_CATEGORY_HATE_SPEECH', 'threshold': 'BLOCK_NONE'},
    {'category':'HARM_CATEGORY_SEXUALLY_EXPLICIT', 'threshold': 'BLOCK_NONE'},
    {'category':'HARM_CATEGORY_DANGEROUS_CONTENT', 'threshold': 'BLOCK_NONE'},
    {'category':'HARM_CATEGORY_HARASSMENT', 'threshold': 'BLOCK_NONE'},
    {'category':'HARM_CATEGORY_CIVIC_INTEGRITY', 'threshold': 'BLOCK_NONE'}
]


def decode_one(human_said, response, recorder=None):
    if response['candidates'][0]['finishReason'] == 'SAFETY':
        raise Exception('Answer censored by Google.')
    answer = response['candidates'][0]['content']['parts'][0]['text']
    if recorder:
        machine_answered = dict(role='model', parts=[dict(text=answer)])
        events = [human_said, machine_answered]
        recorder.log_it(events)
        initial_text = human_said['parts'][0]['text']
        records = [dict(Human=initial_text), dict(machine=answer)]
        recorder.record_it(records)
    return answer


def decode_many(human_said, response, recorder=None):
    candidates = response['candidates']
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
        events = [human_said, machine_answer]
        recorder.log_it(events)
        initial_text = human_said['parts'][0]['text']
        records = [dict(Human=initial_text), dict(machine=answers)]
        recorder.record_it(records)
    return answers


def continuation(text=None, contents=None, instruction=None, recorder=None, **kwargs):
    """A continuation of text with a given context and instruction.
        kwargs:
            temperature     = 0 to 1.0
            top_p           = 0.0 to 1.0
            top_k           = The maximum number of tokens to consider when sampling.
            n               = 1 is mandatory for this method continuationS have n > 1
            max_tokens      = number of tokens
            stop            = ['stop']  array of up to 4 sequences
    """
    instruction         = kwargs.get('system_instruction', instruction)
    system_instruction  = dict(role='system', parts=[dict(text=instruction)]) if instruction else None

    contents            = kwargs.get('contents', contents)

    # if there is a recorded previous conversation
    if recorder and not contents:
        contents = recorder.log.copy()

    # Create a structure that the idiots want.
    human_says = dict(role='user', parts=[dict(text=text)])
    if text and not contents:
        contents = [human_says]
        # contents = [{'parts': [{'text': text}], 'role': 'user'}]
    else:
        contents.append(human_says)
        # {'parts': [{'text': text}], 'role': 'user'})

    json_data = {
        'systemInstruction':        system_instruction,
        'contents':                 contents,
        'safetySettings':           garbage,
        'generationConfig':{
            'stopSequences':        kwargs.get('stop_sequences', ['STOP','Title']),
            'responseMimeType':     kwargs.get('mime_type','text/plain'),
            # 'responseSchema': {},
            'responseModalities':   kwargs.get('modalities',['TEXT']),
            'temperature':          kwargs.get('temperature', 0.5),
            'maxOutputTokens':      kwargs.get('max_tokens', 10000),
            'candidateCount':       kwargs.get('n', 1),  # is in continuationS
            'topP':                 kwargs.get('top_p', 0.9),
            'topK':                 kwargs.get('top_k', 10),
            'enableEnhancedCivicAnswers':   False,
            'thinkingConfig':   {
                'thinkingBudget':   kwargs.get('thinking', 0) # 24576
            }
            #'cachedContent': '',
        },
    }
    try:
        response = requests.post(
            url=f'{gemini_api_base}/models/{kwargs.get("model", gemini_content_model)}:generateContent',
            params=f'key={gemini_key}',
            json=json_data,
        )
        if response.status_code == requests.codes.ok:
            output = response.json()
            if len(output['candidates']) == 1:
                answer = decode_one(human_says, output, recorder)
            elif len(output['candidates']) > 1:
                answer = decode_many(human_says, output, recorder)
            else:
                raise Exception('No candidates in response')
        else:
            print(f'Request status code: {response.status_code}')
            return None

    except Exception as e:
        print(f'Unable to generate continuation of the text, {e}')
        return None

    return answer


def embed(input_list, **kwargs):
    """Returns the embedding of a list of text strings.
    """
    embeddings_list = []
    json_data = {'texts': input_list} | kwargs
    try:
        response = requests.post(
            f'{gemini_api_base}/models/{kwargs.get("model", gemini_embedding_model)}:batchEmbedText',
            params=f'key={gemini_key}',
            json=json_data,
        )
        if response.status_code == requests.codes.ok:
            # embeddings_list = response.json()['embeddings']
            for count, candidate in enumerate(response.json()['embeddings']):
                item = {'index': count, 'embedding': candidate['value']}
                embeddings_list.append(item)
        else:
            print(f'Request status code: {response.status_code}')
        return embeddings_list
    except Exception as e:
        print('Unable to generate Embeddings response')
        print(f'Exception: {e}')
        return embeddings_list


if __name__ == '__main__':
    '''
    ['gemini-2.5-flash-preview-04-17', 'gemini-2.5-pro-exp-03-25', 'gemini-1.5-flash-latest',
    'gemini-2.0-flash-lite','gemini-2.0-flash','gemini-2.0-pro-exp-02-05',
    'gemini-2.0-flash-thinking-exp-01-21']
    '''
    import yaml
    from yaml import safe_load as yl
    from yaml import safe_dump as yd

    long_text = 'Once upon a time, when pigs drank wine, and monkeys chewed tobacco, and hens took snuff – and didn"t the ducks quack grandly in French! – there lived a little old woman and a little old man in a cozy little cottage with a thatch of rushes and a garden full of cabbages. Now, this little old woman and little old man, they weren`t rich, not by half. They had just enough to keep body and soul together, a cow called Crumplehorn, three brown hens, and a pig. '

    previous_turns = f"""
      - role: human          # not the idiotic 'user', God forbid.
        parts: 
          - text: Once upon a time, when pigs drank wine 

      - role: machine        # not the idiotic 'model'
        parts:
          - text: {long_text}
    """
    # that = yl(previous_turns)

    kwargs = """  # this is a string in YAML format
      model:        gemini-2.5-pro-exp-03-25
      mime_type:    text/plain
      modalities:
        - TEXT
      max_tokens:   12768
      n: 3
      stop_sequences:
        - STOP
        - "\nTitle"
      temperature:  0.5
      top_k:        10
      top_p:        0.5
      thinking:     0  # thinking tokens budget. 24576
    """
    this = yl(kwargs)

    instruction = 'You are a eloquent assistant.'

    text_to_continue = 'What is the capital of Indonesia?'

    # yaml_file = '/home/alxfed/Documents/Fairytales/sow-anne.yaml'
    # with open(yaml_file, 'r') as stream:
    #     try:
    #         that = yl(stream)
    #     except yaml.YAMLError as exc:
    #         print(exc)

    machine_responses = continuation(
        text=text_to_continue,
        instruction=instruction,
        # contents=that,
        **yl(kwargs)
    )
    #
    # file_name = '/home/alxfed/2025/next_yaml_test.yaml'
    # with open(file_name, "w") as stream:
    #     try:
    #         yd(machine_responses, stream)
    #     except yaml.YAMLError as exc:
    #         print(exc)
    # # texts = yd(machine_responses)
    # with open(file_name, 'r') as stream:
    #     try:
    #         texts = yl(stream)
    #     except yaml.YAMLError as exc:
    #         print(exc)
...
