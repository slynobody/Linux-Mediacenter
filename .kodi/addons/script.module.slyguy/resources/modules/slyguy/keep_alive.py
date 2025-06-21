from time import time

from slyguy import router, log
from slyguy.util import run_plugin, get_addon
from slyguy.constants import ROUTE_KEEP_ALIVE
from slyguy.settings.db_storage import Settings
from slyguy.settings.types import BaseSettings


setting = BaseSettings.KEEP_ALIVE


class KeepAlive(object):
    def __init__(self):
        self._func = None
        self._interval = 0

    def register(self, func, hours=12, enable=True):
        if not enable:
            self.clear()
            return

        self._func = func
        self._interval = hours * 3600
        self._update_keep_alive()

    def clear(self):
        log.debug("Keep-alive disabled")
        setting.clear()

    def _update_keep_alive(self, interval=None, force=False):
        new_value = int(time() + (interval or self._interval))
        if force or (not setting.value or new_value < setting.value):
            log.debug("Next keep-alive: {}".format(new_value))
            setting.value = new_value

    def run(self):
        # addon that removed its register
        if not self._func:
            self.clear()
            return

        log.debug("Calling keep-alive method: {}".format(self._func.__name__))
        try:
            self._func()
        except Exception as e:
            self.log.warning("Keep-alive failed: {}. Trying again in 1 hour".format(e))
            # try again in an hour
            self._update_keep_alive(3600, force=True)
        finally:
            self._update_keep_alive(force=True)


keep_alive = KeepAlive()


def call_keep_alives():
    # TODO: check kodi is awake / has internet?
    query = (
        Settings
        .select(Settings.addon_id)
        .where(
            (Settings.key == setting.id) &
            (Settings.value != setting._default) &
            (Settings.value < int(time()))
        )
        .distinct()
        .order_by(Settings.value.asc()) # oldest value first
    )
    addon_ids = [x.addon_id for x in query]
    if not addon_ids:
        return

    for addon_id in addon_ids:
        addon = get_addon(addon_id, install=False, required=False)
        if not addon:
            continue

        path = router.url_for(ROUTE_KEEP_ALIVE, _addon_id=addon_id)
        log.debug("Calling keep-alive plugin: {}".format(path))
        run_plugin(path, wait=False)
        # only do one, next will run on next check
        break
