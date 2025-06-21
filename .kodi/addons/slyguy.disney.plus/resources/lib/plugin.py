import json
import time
from base64 import b64decode

import arrow
from slyguy import plugin, gui, userdata, signals, inputstream
from slyguy.exceptions import PluginError
from slyguy.constants import KODI_VERSION, NO_RESUME_TAG, ROUTE_RESUME_TAG
from slyguy.drm import is_wv_secure

from .api import API
from .constants import *
from .language import _
from .settings import settings, Ratio


api = API()


@signals.on(signals.BEFORE_DISPATCH)
def before_dispatch():
    api.new_session()
    plugin.logged_in = api.logged_in


@plugin.route('')
def index(**kwargs):
    folder = plugin.Folder(cacheToDisc=False)

    if not api.logged_in:
        folder.add_item(label=_(_.LOGIN, _bold=True), path=plugin.url_for(login), bookmark=False)
    else:
        folder.add_item(label=_(_.HOME, _bold=True), path=plugin.url_for(home))
        folder.add_item(label=_(_.BRANDS, _bold=True), path=plugin.url_for(brands))
        folder.add_item(label=_(_.MOVIES, _bold=True), path=plugin.url_for(movies))
        folder.add_item(label=_(_.SERIES, _bold=True), path=plugin.url_for(series))
        folder.add_item(label=_(_.ORIGINALS, _bold=True), path=plugin.url_for(originals))
        folder.add_item(label=_(_.SEARCH, _bold=True), path=plugin.url_for(search))

        if settings.SYNC_WATCHLIST.value:
            folder.add_item(label=_(_.WATCHLIST, _bold=True), path=plugin.url_for(watchlist))

        if settings.SYNC_PLAYBACK.value:
            folder.add_item(label=_(_.CONTINUE_WATCHING, _bold=True), path=plugin.url_for(continue_watching))

        if settings.BOOKMARKS.value:
            folder.add_item(label=_(_.BOOKMARKS, _bold=True), path=plugin.url_for(plugin.ROUTE_BOOKMARKS), bookmark=False)

        if not userdata.get('kid_lockdown', False):
            folder.add_item(label=_.SELECT_PROFILE, path=plugin.url_for(select_profile), art={'thumb': userdata.get('avatar')}, info={'plot': userdata.get('profile')}, _kiosk=False, bookmark=False)

        folder.add_item(label=_.LOGOUT, path=plugin.url_for(logout), _kiosk=False, bookmark=False)

    folder.add_item(label=_.SETTINGS, path=plugin.url_for(plugin.ROUTE_SETTINGS), _kiosk=False, bookmark=False)

    return folder


@plugin.route()
def home(**kwargs):
    return _deeplink_page('home')


@plugin.route()
def movies(**kwargs):
    return _deeplink_page('movies')


@plugin.route()
def series(**kwargs):
    return _deeplink_page('series')


@plugin.route()
def originals(**kwargs):
    return _deeplink_page('originals')


def _deeplink_page(ref_id):
    if not api.is_subscribed():
        gui.ok(_.NOT_SUBSCRIBER)
    data = api.deeplink(ref_id=ref_id)
    page_id = _get_actions(data)[BROWSE]['pageId']
    data = api.page(page_id, limit=1, enhanced_limit=99)
    return _process_rows(data)


@plugin.route()
@plugin.pagination()
def brands(page=1, **kwargs):
    data = api.set(BRANDS_ID, page=page)
    folder = _process_rows(data)
    return folder, data['pagination']['hasMore']


@plugin.route()
@plugin.pagination()
def continue_watching(page=1, **kwargs):
    data = api.set(CONTINUE_WATCHING_ID, page=page, _skip_cache=True)
    folder = _process_rows(data, title=_.CONTINUE_WATCHING, continue_watching=True)
    return folder, data['pagination']['hasMore']


@plugin.route()
def watchlist(**kwargs):
    data = api.deeplink(ref_id='watchlist')
    page_id = _get_actions(data)[BROWSE]['pageId']
    data = api.page(page_id, limit=1, enhanced_limit=15, _skip_cache=True)
    return _process_rows(data, title=_.WATCHLIST, watchlist=True, flatten=True)


@plugin.route()
def add_watchlist(deeplink_id, **kwargs):
    with gui.busy():
        data = api.page('entity-{}'.format(deeplink_id.replace('entity-', '')))
        info = _get_info(data)
        api.edit_watchlist('add', page_info=data['infoBlock'], action_info=info[ACTIONS][MODIFYSAVES]['infoBlock'])
    gui.notification(_.ADDED_WATCHLIST, heading=info['title'], icon=info['art'].get('poster') or info['art'].get('thumb'))


