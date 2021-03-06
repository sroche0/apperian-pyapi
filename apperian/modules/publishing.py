import json
import logging
from subprocess import PIPE, Popen
from helpers import response_check


class Publish:
    def __init__(self, php_session, php_payload, py_session, region):
        self.token, self.transactionID, self.file_id = '', '', ''
        self.payload = php_payload
        self.php_session = php_session
        self.py_session = py_session
        self.region = region

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
            pub_data['transactionID'] = transaction_id['result']
            file_id = Publish.upload(self, pub_data)
            if file_id['status'] == 200:
                pub_data['file_id'] = file_id['result']
                pub = Publish.publish(self, metadata, pub_data)
                return pub
            else:
                return file_id
        else:
            return transaction_id

    def create(self):
        """
        Creates an entry in EASE for the publishing API to upload a file to.
        Uses a token from the auth function
        :return: Returns transaction ID
        """
        self.payload['method'] = "com.apperian.eas.apps.create"
        r = self.php_session.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result', 'transactionID')

        return result

    def upload(self, data):
        """
        :param data: Dict with the file anme and transaction ID. Dict keys are: file_name, transactionID
        :return: returns fileID for the publish step
        """
        result = {}
        url = '{}/upload?transactionID={}'.format(self.region['File Uploader'], data['transactionID'])
        file_id, err = Popen(['curl', '--form', 'LUuploadFile=@{}'.format(data['file_name']), url],
                             stdout=PIPE, stdin=PIPE, stderr=PIPE).communicate()
        try:
            result['result'] = json.loads(file_id)['fileID']
            result['status'] = 200
        except (KeyError, ValueError):
            result['status'] = 500
            logging.debug([file_id, 'curl --form', 'LUuploadFile=@{} {}'.format(data['file_name'], url)])
            result['result'] = [file_id, 'curl --form', 'LUuploadFile=@{} {}'.format(data['file_name'], url)]

        return result

    def update(self, app_id):
        self.payload['method'] = "com.apperian.eas.apps.update"
        self.payload['params'].update({'appID': app_id})
        r = self.php_session.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
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
        r = self.php_session.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
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
             "transactionID": publishing_data['transactionID']
             }
        )
        r = self.php_session.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        result = response_check(r, 'result', 'appID')
        return result

    def get_credentials(self):
        """
        Lists all stored signing credentials for authenticated user's account

        :return: List of dicts with needed credential info. Each stored credential gets its own dict
        """
        url = '{}/v1/credentials/'.format(self.region['Python Web Services'])
        r = self.py_session.get(url)
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
        r = self.py_session.put(url)
        result = response_check(r, 'signing_status')
        return result
