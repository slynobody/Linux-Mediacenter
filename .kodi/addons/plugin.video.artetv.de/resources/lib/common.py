# -*- coding: utf-8 -*-

import sys
import os
import re
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import json
import xbmcvfs
import shutil
import socket
import time
from datetime import datetime, timedelta
from calendar import timegm as TGM
import requests
from urllib.parse import parse_qsl, urlencode, quote, unquote, unquote_plus
from urllib.request import urlopen
from concurrent.futures import *
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from .provider import Client


socket.setdefaulttimeout(30)
HOST_AND_PATH				= sys.argv[0]
ADDON_HANDLE				= int(sys.argv[1])
dialog									= xbmcgui.Dialog()
addon									= xbmcaddon.Addon()
addon_id							= addon.getAddonInfo('id')
addon_name						= addon.getAddonInfo('name')
addon_version					= addon.getAddonInfo('version')
addon_desc						= addon.getAddonInfo('description')
addon_folder						= xbmcvfs.translatePath(addon.getAddonInfo('path')).encode('utf-8').decode('utf-8')
addon_profile					= xbmcvfs.translatePath(addon.getAddonInfo('profile')).encode('utf-8').decode('utf-8')
SEARCH_FILE						= xbmcvfs.translatePath(os.path.join(addon_profile, 'search_string'))
defaultFanart						= os.path.join(addon_folder, 'resources', 'media', 'fanart.jpg')
icon										= os.path.join(addon_folder, 'resources', 'media', 'icon.png')
artpic									= os.path.join(addon_folder, 'resources', 'media', '').encode('utf-8').decode('utf-8')
evepic									= os.path.join(addon_folder, 'resources', 'media', 'events', '').encode('utf-8').decode('utf-8')
thepic									= os.path.join(addon_folder, 'resources', 'media', 'themes', '').encode('utf-8').decode('utf-8')
WEB_LANG							= {0: 'DE', 1: 'FR'}[int(addon.getSetting('language'))]
enable_adaptive				= addon.getSetting('use_adaptive') == 'true'
prefer_stream					= int(addon.getSetting('prefer_stream'))
using_fanart						= addon.getSetting('use_fanart') == 'true'
enable_decrease				= addon.getSetting('show_homebutton') == 'true'
verifying								= (True if addon.getSetting('verify_ssl') == 'true' else False)
enable_tune						= addon.getSetting('show_settings') == 'true'
DEB_LEVEL							= (xbmc.LOGINFO if addon.getSetting('enable_debug') == 'true' else xbmc.LOGDEBUG)
KODI_BUILD						= int(xbmc.getInfoLabel('System.BuildVersion')[0:2])
BASE_URL							= 'https://www.arte.tv/'
API_EMAC							= f"https://api.arte.tv/api/emac/v4/{WEB_LANG.lower()}/web/" # https://www.arte.tv/api/emac/v4/
API_OPA								= f"https://api.arte.tv/api/opa/v3/categories?language={WEB_LANG.lower()}&limit=50"
EMAC_TOKEN						= 'wYxYGNiBjNwQjZzIjMhRDOllDMwEjM2MDN3MjY4U2M1ATYkVWOkZTM5QzM4YzN2ITM0E2MxgDO1EjN5kjZmZWM reraeB'
OPA_TOKEN						= 'AOwImM4EGZ2gjYjRGZzEzYxMTNxMWOjJDO4gDO3UWN3UmN5IjNzAzMlRmMwEWM2I2NhFWN1kjYkJjZ1cjY1czN reraeB'
PLAY_TOKEN						= 'gZzYTO3EjNwUmZ1gTYklDZyAzMkF2Y5I2NwIGM0EGZldTM0MTM5YWN0ATMzMDOxkjYjBjNjBjMkFWM4MmNiZTZ reraeB'
traversing							= Client(Client.CONFIG_ARTE)

GERM = True if WEB_LANG == 'DE' else False
xbmcplugin.setContent(ADDON_HANDLE, 'movies')

def py3_dec(d, nom='utf-8', ign='ignore'):
	if isinstance(d, bytes):
		d = d.decode(nom, ign)
	return d

def translation(id):
	return addon.getLocalizedString(id)

def failing(content):
	log(content, xbmc.LOGERROR)

def debug_MS(content):
	log(content, DEB_LEVEL)

