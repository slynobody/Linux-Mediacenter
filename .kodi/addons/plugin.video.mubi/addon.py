# -*- coding: utf-8 -*-
import os
import sys

import requests
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs
import re
import base64
import json
import random
import time
import datetime
import math
from urllib.parse import urlencode, quote_plus, quote, unquote, parse_qsl

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
params = dict(parse_qsl(sys.argv[2][1:]))
addon = xbmcaddon.Addon(id='plugin.video.mubi')

PATH=addon.getAddonInfo('path')
PATH_profile=xbmcvfs.translatePath(addon.getAddonInfo('profile'))
if not xbmcvfs.exists(PATH_profile):
    xbmcvfs.mkdir(PATH_profile)
img_path=PATH+'/resources/img/'
img_empty=img_path+'empty.png'
fanart=img_path+'fanart.jpg'

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
baseurl='https://mubi.com/'
apiURL='https://api.mubi.com/v4/'

langs={'English':'en','Deutsch':'de','español':'es','français':'fr','italiano':'it','Nederlands':'nl','português':'pt','Türkçe':'tr'} 
lng=langs[addon.getSetting('lng')]

def heaATVGen():
    getCliCountry()
    hea={
        'User-Agent':'okhttp/4.10.1',
        'accept-encoding':'gzip',
        'accept':'application/json',
        'client':'android_tv',
        'client-version':'36.1',
        'client-device-identifier':addon.getSetting('deviceID'),
        'client-app':'mubi',
        'client-device-brand':'unknown',
        'client-device-model':'sdk_google_atv_x86',
        'client-device-os':'8.0.0',
        'client-accept-audio-codecs':'AAC',
        'client-country':addon.getSetting('client_country')
    }
    return hea

def heaGen():
    getCliCountry()
    HEA={
        'Referer':baseurl,
        'Origin':baseurl[:-1],
        'User-Agent':UA,
        'Authorization':'Bearer '+addon.getSetting('token'),
        'Anonymous_user_id':addon.getSetting('deviceID'),
        'Client':'web',
        'Client-Accept-Audio-Codecs':'eac3,aac',
        'Client-Accept-Video-Codecs':'h265,vp9,h264',
        'Client-Country':addon.getSetting('client_country'),
        'accept-language':lng,
        
    }
    return HEA

def build_url(query):
    return base_url + '?' + urlencode(query)

def addItemList(url, name, setArt, medType=False, infoLab={}, isF=True, isPla='false', contMenu=False, cmItems=[]):
    li=xbmcgui.ListItem(name)
    li.setProperty("IsPlayable", isPla)
    if medType:
        kodiVer=xbmc.getInfoLabel('System.BuildVersion')
        if kodiVer.startswith('19.'):
            li.setInfo(type=medType, infoLabels=infoLab)
        else:
            types={'video':'getVideoInfoTag','music':'getMusicInfoTag'}
            if medType!=False:
                setMedType=getattr(li,types[medType])
                vi=setMedType()
            
                labels={
                    'year':'setYear', #int
                    'episode':'setEpisode', #int
                    'season':'setSeason', #int
                    'rating':'setRating', #float
                    'mpaa':'setMpaa',
                    'plot':'setPlot',
                    'plotoutline':'setPlotOutline',
                    'title':'setTitle',
                    'originaltitle':'setOriginalTitle',
                    'sorttitle':'setSortTitle',
                    'genre':'setGenres', #list
                    'country':'setCountries', #list
                    'director':'setDirectors', #list
                    'studio':'setStudios', #list
                    'writer':'setWriters',#list
                    'duration':'setDuration', #int (in sec)
                    'tag':'setTags', #list
                    'trailer':'setTrailer', #str (path)
                    'mediatype':'setMediaType',
                    'cast':'setCast', #list        
                }
                
                if 'cast' in infoLab:
                    if infoLab['cast']!=None:
                        cast=[xbmc.Actor(c) for c in infoLab['cast']]
                        infoLab['cast']=cast
                
                for i in list(infoLab):
                    if i in list(labels):
                        setLab=getattr(vi,labels[i])
                        setLab(infoLab[i])
    li.setArt(setArt) 
    if contMenu:
        li.addContextMenuItems(cmItems, replaceItems=False)
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=isF)

def directPlayer(stream_url):
    heaPlay={
        'User-Agent':UA,
        'Referer':baseurl,
        'Origin':baseurl[:-1],
    }
    hp=x='&'.join([k+'='+heaPlay[k] for k in heaPlay])
    stream_url+='|'+hp
    play_item = xbmcgui.ListItem(path=stream_url)
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)
    