@plugin.route()
def delete_watchlist(deeplink_id, **kwargs):
    # TODO: remove list item and dont refresh
    with gui.busy():
        data = api.page('entity-{}'.format(deeplink_id.replace('entity-', '')))
        info = _get_info(data)
        api.edit_watchlist('remove', page_info=data['infoBlock'], action_info=info[ACTIONS][MODIFYSAVES]['infoBlock'])
        # above is async so wait a bit to make sure its removed from list refresh
        time.sleep(1.5)
    gui.refresh()


@plugin.route()
def remove_continue_watching(deeplink_id, **kwargs):
    # TODO: remove list item and dont refresh
    with gui.busy():
        data = api.page('entity-{}'.format(deeplink_id.replace('entity-', '')))
        info = _get_info(data)
        api.remove_continue_watching(action_info=info[ACTIONS][REMOVECONTINUEWATCHING]['infoBlock'])
        # above is async so wait a bit to make sure its removed from list refresh
        time.sleep(1.5)
    gui.refresh()


@plugin.route()
@plugin.search()
def search(query, page, **kwargs):
    data = api.search(query)
    return _process_rows(data['containers'][0]).items if data['containers'] else [], False


@plugin.route()
@plugin.no_error_gui()
def callback(media_id, fguid, _time, **kwargs):
    api.update_resume(media_id, fguid, int(_time))


@plugin.route()
def page(page_id, **kwargs):
    data = api.page(page_id, limit=1, enhanced_limit=99)
    return _process_rows(data, flatten=True)


@plugin.route()
@plugin.pagination()
def set(set_id, watchlist=0, page=1, **kwargs):
    data = api.set(set_id, page=page, _skip_cache=bool(int(watchlist)))
    folder = _process_rows(data, watchlist=bool(int(watchlist)))
    return folder, data['pagination']['hasMore']


@plugin.route()
@plugin.pagination()
def season(show_id, season_id, page=1, **kwargs):
    show_data = api.page(show_id)
    data = api.season(season_id, page=page)
    folder = _process_rows(data, title=show_data['visuals']['title'])
    show_art = _get_art(show_data)
    for key in show_art:
        if key != 'poster' and not folder.art.get(key):
            folder.art[key] = show_art[key]
    return folder, data['pagination']['hasMore']


def _get_actions(data):
    actions = {
        BROWSE: {},
        PLAYBACK: {},
        TRAILER: {},
        MODIFYSAVES: {},
        REMOVECONTINUEWATCHING: {},
        MODAL: {},
    }
    for row in data.get('actions', []):
        if row['type'] == 'browse':
            actions[BROWSE] = row
        elif row['type'] == 'playback':
            actions[PLAYBACK] = row
        elif row['type'] == 'trailer':
            actions[TRAILER] = row
        elif row['type'] == 'modifySaves':
            actions[MODIFYSAVES] = row
        elif row['type'] == 'contextMenu':
            for sub_row in row.get('actions', []):
                if sub_row['type'] == 'removeFromContinueWatching':
                    actions[REMOVECONTINUEWATCHING] = sub_row
        elif row['type'] == 'modal':
            actions[MODAL] = row
    actions[PLAYBACK] = actions[PLAYBACK] or actions[BROWSE]
    return actions


def _get_play_path(**kwargs):
    if not kwargs:
        return None

    profile_id = userdata.get('profile_id')
    if profile_id:
        kwargs['profile_id'] = profile_id

    return plugin.url_for(play, **kwargs)


def _get_info(data):
    actions = _get_actions(data)

    containers = {
        EPISODES: {'seasons': []},
        SUGGESTED: {},
        EXTRAS: {},
        DETAILS: {'visuals': {}},
    }
    for row in data.get('containers', []):
        if row['type'] == 'episodes':
            containers[EPISODES] = row
        elif row['type'] == 'details':
            containers[DETAILS] = row
        elif row.get('id') == SUGGESTED_ID:
            containers[SUGGESTED] = row
        elif row.get('id') == EXTRAS_ID:
            containers[EXTRAS] = row

    description = containers[DETAILS]['visuals'].get('description') or data['visuals'].get('description', {})
    plot = description.get('medium') or description.get('brief') or description.get('full')
    title = containers[DETAILS]['visuals'].get('title') or data['visuals'].get('title')

    # only works for episodes as movies in list views dont give us the legacy id
    legacy_id = actions[PLAYBACK].get('legacyPartnerFeed', {}).get('dmcContentId') or actions[PLAYBACK].get('partnerFeed',{}).get('dmcContentId')
    if legacy_id:
        # try keep old paths for kodi db watch status
        playpath = _get_play_path(content_id=legacy_id)
    elif 'deeplinkId' in actions[PLAYBACK]:
        # new content has no legacy ids, so needs to use deeplink
        playpath = _get_play_path(deeplink_id=actions[PLAYBACK]['deeplinkId'])
    else:
        playpath = None

    return {'title': title, 'plot': plot, CONTAINERS: containers, ACTIONS: actions, 'art': _get_art(data), 'playpath': playpath}


