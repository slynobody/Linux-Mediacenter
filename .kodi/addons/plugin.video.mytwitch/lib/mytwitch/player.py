# -*- coding: utf-8 -*-


from threading import Timer

from xbmc import Player


# ------------------------------------------------------------------------------
# MyTimer

class MyTimer(Timer):

    def __init__(self, func, *args, **kwargs):
        super(MyTimer, self).__init__(2, func, args=args, kwargs=kwargs)
        self.start()


# ------------------------------------------------------------------------------
# MyPlayer

class MyPlayer(Player):

    def __init__(self, logger, *args, **kwargs):
        super(MyPlayer, self).__init__(*args, **kwargs)
        self.logger = logger.getLogger(component="player")
        self.__enabled__ = False
        self.__timer__ = None

    # --------------------------------------------------------------------------

    def __cancel__(self):
        if self.__timer__:
            self.__timer__ = self.__timer__.cancel()

    def __disable__(self):
        self.__cancel__()
        self.__enabled__ = False

    def __reset__(self):
        if self.__enabled__ and (item := self.getPlayingItem()):
            self.play(item.getPath(), item)
            #xbmcplugin.setResolvedUrl(1, True, item)

    def reset(self):
        self.__cancel__()
        if self.__enabled__:
            self.__timer__ = MyTimer(self.__reset__)

    # --------------------------------------------------------------------------

    def onAVStarted(self):
        try:
            item = self.getPlayingItem()
        except Exception:
            item = None
        self.__enabled__ = bool(item and item.getProperty("twitch:channel"))

    # --------------------------------------------------------------------------

    def onPlayBackPaused(self):
        self.__cancel__()

    # --------------------------------------------------------------------------

    def onPlayBackStopped(self):
        self.__disable__()

    def onPlayBackEnded(self):
        self.__disable__()

    def onPlayBackError(self):
        self.__disable__()