def log(msg, level=xbmc.LOGINFO):
	return xbmc.log(f"[{addon_id} v.{addon_version}]{str(msg)}", level)

def build_mass(body):
	return f"{HOST_AND_PATH}?{urlencode(body)}"

def get_userAgent(REV='150.0', VER='150.0'):
	base = f"Mozilla/5.0 {{}} Gecko/20100101 Firefox/{VER}"
	if xbmc.getCondVisibility('System.Platform.Android'):
		if 'arm' in os.uname()[4]: return base.format(f"(X11; Linux arm64; rv:{REV})") # ARM based Linux
		return base.format(f"(X11; Linux x86_64; rv:{REV})") # x64 Linux
	elif xbmc.getCondVisibility('System.Platform.Windows'):
		return base.format(f"(Windows NT 10.0; Win64; x64; rv:{REV})") # Windows
	elif xbmc.getCondVisibility('System.Platform.IOS'):
		return 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0 Mobile/15E148 Safari/604.1' # iOS iPhone/iPad
	elif xbmc.getCondVisibility('System.Platform.Darwin') or xbmc.getCondVisibility('System.Platform.OSX'):
		return base.format(f"(Macintosh; Intel Mac OS X 10.15; rv:{REV})") # Mac OSX
	return base.format(f"(X11; Linux x86_64; rv:{REV})") # x64 Linux

def _header(REFERRER=None, USERTOKEN=None):
	header = {} # !!! Accept-Language only set if browser should offer these languages !!!
	header['Cache-Control'] = 'public, max-age=300'
	header['Accept'] = 'application/json'
	header['Content-Type'] = 'application/json; charset=utf-8'
	header['User-Agent'] = get_userAgent()
	header['DNT'] = '1'
	header['Upgrade-Insecure-Requests'] = '1'
	header['Accept-Encoding'] = 'gzip'
	header['Accept-Language'] = 'de-DE,de;q=0.9,en;q=0.8' if WEB_LANG == 'DE' else 'fr-FR,fr;q=0.9,en;q=0.8'
	header['Referer'] = BASE_URL
	if USERTOKEN: header['Authorization'] = USERTOKEN[::-1]
	return header

def getContent(url, method='GET', queries='JSON', REF=None, AUTH=None, headers={}, redirects=True, verify=verifying, data=None, json=None, timeout=30):
	fixation, ANSWER = requests.Session(), None
	try:
		response = fixation.request(method, url, headers=_header(REF, AUTH), allow_redirects=redirects, verify=verify, timeout=timeout)
		response.raise_for_status()
		ANSWER = response.json() if queries == 'JSON' else response.text if queries == 'TEXT' else response
		debug_MS(f"(common.getContent) === CALLBACK === STATUS : {response.status_code} || URL : {response.url} || HEADER : {_header(REF, AUTH)} ===")
	except Exception as exc:
		failing(f"(common.getContent) ERROR - EXEPTION - ERROR ##### URL : {url} === FAILURE : {exc} #####")
		dialog.notification(translation(30521).format('URL'), translation(30523).format(exc), icon, 12000)
		return sys.exit(0)
	return ANSWER

def plugin_operate(MARKING):
	check_uno = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.GetAddonDetails","params":{{"addonid":"{MARKING}","properties":["enabled"]}}}}')
	answer_uno, answer_due = json.loads(check_uno), json.loads(f'{{"error": "{MARKING} NOT FOUND"}}')
	if not "error" in answer_uno.keys() and answer_uno.get('result', '') and answer_uno['result'].get('addon', {}).get('enabled', False) is False:
		try:
			xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.SetAddonEnabled","params":{{"addonid":"{MARKING}","enabled":true}}}}')
			failing(f"(common.plugin_operate) ERROR - ACTIVATED - ERROR :\n##### Das benötigte Addon : *{MARKING}* ist NICHT aktiviert !!! #####\n##### Es wird jetzt versucht die Aktivierung durchzuführen !!! #####")
		except: pass
		del answer_due
		check_due = xbmc.executeJSONRPC(f'{{"jsonrpc":"2.0","id":1,"method":"Addons.GetAddonDetails","params":{{"addonid":"{MARKING}","properties":["enabled"]}}}}')
		answer_due = json.loads(check_due)
	if (answer_uno.get('result', '') and answer_uno['result'].get('addon', {}).get('enabled', False) is True) or (answer_due.get('result', '') and answer_due['result'].get('addon', {}).get('enabled', False) is True):
		return True
	if answer_due.get('result', '') and answer_due['result'].get('addon', {}).get('enabled', False) is False:
		dialog.ok(addon_id, translation(30501).format(MARKING))
		failing(f"(common.plugin_operate) ERROR - ACTIVATED - ERROR :\n##### Das benötigte Addon : *{MARKING}* ist NICHT aktiviert !!! #####\n##### Eine automatische Aktivierung ist leider NICHT möglich !!! #####")
	if "error" in answer_uno.keys() or "error" in answer_due.keys():
		dialog.ok(addon_id, translation(30502).format(MARKING))
		failing(f"(common.plugin_operate) ERROR - INSTALLED - ERROR :\n##### Das benötigte Addon : *{MARKING}* ist NICHT installiert !!! #####")
	return False

