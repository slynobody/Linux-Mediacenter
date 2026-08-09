# -*- coding: utf-8 -*-


from m3u8 import M3U8, Media, Playlist


# ------------------------------------------------------------------------------
# manifest

def manifest(streams, groups, subtitles, version=7):
    playlist = M3U8()
    for _type_, medias in groups.items():
        for _id_, media in medias.items():
            playlist.add_media(
                Media(type=_type_.upper(), group_id=_id_, **media)
            )
    for subtitle in subtitles:
        playlist.add_media(
            Media(type="SUBTITLES", group_id="subtitles", **subtitle)
        )
    for stream in streams:
        playlist.add_playlist(
            Playlist(stream["url"], stream, playlist.media, None)
        )
    playlist.version = version
    return (playlist.dumps(), "application/x-mpegURL")