def ISAplayer(protocol,stream_url, isDRM=False, lickey=False, drm_config=''):
    heaPlay={
        'User-Agent':UA,
        'Referer':baseurl,
        'Origin':baseurl[:-1],
    }
    hp=x='&'.join([k+'='+heaPlay[k] for k in heaPlay])
    import inputstreamhelper
    
    PROTOCOL = protocol
    DRM = 'com.widevine.alpha'
    is_helper = inputstreamhelper.Helper(PROTOCOL, drm=DRM)
    
    if is_helper.check_inputstream():
        play_item = xbmcgui.ListItem(path=stream_url)                     
        play_item.setMimeType('application/xml+dash')
        play_item.setContentLookup(False)
        play_item.setProperty('inputstream', is_helper.inputstream_addon)        
        play_item.setProperty('IsPlayable', 'true')
        play_item.setProperty('inputstream.adaptive.stream_headers', hp)
        play_item.setProperty('inputstream.adaptive.manifest_headers', hp)
        play_item.setProperty('inputstream.adaptive.manifest_type', PROTOCOL)
        if isDRM:
            kodiVer=xbmc.getInfoLabel('System.BuildVersion')
            if int(kodiVer.split('.')[0])<22:
                play_item.setProperty('inputstream.adaptive.license_type', DRM)
                play_item.setProperty('inputstream.adaptive.license_key', lickey)
            else:
                play_item.setProperty('inputstream.adaptive.drm', json.dumps(drm_config))

    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

def code_gen(x):
    base='0123456789abcdef'
    code=''
    for i in range(0,x):
        code+=base[random.randint(0,15)]
    return code

def translate(txtId):
    return addon.getLocalizedString(txtId)
    
nextPageLabel='[COLOR=cyan][B]>>> %s[/B][/COLOR]'%(translate(30016))

def main_menu():
    items=[]
    if addon.getSetting('logged')=='true':
        items=[
            [translate(30001),'browserList','DefaultAddonVideo.png'],#Browse
            [translate(30002),'search','DefaultAddonsSearch.png'],#Search
            [translate(30003),'logOut','DefaultUser.png']#LOG OUT
        ]
    else:
        items=[
            [translate(30004),'logIn','DefaultUser.png']#LOG IN
        ]
    for i in items:
        setArt={'icon': i[2],'fanart':fanart}
        url = build_url({'mode':i[1]})
        addItemList(url, i[0], setArt)
    xbmcplugin.endOfDirectory(addon_handle)   

def browserList():
    browser={translate(30005):'films',translate(30006):'film_groups',translate(30007):'cast_members',translate(30008):'lists',translate(30009):'industry_events'}
    for b in list(browser.keys()):
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultGenre.png', 'fanart': fanart}
        url = build_url({'mode':'browsStngs','categ':browser[b]})
        addItemList(url, b, setArt)
    xbmcplugin.endOfDirectory(addon_handle)

    
