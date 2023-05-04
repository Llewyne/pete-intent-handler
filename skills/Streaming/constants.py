
from config import SECRET_RAPIDAPI_KEY, SECRET_ANGOLIA_API_KEY, SECRET_ANGOLIA_APP_ID

CACHE_FILE = "streaming_cache.json"

RESULT_CODE_LIMIT = "LIMIT_REACHED"
RESULT_CODE_UNAVAILABLE = "UNAVAILABLE"
RESULT_CODE_AVAILABLE = "AVAILABLE"

DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

RAPIDAPI_KEY = SECRET_RAPIDAPI_KEY

# Unogs constants
UNOGS_RESET_FILE = "skills/unogs_reset.txt"
UNOGS_DAILY_LIMIT = 100
UNOGS_TITLE_URL = "https://unogs-unogs-v1.p.rapidapi.com/search/titles"
UNOGS_TITLE_COUNTRIES_URL = "https://unogs-unogs-v1.p.rapidapi.com/title/countries"
UNOGS_HEADERS = {
	"X-RapidAPI-Key": RAPIDAPI_KEY,
	"X-RapidAPI-Host": "unogs-unogs-v1.p.rapidapi.com"
}
UNOGS_COUNTRY_ID_NL = "67"
UNOGS_COUNTRY_CODE_NL = "NL"
UNOGS_CHEAP_MODE = False # If True, will use only one request per check

#Streaming availability constants
SA_TITLE_URL = "https://streaming-availability.p.rapidapi.com/v2/search/title"
SA_HEADERS = {
	"X-RapidAPI-Key": RAPIDAPI_KEY,
	"X-RapidAPI-Host": "streaming-availability.p.rapidapi.com"
}
SA_COUNTRY_CODE_NL = "nl"

#Videoland constants
VIDEOLAND_SEARCH_API_URL = "https://nhacvivxxk-dsn.algolia.net/1/indexes/*/queries"
VIDEOLAND_HEADERS = {
	"x-algolia-api-key": SECRET_ANGOLIA_API_KEY,
	"x-algolia-application-id": SECRET_ANGOLIA_APP_ID
}
#Skyshowtime constants
SKYSHOWTIME_API_URL = "https://suggest.disco.skyshowtime.com/suggest/v1/stb/home/0/0/0?term="
SKYSHOWTIME_HEADERS = {
    "X-SkyOTT-ActiveTerritory": "NL",
    "X-SkyOTT-Device": "COMPUTER",
    "X-SkyOTT-Platform": "PC",
    "X-SkyOTT-Proposition": "SKYSHOWTIME"
}

#Viaplay constants
VIAPLAY_URL = "https://content.viaplay.com/pcdash-nl/search?query="
VIAPLAY_HEADERS = {
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"
}

#NPO constants
NPO_SEARCH_URL = "https://www.npostart.nl/search?query="
NPO_HEADERS = {
    "x-requested-with":"XMLHttpRequest"
}
