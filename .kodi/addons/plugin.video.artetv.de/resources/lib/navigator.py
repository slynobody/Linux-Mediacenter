# -*- coding: utf-8 -*-

from .common import *
config = traversing.get_config()


def mainMenu():
	for item in config['samples']:
		TITLE = item['title_de'] if GERM else item['title_fr']
		TARGET = item.get('link').format(API_EMAC) if item.get('link') is not None and item['action'] != 'listCategories' else item.get('link', '00')
		FETCH_UNO = create_entries({'Title': TITLE, 'Image': f"{artpic}{item.get('thumb')}"})
		if item['action'] not in ['antuning', 'ietuning']:
			addDir({'mode': item['action'], 'link': TARGET, 'phase': item['phase'], 'name': TITLE}, FETCH_UNO)
		if enable_tune:
			if item['action'] == 'antuning':
				addDir({'mode': item['action']}, FETCH_UNO, False)
			if item['action'] == 'ietuning' and enable_adaptive and plugin_operate('inputstream.adaptive'):
				addDir({'mode': item['action']}, FETCH_UNO, False)
	if not plugin_operate('inputstream.adaptive'):
		addon.setSetting('use_adaptive', 'false')
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listCategories(EXTRA):
	debug_MS(f"(navigator.list{EXTRA.title()}) ------------------------------------------------ START = list{EXTRA.title()} -----------------------------------------------")
	SUPPORTED = ['BAR', 'ADS', 'MUE', 'HIP', 'JAZ', 'CLA', 'MET', 'OPE', 'MUA', 'MUD'] if EXTRA == 'MUSICS' else ['ACT', 'DOR', 'DEC', 'SER', 'HIS', 'CIN', 'CPO', 'EMI', 'SCI']
	DATA_UNO = getContent(config['edges_one'].format(API_EMAC))
	if EXTRA == 'MUSICS':
		FETCH_UNO = create_entries({'Title': translation(30641) if GERM else translation(30642), 'Image': f"{thepic}ARS.png"})
		addDir({'mode': 'listBroadcasts', 'link': config['edges_two'].format(API_EMAC, 'ARTE_CONCERT'), 'phase': 'ARS', 'name': 'ARTE CONCERT'}, FETCH_UNO)
	for item in SUPPORTED:
		for theme in DATA_UNO:
			if theme.get('deeplink', '') and theme['deeplink'].endswith(f"emac/{item}"):
				CODE, TEASER = item, get_Description(theme)
				if EXTRA == 'MUSICS':
					NAME = theme['label'].replace('Barock', translation(30643)).replace('Baroque', translation(30644)).replace('Performance', translation(30645)).replace('Electro', translation(30646) if GERM else translation(30647)).replace('Klassische Musik', translation(30648))
					TITLE = translation(30649).format(NAME)
				else:
					NAME = theme['label'] if item != 'EMI' else translation(30650) if GERM else translation(30651)
					TITLE = f"[B]{NAME}[/B]"
				debug_MS(f"(navigator.list{EXTRA.title()}[1]) ### NAME : {NAME} || CATEGORY : {CODE} || URL : {config['edges_two'].format(API_EMAC, CODE)} ###")
				FETCH_DUE = create_entries({'Title': TITLE, 'Tagline': TEASER, 'Image': f"{thepic}{CODE}.png"})
				addDir({'mode': 'listBroadcasts', 'link': config['edges_two'].format(API_EMAC, CODE), 'phase': CODE, 'name': NAME}, FETCH_DUE)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listThoroughs(EXTRA):
	debug_MS(f"(navigator.list{EXTRA.title()}) ------------------------------------------------ START = list{EXTRA.title()} -----------------------------------------------")
	if EXTRA == 'HISTORY':
		SUPPORTED = [{'name': 'Stimmt es, dass...?', 'zone': 'de609ad5-a957-4109-b7a9-869826256ed1', 'coll': 'RC-026488'},{'name': 'Das 20. Jahrhundert', 'zone': '2b58ae11-edfa-49f3-bab8-134920410e06'},
			{'name': 'Die Zeit vor dem 20. Jahrhundert', 'zone': 'f30c86a4-ed63-41c0-a48d-3cbba123c054'},{'name': 'Die großen Dokureihen', 'zone': '8fbf35e4-324d-4d3e-a194-28f7d288789b', 'coll': 'RC-020554'},
			{'name': 'Biographien', 'zone': '7d91ee35-62fb-4c4f-aec3-057e02196ea3'},{'name': 'Geschichte schreiben', 'zone': 'f9136297-c639-48c7-865c-3f5db07de468', 'coll': 'RC-020782'}] if GERM else \
				[{'name': 'Est-il vrai que...?', 'zone': 'd3bad9c8-b1c0-43db-87fb-fb95cc68766d', 'coll': 'RC-026488'},{'name': 'Civilisations', 'zone': '0fdfa046-a060-4ab3-9498-871a1d15c7e3'},
				{'name': 'XXe siècle', 'zone': '4ed8b40a-ba13-4da4-8574-2a1b73a5878b'},{'name': "Les séries documentaires d'histoire", 'zone': 'e0dfcff6-67bc-4d83-8055-8edf45687aea', 'coll': 'RC-020554'},
				{'name': 'Les grands personnages', 'zone': '8c788ec9-8b2c-455d-b856-7f105ca0dc4e'},{'name': "Faire l'histoire", 'zone': '5c5ab0fc-a32c-493c-bfa1-7d4eddca8834', 'coll': 'RC-020782'}]
		for item in SUPPORTED:
			LINK = config['collections_one'].format(API_EMAC, item['coll']) if item.get('coll', None) else config['zones_one'].format(API_EMAC, item['zone'], WEB_LANG)
			debug_MS(f"(navigator.list{EXTRA.title()}[1]) ### NAME : {item['name']} || CATEGORY : Geschichte/Histoire=HIS || URL : {LINK} ###")
			addDir({'mode': 'listBroadcasts', 'link': LINK, 'phase': 'HIS', 'name': item['name']}, create_entries({'Title': item['name']}))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listVideoDates(START, EXTRA):
	debug_MS("(navigator.listVideoDates) ------------------------------------------------ START = listVideoDates -----------------------------------------------")
	debug_MS(f"(navigator.listVideoDates) ### URL = {START} || EXTRA = {EXTRA} ###")
	if EXTRA == 'DISPLAY': # URL-Day = https://www.arte.tv/api/rproxy/emac/v4/de/web/pages/TV_GUIDE/?day=2026-02-11
		FOUND, DATA_UNO = 0, getContent(START)
		for movie in DATA_UNO['zones'][-1]['content']['data']:
			if 'FULL_VIDEO' in str(movie.get('stickers')) and str(movie.get('duration')).isdecimal() and int(movie['duration']) > 0 and movie.get('programId', None):
				FOUND += 1
				part_uno = create_substances(movie, movie['title'], 'DATA_ONE', 'TV_GUIDE', '(listVideoDates=VIDEOS[1])')
				if part_uno[0] is None: continue
				addDir(part_uno[0], create_entries(part_uno[1]), part_uno[2])
		if FOUND == 0:
			failing(f'(navigator.listVideoDates) ##### NO VIDEO-DATE-LIST - NO ENTRY FOR: "{START.split("?day=")[1]}" FOUND #####')
			return dialog.notification(translation(30524), translation(30526).format(START.split('?day=')[1]), icon, 10000)
	else:
		for ii in range(-20, 21, 1):
			ENDS = (datetime.now() - timedelta(days=ii)).strftime('%Y-%m-%d') # Date for URL // 2025-06-11
			DATE = (datetime.now() - timedelta(days=ii)).strftime('%w~%d.%m.') # Date with weekday numbering // 3~11.06.
			DAYS = [xrs for xrs in config['weekdays'] if xrs.get('route') == DATE.split('~')[0]]
			TITLE = translation(30685).format(DAYS[0]['title_de'] if GERM else DAYS[0]['title_fr'], DATE.split('~')[1]) if ii == 0 else \
				f"{DAYS[0]['title_de'] if GERM else DAYS[0]['title_fr']}, {DATE.split('~')[1]}"
			addDir({'mode': 'listVideoDates', 'link': f"{START}{ENDS}", 'extras': 'DISPLAY'}, create_entries({'Title': TITLE, 'Image': f"{artpic}days.png"}))
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def listBroadcasts(TARGET, PHRASE, NAME, PAGE):
	debug_MS("(navigator.listBroadcasts) ------------------------------------------------ START = listBroadcasts -----------------------------------------------")
	NAME = re.sub(r'\[/?B\]', '', NAME)
	debug_MS(f"(navigator.listBroadcasts) ### URL = {TARGET} || PHRASE = {PHRASE} || NAME = {NAME} || PAGE = {PAGE} ###")
	(BEAM_ONE, TOTAL_BEAM, NEXT_ONE, TOTAL_ONE, NEXT_TWO, TOTAL_TWO), UNIKAT = (None for _ in range(6)), set()
	(COURSE, counterONE, counterTOP, counterEXC), (COMBI_FIRST, COMBI_SECOND, COMBI_LINKS) = (0 for _ in range(4)), ([] for _ in range(3))
	FORWARD, PROCEED, LIMIT, PAGE_NUMBER, MAXIMUM = False, False, 20, int(PAGE), int(PAGE)+1
	includedCODE = ('collection_videos', 'videos_subcategory', 'collection_subcollection', 'listing_') # Wanted Collections
	excludedCODE = ('collection_content', 'collection_upcoming', 'collection_article', 'collection_associated', 'collection_partner') # Unwanted Collections
	excludedNAME = ('auch interessant', 'à voir aussi', 'demnächst', 'à venir') # Unwanted Titles = à voir aussi: auch interessant // à venir: demnächst
	if GERM is True: # e3df396a-3d21-4e6e-908b-17f57e99146d...Nach Themen in 1.Dokus(46d) // 76fdf18b-f820-4270-90f2-fa13243e6e21...Hintergründe in 2.Dokus(e21)
		excludedIDS = ['e3df396a-3d21-4e6e-908b-17f57e99146d', '76fdf18b-f820-4270-90f2-fa13243e6e21']
	else: # fb7c69e9-9b71-468d-b4e3-d2c9309cfb74...Nach Themen in 1.Dokus(b74)
		excludedIDS = ['fb7c69e9-9b71-468d-b4e3-d2c9309cfb74']
	SWITCH = True if any(xs in PHRASE for xs in ['ARS', 'CONCERT', 'BAR', 'ADS', 'MUE', 'HIP', 'JAZ', 'CLA', 'MET', 'OPE', 'MUA', 'MUD']) else False
	COLLECT = True if 'collections/' in TARGET or 'subCollectionId' in TARGET else False # Series name for mixed content = Do not display for folders/videos
	while PAGE_NUMBER > 0:
		COURSE += 1
		DATA_UNO = getContent(TARGET) if PAGE_NUMBER == 1 or COURSE == 1 else getContent(NEXTLINK) if NEXTLINK else DATA_UNO
		debug_MS("++++++++++++++++++++++++++")
		debug_MS(f"(navigator.listBroadcasts[1]) XXXXX CONTENT-01 : {DATA_UNO} XXXXX")
		debug_MS("++++++++++++++++++++++++++")
		DATA_DUE = DATA_UNO['zones'] if DATA_UNO.get('zones', '') and len(DATA_UNO['zones']) > 0 else \
			DATA_UNO['data'] if DATA_UNO.get('data', '') and len(DATA_UNO['data']) > 0 else []
		CODENAMES = [cn for cn in DATA_DUE if str(cn.get('code')).lower().startswith(includedCODE) and cn.get('content', '') and cn['content'].get('data', '')]
		for each in DATA_DUE:
			if each.get('content', '') and each['content'].get('data', '') and len(each['content']['data']) > 0:
				counterONE += 1
				newPHR = DATA_UNO['code'] if DATA_UNO.get('code', '') and PHRASE == 'HOME' else PHRASE # TransmissionCode for Most Viewed and Last Chance
				if ((counterONE in [1, 2] and 'pages/HOME' in TARGET) or (counterONE == 1 and not 'pages/HOME' in TARGET)) and each.get('displayOptions', '') and \
					each['displayOptions'].get('showZoneTitle', True) is False and each['displayOptions'].get('showItemTitle', False) is True:
					counterTOP += 1
					for video in each['content']['data']: # If videos are available in the first category = show it directly
						series = video.get('subtitle', None) if SWITCH or 'ARTE_CONCERT' in str(video.get('stickers')) or not COLLECT else video['title']
						part_uno = create_substances(video, series, 'DATA_TWO', newPHR, '(listBroadcasts=VIDEOS[1])')
						COMBI_FIRST.append([int(counterTOP), series, part_uno[0], part_uno[1], part_uno[2], newPHR])
				else:
					if each.get('displayOptions', '') and str(each['displayOptions'].get('template')).startswith('event'): continue # Hide trailer preview
					if (len(each['content']['data']) == 1 and str(each['content']['data'][0].get('programId')) in ['', 'None']) or (str(each.get('title')).lower().startswith(excludedNAME)) or \
						(str(each.get('id')).split('_')[0] in excludedIDS) or (str(each.get('code')).lower().startswith(excludedCODE)): continue # 1. z.b. Newsletter // 2. excludedNAME // 3. excludedIDS // 4. excludedCODE
					if len(each['content']['data']) == 1 and str(each['content']['data'][0].get('programId'))[:3] == 'RC-': # z.b. Happy Hour under All Films
						short, series, counterTOP = each['content']['data'][0], each['content']['data'][0]['title'], counterTOP.__add__(1)
						part_due = create_substances(short, series, 'DATA_TWO', newPHR, '(listBroadcasts=VIDEOS[2])')
						COMBI_FIRST.append([int(counterTOP), series, part_due[0], part_due[1], part_due[2], newPHR])
					elif each.get('code', '') and str(each.get('code')).lower().startswith(includedCODE):
						if len(CODENAMES) > 1:
							counterTOP, counterEXC = counterTOP.__add__(1), counterEXC.__add__(1) # This is a folder, so exclude it from the sort function
							part_tre = create_substances(each, NAME, 'ZONE_TWO', newPHR, '(listBroadcasts=FOLDER[1])')
							COMBI_FIRST.append([int(counterTOP), NAME, part_tre[0], part_tre[1], part_tre[2], newPHR])
						else:
							FORWARD = True
							BEAM_ONE = each['content']['pagination']['links']['next'] if each.get('content', '') and each['content'].get('pagination', '') and \
								each['content']['pagination'].get('links', '') and 'api/emac' in str(each['content']['pagination']['links'].get('next')) else None
							TOTAL_BEAM = each['content']['pagination']['totalCount'] if each.get('content', '') and each['content'].get('pagination', '') and \
								str(each['content']['pagination'].get('totalCount')).isdecimal() else None
							for mixed in each['content']['data']:
								if mixed.get('kind', '') and mixed['kind'].get('isCollection', False) is True:
									series, term, mark, counterTOP, counterEXC = NAME, 'ZONE_TWO', '(listBroadcasts=FOLDER[2])', counterTOP.__add__(1), counterEXC.__add__(1) # This is a folder, so exclude it from the sort function
								else:
									series = mixed.get('subtitle', None) if SWITCH or 'ARTE_CONCERT' in str(mixed.get('stickers')) or not COLLECT else mixed['title']
									term, mark, counterTOP = 'DATA_TWO', '(listBroadcasts=VIDEOS[3])', counterTOP.__add__(1)
								part_quat = create_substances(mixed, series, term, newPHR, mark)
								COMBI_FIRST.append([int(counterTOP), series, part_quat[0], part_quat[1], part_quat[2], newPHR])
					else:
						series, counterTOP, counterEXC = NAME, counterTOP.__add__(1), counterEXC.__add__(1) # This is a folder, so exclude it from the sort function
						part_cinq = create_substances(each, series, 'ZONE_TWO', newPHR, '(listBroadcasts=FOLDER[3])')
						COMBI_FIRST.append([int(counterTOP), series, part_cinq[0], part_cinq[1], part_cinq[2], newPHR])
			elif DATA_UNO.get('data', '') and len(DATA_UNO['data']) > 0:
				counterTOP, counterEXC = counterTOP.__add__(1), counterEXC.__add__(1) if 'COLLECTION' in str(each.get('stickers')) else counterEXC # This is a folder, so exclude it from the sort function
				series = each.get('subtitle', None) if SWITCH or 'ARTE_CONCERT' in str(each.get('stickers')) else each['title']
				part_sei = create_substances(each, series, 'DATA_TWO', PHRASE, '(listBroadcasts=VARIABLE[1])')
				COMBI_FIRST.append([int(counterTOP), series, part_sei[0], part_sei[1], part_sei[2], PHRASE])
		if COURSE == 1 and int(counterTOP) < 19: # Less than 19 entries
			LIMIT, MAXIMUM, DISPLAY = int(counterTOP), int(MAXIMUM)+2, int(MAXIMUM+2) // 4 + 1
		elif COURSE == 1 and 19 <= int(counterTOP) <= 42 : # Entries between 19 and 42
			LIMIT, MAXIMUM, DISPLAY = int(LIMIT), int(MAXIMUM), int(MAXIMUM) // 2 + 1
		elif COURSE == 1 and int(counterTOP) > 42: # More than 42 entries
			LIMIT, MAXIMUM, DISPLAY = int(counterTOP), int(MAXIMUM)-1, int(MAXIMUM)
		NEXT_ONE, TOTAL_ONE = BEAM_ONE if FORWARD is True else None, TOTAL_BEAM if FORWARD is True else None
		FORWARD = False
		NEXT_TWO = DATA_UNO['pagination']['links']['next'] if DATA_UNO.get('pagination', '') and \
			DATA_UNO['pagination'].get('links', '') and 'api/emac' in str(DATA_UNO['pagination']['links'].get('next')) else None
		TOTAL_TWO = DATA_UNO['pagination']['totalCount'] if DATA_UNO.get('pagination', '') and \
			str(DATA_UNO['pagination'].get('totalCount')).isdecimal() else None
		NEXTLINK = API_EMAC+NEXT_ONE.split('web/')[1] if NEXT_ONE else API_EMAC+NEXT_TWO.split('web/')[1] if NEXT_TWO else None
		NUMBERS = TOTAL_ONE if TOTAL_ONE and NEXT_ONE else TOTAL_TWO if TOTAL_TWO and NEXT_TWO else None
		debug_MS(f"(listBroadcasts=PAGES[1]) ### CHANGE : {SWITCH} || counterTOP : {counterTOP} || TOTAL-COUNT : {NUMBERS} || PAGE*LIMIT : {int(PAGE_NUMBER)*int(LIMIT)} || MAX-PAGES : {MAXIMUM} ###")
		if NEXTLINK and NUMBERS and int(NUMBERS) > int(PAGE_NUMBER)*int(LIMIT) and int(PAGE_NUMBER+1) <= int(MAXIMUM):
			debug_MS(f"(listBroadcasts=PAGES[2]) ### NOW GET NEXTPAGE FROM MAXIMUM : {NEXTLINK} ###")
			PAGE_NUMBER += 1
		else: # NEXTLINK = /api/emac/v4/de/web/zones/af9b8927-0c87-4bc7-8772-e9f889f417d9/content?authorizedCountry=DE&page=2&pageId=FIC&zoneIndexInPage=0
			if NEXTLINK and NUMBERS and int(NUMBERS) > int(PAGE_NUMBER)*int(LIMIT) and int(PAGE_NUMBER) == int(MAXIMUM):
				PROCEED = True
			break
	if COMBI_FIRST: # Counter ZERO is always the numbering of the list
		for xev in sorted(COMBI_FIRST, key=lambda pn: int(pn[0])): # xev[0]=NUMBER, xev[1]=TITLE, xev[2]=ARGIOS, xev[3]=FETCH_UNO, xev[4]=FOLDER, xev[5]=PHRASE
			if xev[2] is not None and frozenset(xev[2].items()) not in UNIKAT:
				UNIKAT.add(frozenset(xev[2].items())) # Filtering double Entries out in Dictionary and hold sortorder
				addDir(xev[2], create_entries(xev[3]), xev[4], True if int(PAGE) > 2 else False, xev[5])
	if counterTOP >= 1:
		if PROCEED is True:
			FETCH_DUE = {'Title': translation(30701).format(DISPLAY) if GERM else translation(30702).format(DISPLAY), 'Image': f"{artpic}nextpage.png"}
			addDir({'mode': 'listBroadcasts', 'link': NEXTLINK, 'phase': PHRASE, 'name': NAME, 'page': int(PAGE_NUMBER)+1}, create_entries(FETCH_DUE))
			debug_MS(f"(listBroadcasts=PAGES[3]) === NOW SHOW NEXTPAGE ENTRY ... No.{int(PAGE_NUMBER)+1} || URL : {NEXTLINK} ... ===")
		if counterEXC == 0:
			for method in getSorting(): xbmcplugin.addSortMethod(ADDON_HANDLE, method)
	elif counterTOP == 0:
		message = translation(30526).format(NAME) if NAME != 'Unknown' else translation(30525)
		failing(f'(navigator.listBroadcasts) ##### NO BROADCAST-LIST - NO ENTRY FOR: "{NAME}" FOUND #####')
		return dialog.notification(translation(30524), message, icon, 10000)
	xbmcplugin.endOfDirectory(ADDON_HANDLE) 

