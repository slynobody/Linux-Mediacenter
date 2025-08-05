# -*- coding: utf-8 -*-


from iapc import public, Service
from nuttig import (
    containerRefresh, getSetting, makeProfile, selectDialog, setSetting
)

from mytube.browse import MyBrowse
from mytube.feed import MyFeed
from mytube.folders import getFolders
from mytube.regional import languages, locations
from mytube.search import MySearch
from mytube.session import MySession


# ------------------------------------------------------------------------------
# MyService

class MyService(Service):

    def __init__(self, *args, **kwargs):
        super(MyService, self).__init__(*args, **kwargs)
        makeProfile()
        self.__folders__ = {}
        self.__session__ = MySession(self.logger)
        self.__browse__ = MyBrowse(self.logger, self.__session__)
        self.__search__ = MySearch(self.logger, self.__session__)
        self.__feed__ = MyFeed(self.logger, self.__session__)

    def __setup__(self):
        self.__session__.__setup__()
        self.__browse__.__setup__()
        self.__search__.__setup__()
        self.__feed__.__setup__()

    def __stop__(self):
        self.__feed__.__stop__()
        self.__search__.__stop__()
        self.__browse__.__stop__()
        self.__session__.__stop__()
        self.__folders__.clear()
        self.logger.info("stopped")

    def start(self, **kwargs):
        self.logger.info("starting...")
        self.__setup__()
        self.serve(**kwargs)
        self.__stop__()

    def onSettingsChanged(self):
        self.__setup__()
        containerRefresh()

    # video --------------------------------------------------------------------

    @public
    def video(self, **kwargs):
        if (videoId := kwargs.pop("videoId", None)):
            return self.__session__.video(videoId, **kwargs)
        self.logger.error(f"Invalid videoId: {videoId}", notify=True)

    # folders ------------------------------------------------------------------

    @public
    def folders(self, *paths):
        folders = self.__folders__.setdefault(paths, getFolders(*paths))
        return [
            folder for folder in folders
            if (not (setting := folder["setting"])) or getSetting(setting, bool)
        ]

    # regional -----------------------------------------------------------------

    def __regional__(self, ordered, setting, heading):
        keys = list(ordered.keys())
        values = list(ordered.values())
        if (
            (
                index := selectDialog(
                    values,
                    preselect=(
                        keys.index(current)
                        if (current := getSetting(setting, str)) in ordered
                        else -1
                    ),
                    heading=heading
                )
            ) > -1
        ):
            setSetting(setting, keys[index], str)
            setSetting(f"{setting}.text", values[index], str)

    @public
    def selectLanguage(self):
        self.__regional__(languages, "session.hl", 41212)

    @public
    def selectLocation(self):
        self.__regional__(locations, "session.gl", 41222)


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":
    (service := MyService()).start(
        browse=service.__browse__,
        search=service.__search__,
        feed=service.__feed__
    )