def browsStngs(cat):
    init=addon.getSetting('init')
    if init=='true':
        sort=None
        filters=None
        html_categ={'films':'films','film_groups':'collections','cast_members':'cast','lists':'lists','industry_events':'awards-and-festivals'}
        url=baseurl+lng+'/'+html_categ[cat]
        hea={'User-Agent':UA}
        resp=requests.get(url,headers=hea).text
        resp1=resp.split('application/json\">')[1].split('</script')[0]
        js=json.loads(resp1)
        data=js['props']['initialProps']['pageProps']
        if 'sortOptionsForBrowseType' in data and 'initialSelectedSortOptions' in data:
            #domyślne sortowanie
            sort=data['initialSelectedSortOptions']['sort']

            sortData=data['sortOptionsForBrowseType']['sort']#
            setArt={'icon': 'DefaultTags.png'}
            url = build_url({'mode':'browsSort','categ':cat})
            sortLabel=[ss['label'] for ss in data['sortOptionsForBrowseType']['sort'] if ss['value']==sort][0]
            addItemList(url, 'Sortowanie: [B]'+ sortLabel +'[/B]', setArt, isF=False)
        if 'filterDescriptivesForBrowseType' in data:
            #domyślne filtry
            filters=data['initialSelectedFilterOptions']
            
            if data['filterDescriptivesForBrowseType']=={} and (cat=='cast_members' or cat=='industry_events'):
                fltrs_data=data['filterOptionsForBrowseType']
                fltrs=list(fltrs_data.keys())
                filAr={}
                for fl in fltrs:
                    filAr[fl]={}
                    for fll in fltrs_data[fl]:
                        v=fll['value']
                        if v!='':
                            filAr[fl][v]=fll['label']
                
                filtersData=filAr#
               
            else:
                filtersData=data['filterDescriptivesForBrowseType']#
                filAr=data['filterDescriptivesForBrowseType']
            for ff in list(filAr.keys()):
                setArt={'icon': 'DefaultTags.png'}
                url = build_url({'mode':'browsFilter','categ':cat,'filte':ff})
                filterVal=filtersData[ff][filters[ff]] if filters[ff]!='' else 'all'
                addItemList(url, '%s %s: [B]%s[/B]'%(translate(30010),ff,filterVal), setArt, isF=False)
    
    else: #po zmianie parametrów przez użytkownika (funkcje browsSort/browsFilter)
        sort=addon.getSetting('sort')
        if sort=='':
            sort=None
        filters=eval(addon.getSetting('filters'))
        if filters=='':
            filters=None
        sortData=eval(addon.getSetting('sortData'))
        filtersData=eval(addon.getSetting('filtersData'))
        
        if sort!=None:
            setArt={'icon': 'DefaultTags.png'}
            url = build_url({'mode':'browsSort','categ':cat})
            sortLabel=[ss['label'] for ss in sortData if ss['value']==sort][0]
            addItemList(url, 'Sort by: [B]'+ sortLabel +'[/B]', setArt, isF=False)
        if filters!=None:
            for ff in list(filters.keys()):
                setArt={'icon': 'DefaultTags.png'}
                url = build_url({'mode':'browsFilter','categ':cat,'filte':ff})
                filterVal=filtersData[ff][filters[ff]] if filters[ff]!='' else 'all'
                addItemList(url, '%s %s: [B]%s[/B]'%(translate(30010),ff,filterVal), setArt, isF=False)
    
    addon.setSetting('sort',sort)
    addon.setSetting('filters',str(filters))
    try:
        addon.setSetting('sortData',str(sortData))
    except:
        pass
    try:
        addon.setSetting('filtersData',str(filtersData))
    except:
        pass
    
    setArt={'icon': 'DefaultAddonVideo.png'}
    url = build_url({'mode':'contList','categ':cat,'sort':sort,'filters':str(filters)})
    addItemList(url, '>>> %s'%(translate(30011)), setArt)
    
    xbmcplugin.endOfDirectory(addon_handle)
    
def browsSort(cat):
    sort=addon.getSetting('sort')
    sortData=eval(addon.getSetting('sortData'))

    labels=[s['label'] for s in sortData]
    select = xbmcgui.Dialog().select(translate(30100), labels)
    if select > -1:
        sort=sortData[select]['value']

    addon.setSetting('init','false')
    addon.setSetting('sort',sort)
    xbmc.executebuiltin('Container.Refresh')
    
    
def browsFilter(cat,ft):
    filters=eval(addon.getSetting('filters'))
    filtersData=eval(addon.getSetting('filtersData'))

    labels=[filtersData[ft][k] for k in list(filtersData[ft].keys())]
    select = xbmcgui.Dialog().select(translate(30101), labels)
    if select > -1:
        ftVal=list(filtersData[ft].keys())[select]
    else:
        ftVal=filters[ft]

    filters[ft]=ftVal

    addon.setSetting('init','false')
    addon.setSetting('filters',str(filters))
    xbmc.executebuiltin('Container.Refresh')
    
