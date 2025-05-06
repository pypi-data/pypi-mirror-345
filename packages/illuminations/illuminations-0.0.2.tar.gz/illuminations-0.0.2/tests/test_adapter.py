# -*- coding: utf-8 -*-
# Python

"""Copyright (c) Alexander Fedotov.
This source code is licensed under the license found in the
LICENSE file in the root directory of this source tree.
"""
import pytest
from src.illuminations.adapter import decode, encode


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

