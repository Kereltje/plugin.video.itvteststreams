# ----------------------------------------------------------------------------------------------------------------------
#  Copyright (c) 2022-2025 Dimitri Kroon.
#  See LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt
# ----------------------------------------------------------------------------------------------------------------------

import requests
import json

from xbmcgui import ListItem

USER_AGENT = 'Mozilla/5.0 (Linux aarch64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36 OPR/46.0.2207.0 OMI/4.13.6.465.Charlie.153 HbbTV/1.5.1 (+PVR+DRM; ARRIS; FS-ARS-01B; 5; ; com.arris.FS-ARS-01;) freesat/3.0 (1.5.2) Freesat_STB_BCM72604_2'


_devices = {
    'linux_web': {
        'client': {
            'id': 'browser',
            'service': 'itv.x',
            'supportsAdPods': True,
            'version': '4.1'
        },
        'device': {
            'manufacturer': 'Firefox',
            'model': '145.0',
            'os': {
                'name': 'Linux',
                'type': 'desktop',
                'version': 'x86_64'
            }
        },
        'user': {
            'token': ''
        },
        'variantAvailability': {
            'drm': {'maxSupported': 'L3', 'system': 'widevine'},
            'featureset': ['mpeg-dash', 'widevine', 'outband-webvtt', 'hd', 'single-track'],
            'platformTag': 'dotcom',
            'player': 'dash'
        }
    },

    'win_web': {
        "client": {
            "version": "4.1",
            "id": "browser",
            "supportsAdPods": True,
            "service": "itv.x",
            "appversion": "2.474.0",
            "ssaiClientSdkVersion": "3",
            "ssaiExtraParams": {}
        },
        "device": {
            "manufacturer": "Chrome",
            "model": "146.0.0.0",
            "os": {
                "name": "Windows",
                "version": "10",
                "type": "desktop"
            },
            "deviceGroup": "dotcom"
        },
        "user": {"token": ""},
        "variantAvailability": {
            "player": "dash",
            "featureset": None,
            "platformTag": "dotcom",
            "drm": {"system": "widevine", "maxSupported": "L3"}
        }
    },

    'freeview': {
        "client": {
            "id": "freeview",
            "isp": {},
            "supportsAdPods": True,
            "appVersion": "3.564.0",
            "version": "3.564.0",
            "service": "itv.x",
            "thirdPartyPaymentModel": "free",
            "ssaiClientSdkVersion": "3"
        },
        "device": {
            "manufacturer": "LG",
            "model": "oled77g36la",
            "os": {
                "name": "oled77g36la"
            }
        },
        "user": {"token": ""},
        "variantAvailability": {
            "drm": {'maxSupported': 'L3','system': 'widevine'},
            "featureset": None,
            "platformTag": "ctv"
        }
    },

    'freesat': {
        "client": {
            "id": "freesat",
            "isp": {},
            'supportsAdPods': True,
            "appVersion": "3.760.8",
            "version": "3.760.8",
            "service": "itv.x",
            "thirdPartyPaymentModel": "free"
        },
        "device": {
            "manufacturer": "Arris",
            "model": "fs-ars-01b",
            "os": {
                "name": "fs-ars-01b"
            }
        },
        "user": {
            "token": "",
            "userGroupLabel": None
        },
        "variantAvailability": {
            "drm": {"system": "playready", "maxSupported": "SL2000"},
            "featureset": None,
            "platformTag": "ctv"
        }
    },
    'virginmedia': {
        "client": {
            "id": "virginmedia",
            "isp": {},
            "supportsAdPods": True,
            "appVersion": "3.760.8",
            "version": "3.760.8",
            "service": "itv.x",
            "thirdPartyPaymentModel": "free"
        },
        "device": {
            "manufacturer": "Humax_liberty",
            "model": "EOS-1008C",
            "os": {
                "name": "EOS-1008C"
            }
        },
        "user": {
            "token": "",
            "userGroupLabel": None
        },
        "variantAvailability": {
            "drm": {"system": "playready", "maxSupported": "SL2000"},
            "featureset": [
                "mpeg-dash",
                "playready",
                "outband-webvtt"
            ],
            "platformTag": "ctv",
        }
    }
}


