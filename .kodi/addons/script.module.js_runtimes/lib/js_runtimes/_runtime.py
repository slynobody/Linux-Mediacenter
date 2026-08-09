# -*- coding: utf-8 -*-


import abc
import contextlib
import os
import pathlib
import shutil
import stat
import subprocess
import tarfile
import traceback
import urllib.parse
import urllib.request
import zipfile

import xbmc, xbmcaddon, xbmcgui, xbmcvfs

from packaging.version import Version


# ------------------------------------------------------------------------------

@contextlib.contextmanager
def __busy__():
    xbmc.executebuiltin("ActivateWindow(busydialognocancel)")
    try:
        yield
    finally:
        xbmc.executebuiltin("Dialog.Close(busydialognocancel)")


# ------------------------------------------------------------------------------

__addon_id__ = "script.module.js_runtimes"
__addon__ = xbmcaddon.Addon(__addon_id__)
__addon_name__ = __addon__.getAddonInfo("name")

__base_path__ = pathlib.Path(
    xbmcvfs.translatePath(__addon__.getAddonInfo("profile"))
)

__progress__ = xbmcgui.DialogProgress()
__mode__ = (stat.S_IRWXU | stat.S_IRWXG | stat.S_IROTH | stat.S_IXOTH)

__headers__ = {"User-Agent": "Mozilla/5.0"}


# ------------------------------------------------------------------------------
# Runtime

class Runtime(abc.ABC):

    @staticmethod
    def __log__(msg, level=xbmc.LOGINFO):
        xbmc.log(f"[{__addon_id__}] {msg}", level=level)

    @staticmethod
    def __run__(*args, check=True):
        return subprocess.run(
            args, check=check, stdout=subprocess.PIPE, text=True
        ).stdout.strip()

    @staticmethod
    def __localize__(_id_):
        return __addon__.getLocalizedString(_id_)

    # --------------------------------------------------------------------------

    @staticmethod
    def __progress_create__(heading):
        __progress__.create(__addon_name__, heading)

    @staticmethod
    def __progress_update__(blocks_count, block_size, total_size):
        __progress__.update(((blocks_count * block_size) * 100) // total_size)

    @staticmethod
    def __progress_close__():
        __progress__.close()

    # --------------------------------------------------------------------------

    __opener__ = urllib.request.build_opener()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        for k in ("key", "name", "url"):
            if (k not in (infos := cls.__infos__)):
                raise TypeError(f"missing info: '{k}'")
        infos["url"] = urllib.parse.urlparse(infos["url"])
        infos["path"] = __base_path__.joinpath(
            (key := infos["key"]), infos.setdefault("bin", key)
        )
        cls.__opener__.addheaders = list(
            infos.setdefault("headers", __headers__).items()
        )

    # --------------------------------------------------------------------------

    @abc.abstractmethod
    def _current_version_args(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _latest_version_url(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _download_url(self):
        raise NotImplementedError

    @abc.abstractmethod
    def _binary_path(self):
        raise NotImplementedError

    # --------------------------------------------------------------------------

    @classmethod
    def _key(cls):
        return cls.__infos__["key"]

    @property
    def key(self):
        return self._key()

    @property
    def name(self):
        return self.__infos__["name"]

    @property
    def _url(self):
        return self.__infos__["url"]

    @property
    def url(self):
        return self._url.geturl()

    @property
    def _path(self):
        return self.__infos__["path"]

    @property
    def path(self):
        return f"{self._path}"

    @property
    def installed(self):
        return ((path := self._path).is_file() and os.access(path, os.X_OK))

    @property
    def version(self):
        if self.installed:
            return self.current

    # --------------------------------------------------------------------------

    def _get_current(self):
        args, kwargs = self._current_version_args()
        return self.__run__(self.path, *args, **kwargs)

    @property
    def current(self):
        if not self.__current__:
            self.__current__ =  self._get_current()
        return self.__current__

    # --------------------------------------------------------------------------

    def _get_latest(self):
        with __busy__():
            with urllib.request.urlopen(self._latest_version_url()) as response:
                return response.read().decode("utf-8").strip()

    @property
    def latest(self):
        if not self.__latest__:
            self.__latest__ = self._get_latest()
        return self.__latest__

    # --------------------------------------------------------------------------

    def _version(self, version):
        return Version(version)

    def _msg(self, _id_, *args):
        return self.__localize__(_id_).format(*args)

    def _label(self, _id_):
        if not self.__label__:
            self.__label__ = f"{self.name} {self.latest}"
        return self._msg(_id_, self.__label__)

    def _download(self, url):
        self.__progress_create__(self._label(30004))
        try:
            path, _ = urllib.request.urlretrieve(
                url, reporthook=self.__progress_update__
            )
            return path
        finally:
            self.__progress_close__()

    def _extract(self, path):
        with __busy__():
            if zipfile.is_zipfile(path):
                with zipfile.ZipFile(path, "r") as zip_file:
                    return zip_file.read(self._binary_path())
            elif tarfile.is_tarfile(path):
                with tarfile.open(path, "r") as tar_file:
                    return tar_file.extractfile(self._binary_path()).read()
            else:
                raise RuntimeError("Unsupported archive type")

    @property
    def outdated(self):
        try:
            return (self._version(self.current) < self._version(self.latest))
        except Exception:
            self.__log__(
                f"{self._msg(30007, self.name)}:\n{traceback.format_exc()}",
                level=xbmc.LOGERROR
            )
            return False

    @property
    def confirmed(self):
        if self.__confirmed__ is None:
            try:
                label = self._label(30002)
            except Exception:
                self.__log__(
                    f"{self._msg(30009, self.name)}:\n{traceback.format_exc()}",
                    level=xbmc.LOGERROR
                )
            else:
                self.__confirmed__ = xbmcgui.Dialog().yesno(
                    __addon_name__, label
                )
        return self.__confirmed__

    def install(self):
        self.__log__(self._label(30003))
        path = self._download(self._download_url())
        try:
            os.makedirs(self._path.parent, exist_ok=True)
            self._path.write_bytes(self._extract(path))
            self._path.chmod(__mode__)
        finally:
            pathlib.Path(path).unlink()
        self.__current__ = None
        self.__log__((msg := self._label(30005)))
        xbmcgui.Dialog().ok(__addon_name__, msg)

    def check(self):
        _opener = urllib.request._opener
        urllib.request.install_opener(self.__opener__)
        try:
            if (((not self.installed) or self.outdated) and self.confirmed):
                try:
                    self.install()
                except Exception:
                    msg = self._msg(30008, self.name)
                    self.__log__(
                        f"{msg}:\n{traceback.format_exc()}", level=xbmc.LOGERROR
                    )
                    xbmcgui.Dialog().notification(
                        __addon_name__, msg, xbmcgui.NOTIFICATION_ERROR
                    )
        finally:
            urllib.request.install_opener(_opener)

    # --------------------------------------------------------------------------

    def __init__(self):
        self.__current__ = None
        self.__latest__ = None
        self.__label__ = None
        self.__confirmed__ = None

    # --------------------------------------------------------------------------

    def info(self):
        installed = self.installed
        result = dict(name=self.name, installed=installed, url=self.url)
        if installed:
            result.update((k, getattr(self, k)) for k in ("path", "version"))
        return result

    def runtime(self):
        if self.installed:
            return {"path": self.path}

    def uninstall(self):
        if self.installed:
            shutil.rmtree(self._path.parent)
            xbmcgui.Dialog().ok(__addon_name__, self._msg(30006, self.name))
            self.__init__()
