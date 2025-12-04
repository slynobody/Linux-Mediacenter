# -*- coding: utf-8 -*-


from datetime import date
from itertools import islice
from re import sub
from time import time

from feedparser import parse

from nuttig import localizedString


# ------------------------------------------------------------------------------

def __date__(datestamp):
    if isinstance(datestamp, str):
        if len(datestamp) == 8:
            return "-".join(
                (datestamp[0:4], datestamp[4:6], datestamp[6:8])
            )
        return date.fromisoformat(datestamp)
    if isinstance(datestamp, int):
        return date.fromtimestamp(datestamp)
    return datestamp


def traverse(data, *keys, default=None):
    for key in keys:
        try:
            data = data.__getitem__(key)
        except (KeyError, IndexError):
            return default
    return data


def joinRuns(obj):
    return "".join((run["text"] for run in obj["runs"]))


def joinParts(parts, delimiter=" • "):
    return delimiter.join(
        (
            text for part in parts
            if (text := traverse(part, "text", "content"))
        )
    )


def getUrl(url):
    if url.startswith("//"):
        url = f"https:{url}"
    return url


def getThumbnail(obj):
    return getUrl(obj["thumbnails"][-1]["url"])


def getLengthSeconds(string):
    # https://stackoverflow.com/a/6403077
    seconds = 0
    for part in string.split(":"):
        seconds = (seconds * 60) + int(sub(r",|\.|\s", "", part), 10)
    return seconds
    # https://stackoverflow.com/a/6402934
    #return sum(
    #    int(x, 10) * 60 ** i for i, x in enumerate(reversed(string.split(":")))
    #)


def videoIsLive(obj):
    for badge in obj.get("badges", []):
        if (
            traverse(
                badge, "metadataBadgeRenderer", "style"
            ) == "BADGE_STYLE_TYPE_LIVE_NOW"
        ):
            return True
    for overlay in obj.get("thumbnailOverlays", []):
        if (
            traverse(
                overlay, "thumbnailOverlayTimeStatusRenderer", "style"
            ) == "LIVE"
        ):
            return True
    return False


# ------------------------------------------------------------------------------

def extractContinuation(obj):
    return traverse(obj, "continuationEndpoint", "continuationCommand", "token")

def extractVideo(obj):
    live = videoIsLive(obj)
    video = {
        "type": "video",
        "videoId": obj["videoId"],
        "title": joinRuns(obj["title"]),
        "thumbnail": getThumbnail(obj["thumbnail"]),
        "live": live
    }
    if (lengthText := obj.get("lengthText")):
        video["duration"] = getLengthSeconds(lengthText.get("simpleText", ""))
    if (viewCountText := obj.get("viewCountText")):
        video["viewsText"] = (
            joinRuns(viewCountText) if live else viewCountText.get("simpleText")
        )
    if (publishedTime := obj.get("publishedTimeText")):
        video["publishedText"] = publishedTime.get("simpleText")
    if (description := obj.get("descriptionSnippet")):
        video["description"] = joinRuns(description)
    return video

def extractChannel(obj):
    channel = {
        "type": "channel",
        "channelId": obj["channelId"],
        "channel": obj["title"].get("simpleText"),
        "thumbnail": getThumbnail(obj["thumbnail"])
    }
    if (subscriberCount := obj.get("videoCountText")): # subs are in videos!!
        channel["subscribersText"] = subscriberCount.get("simpleText")
    if (description := obj.get("descriptionSnippet")):
        channel["description"] = joinRuns(description)
    return channel

def extractPlaylist(obj):
    channel = obj["shortBylineText"]["runs"][0]
    playlist = {
        "type": "playlist",
        "playlistId": obj["playlistId"],
        "title": obj["title"].get("simpleText"),
        "thumbnail": getThumbnail(obj["thumbnails"][0]),
        "videosText": joinRuns(obj["videoCountText"]),
        "channelId": channel["navigationEndpoint"]["browseEndpoint"]["browseId"],
        "channel": channel["text"]
    }
    if (publishedTime := obj.get("publishedTimeText")):
        playlist["updatedText"] = publishedTime.get("simpleText")
    return playlist