def addFilmToList(r,ep=False): #helper
    isSeries=False
    if 'series' in r:
        if r['series']!=None:
            isSeries=True
    if not isSeries or ep:
        title=r['title'] if not ep else '%s: %s'%(r['episode']['label'],r['episode']['episode_title'])
        vid=str(r['id'])
        img=r['still_url']
        
        original_title=r['original_title']
        year=r['year']
        dur=r['duration'] if r['duration']!=None else 0
        genres=r['genres']
        directors=[i['name'] for i in r['directors']]
        countries=r['historic_countries']
        desc=r['short_synopsis']
        
        if r['consumable']==None:
            url=build_url({'mode':'noPlay'})
            isPlayable='false'
            titleToList='[I]%s[/I]'%(title)
            desc='[B]'+translate(30012)+'[/B]\n'+desc
            cm=False
            cmItems=[]
        else:
            now=datetime.datetime.now()
            ts=datetime.datetime(*(time.strptime(r['consumable']['available_at'],'%Y-%m-%dT%H:%M:%SZ')[0:6]))
            try:
                te=datetime.datetime(*(time.strptime(r['consumable']['availability_ends_at'],'%Y-%m-%dT%H:%M:%SZ')[0:6]))
                dateEnd=te.strftime('%Y-%m-%d %H:%M')
            except:
                te=None
                dateEnd='n/a'
            dateStart=ts.strftime('%Y-%m-%d %H:%M')
            desc='[B]%s: [/B]%s\n[B]%s: [/B]%s\n'%(translate(30013),dateStart,translate(30014),dateEnd) +desc
            
            
            if (te!=None and now>ts and now<te) or (te==None and now>ts):           
                url=build_url({'mode':'playMubi','vid':vid})
                isPlayable='true'
                titleToList=title
            else:
                url=build_url({'mode':'noPlay'})
                isPlayable='false'
                titleToList='[I]%s[/I]'%(title)
            
            cm=True
            cmItems=[('[B]%s[/B]'%(translate(30015)),'RunPlugin(plugin://plugin.video.mubi?mode=lang&vid='+vid+')')]
        
        trailerURL=''    
        if 'trailer_url' in r:
            if r['trailer_url']!=None:
                trailerURL=build_url({'mode':'trailer','url':r['trailer_url']})
        
        iL={'title': title,'originaltitle':original_title,'sorttitle': title,'plot': desc,'year':year,'genre':genres,'duration':dur*60,'director':directors,'cast':[],'trailer':trailerURL,'mediatype':'movie'}
        if ep:
            iL['mediatype']='episode'
            iL['episode']=r['episode']['number']
            iL['season']=r['episode']['season_number']
            
            
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': fanart}
        addItemList(url, titleToList, setArt, 'video', iL, False, isPlayable, cm, cmItems)
    else:
        rs=r['series']
        
        title=rs['title']
        sid=rs['slug']
        img=r['still_url']
        
        original_title=rs['original_title']
        year=r['year']
        genres=rs['genres']
        directors=[i['name'] for i in r['directors']] if 'directors' in r else []
        countries=r['historic_countries'] if 'historic_countries' in r else []
        desc=rs['short_synopsis']
        
        trailerURL=''    
        if 'trailer_url' in r:
            if r['trailer_url']!=None:
                trailerURL=build_url({'mode':'trailer','url':r['trailer_url']})
        
        url=build_url({'mode':'seasList','sid':sid})
        iL={'title': title,'originaltitle':original_title,'sorttitle': title,'plot': desc,'year':year,'genre':genres,'director':directors,'cast':[],'trailer':trailerURL,'mediatype':'tvshow'}        
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': fanart}
        addItemList(url, title, setArt, 'video', iL, True, 'false')


def seasList(sid):
    url=apiURL+'series/'+sid+'/up_next'
    resp=requests.get(url,headers=heaGen()).json()
    for s in resp['series']['seasons']:
        title=s['title']
        seas_id=s['slug']
        img='DefaultPlaylist.png'
        
        url=build_url({'mode':'epList','sid':sid,'seas_id':seas_id})
        setArt={'thumb': img, 'poster': img, 'banner': img, 'icon': img, 'fanart': fanart}
        addItemList(url, title, setArt)
        
    xbmcplugin.endOfDirectory(addon_handle)

def epList(sid,seas_id,page):
    url=apiURL+'series/'+sid+'/seasons/'+seas_id+'/episodes'
    URLparams={}
    if page!=None:
        URLparams={'page':page}
    
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['episodes']:
        addFilmToList(r,True)
    
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'epList','sid':sid,'seas_id':seas_id,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)    
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)
   
def films(s,f,p): #Browser Lev.1 [lista filmów]
    URLparams={
        'sort':s,
        'playable':'true'
    }
    if f!=None:
        filters=eval(f)
        for ff in list(filters.keys()):
            URLparams[ff]=filters[ff]
    
    if p!=None:
        URLparams.update({'page':p})
    url=apiURL+'browse/films'
    #print(url)
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['films']:
        addFilmToList(r)
        
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'contList','categ':'films','sort':s,'filters':f,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)
        
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)
    
def collections(s,f,p): #Browser Lev.1 
    URLparams={
        'sort':s,
    }
    if p!=None:
        URLparams.update({'page':p})
    url=apiURL+'browse/film_groups'
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['film_groups']:
        title=r['full_title'] if 'full_title' in r else r['title']
        cid=str(r['id'])
        desc=r['description']
        img=r['image']
        
        iL={'plot':desc}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart': fanart}
        url=build_url({'mode':'itemList','categ':'film_groups','iid':cid,'page':'1'})
        addItemList(url, title, setArt, 'video', iL)
    
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'contList','categ':'film_groups','sort':s,'filters':f,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)

    xbmcplugin.endOfDirectory(addon_handle)
    
