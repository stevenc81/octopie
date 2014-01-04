# -*- coding: utf-8 -*-

from octopie.api import GitHubAPI
from octopie.api import APIError

from nose.tools import assert_equal
from nose.tools import assert_true

class TestAPI(object):
    def test_user_name(self):
        api_client = GitHubAPI()
        result = {}
        try:
            result = api_client.users.get('stevenc81')
        except APIError as e:
            print e

        assert_equal(result['name'], 'Steven Cheng')

    def test_user_login(self):
        api_client = GitHubAPI()
        result = {}
        try:
            result = api_client.users.get('stevenc81')
        except APIError as e:
            print e

        assert_equal(result['login'], 'stevenc81')

    def test_header_ratelimit(self):
        api_client = GitHubAPI()
        result = {}
        try:
            result = api_client.users.get('stevenc81')
        except APIError as e:
            print e

        assert_true('X-RateLimit-Remaining' in result['headers'])