@plugin.route()
def show(show_id, **kwargs):
    data = api.page(show_id, limit=1, enhanced_limit=15)
    info = _get_info(data)

    folder = plugin.Folder(info['title'], art=info['art'])
    for row in info[CONTAINERS][EPISODES]['seasons']:
        folder.items.append(plugin.Item(
            label = row['visuals']['name'],
            info = {
                'plot': u'{}\n\n{}'.format(info['plot'], _(row['visuals']['episodeCountDisplayText'], _bold=True)),
                'tvshowtitle': info['title'],
                'mediatype': 'season',
            },
            art = _get_art(row),
            path = plugin.url_for(season, show_id=data['id'], season_id=row['id']),
        ))

    if info[ACTIONS][TRAILER]:
        folder.items.append(plugin.Item(
            label = _.TRAILER,
            info = {
                'plot': info['plot'],
                'mediatype': 'video',
            },
            path = plugin.url_for(play_trailer, deeplink_id=data['id']),
            playable = True,
            specialsort = 'bottom',
        ))

    if info[CONTAINERS][SUGGESTED]:
        folder.items.append(plugin.Item(
            label = _.SUGGESTED,
            info = {
                'plot': info['plot'],
            },
            path = plugin.url_for(suggested, deeplink_id=data['id']),
            specialsort = 'bottom',
        ))

    if info[CONTAINERS][EXTRAS]:
        folder.items.append(plugin.Item(
            label = _.EXTRAS,
            info = {
                'plot': info['plot'],
            },
            path = plugin.url_for(extras, deeplink_id=data['id']),
            specialsort = 'bottom',
        ))

    return folder


def _process_rows(data, title=None, watchlist=False, flatten=False, continue_watching=False):
    if not data or 'visuals' not in data:
        return plugin.Folder(title)

    title = title or data['visuals'].get('title') or data['visuals'].get('name')
    folder = plugin.Folder(title, art=_get_art(data))
    rows = data.get('containers') or data.get('items') or []

    user_states = {}
    if settings.SYNC_PLAYBACK.value:
        pids = [row.get('personalization',{}).get('pid') for row in rows if row['visuals'].get('durationMs')]
        pids = [x for x in pids if x]
        if pids:
            user_states = api.userstates(pids)

    items = []
    for row in rows:
        # flatten inline single heros
        if row['type'] == 'set' and row['style']['name'] == 'hero_inline_single' and len(row['items']) == 1:
            row = row['items'][0]

        if row['type'] == 'set':
            if 'hero' in row['style']['name'].lower() or 'brand' in row['style']['name'].lower() or 'continue_watching' in row['style']['name'].lower():
                continue

            kwargs = {'set_id': row['id']}
            if watchlist:
                kwargs['watchlist'] = 1

            item = plugin.Item(
                label = row['visuals']['name'],
                art = _get_art(row),
                path = plugin.url_for(set, **kwargs),
            )
            items.append(item)

        elif row.get('actions', []):
            # MOVIE / TV SHOW / EPISODE / REPLAY / LIVE
            item = _parse_row(row)
            _add_progress(user_states.get(row['personalization']['pid']), item)
            if settings.SYNC_WATCHLIST.value and watchlist:
                item.context = [x for x in item.context if x[0] != _.ADD_WATCHLIST]
                item.context.insert(0, (_.DELETE_WATCHLIST, 'RunPlugin({})'.format(plugin.url_for(delete_watchlist, deeplink_id=row['actions'][0]['deeplinkId']))))
            if settings.SYNC_PLAYBACK.value and continue_watching:
                item.context = [x for x in item.context if x[0] != _.ADD_WATCHLIST]
                item.context.insert(0, (_.REMOVE_CONTINUE_WATCHING, 'RunPlugin({})'.format(plugin.url_for(remove_continue_watching, deeplink_id=row['actions'][0]['deeplinkId']))))
            items.append(item)

    if flatten and len(items) == 1:
        return plugin.redirect(items[0].path)

    folder.add_items(items)
    return folder


