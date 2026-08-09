# -*- coding: utf-8 -*-

import sys
import xbmc
import xbmcaddon

def translation(id):
	return xbmcaddon.Addon().getLocalizedString(id)

class Client(object):
	CONFIG_ARTE = {
		'edges_one': '{}pages/',
		'edges_two': '{}pages/{}/',
		'programs_one': '{}programs/{}/',
		'zones_one': '{}zones/{}/content?authorizedCountry={}',
		'zones_two': '{}zones/{}/content?authorizedCountry={}&pageId={}',
		'collections_one': '{}collections/{}/',
		'collections_two': '{}zones/{}/content?authorizedCountry={}&collectionId={}&pageId=collection&type=collection',
		'collections_three': '{}zones/{}/content?authorizedCountry={}&collectionId={}&subCollectionId={}&pageId=collection&type=collection',
		'search_query': '{}pages/SEARCH?query={}',
		'player_mp4': 'https://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/streams/{}/SHOW/{}',
		'player_m3u8': 'https://api.arte.tv/api/player/v2/config/{}/{}',
		'samples': [
		{
			'title_de': translation(30601),
			'title_fr': translation(30602),
			'action': 'listBroadcasts',
			'link': '{}pages/HOME/',
			'phase': 'HOME',
			'thumb': 'start.png',
			'description': 'Startpage'
		},
		{
			'title_de': translation(30603),
			'title_fr': translation(30604),
			'action': 'listCategories',
			'link': 'THEMES',
			'phase': 'ARTE_THEMES',
			'thumb': 'themes.png',
			'description': 'Theme-Categories'
		},
		{
			'title_de': translation(30605),
			'title_fr': translation(30606),
			'action': 'listCategories',
			'link': 'MUSICS',
			'phase': 'ARTE_CONCERT',
			'thumb': 'musics.png',
			'description': 'Music-Categories'
		},
		{
			'title_de': translation(30607),
			'title_fr': translation(30608),
			'action': 'listBroadcasts',
			'link': '{}pages/MAGAZINES/',
			'phase': 'MAGAZINES',
			'thumb': 'broadcasts.png',
			'description': 'Broadcast A-Z'
		},
		{
			'title_de': translation(30609),
			'title_fr': translation(30610),
			'action': 'listVideoDates',
			'link': '{}pages/TV_GUIDE/?day=',
			'phase': 'TV_GUIDE',
			'thumb': 'programs.png',
			'description': 'Program sorted by date'
		},
		{
			'title_de': translation(30611),
			'title_fr': translation(30612),
			'action': 'listBroadcasts',
			'link': '{}pages/MOST_VIEWED/',
			'phase': 'MOST_VIEWED',
			'thumb': 'mostviewed.png',
			'description': 'Most viewed'
		},
		{
			'title_de': translation(30613),
			'title_fr': translation(30614),
			'action': 'listBroadcasts',
			'link': '{}pages/MOST_RECENT/',
			'phase': 'MOST_RECENT',
			'thumb': 'newest.png',
			'description': 'New Videos'
		},
		{
			'title_de': translation(30615),
			'title_fr': translation(30616),
			'action': 'listBroadcasts',
			'link': '{}pages/LAST_CHANCE/',
			'phase': 'LAST_CHANCE',
			'thumb': 'chance.png',
			'description': 'Last Chance'
		},
		{
			'title_de': translation(30617),
			'title_fr': translation(30618),
			'action': 'SearchARTE',
			'phase': 'SEARCH',
			'thumb': 'basesearch.png',
			'description': 'Search ...'
		},
		{
			'title_de': translation(30619),
			'title_fr': translation(30620),
			'action': 'streamTV',
			'phase': 'LIVE_CHANNELS',
			'thumb': 'livestream.png',
			'description': 'Live & Event TV'
		},
		{
			'title_de': translation(30621),
			'title_fr': translation(30622),
			'action': 'antuning',
			'phase': 'ADDON_SETTINGS',
			'thumb': 'settings.png',
			'description': 'ARTE Settings'
		},
		{
			'title_de': translation(30623),
			'title_fr': translation(30624),
			'action': 'ietuning',
			'phase': 'INPUTSTREAM_SETTINGS',
			'thumb': 'settings.png',
			'description': 'Inputstream Settings'
		}],
		'weekdays': [
		{
			'title_de': translation(30671),
			'title_fr': translation(30672),
			'route': '1',
			'description': 'Monday'
		},
		{
			'title_de': translation(30673),
			'title_fr': translation(30674),
			'route': '2',
			'description': 'Tuesday'
		},
		{
			'title_de': translation(30675),
			'title_fr': translation(30676),
			'route': '3',
			'description': 'Wednesday'
		},
		{
			'title_de': translation(30677),
			'title_fr': translation(30678),
			'route': '4',
			'description': 'Thursday'
		},
		{
			'title_de': translation(30679),
			'title_fr': translation(30680),
			'route': '5',
			'description': 'Friday'
		},
		{
			'title_de': translation(30681),
			'title_fr': translation(30682),
			'route': '6',
			'description': 'Saturday'
		},
		{
			'title_de': translation(30683),
			'title_fr': translation(30684),
			'route': '0',
			'description': 'Sunday'
		}],
		'streams': [
		{
			'title_de': translation(32201),
			'title_fr': translation(32202),
			'link': 'https://artesimulcast.akamaized.net/hls/live/2030993/artelive_de/master.m3u8',
			'thumb': 'AIR.png',
			'description': 'ARTE ► Germany live'
		},
		{
			'title_de': translation(32203),
			'title_fr': translation(32204),
			'link': 'https://artesimulcast.akamaized.net/hls/live/2031003/artelive_fr/master.m3u8',
			'thumb': 'AIR.png',
			'description': 'ARTE ► France live'
		},
		{
			'title_de': translation(32205),
			'title_fr': translation(32206),
			'link': 'https://arteconcerthls.akamaized.net/hls/live/2025494/channel01/master.m3u8',
			'thumb': 'ONE.png',
			'description': 'ARTE Event 1'
		},
		{
			'title_de': translation(32207),
			'title_fr': translation(32208),
			'link': 'https://arteconcerthls.akamaized.net/hls/live/2025495/channel02/master.m3u8',
			'thumb': 'TWO.png',
			'description': 'ARTE Event 2'
		},
		{
			'title_de': translation(32209),
			'title_fr': translation(32210),
			'link': 'https://arteconcerthls.akamaized.net/hls/live/2025496/channel03/master.m3u8',
			'thumb': 'THREE.png',
			'description': 'ARTE Event 3'
		},
		{
			'title_de': translation(32211),
			'title_fr': translation(32212),
			'link': 'https://arteconcerthls.akamaized.net/hls/live/2025497/channel04/master.m3u8',
			'thumb': 'FOUR.png',
			'description': 'ARTE Event 4'
		},
		{
			'title_de': translation(32213),
			'title_fr': translation(32214),
			'link': 'https://arteconcerthls.akamaized.net/hls/live/2025498/channel05/master.m3u8',
			'thumb': 'FIVE.png',
			'description': 'ARTE Event 5'
		},
		{
			'title_de': translation(32215),
			'title_fr': translation(32216),
			'link': 'https://arteconcerthls.akamaized.net/hls/live/2025499/channel06/master.m3u8',
			'thumb': 'SIX.png',
			'description': 'ARTE Event 6'
		}],
	}

	def __init__(self, config):
		self._config = config

	def get_config(self):
		return self._config
