# -*- coding: utf-8 -*-


from iapc import public, Service
from nuttig import containerRefresh, inputDialog, makeProfile

from mytwitch.persistence import MyChannels
from mytwitch.proxy import MyProxy


# ------------------------------------------------------------------------------
# MyService

class MyService(Service):

    def __init__(self, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)
        makeProfile()
        self.__channels__ = MyChannels()

    def serve_forever(self, timeout):
        self.__proxy__ = MyProxy(
            self.id,
            logger=self.logger.getLogger(component="proxy"),
            timeout=timeout
        )
        while not self.waitForAbort(timeout):
            self.__proxy__.handle_request()
        self.__proxy__.server_close()

    def start(self, **kwargs):
        self.logger.info("starting...")
        self.serve(**kwargs)
        self.logger.info("stopped")

    # stream -------------------------------------------------------------------

    @public
    def video(self, **kwargs):
        if (channel := kwargs.pop("channel", None)):
            self.__channels__.move_to_end(channel)
            if not (video := self.__proxy__.video(channel)):
                containerRefresh()
            return video
        self.logger.error(f"Missing channel", notify=True)

    # channels -----------------------------------------------------------------

    @public
    def channels(self):
        return list(reversed(self.__channels__.values()))

    @public
    def addChannel(self):
        if (name := inputDialog(heading=30001)):
            self.__channels__.add(name)
            containerRefresh()

    @public
    def renameChannel(self, channel, name):
        if (name := inputDialog(heading=30001, defaultt=name)):
            self.__channels__.rename(channel, name)
            containerRefresh()

    @public
    def removeChannel(self, channel):
        self.__channels__.remove(channel)
        containerRefresh()


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":
    MyService().start(timeout=0.05)
