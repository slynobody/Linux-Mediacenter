# -*- coding: utf-8 -*-


from iapc import Client
from nuttig import getSetting, localizedString


# ------------------------------------------------------------------------------
# YtDlpMpd

class __IntFramerate__(dict):

    def __missing__(self, key):
        return key

class __FloatFramerate__(__IntFramerate__):

    def __init__(self):
        super(__FloatFramerate__, self).__init__(
            {24: 23.976, 30: 29.97, 60: 59.94}
        )

class __NoFramerate__(dict):

    def __missing__(self, key):
        return 0


class YtDlpMpd(object):

    __service_id__ = "service.manifests.mpd"

    __fps_limits__ = {0: 32101, 30: 32102}

    __fps_hints__ = {
        "int":   {"label": 32201, "values": __IntFramerate__()},
        "float": {"label": 32202, "values": __FloatFramerate__()},
        "none":  {"label": 32203, "values": __NoFramerate__()}
    }

    __codecs__ = {
        "avc1": {"label": 33101, "names": ("avc1", )},
        "mp4a": {"label": 33102, "names": ("mp4a", )},
        "vp09": {"label": 33103, "names": ("vp09", "vp9")},
        "opus": {"label": 33104, "names": ("opus", )},
        "av01": {"label": 33105, "names": ("av01", )}
    }

    def __init__(self, logger):
        self.logger = logger.getLogger(component="mpd")
        self.__manifests__ = Client(self.__service_id__)
        self.__streamTypes__ = {
            "video": self.__video_stream__,
            "audio": self.__audio_stream__
        }
        self.__supportedSubtitles__ = ("vtt",)

    def __setup__(self):
        # fps limit
        self.__fps_limit__ = getSetting("fps.limit", int)
        self.logger.info(
            f"{localizedString(32100)}: "
            f"{localizedString(self.__fps_limits__[self.__fps_limit__])}"
        )
        # fps hint
        self.__fps_hint__ = getSetting("fps.hint", str)
        self.logger.info(
            f"{localizedString(32200)}: "
            f"{localizedString(self.__fps_hints__[self.__fps_hint__]['label'])}"
        )
        # exclude codecs
        self.__exclude__ = []
        labels = None
        if (exclude := getSetting("codecs.exclude")):
            self.__exclude__ = exclude.split(",")
            labels = ", ".join(
                localizedString(self.__codecs__[codec]["label"])
                for codec in self.__exclude__
            )
        self.logger.info(f"{localizedString(33100)}: {labels}")

    def __stop__(self):
        self.logger.info("stopped")

    # --------------------------------------------------------------------------

    def __excludes__(self, exclude):
        return tuple(
            name for codec in exclude
            for name in self.__codecs__[codec]["names"]
        )

    def __video_stream__(self, fmt, fps_limit=0, fps_hint="int", **kwargs):
        fmt_fps = fmt["fps"]
        if ((not fps_limit) or (fmt_fps <= fps_limit)):
            return {
                "lang": None,
                "averageBitrate": int(fmt["vbr"] * 1000),
                "width": fmt["width"],
                "height": fmt["height"],
                "frameRate": self.__fps_hints__[fps_hint]["values"][fmt_fps]
            }

    def __audio_stream__(self, fmt, **kwargs):
        return {
            "lang": fmt["language"],
            "averageBitrate": int(fmt["abr"] * 1000),
            "audioSamplingRate": fmt["asr"],
            "audioChannels": fmt.get("audio_channels", 2)
        }

    def __stream__(self, contentType, codecs, fmt, exclude=None, **kwargs):
        if (
            ((not exclude) or (not codecs.startswith(exclude))) and
            (stream := self.__streamTypes__[contentType](fmt, **kwargs))
        ):
            return dict(
                stream,
                contentType=contentType,
                mimeType=f"{contentType}/{fmt['ext']}",
                id=fmt["format_id"],
                codecs=codecs,
                #averageBitrate=int(fmt["tbr"] * 1000),
                url=fmt["url"],
                indexRange=fmt.get("indexRange", {}),
                initRange=fmt.get("initRange", {})
            )

    def __streams__(self, formats, **kwargs):
        for fmt in formats:
            if fmt.get("container", "").endswith("_dash"):
                args = None
                vcodec = fmt.get("vcodec")
                acodec = fmt.get("acodec")
                if (vcodec and (vcodec != "none") and (acodec == "none")):
                    args = ("video", vcodec)
                elif (acodec and (acodec != "none") and (vcodec == "none")):
                    args = ("audio", acodec)
                if args and (stream := self.__stream__(*args, fmt, **kwargs)):
                    yield stream

    def __subtitles__(self, subtitles):
        for lang, subs in subtitles.items():
            for sub in subs:
                if (
                    (id := sub.get("name")) and
                    ((ext := sub["ext"]) in self.__supportedSubtitles__)
                ):
                    yield dict(
                        contentType="text",
                        mimeType=f"text/{ext}",
                        lang=lang,
                        id=id,
                        url=sub["url"]
                    )

    def __manifest__(self, duration, formats, subtitles, **kwargs):
        if (streams := list(self.__streams__(formats, **kwargs))):
            streams.extend(self.__subtitles__(subtitles))
            return self.__manifests__.manifest(duration, streams)

    # manifest -----------------------------------------------------------------

    def manifest(
        self, *args, exclude=None, fps_limit=None, fps_hint=None, **kwargs
    ):
        self.logger.info(
            f"manifest("
                f"exclude={exclude}, "
                f"fps_limit={fps_limit}, "
                f"fps_hint={fps_hint}, "
                f"kwargs={kwargs}"
            f")"
        )
        exclude = exclude if exclude is not None else self.__exclude__
        fps_limit = fps_limit if fps_limit is not None else self.__fps_limit__
        fps_hint = fps_hint if fps_hint is not None else self.__fps_hint__
        return self.__manifest__(
            *args,
            exclude=self.__excludes__(exclude) if exclude else None,
            fps_limit=fps_limit,
            fps_hint=fps_hint,
            **kwargs
        )