def cast(s,f,p): #Browser Lev.1 
    url=apiURL+'browse/cast_members'
    URLparams={}
    if p!=None:
        URLparams.update({'page':p})
    if f!=None:
        filters=eval(f)
        for ff in list(filters.keys()):
            URLparams[ff]=filters[ff]
    
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['cast_members']:
        name=r['name']
        pid=str(r['id'])
        role=r['primary_type']
        img=r['image_url']
        slug=r['slug']
        
        iL={'plot':role}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart': fanart}
        url=build_url({'mode':'itemList','categ':'cast_members','pid':pid,'slug':slug})
        addItemList(url, name, setArt, 'video', iL)
    
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'contList','categ':'cast_members','sort':s,'filters':f,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)    
    
    xbmcplugin.endOfDirectory(addon_handle)

def lists(s,f,p): #Browser Lev.1 
    URLparams={
        'sort':s,
    }
    if p!=None:
        URLparams.update({'page':p})
    url=apiURL+'browse/lists'
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['lists']:
        title=r['title']
        slug=r['slug']
        desc=r['description']
        fans=str(r['fan_count'])
        films=str(r['film_count'])
        img=r['thumbnails'][0]['src']
        plot='[B]Films: [/B]%s\n[B]Followers: [/B]%s\n[I]%s[/I]'%(films,fans,desc)
        
        iL={'plot':plot}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart': fanart}
        url=build_url({'mode':'itemList','categ':'lists','slug':slug,'page':'1'})
        addItemList(url, title, setArt, 'video', iL)
    
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'contList','categ':'lists','sort':s,'filters':f,'page':str(resp['meta']['next_page'])})
        addItemList(url,nextPageLabel, setArt)

    xbmcplugin.endOfDirectory(addon_handle)

def events(s,f,p): #Browser Lev.1 
    URLparams={
        'sort':s,
    }
    if p!=None:
        URLparams.update({'page':p})
    if f!=None:
        filters=eval(f)
        for ff in list(filters.keys()):
            URLparams[ff]=filters[ff]
    url=apiURL+'browse/industry_events'
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['industry_events']:
        name=r['name']
        slug=r['slug']
        eid=str(r['id'])
        img=r['white_logo_url'] if r['white_logo_url']!=None else 'https://assets.mubicdn.net/website/industry_event_logo_placeholder-small_black.png'
        
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart': fanart}
        url=build_url({'mode':'itemList','categ':'industry_events','slug':slug,'eid':eid})
        addItemList(url, name, setArt)
    
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'contList','categ':'industry_events','sort':s,'filters':f,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)

    xbmcplugin.endOfDirectory(addon_handle)


def itemListColl(c,iid,p): #Browser Lev.2 - Coll [lista filmów]
    URLparams={
        'include_upcoming':'true',
        'page':p,
        'per_page':'24'
    }
    url=apiURL+c+'/'+iid+'/'+'film_group_items'
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['film_group_items']:
        if 'film' in r:
            rr=r['film']
            addFilmToList(rr)
        else:
            continue #??? czy będą jakieś inne elementy
    
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'itemList','categ':c,'iid':iid,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)
    
def roleListCast(c,pid,slug): #Browser Lev.2 - Cast  
    url=apiURL+'cast_members/'+slug
    resp=requests.get(url,headers=heaGen()).json()
    img=resp['image_url']
    name=resp['name']
    for r in resp['credits']:
        role=r['credit']
        rid=r['type']
        plot=name
        
        iL={'plot':plot}
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart': fanart}
        url=build_url({'mode':'itemListCastFilms','pid':pid,'role':rid,'page':'1'})
        addItemList(url, role, setArt, 'video', iL)
        
    xbmcplugin.endOfDirectory(addon_handle)
        
def itemListCastFilms(pid,r,p): #Browser Lev.3 - Cast [lista filmów]
    URLparams={
        'page':p,
        'per_page':'12',
        'cast_member_credit':r,
    }
    url=apiURL+'cast_members/'+pid+'/films'
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['films']:
        addFilmToList(r)
        
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'itemListCastFilms','pid':pid,'role':r,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)
    
def itemListLists(slug,p): #Browser Lev.2 - Listy [lista filmów]
    URLparams={
        'page':p,
        'per_page':'48',
    }
    url=apiURL+'lists/'+slug+'/list_films'
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['list_films']:
        if 'film' in r: 
            rr=r['film']
            addFilmToList(rr)
        else:
            continue
        
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'itemList','categ':'lists','slug':slug,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)
    
