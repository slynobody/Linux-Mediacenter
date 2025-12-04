# -*- coding: utf-8 -*-


from yt_dlp import YoutubeDL

from deno import name, path, version

from iapc import Client
from nuttig import getSetting, localizedString


# ------------------------------------------------------------------------------
# MyYtDlp

class MyYtDlp(object):

    __service_id__ = "service.yt-dlp"

    __params__ = {
        "verbose": True,
        "js_runtimes": {"deno": {"path": path()}},
        "remote_components": ["ejs:github"]
    }

    __fps_limits__ = {0: 48211, 30: 48212}

    __fps_hints__ = {"int": 48221, "float": 48222, "none": 48223}

    __codecs__ = {
        "avc1": 48311,
        "mp4a": 48312,
        "vp09": 48313,
        "opus": 48314,
        "av01": 48315
    }

    __heights__ = {
        2160: 48411,
        1440: 48412,
        1080: 48413,
        720: 48414,
        480: 48415,
        360: 48416,
        0: 90011
    }

    __tracks__ = {
        None: 90200,
        "ar": 90201,
        "bn": 90202,
        "de": 90203,
        "en": 90204,
        "es": 90205,
        "fr": 90206,
        "he": 90207,
        "hi": 90208,
        "id": 90209,
        "it": 90210,
        "ja": 90211,
        "ko": 90212,
        "ml": 90213,
        "nl": 90214,
        "pa": 90215,
        "pl": 90216,
        "pt": 90217,
        "ro": 90218,
        "ru": 90219,
        "tr": 90220,
        "uk": 90221,
        "vi": 90222,
        "zh": 90223
    }

    def __init__(self, logger):
        self.logger = logger.getLogger(component="ytdlp")
        self.__infos__ = YoutubeDL()
        self.__client__ = Client(self.__service_id__)

    def __setup__(self, headers=None):
        if headers:
            self.__params__["http_headers"] = headers
        self.logger.info(f"{localizedString(90012)}: {name()} {version()}")
        # include automatic captions
        self.__captions__ = getSetting("subs.captions", bool)
        self.logger.info(f"{localizedString(48110)}: {self.__captions__}")
        # fps limit
        self.__fps_limit__ = getSetting("fps.limit", int)
        self.logger.info(
            f"{localizedString(48210)}: "
            f"{localizedString(self.__fps_limits__[self.__fps_limit__])}"
        )
        # fps hint
        self.__fps_hint__ = getSetting("fps.hint", str)
        self.logger.info(
            f"{localizedString(48220)}: "
            f"{localizedString(self.__fps_hints__[self.__fps_hint__])}"
        )
        # exclude codecs
        self.__exclude__ = []
        labels = None
        if (exclude := getSetting("codecs.exclude")):
            self.__exclude__ = exclude.split(",")
            labels = ", ".join(
                localizedString(self.__codecs__[codec])
                for codec in self.__exclude__
            )
        self.logger.info(f"{localizedString(48310)}: {labels}")
        # preferred resolution
        self.__height__ = getSetting("prefs.height", int)
        self.logger.info(
            f"{localizedString(48410)}: "
            f"{localizedString(self.__heights__[self.__height__])}"
        )
        # preferred audio track
        self.__track__ = getSetting("prefs.track", str) or None
        self.logger.info(
            f"{localizedString(48420)}: "
            f"{localizedString(self.__tracks__[self.__track__])}"
        )

    def __stop__(self):
        self.__infos__ = self.__infos__.close()
        self.logger.info("stopped")

    # --------------------------------------------------------------------------

    def video(self, url, **kwargs):
        #self.logger.info(f"video(url={url})")
        return self.__client__.video(
            url,
            captions=self.__captions__,
            exclude=self.__exclude__,
            fps_limit=self.__fps_limit__,
            fps_hint=self.__fps_hint__,
            height=self.__height__,
            track=self.__track__,
            params=self.__params__,
            **kwargs
        )

    def extract(self, url):
        #self.logger.info(f"extract(url={url})")
        return self.__infos__.extract_info(url, download=False, process=False)
