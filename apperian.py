# coding=utf-8
import json
import os
import logging
import pkgutil
from modules import applications, groups, users, wrapping, publishing, bench
__author__ = 'Shawn Roche'

ENDPOINTS = json.loads(pkgutil.get_data('apperian', 'endpoints.json'))
# with open('endpoints.json', 'rb') as f:
#     ENDPOINTS = json.load(f)


class Client(bench.Bench):
    def __init__(self, user, pw, region='default', verbose=False, php=None, py=None):
        bench.Bench.__init__(self, region)
        self.verbose = verbose
        log_level = logging.DEBUG if self.verbose else logging.CRITICAL
        logging.basicConfig(format="[%(levelname)8s] %(message)s", level=log_level)
        self.username = user
        self.password = pw
        self.user_data = {}
        # self.user, self.app, self.group, self.wrapper, self.publish = '', '', '', '', ''
        self.py = py
        self.php = php
        self.valid = Client.set_region(self, region)

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

        resp = Client.response_check(r)

        if resp['status'] == 200:
            self.token = resp['result']['token']
            self.user_data = resp['result']
            Client.update_connectors(self)
            return True
        else:
            if self.verbose:
                logging.debug('Auth failed\n{}'.format(r.text))
            return False

    def set_region(self, region):
        """
        Change the region you access for this session and authenticates you to the new environment.
        If 'list' is provided as the value for region you will see a list of options to manually choose from.

        :param region: Optional. Provide alternate region string. Use region='list' to manually select one
        """

        if self.php and self.py:
            self.region = {
                'PHP Web Services': 'https://{}/ease.interface.php'.format(self.php),
                'Python Web Services': 'https://{}'.format(self.py),
                'File Uploader': 'https://{}'.format(self.php.replace('easesvc', 'fupload'))
            }
        else:
            key = ENDPOINTS.get(region.lower())
            if key:
                self.region = key
            else:
                if region != 'list':
                    print "%s is not a valid format. Please make a selection from below:" % region
                self.region = Client.display_options(ENDPOINTS, 'region')

        Client.init_connectors(self)
        return Client.auth(self)

    def set_default_region(self):
        """
        Allows you to change the default region this module uses without having to manually edit endpoints.json
        If you have never run this function the default region will be North America
        """

        print """
        You are about to change the default region this module uses for all future sessions.
        Make a selection from one of the below regions:
        """
        ENDPOINTS['default'] = Client.display_options(ENDPOINTS, 'region')
        self.region = ENDPOINTS['default']
        Client.auth(self, self.username, self.password)

        package_dir, package = os.path.split(__file__)
        data_path = os.path.join(package_dir, 'data', 'endpoints.json')
        with open(data_path, 'wb') as f:
            f.write(json.dumps(ENDPOINTS, indent=4, separators=(',', ': ')))

    def init_connectors(self):
        self.app = applications.Apps(self.region)
        self.group = groups.Groups(self.region)
        self.user = users.Users(self.region)
        self.publish = publishing.Publish(self.region)
        self.wrapper = wrapping.Wrapper(self.region, self.app)

    def update_connectors(self):
        for module in [self.app, self.group, self.user, self.publish]:
            module.user_data = self.user_data
            module.token = self.token
            module.py_session.headers.update({'X-TOKEN': self.token})
            module.php_payload["params"] = {"token": self.token}

        # Update app_obj in self.wrapper now that it has proper auth
        self.app.publish = self.publish
        self.wrapper.app_obj = self.app

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
        result = Client.response_check(r, 'deleted_organization')
        return result
