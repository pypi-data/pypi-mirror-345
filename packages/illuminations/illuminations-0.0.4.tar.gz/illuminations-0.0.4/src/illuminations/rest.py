# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
from os import environ
import requests
from .adapter import decode


api_key                 = environ.get('FIREWORKS_API_KEY')
api_base                = environ.get('FIREWORKS_BASE_URL', 'https://api.fireworks.ai/inference/v1')
fireworks_content_model = environ.get('FIREWORKS_MODEL','accounts/fireworks/models/deepseek-v3-0324')

headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + api_key
}


def continuation(text=None, contents=None, instruction=None, recorder=None, **kwargs):
    """A continuation of text with a given context and instruction.
        kwargs:
            temperature     = 0 to 1.0
            top_p           = 0.0 to 1.0
            top_k           = The maximum number of tokens to consider when sampling.
            n               = 1 to ...
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
        'model':                    kwargs.get('model', fireworks_content_model),
        'messages':                 instruction_and_contents,
        'response_format':          kwargs.get('response_format',{'type': 'text'}),
        'temperature':              kwargs.get('temperature', 1),  # 0.0 to 2.0
        'max_tokens':               kwargs.get('max_tokens', 4096),
        'prompt_truncate_len':      kwargs.get('prompt_truncate_len', 100000),
        'n':                        kwargs.get('n', 1),
        'top_p':                    kwargs.get('top_p', 0.9),
        'top_k':                    kwargs.get('top_k', 10),
        # 'reasoning_effort':         kwargs.get('reasoning_effort', 'low'),  # 'low', 'medium', 'high'
        'stream':                   False
    }

    try:
        response = requests.post(
            url=f'{api_base}/chat/completions',
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


def completion(text, **kwargs):
    """A completions endpoint call through requests.
        kwargs:
            temperature     = 0 to 1.0
            top_p           = 0.0 to 1.0
            n               = 1 to ...
            best_of         = 4
            frequency_penalty = -2.0 to 2.0
            presence_penalty = -2.0 to 2.0
            max_tokens      = number of tokens
            logprobs        = number up to 5
            stop            = ["stop"]  array of up to 4 sequences
            logit_bias      = map token: bias -1.0 to 1.0 (restrictive -100 to 100)

    Use this method as follows:
    ..  code-block:: python
        res = aFunction(something, goes, in)
        print(res.avalue)
    """
    responses = []
    json_data = {
        "model":            kwargs.get("model", fireworks_content_model),
        "prompt":           kwargs.get("prompt", text),
        "suffix":           kwargs.get("suffix", None),
        "max_tokens":       kwargs.get("max_tokens", 5),
        "n":                kwargs.get("n", 1),
        "best_of":          kwargs.get("best_of", 1),
        "stop":             kwargs.get("stop_sequences", ["stop"]),
        "seed":             kwargs.get("seed", None),
        "frequency_penalty":kwargs.get("frequency_penalty", None),
        "presence_penalty": kwargs.get("presence_penalty", None),
        "logit_bias":       kwargs.get("logit_bias", None),
        "logprobs":         kwargs.get("logprobs", None),
        "top_logprobs":     kwargs.get("top_logprobs", None),
        "temperature":      kwargs.get("temperature", 0.5),
        "top_p":            kwargs.get("top_p", 0.5),
        "user":             kwargs.get("user", None)
    }

    try:
        response = requests.post(
            f"{api_base}/completions",
            headers=headers,
            json=json_data,
        )
        if response.status_code == requests.codes.ok:
            for choice in response.json()['choices']:
                responses.append(choice)
        else:
            print(f"Request status code: {response.status_code}")
        return responses
    except Exception as e:
        print("Unable to generate Completions response")
        print(f"Exception: {e}")
        return responses


if __name__ == '__main__':
    ...