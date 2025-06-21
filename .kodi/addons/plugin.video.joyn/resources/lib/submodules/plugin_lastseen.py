# -*- coding: utf-8 -*-

from copy import deepcopy
from .. import compat
from ..xbmc_helper import xbmc_helper


def get_lastseen():

	lastseen = xbmc_helper().get_json_data('lastseen')

	if lastseen is not None and len(lastseen) > 0:
		return sorted(lastseen, key=lambda k: k['lastseen'], reverse=True)

	return []


def add_lastseen(max_lastseen, season_id=None, movie_id=None, path=None):

	from time import time

	if max_lastseen > 0:
		found_in_lastseen = False
		lastseen = get_lastseen()

		if lastseen is None:
			lastseen = []

		for idx, lastseen_item in enumerate(lastseen):
			if season_id is not None and 'season_id' in lastseen_item.keys(
			) and lastseen_item['season_id'] == season_id or movie_id is not None and 'movie_id' in lastseen_item.keys(
			) and lastseen_item['movie_id'] == movie_id:

				lastseen[idx]['lastseen'] = time()
				found_in_lastseen = True
				break

		if found_in_lastseen is False:
			if season_id is not None:
				lastseen.append({'season_id': season_id, 'path': path, 'lastseen': time()})
			elif movie_id is not None:
				lastseen.append({'movie_id': movie_id, 'path': path, 'lastseen': time()})

		lastseen = sorted(lastseen, key=lambda k: k['lastseen'], reverse=True)

		if len(lastseen) > max_lastseen:
			lastseen = lastseen[:(max_lastseen - 1)]

		xbmc_helper().set_json_data('lastseen', lastseen)


def show_lastseen(max_lastseen_count, default_fanart):

	from ..lib_joyn import lib_joyn
	from .plugin_favorites import check_favorites
	from ..plugin import get_list_items, get_dir_entry

	list_items = []
	season_ids = []
	movie_ids = []

	if lib_joyn().get_auth_token().get('has_account', False) is not False:
		landingpage = deepcopy(lib_joyn().get_landingpage())

		for block in landingpage.get('page').get('blocks'):
			if block.get('__typename') == 'ResumeLane':
				resume_data = lib_joyn().get_graphql_response('RESUMELANE', {'blockId': block['id']})
				if resume_data is not None and isinstance(resume_data.get('block', {}).get('assets', None), list):
					for asset in resume_data.get('block').get('assets'):
						if len(list_items) < max_lastseen_count:
							if asset['__typename'] == 'Movie':
								list_items.extend(get_list_items([asset], prefix_label='CONTINUE_WATCHING', override_fanart=default_fanart))
							if asset['__typename'] == 'Episode' and isinstance(
							        asset.get('series', None),
							        dict) and asset.get('season', {}).get('id', None) is not None and asset.get('season').get('id') not in season_ids:
								if xbmc_helper().get_bool_setting('dont_show_watchlist_in_lastseen') is True and check_favorites(
								        {'seasonId': asset.get('season').get('id')}) is True:
									continue
								list_items.extend(
								        get_list_items([asset],
								                       prefix_label='CONTINUE_WATCHING',
								                       subtype_merges=['EPSIODE_AS_SERIES_SEASON'],
								                       override_fanart=default_fanart))
								season_ids.append(asset['season']['id'])
						else:
							break

	lastseen = get_lastseen()
	if len(lastseen) > 0:
		for lastseen_item in lastseen:
			if len(list_items) < max_lastseen_count:
				if lastseen_item.get('season_id', None) is not None and lastseen_item.get('season_id') not in season_ids:
					if xbmc_helper().get_bool_setting('dont_show_watchlist_in_lastseen') is True and check_favorites(
					        {'seasonId': lastseen_item['season_id']}) is True:
						continue

					tvshow_data = lib_joyn().get_graphql_response('SEASONS', {
					        'path': lastseen_item['path'],
					        'licenseFilter': lib_joyn().get_license_filter()
					})

					if tvshow_data.get('page') is not None and tvshow_data.get('page').get('series') is not None:
						for season in tvshow_data.get('page').get('series').get('allSeasons'):
							if lastseen_item['season_id'] == season['id'] and season['numberOfEpisodes'] > 0:
								season_metadata = lib_joyn().get_metadata(tvshow_data.get('page').get('series'), 'TVSHOW')
								season_metadata['infoLabels'].update({
								        'title':
								        compat._format(xbmc_helper().translation('CONTINUE_WATCHING'), compat._format('{} - {}', season_metadata['infoLabels'].get('title', ''),
								                       compat._format(xbmc_helper().translation('SEASON_NO'), str(season['number']))))
								})

								list_items.append(
								        get_dir_entry(
								                mode='season_episodes',
								                season_id=lastseen_item['season_id'],
								                metadata=season_metadata,
								                override_fanart=default_fanart,
								        ))

				elif lastseen_item.get('movie_id', None) is not None:
					if xbmc_helper().get_bool_setting('dont_show_watchlist_in_lastseen') is True and check_favorites(
					        {'movie_id': lastseen_item['movie_id']}) is True:
						continue

					movie_data = lib_joyn().get_graphql_response('MOVIES', {
					        'path': lastseen_item['path'],
					})
					if lastseen_item['movie_id'] not in movie_ids and movie_data.get('page') is not None and movie_data.get('page').get('movie') is not None:
						movie_metadata = lib_joyn().get_metadata(movie_data.get('page').get('movie'), 'EPISODE', 'MOVIE')

						movie_metadata['infoLabels'].update({
						        'title':
						        compat._format(xbmc_helper().translation('CONTINUE_WATCHING'), movie_metadata['infoLabels'].get('title', ''))
						})
						movie_metadata['infoLabels'].update({'mediatype': 'movie'})

						list_items.append(
								get_dir_entry(is_folder=False,
											  mode='play_movie',
											  metadata=movie_metadata,
											  override_fanart=default_fanart,
											  path=movie_data.get('page').get('path')))

						movie_ids.append(lastseen_item['movie_id'])

			else:
				break

	return list_items