def itemListEvents(slug,eid): #Browser Lev.2 - Events filtry
    initEv=addon.getSetting('initEv')
    if initEv=='true':
        fy={}
        url=apiURL+'industry_events/'+slug+'/years'
        resp=requests.get(url,headers=heaGen()).json()
        for r in resp:
            fy[str(r)]=str(r)
        fs={'1':translate(30017),'0':translate(30018),'6':translate(30019)}
        #domyślne
        filtersEvents={
            'year':list(fy.keys())[0],
            'status':''
        }
        
        filters={'year':translate(30020),'status':translate(30021)}
        filtersEventsData={'year':fy,'status':fs}
        for ff in list(filters.keys()):
            setArt={'icon': 'DefaultTags.png'}
            url = build_url({'mode':'eventsFilter','slug':slug,'eid':eid,'filte':ff})
            filterVal=filtersEventsData[ff][filtersEvents[ff]] if filtersEvents[ff]!='' else 'all'
            addItemList(url, '%s %s: [B]%s[/B]'%(translate(30010),filters[ff],filterVal), setArt, isF=False)
    
    else:
        filtersEventsData=eval(addon.getSetting('filtersEventsData'))
        filtersEvents=eval(addon.getSetting('filtersEvents'))
        for ff in list(filtersEvents.keys()):
            setArt={'icon': 'DefaultTags.png'}
            url = build_url({'mode':'eventsFilter','slug':slug,'eid':eid,'filte':ff})
            filterVal=filtersEventsData[ff][filtersEvents[ff]] if filtersEvents[ff]!='' else 'all'
            addItemList(url, '%s %s: [B]%s[/B]'%(translate(30010),ff,filterVal), setArt, isF=False)
    
    addon.setSetting('filtersEvents',str(filtersEvents))
    addon.setSetting('filtersEventsData',str(filtersEventsData))
    
    setArt={'icon': 'DefaultAddonVideo.png'}
    url = build_url({'mode':'itemListEventsFilms','eid':eid,'filters':filtersEvents,'page':'1'})
    addItemList(url, '>>>', setArt)
    
    xbmcplugin.endOfDirectory(addon_handle)


def eventsFilter(slug,eid,ft):
    filtersEvents=eval(addon.getSetting('filtersEvents'))
    filtersEventsData=eval(addon.getSetting('filtersEventsData'))
    
    labels=[filtersEventsData[ft][k] for k in list(filtersEventsData[ft].keys())]
    select = xbmcgui.Dialog().select(translate(30101), labels)
    if select > -1:
        ftVal=list(filtersEventsData[ft].keys())[select]
    else:
        ftVal=filtersEvents[ft]

    filtersEvents[ft]=ftVal

    addon.setSetting('initEv','false')
    addon.setSetting('filtersEvents',str(filtersEvents))
    xbmc.executebuiltin('Container.Refresh')
    
def itemListEventsFilms(eid,f,p): #Browser Lev.3 - Listy [lista filmów]
    URLparams={
        
    }
    if f!=None:
        filters=eval(f)
        for ff in list(filters.keys()):
            if filters[ff]!='':
                URLparams[ff]=filters[ff]
    
    if p!=None:
        URLparams.update({'page':p})
    url=apiURL+'industry_events/'+eid+'/films'
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    for r in resp['films']:
        addFilmToList(r)
        
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'itemListEventsFilms','eid':eid,'filters':f,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)
        
    
    xbmcplugin.setContent(addon_handle, 'videos')
    xbmcplugin.endOfDirectory(addon_handle)

def searchResults(query):
    groups={'films':translate(30005),'cast_members':translate(30007)}
    for r in list(groups.keys()):    
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': 'DefaultAddonsSearch.png', 'fanart': fanart}
        url=build_url({'mode':'searchList','type':r,'query':query,'page':'1'})
        addItemList(url, groups[r], setArt)
    
    xbmcplugin.endOfDirectory(addon_handle)
    
