# coding=utf-8
import json
import bench


class Users(bench.Bench):
    def __init__(self, region):
        bench.Bench.__init__(self, region)

    def add(self, data):
        """
        Must be authenticated as an EASE admin. Adds a new user to the EASE organization of the authenticated user.

        :param data: a dict of the user details you want to add.
        :return: A successful response provides a unique key (user_psk) for the user.
        """
        url = '%s/v1/users' % self.region['Python Web Services']
        r = self.py_session.post(url, data=json.dumps(data))
        result = Users.response_check(r, 'user_psk')
        return result

    def info(self, psk):
        """
        Returns information stored in the database about a user, such as user ID, email, phone number,
        and the date when the user was created.

        :param psk: Unique ID assigned to the user you want to look up
        :return: Returns a dict with the target user's details
        """
        url = '%s/v1/users/%s' % (self.region['Python Web Services'], psk)
        r = self.py_session.get(url)
        result = Users.response_check(r, 'user')
        return result

    def list(self):
        """
        Lists user details for every user in the org you are authenticated to. must be admin user to run

        :return: Returns a list of dicts. Dict keys are: psk, first_name, last_name, modified_date, deleted, email,
        mobile_phone, role, created_date, until_date, disabled_reason, id, last_login_from_catalog
        """
        url = '%s/users' % self.region['Python Web Services']
        r = self.py_session.get(url)
        result = Users.response_check(r, 'users')
        return result

    def delete(self, psk):
        """
        Deletes a user from your EASE organization. A deleted user can no longer access the App Catalog or the EASE
        Portal. If a deleted user tries to log in, the user will see a message that advises the user to contact support.

        :param psk: psk of the user to be deleted
        :return: returns "ok", "auth", or the error message
        """
        url = '%s/users/%s' % (self.region['Python Web Services'], psk)
        r = self.py_session.delete(url)
        result = Users.response_check(r, 'delete_user_response')
        return result

    def update(self, psk, payload):
        """
        Updates the following data attributes for a user in your EASE organization: email, password, first_name,
        last_name, phone.

        When you request this resource, you will need to provide the user_psk value assigned when you added the user.

        :param psk: Unique ID assigned to the user by EASE.
        :param payload: a dict with the following keys: email, password, first_name, last_name, phone
        :return: Dict with status and result of True/False
        """
        url = '%s/v1/users/%s' % (self.region['Python Web Services'], psk)
        r = self.py_session.put(url, data=json.dumps(payload), headers={"Content-Type": "application/json"})
        result = Users.response_check(r, 'update_user_success')
        return result
