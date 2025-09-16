# -*- coding: utf-8 -*-


from collections import deque
from urllib.parse import urljoin

import re

import requests

from iapc import Client
from nuttig import buildUrl, notify, ICONWARNING

from mytwitch.m3u8 import protocol, M3U8, PlaylistList


# ------------------------------------------------------------------------------
# MyDiscontinuity

class MyDiscontinuity(deque):

    __marker__ = "#EXT-X-DISCONTINUITY\n"

    def __init__(self, maxlen=5):
        super(MyDiscontinuity, self).__init__(maxlen=maxlen)
        self.__state__ = False

    def push(self, response):
        self.append(self.__marker__ in response.text)
        if (reset := (self.__state__ != (state := any(self)))):
            self.__state__ = state
        return (state, reset)


# ------------------------------------------------------------------------------
# MyPlaylist

class MyPlaylist(dict):

    def __init__(self, playlist, channel, url, headers):
        super(MyPlaylist, self).__init__()
        self.__playlist__ = self.__variant__(playlist, channel, url, headers)

    def __redirect__(self, playlists, channel, url, headers):
        for p in playlists:
            quality = (p.stream_info.video or p.stream_info.audio)
            self[quality] = (p.uri, headers)
            p.uri = buildUrl(url, "stream", channel=channel, quality=quality)
            yield p

    def __variant__(self, playlist, channel, url, headers):
        playlist.playlists = PlaylistList(
            [
                p for p in self.__redirect__(
                    playlist.playlists, channel, url, headers
                )
            ]
        )
        return playlist

    @property
    def content_type(self):
        return self.__playlist__.content_type

    def dumps(self):
        return self.__playlist__.dumps()


# ------------------------------------------------------------------------------
# MyChannel

class MyChannel(object):

    __verbose__ = False

    __client_id__ = "kimne78kx3ncx6brgo4mv6wki5h1ko"

    __params__ = {
        "client_id": "ue6666qo983tsx6so1t0vnawi233wa",
        "platform": "ios",
        "player_type": "autoplay",
        "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_7_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/138.0.7204.33 Mobile/15E148 Safari/604.1"
    }

    __headers__ = ("Client-Id", "User-Agent")

    __twitch_url__ = "https://www.twitch.tv"

    __client__ = Client("service.yt-dlp")

    @classmethod
    def __make_params__(cls, **kwargs):
        client_id = kwargs.setdefault("client_id", cls.__client_id__)
        http_headers = {"Client-Id": client_id}
        if (user_agent := kwargs.pop("user_agent", None)):
            http_headers["User-Agent"] = user_agent
        return {
            "allowed_extractors": ["twitch:stream"],
            "verbose": cls.__verbose__,
            "http_headers": http_headers,
            "extractor_args": {"twitch": {k: [v] for k, v in kwargs.items()}}
        }

    @classmethod
    def __make_headers__(cls, headers):
        return {
            key: headers[key] for key in headers if key in cls.__headers__
        }

    @classmethod
    def __video__(cls, channel, **kwargs):
        if (
            video := cls.__client__.video(
                f"{cls.__twitch_url__}/{channel}",
                params=cls.__make_params__(**kwargs)
            )
        ):
            video["headers"] = cls.__make_headers__(video["headers"])
        return video

    def __new__(cls, channel, url, logger):
        if (
            (video := cls.__video__(channel)) and
            (_channel_ := super(MyChannel, cls).__new__(cls)) and
            _channel_.__setup__(
                video=video,
                channel=channel,
                url=url,
                logger=logger.getLogger(component=channel),
                discontinuity=MyDiscontinuity()
            )
        ):
            return _channel_

    def __setup__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)
        if (playlist := self.__playlist__(self.video)):
            self.playlist = MyPlaylist(
                playlist, self.channel, self.url, self.video["headers"]
            )
            if (
                (video := self.__video__(self.channel, **self.__params__)) and
                (playlist := self.__playlist__(video))
            ):
                self.playlist.update(
                    MyPlaylist(
                        playlist, self.channel, self.url, video["headers"]
                    )
                )
            self.video["url"] = buildUrl(self.url, "stream", channel=self.channel)
            return True
        return False

    # --------------------------------------------------------------------------

    def __get__(self, url, headers, timeout=10.0, **kwargs):
        try:
            response = requests.get(
                url, headers=headers, timeout=timeout, **kwargs
            )
            response.raise_for_status()
            return response
        except Exception as error:
            self.logger.error(error)

    # --------------------------------------------------------------------------

    __protocol__ = (
        protocol.ext_x_discontinuity_sequence,
        protocol.ext_x_discontinuity
    )

    def __parser__(self, line, lineno, data, state):
        if line.startswith(self.__protocol__):
            return True
        return False

    def __m3u8__(self, text, response):
        try:
            playlist = M3U8(
                text,
                base_uri=urljoin(response.url, "."),
                custom_tags_parser=self.__parser__
            )
            playlist.url = response.url
            playlist.content_type = response.headers["content-type"]
            return playlist
        except Exception as error:
            self.logger.error(error)

    # --------------------------------------------------------------------------

    __pattern__ = re.compile(r"CODECS=\"([^,]+)(?:,[^\"]*)?\"")

    def __fix_text__(self, lines):
        for line in lines:
            if ("audio_only" in line):
                #line = line.replace(
                #    "VIDEO", "AUDIO"
                #).replace(
                #    "AUTOSELECT=NO", "AUTOSELECT=YES"
                #).replace(
                #    "DEFAULT=NO", "DEFAULT=YES"
                #)
                line = line.replace("VIDEO", "AUDIO").replace("NO", "YES")
            elif (line.startswith(protocol.ext_x_stream_inf)):
                line = re.sub(
                    self.__pattern__,
                    f"CODECS=\"{self.__pattern__.search(line).group(1)}\"",
                    line
                )
            yield line

    def __fix_playlist__(self, text):
        if ("audio_only" in text):
            return "".join(self.__fix_text__(text.splitlines(True)))
        return text

    def __playlist__(self, video):
        if (response := self.__get__(video["url"], video["headers"])):
            #self.logger.info(f"__playlist__(), response: {response.text}")
            return self.__m3u8__(self.__fix_playlist__(response.text), response)

    def __stream__(self, quality):
        reset = False
        if (response := self.__get__(*self.playlist[quality])):
            discontinuity, reset = self.discontinuity.push(response)
            if discontinuity:
                notify(30006, icon=ICONWARNING, time=10000)
                response = self.__get__(*self.playlist["360p30"])
        if response:
            #self.logger.info(f"__stream__(), response: {response.text}")
            return (self.__m3u8__(response.text, response), reset)

    # --------------------------------------------------------------------------

    def stream(self, quality=None):
        if quality:
            return self.__stream__(quality)
        #self.logger.info(f"self.playlist: {self.playlist.dumps()}")
        return (self.playlist, False)
