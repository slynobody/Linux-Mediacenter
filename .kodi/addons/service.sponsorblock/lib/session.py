# -*- coding: utf-8 -*-


from requests import HTTPError, Session, Timeout

from nuttig import buildUrl, getSetting, localizedString


# ------------------------------------------------------------------------------
# SBSession

class SBSession(Session):

    __url__ = "https://sponsor.ajay.app/api"

    def __init__(self, logger):
        super(SBSession, self).__init__()
        self.logger = logger.getLogger(component="session")

    def __setup__(self):
        if (timeout := getSetting("session.timeout", float)) > 0.0:
            self.__timeout__ = (((timeout - (timeout % 3)) + 0.05), timeout)
        else:
            self.__timeout__ = None
        self.logger.info(f"{localizedString(41110)}: {self.__timeout__}")

    def __stop__(self):
        self.close()
        self.logger.info("stopped")

    # --------------------------------------------------------------------------

    def request(self, method, paths, **kwargs):
        url = buildUrl(self.__url__, *paths)
        self.logger.info(
            f"request: {method} {buildUrl(url, **kwargs.get('params', {}))}"
        )
        return super(SBSession, self).request(
            method, url, timeout=self.__timeout__, **kwargs
        )

    def get(self, *paths, **kwargs):
        try:
            response = super(SBSession, self).get(paths, params=kwargs)
            response.raise_for_status()
        except Timeout as error:
            self.logger.error(error, notify=True)
        except HTTPError as error:
            self.logger.info(error)
        except Exception as error:
            self.logger.error(error)
        else:
            return response.json()

    # --------------------------------------------------------------------------

    def skipSegments(self, videoID):
        return self.get("skipSegments", videoID=videoID)
