# -*- coding: utf-8 -*-


from functools import wraps
from urllib.parse import unquote

from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError, ExtractorError, UserNotLive

from iapc import public, Service

from videos import YtDlpVideos


# __params__ -------------------------------------------------------------------

def __params__(func):
    @wraps(func)
    def wrapper(self, url, **kwargs):
        if (params := kwargs.pop("params", None)):
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
# YtDlpService

class YtDlpService(Service):

    def __init__(self, *args, **kwargs):
        super(YtDlpService, self).__init__(*args, **kwargs)
        self.__extractor__ = YoutubeDL()
        self.__videos__ = YtDlpVideos(self.logger)

    def __setup__(self):
        self.__videos__.__setup__()

    def __stop__(self):
        self.__videos__ = self.__videos__.__stop__()
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
            value = None
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
        except UserNotLive as error:
            self.logger.info(error.__class__.__name__, notify=True, time=1000)
        except ExtractorError as error:
            self.logger.info(error, notify=True)

    # public api ---------------------------------------------------------------

    @public
    @__params__
    def video(self, url, **kwargs):
        self.logger.info(f"video(url={url}, kwargs={kwargs})")
        if (info := self.__extract__(url)):
            return self.__videos__.video(info, **kwargs)

    @public
    @__params__
    def extract(self, url, **kwargs):
        self.logger.info(f"extract(url={url}, kwargs={kwargs})")
        if (info := self.__extract__(url, **kwargs)):
            return self.__extractor__.sanitize_info(info)


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":
    YtDlpService().start()