def extractShort(obj):
    endpoint = obj["onTap"]["innertubeCommand"]["reelWatchEndpoint"]
    metadata = obj["overlayMetadata"]
    short = {
        "type": "video",
        "videoId": endpoint["videoId"],
        "title": metadata["primaryText"]["content"],
        "thumbnail": getThumbnail(endpoint["thumbnail"])
    }
    if (viewCountText := metadata.get("secondaryText")):
        short["viewsText"] = viewCountText.get("content")
    return short

def extractGridPlaylist(obj):
    playlist = {
        "type": "playlist",
        "playlistId": obj["playlistId"],
        "title": joinRuns(obj["title"]),
        "thumbnail": getThumbnail(obj["thumbnail"]),
        "videosText": joinRuns(obj["videoCountText"])
    }
    if (publishedTime := obj.get("publishedTimeText")):
        playlist["updatedText"] = publishedTime.get("simpleText")
    return playlist

def extractRichItem(obj):
    return __extract__(obj["content"])


# ------------------------------------------------------------------------------

# this is all stupid :(

def extractLockupContentPlaylist(obj):
    #from nuttig import Logger
    #logger = Logger()
    #logger.info(f"extractLockupContentPlaylist()")
    #logger.info(f"extractLockupContentPlaylist(), obj={obj}")
    metadataViewModel = obj["metadata"]["lockupMetadataViewModel"]
    thumbnailViewModel = obj["contentImage"]["collectionThumbnailViewModel"]["primaryThumbnail"]["thumbnailViewModel"]
    playlist = {
        "type": "playlist",
        "playlistId": obj["contentId"],
        "title": metadataViewModel["title"]["content"],
        "thumbnail": getUrl(thumbnailViewModel["image"]["sources"][-1]["url"]),
        "videosText": traverse(
            thumbnailViewModel,
            "overlays",
            0,
            "thumbnailOverlayBadgeViewModel",
            "thumbnailBadges",
            0,
            "thumbnailBadgeViewModel",
            "text"
        ),
    }
    return playlist

def extractLockupContentVideo(obj):
    #from nuttig import Logger
    #logger = Logger()
    #logger.info(f"extractLockupContentVideo()")
    #logger.info(f"extractLockupContentVideo(), obj={obj}")
    metadataViewModel = obj["metadata"]["lockupMetadataViewModel"]
    thumbnailViewModel = obj["contentImage"]["thumbnailViewModel"]
    video = {
        "type": "video",
        "videoId": obj["contentId"],
        "title": metadataViewModel["title"]["content"],
        "thumbnail": getUrl(thumbnailViewModel["image"]["sources"][-1]["url"]),
    }
    durationText = traverse(
        thumbnailViewModel,
        "overlays",
        0,
        "thumbnailBottomOverlayViewModel",
        "badges",
        0,
        "thumbnailBadgeViewModel",
        "text"
    )
    if durationText:
        video["duration"] = getLengthSeconds(durationText)
    parts = traverse(
        metadataViewModel,
        "metadata",
        "contentMetadataViewModel",
        "metadataRows",
        0,
        "metadataParts"
    )
    if parts:
        if (viewsText := traverse(parts, 0, "text", "content")):
            video["viewsText"] = viewsText
        if (publishedText := traverse(parts, 1, "text", "content")):
            video["publishedText"] = publishedText
    return video

__lockupContentType__ = {
    "LOCKUP_CONTENT_TYPE_PLAYLIST": extractLockupContentPlaylist,
    "LOCKUP_CONTENT_TYPE_PODCAST": extractLockupContentPlaylist,
    "LOCKUP_CONTENT_TYPE_VIDEO": extractLockupContentVideo
}

def extractLockupViewModel(obj):
    return __lockupContentType__[obj["contentType"]](obj)


