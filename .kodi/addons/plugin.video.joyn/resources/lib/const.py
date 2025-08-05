# -*- coding: utf-8 -*-

CONST = {
    'BASE_URL': 'https://www.joyn.{}',
    'ENTITLEMENT_URL': 'entitlement-token',
    'IP_API_URL': 'http://ip-api.com/json/?fields=status,country,countryCode',
    'AUTH_URL': 'https://auth.joyn.de/auth',
    'AUTH_ANON': '/anonymous',
    'AUTH_REFRESH': '/refresh',
    'AUTH_LOGIN': '/login',
    'AUTH_LOGOUT': '/logout',
    'SSO_AUTH_URL': 'https://auth.joyn.de/sso/endpoints',
    'OAUTH_URL': 'https://www.joyn.{}/oauth',
    'CLIENT_NAMES': ['web', 'ios', 'android'],
    'EDGE_UA': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0',
    'JOYN_CLIENT_VERSION': '5.733.6',
    'MAX_VIDEO_TRIES': 5,
    'SIGNATURE_KEY': 'MzU0MzM3MzgzMzM4MzMzNjM1NDMzNzM4MzYzNDM2MzYzNTQzMz'\
                     'czODM2MzYzMzM4MzIzNjM1NDMzNzM4MzMzMDM2MzQzNTM5MzU0'\
                     'MzM3MzgzMzM5MzMzNTMyMzQzNTQzMzczODM2MzUzMzM5MzU0Mz'\
                     'M3MzgzMzM4MzMzMjMzNDYzNTQzMzczODM2MzYzMzMzMzM0NDMz'\
                     'NDIzNTQzMzczODMzMzgzNjM2MzMzNQ==',

    'PRELOAD_JS_CONFIGS': {
        'API_GW_API_KEY': r'API_GW_API_KEY.*?value:"(.*?)"',
    },
    'CHUNKS_JS_CONFIGS': {
        'PLAYERCONFIG_URL': 'https://playerconfig.*?.json',
    },
    'COUNTRIES': {
        'DE': {
            'language': 'de',
            'setting_id': '1',
        },
        'AT': {
            'language': 'at',
            'setting_id': '2',
        },
        'CH': {
            'language': 'ch',
            'setting_id': '3',
        },
    },
    'ENTITLEMENT_BASE_URL': 'https://entitlements-service-alb.prd.platform.s.joyn.de/api/user',
    'PLAYBACK_API_BASE_URL': 'https://api.vod-prd.s.joyn.de/v1',

    'CACHE_DIR': 'cache',
    'TEMP_DIR': 'tmp',
    'DATA_DIR': 'data',
    'CACHE': {
        'CONFIG': { 'key': 'config', 'expires': 432000 },
        'EPG': { 'key': 'epg', 'expires': 36000 },
        'ETAGS': { 'key': 'etags', 'expires': None},
        'ACCOUNT_INFO': { 'key': 'account_info', 'expires': 36000}
    },

    'ETAGS_TTL': 1209600,  # 14 days

    'LASTSEEN_ITEM_COUNT': 20,
    'UEPG_REFRESH_INTERVAL': 7200,
    'UEPG_ROWCOUNT': 5,
    'INPUTSTREAM_ADDON': 'inputstream.adaptive',

    'MSG_IDS': {
        'ADD_TO_WATCHLIST': 30651,
        'ADD_TO_WATCHLIST_PRX': 30653,
        'REMOVE_FROM_WATCHLIST': 30652,
        'REMOVE_FROM_WATCHLIST_PRFX': 30654,
        'MEDIA_LIBRARY': 30622,
        'CATEGORY': 30623,
        'TV_SHOW': 30624,
        'SEASON': 30625,
        'EPISODE': 30625,
        'WATCHLIST': 30601,
        'MEDIA_LIBRARIES': 30602,
        'CATEGORIES': 30603,
        'SEARCH': 30604,
        'LIVE_TV': 30605,
        'LIVE_TV_VOD': 30606,
        'MEDIA_LIBRARIES_PLOT': 30608,
        'CATEGORIES_PLOT': 30609,
        'WATCHLIST_PLOT': 30607,
        'SEARCH_PLOT': 30610,
        'LIVE_TV_PLOT': 30611,
        'WL_TYPE_ADDED': 30526,
        'WL_TYPE_REMOVED': 30527,
        'MSG_INPUSTREAM_NOT_ENABLED': 30501,
        'MSG_WIDEVINE_NOT_FOUND': 30502,
        'MSG_NO_SEARCH_RESULTS': 30525,
        'MSG_NO_FAVS_YET': 30528,
        'MSG_FAVS_UNAVAILABLE': 30529,
        'ERROR': 30521,
        'MSG_ERR_TRY_AGAIN': 30522,
        'MSG_ERROR_CONFIG_DECRYPTION': 30523,
        'MSG_ERROR_NO_VIDEOSTEAM': 30524,
        'LIVETV_TITLE': 30655,
        'LIVETV_UNTIL': 30656,
        'LIVETV_UNTIL_AND_NEXT': 30657,
        'MIN_AGE': 30658,
        'VIDEO_AVAILABLE': 30650,
        'SEASON_NO': 30621,
        'MSG_CONFIG_VALUES_INCOMPLETE': 30530,
        'MSG_NO_ACCESS_TO_URL': 30531,
        'MSG_COUNTRY_NOT_DETECTED': 30532,
        'MSG_COUNTRY_INVALID': 30533,
        'CANCEL': 30503,
        'OPEN_ADDON_SETTINGS': 30504,
        'CACHE_WAS_CLEARED': 30659,
        'CACHE_COULD_NOT_BE_CLEARED': 30660,
        'LANG_CODE': 30661,
        'MSG_VIDEO_UNAVAILABLE': 30662,
        'MSG_GAPHQL_ERROR': 30663,
        'MSG_NO_CONTENT': 30664,
        'CONTINUE_WATCHING': 30665,
        'RECOMMENDATION': 30666,
        'MOVIE': 30667,
        'SERIES': 30668,
        'TITLE_LABEL': 30669,
        'LOGGED_IN_LABEL': 30670,
        'LOGIN_FAILED_LABEL': 30671,
        'ACCOUNT_INFO_LABEL': 30672,
        'YES_LABEL': 30673,
        'NO_LABEL': 30674,
        'USERNAME_LABEL': 30675,
        'PASSWORD_LABEL': 30676,
        'MSG_INVALID_EMAIL': 30677,
        'LOGOUT_OK_LABEL': 30678,
        'NOT_LOGGED_IN_LABEL': 30679,
        'LOGOUT_NOK_LABEL': 30680,
        'RETRY': 30505,
        'ACCOUNT': 30352,
        'MSG_RERESH_AUTH_FAILED_RELOG': 30534,
        'MSG_RERESH_AUTH_FAILED': 30535,
        'CONTINUE_ANONYMOUS': 30506,
        'JOYN_BOOKMARKS': 30681,
        'JOYN_BOOKMARK_LABEL': 30682,
        'MSG_JOYN_BOOKMARK_ADD_SUCC': 30683,
        'MSG_JOYN_BOOKMARK_ADD_FAIL': 30684,
        'MSG_JOYN_BOOKMARK_DEL_SUCC': 30685,
        'MSG_JOYN_BOOKMARK_DEL_FAIL': 30686,
        'ADD_TO_JOYN_BOOKMARKS_LABEL': 30687,
        'DEL_FROM_JOYN_BOOKMARKS_LABEL': 30688,
        'MPAA_PIN': 30689,
        'MSG_INVALID_MPAA_PIN': 30690,
        'PLUS_HIGHLIGHT_LABEL': 30691,
        'MSG_INVALID_PASSWORD': 30692,
        'NO_INFORMATION_AVAILABLE': 30693,
        'LOGIN_NOW_LABEL': 30694,
        'LOGIN_LABEL': 30136,
        'ASCENDING_LABEL': 30695,
        'DESCENDING_LABEL': 30696,
        'TV_SHOWS': 30697,
        'TV_SHOWS_PLOT': 30698,
        'MOVIES': 30699,
        'MOVIES_PLOT': 30700,
        'SPORT': 30701,
        'SPORT_PLOT': 30702,
    },

    'VIEW_MODES': {
        'Standard': {
            'skin.estuary': '0',
        },
        'List': {
            'skin.estuary': '50',
        },
        'Poster': {
            'skin.estuary': '51',
        },
        'IconWall': {
            'skin.estuary': '52',
        },
        'Shift': {
            'skin.estuary': '53',
         },
        'InfoWall': {
            'skin.estuary': '54',
        },
        'WideList': {
            'skin.estuary': '55',
        },
        'Wall': {
            'skin.estuary': '500',
        },
        'Banner': {
            'skin.estuary': '501',
        },
        'Fanart': {
            'skin.estuary': '502',
        },
    },
    'LICENSE_FILTER': {
        'hasActivePlus': 'FREE',
    },
    'LICENSE_TYPES': {
        'FREE': {
            'AVOD': {
                'MARKING_TYPES': ['JOYN_ORIGINAL', 'HD', 'PREVIEW', 'WITH_ADS']
            },
            'FVOD': {
                'MARKING_TYPES': ['JOYN_ORIGINAL', 'HD', 'PREVIEW', 'WITH_ADS']
            }
        },
        'PAID': {
            'SVOD': {
                'SUBSCRIPTION_TYPE': 'hasActivePlus',
                'MARKING_TYPES': ['JOYN_ORIGINAL', 'HD', 'PREVIEW', 'PLUS', 'PREMIUM'],
            },
        },
    },
    'FOLDERS': {
        'INDEX': {
            'content_type': 'tags',
            'view_mode': 'categories_view',
        },
         'CATEORIES': {
            'content_type': 'tags',
            'view_mode': 'categories_view',
            'cacheable': True,
        },
        'MEDIA_LIBS': {
            'content_type': 'tags',
            'view_mode': 'categories_view',
            'cacheable': True,
        },
        'WATCHLIST': {
            'content_type': 'videos',
            'view_mode': 'watchlist_view',
        },
        'CATEGORY': {
            'content_type': 'tvshows',
            'view_mode': 'category_view',
            'cacheable': True,
        },
        'LIVE_TV': {
            'content_type': 'videos',
            'view_mode': 'livetv_view',
        },
        'LIVE_TV_VOD': {
            'content_type': 'videos',
            'view_mode': 'livetv_view',
        },
        'TV_SHOWS': {
            'content_type': 'tvshows',
            'view_mode': 'tvshow_view',
            'cacheable': True,
        },
        'SEASONS': {
            'content_type': 'seasons',
            'view_mode': 'season_view',
            'sort': {
               'order_type': '7',  # SortByTitle
               'setting_id': 'season_order',
            },
            'cacheable': True,
        },
        'EPISODES': {
            'content_type': 'episodes',
            'view_mode': 'episode_view',
            'sort': {
               'order_type': '23',  # SortByEpisodeNumber
               'setting_id': 'episode_order',
            },
            'cacheable': True,
        },
    },

    'SETTING_VALS': {
        'SORT_ORDER_DEFAULT': '0',
        'SORT_ORDER_ASC': '1',
        'SORT_ORDER_DESC': '2',
    },

    'GRAPHQL': {
        'API_URL': 'https://api.joyn.de/graphql',

        'REQUIRED_HEADERS': ['x-api-key', 'joyn-platform'],

        'STATIC_VARIABLES': {
            'first': 1000,
            'offset': 0,
        },

        'METADATA': {
            'TVCHANNEL': {
                'TEXTS': {'title': 'title'},
                'ART': {
                    'logo': {
                        'icon': 'profile:nextgen-web-artlogo-183x75',
                        'thumb': 'profile:original',
                        'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                    },
                    'brand': {
                        'logo': {
                            'icon': 'profile:nextgen-web-artlogo-183x75',
                            'thumb': 'profile:original',
                            'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                        },
                    },
                },
            },

            'TVSHOW': {
                'TEXTS': {'title': 'title', 'description': 'plot'},
                'ART': {
                    'primaryImage': {
                        'thumb': 'profile:original'
                    },
                    'artLogoImage': {
                        'icon': 'profile:nextgen-web-artlogo-183x75',
                        'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                        'clearart': 'profile:nextgen-web-artlogo-183x75',
                    },
                    'heroLandscapeImage': {
                        'thumb': 'profile:original',
                        'fanart': 'profile:nextgen-web-herolandscape-1920x',
                        'landscape': 'profile:nextgen-web-herolandscape-1920x',
                    },
                    'heroPortraitImage': {
                        'thumb': 'profile:original',
                        'poster': 'profile:nextgen-webphone-heroportrait-563x',
                    },
                },
            },

           'EPISODE': {
               'TEXTS': {'title': 'title', 'description': 'plot'},
               'ART': {
                    'primaryImage': {
                        'thumb': 'profile:original'
                    },
                    'artLogoImage': {
                        'icon': 'profile:nextgen-web-artlogo-183x75',
                        'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                    },
                    'heroLandscapeImage': {
                        'fanart': 'profile:nextgen-web-herolandscape-1920x',
                    },
                    'heroPortrait': {
                        'poster': 'profile:nextgen-webphone-heroportrait-563x',
                    },
                },
            },

            'EPG': {
                'TEXTS': {'title': 'title', 'secondaryTitle': 'plot'},
                'ART': {
                    'images': {
                        'LIVE_STILL': {
                            'poster': 'profile:original',
                            'thumb': 'profile:original',
                        },
                    },
                },
            },

            'TEASER': {
                'TEXTS': {'title': 'title'},
                'ART': {
                    'images': {
                        'icon': 'profile:nextgen-web-artlogo-183x75',
                        'thumb': 'profile:original',
                        'clearlogo': 'profile:nextgen-web-artlogo-183x75',
                    },
                },
            },
        },

        'NAVIGATION': {
            'OPERATION': 'Navigation',
            'HASH': '818622ff5afe143664241034ba0c537650ec9a2eeae4d568830b47d8de605b7e',
        },

        'LANDINGPAGECLIENT': {
            'OPERATION': 'LandingPageClient',
            'REQUIRED_VARIABLES': ['path'],
            'HASH': 'bcd4468a3b6851cc09321b37ce8866ccf892859780ca7cf03fd8841d5a0f49ed',
        },

       'LANDINGBLOCKS': {
            'OPERATION': 'LandingBlocks',
            'REQUIRED_VARIABLES': ['ids'],
            'BOOKMARKS': True,
            'HASH': 'bd421dd41dd88aa826bd7193de779960ad3fe7c75eef8047b13ba49072a56855',
        },

        'CHANNEL': {
            'OPERATION': 'PageDetailMediaLibrary',
            'REQUIRED_VARIABLES': ['path', 'first', 'offset'],
            'BOOKMARKS': True,
            'HASH': 'f61159391eed95487997fe2a9eab1fe25198e12b35f6206f60eb9f477187fab3',
        },

        'COLLECTION': {
            'OPERATION': 'PageCollectionsDetail',
            'REQUIRED_VARIABLES': ['path'],
            'BOOKMARKS': True,
            'HASH': 'f700a30ceee32ea9ad245002e4ed5bf236bf54455608592a3ee1ecef5fffbe0e',
        },

        'COMPILATION': {
            'OPERATION': 'CompilationDetailPageStatic',
            'REQUIRED_VARIABLES': ['path'],
            'BOOKMARKS': True,
            'HASH': '0672194d788614168fba6effad2cf3f3de8cd73d980efd8a41991a177ded4693',
        },

        'MOVIES': {
            'OPERATION': 'PageMovieDetailStatic',
            'REQUIRED_VARIABLES': ['path'],
            'BOOKMARKS': True,
            'HASH': '5cd6d962be007c782b5049ec7077dd446b334f14461423a72baf34df294d11b2',
        },

        'SEASONS': {
           'OPERATION': 'SeriesDetailPageStatic',
           'REQUIRED_VARIABLES': ['path', 'licenseFilter'],
           'BOOKMARKS': True,
           'HASH': '43cad327eeae12e14dfb629d662ebc947d78b71ec91d972ea1ef46ccdb29eede',
        },

        'EPISODES': {
            'OPERATION': 'Season',
            'REQUIRED_VARIABLES': ['id', 'licenseFilter', 'first', 'offset'],
            'BOOKMARKS': True,
            'HASH': 'ee2396bb1b7c9f800e5cefd0b341271b7213fceb4ebe18d5a30dab41d703009f',
        },

        'RECENT_EPISODES': {
            'OPERATION': 'RecentEpisodes',
            'REQUIRED_VARIABLES': ['id', 'offset'],
            'BOOKMARKS': True,
            'HASH': '165df4f031673746960ae3b36a86d3a6249257b26551dd1407fde75056689305',
        },

        'PLAYER_LIVESTREAMS': {
            'QUERY': '{ liveStreams(filterLivestreamsTypes: [EVENT,LINEAR,ON_DEMAND], first: 5000, offset: 0) { agofCode, brand { brandCode, id, livestream '\
                '{ logo { url(profile: "nextgen-web-artlogo-183x75") } } }, epgEvents { endDate, program { ... on CompilationItem { __typename, title, ageRating '\
                '{ descriptorsText, minAge }, licenseTypes, path, productPlacement, thumbnailImage: image(type: PRIMARY) { url(profile: "nextgen-web-episodestillplayer-693x390") }, '\
                'tracking { agofCode, externalAssetId, genres }, video { id }, compilation { artLogoImage: image(type: ART_LOGO) { url(profile: "nextgen-web-artlogo-300x123") }, brands '\
                '{ logo { url }, title }, features, heroLandscapeImage: image(type: HERO_LANDSCAPE) { vibrantColor: accentColor(type: DARK_VIBRANT) }, id, title }, posterImage: image(type: PRIMARY) '\
                '{ url(profile: "nextgen-web-primarycut-1920x1080") } } ... on EpgEntry { __typename, title, secondaryTitle, images { __typename, id, type, url } } ... on Extra { __typename, ageRating { descriptorsText, minAge }, '\
                'artLogoImage: image(type: ART_LOGO) { url(profile: "nextgen-web-artlogo-300x123") }, brands { logo { url(profile: "nextgen-web-artlogo-183x75") }, title }, id, '\
                'parent { ... on Compilation { __typename, id } ... on Episode { __typename, id, series { __typename, genres { __typename, name }, id, title } } ... on Movie '\
                '{ __typename, genres { __typename, name }, id, title } ... on Season { __typename, series { __typename, genres { __typename, name }, id, title } } ... on Series '\
                '{ __typename, genres { __typename, name }, id, title } ... on SportsCompetition { __typename, id } ... on SportsStage { __typename } ... on SportsMatch '\
                '{ __typename } }, path, posterImage: image(type: PRIMARY) { url(profile: "nextgen-web-primarycut-1920x1080") }, title, tracking { agofCode, externalAssetId, genres }, '\
                'vibrantColorImage: image(type: PRIMARY) { vibrantColor: accentColor(type: DARK_VIBRANT) }, video { id } } ... on Movie { __typename, title, ageRating '\
                '{ descriptorsText, minAge }, artLogoImage: image(type: ART_LOGO) { url(profile: "nextgen-web-artlogo-300x123") }, brands { logo { url(profile: "nextgen-web-artlogo-183x75") }, '\
                'title }, cast { name }, features, heroLandscapeImage: image(type: HERO_LANDSCAPE) { vibrantColor: accentColor(type: DARK_VIBRANT) }, id, licenseTypes, path, '\
                'posterImage: image(type: PRIMARY) { url(profile: "nextgen-web-primarycut-1920x1080") }, productPlacement, tracking { agofCode, externalAssetId, genres }, '\
                'video { id }, videoDescriptors { name } } ... on Episode { __typename, title, ageRating { descriptorsText, minAge }, brands { logo { url(profile: "nextgen-web-artlogo-183x75") }, '\
                'title }, cast { name }, description, id, licenseTypes, number, path, posterImage: image(type: PRIMARY) { url(profile: "nextgen-web-primarycut-1920x1080") }, productPlacement, '\
                'season { number }, series { artLogoImage: image(type: ART_LOGO) { url(profile: "nextgen-web-artlogo-210x86") }, brands { logo { url(profile: "nextgen-web-artlogo-183x75") }, title }, '\
                'features, heroLandscapeImage: image(type: HERO_LANDSCAPE) { vibrantColor: accentColor(type: DARK_VIBRANT) }, id, title }, thumbnailImage: image(type: PRIMARY) '\
                '{ url(profile: "nextgen-web-episodestillplayer-693x390") }, tracking { agofCode, externalAssetId, genres }, video { id }, videoDescriptors { name } } ... on SportsMatch '\
                '{ __typename, title, ageRating { descriptorsText, minAge }, artLogoImage: image(type: ART_LOGO) { url(profile: "nextgen-web-artlogo-300x123") }, brands '\
                '{ logo { url(profile: "nextgen-web-artlogo-183x75") }, title }, heroLandscapeImage: image(type: HERO_LANDSCAPE) { vibrantColor: accentColor(type: DARK_VIBRANT) }, id, '\
                'licenseTypes, path, posterImage: image(type: PRIMARY) { url(profile: "nextgen-web-primarycut-1920x1080") }, sportsStage { sportsCompetition { id, title } }, tracking '\
                '{ agofCode, externalAssetId, genres }, video { id } } }, startDate }, id, liveStreamGroups, markings, quality, title, type } }',
            'OPERATION': 'PlayerLivestreams',
            'HAS_EXTENSIONS': False,
            'NO_CACHE': True,
        },

        'SEARCH': {
            'OPERATION': 'SearchQ',
            'REQUIRED_VARIABLES': ['text', 'first', 'offset'],
            'NO_CACHE': True,
            'BOOKMARKS': True,
            'HASH': 'bb2bab6cbe17321d7eddd5006e7f40765faedd79790b193a59d83f4640694856',
        },

        'ACCOUNT': {
            'OPERATION': 'GetMeState',
            'NO_CACHE': True,
            'HASH': '18d7d43a02a35574c461f82932012fce225e98223e7f6ab7c9e79dbfe1aa99b4',
        },

        'LANEBOOKMARK': {
            'OPERATION': 'LaneBookmark',
            'REQUIRED_VARIABLES': ['blockId'],
            'BOOKMARKS': True,
            'HASH': '7a15f636106535ea73d0cf6dff0c868ff63d49b273cef76220842064d5fd7247',
        },

        'MEBOOKMARK': {
            'OPERATION': 'MeBookmark',
            'BOOKMARKS': True,
            'HASH': '5bd7bf0a7ec62faf7d76ad39712e647af69488b0d8e574db1f53c0d89b8b4d53',
        },

        'ADD_BOOKMARK': {
            'QUERY': '($assetId: ID!) {setBookmark(assetId:$assetId) { __typename}}',
            'OPERATION': 'setBookmarkMutation',
            'REQUIRED_VARIABLES': ['assetId'],
            'IS_MUTATION': True,
            'NO_CACHE': True,
        },

        'DEL_BOOKMARK': {
            'QUERY': '($assetId: ID!) { removeBookmark(assetId:$assetId) }',
            'OPERATION': 'removeBookmarkMutation',
            'REQUIRED_VARIABLES': ['assetId'],
            'IS_MUTATION': True,
            'NO_CACHE': True,
        },

        'RESUMELANE': {
            'OPERATION': 'ResumeLaneWithToken',
            'REQUIRED_VARIABLES': ['blockId'],
            'BOOKMARKS': True,
            'HASH': '8795acc1fe7e6183e5a81f51a7a38b07fad9f60d3018f0db70b4ba72a49aec0d',
        },

        'RESUMEPOSITIONS': {
            'OPERATION': 'ResumePositionsWithToken',
            'REQUIRED_VARIABLES': ['ids'],
            'BOOKMARKS': True,
            'HASH': '362a1247c64705097a83a48dc5fb99a29dd573fe276f0b2fb91e50c165752e0b',
        },

        'SET_RESUME_POSITION': {
            'QUERY': '($assetId: ID!, $position: Int!) { setResumePosition(assetId:$assetId, position:$position) { __typename '\
                'assetId position } }',
            'OPERATION': 'setResumeMutation',
            'IS_MUTATION': True,
            'NO_CACHE': True,
        },
    },

    'CATEGORY_LANES': ['StandardLane', 'CollectionLane', 'FeaturedLane', 'LiveLane'],
    'COLLECTION_LANES': ['StandardLane'],
    'COLLECTION_GRID': ['Grid'],
}
