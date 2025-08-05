# -*- coding: utf-8 -*-


from iapc import http, RequestHandler, Server

from mytwitch.channel import MyChannel
from mytwitch.player import MyPlayer


# ------------------------------------------------------------------------------
# MyProxy

class MyHandler(RequestHandler):

    def log_message(self, message, *args):
        self.server.logger.debug(message % args)
        #super(MyHandler, self).log_message(message, *args)


class MyProxy(Server):

    def __init__(self, *args, **kwargs):
        super(MyProxy, self).__init__(*args, handler=MyHandler, **kwargs)
        self.__player__ = MyPlayer(self.logger)
        self.__channels__ = {}

    def server_close(self):
        self.__channels__.clear()
        self.__player__ = None
        super(MyProxy, self).server_close()

    def __raise__(self, error, throw=False):
        if not isinstance(error, Exception):
            error = Exception(error)
        if throw:
            raise error
        else:
            self.logger.error(error, notify=True)

    # --------------------------------------------------------------------------

    def __channel__(self, channel):
        if not (_channel_ := self.__channels__.get(channel)):
            _channel_ = self.__channels__[channel] = MyChannel(
                channel, self.url, self.logger
            )
        return _channel_

    # --------------------------------------------------------------------------

    def video(self, channel):
        self.__channels__.pop(channel, None)
        if (_channel_ := self.__channel__(channel)):
            return _channel_.video

    @http()
    def stream(self, **kwargs):
        if (channel := kwargs.pop("channel", None)):
            if (
                (_channel_ := self.__channel__(channel)) and
                (result := _channel_.stream(**kwargs))
            ):
                stream, reset = result
                if stream:
                    if reset:
                        self.__player__.reset()
                    return (200, (stream.dumps(), stream.content_type), None)
            self.__raise__("Something went wrong")
        self.__raise__("Missing channel", throw=False)
