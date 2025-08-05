# -*- coding: utf-8 -*-


from iapc import Client

from mytwitch.items import Channels, Video


# ------------------------------------------------------------------------------
# MyClient

class MyClient(object):

    def __init__(self, logger):
        self.logger = logger.getLogger(component="client")
        self.__client__ = Client()

    # play ---------------------------------------------------------------------

    def play(self, **kwargs):
        if (video := self.__client__.video(**kwargs)):
            if (item := Video(video)):
                item.setProperty("twitch:channel", kwargs["channel"])
            return (
                (item, video["manifestType"]), {"mimeType": video["mimeType"]}
            )
        return ((None, None), {})

    # channels -----------------------------------------------------------------

    def channels(self):
        return Channels(self.__client__.channels())

    def addChannel(self):
        self.__client__.addChannel()

    def renameChannel(self, channel, name):
        self.__client__.renameChannel(channel, name)

    def removeChannel(self, channel):
        self.__client__.removeChannel(channel)
