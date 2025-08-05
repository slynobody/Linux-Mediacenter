APP_VERSION = '4.11.0-rc2-2025.07.10.0'
CLIENT_VERSION = '10.1.0'
SDK_VERSION = '6.0'
EXPLORE_VERSION = 'v1.10'
CLIENT_ID = 'disney-svod-3d9324fc'

API_KEY = 'ZGlzbmV5JmFuZHJvaWQmMS4wLjA.bkeb0m230uUhv8qrAXuNu39tbE_mD5EEhM_NAcohjyA'
CONFIG_URL = 'https://bam-sdk-configs.bamgrid.com/bam-sdk/v{}/{}/android/v{}/google/tv/prod.json'.format(SDK_VERSION, CLIENT_ID, CLIENT_VERSION)
DEVICE_CODE_URL = 'https://www.disneyplus.com/begin'

BAM_PARTNER = 'disney'
BRANDS_ID = '552e2219-3eba-4bbd-94df-e99fca24553a'
CONTINUE_WATCHING_ID = '76aed686-1837-49bd-b4f5-5d2a27c0c8d4'
SUGGESTED_ID = '3cd8f37d-5480-46fb-9eeb-5002123abe53'
EXTRAS_ID = '83f33e19-3e08-490d-a59a-6ef5cb93f030'

EPISODES = 'EPISODES'
SUGGESTED = 'SUGGESTED'
EXTRAS = 'EXTRAS'
DETAILS = 'DETAILS'
BROWSE = 'BROWSE'
PLAYBACK = 'PLAYBACK'
TRAILER = 'TRAILER'
MODIFYSAVES = 'MODIFYSAVES'
REMOVECONTINUEWATCHING = 'REMOVECONTINUEWATCHING'
MODAL = 'MODAL'
CONTAINERS = 'CONTAINERS'
ACTIONS = 'ACTIONS'

HEADERS = {
    'User-Agent': 'BAMSDK/v{} ({} {}; v{}/v{}; android; tv)'.format(CLIENT_VERSION, CLIENT_ID, APP_VERSION, SDK_VERSION, CLIENT_VERSION),
    'x-application-version': 'google',
    'x-bamsdk-platform-id': 'android-tv',
    'x-bamsdk-client-id': CLIENT_ID,
    'x-bamsdk-platform': 'android/google/tv',
    'x-bamsdk-version': CLIENT_VERSION,
    'Accept-Encoding': 'gzip',
    'x-bamsdk-platform': 'android/google/tv',
}
