# -*- coding: utf-8 -*-


from urllib.parse import quote_plus

from nuttig import (
    buildUrl, getAddonId, getCondition, getSetting,
    localizedString, maybeLocalize, ListItem
)
from nuttig.objects import List, Object


# misc useful items ------------------------------------------------------------

def __makeItem__(label, url, art=None, isFolder=True, properties=None, **kwargs):
    label = localizedString(label)
    return ListItem(
        label,
        buildUrl(url, **kwargs),
        isFolder=isFolder,
        isPlayable=False,
        properties=properties,
        infoLabels={"video": {"title": label, "plot": label}},
        thumb=art,
        poster=art,
        icon=art
    )


# addChannel item
def addChannelItem(url, **kwargs):
    return __makeItem__(
        30002,
        url,
        art="DefaultAddSource.png",
        isFolder=False,
        properties={"SpecialSort": "top"},
        **kwargs
    )


# ------------------------------------------------------------------------------
# Items

class Item(Object):

    __menus__ = []

    @classmethod
    def __condition__(cls, args, expected):
        result = getSetting(*args) if (len(args) > 1) else getCondition(*args)
        return (result == expected)

    @classmethod
    def menus(cls, **kwargs):
        addonId = getAddonId()
        return [
            (
                maybeLocalize(label).format(**kwargs),
                action.format(
                    addonId=addonId,
                    **{key: quote_plus(value) for key, value in kwargs.items()}
                )
            )
            for label, action, *conditions in cls.__menus__
            if all(cls.__condition__(*condition) for condition in conditions)
        ]

    def __infos__(self, *args):
        for arg in args:
            if (attr := getattr(self, arg, None)):
                yield f"{attr}"

    @property
    def thumbnail(self):
        return self.get("thumbnail", self.__thumbnail__)

    @property
    def poster(self):
        return self.get("poster", self.__thumbnail__)

    @property
    def icon(self):
        return self.get("icon", self.__thumbnail__)

    def labels(self, title, plot, **kwargs):
        return dict(video=dict(title=title, plot=plot, **kwargs))


class Items(List):

    __ctor__ = Item


# ------------------------------------------------------------------------------
# Channels

class Channel(Item):

    __menus__ = [
        (30003, ""),
        (30004, "RunScript({addonId},renameChannel,{channel},{name})"),
        (30005, "RunScript({addonId},removeChannel,{channel})")
    ]

    __thumbnail__ = "DefaultArtist.png"

    def getItem(self, url):
        return ListItem(
            self.name,
            buildUrl(url, action="play", channel=self.channel),
            infoLabels=self.labels(self.name, self.name),
            contextMenus=self.menus(
                channel=self.channel,
                name=self.name
            ),
            thumb=self.thumbnail
        )


class Channels(Items):

    __ctor__ = Channel


# ------------------------------------------------------------------------------
# Video

def Video(info):
    title = info["title"]
    return ListItem(
        title,
        info["url"],
        infoLabels={
            "video": {
                "mediatype": "video",
                "title": title,
                "plot": "\n\n".join((title, info["description"])),
                "playcount":0
            }
        },
        streamInfos={
            "video": {
                "duration": info["duration"]
            }
        },
        thumb=info["thumbnail"]
    )
