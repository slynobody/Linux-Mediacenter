# -*- coding: utf-8 -*-


from concurrent.futures import ThreadPoolExecutor
from functools import wraps
from random import randint
from time import time

from requests import HTTPError, Session, Timeout

from nuttig import buildUrl, getSetting, localizedString

from mytube.extract import traverse, MyChannel, MyPlaylist, MyRss, MyVideo
from mytube.find import __find__, find, findIter, PatternsError
from mytube.ytdlp import MyYtDlp


# ------------------------------------------------------------------------------
# __MySession__

class __MySession__(Session):

    __headers__ = {}
    __url__ = "https://www.youtube.com"
    __cookies__ = {None: "CAA", False: "CAE", True: "CAI"}

    def __init__(self):
        super(__MySession__, self).__init__()
        self.headers.update(self.__headers__)
        self.__params__ = {}
        self.__inner__ = {}

    def __setup__(self):
        self.cookies.clear()
        self.__inner__.clear()
        self.__params__.clear()
        if (timeout := getSetting("session.timeout", float)) > 0.0:
            self.__timeout__ = (((timeout - (timeout % 3)) + 0.05), timeout)
        else:
            self.__timeout__ = None
        self.__params__["hl"] = getSetting("session.hl", str)
        self.__params__["gl"] = getSetting("session.gl", str)
        settings = (
            (41110, self.__timeout__),
            (41120, getSetting('session.cookies', bool)),
            (41211, getSetting('session.hl.text', str)),
            (41221, getSetting('session.gl.text', str))
        )
        for label, setting in settings:
            self.logger.info(f"{localizedString(label)}: {setting}")

    def __stop__(self):
        self.close()

    # --------------------------------------------------------------------------

    def request(self, method, path, notify=True, **kwargs):
        url = buildUrl(self.__url__, *path)
        self.logger.info(
            f"request: {method} {buildUrl(url, **kwargs.get('params', {}))}"
        )
        try:
            response = super(__MySession__, self).request(
                method, url, timeout=self.__timeout__, **kwargs
            )
            response.raise_for_status()
            return response
        except Exception as error:
            self.logger.error(error, notify=notify)
            if (not isinstance(error, (HTTPError, Timeout))):
                raise error

    def __get__(self, *path, **kwargs):
        kwargs.setdefault("params", {}).update(self.__params__)
        return super(__MySession__, self).get(path, **kwargs).text

    def __post__(self, *path, **kwargs):
        return super(__MySession__, self).post(path, **kwargs).json()

    # --------------------------------------------------------------------------
    # get

    @property
    def __consent__(self):
        return (
            (
                (consent := self.cookies.get("CONSENT")) and ("YES" in consent)
            ) and
            (
                (socs := self.cookies.get("SOCS")) and
                (not socs.startswith(self.__cookies__[None]))
            )
        )

    def __setup_consent__(self):
        try:
            value = __find__(self.__get__(), r'cb\..+?(?=\")').group()
        except PatternsError:
            if (
                (consent := self.cookies.get("CONSENT")) and
                ("PENDING" in consent)
            ):
                cid = consent.split("+")[1]
            else:
                cid = randint(100, 999)
            value = f"cb.20221213-07-p1.en+FX+{cid}"
        self.cookies.set("CONSENT", f"YES+{value}", domain=".youtube.com")
        self.cookies.set(
            "SOCS",
            self.__cookies__[getSetting("session.cookies", bool)],
            domain=".youtube.com",
            secure=True
        )

    def get(self, *path, notify=True, **kwargs):
        #self.logger.info(f"get(path={path}, kwargs={kwargs}, notify={notify})")
        if (not self.__consent__):
            self.__setup_consent__()
        return self.__get__(*path, notify=notify, **kwargs)

    # --------------------------------------------------------------------------
    # innertube

    def __setup_inner__(self):
        config = findIter(self.get(), r"ytcfg\.set\s*\(\s*")
        self.__inner__["path"] = ("youtubei", config["INNERTUBE_API_VERSION"])
        self.__inner__["params"] = {
            #"key": config["INNERTUBE_API_KEY"],
            "prettyPrint": False
        }
        self.__inner__["headers"] = {
            #"X-Goog-Visitor-Id": config["VISITOR_DATA"],
            "X-Youtube-Client-Name": str(config["INNERTUBE_CONTEXT_CLIENT_NAME"]),
            "X-Youtube-Client-Version": config["INNERTUBE_CONTEXT_CLIENT_VERSION"]
        }
        self.__inner__["context"] = {
            "client": {
                "hl": self.__params__["hl"],
                "gl": self.__params__["gl"],
                #"userAgent": self.headers["User-Agent"],
                "clientName": config["INNERTUBE_CLIENT_NAME"],
                "clientVersion": config["INNERTUBE_CLIENT_VERSION"]
            }
        }

    def innertube(self, *path, notify=True, **kwargs):
        #self.logger.info(
        #    f"innertube(path={path}, kwargs={kwargs}, notify={notify})"
        #)
        if (not self.__inner__):
            self.__setup_inner__()
        return self.__post__(
            *self.__inner__["path"], *path,
            notify=notify,
            params=self.__inner__["params"],
            headers=self.__inner__["headers"],
            json=dict(kwargs, context=self.__inner__["context"])
        )


