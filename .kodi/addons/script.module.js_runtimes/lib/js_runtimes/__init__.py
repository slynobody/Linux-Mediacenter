# -*- coding: utf-8 -*-


import json
import platform

from ._runtime import Runtime


# ------------------------------------------------------------------------------

__machine__ = platform.machine()
#__system__ = platform.system().lower()


# ------------------------------------------------------------------------------
# BunRuntime

class BunRuntime(Runtime):

    __infos__ = {
        "key": "bun",
        "name": "Bun",
        "url": "https://github.com/oven-sh/bun"
    }

    # --------------------------------------------------------------------------

    def _get_latest(self):
        return json.loads(super()._get_latest())["tag_name"].split("-")[-1]

    # --------------------------------------------------------------------------

    def _current_version_args(self):
        return (("-p", "Bun.version"), {})

    def _latest_version_url(self):
        # https://github.com/oven-sh/bun/raw/refs/heads/main/LATEST
        #return self._url._replace(
        #    path=f"{self._url.path}/raw/refs/heads/main/LATEST"
        #).geturl()
        return "https://api.github.com/repos/oven-sh/bun/releases/latest"

    __machines__ = {
        "arm64": "aarch64",
        "x86_64": "x64"
    }

    def __target__(self):
        return "bun-linux-{}".format(
            self.__machines__.get(__machine__, __machine__)
        )

    def _download_url(self):
        # https://github.com/oven-sh/bun/releases/download/bun-v1.3.10/bun-linux-x64.zip
        return self._url._replace(
            path="{}/releases/download/bun-{}/{}.zip".format(
                self._url.path, self.latest, self.__target__()
            )
        ).geturl()

    def _binary_path(self):
        return f"{self.__target__()}/bun"


# ------------------------------------------------------------------------------
# DenoRuntime

class DenoRuntime(Runtime):

    __infos__ = {
        "key": "deno",
        "name": "Deno",
        "url": "https://dl.deno.land"
    }

    # --------------------------------------------------------------------------

    def _current_version_args(self):
        return (("eval", "-p", "Deno.version.deno"), {})

    def _latest_version_url(self):
        # https://dl.deno.land/release-latest.txt
        return self._url._replace(path="release-latest.txt").geturl()

    __machines__ = {
        "arm64": "aarch64"
    }

    def __target__(self):
        return "deno-{}-unknown-linux-gnu".format(
            self.__machines__.get(__machine__, __machine__)
        )

    def _download_url(self):
        # https://dl.deno.land/release/v2.7.7/deno-x86_64-unknown-linux-gnu.zip
        return self._url._replace(
            path="release/{}/{}.zip".format(self.latest, self.__target__())
        ).geturl()

    def _binary_path(self):
        return "deno"


# ------------------------------------------------------------------------------
# NodeRuntime

class NodeRuntime(Runtime):

    __infos__ = {
        "key": "node",
        "name": "Node.js",
        "url": "https://nodejs.org/"
    }

    # --------------------------------------------------------------------------

    def _get_latest(self):
        return json.loads(super()._get_latest())[0]["version"]

    # --------------------------------------------------------------------------

    def _current_version_args(self):
        return (("-p", "process.version"), {})

    def _latest_version_url(self):
        # https://nodejs.org/dist/index.json
        return self._url._replace(path="dist/index.json").geturl()

    __machines__ = {
        "x86_64": "x64"
    }

    def __target__(self):
        return "node-{}-linux-{}".format(
            self.latest, self.__machines__.get(__machine__, __machine__)
        )

    def _download_url(self):
        # https://nodejs.org/dist/v25.8.1/node-v25.8.1-linux-x64.tar.xz
        return self._url._replace(
            path="dist/{}/{}.tar.xz".format(self.latest, self.__target__())
        ).geturl()

    def _binary_path(self):
        return f"{self.__target__()}/bin/node"


# ------------------------------------------------------------------------------
# QuickJSRuntime

class QuickJSRuntime(Runtime):

    __infos__ = {
        "key": "quickjs",
        "name": "QuickJS",
        "url": "https://bellard.org/quickjs",
        "bin": "qjs"
    }

    # --------------------------------------------------------------------------

    def _get_current(self):
        return super()._get_current().splitlines()[0].split(" ")[-1]

    def _get_latest(self):
        return json.loads(super()._get_latest())["version"]

    def _version(self, version):
        return super()._version(version.replace("-", "."))

    # --------------------------------------------------------------------------

    def _current_version_args(self):
        return (("-h", ), {"check": False})

    def _latest_version_url(self):
        # https://bellard.org/quickjs/binary_releases/LATEST.json
        return self._url._replace(
            path=f"{self._url.path}//binary_releases/LATEST.json"
        ).geturl()

    def __target__(self):
        return "quickjs-linux-{}".format(__machine__)

    def _download_url(self):
        # https://bellard.org/quickjs/binary_releases/quickjs-linux-x86_64-2025-09-13.zip
        return self._url._replace(
            path="{}/binary_releases/{}-{}.zip".format(
                self._url.path, self.__target__(), self.latest
            )
        ).geturl()

    def _binary_path(self):
        return "qjs"


# ------------------------------------------------------------------------------

class Runtimes(dict):

    def __missing__(self, key):
        raise RuntimeError(f"JavaScript runtime '{key}' not found")

    def __init__(self, *runtimes):
        super().__init__((rt._key(), rt()) for rt in runtimes)


__runtimes__ = Runtimes(DenoRuntime, NodeRuntime, QuickJSRuntime)
__deprecated__ = Runtimes(BunRuntime)


# ------------------------------------------------------------------------------

def info(key):
    return __runtimes__[key].info()

def runtime(key, force=False):
    if (rt := __deprecated__.get(key)):
        rt.uninstall()
    else:
        rt = __runtimes__[key]
        if force:
            rt.__init__()
        rt.check()
        if rt.installed:
            return rt.runtime()

def uninstall(key):
    __runtimes__[key].uninstall()


def infos():
    return {k: rt.info() for k, rt in __runtimes__.items()}

def runtimes(key="deno"):
    __runtimes__[key].check()
    return {k: rt.runtime() for k, rt in __runtimes__.items() if rt.installed}
