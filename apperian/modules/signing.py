# coding=utf-8
import json
from helpers import response_check


class Sign:
    def __init__(self, session, region):
        self.session = session
        self.base = '{}/v1/applications'.format(region['Python Web Services'])

    def upload(self, platform):
        pass
        # if platform == 1:
        #     data = {
        #         "jsonrpc": "2.0",
        #         "id": 1,
        #         "method": "com.apperian.eas.credentials.create",
        #         "params": {
        #             "token": auth_token,
        #             "orgPsk": self.orgpsk,
        #             "description": test cred,
        #             "platform": str(platform),
        #             "identity": IDENTITY,
        #             "expirationdate": "2040-04-01 00:00:00",
        #             "p12filename": p12filename,
        #             "p12file": b64file,
        #             "nameprovisioningprofile": mobileprovfilename,
        #             "mobileprovisionfilename": mobileprovfilename,
        #             "mobileprovisionfile": b64mobileprovfile,
        #             "is_passwordstored": "true"}
        #     }
        # else:
        #     data = "jsonrpc": "2.0",
        #                 "id": 1,
        #                 "method": "com.apperian.eas.credentials.create",
        #                 "params": {
        #                     "token": "auth_token ,
        #                     "orgPsk": self.orgpsk
        #                     "description": "test cred",
        #                     "platform": str(self.platform)
        #                     "identity": "IDENTITY ,
        #                     "expirationdate": "2040-04-01 00:00:00",
        #                     "p12filename": "p12filename ,
        #                     "p12file": "b64file ,
        #                     "password": "str(self.cred_pass) ,
        #                     "is_passwordstored": true
        #                 }
        #             }