# cached -----------------------------------------------------------------------

def cached(name):
    def decorator(func):
        @wraps(func)
        def wrapper(self, key, *args, **kwargs):
            cache = self.__cache__.setdefault(name, {})
            if (
                (not (value := cache.get(key))) or
                (
                    (expires := getattr(value, "__expires__", None)) and
                    (time() >= expires)
                )
            ):
                value = cache[key] = func(self, *(args or (key,)), **kwargs)
            return value
        return wrapper
    return decorator


# ------------------------------------------------------------------------------
# MySession

class MySession(__MySession__):

    def __init__(self, logger):
        self.logger = logger.getLogger(component="session")
        super(MySession, self).__init__()
        self.__pool__ = ThreadPoolExecutor()
        self.__ytdlp__ = MyYtDlp(self.logger)
        self.__cache__ = {}

    def __setup__(self):
        super(MySession, self).__setup__()
        self.__ytdlp__.__setup__()
        self.__cache__.clear()

    def __stop__(self):
        self.__cache__.clear()
        self.__ytdlp__ = self.__ytdlp__.__stop__()
        self.__pool__.shutdown(cancel_futures=True)
        super(MySession, self).__stop__()
        self.logger.info("stopped")

    # --------------------------------------------------------------------------

    def playlists(self, channelId, **kwargs):
        return find(
            self.get("channel", channelId, "playlists", params=kwargs),
            r"ytInitialData\s*=\s*"
        )

    def __search__(self, **kwargs):
        return self.innertube("search", **kwargs)

    def __browse__(self, **kwargs):
        return self.innertube("browse", **kwargs)

    def __continue__(self, path, continuation, responseKey):
        return traverse(
            self.innertube(path, continuation=continuation),
            responseKey,
            0,
            "appendContinuationItemsAction",
            "continuationItems",
            default=[]
        )

    # cached -------------------------------------------------------------------

    @cached("videos")
    def video(self, videoId, **kwargs):
        return MyVideo(
            self.__ytdlp__.video(
                buildUrl(self.__url__, "watch", v=videoId, **self.__params__),
                **kwargs
            )
        )

    @cached("channels")
    def channel(self, channelId, **kwargs):
        return MyChannel(self.__browse__(browseId=channelId, **kwargs))

    @cached("playlists")
    def playlist(self, playlistId):
        return MyPlaylist(
            self.__ytdlp__.extract(
                buildUrl(
                    self.__url__, "playlist", list=playlistId, **self.__params__
                )
            )
        )

    # feed ---------------------------------------------------------------------

    def feed(self, **kwargs):
        return MyRss(
            self.get("feeds", "videos.xml", params=kwargs, notify=False)
        )

    def __feeds__(self, keys):
        if (not self.__consent__):
            self.__setup_consent__()
        def __map_feed__(key):
            try:
                return self.feed(channel_id=key)
            except Exception:
                return None
        #return (f for f in self.__pool__.map(__map_feed__, keys) if f)
        for feed in self.__pool__.map(__map_feed__, keys):
            if feed:
                yield from feed

    def __channels__(self, keys):
        if (not self.__inner__):
            self.__setup_inner__()
        def __map_channel__(key):
            try:
                return self.channel(key, notify=False)
            except Exception:
                return None
        #return (c for c in self.__pool__.map(__map_channel__, keys) if c)
        for channel in self.__pool__.map(__map_channel__, keys):
            if channel:
                yield channel