def searchList(type,query,p):
    url=apiURL+'search/'+type
    URLparams={
        'query':quote(query),
        'page':p,
        'per_page':'24',
    }
    isPlayable=addon.getSetting('playable')
    if isPlayable=='true':
         URLparams.update({'playable':'true'})
    resp=requests.get(url,headers=heaGen(),params=URLparams).json()
    if type=='films':
        for r in resp['films']:
            addFilmToList(r)
        xbmcplugin.setContent(addon_handle, 'videos')
    elif type=='cast_members':
        for r in resp['cast_members']:
            name=r['name']
            pid=str(r['id'])
            credits=[c['credit'] for c in r['credits']]
            role=', '.join(credits)
            img=r['image_url']
            slug=r['slug']
            
            iL={'plot':role}
            setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img, 'fanart': fanart}
            url=build_url({'mode':'itemList','categ':'cast_members','pid':pid,'slug':slug})
            addItemList(url, name, setArt, 'video', iL)
    
    if resp['meta']['next_page']!=None:
        setArt={'thumb': '', 'poster': '', 'banner': '', 'icon': img_empty, 'fanart': fanart}
        url=build_url({'mode':'searchList','type':type,'query':query,'page':str(resp['meta']['next_page'])})
        addItemList(url, nextPageLabel, setArt)
        
    xbmcplugin.endOfDirectory(addon_handle)
    
    
def playMubi(vid):
    url=apiURL+'films/'+vid+'/viewing?parental_lock_enabled=true'
    data={}
    resp=requests.post(url,headers=heaGen(),json=data).json()
    
    url=apiURL+'prerolls/viewings'
    data={
        'viewing_film_id':int(vid)
    }
    resp=requests.post(url,headers=heaGen(),json=data)
    
    url='https://api.mubi.com/v3/films/'+vid+'/viewing/secure_url'
    resp=requests.get(url,headers=heaGen()).json()
      
    if 'url' in resp:
        stream_url=resp['url']
        token=addon.getSetting('token')
        userID=addon.getSetting('userID')
        dcd='{"userId":'+str(userID)+',"sessionId":"'+token+'","merchant":"mubi"}'
        dcd_enc=base64.b64encode(dcd.encode()).decode()
        heaLic={
            'User-Agent':UA,    
            'dt-custom-data':dcd_enc,
            'Referer':'https://mubi.com/',
            'Origin':'https://mubi.com',
            'Content-Type':''
        }
        licURL='https://lic.drmtoday.com/license-proxy-widevine/cenc/'
        #K21
        lickey='%s|%s|R{SSM}|JBlicense'%(licURL,urlencode(heaLic))
        #K22
        drm_config={
            "com.widevine.alpha": {
                "license": {
                    "server_url": licURL,
                    "req_headers": urlencode(heaLic),
                    "unwrapper":"json,base64",
                    "unwrapper_params": {"path_data": "license"},
                }
            }
        }
        
        ISAplayer('mpd',stream_url, True, lickey, drm_config)
    else:
        message=resp['user_message'] if 'user_message' in resp else ''
        xbmcgui.Dialog().notification('MUBI', '%s: %s'%(translate(30103),message), xbmcgui.NOTIFICATION_INFO)
        xbmcplugin.setResolvedUrl(addon_handle, False, xbmcgui.ListItem())
        

def trailer(u):
    if '.mp4' in u:
        directPlayer(u)
    else:
        xbmcgui.Dialog().notification('MUBI', translate(30104), xbmcgui.NOTIFICATION_INFO)
        
def lang(v):
    url=apiURL+'films/'+v+'/playback_languages'
    try:
        resp=requests.get(url,headers=heaGen()).json()
        plot='[B]%s: [/B]%s\n'%(translate(30022),', '.join(resp['audio_options']))
        plot+='[B]%s: [/B]%s\n'%(translate(30023),', '.join(resp['subtitle_options']))
        plot+='[B]%s: [/B]%s\n'%(translate(30024),', '.join(resp['media_features']))
    except:
        plot=translate(30025)
    
    dialog = xbmcgui.Dialog()
    dialog.textviewer(translate(30102), plot)
    
def getCliCountry():
    if addon.getSetting('client_country')=='':
        hea={
            'User-Agent':UA
        }
        url='https://mubi.com/'
        resp=requests.get(url,headers=hea).text
        country=re.compile('\"Client-Country\":\"([^"]+?)\"').findall(resp)
        cli_country=country[0] if len(country)>0 else 'PL'
        addon.setSetting('client_country',cli_country)
    
def logIn():
    def getCode():
        url=apiURL+'link_code'
        resp=requests.get(url,headers=heaATVGen()).json()
        return resp

    #client-country
    getCliCountry()
    
    code=getCode()
    if 'auth_token' in code and 'link_code' in code:
        ok=xbmcgui.Dialog().ok(translate(30105), translate(30106)%('[COLOR=yellow][B]'+code['link_code']+'[/B][/COLOR]'))
        if ok:
            urlAuth=apiURL+'authenticate'
            data={'auth_token':code['auth_token']}
            respAuth=requests.post(urlAuth,headers=heaATVGen(),json=data).json()
            if 'token' in respAuth:
                addon.setSetting('token',respAuth['token'])
                addon.setSetting('userID',str(respAuth['user']['id']))
                addon.setSetting('logged','true')
            else:
                xbmcgui.Dialog().notification('MUBI', '%s: %s'%(translate(30103),respAuth['message']), xbmcgui.NOTIFICATION_INFO)
    
    else:    
        xbmcgui.Dialog().notification('MUBI', translate(30107), xbmcgui.NOTIFICATION_INFO)

 