def _parse_episode(data):
    info = _get_info(data)

    item = plugin.Item(
        label = data['visuals']['episodeTitle'],
        art = info['art'],
        info = {
            'plot': info['plot'],
            'season': data['visuals'].get('seasonNumber'),
            'episode': data['visuals'].get('episodeNumber'),
            'tvshowtitle': info['title'],
            'duration': int(data['visuals'].get('durationMs', 0) / 1000),
            'mediatype': 'episode',
        },
        playable = True,
        path = info['playpath'],
    )
    return item


def _parse_page(data):
    info = _get_info(data)

    item = plugin.Item(
        label = info['title'],
        art = info['art'],
        info = {
            'plot': info['plot'],
        },
        path = plugin.url_for(page, page_id=info[ACTIONS][BROWSE]['pageId']),
    )
    return item


def _parse_event(data):
    info = _get_info(data)
    meta = data['visuals'].get('metastringParts', {})
    is_live = data['visuals']['badging']['airingEventState']['state'] == 'live'
    actions = info[ACTIONS]
    if actions[MODAL]:
        actions = _get_actions(info[ACTIONS][MODAL])
        info['art'] = _get_art(info[ACTIONS][MODAL])

    if actions[PLAYBACK].get('contentType') == 'linear':
        start_time = arrow.get(data['visuals']['badging']['airingEventState']['timeline']['startTime']).to('local')
        end_time = arrow.get(data['visuals']['badging']['airingEventState']['timeline']['endTime']).to('local')
        plot = u'[B]{} - {}[/B]\n{}'.format(start_time.format('h:mmA').lower(), end_time.format('hh:mmA').lower(), info['title'])

        if data['visuals'].get('episodeTitle') and data['visuals']['episodeTitle'] != info['title']:
            try:
                plot += u'\n\nS{}:E{}\n{}'.format(data['visuals']['seasonNumber'], data['visuals']['episodeNumber'], data['visuals']['episodeTitle'])
            except KeyError:
                plot += u'\n\n{}'.format(data['visuals']['episodeTitle'])

        if info['plot']:
            plot += u'\n\n{}'.format(info['plot'])

        try:
            info['art']['clearlogo'] = 'https://disney.images.edge.bamgrid.com/ripcut-delivery/v2/variant/disney/{}/scale?width=800&aspectRatio=1.78'.format(
                data['visuals']['networkAttribution']['artwork']['brand']['logo']['2.00']['imageId'])
        except KeyError:
            pass

        resource_data = json.loads(b64decode(actions[PLAYBACK]['resourceId']).decode("utf-8"))
        item = plugin.Item(
            label = data['visuals']['networkAttribution']['ttsText'],
            info = {
                'plot': plot,
                'mediatype': 'video',
            },
            art = info['art'],
            playable = True,
            path = _get_play_path(channel_id=resource_data['channelId'], _is_live=True),
        )
        # if data['visuals'].get('episodeNumber'):
        #     item.context.append(("Play VOD", 'RunPlugin({})'.format(_get_play_path(deeplink_id=actions[PLAYBACK]['deeplinkId']))))
    else:
        item = plugin.Item(
            label = info['title'],
            art = info['art'],
            info = {
                'plot': info['plot'],
                'mediatype': 'video',
            },
            playable = True,
            path = _get_play_path(deeplink_id=actions[PLAYBACK]['deeplinkId'], _is_live=is_live),
        )
        if settings.SYNC_WATCHLIST.value:
            item.context.append((_.ADD_WATCHLIST, 'RunPlugin({})'.format(plugin.url_for(add_watchlist, deeplink_id=actions[PLAYBACK]['deeplinkId']))))
        # TODO: Watch from live / start

    if 'sportsLeague' in meta:
        league = meta['sportsLeague']['name']
        if 'releaseYearRange' in meta:
            league = u'{} - {}'.format(league, meta['releaseYearRange']['startYear'])
        item.info['plot'] = u'[B]{}[/B]\n\n{}'.format(league, item.info['plot'])

    if data['visuals']['badging']['airingEventState']['state'] not in ('replay',):
        item.label = u'[B][{}][/B] {}'.format(data['visuals']['badging']['airingEventState']['badgeLabel'], item.label)

    if 'prompt' in data['visuals'] and not info[ACTIONS][MODAL]:
        item.info['plot'] = u'[B]{}[/B]\n{}'.format(data['visuals']['prompt'], item.info['plot'])

    return item


