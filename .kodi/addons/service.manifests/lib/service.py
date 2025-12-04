# -*- coding: utf-8 -*-


from importlib import import_module
from uuid import uuid4

from iapc import http, public, Server, Service
from nuttig import buildUrl


# ------------------------------------------------------------------------------
# ManifestsHttpd

class ManifestsHttpd(Server):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__manifests__ = {}

    def server_close(self):
        self.__manifests__.clear()
        super().server_close()

    def __raise__(self, error):
        if not isinstance(error, Exception):
            error = Exception(error)
        self.logger.error(error, notify=True)

    # --------------------------------------------------------------------------

    def __manifest__(self, _type_, *args, **kwargs):
        try:
            self.__manifests__[(id := uuid4().hex)] = import_module(
                f"manifests.{_type_}"
            ).manifest(
                *args, **kwargs
            )
            return buildUrl(self.url, "manifest", id=id)
        except Exception as error:
            self.__raise__(error)



    @http()
    def manifest(self, **kwargs):
        if (
            (id := kwargs.pop("id", None)) and
            (manifest := self.__manifests__.get(id))
        ):
            return (200, manifest, None)
        self.__raise__("missing or invalid id")


# ------------------------------------------------------------------------------
# ManifestsService

class ManifestsService(Service):

    def serve_forever(self, timeout):
        self.__httpd__ = ManifestsHttpd(
            self.id,
            logger=self.logger.getLogger(component="httpd"),
            timeout=timeout
        )
        while not self.waitForAbort(timeout):
            self.__httpd__.handle_request()
        self.__httpd__.server_close()

    def start(self, **kwargs):
        self.logger.info("starting...")
        self.serve(**kwargs)
        self.logger.info("stopped")

    # public api ---------------------------------------------------------------

    @public
    def manifest(self, *args, **kwargs):
        return self.__httpd__.__manifest__(*args, **kwargs)


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":
    ManifestsService().start(timeout=0.25)
