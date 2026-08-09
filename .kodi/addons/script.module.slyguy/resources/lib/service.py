import sys
import uuid
from ssl import OPENSSL_VERSION
from time import time

from slyguy import monitor, gui, settings, log, check_donor, is_donor, set_drm_level, _
from slyguy.keep_alive import call_keep_alives
from slyguy.session import Session
from slyguy.util import get_system_arch
from slyguy.constants import KODI_VERSION
from slyguy.settings.db_storage import db

from .proxy import Proxy
from .player import Player
from .util import check_updates, check_repo
from .constants import *


def _check_news():
    _time = int(time())
    if _time < settings.getInt('_last_news_check', 0) + NEWS_CHECK_TIME:
        return

    settings.setInt('_last_news_check', _time)

    with Session(timeout=15) as session:
        news = session.gz_json(NEWS_URL)
    if not news:
        return

    if 'id' not in news or news['id'] == settings.get('_last_news_id'):
        return
    settings.set('_last_news_id', news['id'])
    settings.setDict('_news', news)


def check_arch():
    arch = get_system_arch()[1]
    mac = int(uuid.getnode())

    prev_mac = settings.getInt('_mac')
    prev_arch = settings.get('_arch')
    settings.set('_arch', arch)
    settings.setInt('_mac', mac)
    if not prev_mac or not prev_arch:
        return

    if prev_mac == mac and prev_arch != arch:
        gui.ok(_(_.ARCH_CHANGED, old=prev_arch, new=arch))


def run():
    try:
        _run()
    except Exception as e:
        log.exception(e)
        gui.exception()


def _run():
    system, arch = get_system_arch()
    log.info('Shared Service: Started')
    log.info('Kodi Version: {}'.format(KODI_VERSION))
    log.info('System: {}, Arch: {}'.format(system, arch))
    log.info('Python Version: {}'.format(sys.version))
    log.info('OpenSSL Version: {}'.format(OPENSSL_VERSION))  # 17.6/18.9: 1.0.2j  19.5: 1.1.1d  20/21: 1.1.1q

    try:
        # updates at start may already have called abort
        if not monitor.abortRequested():
            player = Player()
            proxy = Proxy()
            proxy.start()

            check_donor(force=True)
            if is_donor():
                log.info("Welcome SlyGuy Supporter!")
            else:
                log.info("Visit donate.slyguy.uk to become a supporter and unlock perks!")

            set_drm_level()
            check_arch()

        ## Inital wait on boot
        monitor.waitForAbort(10)

        # run service loop
        while not monitor.abortRequested():
            try:
                settings.reset()
                check_donor()

                if is_donor() and settings.getBool('fast_updates'):
                    check_updates()

                if not is_donor() or settings.getBool('show_news'):
                    _check_news()

                call_keep_alives()
                check_repo()
            except Exception as e:
                log.exception(e)
                log.warning('Service loop failed')

            if monitor.waitForAbort(30):
                break
    except KeyboardInterrupt:
        pass
    finally:
        try: proxy.stop()
        except: pass

        try: del player
        except: pass

        try: db.close()
        except: pass
        log.info('Shared Service: Stopped')