def _parse_movie(data):
    info = _get_info(data)
    meta = data['visuals'].get('metastringParts', {})

    item = plugin.Item(
        label = info['title'],
        art = info['art'],
        info = {
            'plot': info['plot'],
            'duration': int(meta['runtime']['runtimeMs'] / 1000),
            'trailer': plugin.url_for(play_trailer, deeplink_id=info[ACTIONS][PLAYBACK]['deeplinkId']),
            'mediatype': 'movie',
        },
        playable = True,
        path = info['playpath'],
    )

    if 'releaseYearRange' in meta:
        item.info['year'] = meta['releaseYearRange']['startYear']

    if settings.SYNC_WATCHLIST.value:
        item.context.append((_.ADD_WATCHLIST, 'RunPlugin({})'.format(plugin.url_for(add_watchlist, deeplink_id=info[ACTIONS][PLAYBACK]['deeplinkId']))))
    item.context.append((_.EXTRAS, "Container.Update({})".format(plugin.url_for(extras, deeplink_id=info[ACTIONS][PLAYBACK]['deeplinkId']))))
    item.context.append((_.SUGGESTED, "Container.Update({})".format(plugin.url_for(suggested, deeplink_id=info[ACTIONS][PLAYBACK]['deeplinkId']))))
    return item


def _parse_show(data):
    info = _get_info(data)
    meta = data['visuals'].get('metastringParts', {})

    item = plugin.Item(
        label = info['title'],
        art = info['art'],
        info = {
            'plot': info['plot'],
            'trailer': plugin.url_for(play_trailer, deeplink_id=info[ACTIONS][PLAYBACK]['deeplinkId']),
            'mediatype': 'tvshow',
        },
    )

    # this not available when quering the show entity directly
    if info[ACTIONS][BROWSE]:
        item.path = plugin.url_for(show, show_id=info[ACTIONS][BROWSE]['pageId'])

    if 'releaseYearRange' in meta:
        item.info['year'] = meta['releaseYearRange']['startYear']

    if settings.SYNC_WATCHLIST.value:
        item.context.append((_.ADD_WATCHLIST, 'RunPlugin({})'.format(plugin.url_for(add_watchlist, deeplink_id=info[ACTIONS][PLAYBACK]['deeplinkId']))))
    item.context.append((_.EXTRAS, "Container.Update({})".format(plugin.url_for(extras, deeplink_id=info[ACTIONS][PLAYBACK]['deeplinkId']))))
    item.context.append((_.SUGGESTED, "Container.Update({})".format(plugin.url_for(suggested, deeplink_id=info[ACTIONS][PLAYBACK]['deeplinkId']))))
    return item


def _parse_row(data):
    meta = data['visuals'].get('metastringParts', {})

    if 'airingEventState' in data['visuals'].get('badging', {}):
        item = _parse_event(data)

    elif 'episodeTitle' in data['visuals']:
        item = _parse_episode(data)

    elif 'runtime' in meta:
        item = _parse_movie(data)

    elif meta:
        item = _parse_show(data)

    else:
        item = _parse_page(data)

    if 'genres' in meta:
        item.info['genre'] = meta['genres']['values']

    if 'ratingInfo' in meta:
        item.info['rating'] = meta['ratingInfo']['rating']['text']

    return item


@plugin.route()
def play_trailer(deeplink_id, **kwargs):
    with gui.busy():
        data = api.page('entity-{}'.format(deeplink_id.replace('entity-', '')))
        info = _get_info(data)
        item = _parse_row(data)

        item = plugin.get_trailer_item(item, check=not info[ACTIONS][TRAILER])
        if info[ACTIONS][TRAILER]:
            item.inputstream = inputstream.Widevine(
                license_key = api.get_config()['services']['drm']['client']['endpoints']['widevineLicense']['href'],
                manifest_type = 'hls',
                mimetype = 'application/vnd.apple.mpegurl',
                wv_secure = is_wv_secure(),
            )
            playback_data = api.playback(info[ACTIONS][TRAILER]['resourceId'], item.inputstream.wv_secure)
            item.path = playback_data['stream']['sources'][0]['complete']['url']
            item.headers = api.session.headers

        return item


@plugin.route()
def extras(deeplink_id, **kwargs):
    data = api.page('entity-{}'.format(deeplink_id.replace('entity-', '')), enhanced_limit=15)
    info = _get_info(data)
    return _process_rows(info[CONTAINERS][EXTRAS], title=u"{} ({})".format(info['title'], _.EXTRAS))