def SearchARTE():
	debug_MS("(navigator.SearchARTE) ------------------------------------------------ START = SearchARTE -----------------------------------------------")
	keyword = preserve(SEARCH_FILE) if xbmcvfs.exists(SEARCH_FILE) else None
	if xbmc.getInfoLabel('Container.FolderPath') == HOST_AND_PATH: # !!! this hack is necessary to prevent KODI from opening the input mask all the time !!!
		keyword = dialog.input(translation(30711) if GERM else translation(30712), type=xbmcgui.INPUT_ALPHANUM, autoclose=15000)
		if keyword: preserve(SEARCH_FILE, keyword)
	if keyword: return listBroadcasts(config['search_query'].format(API_EMAC, quote(keyword)), 'SEARCH', keyword, 1)
	return None

def callingInfos(TARGET, PHRASE):
	debug_MS("(navigator.callingInfos) ------------------------------------------------ START = callingInfos -----------------------------------------------")
	CHANGE = True if any(cs in PHRASE for cs in ['ARS', 'CONCERT', 'BAR', 'ADS', 'MUE', 'HIP', 'JAZ', 'CLA', 'MET', 'OPE', 'MUA', 'MUD']) else False
	debug_MS(f"(navigator.callingInfos[1]) ### CHANGE = {CHANGE} || TARGET = {TARGET} || PHRASE = {PHRASE}")
	DETAILS = getContent(config['programs_one'].format(API_EMAC, TARGET))
	if DETAILS.get('zones', '') and len(DETAILS['zones']) > 0:
		for articles in DETAILS.get('zones', []):
			if str(articles.get('code')).lower().startswith('program_content') and articles.get('content', '') and articles['content'].get('data', '') and len(articles['content']['data']) > 0:
				for selection in articles['content'].get('data', []):
					entries = create_substances(selection, selection['title'], 'DATA_THREE', 'INFORMATION', '(callingInfos=VIDEOS[1])')
					title = entries[1].get('TvShowTitle') if CHANGE and entries[1].get('TvShowTitle') is not None and entries[1].get('Title') is not None else entries[1].get('Title')
					series = entries[1].get('Title') if CHANGE and entries[1].get('TvShowTitle') is not None else None if CHANGE and entries[1].get('TvShowTitle') is None else entries[1].get('TvShowTitle')
					plot = translation(30721).format(title) # Title
					if series is not None: plot += translation(30722).format(series) if GERM else translation(30723).format(series) # TV-Show
					if entries[1].get('Year') is not None:
						plot += translation(30724).format(entries[1].get('Year')) if GERM else translation(30725).format(entries[1].get('Year')) # Production-Year
					if entries[1].get('Duration') is not None and str(entries[1].get('Duration')).isdecimal():
						plot += translation(30726).format(int(entries[1].get('Duration')) // 60) if GERM else translation(30727).format(int(entries[1].get('Duration')) // 60) # Duration in minutes
					if entries[1].get('Genre') is not None and len(entries[1].get('Genre')) > 0: plot += translation(30728).format(entries[1].get('Genre'))
					if entries[1].get('Country') is not None and len(entries[1].get('Country')) > 0:
						plot += translation(30729).format(entries[1].get('Country')) if GERM else translation(30730).format(entries[1].get('Country')) # Countries
					if entries[1].get('Cast') is not None and len(entries[1].get('Cast')) > 0:
						plot += translation(30731).format(entries[1].get('Cast')) if GERM else translation(30732).format(entries[1].get('Cast')) # Cast-Names small
					if entries[1].get('Director') is not None and len(entries[1].get('Director')) > 0:
						plot += translation(30733).format(entries[1].get('Director')) if GERM else translation(30734).format(entries[1].get('Director')) # Director-Names
					if entries[1].get('Writer') is not None and len(entries[1].get('Writer')) > 0:
						plot += translation(30735).format(entries[1].get('Writer')) if GERM else translation(30736).format(entries[1].get('Writer')) # Writer-Names
					if entries[1].get('Mpaa') is not None:
						plot += translation(30737).format(entries[1].get('Mpaa')) if GERM else translation(30738).format(entries[1].get('Mpaa')) # Mpaa
					if len(entries[1].get('Desc_Small')) > 0: plot += f"[CR]{entries[1].get('Desc_Small')}" # Description
					if len(plot) < 40: plot = translation(30739) if GERM else translation(30740) # Nothing found
					dialog.textviewer(translation(30741) if GERM else translation(30742), plot, usemono=True)

def create_substances(info, naming, category, phrase, extras, FOLDER=True, STOCK=False):
	(Note_1, Note_2, Note_3), FANART = ("" for _ in range(3)), defaultFanart
	SEASON, EPISODE, TAGLINE, start_times, AIRED, BEGINS, ends_times, MPAA, ARGIOS, DURATION, THUMB, POSTER = (None for _ in range(12))
	YEAR_SET, COUS_SET, DIRS_SET, CREA_SET, STAR_SET = (None for _ in range(5))
	CID = info['id'].split('_')[0] if info.get('id', '') and '_' in info['id'] else info['id'] if info.get('id', '') else None
	PID = info.get('programId', None)
	NAME = info['title'].strip()
	SUBTITLE = info['subtitle'].strip() if info.get('subtitle', '') else None
	MARKER ='lastOverview' if str(info.get('code')).lower().startswith(('collection_videos', 'collection_subcollection')) else None # Hide Poster-Pictures in Season/Episode-Listing
	matchSEA = re.search(r'(Staffel:? |Saison:? )([0-9]+)', info['title']) # "Staffel 2, Folge 5 // Staffel: 2, Folge: 6 // S2 E10 // (2/2)
	if matchSEA: SEASON = f"{int(matchSEA.group(2)):02}" if str(matchSEA.group(2)).isdecimal() and int(matchSEA.group(2)) != 0 else None
	matchEP = re.search(r'(Episode:? |Épisode:? |Folge:? |E)([0-9]+)', info['title']) # Folge 18 // Staffel: 2, Folge: 6 // S2 E10
	if matchEP: EPISODE = f"{int(matchEP.group(2)):02}" if str(matchEP.group(2)).isdecimal() and int(matchEP.group(2)) != 0 else None
	if EPISODE is None:
		matchSO = re.search(r'\(([0-9]+)/[0-9]+\)', info['title']) # (1/2)
		if matchSO: EPISODE = f"{int(matchSO.group(1)):02}" if str(matchSO.group(1)).isdecimal() and int(matchSO.group(1)) != 0 else None
	if EPISODE is None and SUBTITLE:
		matchDE = re.search(r'(Episode:? |Épisode:? |Folge:? |E)([0-9]+)', SUBTITLE) # Folge 18 // Staffel: 2, Folge: 6 // S2 E10
		if matchDE: EPISODE = f"{int(matchDE.group(2)):02}" if str(matchDE.group(2)).isdecimal() and int(matchDE.group(2)) != 0 else None
	if str(NAME)[:10].upper() in ['BANNER TEM', 'ZONE EVENT'] and info.get('content', '') and info['content'].get('data', '') and len(info['content']['data']) > 0:
		NAME = f"{info['content']['data'][0]['title'].strip()}  [COLOR lime](Special)[/COLOR]"
	TAGLINE = info['teaserText'].strip() if info.get('teaserText', '') else None
	if TAGLINE and len(TAGLINE) > 125:
		TAGLINE = f"{TAGLINE[:125]}..."
	if info.get('availability', ''):
		if category == 'DATA_ONE' and str(info['availability'].get('upcomingDate'))[:4] not in ['None', '0', '1970']:
			local_upcom = get_CentralTime(info['availability']['upcomingDate'])
			NAME = f"[COLOR orange]{local_upcom.strftime('%H:%M')}[/COLOR]  {NAME}"
		if str(info['availability'].get('start'))[:4] not in ['None', '0', '1970']:
			local_start = get_CentralTime(info['availability']['start'])
			start_times = local_start.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
			AIRED = local_start.strftime('%d.%m.%Y') # FirstAired
			BEGINS = local_start.strftime('%Y-%m-%dT%H:%M') if KODI_BUILD >= 20 else local_start.strftime('%d.%m.%Y') # 2023-03-09T12:30:00 = NEWFORMAT // 09.03.2023 = OLDFORMAT
		if str(info['availability'].get('end'))[:4] not in ['None', '0', '1970']:
			local_ends = get_CentralTime(info['availability']['end'])
			ends_times = local_ends.strftime('%d{0}%m{0}%y {1} %H{2}%M').format('.', '•', ':')
	if str(info.get('ageRating')).isdecimal():
		MPAA = translation(30761).format(info['ageRating'])
	GENRE = info['genre']['label'].strip() if info.get('genre', '') and info['genre'].get('label', '') else None
	if info.get('credits', '') and len(info['credits']) > 2:
		YEARING = next(filter(lambda xv: (xv.get('values', '') and xv.get('code') == 'PRODUCTION_YEAR'), info.get('credits', [])), None)
		YEAR_SET = [year for year in YEARING.get('values', {})][0] if YEARING else None
		COUNTRIES = next(filter(lambda xv: (xv.get('values', '') and xv.get('code') == 'COUNTRY'), info.get('credits', [])), None)
		COUS_SET = ', '.join(sorted([cous for cous in COUNTRIES.get('values', {})])) if COUNTRIES else None
		DIRECTORS = next(filter(lambda xv: (xv.get('values', '') and xv.get('code') == 'REA'), info.get('credits', [])), None)
		DIRS_SET = ', '.join(sorted([dirs for dirs in DIRECTORS.get('values', {})])) if DIRECTORS else None
		WRITERS = next(filter(lambda xv: (xv.get('values', '') and xv.get('code') == 'SCE'), info.get('credits', [])), None)
		CREA_SET = ', '.join(sorted([creas for creas in WRITERS.get('values', {})])) if WRITERS else None
		STARRING = next(filter(lambda xv: (xv.get('values', '') and xv.get('code') == 'ACT'), info.get('credits', [])), None)
		STAR_SET = ', '.join([stars for stars in STARRING.get('values', {})]) if STARRING else None
	if category =='ZONE_TWO':
		FOLLOW = 'listBroadcasts'
		if info.get('code', '') and str(info['code']).lower().startswith('collection_videos') and info.get('id', '') and info['id'].count('_') == 1:
			gangway = '111'
			ACCESS = config['collections_two'].format(API_EMAC, info['id'].split('_')[0], WEB_LANG, info['id'].split('_')[1])
		elif info.get('code', '') and str(info['code']).lower().startswith('collection_subcollection') and info.get('id', '') and info['id'].count('_') == 2:
			gangway = '222'
			ACCESS = config['collections_three'].format(API_EMAC, info['id'].split('_')[0], WEB_LANG, info['id'].split('_')[1], info['id'].split('_')[2])
		else:
			DEEPLINK = info['link']['deeplink'] if info.get('link', '') and info['link'].get('deeplink', '') else info['deeplink'] if info.get('deeplink', '') else None
			LINKPAGE = info['link']['page'] if info.get('link', '') and info['link'].get('page', '') else info['page'] if info.get('page', '') else None
			if (DEEPLINK or LINKPAGE):
				ROUTE_ONE = DEEPLINK.upper().split('/')[-1] if DEEPLINK and 'emac' in DEEPLINK else \
					LINKPAGE.upper() if LINKPAGE and str(LINKPAGE)[:3] != 'RC-' else None
				ROUTE_TWO = DEEPLINK.split('/')[-1] if DEEPLINK and 'collection' in DEEPLINK else \
					LINKPAGE if LINKPAGE and str(LINKPAGE)[:3] == 'RC-' else None
				if ROUTE_ONE:
					gangway = '333'
					ACCESS = config['edges_two'].format(API_EMAC, ROUTE_ONE)
				elif ROUTE_TWO:
					gangway = '444'
					ACCESS = config['collections_one'].format(API_EMAC, ROUTE_TWO)
			elif CID in ['2f19c109-044b-420b-9069-6c2e5daf6a74', '67747aea-5426-4b45-8ef4-f648fd227a69', 'a4245cee-29a8-4ae1-9d6b-df5d1b280002', 'cbde5425-226c-4638-b9f6-6847e509db7f']:
				if CID in ['2f19c109-044b-420b-9069-6c2e5daf6a74', 'a4245cee-29a8-4ae1-9d6b-df5d1b280002']:
					gangway = '555' # 1.Musik Genres(a74)+3.Parcourir les genres(002)
					FOLLOW, ACCESS = 'listCategories', 'MUSICS'
				else:
					gangway = '666' # 2.Alle Kategorien(a69)+4.Parcourir toute l'offre(b7f) ???
					FOLLOW, ACCESS = 'listCategories', 'THEMES'
			elif CID in ['0f41c5ac-eb59-4a54-8fea-75a1cbfa4c22', 'faab3de5-678c-4a5b-9f56-3c96838beded']:
				gangway = '666' # 1.Geschichte nach Themen(c22)+2.Parcourir toute l'offre Histoire(ded)
				FOLLOW, ACCESS = 'listThoroughs', 'HISTORY'
			else:
				gangway = '777'
				ACCESS = config['zones_one'].format(API_EMAC, CID, WEB_LANG)
		ARGIOS = {'mode': FOLLOW, 'link': ACCESS, 'phase': phrase, 'name': NAME}
	elif category in ['DATA_ONE', 'DATA_TWO', 'DATA_THREE'] and ((PID and len(PID) > 5) or (str(CID)[:3] == 'RC-')):
		if 'COLLECTION' in str(info.get('stickers')):
			gangway = 'P-888'
			ACCESS = config['collections_one'].format(API_EMAC, CID if str(CID)[:3] == 'RC-' else PID)
			ARGIOS = {'mode': 'listBroadcasts', 'link': ACCESS, 'phase': phrase, 'name': NAME}
		elif 'FULL_VIDEO' in str(info.get('stickers')) and str(info.get('duration')).isdecimal() and int(info['duration']) > 0:
			gangway = 'P-999'
			ACCESS, FOLDER = PID, False
			ARGIOS = {'mode': 'playVideo', 'link': ACCESS}
			DURATION = int(info['duration'])
		else:
			gangway, ACCESS, ARGIOS = 'NULL', 'NO ►COLLECTION◄ OR ►FULL_VIDEO◄ IN STICKERS', None
	else:
		gangway, ACCESS, ARGIOS = 'NULL', 'CATEGORY IS NOTHING, BECAUSE PROGRAMID IS NONE', None
	if info.get('availability', '') and info['availability'].get('type', '') == 'LIVESTREAM_WEB': ACCESS, ARGIOS = 'LIVESTREAM_WEB', None # 1. noch nicht vorh. Videos // 2. z.b. Das Wichtigste in Kürze unter Aktuelles und Gesellschaft
	SERIE = re.sub(r'(\([0-9]+/[0-9]+\)| - Staffel:? [0-9]+| - Saison:? [0-9]+)', '', naming).strip() if DURATION and naming and (info.get('type', '') == 'teaser' or info.get('standaloneContent', False) is True) else None
	if SUBTITLE and phrase != 'TV_GUIDE' and re.search(r'(Staffel:? [0-9]+|Saison:? [0-9]+)', NAME) and FOLDER is False:
		NAME = f"Staffel{NAME.split('Staffel')[1]} - {SUBTITLE}" if GERM and 'Staffel' in NAME else f"Saison{NAME.split('Saison')[1]} - {SUBTITLE}"
	elif SUBTITLE and phrase != 'TV_GUIDE' and SERIE and SERIE.title() in NAME.title() and FOLDER is False:
		NAME = f"{SUBTITLE.replace('(', '[').replace(')', ']')}{NAME.title().replace(SERIE.title(), '')}"
	elif SUBTITLE and phrase == 'TV_GUIDE' and SERIE and FOLDER is False:
		NAME = f"{NAME.split('[/COLOR]  ')[0]}[/COLOR]  {SUBTITLE.replace('(', '[').replace(')', ']')}{NAME.split('[/COLOR]  ')[1].title().replace(SERIE.title(), '')}"
	elif SUBTITLE and (phrase == 'TV_GUIDE' or not re.search(r'(Staffel:? [0-9]+|Saison:? [0-9]+)', NAME)) and (SERIE is None or SERIE.title() not in SUBTITLE.title()) and FOLDER is False:
		NAME = f"{NAME} - {SUBTITLE}"
	elif SUBTITLE and FOLDER is True: TAGLINE = SUBTITLE
	DESCRIPT = get_Description(info)
	if TAGLINE and (TAGLINE.replace('.', '') == SERIE or TAGLINE[:-7] in DESCRIPT): TAGLINE = None
	if SERIE and phrase != 'TV_GUIDE' and SERIE.title() != NAME.title(): Note_1 = translation(30762).format(SERIE)
	if SERIE and phrase == 'TV_GUIDE' and SERIE.title() != NAME.split('[/COLOR]  ')[1].title(): Note_1 = translation(30762).format(SERIE)
	if SEASON and EPISODE:
		Note_2 = translation(30763).format(SEASON, EPISODE) if GERM else translation(30764).format(SEASON, EPISODE)
	elif SEASON is None and EPISODE: 
		Note_2 = translation(30765).format(EPISODE) if GERM else translation(30766).format(EPISODE)
	if start_times and ends_times:
		Note_3 = translation(30767).format(start_times, ends_times) if GERM else translation(30768).format(start_times, ends_times)
	elif start_times and ends_times is None:
		Note_3 = translation(30769).format(start_times) if GERM else translation(30770).format(start_times)
	elif SERIE and start_times is None and ends_times is None: Note_3 = '[CR]'
	PLOT_SHORT = Note_2+Note_3+DESCRIPT
	PLOT_LONG = Note_1+PLOT_SHORT
	if MPAA and FOLDER is True: MPAA = None # Hide MPAA on Folders
	if info.get('mainImage', '') and info['mainImage'].get('url', ''):
		resources, STOCK = info['mainImage']['url'], True
	if STOCK is False and info.get('content', '') and info['content'].get('data', '') and len(info['content']['data']) > 0 and \
		info['content']['data'][0].get('mainImage', '') and info['content']['data'][0]['mainImage'].get('url', ''):
		resources, STOCK = info['content']['data'][0]['mainImage']['url'], True
	if STOCK: # Square=940x940 or Square=720x720 / Portrait=500x750 / Banner=1024x256 or Banner=768x192 / Landscape=1920x1080
		THUMB = resources.split('?type=TEXT')[0].replace('__SIZE__', '1280x720')+'?type=TEXT'
		POSTER = resources.split('?type=TEXT')[0].replace('__SIZE__', '500x750')+'?type=TEXT'
		FANART = resources.split('?type=TEXT')[0].replace('__SIZE__', '1920x1080')+'?type=TEXT'
	FETCH_UNO = {'Title': NAME, 'TvShowTitle': SERIE if Note_1 != "" else None, 'Tagline': TAGLINE, 'Desc_Small': PLOT_SHORT, 'Plot': PLOT_LONG, 'Duration': DURATION, 'Season': SEASON, \
		'Episode': EPISODE, 'Date': BEGINS, 'Aired': AIRED, 'Year': YEAR_SET, 'Genre': GENRE, 'Country': COUS_SET, 'Director': DIRS_SET, 'Writer': CREA_SET, 'Cast': STAR_SET, 'Mpaa': MPAA, \
		'Mediatype': 'episode' if not FOLDER else None, 'Image': THUMB, 'Poster': POSTER, 'Fanback': FANART, 'Reference': 'Single' if not FOLDER else None, 'Marker': MARKER}
	if extras:
		debug_MS(f"{extras} ### TITLE : {NAME} || CATEGORY : {category} || PHRASE : {phrase} || CALLno : {gangway} ###")
		debug_MS(f"{extras} ### URL : {ACCESS} || CID : {CID} || CODE : {info.get('code', None)} || PROGRAM_ID : {PID} ###")
		debug_MS(f"{extras} ### is FOLDER : {FOLDER} || DURATION : {DURATION} || THUMB : {THUMB} ###")
		debug_MS("---------------------------------------------")
	return [ARGIOS, FETCH_UNO, FOLDER]

def playVideo(TARGET):
	debug_MS("(navigator.playVideo) ------------------------------------------------ START = playVideo -----------------------------------------------")
	"""
	Übergabe des Abspiellinks von anderem Video-ADDON: plugin://plugin.video.artetv.de/?mode=playVideo&link=048256-000-A oder: plugin://plugin.video.artetv.de/?mode=playVideo&link=https://www.arte.tv/de/videos/048256-000-A/wir-waren-koenige/
	NEW_MP4: https://www.arte.tv/hbbtvv2/services/web/index.php/OPA/v3/streams/092065-000-A/SHOW/de // at 28.09.2024
	DEUTSCH::: "VOA" = Original deutsch | "VOA-STMA" = Original mit deutschen Untertiteln | "VAAUD" = Deutsch mit Audiodescription | "OV" = Stumm oder Originalversion | "VOA-STF" = Deutsch/UT-Französisch
	FRANCE::: "VOF" = Original französisch | "VF-STF" = französisch vertont | "VFAUD" = Französisch mit Audiodescription | "VOF-STMF" = Stumm oder Original mit französischen Untertiteln
	"""
	(MASTERS, MEDIAS), (PRESENT_UNO, PRESENT_DUE, STREAM, QUALITY, FINAL_URL, TEST_URL) = ([] for _ in range(2)), (False for _ in range(6))
	PLID = re.compile(r'/videos/([^/]+)/', re.S).findall(TARGET)[0] if TARGET[:4] == 'http' else TARGET
	debug_MS(f"(navigator.playVideo[1]) ### Original-URL = {TARGET} || PLID = {PLID} ###")
	QUALITIES = [2160, 1080, 720, 406, 360, 216] # Height of the Stream
	SHORTCUTS = ['DE', 'UT', 'AD'] if GERM else ['FR', 'UT', 'AD']
	try:
		DATA_UNO = getContent(config['player_mp4'].format(PLID, WEB_LANG.lower())) # For mp4- Streams // Currently function without Token 11.02.2026
		if len(DATA_UNO['videoStreams']) >= 1: PRESENT_UNO = True
	except: pass
	if PRESENT_UNO:
		for each in DATA_UNO['videoStreams']:
			stream_one = each.get('url', '')
			version_one = each.get('audioSlot') if str(each.get('audioSlot')).isdecimal() else 0
			name_one    = each.get('audioLabel', 'NOT FOUND')
			lang_one      = each.get('audioShortLabel', 'NOT FOUND')
			quality_one  = each.get('height') if str(each.get('height')).isdecimal() else 0
			mime_one    = 'video/mp4'
			if version_one == 1 and '.mp4' in stream_one and int(quality_one) > 358:
				MEDIAS.append({'link': stream_one, 'quality': quality_one, 'mimeType': mime_one, 'name': name_one, 'language': lang_one})
				MEDIAS = sorted(MEDIAS, key=lambda v3: int(v3['quality']), reverse=True)
		debug_MS(f"(navigator.playVideo[2]) SORTED_LIST | MPP4 ### sorted_LIST : {MEDIAS} ###")
	try:
		DATA_DUE = getContent(config['player_m3u8'].format(WEB_LANG.lower(), PLID), AUTH=PLAY_TOKEN) # For HLS- and m3u8- Streams // Currently function with or without Token 11.02.2026
		if len(DATA_DUE['data']['attributes']['streams']) >= 1: PRESENT_DUE = True
	except: pass
	if PRESENT_DUE:
		for elem in DATA_DUE['data']['attributes']['streams']:
			stream_two = elem.get('url', '')
			name_two    = elem['versions'][0]['label'] if elem.get('versions', '') and elem.get('versions', {})[0].get('label', '') else 'NOT FOUND'
			lang_two      = elem['versions'][0]['shortLabel'] if elem.get('versions', '') and elem.get('versions', {})[0].get('shortLabel', '') else 'NOT FOUND'
			height_two  = elem['mainQuality']['label'] if elem.get('mainQuality', '') and elem['mainQuality'].get('label', '') else 'NOT FOUND'
			quality_two  = height_two.replace('p', '') if height_two != 'NOT FOUND' and not isinstance(height_two, int) else height_two if height_two != 'NOT FOUND' and isinstance(height_two, int) else 0
			version_two  = elem.get('slot') if str(elem.get('slot')).isdecimal() else 0
			mime_two     = 'application/vnd.apple.mpegurl'
			if version_two == 1 and '.m3u8' in stream_two and int(quality_two) > 404:
				MASTERS.append({'link': stream_two, 'quality': quality_two, 'mimeType': mime_two, 'name': name_two, 'language': lang_two})
				MASTERS = sorted(MASTERS, key=lambda v2: int(v2['quality']), reverse=True)
		debug_MS(f"(navigator.playVideo[3]) SORTED_LIST | M3U8 ### sorted_LIST : {MASTERS} ###")
	if ((prefer_stream == 1 and not enable_adaptive) or (not MASTERS)) and MEDIAS:
		debug_MS("(navigator.playVideo[4]) ~~~~~ TRY NUMBER ONE TO GET THE FINALURL (mp4) ~~~~~")
		STREAM, MIME, QUALITY, FINAL_URL = 'MP4', MEDIAS[0]['mimeType'], MEDIAS[0]['quality'], MEDIAS[0]['link']
	if not FINAL_URL and MASTERS:
		debug_MS("(navigator.playVideo[4]) ~~~~~ TRY NUMBER TWO TO GET THE FINALURL (m3u8/hls) ~~~~~")
		STREAM = 'HLS' if enable_adaptive else 'M3U8'
		MIME, QUALITY, FINAL_URL = MASTERS[0]['mimeType'], MASTERS[0]['quality'], MASTERS[0]['link']
	try: # Test function to see if stream can be played !!!
		code = urlopen(FINAL_URL, timeout=6).getcode()
		if code in [200, 201, 202]: TEST_URL = True
	except: pass
	if FINAL_URL and TEST_URL:
		LSM = xbmcgui.ListItem(path=FINAL_URL, offscreen=True)
		LSM.setMimeType(MIME)
		if plugin_operate('inputstream.adaptive') and STREAM in ['HLS', 'MPD']:
			IA_NAME = 'inputstream.adaptive'
			LSM.setContentLookup(False), LSM.setProperty('inputstream', IA_NAME)
			if KODI_BUILD in [19, 20]: LSM.setProperty(f"{IA_NAME}.manifest_type", STREAM.lower()) # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
			PHRASE = 'stream' if KODI_BUILD == 19 else 'manifest' if KODI_BUILD in [20, 21] else 'common'
			LSM.setProperty(f"{IA_NAME}.{PHRASE}_headers", f"User-Agent={get_userAgent}") # 'stream_headers' ON KODI v19 // 'manifest_headers' ON KODI v20 and v21 // 'common_headers' ON KODI v22 and above
		xbmcplugin.setResolvedUrl(ADDON_HANDLE, True, LSM)
		log(f"(navigator.playVideo) [{QUALITY}p] {STREAM}_stream : {FINAL_URL}")
	elif FINAL_URL and not TEST_URL:
		failing(f"(navigator.playVideo) $$$$$ Playback of the stream is NOT possible; the Stream-URL on the *arte.tv* website is BROKEN or OFFLINE !!! $$$$$\n $$$$$ IDD : {PLID} || FINAL_URL : {FINAL_URL} $$$$$")
		return dialog.notification(translation(30521).format('VIDEO'), translation(30527), icon, 10000)
	else:
		failing(f"(navigator.playVideo) $$$$$ Playback of the stream is NOT possible $$$$$ IDD : {PLID} $$$$$\n ########## NO Stream-Entry found on *arte.tv* !!! ##########")
		return dialog.notification(translation(30521).format('VIDEO'), translation(30528), icon, 8000)

def streamTV():
	debug_MS("(navigator.streamTV) ------------------------------------------------ START = streamTV -----------------------------------------------")
	for item in config['streams']:
		if GERM and 'France' in item.get('description'): continue
		elif not GERM and 'Germany' in item.get('description'): continue
		TITLE = item['title_de'] if GERM else item['title_fr']
		FETCH_UNO = create_entries({'Title': TITLE, 'Image': f"{evepic}{item.get('thumb')}"})
		addDir({'mode': 'playLive', 'link': item['link'], 'name': TITLE, 'extras': f"{evepic}{item.get('thumb')}"}, FETCH_UNO, False)
	xbmcplugin.endOfDirectory(ADDON_HANDLE)

def playLive(TARGET, NAME, EXTRA):
	LTM = xbmcgui.ListItem(NAME, path=TARGET, offscreen=True)
	LTM.setMimeType('application/vnd.apple.mpegurl')
	LTM.setArt({'icon': icon, 'thumb': EXTRA, 'poster': EXTRA})
	if plugin_operate('inputstream.adaptive'):
		IA_NAME = 'inputstream.adaptive'
		LTM.setProperty('inputstream', IA_NAME)
		if KODI_BUILD in [19, 20]: LTM.setProperty(f"{IA_NAME}.manifest_type", 'hls') # DEPRECATED ON Kodi v21, because the manifest type is now auto-detected.
	xbmc.Player().play(item=TARGET, listitem=LTM)

def addDir(params, listitem, folder=True, higher=False, sample='standard'):
	uws, entries = build_mass(params), []
	listitem.setPath(uws)
	if params.get('mode') == 'playVideo' and params.get('link', ''):
		entries.append([translation(32231) if GERM else translation(32232), f"RunPlugin({build_mass({'mode': 'callingInfos', 'link': params.get('link'), 'phase': sample})})"])
	if enable_decrease and higher is True:
		entries.append([translation(32233) if GERM else translation(32234), f"RunPlugin({build_mass({'mode': 'callingMain'})})"])
	if len(entries) > 0: listitem.addContextMenuItems(entries)
	return xbmcplugin.addDirectoryItem(ADDON_HANDLE, uws, listitem, folder)
