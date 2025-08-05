# -*- coding: utf-8 -*-


import xbmc
from xbmcgui import (
    WindowXMLDialog, ACTION_NAV_BACK, ACTION_PREVIOUS_MENU, ACTION_STOP
)

from nuttig import getAddonPath


# ------------------------------------------------------------------------------
# SBDialog

class SBDialog(WindowXMLDialog):

    __closeActions__ = {ACTION_NAV_BACK, ACTION_PREVIOUS_MENU, ACTION_STOP}

    def __new__(cls, *args, **kwargs):
        return super(SBDialog, cls).__new__(
            cls, "skipDialog.xml", getAddonPath(), "default", "1080i"
        )

    def __init__(self, logger):
        self.logger = logger.getLogger(component="dialog")
        self.__showing__ = False
        self.__seekTime__ = None

    @property
    def isShowing(self):
        return self.__showing__

    # --------------------------------------------------------------------------

    def show(self, seekTime):
        #self.logger.info(f"show(seekTime={seekTime})")
        self.__seekTime__ = seekTime
        if not self.__showing__:
            super(SBDialog, self).show()
            self.__showing__ = True

    def close(self):
        #self.logger.info(f"close()")
        if self.__showing__:
            super(SBDialog, self).close()
            self.__showing__ = False

    # --------------------------------------------------------------------------

    def onAction(self, action):
        #self.logger.info(f"onAction(action={action})")
        if action.getId() in self.__closeActions__:
            self.close()

    def onClick(self, controlId):
        #self.logger.info(f"onClick(controlId={controlId})")
        if controlId == 1:
            if self.__seekTime__:
                xbmc.Player().seekTime(self.__seekTime__)
            self.close()

    # --------------------------------------------------------------------------

    #def onControl(self, control):
    #    self.logger.info(f"onControl(control={control})")
    #    raise NotImplementedError()

    #def onDoubleClick(self, controlId):
    #    self.logger.info(f"onDoubleClick(controlId={controlId})")
    #    raise NotImplementedError()

    #def onFocus(self, controlId):
    #    self.logger.info(f"onFocus(controlId={controlId})")
    #    raise NotImplementedError()

    #def onInit(self):
    #    self.logger.info(f"onInit()")
    #    raise NotImplementedError()
