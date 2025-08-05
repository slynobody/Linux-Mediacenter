# -*- coding: utf-8 -*-


__all__ = [
    "executeBuiltin", "executeJSONRPC", "getCondition", "getInfoLabel",
    "containerRefresh", "containerUpdate", "playMedia", "runScript",
    "addFavourite", "getAddons", "addonInstalled", "addonEnabled",
    "hasAddon", "addonIsEnabled", "activateWindow",
    "getApplicationProperty", "getKodiVersion"
]


from json import dumps, loads

import xbmc


# executeBuiltin ---------------------------------------------------------------

def executeBuiltin(function, *args, wait=False):
    xbmc.executebuiltin(
        f"{function}({','.join(str(arg) for arg in args)})", wait
    )


# executeJSONRPC ---------------------------------------------------------------

class JSONRPCError(Exception):

    def __init__(self, error):
        message = f"[{error['code']}] {error['message']}".rstrip(".")
        if (data := error.get("data")):
            message = f"{message} {self.__data__(data)}"
        super(JSONRPCError, self).__init__(message)

    def __data__(self, data):
        message = f"in {data['method']}"
        if (stack := data.get("stack")):
            message = f"{message} {self.__stack__(stack)}"
        return message

    def __stack__(self, stack):
        return f"({stack['message']} ('{stack['name']}'))"


def executeJSONRPC(method, **params):
    request = {"id": 1, "jsonrpc": "2.0", "method": method, "params": params}
    response = loads(xbmc.executeJSONRPC(dumps(request)))
    if (error := response.get("error")):
        raise JSONRPCError(error)
    return response.get("result")


# getCondition -----------------------------------------------------------------

def getCondition(condition):
    return xbmc.getCondVisibility(condition)


# getInfoLabel -----------------------------------------------------------------

def getInfoLabel(infotag):
    return xbmc.getInfoLabel(infotag)


# __getApplicationProperties__ -------------------------------------------------

def __getApplicationProperties__(*args):
    return executeJSONRPC("Application.GetProperties", properties=list(args))


# misc execute utils -----------------------------------------------------------

# containerRefresh
def containerRefresh(*args, **kwargs):
    executeBuiltin("Container.Refresh", *args, **kwargs)

# containerUpdate
def containerUpdate(*args, **kwargs):
    executeBuiltin("Container.Update", *args, **kwargs)

# playMedia
def playMedia(*args, **kwargs):
    executeBuiltin("PlayMedia", *args, **kwargs)

# runScript
def runScript(*args, **kwargs):
    executeBuiltin("RunScript", *args, **kwargs)

# addFavourite
def addFavourite(title, type, **kwargs):
    executeJSONRPC("Favourites.AddFavourite", title=title, type=type, **kwargs)

# getAddons
def getAddons(**kwargs):
    return executeJSONRPC("Addons.GetAddons", **kwargs)["addons"]

# addonInstalled
def addonInstalled(addonid):
    return (addonid in (addon["addonid"] for addon in getAddons()))

# addonEnabled
def addonEnabled(addonid):
    return (addonid in (addon["addonid"] for addon in getAddons(enabled=True)))

# hasAddon
def hasAddon(addonid):
    return getCondition(f"System.HasAddon({addonid})")

# addonIsEnabled
def addonIsEnabled(addonid):
    return getCondition(f"System.AddonIsEnabled({addonid})")

# activateWindow
def activateWindow(*args, **kwargs):
    executeBuiltin("ActivateWindow", *args, **kwargs)

# getApplicationProperty
def getApplicationProperty(name):
    return __getApplicationProperties__(name)[name]

# getKodiVersion
def getKodiVersion():
    return getApplicationProperty("version")
