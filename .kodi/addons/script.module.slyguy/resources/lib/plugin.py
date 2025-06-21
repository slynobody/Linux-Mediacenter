from kodi_six import xbmcaddon

from slyguy import plugin, gui, _
from slyguy.settings import reset_addon
from slyguy.settings.types import STORAGE
from slyguy.util import get_kodi_setting
from slyguy.constants import ROUTE_SETTINGS

from .util import check_updates


@plugin.route('')
def home(**kwargs):
    folder = plugin.Folder(_.SETTINGS)

    folder.add_item(
        label = _.COMMON,
        path = plugin.url_for(ROUTE_SETTINGS),
        bookmark = False,
    )

    addons = []
    for addon_id in STORAGE.get_addon_ids():
        try:
            addons.append(xbmcaddon.Addon(addon_id))
        except:
            continue

    for addon in sorted(addons, key=lambda x: x.getAddonInfo('name')):
        folder.add_item(
            label = addon.getAddonInfo('name'),
            art = {'thumb': addon.getAddonInfo('icon')},
            path = plugin.url_for(ROUTE_SETTINGS, _addon_id=addon.getAddonInfo('id')),
            bookmark = False,
            context = ((_.RESET_ADDON, 'RunPlugin({})'.format(plugin.url_for(reset, addon_id=addon.getAddonInfo('id')))),),
        )

    return folder


@plugin.route()
def reset(addon_id, **kwargs):
    if reset_addon(addon_id):
        gui.refresh()


@plugin.route()
def update_addons(**kwargs):
    updates = check_updates(force=True)
    if not updates:
        return gui.ok(_.NO_UPDATES)

    try:
        auto_updates = int(get_kodi_setting('general.addonupdates')) == 0
    except:
        auto_updates = False

    text = u''
    for addon_id in updates:
        update = updates[addon_id]
        text += u'{} {} > {}\n'.format(update['name'], update['cur'], update['new'])
    text = text.rstrip()

    if auto_updates:
        text = _(_.UPDATES_INSTALLED, count=len(updates), updates=text)
    else:
        text = _(_.UPDATES_AVAILABLE, count=len(updates), updates=text)

    gui.text(text)