def getSorting():
	return [xbmcplugin.SORT_METHOD_UNSORTED, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE, xbmcplugin.SORT_METHOD_DATE, xbmcplugin.SORT_METHOD_DURATION]

def get_CentralTime(info):
	UTC_DATE = datetime(*(time.strptime(info[:19], '%Y-%m-%dT%H:%M:%S')[0:6]))
	try:
		LOCAL_DATE = datetime.fromtimestamp(TGM(UTC_DATE.timetuple()))
		assert UTC_DATE.resolution >= timedelta(microseconds=1)
		LOCAL_DATE = LOCAL_DATE.replace(microsecond=UTC_DATE.microsecond)
	except (ValueError, OverflowError): # ERROR on Android 32bit Systems = cannot convert unix timestamp over year 2038
		LOCAL_DATE = datetime.fromtimestamp(0) + timedelta(seconds=TGM(UTC_DATE.timetuple()))
		LOCAL_DATE = LOCAL_DATE - timedelta(hours=datetime.timetuple(LOCAL_DATE).tm_isdst)
	return LOCAL_DATE

def get_Description(info):
	if info.get('fullDescription', '') and len(cleaning(info['fullDescription'])) > 10:
		return cleaning(info['fullDescription'])
	elif info.get('description', '') and len(cleaning(info['description'])) > 10:
		return cleaning(info['description'])
	elif info.get('shortDescription', '') and len(cleaning(info['shortDescription'])) > 10:
		return cleaning(info['shortDescription'])
	return ""

def preserve(store, data=None):
	if data is not None:
		with open(store, 'w') as topics:
			topics.write(data)
	else:
		with open(store, 'r') as topics:
			arrive = topics.read()
		return arrive

def cleaning(text):
	if text is not None:
		text = re.sub(r'<br ?/>', '[CR]', text.replace('. ', '.').replace('.', '. ').replace('! ', '!').replace('!', '! ').replace('? ', '?').replace('?', '? '))
		text = re.sub(r'\<.*?\>', '', text)
		text = text.replace('\n\n\n\n', '[CR][CR]').replace('\n\n\n', '[CR][CR]').replace('[CR][CR][CR][CR]', '[CR][CR]').replace('[CR][CR][CR]', '[CR][CR]').strip()
	return text