@plugin.route()
def suggested(deeplink_id, **kwargs):
    data = api.page('entity-{}'.format(deeplink_id.replace('entity-', '')), enhanced_limit=15)
    info = _get_info(data)
    return _process_rows(info[CONTAINERS][SUGGESTED], title=u"{} ({})".format(info['title'], _.SUGGESTED))


def _add_progress(user_state, item):
    if not user_state or not settings.SYNC_PLAYBACK.value:
        return

    if user_state['progress']['progressPercentage'] == 100:
        item.info['playcount'] = 1

    elif user_state['progress']['progressPercentage'] > 0:
        item.info['playcount'] = 0
        if 'secondsRemaining' in user_state['progress']:
            item.resume_from = int(item.info['duration'] - user_state['progress']['secondsRemaining'])
        else:
            item.resume_from = int(user_state['progress']['progressPercentage']/100.0 * item.info['duration'])


def _get_art(row):
    if not row or 'artwork' not in row['visuals'] or 'standard' not in row['visuals']['artwork']:
        return {}

    is_episode = 'episodeTitle' in row['visuals']
    images = row['visuals']['artwork']['standard']

    if 'tile' in row['visuals']['artwork']:
        images['hero_tile'] = row['visuals']['artwork']['tile']['background']

    if 'network' in row['visuals']['artwork']:
        images['thumbnail'] = row['visuals']['artwork']['network']['tile']

    for key in ('hero', 'brand', 'up_next'):
        try:
            images['background'] = row['visuals']['artwork'][key]['background']
        except KeyError:
            pass

    def _first_image_url(d):
        return 'https://disney.images.edge.bamgrid.com/ripcut-delivery/v2/variant/disney/{}'.format(d['imageId'])

    art = {}
    # don't ask for jpeg thumb; might be transparent png instead
    thumbsize = '/scale?width=800&aspectRatio=1.78'
    bannersize = '/scale?width=1440&aspectRatio=1.78&format=jpeg'
    fullsize = '/scale?width=1440&aspectRatio=1.78&format=jpeg'

    thumb_ratios = ['1.78', '1.33', '1.00']
    poster_ratios = ['0.71', '0.75', '0.80']
    clear_ratios = ['2.00', '1.78', '3.32']
    banner_ratios = ['3.91', '3.00', '1.78']
    watermark_used = False

    if is_episode:
        thumbs = ('thumbnail',)
    else:
        thumbs = ('thumbnail', 'tile', 'watermark')

    fanart_count = 0
    for name in images or []:
        art_type = images[name]

        tr = br = pr = cr = ''

        for ratio in thumb_ratios:
            if ratio in art_type:
                tr = ratio
                break

        for ratio in banner_ratios:
            if ratio in art_type:
                br = ratio
                break

        for ratio in poster_ratios:
            if ratio in art_type:
                pr = ratio
                break

        for ratio in clear_ratios:
            if ratio in art_type:
                cr = ratio
                break

        if name in thumbs:
            if tr:
                art['thumb'] = _first_image_url(art_type[tr]) + thumbsize
            if pr:
                art['poster'] = _first_image_url(art_type[pr]) + thumbsize

            if (tr or pr) and name == 'watermark':
                watermark_used = True

        elif name == 'hero_tile':
            if br:
                art['banner'] = _first_image_url(art_type[br]) + bannersize

        elif name in ('hero_collection', 'background_details', 'background'):
            if tr:
                k = 'fanart{}'.format(fanart_count) if fanart_count else 'fanart'
                art[k] = _first_image_url(art_type[tr]) + fullsize
                fanart_count += 1
            if pr:
                art['keyart'] = _first_image_url(art_type[pr]) + bannersize

        elif name in ('title_treatment', 'logo'):
            if cr:
                art['clearlogo'] = _first_image_url(art_type[cr]) + thumbsize

    if is_episode or watermark_used:
        art.pop('poster', None)

    return art


def _get_milestone(milestones, name, default=0):
    if not milestones:
        return default

    for row in milestones:
        if row['label'] == name:
            return int(row['offsetMillis'] / 1000)

    return default


@plugin.route()
@plugin.login_required()
def play(**kwargs):
    return _play(**kwargs)


