# coding=utf-8
import json
import time
import datetime
from helpers import response_check, php_token


class Wrapper:
    def __init__(self, php_session, php_payload, app_obj, region, user_psk):
        self.session = php_session
        self.payload = php_payload
        self.user_psk = user_psk
        self.app_obj = app_obj
        self.region = region
        self.session.headers.update({'X-Ds-Client-Type': 9, 'X-HTTP-Token': php_token})
        # headers['Content-Type'] = 'application/json'

    def wrap_app(self, policies, psk):
        resp = self.app_obj.get_details(psk)
        version_psk = resp['result']['version']['psk']
        converted_policies = Wrapper.convert_policies(policies)
        dynamic_policy_info = Wrapper.gen_dynamic_policy_info(self, converted_policies, psk, version_psk)
        wrapper_status = Wrapper.get_status(self, psk)
        print wrapper_status
        wrapper_version = wrapper_status['apperian_wrapper_info']['wrapper_version']
        params = {
            'appPsk': psk,
            'data': converted_policies,
            'dynamicPolicyInfo': dynamic_policy_info,
            'apperianWrapperVersion': wrapper_version,
            'userPsk': self.user_psk,
            'pythonAuthToken': self.payload['params']['token']
        }
        # params['pythonAuthToken'] = web_svc.auth_token
        self.payload['params'].update(params)
        self.payload['method'] = 'com.apperian.eas.apps.wrapappasync'
        self.session.post(self.region['PHP Web Services'], data=json.dumps(self.payload))

        message = {
            -1: "Error applying policies",
            0: "Wrapping completed, no policies applied",
            1: "Policies applied",
            2: "Wrapping in progress...",
            3: "Wrapping completed, pending signing",
            4: "Wrapping completed, no policies applied"}

        done_wrapping = False

        while not done_wrapping:
            wrap_status_result = Wrapper.get_status(self, psk)
            ts = time.time()
            st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            if wrap_status_result['ver_status'] in [1, 2]:
                pass
            elif wrap_status_result['ver_status'] in [3, 4]:
                done_wrapping = True
            else:
                break

            print("{0}: {1}".format(st, message[wrap_status_result['ver_status']]))
            if not done_wrapping:
                time.sleep(10)

        if done_wrapping:
            return {'status': 200, 'result': message[wrap_status_result['ver_status']]}
        else:
            return {'status': 500, 'result': message[wrap_status_result['ver_status']]}

    @staticmethod
    def convert_policies(policies):
        conversion = {
            0: 'ibm_vpn',
            1: 'data_in_use',
            2: 'data_at_rest',
            3: 'rootprotection',
            4: 'encrypted_checksum_validation',
            5: 'security_settings_check',
            6: 'versioncontrol',
            7: 'iprestriction',
            8: 'log_blocking',
            9: 'vpn_config',
            10: 'checksum_validation',
            11: 'dynamicauth',
            12: 'datawipe',
            13: 'app_usage',
            14: 'crash_log',
            15: 'emm_compliance',
            16: 'device_mdm'
        }
        policy_list = {
            'ibm_vpn': 0,
            'data_in_use': 0,
            'data_at_rest': 0,
            'vpn_config': 0,
            'rootprotection': 0,
            'security_settings_check': 0,
            'iprestriction': 0,
            'log_blocking': 0,
            'checksum_validation': 0,
            'encrypted_checksum_validation': 0,
            'dynamicauth': 0,
            'datawipe': 0,
            'app_usage': 0,
            'crash_log': 0,
            'versioncontrol': 0,
            'emm_compliance': 0,
            'device_mdm': 0,
            'remotecontrol': 0,
            'copypaste': 0,
            'dar': 0,
            'jailbreak': 0,
            'geofencing': None,
            'pin': None,
            'expiration': None,
            'fakeloc': None,
            'vpn': None,
            'lockout': None,
            'appfederation': None,
            'smartfirewall': None
        }
        for i in policies:
            if policy_list[conversion[i]] == 0:
                policy_list[conversion[i]] = 1
            else:
                policy_list[conversion[i]] = True

        return policy_list

    def gen_dynamic_policy_info(self, policies, app_psk, version_psk):
        r = self.session.get('{}/policies/dynamic/policy/version/{}'.format(
            self.region['PHP Web Services'], version_psk))
        policy_response = response_check(r)
        if policy_response['status'] == 200:
            policy_response = policy_response['result']

        policy_name = "MyDynamicPolicy_appPsk{0}".format(app_psk)

        policy_description = "Placeholder description for app psk {0}".format(app_psk)
        rules = []

        if 'policies' not in policy_response:
            new_policy = True
        elif len(policy_response['policies']) > 0:
            new_policy = False
        else:
            new_policy = True

        policy_keys = {}

        if 'policies' not in policy_response:
            current_rules = []
        elif len(policy_response['policies']) > 0:
            current_rules = policy_response['policies'][0]['rules']
        else:
            current_rules = []

        # Hardcoded rule name for now, in the future it will be customizable by the admin
        rule_names = {
            'dynamicauth': "Enterprise SSO",
            'remotecontrol': "Remote Control",
            'datawipe': "Datawipe",
            'app_usage': "App Usage",
            'versioncontrol': "Version Control",
            'emm_compliance': "EMM Compliance",
            'crash_log': "Crash Log Collection",
            'checksum_validation': "Checksum Validation",
            'ibm_vpn': "IBM VPN",
            'data_in_use': "Data In Use",
            'data_at_rest': "Data At Rest",
            'vpn_config': "VPN Config",
            'iprestriction': "IP Restriction",
            'rootprotection': "Root Protection",
            'security_settings_check': "Security Settings Check",
            'log_blocking': "Log Blocking",
            'encrypted_checksum_validation': "Encrypted Checksum Validation",
            'device_mdm': "Device MDM"
        }

        if not new_policy:
            policy_keys = {y[0]: x for x in current_rules for y in rule_names.iteritems() if x['name'] == y[1]}

        action_prefix = 'com.apperian.'

        # Dynamic Auth policy
        if policies['dynamicauth'] == 1:
            operation_pattern = "(facts['com.apperian.user.authenticated'])"
            actions_success = [{'id': "{0}keepcalmandcarryon.lol".format(action_prefix), 'params': ''}]
            actions_fail = [{'id': "{0}authenticate".format(action_prefix), 'params': ''}]
            dynamicauth_rule = {'name': rule_names['dynamicauth'],
                                'operationpattern': operation_pattern,
                                'description': 'Require user authentication for app access.',
                                'actions': {'onsuccess': actions_success,
                                            'onfail': actions_fail}, 'ruleparams': {}}
            if 'dynamicauth' in policy_keys:
                dynamicauth_rule['psk'] = policy_keys['dynamicauth']['psk']
            rules.append(dynamicauth_rule)

        # Remote Control Policy
        if policies['remotecontrol'] == 1:
            operation_pattern = "(true)"
            actions_success = [{'id': "{0}remotecontrol".format(action_prefix), 'params': ''}]
            actions_fail = [{'id': "{0}keepcalmandcarryon.lol".format(action_prefix), 'params': ''}]
            remotecontrol_rule = {'name': rule_names['remotecontrol'],
                                  'operationpattern': operation_pattern,
                                  'description': 'Turn remote control listening on for the app.',
                                  'actions': {'onsuccess': actions_success,
                                              'onfail': actions_fail}, 'ruleparams': {}}
            if 'remotecontrol' in policy_keys:
                remotecontrol_rule['psk'] = current_rules[policy_keys['remotecontrol']]['psk']
            rules.append(remotecontrol_rule)

        # Datawipe Policy
        if policies['datawipe'] == 1:
            operation_pattern = "(facts['com.apperian.application.datawipe'])"
            actions_success = [{'id': "{0}datawipe".format(action_prefix), 'params': ''}]
            actions_fail = [{'id': "{0}keepcalmandcarryon.lol".format(action_prefix), 'params': ''}]
            datawipe_rule = {'name': rule_names['datawipe'],
                             'operationpattern': operation_pattern,
                             'description': 'Wipes all data from an application if requested by an administrator.',
                             'actions': {'onsuccess': actions_success, 'onfail': actions_fail}, 'ruleparams': {}}
            if 'datawipe' in policy_keys:
                datawipe_rule['psk'] = current_rules[policy_keys['datawipe']]['psk']
            rules.append(datawipe_rule)

        # App Usage Policy
        if policies['app_usage'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': "{0}appusage".format(action_prefix), 'params': ''}]
            actions_fail = [{'id': "{0}keepcalmandcarryon.lol".format(action_prefix), 'params': ''}]
            app_usage_rule = {'name': rule_names['app_usage'],
                              'operationpattern': operation_pattern,
                              'description': 'Tracks the application usage.',
                              'actions': {'onsuccess': actions_success, 'onfail': actions_fail}, 'ruleparams': {}}
            if 'app_usage' in policy_keys:
                app_usage_rule['psk'] = policy_keys['app_usage']['psk']
            rules.append(app_usage_rule)

        # IBM VPN Policy
        if policies['ibm_vpn'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}ibmvpn'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            ibm_vpn_usage_rule = {'name': rule_names['ibm_vpn'],
                                  'operationpattern': operation_pattern,
                                  'description': 'Facilitates IBM VPN',
                                  'actions': {'onsuccess': actions_success, 'onfail': actions_fail}, 'ruleparams': {}}
            if 'ibm_vpn' in policy_keys:
                ibm_vpn_usage_rule['psk'] = policy_keys['ibm_vpn']['psk']
            rules.append(ibm_vpn_usage_rule)

        # Data in Use Encryption policy
        if policies['data_in_use'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            data_in_use_usage_rule = {'name': rule_names['data_in_use'],
                                      'operationpattern': operation_pattern,
                                      'description': 'Protects application data in memory',
                                      'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                      'ruleparams': {}}
            if 'data_in_use' in policy_keys:
                data_in_use_usage_rule['psk'] = policy_keys['data_in_use']['psk']
            rules.append(data_in_use_usage_rule)

        # Data at Rest Encryption policy
        if policies['data_at_rest'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            data_at_rest_usage_rule = {'name': rule_names['data_at_rest'],
                                       'operationpattern': operation_pattern,
                                       'description': 'Protects application data on disk',
                                       'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                       'ruleparams': {}}
            if 'data_at_rest' in policy_keys:
                data_at_rest_usage_rule['psk'] = policy_keys['data_at_rest']['psk']
            rules.append(data_at_rest_usage_rule)

        # VPN Configuration Policy
        if policies['vpn_config'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            vpn_config_usage_rule = {'name': rule_names['vpn_config'],
                                     'operationpattern': operation_pattern,
                                     'description': 'Configures VPN Apps',
                                     'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                     'ruleparams': {}}
            if 'vpn_config' in policy_keys:
                vpn_config_usage_rule['psk'] = policy_keys['vpn_config']['psk']
            rules.append(vpn_config_usage_rule)

        # IP Restriction Policy
        if policies['iprestriction'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            iprestriction_usage_rule = {'name': rule_names['iprestriction'],
                                        'operationpattern': operation_pattern,
                                        'description': 'Set IP Restrictions',
                                        'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                        'ruleparams': {}}
            if 'iprestriction' in policy_keys:
                iprestriction_usage_rule['psk'] = policy_keys['iprestriction']['psk']
            rules.append(iprestriction_usage_rule)

        # Root Protection Policy
        if policies['rootprotection'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            rootprotection_usage_rule = {'name': rule_names['rootprotection'],
                                         'operationpattern': operation_pattern,
                                         'description': 'Prevents rooted devices from running the app',
                                         'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                         'ruleparams': {}}
            if 'rootprotection' in policy_keys:
                rootprotection_usage_rule['psk'] = policy_keys['rootprotection']['psk']
            rules.append(rootprotection_usage_rule)

        # Security Settings Check
        if policies['security_settings_check'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            security_settings_check_usage_rule = {'name': rule_names['security_settings_check'],
                                                  'operationpattern': operation_pattern,
                                                  'description': 'Ensures certain device-level settings are enabled',
                                                  'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                                  'ruleparams': {}}
            if 'security_settings_check' in policy_keys:
                security_settings_check_usage_rule['psk'] = policy_keys['security_settings_check']['psk']
            rules.append(security_settings_check_usage_rule)

        # Log Blocking Policy
        if policies['log_blocking'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            log_blocking_usage_rule = {'name': rule_names['log_blocking'],
                                       'operationpattern': operation_pattern,
                                       'description': 'Prevents app from writing data to the system log',
                                       'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                       'ruleparams': {}}
            if 'log_blocking' in policy_keys:
                log_blocking_usage_rule['psk'] = policy_keys['log_blocking']['psk']
            rules.append(log_blocking_usage_rule)

        # EMM Compliance Policy
        if policies['emm_compliance'] == 1:
            # if status is 1 run the app and do nothiing, else quit the app
            operation_pattern = "(facts['com.apperian.emmcompliance.status'] == 1)"
            actions_success = [{"id": '{0}keepcalmandcarryon.lol'.format(action_prefix), "params": ''}]
            actions_fail = [{"id": "{0}emmcompliance".format(action_prefix), "params": ''}]
            emm_compliance_rule = {"name": rule_names['emm_compliance'],
                                   "operationpattern": operation_pattern,
                                   "description": "Makes sure the app only runs when device is EMM Comnpliance.",
                                   "actions": {"onsuccess": actions_success, "onfail": actions_fail},
                                   "ruleparams": {}}
            if "emm_compliance" in policy_keys:
                emm_compliance_rule["psk"] = policy_keys["emm_compliance"]["psk"]
            rules.append(emm_compliance_rule)

        # Crash log policy
        if policies['crash_log'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}sendcrashlog'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            crash_log_rule = {'name': rule_names['crash_log'],
                              'operationpattern': operation_pattern,
                              'description': 'Sends the latest crash data',
                              'actions': {'onsuccess': actions_success, 'onfail': actions_fail}, 'ruleparams': {}}
            if 'crash_log' in policy_keys:
                crash_log_rule['psk'] = policy_keys['crash_log']['psk']
            rules.append(crash_log_rule)

        # Checksum validation policy
        if policies['checksum_validation'] == 1:
            operation_pattern = "(facts['com.apperian.apps.clientchecksumvalue'] === facts['com.apperian.apps." \
                                "checksumvalue']) || facts['com.apperian.apps.checksumvalue'] === 0"
            # on success we "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}sendchecksummismatch'.format(action_prefix), 'params': ''}]
            checksum_validation_rule = {'name': rule_names['checksum_validation'],
                                        'operationpattern': operation_pattern,
                                        'description': 'Informs the server that there has been a checksum mismatch',
                                        'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                        'ruleparams': {}}
            if 'checksum_validation' in policy_keys:
                checksum_validation_rule['psk'] = policy_keys['checksum_validation']['psk']
            rules.append(checksum_validation_rule)

        # Encrypted checksum validation policy
        if policies['encrypted_checksum_validation'] == 1:
            operation_pattern = "(true)"
            # on success and failure we do the same thing which is "do nothing"
            actions_success = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            actions_fail = [{'id': '{0}keepcalmandcarryon.lol'.format(action_prefix), 'params': ''}]
            encrypted_checksum_validation_rule = {'name': rule_names['encrypted_checksum_validation'],
                                                  'operationpattern': operation_pattern,
                                                  'description': 'Informs the server that there has been a checksum mismatch with Secure Element',
                                                  'actions': {'onsuccess': actions_success, 'onfail': actions_fail},
                                                  'ruleparams': {}}
            if 'encrypted_checksum_validation' in policy_keys:
                encrypted_checksum_validation_rule['psk'] = policy_keys['encrypted_checksum_validation']['psk']
            rules.append(encrypted_checksum_validation_rule)

        # Version Control Policy
        if policies['versioncontrol'] == 1:
            # If com.apperian.application.version is undefined, this is an older version of the wrapper which doesn't
            # have the version_psk baked in. Therefore, we use what the system has. If the app has the version psk
            # baked in, always use that because it's always accurate.
            operation_pattern = "((typeof(facts['com.apperian.application.version']) === 'undefined' \
                                && facts['com.apperian.apps.installedversion'] !== -1 && facts['com.apperian.apps.latestversion'] > facts['com.apperian.apps.installedversion'])\
                                || (facts['com.apperian.apps.latestversion'] > facts['com.apperian.application.version']))"
            actions_fail = [{"id": '{0}keepcalmandcarryon.lol'.format(action_prefix), "params": ''}]
            actions_success = [{"id": '{0}update'.format(action_prefix), "params": ''}]
            versioncontrol_rule = {"name": rule_names['versioncontrol'], "operationpattern": operation_pattern,
                                   "description": 'Check whether the application is up to date.',
                                   "actions": {"onsuccess": actions_success,
                                               "onfail": actions_fail},
                                   "ruleparams": {}}
            if 'versioncontrol' in policy_keys:
                versioncontrol_rule['psk'] = policy_keys['versioncontrol']['psk']
            rules.append(versioncontrol_rule)

        # Device MDM Policy
        if policies['device_mdm'] == 1:
            operation_pattern = "(facts['com.apperian.device.mdm_enrolled'])"
            actions_success = [{'id': "{0}keepcalmandcarryon.lol".format(action_prefix), 'params': ''}]
            actions_fail = [{
                'id': "{0}block".format(action_prefix),
                'params': '{"block_reason": "This device is not enrolled in MDM. Contact your administrator to enroll your device so you can run this app."}'
            }]
            device_mdm_rule = {'name': rule_names['device_mdm'],
                               'operationpattern': operation_pattern,
                               'description': 'Makes sure the app only runs when device is under any MDM Enrollment.',
                               'actions': {'onsuccess': actions_success, 'onfail': actions_fail}, 'ruleparams': {}}
            if 'device_mdm' in policy_keys:
                device_mdm_rule['psk'] = policy_keys['device_mdm']['psk']
            rules.append(device_mdm_rule)

        policy_op_pattern = Wrapper.format_policies(rules)

        return_policy_info = {'action': '', 'policy_data': None}

        try:
            policy_psk = policy_response.get('policies')[0].get('psk')
        except (IndexError, TypeError):
            policy_psk = None

        if len(rules) == 0:
            # if nothing is set now and nothing was set before, do nothing, we aren't changing
            # any policies
            if new_policy:
                return_policy_info['action'] = 'nothing'
            else:
                # Rules were set before, now nothing, therefore delete
                return_policy_info['action'] = 'delete'
                return_policy_info['policy_data'] = {'versionpsk': version_psk, 'policy_psk': policy_psk}
        # if new policy, don't pass any policy_psk as this constitutes a create
        elif new_policy:
            return_policy_info['action'] = 'save'
            return_policy_info['policy_data'] = {'name': policy_name,
                                                 'versionpsk': version_psk,
                                                 'description': policy_description,
                                                 'operationpattern': policy_op_pattern, 'rules': rules}
        # this is updating a policy, we reuse the existing policy_psk, and save all changes
        else:
            return_policy_info['action'] = 'save'
            return_policy_info['policy_data'] = {'policy_psk': policy_psk,
                                                 'name': policy_name,
                                                 'versionpsk': version_psk,
                                                 'description': policy_description,
                                                 'operationpattern': policy_op_pattern, 'rules': rules}
        return {'policy_data': return_policy_info}

    @staticmethod
    def format_policies(rules):
        # Takes in an array of rule objects, each containing the 'name' key, and
        # returns a string of names separated by '&&' symbols. This is how
        # the dynamic policy engine expects the policy operation to be defined.
        policy_op_pattern = ''
        for i, rule in enumerate(rules):
            if i != 0:
                policy_op_pattern += " && "
            policy_op_pattern += '"' + rules[i]['name'] + '"'
        return policy_op_pattern

    def get_status(self, app_psk):
        """
        :param app_psk:
        :return:
        Returns:
        JSON Dict of:
        {"success" => TRUE,
              "ver_status"  => $versionInfo['wrapstatus'],
              "ver_psk" => $versionInfo['psk'],
              "app_status" => $applicationInfo['status'],
              "apperian_wrapper_info" => $apperianWrapperInfo}
        """

        self.payload['method'] = 'com.apperian.eas.apps.getversionstatus'
        self.payload['params'].update({'appPsk': app_psk})

        resp = self.session.post(self.region['PHP Web Services'], data=json.dumps(self.payload))
        resp = response_check(resp, 'result')
        return resp['result']
