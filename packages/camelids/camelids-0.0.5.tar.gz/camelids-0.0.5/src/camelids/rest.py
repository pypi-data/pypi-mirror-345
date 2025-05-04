# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from os import environ
import requests
from .adapter import decode


meta_key              = environ.get('META_API_KEY','') # meta_KEY', '')
meta_api_base         = environ.get('META_API_BASE','https://api.llama.com/v1')
meta_content_model    = environ.get('META_DEFAULT_CONTENT_MODEL', 'Llama-4-Maverick-17B-128E-Instruct-FP8')
meta_embedding_model  = environ.get('META_DEFAULT_EMBEDDING_MODEL', '')


# def decode_one(human_said, response, recorder=None):
#     answer = response['completion_message']['content']['text']
#     # TODO: system_instruction
#     if recorder:
#         machine_answered = dict(role='assistant',
#                                 content=answer,
#                                 stop_reason = response['completion_message']['stop_reason'])
#         events = [human_said, machine_answered]
#         recorder.log_it(events)
#         initial_text = human_said['content']
#         records = [dict(Human=initial_text), dict(machine=answer)]
#         recorder.record_it(records)
#     return answer
#
#
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
    first_message       = [dict(role='system', content=instruction)] if instruction else []

    # contents can come in kwards or as an argument
    contents            = kwargs.get('contents', contents)

    # if there is a recorded log of the previous conversation
    if recorder and not contents:
        contents = recorder.log.copy()

    # now add the incoming human text
    human_says = dict(role='user', content=text)
    if text and not contents:
        contents = [human_says]
    else:
        contents.append(human_says)

    # add contents and user text to the first (instruction) message
    first_message.extend(contents)
    instruction_and_contents = first_message

    json_data = {
        'model':                    kwargs.get('model', meta_content_model),
        'messages':                 instruction_and_contents,
        'response_format':          kwargs.get('response_format',{'type': 'text'}),
        'temperature':              kwargs.get('temperature', 0.5),  # 0.0 to 1.0
        'max_completion_tokens':    kwargs.get('max_tokens', 4028),
        'top_p':                    kwargs.get('top_p', 0.9),
        'top_k':                    kwargs.get('top_k', 10),
        'stream':                   False
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer " + meta_key
    }
    try:
        response = requests.post(
            url=f'{meta_api_base}/chat/completions',
            headers=headers,
            json=json_data,
        )
        if response.status_code == requests.codes.ok:
            output = response.json()
            answer = decode(human_says, output, recorder)
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
            f'{meta_api_base}/models/{kwargs.get("model", meta_embedding_model)}:batchEmbedText',
            params=f'key={meta_key}',
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
    ['Llama-4-Scout-17B-16E-Instruct-FP8', 'Llama-4-Maverick-17B-128E-Instruct-FP8', 'Llama-3.3-70B-Instruct', 'Llama-3.3-8B-Instruct']
    '''
    # from grammateus import Grammateus

    location = '/home/alxfed/Documents/Fairytales/two/'

    # recorder = Grammateus(location)

    from yaml import safe_load as yl

    kwargs = """  # this is a string in YAML format
      model:        Llama-4-Maverick-17B-128E-Instruct-FP8
      mime_type:    text/plain
      response_format: 
        type: text
      max_tokens:   4028
      temperature:  0.5
      top_k:        10
      top_p:        0.5
    """
    this = yl(kwargs)

    instruction = 'I am Joseph Jacobs, I retell folk tales.'

    text_to_continue = 'And what happened next?'

    machine_responses = continuation(
        text=text_to_continue,
        instruction=instruction,
        # contents=that,
        **yl(kwargs)
    )
...
