# coding=utf-8
import json
import requests
import os
import logging
import pkgutil
from modules import applications, groups, users, wrapping
from modules.helpers import display_options, response_check
__author__ = 'Shawn Roche'

# ENDPOINTS = json.loads(pkgutil.get_data('apperian', 'endpoints.json'))
with open('endpoints.json', 'rb') as f:
    ENDPOINTS = json.load(f)


class Ease:
    def __init__(self, user, pw, region='default', verbose=False):
        self.verbose = verbose
        log_level = logging.DEBUG if self.verbose else logging.CRITICAL
        logging.basicConfig(format="[%(levelname)8s] %(message)s", level=log_level)
        self.username = user
        self.password = pw
        self.region, self.token = {}, ''
        self.user, self.app, self.group, self.wrapper = '', '', '', ''
        # Setup python session
        self.py_session = requests.Session()
        self.py_session.headers.update({"Content-Type": "application/json"})
        # Setup php session
        self.php_session = requests.Session()
        self.php_session.headers = {"Content-Type": "application/js"}
        self.php_payload = {"id": 1, "apiVersion": "1.0", "method": "", "jsonrpc": "2.0"}

        self.valid = Ease.set_region(self, region)

    def auth(self, user=None, password=None):
        """
        Authenticate user to the API. If user and password params are left blank, function will use the
        credentials instance was started with

        :param user: User ID for a valid EASE user in your organization’s EASE account
        :param password: User’s password
        :return: Boolean
        """
        if user:
            self.username = user
        if password:
            self.password = password

        # Python auth
        payload = json.dumps({'user_id': self.username, 'password': self.password})
        url = '%s/users/authenticate/' % self.region['Python Web Services']
        if self.verbose:
            logging.debug('Sending auth via {}'.format(url))
        r = self.py_session.post(url, data=payload)

        resp = response_check(r, 'token')

        if resp['status'] == 200:
            self.token = resp['result']
            self.py_session.headers.update({'X-TOKEN': self.token})
            self.php_payload["params"] = {"token": self.token}
            Ease.connectors(self)
            return resp['result']
        else:
            if self.verbose:
                logging.debug('Auth failed\n{}'.format(r.text))
            return False

    def set_region(self, region='default'):
        """
        Change the region you access for this session and authenticates you to the new environment.
        If 'list' is provided as the value for region you will see a list of options to manually choose from.

        :param region: Optional. Provide alternate region string. Use region='list' to manually select one
        """

        key = ENDPOINTS.get(region)
        if key:
            self.region = key
        else:
            if region != 'list':
                print "%s is not a valid region. Please make a selection from below:" % region
            self.region = display_options(ENDPOINTS, 'region')

        return Ease.auth(self)

    def set_default_region(self):
        """
        Allows you to change the default region this module uses without having to manually edit endpoints.json
        If you have never run this function the default region will be North America
        """

        print """
        You are about to change the default region this module uses for all future sessions.
        Make a selection from one of the below regions:
        """
        ENDPOINTS['default'] = display_options(ENDPOINTS, 'region')
        self.region = ENDPOINTS['default']
        Ease.auth(self, self.username, self.password)

        package_dir, package = os.path.split(__file__)
        data_path = os.path.join(package_dir, 'data', 'endpoints.json')
        with open(data_path, 'wb') as f:
            f.write(json.dumps(ENDPOINTS, indent=4, separators=(',', ': ')))

    def connectors(self):
        self.app = applications.Apps(self.py_session, self.region)
        self.group = groups.Groups(self.py_session, self.region)
        self.user = users.Users(self.py_session, self.region)
        self.wrapper = wrapping.Wrapper(self.php_session, self.php_payload, self.app, self.region)

    ######################################
    # Org Functions
    ######################################

    def org_delete(self, psk):
        """
        :param psk: psk of the organization to be deleted
        :return: returns "ok", "auth", or the error message
        """
        url = '%s/organizations/%s' % (self.region['Python Web Services'], psk)
        r = self.py_session.delete(url)
        result = response_check(r, 'deleted_organization')
        return result