def _play(family_id=None, content_id=None, deeplink_id=None, channel_id=None, **kwargs):
    if KODI_VERSION > 18:
        ver_required = '2.6.0'
    else:
        ver_required = '2.4.5'

    ia = inputstream.Widevine(
        manifest_type = 'hls',
        mimetype = 'application/vnd.apple.mpegurl',
        wv_secure = is_wv_secure(),
    )
    if not ia.check() or not inputstream.require_version(ver_required):
        gui.ok(_(_.IA_VER_ERROR, kodi_ver=KODI_VERSION, ver_required=ver_required))

    if channel_id:
        data = api.deeplink(channel_id, ref_type='channelId', action='playback')
    elif content_id:
        data = api.deeplink(content_id, ref_type='dmcContentId', action='playback')
    elif family_id:
        data = api.deeplink(family_id, ref_type='encodedFamilyId', action='playback')
    else:
        data = api.deeplink(deeplink_id.replace('entity-', ''), action='playback')

    deeplink_id = data['actions'][0]['deeplinkId'].replace('entity-', '')
    resource_id = data['actions'][0]['resourceId']
    available_id = data['actions'][0]['availId']
    upnext_id = data['actions'][0].get('upNextId')
    is_linear = data['actions'][0].get('contentType') == 'linear'

    player_experience = api.player_experience(available_id)
    program_type = player_experience['analytics']['programType']

    flags = []
    item = plugin.Item()

    #TODO: dont need to do this if clicking from existing listitem with all info
    # skip this if we already have good info
    if is_linear:
        # TODO channel list item data
        pass
    elif program_type == 'movie':
        data = api.page('entity-{}'.format(deeplink_id))
        flags = [x['value'] for x in data['visuals']['metastringParts']['audioVisual']['flags']]
        item = _parse_row(data)
    elif program_type == 'episode':
        # TODO: this is a few requests and needs ugly season name matching. Ideally an api endpoint for episode details exist
        season_name = player_experience['subtitle'].split(':')[0].lower().strip().lstrip('s')
        show = api.page(data['actions'][1]['pageId'], limit=0, enhanced_limit=0)
        for row in show['containers'][0]['seasons']:
            # TODO: this probably doesnt work for non-english
            if row['visuals']['name'].lower().endswith(season_name):
                data = api.season(row['id'])
                for row in data['items']:
                    if row['actions'][0]['deeplinkId'].replace('entity-', '') == deeplink_id:
                        item = _parse_row(row)
                        break
                break

    if 'imax_enhanced' in flags:
        deault_ratio = settings.DEFAULT_RATIO.value

        if deault_ratio == Ratio.ASK:
            index = gui.context_menu([_.IMAX, _.WIDESCREEN])
            if index == -1:
                return
            imax = True if index == 0 else False
        else:
            imax = True if deault_ratio == Ratio.IMAX else False

        profile = api.profile()[0]
        if imax != profile['attributes']['playbackSettings']['preferImaxEnhancedVersion']:
            api.set_imax(imax)

    playback_data = api.playback(resource_id, ia.wv_secure)

    # LEGACY RESUME (Remove once legacy browsing removed)
    if not kwargs.get(ROUTE_RESUME_TAG):
        if content_id and settings.SYNC_PLAYBACK.value and NO_RESUME_TAG in kwargs and playback_data['playhead']['status'] == 'PlayheadFound':
            item.resume_from = plugin.resume_from(playback_data['playhead']['position'])
            if item.resume_from == -1:
                return

    if is_linear:
        url = playback_data['stream']['sources'][0]['slide']['url']
        ia.license_key = api.get_config()['services']['drm']['client']['endpoints']['widevineLinearLicense']['href']
    else:
        url = playback_data['stream']['sources'][0]['complete']['url']
        ia.license_key = api.get_config()['services']['drm']['client']['endpoints']['widevineLicense']['href']

    item.update(
        playable = True,
        path = url,
        inputstream = ia,
        headers = api.session.headers,
        proxy_data = {'original_language': player_experience.get('originalLanguage') or ''},
    )

    item.play_skips = []
    milestones = playback_data['stream'].get('editorial', [])
    if milestones and settings.getBool('skip_recaps', False):
        recap_start = _get_milestone(milestones, 'recap_start')
        recap_end = _get_milestone(milestones, 'recap_end')
        if recap_end > recap_start:
            item.play_skips.append({'from': recap_start, 'to': recap_end})

    if milestones and settings.getBool('skip_intros', False):
        intro_start = _get_milestone(milestones, 'intro_start')
        intro_end = _get_milestone(milestones, 'intro_end')
        if intro_end > intro_start:
            item.play_skips.append({'from': intro_start, 'to': intro_end})

    if milestones and settings.getBool('skip_credits', False):
        credits_start = _get_milestone(milestones, 'up_next')
        tag_start = _get_milestone(milestones, 'tag_start')
        tag_end = _get_milestone(milestones, 'tag_end')
        item.play_skips.append({'from': credits_start, 'to': tag_start})
        if tag_end:
            item.play_skips.append({'from': tag_end, 'to': 0})

    upnext = None
    if upnext_id and program_type == 'episode' and settings.getBool('play_next_episode', True):
        data = api.upnext(upnext_id)
        for row in data.get('items', []):
            if row.get('type') != 'upNext' or not row.get('sequentialEpisode'):
                continue
            upnext = row['item']

    elif upnext_id and program_type == 'movie' and settings.getBool('play_next_movie', False):
        data = api.upnext(upnext_id)
        for row in data.get('items', []):
            if row.get('type') != 'upNext' or row.get('sequentialEpisode'):
                continue
            upnext = row['item']

    if upnext:
        info = _get_info(upnext)
        item.play_next = {'next_file': info['playpath']}

    if settings.SYNC_PLAYBACK.value:
        telemetry = playback_data['tracking']['telemetry']
        item.callback = {
            'type':'interval',
            'interval': 30,
            'callback': plugin.url_for(callback, media_id=telemetry['mediaId'], fguid=telemetry['fguid']),
        }

    return item


