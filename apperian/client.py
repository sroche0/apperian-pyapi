# coding=utf-8
import json
import requests
from subprocess import Popen, PIPE
import os
import logging
import pkgutil
from modules import applications, groups, users
from modules.helpers import region_options, response_check
__author__ = 'Shawn Roche'

ENDPOINTS = json.loads(pkgutil.get_data('apperian', 'endpoints.json'))
# with open('endpoints.json', 'rb') as f:
#     ENDPOINTS = json.load(f)


class Ease:
    def __init__(self, user, pw, region='default', verbose=False):
        self.verbose = verbose
        log_level = logging.DEBUG if self.verbose else logging.CRITICAL
        logging.basicConfig(format="[%(levelname)8s] %(message)s", level=log_level)
        self.username = user
        self.password = pw
        self.region = {}
        self.user, self.app, self.group = '', '', ''
        self.s = requests.Session()
        self.s.headers.update({"Content-Type": "application/json"})
        self.valid = Ease.set_region(self, region)

    def auth(self, user=None, password=None):
        """
        Authenticate user to the python API. If user and password params are left blank, function will use the
        credentials instance was started with

        :param user: User ID for a valid EASE user in your organization’s EASE account
        :param password: User’s password
        :return: Boolean
        """
        if user:
            self.username = user
        if password:
            self.password = password

        payload = json.dumps({'user_id': self.username, 'password': self.password})
        url = '%s/users/authenticate/' % self.region['Python Web Services']
        if self.verbose:
            logging.debug('Sending auth via {}'.format(url))
        r = self.s.post(url, data=payload)

        resp = response_check(r, 'token')

        if resp['status'] == 200:
            self.s.headers.update({'X-TOKEN': resp['result']})
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
            self.region = region_options(ENDPOINTS)

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
        ENDPOINTS['default'] = region_options(ENDPOINTS)
        self.region = ENDPOINTS['default']
        Ease.auth(self, self.username, self.password)

        package_dir, package = os.path.split(__file__)
        data_path = os.path.join(package_dir, 'data', 'endpoints.json')
        with open(data_path, 'wb') as f:
            f.write(json.dumps(ENDPOINTS, indent=4, separators=(',', ': ')))

    def connectors(self):
        self.app = applications.Apps(self.s, self.region)
        self.group = groups.Groups(self.s, self.region)
        self.user = users.Users(self.s, self.region)

    ######################################
    # Org Functions
    ######################################

    def org_delete(self, psk):
        """
        :param psk: psk of the organization to be deleted
        :return: returns "ok", "auth", or the error message
        """
        url = '%s/organizations/%s' % (self.region['Python Web Services'], psk)
        r = self.s.delete(url)
        result = response_check(r, 'deleted_organization')
        return result


