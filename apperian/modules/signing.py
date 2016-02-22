# coding=utf-8
import json
from helpers import response_check

class Sign:
    def __init__(self, session, region):
        self.session = session
        self.base = '{}/v1/applications'.format(region['Python Web Services'])
