
#  Copyright (c) 2022 Dimitri Kroon.
#
#  SPDX-License-Identifier: GPL-2.0-or-later

import os
import sys
import inspect

from urllib.parse import parse_qsl, urlencode

import xbmc
import xbmcaddon
import xbmcplugin
import xbmcgui


ADDON = xbmcaddon.Addon()
ADDON_PATH = ADDON.getAddonInfo('path')


def log(message):
    xbmc.log('[ITV_TEST_STREAMS] ' + message, xbmc.LOGDEBUG)


def build_url(callb, **kwargs):
    kwargs['callb'] = callb
    qs = urlencode(kwargs)
    return '{}?{}'.format(plugin_url, qs)


def menu():
    log(f'Showing main menu')
    for device in ('linux_web', 'win_web', 'freesat', 'freeview', 'virginmedia', 'androidtv'):
        mnu_item = xbmcgui.ListItem(device)
        mnu_item.setProperty('IsPlayable', 'true')
        callb_url = build_url('list_video', device=device)
        xbmcplugin.addDirectoryItem(plugin_handle, callb_url, mnu_item, True)
    xbmcplugin.setContent(plugin_handle, 'videos')
    xbmcplugin.endOfDirectory(plugin_handle)


def list_video(device):
    log(f'Showing video for device {device}')
    url = 'https://magni.itv.com/playlist/itvonline/ITV/10_3104_0001.001'
    for name, callb, params in (
        (f'Secret Service ({device}, native)', 'play', {'device': device}),
        (f'Secret Service ({device}, pr-dvb, pr)', 'play', {'device': device, 'feature_set': 'pr_dvb'}),
        (f'Secret Service ({device}, pr-dvb, wv)', 'play', {'device': device, 'feature_set': 'pr_dvb', 'drm': 'wv'}),
        (f'Secret Service ({device}, pr-mpeg, pr)', 'play', {'device': device, 'feature_set': 'pr_mpeg', 'drm': 'pr'}),
        (f'Secret Service ({device}, pr-mpeg, wv)', 'play', {'device': device, 'feature_set': 'pr_mpeg', 'drm': 'wv'}),
        (f'Secret Service ({device}, wv-dvb, wv)', 'play', {'device': device, 'feature_set': 'wv_dvb', 'drm': 'wv'}),
        (f'Secret Service ({device}, wv-mpeg, wv)', 'play', {'device': device, 'feature_set': 'wv_mpeg', 'drm': 'wv'})
    ):
        mnu_item = xbmcgui.ListItem(name)
        mnu_item.setProperty('IsPlayable', 'true')
        mnu_item.setArt({'thumb': os.path.join(ADDON_PATH, 'resources/icon.png')})

        callb_url = build_url(callb, url=url, **params)
        xbmcplugin.addDirectoryItem(plugin_handle, callb_url, mnu_item, False)
    xbmcplugin.setContent(plugin_handle, 'videos')
    xbmcplugin.endOfDirectory(plugin_handle)


def play(url, device, feature_set=None, drm=None, has_ad=False):
    log(f"Playing {device}, {feature_set} - {url}")
    from resources.lib.stream import play_vod
    li = play_vod(url, device, feature_set, drm, has_ad)
    xbmcplugin.setResolvedUrl(plugin_handle, True, listitem=li)


def route():
    params = dict(parse_qsl(sys.argv[2][1:]))
    func_name = params.pop('callb', '')
    funcs = {name: member for name, member in inspect.getmembers(sys.modules[__name__])
             if (inspect.isfunction(member))}
    callb = funcs.get(func_name)
    if callb:
        callb(**params)
    else:
        menu()


if __name__ == '__main__':
    plugin_url = sys.argv[0]
    plugin_handle = int(sys.argv[1])
    route()
