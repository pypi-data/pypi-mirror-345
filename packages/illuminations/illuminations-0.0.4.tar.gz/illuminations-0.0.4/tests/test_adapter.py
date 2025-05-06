# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import pytest
from src.illuminations.adapter import decode, encode


SINGLE_OUTPUT = {
    'id': 'b205b1ab-79e7-4f85-b822-919ca1b1d886',
    'object': 'chat.completion',
    'created': 1746469042,
    'model': 'accounts/fireworks/models/deepseek-v3-0324',
    'choices': [
        {'index': 0,
         'message': {
             'role': 'assistant',
             'content': 'Ah! That sounds like the opening of one of those old, whimsical folktales where the world was topsy-turvy and animals did all sorts of peculiar things. '},
         'finish_reason': 'stop'
         }
    ],
    'usage': {'prompt_tokens': 21, 'total_tokens': 604, 'completion_tokens': 583}
}


MULTIPLE_OUTPUTS = {
    'id': 'a33d247b-18b9-4141-92ac-68b0247689cb',
    'object': 'chat.completion',
    'created': 1746469566,
    'model': 'accounts/fireworks/models/deepseek-v3-0324',
    'choices': [
        {
            'index': 0,
            'message':
                {
                    'role': 'assistant',
                    'content': 'Ah! That sounds like the opening of one of those old, whimsical folktales where the world was topsy-turvy and animals did all sorts of peculiar things. '
                },
            'finish_reason': 'stop'
        },
        {
            'index': 1,
            'message':
                {
                    'role': 'assistant',
                    'content': 'Ah! That sounds like the opening of an old folk tale or nursery rhyme. '
                },
            'finish_reason': 'stop'
        }
    ],
    'usage': {'prompt_tokens': 21, 'total_tokens': 461, 'completion_tokens': 440}
}


@pytest.fixture(scope="session")
def user_said():
    message = {
        'role': 'user',
        'content': 'This is a user text'
    }
    return message


@pytest.fixture(scope="session")
def instruction():
    message = {
        'role': 'system',
        'content': 'This is a system message'
    }
    return message


@pytest.fixture(scope="session")
def single_response():
    response = {
        'choices': [
            {'message':
                 {
                     'role': 'assistant',
                     'content': 'Here is a response'
                 }
            }
        ]
    }
    return response


@pytest.fixture(scope="session")
def multiple_responses():
    responses = {
        'choices': [
            {
                'message':
                    {
                        'role': 'assistant',
                        'content': 'Here is a response'
                    }
            },
            {
                'message':
                    {
                        'role': 'assistant',
                        'content': 'Here is a yet another response'
                    }
            }
        ]
    }
    return responses


@pytest.fixture(scope="session")
def log_of_a_turn_with_single_response():
    messages = [
        {
            'role': 'user',
            'content': 'This is a user text'

        }, {
            'role': 'assistant',
            'content': 'Here is a response'
        }
    ]
    return messages


@pytest.fixture(scope="session")
def record_of_a_turn_with_single_response():
    records = [
        {
            'Human': 'This is a user text'
        }, {
            'machine': 'Here is a response'
        }
    ]
    return records


@pytest.fixture(scope="session")
def log_of_a_turn_with_many_responses():
    messages = [
        {
            'role': 'user',
            'content': 'This is a user text'

        }, {
            'role': 'assistant',
            'content': 'Here is a response'
        }
    ]
    return messages


@pytest.fixture(scope="session")
def record_of_a_turn_with_many_responses():
    records = [
        {
            'Human': 'This is a user text'
        }, {
            'machine': [
                'Here is a response',
                'Here is a yet another response'
            ]
        }
    ]
    return records

