
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
    for prgm in ({'programme': 'Secret Service', 'url': 'https://magni.itv.com/playlist/itvonline/ITV/10_3104_0001.001'},
                 {'programme': 'The Patient', 'url': 'https://magni.itv.com/playlist/itvonline/ITV/10_7483_0001.001'}):
        for device in ('linux_web', 'win_web', 'freesat', 'freeview', 'virginmedia', 'androidtv'):
            mnu_item = xbmcgui.ListItem(' - '.join((prgm['programme'], device)))
            mnu_item.setProperty('IsPlayable', 'true')
            callb_url = build_url('list_video', device=device, **prgm)
            xbmcplugin.addDirectoryItem(plugin_handle, callb_url, mnu_item, True)
    xbmcplugin.setContent(plugin_handle, 'videos')
    xbmcplugin.endOfDirectory(plugin_handle)


def list_video(device, programme, url):
    log(f'Showing video for {programme} on device {device}')
    for name, callb, params in (
        (f'{programme} ({device}, native)', 'play', {'device': device}),
        (f'{programme} ({device}, pr-dvb, pr)', 'play', {'feature_set': 'pr_dvb'}),
        (f'{programme} ({device}, pr-dvb, wv)', 'play', {'feature_set': 'pr_dvb', 'drm': 'wv'}),
        (f'{programme} ({device}, pr-mpeg, pr)', 'play', {'feature_set': 'pr_mpeg', 'drm': 'pr'}),
        (f'{programme} ({device}, pr-mpeg, wv)', 'play', {'feature_set': 'pr_mpeg', 'drm': 'wv'}),
        (f'{programme} ({device}, wv-dvb, wv)', 'play', {'feature_set': 'wv_dvb', 'drm': 'wv'}),
        (f'{programme} ({device}, wv-mpeg, wv)', 'play', {'feature_set': 'wv_mpeg', 'drm': 'wv'})
    ):
        mnu_item = xbmcgui.ListItem(name)
        mnu_item.setProperty('IsPlayable', 'true')
        mnu_item.setIsFolder(False)
        mnu_item.setArt({'thumb': os.path.join(ADDON_PATH, 'resources/icon.png')})

        params.update({
            'programme': programme,
            'device': device
        })
        callb_url = build_url(callb, url=url, **params)
        xbmcplugin.addDirectoryItem(plugin_handle, callb_url, mnu_item, False)
    xbmcplugin.setContent(plugin_handle, 'videos')
    xbmcplugin.endOfDirectory(plugin_handle)


def play(url, device, programme, feature_set=None, drm=None, has_ad=False):
    log(f"Playing {programme} on {device}, {feature_set}/{drm} - {url}")
    from resources.lib.stream import play_vod
    li = play_vod(url, device, feature_set, drm, has_ad)
    li.setProperty('IsPlayable', 'true')
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
