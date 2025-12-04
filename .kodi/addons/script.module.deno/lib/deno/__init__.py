# -*- coding: utf-8 -*-


import os
import pathlib
import platform
import shutil
import stat
import subprocess
import urllib
import zipfile

import xbmc, xbmcaddon, xbmcgui, xbmcvfs

from packaging.version import Version


# ------------------------------------------------------------------------------
# Runtime

class Runtime(object):

    __runtime_name__ = "Deno"
    __runtime_desc__ = "Deno JavaScript Runtime"
    __runtime_id__ = "deno"
    __runtime_exe__ = "deno"
    __runtime_url__ = "https://dl.deno.land"

    # --------------------------------------------------------------------------

    __addon_id__ = f"script.module.{__runtime_id__}"
    __addon__ = xbmcaddon.Addon(__addon_id__)

    __path__ = pathlib.Path(
        xbmcvfs.translatePath(__addon__.getAddonInfo("profile")),
        __runtime_exe__
    )
    __url__ = urllib.parse.urlparse(__runtime_url__)

    __progress__ = xbmcgui.DialogProgress()
    __mode__ = (stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)

    __current_version__ = None
    __latest_version__ = None
    __label_version__ = None
    __confirmed__ = None

    # --------------------------------------------------------------------------

    @classmethod
    def __log__(cls, msg, level=xbmc.LOGINFO):
        xbmc.log(f"[{cls.__addon_id__}] {msg}", level=level)

    @classmethod
    def __string__(cls, _id_):
        return cls.__addon__.getLocalizedString(_id_)

    @classmethod
    def __run__(cls, *args, check=True):
        return subprocess.run(
            args, check=check, stdout=subprocess.PIPE, text=True
        ).stdout.strip()

    @classmethod
    def __update__(cls, block_count, block_size, total_size):
        cls.__progress__.update(
            ((block_count * block_size) * 100) // total_size
        )

    # --------------------------------------------------------------------------

    @classmethod
    def __installed__(cls):
        return (cls.__path__.is_file() and os.access(cls.__path__, os.X_OK))

    @classmethod
    def __current__(cls):
        if not cls.__current_version__:
            cls.__current_version__ =  cls.__get_current__()
        return cls.__current_version__

    @classmethod
    def __latest__(cls):
        if not cls.__latest_version__:
            cls.__latest_version__ = cls.__get_latest__()
        return cls.__latest_version__

    @classmethod
    def __label__(cls):
        if not cls.__label_version__:
            cls.__label_version__ = f"{cls.__runtime_name__} {cls.__latest__()}"
        return cls.__label_version__

    @classmethod
    def __version__(cls, version):
        return Version(cls.__get_version__(version))

    @classmethod
    def __outdated__(cls):
        return (
            cls.__version__(cls.__current__()) <
            cls.__version__(cls.__latest__())
        )

    @classmethod
    def __confirm__(cls):
        if cls.__confirmed__ is None:
            cls.__confirmed__ = xbmcgui.Dialog().yesno(
                cls.__runtime_desc__,
                cls.__string__(30002).format(cls.__label__())
            )
        return cls.__confirmed__

    @classmethod
    def __target__(cls):
        return cls.__url__._replace(path=f"{cls.__get_target__()}.zip").geturl()

    @classmethod
    def __install__(cls):
        cls.__log__(cls.__string__(30003).format(cls.__label__()))
        cls.__progress__.create(
            cls.__runtime_desc__, cls.__string__(30004).format(cls.__label__())
        )
        path, _ = urllib.request.urlretrieve(
            cls.__target__(), reporthook=cls.__update__
        )
        cls.__progress__.close()
        os.makedirs(cls.__path__.parent, exist_ok=True)
        with zipfile.ZipFile(path, "r") as zip_file:
            zip_file.extract(cls.__runtime_exe__, path=cls.__path__.parent)
        pathlib.Path(path).unlink()
        cls.__path__.chmod(cls.__mode__)
        cls.__current_version__ = None
        xbmcgui.Dialog().ok(
            cls.__runtime_desc__, cls.__string__(30005).format(cls.__label__())
        )

    @classmethod
    def __uninstall__(cls):
        shutil.rmtree(cls.__path__.parent)
        xbmcgui.Dialog().ok(
            cls.__runtime_desc__,
            cls.__string__(30006).format(cls.__runtime_name__)
        )

    # --------------------------------------------------------------------------

    @classmethod
    def __get_version__(cls, version):
        return version

    @classmethod
    def __get_current__(cls):
        return cls.__run__(f"{cls.__path__}", "eval", "-p", "Deno.version.deno")

    @classmethod
    def __get_latest__(cls):
        with urllib.request.urlopen(
            cls.__url__._replace(path="release-latest.txt").geturl()
        ) as response:
            return response.read().decode("utf-8").strip()

    __systems__ = {
        "Linux": {
            "suffix": "unknown-linux-gnu"
        },
        "Darwin": {
            "suffix": "apple-darwin",
            "machines": {
                "arm64": "aarch64"
            }
        }
    }

    @classmethod
    def __get_target__(cls):
        system = cls.__systems__[platform.system()]
        machine = system.get("machines", {}).get(
            (machine := platform.machine()), machine
        )
        return "release/{}/{}-{}-{}".format(
            cls.__latest__(),
            cls.__runtime_id__,
            machine,
            system["suffix"]
        )

    # --------------------------------------------------------------------------

    def __init__(self):
        if (
            ((not self.__installed__()) or self.__outdated__()) and
            self.__confirm__()
        ):
            self.__install__()


# ------------------------------------------------------------------------------

def name():
    if ((runtime := Runtime()).__installed__()):
        return runtime.__runtime_name__

def path():
    if ((runtime := Runtime()).__installed__()):
        return str(runtime.__path__)

def version():
    if ((runtime := Runtime()).__installed__()):
        return str(runtime.__current__())
