# coding=utf-8
import json
from helpers import response_check, display_options


class Apps:
    def __init__(self, session, region):
        self.session = session
        self.base = '{}/v1/applications'.format(region['Python Web Services'])

    def list(self):
        """
        GET /applications
        List application data about all the native applications stored in the EASE database for the authenticated
        user’s organization.

        :return: Dict with key:value pairs of the app psk and it's metadata. For example: {123:{METADATA}}
        """
        url = self.base
        r = self.session.get(url)
        resp = response_check(r, 'applications')
        # if resp['status'] == 200:
        #     app_data = {}
        #     for i in resp['resp']:
        #         app_data.update({i['psk']: i})
        #     resp['resp'] = app_data
        return resp

    def get_details(self, psk):
        """
        GET /applications/<app_psk>
        List data for a specific app

        :param psk: Unique ID of the app
        :return: Returns dict of metadata about the specified application. Specify the app with app_psk.
        """
        url = '{}/{}'.format(self.base, str(psk))
        r = self.session.get(url)
        resp = response_check(r, 'application')
        return resp

    def add_screenshot(self, psk, form, slot):
        """
        POST /applications/<app_psk>/screenshots/[phone/tablet]/<slot>
        Upload a Screenshot for An Application

        :param psk: unique ID of the app
        :param form: Form factor of the app the screenshot it for. Valid Value: phone, tablet
        :param slot: Order in which the screenshot will display on the app's details page in the App Catalog. If you
            specify the same slot of a screenshot that is already stored for the same form factor (phone or tablet),
            the new file will overwrite the previously added file. Valid values: 1-5:
        :return:

        """
        url = '{}/{}/screenshots/{}/{}'.format(self.base, psk, form, slot)
        r = self.session.post(url)
        resp = response_check(r)
        return resp

    def delete_screenshot(self, psk, form, slot):
        """
        DELETE /applications/<app_psk>/screenshots/[phone/tablet]/<slot>
        Delete an Application Screenshot

        :param psk: unique ID of the app
        :param form: Form factor of the app the screenshot it for. Valid Value: phone, tablet
        :param slot: Specify the slot of the screenshot you want to delete. You can view a list with slot number of all
            the screenshots stored for an app by returning details about the app with the GET /applications/<app_psk>
            resource. Be sure to specify the correct form factor (phone or tablet) in the URL. There is a slot 1 - 5
            for both phone and tablet. Valid values: 1-5
        :return:

        """
        url = '{}/{}/screenshots/{}/{}'.format(self.base, psk, form, slot)
        r = self.session.delete(url)
        resp = response_check(r)
        return resp

    def get_media(self, psk):
        """
        GET /applications/<app_psk>/related_media/
        List data for a specific app

        :param psk: Unique ID of the app
        :return: Returns list of media files and their metadata in dicts.
        """
        url = '{}/{}/related_media'.format(self.base, str(psk))
        r = self.session.get(url)
        resp = response_check(r, 'related_media')
        return resp

    def get_usage(self, psk, start_date, end_date):
        """
        GET /applications/<app_psk>/stats
        List download and usage count for a specific app

        :param psk: Unique ID for the app.
        :param start_date: Start date for the statistical period. yyyy-mm-dd format
        :param end_date: End date for the statistical period. yyyy-mm-dd format
        :return:Returns Download Count and Usage Count for an application during a specified statistical time period.
        """
        url = '{}/{}/stats?start_date={}&end_date={}'.format(self.base, psk, start_date, end_date)
        r = self.session.get(url)
        resp = response_check(r, 'app_stats')
        return resp

    def get_versions(self, psk):
        """
        GET /applications/<app_psk>/versions/
        List All Version Information for an Application

        :param psk: Unique ID of the app
        :return: Returns version information for all versions of the specified application
        :rtype: list of dicts
        """
        pass

    def list_catalogs(self):
        """
        GET /applications/app_catalogs
        List data for all app catalogs

        :return: Returns data about all the App Catalogs in the authenticated user's organization
        """
        url = '{}/app_catalogs/'.format(self.base)
        r = self.session.get(url)
        resp = response_check(r, 'app_catalogs')
        if resp['status'] == 200:
            app_data = {}
            for i in resp['data']:
                app_data.update({i['psk']: i})
            resp['data'] = app_data
        return resp

    def list_available(self):
        """
        GET /applications/user
        List application data about all the applications available in EASE to the authenticated user. An application
        is available if it is assigned to a group to which the user belongs

        :return: Dict with key:value pairs of the app psk and it's metadata. For example: {123:{METADATA}}

        """
        url = '{}/user'.format(self.base)
        r = self.session.get(url)
        resp = response_check(r, 'applications')
        if resp['status'] == 200:
            app_data = {}
            for i in resp['result']:
                app_data.update({i['psk']: i})
            resp['result'] = app_data
        return resp

    def download(self, psk, path=False):
        """
        GET /downloads/direct/applications/<app_id>
        Download the Application's Binary File

        :param psk: Unique ID of the app. Returned by list() or get_details() as "direct_download_binary_url"
        :param path: Path to save file to. If not passed, file will save in CWD with default filename
        :return: True False for download success/
        """
        pass

    def toggle(self, app_psk, state):
        """
        PUT /applications/<app_psk>
        Allows you do enable or disable and app in your account.

        :param app_psk: Unique ID of the app. Use the app_list_available() method
        :param state: Boolean Value of desired state of the app
        :return: Dict of request status
        """
        url = '{}/{}'.format(self.base, app_psk)
        r = self.session.put(url, data=json.dumps({'enabled': state}))
        resp = response_check(r, 'update_application_resp')
        return resp

    def delete(self, psk):
        """
        DELETE /applications/<app_psk>
        Deletes a specific application from your EASE organization

        :param psk: Unique ID for the app
        :return: psk of deleted app on success, dict of error on failure
        """
        url = '{}/{}'.format(self.base, psk)
        r = self.session.delete(url)
        resp = response_check(r, 'deleted_application')
        return resp

    def get_credentials(self, show=False):
        """
        GET /credentials
        Returns data about all signing credentials stored in EASE for the authenticated user’s organization. Optional
        parameter to select from a list. If used it will return just the psk of the selected credential

        :param show: Optional, if set to True, you will select from a list of options
        :return: List of stored credentials for the
        """
        url = '{}credentials'.format(self.base)
        url = url.replace('applications', '')
        r = self.session.get(url)
        resp = response_check(r, 'credentials')
        if show:
            choice = display_options(resp['result'], 'credential', 'description')
            resp['result'] = choice['psk']
        return resp

    def sign(self, app_psk, cred_psk):
        """
        PUT /applications/<app_psk>/credentials/<credentials_psk>
        Signs an iOS or Android application using signing credentials that were previously stored in EASE for the
        authenticated user's organization

        :param app_psk: Unique ID for the App
        :param cred_psk: Unique ID for the credentials
        :return: dict of Signing Status
        """
        url = '{}/{}/credentials/{}'.format(self.base, app_psk, cred_psk)
        r = self.session.put(url)
        result = response_check(r, 'signing_status')
        return result
