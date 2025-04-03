# -*- coding: utf-8 -*-


from functools import wraps
from urllib.parse import unquote

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError, UserNotLive

from iapc import public, Service
from nuttig import getSetting, localizedString

from mpd import YtDlpMpd


# __params__ -------------------------------------------------------------------

def __params__(func):
    @wraps(func)
    def wrapper(self, url, params=None, **kwargs):
        if params:
            extractor = self.__extractor__
            self.__extractor__ = YoutubeDL(params=params)
        try:
            return func(self, url, **kwargs)
        finally:
            if params:
                self.__extractor__.close()
                self.__extractor__ = extractor
    return wrapper


# ------------------------------------------------------------------------------
# YtDlpVideo

class YtDlpVideo(dict):

    def __init__(self, info, captions=False):
        subtitles = info.get("subtitles", {})
        if not subtitles and captions:
            subtitles = info.get("automatic_captions", {})
        super(YtDlpVideo, self).__init__(
            video_id=info.get("id"),
            title=info.get("fulltitle", ""),
            description=info.get("description", ""),
            channel_id=info.get("channel_id"),
            channel=info.get("channel", ""),
            duration=info.get("duration", -1),
            is_live=info.get("is_live", False),
            url=info.get("manifest_url"),
            thumbnail=info.get("thumbnail"),
            like_count=info.get("like_count", 0),
            view_count=info.get("view_count", 0),
            timestamp=info.get("timestamp", 0),
            #headers=info.get("http_headers", {}),
            formats=info.get("formats", []),
            subtitles=subtitles,
            language=info.get("language", ""),
        )


# ------------------------------------------------------------------------------
# YtDlpService


class YtDlpService(Service):

    def __init__(self, *args, **kwargs):
        super(YtDlpService, self).__init__(*args, **kwargs)
        self.__extractor__ = YoutubeDL()
        self.__mpd__ = YtDlpMpd(self.logger)

    def __setup__(self):
        # include automatic captions
        self.__captions__ = getSetting("subs.captions", bool)
        self.logger.info(f"{localizedString(31100)}: {self.__captions__}")
        self.__mpd__.__setup__()

    def __stop__(self):
        self.__mpd__ = self.__mpd__.__stop__()
        self.__extractor__ = self.__extractor__.close()
        self.logger.info("stopped")

    def start(self, **kwargs):
        self.logger.info("starting...")
        self.__setup__()
        self.serve(**kwargs)
        self.__stop__()

    def onSettingsChanged(self):
        self.__setup__()
        #super(YtDlpService, self).onSettingsChanged() # XXX: do NOT do that

    # --------------------------------------------------------------------------

    def __reraise__(self, _type_, value, traceback=None):
        try:
            if value is None:
                value = _type_()
            if value.__traceback__ is not traceback:
                raise value.with_traceback(traceback)
            raise value
        finally:
            v = None
            traceback = None

    def __extract__(self, url, **kwargs):
        try:
            try:
                return self.__extractor__.extract_info(
                    unquote(url), download=False, **kwargs
                )
            except DownloadError as error:
                if (exc_info := error.exc_info):
                    self.__reraise__(*exc_info)
                raise error
        except (UserNotLive, ExtractorError) as error:
            self.logger.info(error, notify=True, time=1000)

    def __video__(self, info, captions=None, **kwargs):
        captions = captions if captions is not None else self.__captions__
        if (video := YtDlpVideo(info, captions=captions)):
            #self.logger.info(f"info: {info}")
            formats = video.pop("formats")
            subtitles = video.pop("subtitles")
            if video["url"]:
                #self.logger.info(f"url: {video['url']}")
                video["manifestType"] = "hls"
                video["mimeType"] = None
            else:
                video["url"] = self.__mpd__.manifest(
                    video["duration"], formats, subtitles, **kwargs
                )
                video["manifestType"] = "mpd"
                video["mimeType"] = "application/dash+xml"
            return video

    # public api ---------------------------------------------------------------

    @public
    @__params__
    def video(self, url, **kwargs):
        self.logger.info(f"video(url={url}, kwargs={kwargs})")
        if (info := self.__extract__(url)):
            return self.__video__(info, **kwargs)

    @public
    @__params__
    def extract(self, url, **kwargs):
        self.logger.info(f"extract(url={url}, kwargs={kwargs})")
        if (info := self.__extract__(url, **kwargs)):
            return self.__extractor__.sanitize_info(info)


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":
    YtDlpService().start()