class Publish:
    def __init__(self, user, pw, region='default', verbose=False):
        self.verbose = verbose
        log_level = logging.DEBUG if self.verbose else logging.ERROR
        logging.basicConfig(format="[%(levelname)8s] %(message)s", level=log_level)
        self.token, self.trans_id, self.file_id = '', '', ''
        self.payload = {"id": 1, "apiVersion": "1.0", "method": "", "jsonrpc": "2.0"}
        self.username = user
        self.password = pw
        self.s = requests.Session()
        self.s.headers = {"Content-Type": "application/js"}
        self.region = {}
        self.valid = Publish.set_region(self, region)

    def add_new_app(self, file_name, metadata):
        """
        Adds a new app to your EASE instance under the category "Company Wide".
        Uses the functions create, upload, and publish

        :param file_name: name of the file you will be uploading. Can be a relative or absolute path
        :param metadata: Dict of the metadata needed to publish to ease. See API docs for dict keys

        :return:

        https://help.apperian.com/display/pub/apps.publish
        """
        pub_data = dict(file_name=file_name)
        transaction_id = Publish.create(self)
        if transaction_id['status'] == 200:
            pub_data['trans_id'] = transaction_id['result']
            file_id = Publish.upload(self, pub_data)
            if file_id['status'] == 200:
                pub_data['file_id'] = file_id['result']
                pub = Publish.publish(self, metadata, pub_data)
                return pub
            else:
                return file_id
        else:
            return transaction_id

    # def update_app(self, app_id):
    #     app_list = Publish.get_list(self)
    #     for k, v in app_list.iteritems():
    #         if i['ID'] ==
    #     data = {'app_id': app_list[app_id]}
    #
    #     pass

    def auth(self, user=None, password=None):
        """
        :param user: Admin username
        :param password: Admin password
        :return: Boolean
        """
        if user:
            self.username = user
        if password:
            self.password = password

        self.payload['method'] = "com.apperian.eas.user.authenticateuser"
        self.payload['params'] = {"email": self.username, "password": self.password}

        r = self.s.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result', 'token')
        if result.get('result'):
            try:
                self.token = str(result['result'].encode('ascii'))
                result = result['result']
            except AttributeError:
                result = False
        else:
            result = False

        self.payload["params"] = {"token": self.token}

        return result

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
            self.region = region_options(ENDPOINTS)

        return Publish.auth(self)

    def create(self):
        """
        Creates an entry in EASE for the publishing API to upload a file to.
        Uses a token from the auth function
        :return: Returns transaction ID
        """
        self.payload['method'] = "com.apperian.eas.apps.create"
        r = self.s.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result', 'transactionID')

        return result

    def upload(self, data):
        """
        :param data: Dict with the file anme and transaction ID. Dict keys are: file_name, trans_id
        :return: returns fileID for the publish step
        """
        result = {}
        url = '{}/upload?transactionID={}'.format(self.region['File Uploader'], data['trans_id'])
        file_id, err = Popen(['curl', '--form', 'LUuploadFile=@{}'.format(data['file_name']), url],
                             stdout=PIPE, stdin=PIPE, stderr=PIPE).communicate()
        try:
            result['result'] = json.loads(file_id)['fileID']
            result['status'] = 200
        except KeyError or ValueError:
            result['status'] = err
            result['result'] = [file_id, 'curl --form', 'LUuploadFile=@{} {}'.format(data['file_name'], url)]

        return result

    def update(self, app_id):
        self.payload['method'] = "com.apperian.eas.apps.update"
        self.payload['params'].update({'appID': app_id})
        r = self.s.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result')
        return result

    def get_list(self):
        """
        Lists all of the native apps in the organization you are authenticated to. Does not include webapps, or public
        app store links

        :return: List of dicts of app metadata. Dict keys are: ID, author, bundleID, longdescription, shortdescription,
            status, type, version, versionNotes
        """
        self.payload['method'] = "com.apperian.eas.apps.getlist"
        r = self.s.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result', 'applications')
        return result

    def publish(self, metadata, publishing_data):
        """
        :param metadata: Dict of the metadata that is required to upload to ease
        :param publishing_data: Dict of the params needed to publish
        """
        self.payload['method'] = 'com.apperian.eas.apps.publish'
        self.payload['params'].update(
            {"EASEmetadata": metadata,
             "files": {"application": publishing_data['file_id']},
             "transactionID": publishing_data['trans_id']
             }
        )
        r = self.s.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result')
        return result

    def get_credentials(self):
        """
        Lists all stored signing credentials for authenticated user's account

        :return: List of dicts with needed credential info. Each stored credential gets its own dict
        """
        url = '{}/v1/credentials/'.format(self.region['Python Web Services'])
        self.s.headers.update({'X-TOKEN': self.token})
        r = self.s.get(url)
        result = response_check(r, 'credentials')
        return result

    def sign_application(self, app_psk, credentials_psk):
        """
        Signs an app with the specified stored credential

        :param app_psk: Unique ID of app in ease. Can be found using list_apps()
        :param credentials_psk: Unique ID of the credentials to be used. Can be found via get_credentials()
        :return:
        """
        url = '{}/v1/applications/{}/credentials/{}'.format(self.region['Python Web Services'],
                                                            app_psk, credentials_psk)
        self.s.headers.update({'X-TOKEN': self.token})
        r = self.s.put(url)
        result = response_check(r, 'signing_status')
        return result
