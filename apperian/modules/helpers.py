import logging


def region_options(data):
    options, valid, choice = [], False, ''
    for key, value in enumerate(data):
        print "    %s. %s" % (key+1, value)
        options.append(value)

    while not valid:
        try:
            choice = int(raw_input('\nEnter number of region to use > '))
            if 0 < choice <= len(options):
                valid = True
                choice -= 1
            else:
                print 'Please select a valid option between 1 and {}'.format(len(options))
        except ValueError:
            print "Please enter a number."

    return data[options[choice]]


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
