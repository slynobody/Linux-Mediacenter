# -*- coding: utf-8 -*-


from iapc import Client

from nuttig import addonIsEnabled

from mytube.items import (
    FeedChannels, Folders, Playlists, Queries, Results, Video, Videos
)
from mytube.persistence import MyNavigationHistory


# ------------------------------------------------------------------------------
# MyClient

class MyClient(object):

    def __init__(self, logger):
        self.logger = logger.getLogger(f"{logger.component}.client")
        self.__client__ = Client()
        self.__history__ = MyNavigationHistory()

    # video --------------------------------------------------------------------

    def video(self, sb=False, **kwargs):
        #self.logger.info(f"video(sb={sb}, kwargs={kwargs})")
        if (video := self.__client__.video(**kwargs)):
            item = Video(video).makeItem(video["url"])
            if (item and sb and addonIsEnabled("service.sponsorblock")):
                item.setProperty("SB:videoID", video["videoId"])
            return (
                (item, video["manifestType"]), {"language": video["language"]}
            )
        return ((None, None), {})

    # channel ------------------------------------------------------------------

    def tabs(self, *args, **kwargs):
        if (
            tabs := self.__client__.browse.tabs(
                *args, channelId=kwargs["channelId"]
            )
        ):
            return Folders(tabs, **kwargs)

    def __tab__(self, key, **kwargs):
        items, next, category = self.__client__.browse.tab(key, **kwargs)
        previous = self.__history__.continuation(key, kwargs.get("continuation"))
        return Videos(items, next=next, category=category, previous=previous)

    def videos(self, **kwargs):
        return self.__tab__("videos", **kwargs)

    def shorts(self, **kwargs):
        return self.__tab__("shorts", **kwargs)

    def streams(self, **kwargs):
        return self.__tab__("streams", **kwargs)

    def playlists(self, **kwargs):
        items, next, category = self.__client__.browse.playlists(**kwargs)
        previous = self.__history__.continuation(
            "playlists", kwargs.get("continuation")
        )
        return Playlists(items, next=next, category=category, previous=previous)

    # playlist -----------------------------------------------------------------

    def playlist(self, limit=29, **kwargs):
        items, next, category = self.__client__.browse.playlist(
            limit=limit, **kwargs
        )
        previous = self.__history__.page("playlist", kwargs["page"])
        return Videos(items, next=next, category=category, previous=previous)

    # home ---------------------------------------------------------------------

    def home(self):
        return Folders(self.__client__.folders())

    # feed ---------------------------------------------------------------------

    def feed(self, limit=29, **kwargs):
        items, next = self.__client__.feed.feed(limit, **kwargs)
        previous = self.__history__.page("feed", kwargs["page"])
        return Videos(items, next=next, previous=previous)

    def channels(self):
        return FeedChannels(self.__client__.feed.channels())

    # search -------------------------------------------------------------------

    def query(self):
        return self.__client__.search.query()

    def history(self):
        return Queries(self.__client__.search.history())

    def search(self, **query):
        items, next = self.__client__.search.search(**query)
        previous = self.__history__.continuation(
            "search", query.get("continuation")
        )
        return Results(
            items, next=next, previous=previous, category=query["query"]
        )
