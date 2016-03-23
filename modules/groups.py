# coding=utf-8
import json
import bench


class Groups(bench.Bench):
    def __init__(self, region):
        bench.Bench.__init__(self, region)
        self.region = region

    def list(self):
        """
        list of all the groups for the authenticated user’s organization. This list includes the number of users
        and number of applications belonging to each group.

        :return: List of dicts of the groups. Dict keys are: app_count, psk, user_count, name, description

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '%s/v1/groups/' % self.region['Python Web Services']
        r = self.py_session.get(url)
        result = Groups.response_check(r, 'groups')
        return result

    def add(self, data):
        """
        Adds a new group to the authenticated user’s organization.

        :param data: Dict with metadata for group. Required keys are: group_name, group_description
        :return: Dict of new groups details. Dict keys are: psk, name, description

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '%s/v1/groups/' % self.region['Python Web Services']
        payload = json.dumps(data)
        r = self.py_session.post(url, data=payload)
        result = Groups.response_check(r, 'group')
        return result

    def list_apps(self, group_psk):
        """
        Returns a list of the applications that are in the specified group.

        :param group_psk: Unique ID assigned by EASE to the group.
        :return: List of dicts. See API docs for dict keys

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '{}/v1/groups/{}'.format(self.region['Python Web Services'], group_psk)
        r = self.py_session.get(url)
        result = Groups.response_check(r, 'applications')
        return result

    def add_apps(self, group_psk, app_list):
        """
        Adds applications to a specified group. Specify apps by app_psk.

        :param group_psk: Unique ID assigned by EASE to the group.
        :param app_list: Comma-separated list of the app_psks for the applications you want to add to the group.
        :return: Dict of lists. Dict keys are: apps_added, apps_failed
        """
        url = '{}/v1/groups/{}/applications'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({"app_psk": app_list})
        r = self.py_session.post(url, data=payload)
        result = Groups.response_check(r, 'response')
        return result

    def delete_apps(self, group_psk, app_list):
        """
        Removes applications from a group. Specify apps by app_psk

        :param group_psk: Unique ID assigned by EASE to the group.
        :param app_list: Comma-separated list of the app_psks for the applications you want to remove from the group.
        :return: Dict of lists. Dict keys are: apps_removed, apps_failed
        """
        url = '{}/v1/groups/{}/applications'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({"app_psk": app_list})
        r = self.py_session.delete(url, data=payload)
        result = Groups.response_check(r, 'response')
        return result

    def list_members(self, group_psk):
        """
        Lists users who are members of a specified group.

        :param group_psk: Unique ID assigned by EASE to the group.
        :return: List of Dicts. See API docs for dict keys

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '{}/v1/groups/{}/users/'.format(self.region['Python Web Services'], group_psk)
        r = self.py_session.get(url)
        result = Groups.response_check(r, 'users_in_group')
        return result

    def add_member(self, user_psk, groups):
        """
        Adds a specified user to a list of groups. Specify groups by group_psk.

        :param user_psk: Unique ID assigned by EASE to the user you want to add to the list of groups
        :param groups: Comma-separated list of the group psks
        :return:Dict of lists. Dict keys are: added_groups, failed_groups

        https://apidocs.apperian.com/v1/groups.html
        """
        url = '{}/v1/groups/users/{}'.format(self.region['Python Web Services'], user_psk)
        payload = json.dumps({"group_psk": groups})
        r = self.py_session.get(url, data=payload)
        result = Groups.response_check(r, 'response')
        return result

    def add_users(self, users, groups):
        try:
            user_is_list = users[1]
        except IndexError:
            user_is_list = False

        try:
            group_is_list = groups[0]
        except IndexError:
            group_is_list = False

        if group_is_list and user_is_list:
            result = {'status': 200}
            for i in groups:
                resp = Groups.add_members(self, i, users)
                result[i] = resp['result']
        elif group_is_list:
            result = Groups.add_member(self, users, groups)
        elif user_is_list:
            result = Groups.add_members(self, users, groups)
        else:
            result = {'status': 500, 'reuslt': 'Incorrect parameters passed'}

        return result

    def add_members(self, group_psk, user_list):
        """
        Adds a list of users to a specified group. Specify users by user_psk.

        :param group_psk: Unique ID assigned by EASE to the group.
        :param user_list: Comma-separated list of the user_psks for the users you want to add to the group.
        :return: Dict of lists. Dict keys are: users_failed, users_added
        """
        url = '{}/v1/groups/{}/users'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({"user_psk": user_list})
        r = self.py_session.get(url, data=payload)
        result = Groups.response_check(r, 'response')
        return result

    def remove_members(self, group_psk, user_list):
        """
        Removes applications from a group. Specify apps by app_psk

        :param group_psk: Unique ID assigned by EASE to the group.
        :param user_list: Comma-separated list of the app_psks for the applications you want to remove from the group.
        :return: Dict of lists. Dict keys are: users_failed, users_removed
        """
        url = '{}/v1/groups/{}/users'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({"user_psk": user_list})
        r = self.py_session.delete(url, data=payload)
        result = Groups.response_check(r, 'response')
        return result

    def update(self, group_psk, data):
        """
        Updates data for an existing group in the authenticated user's organization.

        :param group_psk: Unique ID assigned by EASE to the group.
        :param data: Dict of group metadata to change. Required keys: group_name, group_description
        :return: Dict with updated metadata. Dict keys are: psk, name, description
        """
        url = '{}/v1/groups/{}'.format(self.region['Python Web Services'], group_psk)
        payload = json.dumps({data})
        r = self.py_session.put(url, data=payload)
        result = Groups.response_check(r, 'group')
        return result

    def delete(self, group_psk):
        """
        Permanently deletes a group from the authenticated user’s organization.

        :param group_psk: Unique ID assigned by EASE to the group.
        :result: Dict with deleted groups metadata. Dict keys are: psk, name, description
        """
        url = '{}/v1/groups/{}'.format(self.region['Python Web Services'], group_psk)
        r = self.py_session.delete(url)
        result = Groups.response_check(r, 'deleted_group')
        return result