def logOut():
    url=apiURL+'sessions'
    hea=heaATVGen()
    hea.update({'authorization':'Bearer '+addon.getSetting('token')})
    resp=requests.delete(url,headers=hea)

    if resp.status_code==200:
        addon.setSetting('token','')
        addon.setSetting('userID','')
        addon.setSetting('logged','false')
        addon.setSetting('client_country','')
    else:
        xbmcgui.Dialog().notification('MUBI', translate(30108), xbmcgui.NOTIFICATION_INFO)      
    
mode = params.get('mode', None)

if not mode:
    if addon.getSetting('deviceID')=='' or addon.getSetting('deviceID')==None:#
        addon.setSetting('deviceID',"%s-%s-%s-%s-%s" %(code_gen(8),code_gen(4),code_gen(4),code_gen(4),code_gen(12)))
    main_menu()
       
else:
    if mode=='browserList':
        addon.setSetting('init','true')
        browserList()
    
    if mode=='browsStngs':
        categ=params.get('categ')
        browsStngs(categ)
        
    if mode=='browsSort':
        c=params.get('categ')
        browsSort(c)
    
    if mode=='browsFilter':
        c=params.get('categ')
        ft=params.get('filte')
        browsFilter(c,ft)
    
    if mode=='contList':
        c=params.get('categ')
        s=params.get('sort')
        f=params.get('filters')
        p=params.get('page')
        if c=='films':
            films(s,f,p)
        elif c=='film_groups':
            collections(s,f,p)
        elif c=='cast_members':
            cast(s,f,p)
        elif c=='lists':
            lists(s,f,p)
        elif c=='industry_events':
            addon.setSetting('initEv','true')
            events(s,f,p)
    
    if mode=='itemList':
        categ=params.get('categ')
        if categ=='film_groups':
            iid=params.get('iid')
            page=params.get('page')
            itemListColl(categ,iid,page)
        if categ=='cast_members':
            pid=params.get('pid')
            slug=params.get('slug')
            roleListCast(categ,pid,slug)
        if categ=='lists':
            slug=params.get('slug')
            page=params.get('page')
            itemListLists(slug,page)
        if categ=='industry_events':
            slug=params.get('slug')
            eid=params.get('eid')            
            itemListEvents(slug,eid)
     
    if mode=='itemListCastFilms':
        pid=params.get('pid')
        role=params.get('role')
        page=params.get('page')
        
        itemListCastFilms(pid,role,page)
    
    if mode=='itemListEventsFilms':
        eid=params.get('eid')
        filters=params.get('filters')
        page=params.get('page')
        itemListEventsFilms(eid,filters,page)
    
    if mode=='eventsFilter':
        slug=params.get('slug')
        eid=params.get('eid')
        filte=params.get('filte')
        eventsFilter(slug,eid,filte)
    
    if mode=='search':   
        query = xbmcgui.Dialog().input('%s:'%(translate(30109)), type=xbmcgui.INPUT_ALPHANUM)
        if query:
            searchResults(query)


    if mode=='searchList':
        type=params.get('type')
        query=params.get('query')
        page=params.get('page')
        searchList(type,query,page)
    
    
    if mode=='films':
        page=params.get('page')
        films(page)
                
    if mode=='playMubi':
        vid=params.get('vid')
        playMubi(vid)
        
    if mode=='noPlay':
        pass
    
    if mode=='trailer':
        u=params.get('url')
        trailer(u)
        
    if mode=='lang':
        vid=params.get('vid')
        lang(vid)
    
    if mode=='seasList':
        sid=params.get('sid')
        seasList(sid)
    
    if mode=='epList':
        sid=params.get('sid')
        seas_id=params.get('seas_id')
        page=params.get('page')
        epList(sid,seas_id,page)
    
    if mode=='logIn':
        logIn()        
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Update(plugin://plugin.video.mubi/,replace)')
            
    if mode=='logOut':
        logOut()
        xbmcplugin.endOfDirectory(addon_handle, cacheToDisc=False)
        xbmc.executebuiltin('Container.Update(plugin://plugin.video.mubi/,replace)')
    