@plugin.route()
def login(**kwargs):
    options = [
        [_.EMAIL_PASSWORD, _email_password],
    ]

    index = 0 if len(options) == 1 else gui.context_menu([x[0] for x in options])
    if index == -1 or not options[index][1]():
        return

    _select_profile()
    gui.refresh()


def _email_password():
    email = gui.input(_.ASK_EMAIL, default=userdata.get('username', '')).strip()
    if not email:
        return

    userdata.set('username', email)

    token = api.register_device()
    next_step = api.check_email(email, token)

    if next_step.lower() == 'register':
        raise PluginError(_.EMAIL_NOT_FOUND)

    elif next_step.lower() == 'otp':
        api.request_otp(email, token)

        while True:
            otp = gui.input(_(_.OTP_INPUT, email=email)).strip()
            if not otp:
                return

            error = api.login_otp(email, otp, token)
            if not error:
                return True

            gui.error(error)
    else:
        password = gui.input(_.ASK_PASSWORD, hide_input=True).strip()
        if not password:
            return

        api.login(email, password, token)
        return True


@plugin.route()
def select_profile(**kwargs):
    if userdata.get('kid_lockdown', False):
        return

    _select_profile()
    gui.refresh()


def _avatars(ids):
    avatars = {}

    data = api.avatar_by_id(ids)
    for row in data['avatars']:
        avatars[row['avatarId']] = row['image']['tile']['1.00']['avatar']['default']['url'] + '/scale?width=300'

    return avatars


def _select_profile():
    account = api.account(_skip_cache=True)['account']
    profiles = account['profiles']
    avatars = _avatars([x['attributes']['avatar']['id'] for x in profiles])

    options = []
    values = []
    default = -1

    for index, profile in enumerate(profiles):
        values.append(profile)
        profile['_avatar'] = avatars.get(profile['attributes']['avatar']['id'])

        if profile['attributes']['parentalControls']['isPinProtected']:
            label = _(_.PROFILE_WITH_PIN, name=profile['name'])
        else:
            label = profile['name']

        options.append(plugin.Item(label=label, art={'thumb': profile['_avatar']}))

        if account['activeProfile'] and profile['id'] == account['activeProfile']['id']:
            default = index
            userdata.set('avatar', profile['_avatar'])
            userdata.set('profile', profile['name'])
            userdata.set('profile_id', profile['id'])

    index = gui.select(_.SELECT_PROFILE, options=options, preselect=default, useDetails=True)
    if index < 0:
        return

    _switch_profile(values[index])


def _switch_profile(profile):
    pin = None
    if profile['attributes']['parentalControls']['isPinProtected']:
        pin = gui.input(_.ENTER_PIN, hide_input=True).strip()

    api.switch_profile(profile['id'], pin=pin)

    if settings.getBool('kid_lockdown', False) and profile['attributes']['kidsModeEnabled']:
        userdata.set('kid_lockdown', True)

    userdata.set('avatar', profile['_avatar'])
    userdata.set('profile', profile['name'])
    userdata.set('profile_id', profile['id'])
    gui.notification(_.PROFILE_ACTIVATED, heading=profile['name'], icon=profile['_avatar'])


@plugin.route()
def logout(**kwargs):
    if not gui.yes_no(_.LOGOUT_YES_NO):
        return

    api.logout()
    userdata.delete('kid_lockdown')
    userdata.delete('avatar')
    userdata.delete('profile')
    userdata.delete('profile_id')
    gui.refresh()
