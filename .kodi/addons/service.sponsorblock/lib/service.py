# -*- coding: utf-8 -*-


from iapc import Service

from player import SBPlayer


# ------------------------------------------------------------------------------
# SBService

class SBService(Service):

    def __init__(self, *args, **kwargs):
        super(SBService, self).__init__(*args, **kwargs)
        self.__player__ = SBPlayer(self.logger)

    def __setup__(self):
        self.__player__.__setup__()

    def __stop__(self):
        self.__player__ = self.__player__.__stop__()
        self.logger.info("stopped")

    def start(self, **kwargs):
        self.logger.info("starting...")
        self.__setup__()
        self.serve(**kwargs)
        self.__stop__()

    def onSettingsChanged(self):
        self.__setup__()


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":
    SBService().start()
