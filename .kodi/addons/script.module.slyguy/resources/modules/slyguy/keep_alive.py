from time import time

from slyguy import router, log
from slyguy.util import run_plugin, get_addon
from slyguy.constants import ROUTE_KEEP_ALIVE
from slyguy.settings.db_storage import Settings
from slyguy.settings.types import BaseSettings


setting = BaseSettings.KEEP_ALIVE
enabled = BaseSettings.KEEP_ALIVE_ENABLED

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

        self._update_keep_alive(force=True)
        log.debug("Calling keep-alive method: {}".format(self._func.__name__))
        try:
            self._func()
        except Exception as e:
            log.exception(e)
            log.warning("Keep-alive failed: {}. Trying again in 1 hour".format(e))
            self._update_keep_alive(3600, force=True)


keep_alive = KeepAlive()


def call_keep_alives():
    # TODO: check kodi is awake / has internet?
    query = (
        Settings
        .select(Settings.addon_id, Settings.key, Settings.value)
        .where(
            (
                (Settings.key == setting.id) &
                (Settings.value > 0) &
                (Settings.value < int(time()))
            ) |
            (
                (Settings.key == enabled.id) &
                (Settings.value == False)
            )
        )
        .order_by(Settings.value.asc())  # oldest value first
    )

    ignore = set()
    addon_ids = set()
    for row in query:
        addon_ids.add(row.addon_id)
        if row.key == 'keep_alive_enabled':
            ignore.add(row.addon_id)

    addon_ids = [x for x in addon_ids if x not in ignore]
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
