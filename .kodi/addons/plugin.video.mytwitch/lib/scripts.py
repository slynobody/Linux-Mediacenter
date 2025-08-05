# -*- coding: utf-8 -*-


from sys import argv
from urllib.parse import unquote_plus

from iapc import Client


# channels ---------------------------------------------------------------------

def renameChannel(channel, name):
    return Client().renameChannel(channel, name)

def removeChannel(channel):
    return Client().removeChannel(channel)


# __main__ ---------------------------------------------------------------------

__scripts__ = {
    "renameChannel": renameChannel,
    "removeChannel": removeChannel
}

def dispatch(name, *args):
    if (not (script := __scripts__.get(name)) or not callable(script)):
        raise Exception(f"Invalid script '{name}'")
    script(*(unquote_plus(arg) for arg in args))


if __name__ == "__main__":
    dispatch(*argv[1:])
