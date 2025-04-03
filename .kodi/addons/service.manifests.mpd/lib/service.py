# -*- coding: utf-8 -*-


from uuid import uuid4

from iapc import http, public, Server, Service
from nuttig import buildUrl, notify, ICONERROR

from adaptive import manifest


# ------------------------------------------------------------------------------
# DashHttpServer

class DashHttpServer(Server):

    def __init__(self, *args, **kwargs):
        super(DashHttpServer, self).__init__(*args, **kwargs)
        self.__manifests__ = {}

    def server_close(self):
        self.__manifests__.clear()
        super(DashHttpServer, self).server_close()

    def __raise__(self, error, throw=True):
        if not isinstance(error, Exception):
            error = Exception(error)
        notify(f"error: {error}", icon=ICONERROR)
        if throw:
            raise error

    # --------------------------------------------------------------------------

    def __manifest__(self, *args):
        self.__manifests__[(id := uuid4().hex)] = manifest(*args)
        return buildUrl(self.url, "manifest", id=id)

    @http()
    def manifest(self, **kwargs):
        if (id := kwargs.pop("id", None)):
            if (manifest := self.__manifests__.get(id)):
                return (200, (manifest, "application/dash+xml"), None)
            self.__raise__("Invalid id")
        self.__raise__("Missing id")


# ------------------------------------------------------------------------------
# DashService

class DashService(Service):

    def serve_forever(self, timeout):
        self.__httpd__ = DashHttpServer(
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
    def manifest(self, *args):
        return self.__httpd__.__manifest__(*args)


# __main__ ---------------------------------------------------------------------

if __name__ == "__main__":
    DashService().start(timeout=0.25)
