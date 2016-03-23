# coding=utf-8
import requests
import logging


class Bench(object):
    def __init__(self, region):
        self.region = region
        self.token = ''
        self.user_data = ''
        self.user = ''
        self.app = ''
        self.group = ''
        self.wrapper = ''
        self.publish = ''
        self.py_session = requests.Session()
        self.py_session.headers.update({"Content-Type": "application/json"})
        # Setup php session
        self.php_session = requests.Session()
        self.php_session.headers = {"Content-Type": "application/js"}
        self.php_payload = {"id": 1, "apiVersion": "1.0", "method": "", "jsonrpc": "2.0"}
        self.php_token = "e(PujgdDx0s3kScfctYqCBug{plur1bus^unum})"

    @staticmethod
    def display_options(data, msg, narrow=False):
        valid, choice = False, ''
        print 'Possible Regions:'
        if narrow:
            try:
                for index, value in enumerate(data):
                    print "    %s. %s" % (index+1, value[narrow])
            except KeyError:
                print 'Passed value is not a key. Select from full list'
                for index, value in enumerate(data):
                    print "    %s. %s" % (index+1, value)
        else:
            for index, value in enumerate(data):
                print "    %s. %s" % (index+1, value)

        while not valid:
            try:
                choice = int(raw_input('\nPlease select the {} you would like to use: '.format(msg)))
                if 0 < choice <= len(data):
                    valid = True
                    choice -= 1
                else:
                    print 'Please select a valid option between 1 and {}'.format(len(data))
            except ValueError:
                print "Please enter a number."

        return data[choice]

    @staticmethod
    def response_check(requests_obj, *args):
        result = {'status': requests_obj.status_code}
        logging.debug('status_code = {}'.format(result['status']))
        try:
            message = requests_obj.json()
            if 'error' in message.keys():
                logging.debug('Error found in response keys:')
                logging.debug(message)
                result['status'] = 401
                message = message['error']
            else:
                if args:
                    try:
                        for arg in args:
                            message = message[arg]
                    except KeyError:
                        logging.debug('Expected key not present in response')
                        logging.debug('Keys in response json are: {}'.format(message.keys()))
                        result['status'] = 500
        except ValueError:
            logging.debug('Unable to get json from  response')
            logging.debug(requests_obj.text)
            result['status'] = 500
            message = requests_obj.text

        result['result'] = message
        logging.debug(result)
        return result
