# -*- coding: utf-8 -*-


from math import isclose
from operator import le, lt, sub
from threading import Timer

from xbmc import Player

from nuttig import getSetting, localizedString

from dialog import SBDialog
from session import SBSession


# ------------------------------------------------------------------------------
# SBTimer

class SBTimer(Timer):

    def __init__(self, func, ival, *args, **kwargs):
        super(SBTimer, self).__init__(ival, func, args=args, kwargs=kwargs)
        self.start()


# ------------------------------------------------------------------------------
# SBSegments

class SBSegments(list):

    def __init__(self, skips=None, threshold=-5.0):
        super(SBSegments, self).__init__(
            segment for skip in (skips or [])
            if (
                (skip["votes"] >= 0) and
                (sub(*(segment := skip["segment"])) < threshold)
            )
        )


# ------------------------------------------------------------------------------
# SBPlayer

class SBPlayer(Player):

    # _must_ be negative and
    # abs(__threshold__) _must_ be greater than __tol__
    __threshold__ = -5.0 # should be a setting
    __tol__ = 1.0 # math.isclose() abs_tol

    def __init__(self, logger, *args, **kwargs):
        super(SBPlayer, self).__init__(*args, **kwargs)
        self.logger = logger.getLogger(component="player")
        self.__session__ = SBSession(self.logger)
        self.__dialog__ = SBDialog(self.logger)
        self.__segments__ = None
        self.__timer__ = None

    def __setup__(self):
        #self.__threshold__ = -getSetting("sponsorblock.threshold", float))
        #self.logger.info(f"{localizedString(42110)}: {self.__threshold__}")
        self.__session__.__setup__()

    def __stop__(self):
        self.__reset__()
        self.__dialog__ = None
        self.__session__ = self.__session__.__stop__()
        self.logger.info("stopped")

    # --------------------------------------------------------------------------

    def __wakeup__(self, seekTime):
        #self.logger.info(f"__wakeup__(seekTime={seekTime})")
        if seekTime:
            self.__dialog__.show(seekTime)
        else:
            self.__dialog__.close()
        self.__schedule__(self.getTime(), rerun=True)

    # --------------------------------------------------------------------------

    def __reset__(self):
        #self.logger.info("__reset__()")
        if self.__timer__:
            self.__timer__ = self.__timer__.cancel()

    def __interval__(self, func, current, target, rerun=False):
        if (
            (ival := (target - current) if func(current, target) else None) and
            (not (rerun and isclose(ival, 0.0, abs_tol=self.__tol__)))
        ):
            return ival
        return None

    def __args__(self, current, start, stop, rerun=False):
        seekTime = None
        if (ival := self.__interval__(le, current, start, rerun=rerun)):
            seekTime = stop
            if (not rerun):
                self.__dialog__.close() # if we jumped out of a segment
        else:
            ival = self.__interval__(lt, current, stop, rerun=rerun)
            if (ival and (not rerun)):
                self.__dialog__.show(stop) # if we jumped into a segment

        if ival:
            return (ival, seekTime)
        return None

    def __schedule__(self, current, rerun=False):
        #self.logger.info(f"__schedule__(current={current}, rerun={rerun})")
        self.__reset__()
        if self.__segments__:
            for segment in self.__segments__:
                if (args := self.__args__(current, *segment, rerun=rerun)):
                    self.__timer__ = SBTimer(self.__wakeup__, *args)
                    break
            else:
                self.__dialog__.close() # we're past the last segment

    # --------------------------------------------------------------------------

    def onPlayBackStarted(self):
        #self.logger.info(f"onPlayBackStarted()")
        try:
            item = self.getPlayingItem()
        except Exception:
            item = None
        if (item and (videoID := item.getProperty("SB:videoID"))):
            self.__segments__ = SBSegments(
                self.__session__.skipSegments(videoID),
                threshold=self.__threshold__
            )
        else:
            self.__segments__ = None

    # --------------------------------------------------------------------------

    def onAVStarted(self):
        #self.logger.info(f"onAVStarted()")
        self.__schedule__(self.getTime())

    def onPlayBackResumed(self):
        #self.logger.info(f"onPlayBackResumed()")
        self.__schedule__(self.getTime())

    def onPlayBackSeek(self, time, seekOffset):
        #self.logger.info(f"onPlayBackSeek(time={time}, seekOffset={seekOffset})")
        self.__schedule__(time / 1000)

    # --------------------------------------------------------------------------

    def onPlayBackPaused(self):
        #self.logger.info(f"onPlayBackPaused()")
        self.__reset__()

    def onPlayBackStopped(self):
        #self.logger.info(f"onPlayBackStopped()")
        self.__reset__()

    def onPlayBackEnded(self):
        #self.logger.info(f"onPlayBackEnded()")
        self.__reset__()

    def onPlayBackError(self):
        #self.logger.info(f"onPlayBackError()")
        self.__reset__()

    # --------------------------------------------------------------------------

    #def onAVChange(self):
    #    self.logger.info(f"onAVChange()")
    #    if self.__timer__:
    #        self.__schedule__(self.getTime())

    #def onPlayBackSpeedChanged(self, speed):
    #    self.logger.info(f"onPlayBackSpeedChanged(speed={speed})")
    #    raise NotImplementedError()

    #def onPlayBackSeekChapter(self, chapter):
    #    self.logger.info(f"onPlayBackSeekChapter(chapter={chapter})")
    #    raise NotImplementedError()

    #def onQueueNextItem(self):
    #    self.logger.info(f"onQueueNextItem()")
    #    raise NotImplementedError()
