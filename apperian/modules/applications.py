# coding=utf-8
import json
from helpers import response_check


class Apps:
    def __init__(self, session, region):
        self.session = session
        self.region = region

    def list_catalogs(self):
        """
        List data for all app catalogs

        :return: Returns data about all the App Catalogs in the authenticated user's organization
        """
        url = '%s/v1/applications/app_catalogs/' % self.region['Python Web Services']
        r = self.session.get(url)
        result = response_check(r, 'app_catalogs')
        if result['status'] == 200:
            app_data = {}
            for i in result['data']:
                app_data.update({i['psk']: i})
            result['data'] = app_data
        return result

    def list_available(self):
        """
        List application data about all the applications available in EASE to the authenticated user. An application
        is considered available if it is assigned to a group to which the user belongs

        :return: Dict with key:value pairs of the app psk and it's metadata. For example: {123:{METADATA}}

        """
        url = '%s/v1/applications/user' % self.region['Python Web Services']
        r = self.session.get(url)
        result = response_check(r, 'applications')
        if result['status'] == 200:
            app_data = {}
            for i in result['data']:
                app_data.update({i['psk']: i})
            result['data'] = app_data
        return result

    def list(self):
        """
        List application data about all the native applications stored in the EASE database for the authenticated
        user’s organization.

        :return: Dict with key:value pairs of the app psk and it's metadata. For example: {123:{METADATA}}
        """
        url = '%s/v1/applications/' % self.region['Python Web Services']
        r = self.session.get(url)
        result = response_check(r, 'applications')
        # if result['status'] == 200:
        #     app_data = {}
        #     for i in result['result']:
        #         app_data.update({i['psk']: i})
        #     result['result'] = app_data
        return result

    def usage(self, psk, start_date, end_date):
        """
        List download and usage count for a specific app

        :param psk: Unique ID for the app.
        :param start_date: Start date for the statistical period. For example: 2014-01-15
        :param end_date: End date for the statistical period. For example: 2014-01-30
        :return:Returns Download Count and Usage Count for an application during a specified statistical time period.
        """
        url = '%s/v1/applications/%s/stats?start_date=%s&end_date=%s' % \
              (self.region['Python Web Services'], str(psk), start_date, end_date)
        r = self.session.get(url)
        result = response_check(r, 'app_stats')
        return result

    def info(self, psk):
        """
        List data for a specific app

        :param psk: Unique ID of the app
        :return: Returns dict of metadata about the specified application. Specify the app with app_psk.
        """
        url = '%s/v1/applications/%s' % (self.region['Python Web Services'], str(psk))
        r = self.session.get(url)
        result = response_check(r, 'application')
        return result

    def toggle(self, app_psk, state):
        """
        Allows you do enable or disable and app in your account.

        :param app_psk: Unique ID of the app. Use the app_list_available() method
        :param state: Boolean Value of desired state of the app
        :return: Dict of request status
        """
        url = '{}/v1/applications/{}'.format(self.region['Python Web Services'], app_psk)
        r = self.session.put(url, data=json.dumps({'enabled': state}))
        result = response_check(r, 'update_application_result')
        return result
