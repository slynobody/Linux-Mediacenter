# -*- coding: utf-8 -*-


from sys import argv

from inputstreamhelper import Helper

from nuttig import action, parseQuery, Plugin, getKodiVersion

from mytwitch.client import MyClient
from mytwitch.items import addChannelItem


# ------------------------------------------------------------------------------
# MyPlugin

class MyPlugin(Plugin):

    def __init__(self, *args, **kwargs):
        super(MyPlugin, self).__init__(*args, **kwargs)
        self.__client__ = MyClient(self.logger)

    # helpers ------------------------------------------------------------------

    def addAddChannel(self):
        return self.addItem(addChannelItem(self.url, action="addChannel"))

    # play ---------------------------------------------------------------------

    def playItem(self, item, manifestType, mimeType=None):
        #self.logger.info(
        #    f"playItem(item={item}, "
        #    f"manifestType={manifestType}, "
        #    f"mimeType={mimeType}"
        #)
        if item:
            if (getKodiVersion()["major"] > 20):
                if not Helper(manifestType).check_inputstream():
                    return False
                item.setProperty("inputstream", "inputstream.adaptive")
            return super(MyPlugin, self).playItem(item, mimeType=mimeType)
        return False

    @action()
    def play(self, **kwargs):
        args, kwargs = self.__client__.play(**kwargs)
        return self.playItem(*args, **kwargs)

    # home ---------------------------------------------------------------------

    @action(category=30000)
    def home(self, **kwargs):
        if self.addAddChannel():
            return self.addDirectory(self.__client__.channels())
        return False

    # addChannel ---------------------------------------------------------------

    @action(directory=False)
    def addChannel(self, **kwargs):
        self.__client__.addChannel()
        return True


# __main__ ---------------------------------------------------------------------

def dispatch(url, handle, query, *args):
    MyPlugin(url, int(handle)).dispatch(**parseQuery(query))


if __name__ == "__main__":
    dispatch(*argv)
