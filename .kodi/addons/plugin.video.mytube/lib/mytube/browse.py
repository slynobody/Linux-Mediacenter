# -*- coding: utf-8 -*-


from functools import wraps

from iapc import public


# ided -------------------------------------------------------------------------

def ided(idKey):
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if (id := kwargs.pop(idKey, None)):
                return func(self, id, *args, **kwargs)
            self.logger.error(f"Invalid {idKey}: {id}", notify=True)
        return wrapper
    return decorator


# ------------------------------------------------------------------------------
# MyBrowse

class MyBrowse(object):

    def __init__(self, logger, session):
        self.logger = logger.getLogger(component="browse")
        self.__session__ = session

    def __setup__(self):
        pass

    def __stop__(self):
        self.__session__ = None
        self.logger.info("stopped")

    # --------------------------------------------------------------------------

    def __continue__(self, continuation):
        return self.__session__.__continue__(
            "browse", continuation, "onResponseReceivedActions"
        )

    # channel ------------------------------------------------------------------

    @public
    @ided("channelId")
    def tabs(self, channelId, *args):
        #self.logger.info(f"tabs(channelId={channelId}, args={args})")
        return [
            v for k, v in self.__session__.channel(channelId)["tabs"].items()
            if k not in args
        ]

    @public
    @ided("channelId")
    def tab(self, channelId, key, **kwargs):
        #self.logger.info(f"tab(channelId={channelId}, key={key}, kwargs={kwargs})")
        if (channel := self.__session__.channel(channelId)):
            data = {}
            if (continuation := kwargs.pop("continuation", None)):
                data = self.__continue__(continuation)
            elif (params := channel["tabs"].get(key, {}).get("params")):
                data = channel.extractData(
                    key, self.__session__.__browse__(**params)
                )
            return (*channel.extractContents(data), channel["channel"])

    @public
    @ided("channelId")
    def playlists(self, channelId, **kwargs):
        #self.logger.info(f"playlists(channelId={channelId}, kwargs={kwargs})")
        if (channel := self.__session__.channel(channelId)):
            data = {}
            if (continuation := kwargs.pop("continuation", None)):
                data = self.__continue__(continuation)
            else:
                data = channel.extractData(
                    "playlists",
                    self.__session__.playlists(
                        channelId, view=1, sort="lad"
                    )
                )
            return (*channel.extractContents(data), channel["channel"])

    # playlist -----------------------------------------------------------------

    @public
    @ided("playlistId")
    def playlist(self, playlistId, **kwargs):
        #self.logger.info(f"playlist(playlistId={playlistId}, kwargs={kwargs})")
        if (playlist := self.__session__.playlist(playlistId)):
            return (*playlist.videos(**kwargs), playlist["title"])