# ------------------------------------------------------------------------------

__extractors__ = {
    "videoRenderer": extractVideo,
    "channelRenderer": extractChannel,
    "playlistRenderer": extractPlaylist,
    "shortsLockupViewModel": extractShort,
    "gridPlaylistRenderer": extractGridPlaylist,
    "richItemRenderer": extractRichItem,
    "lockupViewModel": extractLockupViewModel
}

def __extract__(data, **defaults):
    for key, extractor in __extractors__.items():
        if ((obj := data.get(key)) and (extracted := extractor(obj))):
            return dict(extracted, **defaults)

def extractContent(data, **defaults):
    if (obj := data.get("continuationItemRenderer")):
        return (None, extractContinuation(obj))
    return (__extract__(data, **defaults), None)


# ------------------------------------------------------------------------------
# MyResults

def renderVideo(obj):
    channel = obj["ownerText"]["runs"][0]
    channelId = (
        traverse(
            channel, "navigationEndpoint", "browseEndpoint", "browseId"
        ) or
        traverse(
            channel,
            "navigationEndpoint",
            "showDialogCommand",
            "panelLoadingStrategy",
            "inlineContent",
            "dialogViewModel",
            "customContent",
            "listViewModel",
            "listItems",
            0,
            "listItemViewModel",
            "rendererContext",
            "commandContext",
            "onTap",
            "innertubeCommand",
            "browseEndpoint",
            "browseId"
        )
    )
    if channelId:
        yield dict(
            extractVideo(obj),
            channelId=channelId,
            channel=channel["text"]
        )

def renderChannel(obj):
    yield extractChannel(obj)

def renderPlaylist(obj):
    yield extractPlaylist(obj)

def renderShelf(obj):
    yield from __render__(obj["content"])

def renderLockupViewModel(obj):
    channelParts = traverse(
        obj,
        "metadata",
        "lockupMetadataViewModel",
        "metadata",
        "contentMetadataViewModel",
        "metadataRows",
        0,
        "metadataParts",
        0,
        "text",
        default={}
    )
    if (
        channelId := traverse(
            channelParts,
            "commandRuns",
            0,
            "onTap",
            "innertubeCommand",
            "browseEndpoint",
            "browseId"
        )
    ):
        yield dict(
            extractLockupViewModel(obj),
            channelId=channelId,
            channel=channelParts["content"]
        )

__renderers__ = {
    "videoRenderer": renderVideo,
    "channelRenderer": renderChannel,
    "playlistRenderer": renderPlaylist,
    "shelfRenderer": renderShelf,
    "lockupViewModel": renderLockupViewModel,
    "verticalListRenderer": lambda obj: renderList(obj["items"])
}

def __render__(content):
    for key, renderer in __renderers__.items():
        if ((obj := content.get(key)) and (rendered := renderer(obj))):
            yield from rendered

def renderList(items):
    for item in items:
        yield from __render__(item)

class MyResults(list):

    @staticmethod
    def extractResults(results, limit):
        items = list(
            renderList(
                traverse(
                    results, 0, "itemSectionRenderer", "contents", default=[]
                )
            )
        )
        next = None
        if (
            (len(items) >= limit) and
            (
                continuation := extractContinuation(
                    traverse(results, 1, "continuationItemRenderer", default={})
                )
            )
        ):
            next = {"continuation": continuation}
        return (items, next)

    def __init__(self, results, limit=10):
        super(MyResults, self).__init__(self.extractResults(results, limit))


# ------------------------------------------------------------------------------
# MyContents

class MyContents(list):

    @staticmethod
    def extractContents(data, **defaults):
        items = []
        next = None
        for obj in data:
            item, continuation = extractContent(obj, **defaults)
            if item:
                items.append(item)
            if continuation:
                next = {"continuation": continuation}
        return (items, next)

    def __init__(self, data, **defaults):
        super(MyContents, self).__init__(self.extractContents(data, **defaults))