_features = {
    'live': {
        "min": ["mpeg-dash", "widevine",],
        "max": ["hd", "mpeg-dash", "widevine", "inband-webvtt"]
    },
    'wv_mpeg': [
        'mpeg-dash',
        'widevine',
        'outband-webvtt',
        'hd',
        'single-track'],
    'wv_dvb': [
        'dvb-dash',
        'widevine',
        'outband-webvtt',
        'hd',
        'single-track'],
    'pr_mpeg': [
        "mpeg-dash",
        "playready",
        "outband-webvtt",
        "hd",
        "single-track",
    ],
    'pr_dvb': [
        "dvb-dash",
        "playready",
        "outband-webvtt",
        "hd",
        "single-track",
    ]
}


_drm = {
    'wv': {"system": "widevine", "maxSupported": "L3"},
    'pr': {"system": "playready", "maxSupported": "SL2000"}
}


def _request_playlist(url, device, featureset, drmtype=None, has_ad=False):
    from .itv_account import itv_session
    session = itv_session()

    stream_req_data = _devices[device]
    stream_req_data['user']['token'] = session.access_token

    if featureset:
        stream_req_data['variantAvailability']['featureset'] = _features[featureset][:]
    if has_ad:
        stream_req_data['variantAvailability']['featureset'].append('inband-audio-description')

    if drmtype is not None:
        stream_req_data['variantAvailability']['drm'] = _drm[drmtype]

    resp = requests.post(
        url,
        json=stream_req_data,
        headers={'Accept': 'application/vnd.itv.vod.playlist.v4+json',
                 'user-agent': USER_AGENT})
    return resp.json()


def parse_playlist(playlist):
    """Return the urls to the dash stream and licence key servers for a particular catchup
    episode and the type of video.

    """

    # Select the media with the highest resolution
    stream_data = playlist['Video']
    highest_resolution = 0
    video_locations = {}
    base_url = stream_data.get('Base')
    for media in stream_data['MediaFiles']:
        res = int(media.get('Resolution', 0))
        if res > highest_resolution:
            video_locations = media
            highest_resolution = res

    if base_url:
        dash_url = base_url + video_locations['Href']
    else:
        dash_url = video_locations['Href']

    # # Force display height <= 1080
    # url, qs = dash_url.rsplit('?')
    # # # Force display height <= 1080
    # # qs = qs.replace('720', '1080')
    # url = url.replace('-HD-S', '-HD')
    # dash_url = '?'.join((url, qs))

    key_service = video_locations['KeyServiceUrl']
    key_service = key_service.replace('playready/rightsmanager.asmx', 'widevine/getlicense')
    return dash_url, key_service


def create_dash_stream_item(manifest_url, key_service_url):
    # noinspection PyImport,PyUnresolvedReferences
    li = ListItem(offscreen=True)
    li.setPath(manifest_url)
    li.setContentLookup(False)
    li.setMimeType('application/dash+xml')

    stream_headers = ''.join((
            'User-Agent=',
            USER_AGENT,
            '&Referer=https://www.itv.com/&'
            'Origin=https://www.itv.com&'
            'Sec-Fetch-Dest=empty&'
            'Sec-Fetch-Mode=cors&'
            'Sec-Fetch-Site=same-site'))

    isa_config = {
        'internal_cookies': True,
    }
    li.setProperties({
        'inputstream': 'inputstream.adaptive',
        'inputstream.adaptive.stream_headers': stream_headers,
        'inputstream.adaptive.manifest_headers': stream_headers,
        'inputstream.adaptive.config': json.dumps(isa_config),
        'inputstream.adaptive.drm_legacy': ''.join(
            ('com.widevine.alpha|',
             key_service_url,
             '|User-Agent=', USER_AGENT,
             '&Content-Type=application/octet-stream',
             '&Referer=https://www.itv.com/'
             '&Origin=https://www.itv.com'
             '&Sec-Fetch-Dest=empty'
             '&Sec-Fetch-Mode=cors'
             '&Sec-Fetch-Site=cross-site',
             )
        ),
    })
    return li


def play_vod(playlist_url, device, feature_set, drm_type=None, has_ad=False):
    playlist = _request_playlist(playlist_url, device, feature_set, drm_type, has_ad)
    manifest_url, key_service_url = parse_playlist(playlist['Playlist'])
    list_item = create_dash_stream_item(manifest_url, key_service_url)
    return list_item
