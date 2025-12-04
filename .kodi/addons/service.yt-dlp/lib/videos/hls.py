# -*- coding: utf-8 -*-


from videos import defaultResolution, languages, NoneCodec


# streams ----------------------------------------------------------------------

def __subtitles__(subtitles):
    return [
        dict(
            language=subtitle["language"],
            name=subtitle["name"],
            uri=subtitle["uri"]
        )
        for subtitle in subtitles
        if (subtitle["protocol"] == "m3u8_native")
    ]


def streams(video, formats, subtitles, height=None, track=None, **kwargs):
    streams = []
    groups = {group_type: {} for group_type in ("video", "audio")}
    subtitles = __subtitles__(subtitles)
    for f in formats:
        if f.get("protocol", "") == "m3u8_native":
            vcodec = (
                ((vcodec := f.get("vcodec", NoneCodec)) != NoneCodec) and vcodec
            )
            acodec = (
                ((acodec := f.get("acodec", NoneCodec)) != NoneCodec) and acodec
            )
            if (codecs := [codec for codec in (vcodec, acodec) if codec]):
                stream = {
                    "codecs": ",".join(codecs),
                    "bandwidth": f["tbr"] * 1000,
                    "url": f["url"]
                }
                if (vcodec and (resolution := f.get("resolution"))):
                    default = (height and defaultResolution(f, height))
                    autoselect = "YES" if default else "NO"
                    stream["resolution"] = resolution
                    if (fps := f.get("fps")):
                        stream["frame_rate"] = fps
                        resolution = f"{resolution}@{int(fps)}"
                    groups["video"][resolution] = { # setdefault?
                        "name": resolution,
                        "default": autoselect,
                        "autoselect": autoselect
                    }
                    stream["video"] = resolution
                if (
                    acodec and
                    (language := f.get("language")) and
                    (name := languages.language_name(language))
                ):
                    original = (f.get("language_preference", -1) == 10)
                    default = language.startswith(track) if track else original
                    autoselect = "YES" if default else "NO"
                    groups["audio"][language] = { # setdefault?
                        "name": name,
                        "language": language,
                        "default": autoselect,
                        "autoselect": autoselect
                    }
                    stream["audio"] = language
                if subtitles:
                    stream["subtitles"] = "subtitles"
                streams.append(stream)
    return (streams, groups, subtitles)