# ------------------------------------------------------------------------------
# MyChannel

def extractParts(parts, delimiter):
    line = [
        text for part in parts
        if (text := traverse(part, "text", "content"))
    ]
    if line:
        return f" {delimiter} ".join(line)

def extractMetadata(metadata):
    if (
        (model := metadata.get("contentMetadataViewModel")) and
        (rows := model.get("metadataRows"))
    ):
        delimiter = model.get("delimiter", "-")
        lines = [
            line for row in rows
            if (
                (parts := row.get("metadataParts")) and
                (line := extractParts(parts, delimiter))
            )
        ]
        if lines:
            return f"\n".join(lines)


class MyChannel(dict):

    def __init__(self, data, expires=1800):
        metadata = data["metadata"]["channelMetadataRenderer"]
        if (
            subscribersText := traverse(
                data,
                "header",
                "pageHeaderRenderer",
                "content",
                "pageHeaderViewModel",
                "metadata"
            )
        ):
            subscribersText = extractMetadata(subscribersText)
        tabs = self.extractTabs(
            traverse(
                data,
                "contents",
                "twoColumnBrowseResultsRenderer",
                "tabs",
                default=[]
            )
        )
        super(MyChannel, self).__init__(
            type="channel",
            channelId=metadata["externalId"],
            channel=metadata["title"],
            description=metadata["description"],
            thumbnail=getThumbnail(metadata["avatar"]),
            subscribersText=subscribersText,
            tabs=tabs
        )
        self.__expires__ = (int(time()) + expires)

    def __repr__(self):
        return f"MyChannel({self['channel']}, tabs={list(self['tabs'].keys())})"

    __defaut_args__ = ("content", "richGridRenderer", "contents")

    __tabs__ = {
        "videos": __defaut_args__,
        "shorts": __defaut_args__,
        "streams": __defaut_args__,
        "playlists": (
            "content",
            "sectionListRenderer",
            "contents",
            0,
            "itemSectionRenderer",
            "contents",
            0,
            "gridRenderer",
            "items"
        )
    }

    def extractTabs(self, tabs):
        result = {}
        for tab in tabs:
            if (
                (renderer := tab.get("tabRenderer")) and
                (endpoint := renderer.get("endpoint")) and
                (
                    url := traverse(
                        endpoint, "commandMetadata", "webCommandMetadata", "url"
                    )
                ) and
                ((name := url.split("/")[-1]) in self.__tabs__) and
                (params := endpoint.get("browseEndpoint"))
            ):
                result[name] = {
                    "title": renderer["title"],
                    "action": name,
                    "params": params,
                    "properties": {"SpecialSort": "top"}
                }
        return result

    def extractData(self, key, data):
        tabs = traverse(
            data,
            "contents",
            "twoColumnBrowseResultsRenderer",
            "tabs",
            default=[]
        )
        if tabs:
            for tab in tabs:
                if (
                    (renderer := tab.get("tabRenderer")) and
                    (renderer.get("selected", False))
                ):
                    return traverse(renderer, *self.__tabs__[key], default=[])

    def extractContents(self, data):
        return MyContents(
            data, channelId=self["channelId"], channel=self["channel"]
        )


# ------------------------------------------------------------------------------
# MyVideo

class __MyVideo__(dict):

    def __init__(self, published=None, views=None, likes=None, **kwargs):
        if (published is not None):
            publishedText = localizedString(50101).format(published)
        else:
            publishedText = None
        if (views is not None):
            viewsText = localizedString(50102).format(views)
        else:
            viewsText = None
        if (likes is not None):
            likesText = localizedString(50103).format(likes)
        else:
            likesText = None
        super(__MyVideo__, self).__init__(
            kwargs,
            type="video",
            published=published,
            publishedText=publishedText,
            views=views,
            viewsText=viewsText,
            likes=likes,
            likesText=likesText
        )

    def __repr__(self):
        return f"MyVideo({self['videoId']})"


