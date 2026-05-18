# ----------------------------------------------------------------------------------------------------------------------
#  Copyright (c) 2022-2025 Dimitri Kroon.
#  See LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt
# ----------------------------------------------------------------------------------------------------------------------
import sys
import time
import os
import json

import requests
import xbmcaddon
import xbmcvfs
import xbmcgui

from .errors import *


SESS_DATA_VERS = 2

TXT_INVALID_EMAIL_OR_PASSW = 30616
TXT_LOGIN_FORBIDDEN = 30617
WEB_TIMEOUT = (3.5, 7)


class ItvSession:
    def __init__(self):
        self.account_data = {}
        profile = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
        self.sess_file_path = os.path.join(profile, "itv_session")
        os.makedirs(profile, exist_ok=True)
        self.read_account_data()

    @property
    def access_token(self):
        """Return the cached access token
        """
        try:
            if self.account_data['refreshed'] < time.time() - 4 * 3600:
                self.refresh()
            return self.account_data['itv_session']['access_token']
        except (KeyError, TypeError):
            xbmcgui.Dialog().ok('Error', "Invalid session data\nCopy the file 'itv_session' from viwx to this addon")
            sys.exit(1)

    def read_account_data(self):
        try:
            with open(self.sess_file_path, 'r') as f:
                acc_data = json.load(f)
            self.account_data = acc_data
        except (FileNotFoundError, json.JSONDecodeError):
            xbmcgui.Dialog().ok('Error',
                                "Missing, or invalid account info\nCopy the file 'itv_session' from viwx to this addon")
            sys.exit(1)

    def save_account_data(self):
        data_str = json.dumps(self.account_data)
        with open(self.sess_file_path, 'w') as f:
            f.write(data_str)

    def refresh(self):
        """Refresh tokens.
        Perform a get request with the current renew token in the param string. ITV hub will
        return a json formatted string containing a new access token and a new renew-token.

        """
        try:
            token = self.account_data['itv_session']['refresh_token']
            # Refresh requests require no authorization header and no cookies at all
            resp = requests.get(
                'https://auth.prd.user.itv.com/token',
                params={'refresh': token},
                headers={'Accept': 'application/vnd.user.auth.v2+json',
                         'origin': 'https://app.10ft.itv.com',
                         'referer': 'https://app.10ft.itv.com/',
                         },
                timeout=WEB_TIMEOUT
            )
            new_tokens = resp.json()
            session_data = self.account_data['itv_session']
            session_data.update(new_tokens)
            self.account_data['refreshed'] = time.time()
            self.save_account_data()
            return True
        except (KeyError, ValueError, HttpError, TypeError) as e:
            xbmcgui.Dialog().ok('Account error', f'Failed to refresh access token:\n{e}.')
        sys.exit(1)


def itv_session():
    sess = getattr(itv_session, 'sess_obj', None)
    if sess is None:
        itv_session.sess_obj = sess = ItvSession()
    return sess