def create_entries(metadata, SIGNS=None):
	listitem = xbmcgui.ListItem(metadata['Title'])
	vinfo = listitem.getVideoInfoTag() if KODI_BUILD >= 20 else {}
	if KODI_BUILD >= 20: vinfo.setTitle(metadata['Title'])
	else: vinfo['Title'] = metadata['Title']
	if metadata.get('TvShowTitle', ''):
		if KODI_BUILD >= 20: vinfo.setTvShowTitle(metadata['TvShowTitle'])
		else: vinfo['Tvshowtitle'] = metadata['TvShowTitle']
	if metadata.get('Tagline', ''):
		if KODI_BUILD >= 20: vinfo.setTagLine(metadata['Tagline'])
		else: vinfo['Tagline'] = metadata['Tagline']
	description = metadata['Plot'] if metadata.get('Plot') not in ['', 'None', None] else ' '
	if KODI_BUILD >= 20: vinfo.setPlot(description)
	else: vinfo['Plot'] = description
	if str(metadata.get('Duration')).isdecimal():
		if KODI_BUILD >= 20: vinfo.setDuration(int(metadata['Duration']))
		else: vinfo['Duration'] = metadata['Duration']
	if str(metadata.get('Season')).isdecimal():
		if KODI_BUILD >= 20: vinfo.setSeason(int(metadata['Season']))
		else: vinfo['Season'] = metadata['Season']
	if str(metadata.get('Episode')).isdecimal():
		if KODI_BUILD >= 20: vinfo.setEpisode(int(metadata['Episode']))
		else: vinfo['Episode'] = metadata['Episode']
	if metadata.get('Date', ''):
		if KODI_BUILD >= 20: listitem.setDateTime(metadata['Date'])
		else: vinfo['Date'] = metadata['Date']
	if metadata.get('Aired', ''):
		if KODI_BUILD >= 20: vinfo.setFirstAired(metadata['Aired'])
		else: vinfo['Aired'] = metadata['Aired']
	if str(metadata.get('Year')).isdecimal():
		if KODI_BUILD >= 20: vinfo.setYear(int(metadata['Year']))
		else: vinfo['Year'] = metadata['Year']
	elif str(metadata.get('Aired'))[6:10].isdecimal():
		if KODI_BUILD >= 20: vinfo.setYear(int(metadata['Aired'][6:10]))
		else: vinfo['Year'] = metadata['Aired'][6:10]
	if metadata.get('Genre', '') and metadata.get('Reference') == 'Single':
		if KODI_BUILD >= 20: vinfo.setGenres([metadata['Genre']])
		else: vinfo['Genre'] = metadata['Genre']
	if metadata.get('Country', ''):
		if KODI_BUILD >= 20: vinfo.setCountries([metadata['Country']])
		else: vinfo['Country'] = metadata['Country']
	if metadata.get('Director', ''):
		if KODI_BUILD >= 20: vinfo.setDirectors([metadata['Director']])
		else: vinfo['Director'] = metadata['Director']
	if metadata.get('Writer', ''):
		if KODI_BUILD >= 20: vinfo.setWriters([metadata['Writer']])
		else: vinfo['Writer'] = metadata['Writer']
	if metadata.get('Cast', '') and len(metadata['Cast']) > 10:
		CASTING = []
		for index, person in enumerate(metadata['Cast'].split(','), 1):
			actor = {'name': person, 'role': '', 'order': index, 'thumb': ''}
			if actor['name'] not in ['' , None]:
				CASTING.append(xbmc.Actor(actor['name'], actor['role'], actor['order'], actor['thumb'])) if KODI_BUILD >= 20 else CASTING.append(actor)
		if CASTING and len(CASTING) > 0 and KODI_BUILD >= 20: vinfo.setCast(CASTING)
		elif CASTING and len(CASTING) > 0 and not KODI_BUILD >= 20: listitem.setCast(CASTING)
	if metadata.get('Mpaa', ''):
		if KODI_BUILD >= 20: vinfo.setMpaa(str(metadata['Mpaa']))
		else: vinfo['Mpaa'] = str(metadata['Mpaa'])
	if KODI_BUILD >= 20: vinfo.setStudios(['ARTE'])
	else: vinfo['Studio'] = 'ARTE'
	if metadata.get('Mediatype', ''):
		if KODI_BUILD >= 20: vinfo.setMediaType(metadata['Mediatype'])
		else: vinfo['Mediatype'] = metadata['Mediatype']
	picture, portrait = metadata.get('Image', icon), (metadata.get('Poster', '') or metadata.get('Image', icon))
	if metadata.get('Reference') == 'Single':
		listitem.setProperty('IsPlayable', 'true')
		listitem.setArt({'icon': icon, 'thumb': picture, 'poster': picture, 'fanart': defaultFanart}) # POSTERS are displayed truncated in the video overview
	else:
		if metadata.get('Marker') == 'lastOverview': portrait = picture # POSTERS are displayed truncated in season overview = ('collection_subcollection')
		listitem.setArt({'icon': icon, 'thumb': picture, 'poster': portrait, 'fanart': defaultFanart})
	if using_fanart and metadata.get('Fanback', '') and not artpic in metadata['Fanback']:
		listitem.setArt({'fanart': metadata['Fanback']})
	if KODI_BUILD < 20: listitem.setInfo('Video', vinfo)
	return listitem