class __MyYtDlpVideo__(__MyVideo__):

    def __init__(self, info, **kwargs):
        if ((published := info.get("timestamp")) is not None):
            published = f"{__date__(published)}"
        super(__MyYtDlpVideo__, self).__init__(
            published=published,
            views=info.get("view_count"),
            likes=info.get("like_count"),
            title=info["title"],
            description=(info.get("description") or None),
            channelId=info["channel_id"],
            channel=info["channel"],
            duration=info["duration"],
            url=(info.get("url") or None),
            manifestType=(info.get("manifestType") or None),
            mimeType=(info.get("mimeType") or None),
            language=(info.get("language") or None),
            **kwargs
        )


class MyVideo(__MyYtDlpVideo__):

    def __init__(self, info, expires=1800):
        super(MyVideo, self).__init__(
            info,
            videoId=info["video_id"],
            live=info["is_live"],
            thumbnail=info["thumbnail"]
        )
        self.__expires__ = (int(time()) + expires)


# ------------------------------------------------------------------------------
# MyPlaylist

class MyPlaylistVideo(__MyYtDlpVideo__):

    def __init__(self, info):
        super(MyPlaylistVideo, self).__init__(
            info,
            videoId=info["id"],
            live=(info["live_status"] == "is_live"),
            thumbnail=getThumbnail(info)
        )

class MyPlaylist(dict):

    def __init__(self, info, expires=1800):
        if ((views := info.get("view_count")) is not None):
            viewsText = localizedString(50102).format(views)
        else:
            viewsText = None
        if ((videos := info.get("playlist_count")) is not None):
            videosText = localizedString(50301).format(videos)
        else:
            videosText = None
        if ((updated := info.get("modified_date")) is not None):
            updated = f"{__date__(updated)}"
            updatedText = localizedString(50302).format(updated)
        else:
            updatedText = None
        super(MyPlaylist, self).__init__(
            type="playlist",
            playlistId=info["id"],
            title=info["title"],
            description=(info.get("description") or None),
            channelId=info["channel_id"],
            channel=info["channel"],
            thumbnail=info["thumbnails"][-1]["url"],
            views=views,
            viewsText=viewsText,
            videos=videos,
            videosText=videosText,
            updated=updated,
            updatedText=updatedText
        )
        self.__expires__ = (int(time()) + expires)
        self.__entries__ = info["entries"]
        self.__videos__ = []
        self.__last__ = -1

    def __repr__(self):
        return f"MyPlaylist({self['playlistId']})"

    def videos(self, page=1, limit=29):
        page = int(page) or 1
        limit = int(limit) or 29
        if (self.__last__ < 0):
            while (len(self.__videos__) <= page):
                videos = [
                    MyPlaylistVideo(video)
                    for video in islice(self.__entries__, limit)
                    if (video.get("channel_id") and video.get("channel"))
                ]
                if not videos:
                    self.__last__ = len(self.__videos__)
                    break
                self.__videos__.append(videos)
        next = {"page": (page + 1)}
        if (((last := self.__last__) > -1) and (page >= last)):
            next = None
        try:
            items = self.__videos__[page - 1]
        except IndexError:
            items = []
        return (items, next)


# ------------------------------------------------------------------------------
# MyRss

class MyRssVideo(__MyVideo__):

    def __init__(self, entry):
        super(MyRssVideo, self).__init__(
            published=entry.get("published"),
            views=traverse(entry, "media_statistics", "views"),
            likes=traverse(entry, "media_starrating", "count"),
            videoId=entry["yt_videoid"],
            title=entry["title"],
            description=entry["summary"],
            channelId=entry["yt_channelid"],
            channel=entry["author"],
            thumbnail=entry["media_thumbnail"][0]["url"]
        )

class MyRss(list):

    def __init__(self, feed):
        super(MyRss, self).__init__(
            (MyRssVideo(entry) for entry in parse(feed)["entries"])
        )
