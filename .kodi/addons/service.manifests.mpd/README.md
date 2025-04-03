# service.manifests.mpd

Kodi service for MPEG-DASH manifests.

### USAGE:

```
from iapc import Client

duration = 1712 # int - length in seconds
streams = [ # list of streams
    # video
    {
        'contentType': 'video',
        'mimeType': 'video/mp4',
        'lang': None,
        'id': 'av1',
        'url': 'http://...',
        'codecs': 'av01.0.08M.08',
        'averageBitrate': 1134143,
        'width': 1920,
        'height': 1080,
        'frameRate': 25,
        'indexRange': {'end': '4883', 'start': '700'},
        'initRange': {'end': '699', 'start': '0'}
    },
    {
        'contentType': 'video',
        'mimeType': 'video/mp4',
        'lang': None,
        'id': 'h264',
        'url': 'http://...',
        'codecs': 'avc1.640028',
        'averageBitrate': 1564778,
        'width': 1920,
        'height': 1080,
        'frameRate': 25,
        'indexRange': {'end': '4925', 'start': '742'},
        'initRange': {'end': '741', 'start': '0'}
    },
    {
       'contentType': 'video',
       'mimeType': 'video/webm',
       'lang': None,
       'id': 'vp9',
       'url': 'http://...',
       'codecs': 'vp09.00.40.08',
       'averageBitrate': 1349664,
       'width': 1920,
       'height': 1080,
       'frameRate': 25,
       'indexRange': {'end': '6170', 'start': '221'},
       'initRange': {'end': '220', 'start': '0'}
    },
    # audio
    {
        'contentType': 'audio',
        'mimeType': 'audio/m4a',
        'lang': 'en',
        'id': '140',
        'url': 'http://...',
        'codecs': 'mp4a.40.2',
        'averageBitrate': 129473,
        'audioSamplingRate': 44100,
        'audioChannels': 2,
        'indexRange': {'end': '2727', 'start': '632'},
        'initRange': {'end': '631', 'start': '0'}
    },
    {
        'contentType': 'audio',
        'mimeType': 'audio/webm',
        'lang': 'en',
        'id': '251',
        'url': 'http://...',
        'codecs': 'opus',
        'averageBitrate': 102114,
        'audioSamplingRate': 48000,
        'audioChannels': 2,
        'indexRange': {'end': '3222', 'start': '266'},
        'initRange': {'end': '265', 'start': '0'}
    },
    # subtitles
    {
        'contentType': 'text',
        'mimeType': 'text/vtt',
        'lang': 'en-GB',
        'id': 'English (United Kingdom)',
        'url': 'http://...'
    },
    {
        'contentType': 'text',
        'mimeType': 'text/vtt',
        'lang': 'fr',
        'id': 'Français',
        'url': 'http://...'
    }
]

local_manifest_url = Client("service.manifests.mpd").manifest(duration, streams)
```
