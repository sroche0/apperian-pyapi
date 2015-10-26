# coding=utf-8
__author__ = 'Shawn Roche'
import json
import ast
import requests
from subprocess import check_output
import os
import pkgutil

ENDPOINTS = json.loads(pkgutil.get_data('apperian', 'data/endpoints.json'))


def region_options(data):
    options, valid, choice = [], False, ''
    for key, value in enumerate(data):
        print "    %s. %s" % (key+1, value)
        options.append(value)

    while not valid:
        try:
            choice = int(raw_input('\nEnter number of new default region > '))
            if 0 < choice <= len(options):
                valid = True
                choice -= 1
            else:
                print 'Please select a valid option'
        except ValueError:
            print "Please enter a number."

    return data[options[choice]]


def response_check(r, *args):
    result = {'status': r.status_code}
    try:
        message = r.json()
        if r.ok:
            if args:
                for arg in args:
                    message = message[arg]
        else:
            try:
                message = message['error']['message']
            except KeyError:
                pass
    except ValueError:
        message = r.text

    result['result'] = message
    return result


class Ease:
    def __init__(self, user, pw, region='default'):
        self.username = user
        self.password = pw
        self.region = {}
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
        if user: self.username = user
        if password: self.password = password

        payload = json.dumps({'user_id': self.username, 'password': self.password})
        url = '%s/users/authenticate/' % self.region['Python Web Services']
        r = self.s.post(url, data=payload)

        if r.ok:
            self.s.headers.update({'X-TOKEN': r.json()['token']})
            return True
        else:
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

    ######################################
    # Application Functions
    ######################################

    def app_list_catalogs(self):
        """
        List data for all app catalogs

        :return: Returns data about all the App Catalogs in the authenticated user's organization
        """
        url = '%s/v1/applications/app_catalogs/' % self.region['Python Web Services']
        r = self.s.get(url)
        result = response_check(r, 'app_catalogs')
        if result['status'] == 200:
            app_data = {}
            for i in result['data']:
                app_data.update({i['psk']: i})
            result['data'] = app_data
        return result

    def app_list_available(self):
        """
        List application data about all the applications available in EASE to the authenticated user. An application is
        considered available if it is assigned to a group to which the user belongs

        :return: Dict with key:value pairs of the app psk and it's metadata. For example: {123:{METADATA}}

        """
        url = '%s/v1/applications/user' % self.region['Python Web Services']
        r = self.s.get(url)
        result = response_check(r, 'applications')
        if result['status'] == 200:
            app_data = {}
            for i in result['data']:
                app_data.update({i['psk']: i})
            result['data'] = app_data
        return result

    def app_list_all(self):
        """
        List application data about all the native applications stored in the EASE database for the authenticated
        user’s organization.

        :return: Dict with key:value pairs of the app psk and it's metadata. For example: {123:{METADATA}}
        """
        url = '%s/v1/applications/' % self.region['Python Web Services']
        r = self.s.get(url)
        result = response_check(r, 'applications')
        # if result['status'] == 200:
        #     app_data = {}
        #     for i in result['result']:
        #         app_data.update({i['psk']: i})
        #     result['result'] = app_data
        return result

    def app_usage(self, psk, start_date, end_date):
        """
        List download and usage count for a specific app

        :param psk: Unique ID for the app.
        :param start_date: Start date for the statistical period. For example: 2014-01-15
        :param end_date: End date for the statistical period. For example: 2014-01-30
        :return:Returns Download Count and Usage Count for an application during a specified statistical time period.
        """
        url = '%s/v1/applications/%s/stats?start_date=%s&end_date=%s' % \
              (self.region['Python Web Services'], str(psk), start_date, end_date)
        r = self.s.get(url)
        result = response_check(r, 'app_stats')
        return result

    def app_data(self, psk):
        """
        List data for a specific app

        :param psk: Unique ID of the app
        :return: Returns dict of metadata about the specified application. Specify the app with app_psk.
        """
        url = '%s/v1/applications/%s' % (self.region['Python Web Services'], str(psk))
        r = self.s.get(url)
        result = response_check(r, 'application')
        return result

    ######################################
    # User Functions
    ######################################

    def user_add(self, data):
        """
        Must be authenticated as an EASE admin. Adds a new user to the EASE organization of the authenticated user.

        :param data: a dict of the user details you want to add.
        :return: A successful response provides a unique key (user_psk) for the user.
        """
        url = '%s/v1/users' % self.region['Python Web Services']
        r = self.s.post(url, data=json.dumps(data))
        result = response_check(r, 'user_psk')
        return result

    def user_list(self, psk):
        """
        Returns information stored in the database about a user, such as user ID, email, phone number,
        and the date when the user was created.

        :param psk: Unique ID assigned to the user you want to look up
        :return: Returns a dict with the target user's details
        """
        url = '%s/v1/users/%s' % (self.region['Python Web Services'], psk)
        r = self.s.get(url)
        result = response_check(r, 'user')
        return result

    def user_list_all(self):
        """
        Lists user details for every user in the org you are authenticated to. must be admin user to run

        :return: Returns a list of dicts. Dict keys are: psk, first_name, last_name, modified_date, deleted, email,
        mobile_phone, role, created_date, until_date, disabled_reason, id, last_login_from_catalog
        """
        url = '%s/users' % self.region['Python Web Services']
        r = self.s.get(url)
        result = response_check(r, 'users')
        return result

    def user_delete(self, psk):
        """
        Deletes a user from your EASE organization. A deleted user can no longer access the App Catalog or the EASE
        Portal. If a deleted user tries to log in, the user will see a message that advises the user to contact support.

        :param psk: psk of the user to be deleted
        :return: returns "ok", "auth", or the error message
        """
        url = '%s/users/%s' % (self.region['Python Web Services'], psk)
        r = self.s.delete(url)
        result = response_check(r, 'delete_user_response')
        return result

    def user_update(self, psk, payload):
        """
        Updates the following data attributes for a user in your EASE organization: email, password, first_name,
        last_name, phone.

        When you request this resource, you will need to provide the user_psk value assigned when you added the user.

        :param psk: Unique ID assigned to the user by EASE.
        :param payload: a dict with the following keys: email, password, first_name, last_name, phone
        :return: Dict with status and result of True/False
        """
        url = '%s/v1/users/%s' % (self.region['Python Web Services'], psk)
        r = self.s.put(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        result = response_check(r, 'update_user_success')
        return result

    ######################################
    # Group Functions
    ######################################

    def group_list(self):
        """
        list of all the groups for the authenticated user’s organization. This list includes the number of users
        and number of applications belonging to each group.

        :return: List of dicts of the groups. Dict keys are: app_count, psk, user_count, name, description

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '%s/v1/groups/' % self.region['Python Web Services']
        r = self.s.get(url)
        result = response_check(r, 'groups')
        return result

    def group_add(self, data):
        """
        Adds a new group to the authenticated user’s organization.

        :param data: Dict with metadata for group. Required keys are: group_name, group_description
        :return: Dict of new groups details. Dict keys are: psk, name, description

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '%s/v1/groups/' % self.region['Python Web Services']
        payload = json.dumps(data)
        r = self.s.post(url, data=payload)
        result = response_check(r, 'group')
        return result

    def group_add_member(self, user_psk, groups):
        """
        Adds a specified user to a list of groups. Specify groups by group_psk.

        :param user_psk: Unique ID assigned by EASE to the user you want to add to the list of groups
        :param groups: Comma-separated list of the group psks
        :return:Dict of lists. Dict keys are: added_groups, failed_groups

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '{}/v1/groups/users/{}'.format(self.region['Python Web Services'], user_psk)
        payload = json.dumps({"group_psk": groups})
        r = self.s.get(url, data=payload)
        result = response_check(r, 'response')
        return result

    def group_list_apps(self, group_psk):
        """
        Returns a list of the applications that are in the specified group.

        :param group_psk: Unique ID assigned by EASE to the group.
        :return: List of dicts. See API docs for dict keys

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '{}/v1/groups/{}'.format(self.region['Python Web Services'], group_psk)
        r = self.s.post(url)
        result = response_check(r, 'applications')
        return result

    def group_add_apps(self, group_psk, app_list):
        """
        Adds applications to a specified group. Specify apps by app_psk.

        :param group_psk: Unique ID assigned by EASE to the group.
        :param app_list: Comma-separated list of the app_psks for the applications you want to add to the group.
        :return: Dict of lists. Dict keys are: apps_added, apps_failed
        """
        url = '{}/v1/groups/{}/applications'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({"app_psk": app_list})
        r = self.s.get(url, data=payload)
        result = response_check(r, 'response')
        return result

    def group_delete_apps(self, group_psk, app_list):
        """
        Removes applications from a group. Specify apps by app_psk

        :param group_psk: Unique ID assigned by EASE to the group.
        :param app_list: Comma-separated list of the app_psks for the applications you want to remove from the group.
        :return: Dict of lists. Dict keys are: apps_removed, apps_failed
        """
        url = '{}/v1/groups/{}/applications'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({"app_psk": app_list})
        r = self.s.delete(url, data=payload)
        result = response_check(r, 'response')
        return result

    def group_list_members(self, group_psk):
        """
        Lists users who are members of a specified group.

        :param group_psk: Unique ID assigned by EASE to the group.
        :return: List of Dicts. See API docs for dict keys

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '{}/v1/groups/{}/users/'.format(self.region['Python Web Services'], group_psk)
        r = self.s.get(url)
        result = response_check(r, 'users_in_group')
        return result

    def group_add_members(self, group_psk, user_list):
        """
        Adds a list of users to a specified group. Specify users by user_psk.

        :param group_psk: Unique ID assigned by EASE to the group.
        :param user_list: Comma-separated list of the user_psks for the users you want to add to the group.
        :return: Dict of lists. Dict keys are: users_failed, users_added
        """
        url = '{}/v1/groups/{}/users'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({"user_psk": user_list})
        r = self.s.get(url, data=payload)
        result = response_check(r, 'response')
        return result

    def group_remove_members(self, group_psk, user_list):
        """
        Removes applications from a group. Specify apps by app_psk

        :param group_psk: Unique ID assigned by EASE to the group.
        :param user_list: Comma-separated list of the app_psks for the applications you want to remove from the group.
        :return: Dict of lists. Dict keys are: users_failed, users_removed
        """
        url = '{}/v1/groups/{}/users'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({"user_psk": user_list})
        r = self.s.delete(url, data=payload)
        result = response_check(r, 'response')
        return result

    def group_update(self, group_psk, data):
        """
        Updates data for an existing group in the authenticated user's organization.

        :param group_psk: Unique ID assigned by EASE to the group.
        :param data: Dict of group metadata to change. Required keys: group_name, group_description
        :return: Dict with updated metadata. Dict keys are: psk, name, description
        """
        url = '{}/v1/groups/{}'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({data})
        r = self.s.put(url, data=payload)
        result = response_check(r, 'group')
        return result

    def group_delete(self, group_psk):
        """
        Permanently deletes a group from the authenticated user’s organization.

        :param group_psk: Unique ID assigned by EASE to the group.
        :result: Dict with deleted groups metadata. Dict keys are: psk, name, description
        """
        url = '{}/v1/groups/{}'.format(self.region['Python Web Services'], group_psk)
        r = self.s.delete(url)
        result = response_check(r, 'deleted_group')
        return result


class Publish:
    def __init__(self, user, pw, region='default'):
        self.token, self.trans_id, self.file_id, self.region = '', '', '', {}
        self.payload = {"id": 1, "apiVersion": "1.0", "method": "", "jsonrpc": "2.0"}
        self.username = user
        self.password = pw
        self.s = requests.Session()
        self.s.headers = {"Content-Type": "application/js"}
        self.valid = Publish.set_region(self, region)

        Publish.set_region(self)

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
        if user: self.username = user
        if password: self.password = password

        self.payload['method'] = "com.apperian.eas.user.authenticateuser"
        self.payload['params'] = {"email": self.username, "password": self.password}

        r = self.s.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        if r.ok:
            self.token = r.json().get('result', {}).get('token')
            result = True
        else:
            print 'Authentication Failed.'
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
        r = requests.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result', 'transactionID')

        return result

    def upload(self, data):
        """
        :param data: Dict with the file anme and transaction ID. Dict keys are: file_name, trans_id
        :return: returns fileID for the publish step
        """
        result = {}
        print 'Uploading File...\n'
        url = '%s/upload?transactionID=%s' % (self.region['File Uploader'], data['trans_id'])
        upload = ast.literal_eval(check_output(['curl', '--form', 'LUuploadFile=@{}'.format(data['file_name']), url]))
        result['result'] = upload.get('fileID')
        if result['result']:
            result['status'] = 200
            print 'Upload Complete'
            return result
        else:
            print 'check upload command: curl --form', 'LUuploadFile=@{}'.format(data['file_name']), url
            exit('File Upload Failed')

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
        r = requests.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result', 'applications')
        return result

    def publish(self, metadata, data):
        """
        :param data: Dict of the metadata that is required to upload to ease.
        """
        self.payload['method'] = 'com.apperian.eas.apps.publish'
        self.payload['params'].update(
            {"EASEmetadata": metadata,
             "files": {"application": data['file_id']},
             "transactionID": data['trans_id']
             }
        )
        r = self.s.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result')
        return result

    def get_credentials(self):
        url = '{}/v1/credentials/'.format(self.region['Python Web Services'])
        self.s.headers.update({'X-TOKEN': self.token})
        r = self.s.get(url)
        result = response_check(r, 'credentials')
        return result

    def sign_application(self, app_psk, credentials_psk):
        url = '{}/v1/applications/{}/credentials/{}'.format(self.region['Python Web Services'],
                                                            app_psk, credentials_psk)
        self.s.headers.update({'X-TOKEN': self.token})
        r = self.s.put(url)
        result = response_check(r, 'signing_status')
        return result
