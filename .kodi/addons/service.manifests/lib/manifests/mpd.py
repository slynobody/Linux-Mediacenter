# -*- coding: utf-8 -*-


import collections
import io
import math
import xml.etree.ElementTree as ET


# ------------------------------------------------------------------------------
# Options

Options = collections.namedtuple(
    "Options", ("lang", "original", "default", "impaired")
)


# ------------------------------------------------------------------------------
# DashElement

class DashElement(ET.Element):

    @staticmethod
    def duration(arg):
        return f"PT{(math.floor(float(arg) * 10)/10.0):.1f}S"

    @staticmethod
    def range(**kwargs):
        return "{start}-{end}".format(**kwargs)

    __defaults__ = {}

    def __init__(self, **kwargs):
        super(DashElement, self).__init__(
            self.__class__.__name__, attrib=self.__defaults__, **kwargs
        )

    def toString(self):
        with io.BytesIO() as stream:
            ET.ElementTree(self).write(
                stream, encoding="UTF-8", xml_declaration=True, method="xml"
            )
            return stream.getvalue()


# ------------------------------------------------------------------------------
# Initialization

class Initialization(DashElement):

    def __init__(self, **initRange):
        super(Initialization, self).__init__(range=self.range(**initRange))


# ------------------------------------------------------------------------------
# SegmentBase

class SegmentBase(DashElement):

    def __init__(self, indexRange, data):
        super(SegmentBase, self).__init__(indexRange=self.range(**indexRange))
        if (initRange := data.get("initRange", {})):
            self.append(Initialization(**initRange))


# ------------------------------------------------------------------------------
# BaseURL

class BaseURL(DashElement):

    def __init__(self, url):
        super(BaseURL, self).__init__()
        self.text = url


# ------------------------------------------------------------------------------
# AudioChannelConfiguration

class AudioChannelConfiguration(DashElement):

    __defaults__ = {
        "schemeIdUri": "urn:mpeg:dash:23003:3:audio_channel_configuration:2011"
    }

    def __init__(self, audioChannels):
        super(AudioChannelConfiguration, self).__init__(value=audioChannels)


# ------------------------------------------------------------------------------
# Representation

class Representation(DashElement):

    def __init__(self, data):
        kwargs = {
            "id": data["id"]
        }
        #codecs
        if (codecs := data.get("codecs")):
            kwargs["codecs"] = codecs
        #bandwidth
        if (bandwidth := data.get("bandwidth", 0)):
            kwargs["bandwidth"] = str(bandwidth)
        # width
        if (width := data.get("width", 0)):
            kwargs["width"] = str(width)
        # height
        if (height := data.get("height", 0)):
            kwargs["height"] = str(height)
        # frameRate
        if (frameRate := data.get("frameRate", 0)):
            kwargs["frameRate"] = str(frameRate)
        # audioSamplingRate
        if (audioSamplingRate := data.get("audioSamplingRate", 0)):
            kwargs["audioSamplingRate"] = str(audioSamplingRate)
        super(Representation, self).__init__(**kwargs)
        if (audioChannels := data.get("audioChannels", 0)):
            self.append(AudioChannelConfiguration(str(audioChannels)))
        self.append(BaseURL(data["url"]))
        if (indexRange := data.get("indexRange", {})):
            self.append(SegmentBase(indexRange, data))


# ------------------------------------------------------------------------------
# AdaptationSet

class AdaptationSet(DashElement):

    __defaults__ = {
        #"segmentAlignment": "true",
        #"startWithSAP": "1",
        #"subsegmentAlignment": "true",
        #"subsegmentStartsWithSAP": "1",
        #"bitstreamSwitching": "true"
    }

    def __init__(self, id, contentType, mimeType, options, data):
        kwargs = {
            "id": id,
            "contentType": contentType,
            "mimeType": mimeType
        }
        if any(options):
            kwargs.update(
                {
                    k: v if isinstance(v, str) else str(v).lower()
                    for k, v in options._asdict().items() if v
                }
            )
        super(AdaptationSet, self).__init__(**kwargs)
        self.extend(Representation(d) for d in data)


# ------------------------------------------------------------------------------
# Period

class Period(DashElement):

    __defaults__ = {
        "start": "PT0.0S"
    }

    def __init__(self, duration, data):
        super(Period, self).__init__(duration=self.duration(duration))
        self.extend(
            AdaptationSet(str(id), *k, v)
            for id, (k, v) in enumerate(data.items())
        )


# ------------------------------------------------------------------------------
# MPD

class MPD(DashElement):

    __defaults__ = {
        "xmlns": "urn:mpeg:dash:schema:mpd:2011",
        "profiles": "urn:mpeg:dash:profile:full:2011",
        "minBufferTime": "PT1.5S",
        #"type": "static"
    }

    def __init__(self, duration, data):
        super(MPD, self).__init__(
            mediaPresentationDuration=self.duration(duration)
        )
        self.append(Period(duration, data))


# ------------------------------------------------------------------------------
# manifest

def manifest(duration, streams):
    data = {}
    for stream in streams:
        key = (
            stream["contentType"],
            stream["mimeType"],
            Options(
                stream.get("lang"),
                stream.get("original", False),
                stream.get("default", False),
                stream.get("impaired", False)

            )
        )
        data.setdefault(key, []).append(stream)
    return (MPD(duration, data).toString(), "application/dash+xml")
