
import datetime
import json
import os

import requests
from rhasspyhermes.nlu import NluIntent
from rhasspyhermes_app import EndSession
from lxml import etree
from app import app, _LOGGER
from skills.Streaming.constants import *
from skills.models import Skill, SkillResult

class StreamingSkill(Skill):

    def __init__ (self, app):
        super().__init__(app, NluIntent("PietPlayOnChromecast"))

    def can_handle(self, user_input):
        return user_input.startswith("play")
    
    def perform(self, intent):
        title = intent.slots["title"]

        results = any_availability_by_title(title)
        if(not any([results["services"][x]["available"] == RESULT_CODE_AVAILABLE for x in results["services"]])):
            return SkillResult(False, "Not available")
        
        first_available = next((results["services"][x] for x in results["services"] if results["services"][x]["available"] == RESULT_CODE_AVAILABLE),None)
        
        return SkillResult(True, "Started on " + first_available["name"], {"title":results["title"], "watch_url":first_available["watch_url"]})

# @app.on_intent("PietPlayOnChromecast")
# async def handle_intent(intent: NluIntent):
#     if intent.site_id != "sat2":
#         return
    
#     # Get title
#     title = intent.slots["title"]

#     _LOGGER.info(title)

#     results = any_availability_by_title(title)
#     if(not any([results["services"][x]["available"] == RESULT_CODE_AVAILABLE for x in results["services"]])):
#         app.mqtt_client.publish("piet/streaming/unavailable", title)
#         return EndSession("Not available")
    
#     first_available = next((results["services"][x] for x in results["services"] if results["services"][x]["available"] == RESULT_CODE_AVAILABLE),None)
    
#     app.mqtt_client.publish("piet/streaming/" + first_available["name"], json.dumps({"title":results["title"], "watch_url":first_available["watch_url"]}))
#     return EndSession("Started on " + first_available["name"])

def get_watch_url(title:str):
    result = any_availability_by_title(title)

    if result != RESULT_CODE_UNAVAILABLE:
        return result["watch_url"]

def any_availability_by_title(title:str):
    #check cache
    cache_results = get_cache(title)
    if cache_results != None:
        return cache_results
    
    #first check unlimited apis/no api neccesary
    results = {}
    results["videoland"] = videoland_availability_by_title(title)
    results["skyshowtime"] = skyshowtime_availability_by_title(title)
    results["viaplay"] = viaplay_availability_by_title(title)
    results["npo"] = npo_availability_by_title(title)

    if(not any([results[x]["result"] == RESULT_CODE_AVAILABLE for x in results])):
        #Check apis with limits
        results["netflix"] = netflix_availability_by_title(title)
        results["hbo"] = hbo_availability_by_title(title)

    title = next((results[x]["title"] for x in results if "title" in results[x]), None)
    
    new_result = {
        "title":title,
        "expiration_date": str(datetime.datetime.today() + datetime.timedelta(days=1))
    }

    new_result["services"] = [{"name":x,"available":results[x]["result"]} for x in results if not "watch_url" in results[x]]
    new_result["services"] = [{"name":x,"available":results[x]["result"],"watch_url":results[x]["watch_url"]} for x in results if "watch_url" in results[x]]
    save_cache(new_result)

    return new_result

def get_cache(title:str):
    #open cache file
    curpath = os.path.abspath(os.curdir)
    if not os.path.exists(os.path.join(curpath,CACHE_FILE)):
        init_cache()
        return None
    
    f = open(os.path.join(curpath,CACHE_FILE),"r")

    cache = json.loads(f.read())

    cache_results = next((cache[x] for x in cache if cache[x]["title"].lower() == title.lower()), None)
    f.close()
    if cache_results == None:
        return None
    if datetime.datetime.strptime(cache_results["expiration_date"], '%Y-%m-%d %H:%M:%S.%f') < datetime.datetime.today():
        return None
    
    return cache_results

def save_cache(data):
     #open cache file
    curpath = os.path.abspath(os.curdir)
    if not os.path.exists(os.path.join(curpath,CACHE_FILE)):
        init_cache()
    
    f = open(os.path.join(curpath,CACHE_FILE),"r")

    cache = json.loads(f.read())
    f.close()
    f = open(os.path.join(curpath,CACHE_FILE),"w")

    cache[data["title"]] = data

    f.write(json.dumps(cache))
    f.close()

def init_cache():
    print("init")
    curpath = os.path.abspath(os.curdir)
    if not os.path.exists(os.path.join(curpath,CACHE_FILE)):
        contents = []
        f = open(os.path.join(curpath,CACHE_FILE),"w")
        f.write(json.dumps(contents))
        f.close()

def netflix_availability_by_title(title:str, region_id:str = UNOGS_COUNTRY_ID_NL, region_code:str = UNOGS_COUNTRY_CODE_NL):
    """Check if a title is available on netflix"""
    if unogs_limit_reached():
        return {"result":RESULT_CODE_LIMIT}
    
    if UNOGS_CHEAP_MODE:
        querystring = {"order_by":"rating","title":title,"country_list":region_id}
        response = requests.request("GET", UNOGS_TITLE_URL, headers=UNOGS_HEADERS, params=querystring)
        requests_remaining = response.headers["X-RateLimit-requests-Remaining"]
        requests_reset = response.headers["X-RateLimit-requests-Reset"]
        unogs_update_request_reset(requests_remaining, requests_reset)

        # Get title
        results = json.loads(response.text)
        title_results = next((x for x in results["results"] if x["title"].lower() == title.lower()), None)
        if title_results == None:
            return {"result": RESULT_CODE_UNAVAILABLE}
        return {"result": RESULT_CODE_AVAILABLE, "data_titles":title_results}
    else:
        querystring1 = {"order_by":"rating","title":title}
        response1 = requests.request("GET", UNOGS_TITLE_URL, headers=UNOGS_HEADERS, params=querystring1)

        requests_remaining1 = response1.headers["X-RateLimit-requests-Remaining"]
        requests_reset1 = response1.headers["X-RateLimit-requests-Reset"]
        unogs_update_request_reset(requests_remaining1, requests_reset1)

        # Find neflix id number
        results1 = json.loads(response1.text)
        title_results = next((x for x in results1["results"] if x["title"].lower() == title.lower()), None)
        if title_results == None:
            return {"result": RESULT_CODE_UNAVAILABLE}
        netflix_id = title_results["netflix_id"]

        # Get countries
        querystring = {"netflix_id":netflix_id}
        response = requests.request("GET", UNOGS_TITLE_COUNTRIES_URL, headers=UNOGS_HEADERS, params=querystring)

        requests_remaining = response.headers["X-RateLimit-requests-Remaining"]
        requests_reset = response.headers["X-RateLimit-requests-Reset"]
        unogs_update_request_reset(requests_remaining, requests_reset)

        # Find country information
        results = json.loads(response.text)

        
        country_results = next((x for x in results["results"] if x["country_code"] == region_code), None)
        if country_results == None:
            return {"result": RESULT_CODE_UNAVAILABLE}
        return {"result": RESULT_CODE_AVAILABLE, "name":"netflix", "title":netflix_full_title(title_results), "watch_url": netflix_watch_url(title_results), "data_titles":title_results, "data_countries":country_results}

def netflix_full_title(data):
    return data["title"]

def netflix_watch_url(data):
    return "https://www.netflix.com/watch/" + data["data_titles"]["netflix_id"]
    
def hbo_availability_by_title(title:str, region_code:str = SA_COUNTRY_CODE_NL):
    querystring = {"title":title,"country":region_code,"show_type":"all","output_language":"en"}
    response = requests.request("GET", SA_TITLE_URL, headers=SA_HEADERS, params=querystring)
    # print(response.text)

    curpath = os.path.abspath(os.curdir)
    f = open(os.path.join(curpath,"hbo.json"),"w")
    f.write(response.text)
    # Get title
    results = json.loads(response.text)
    title_results = next((x for x in results["result"] if x["title"].lower() == title.lower()), None)
    if title_results["streamingInfo"] == {}:
        return {"result": RESULT_CODE_UNAVAILABLE}
    if not "hbo" in title_results["streamingInfo"][region_code]:
        return {"result": RESULT_CODE_UNAVAILABLE}
    return {"result": RESULT_CODE_AVAILABLE, "name":"hbo", "watch_url": hbo_watch_url(title_results, region_code), "title": hbo_full_title(title_results), "data_titles":title_results}

def hbo_full_title(data):
    return data["title"]

def hbo_watch_url(data, region_code:str = SA_COUNTRY_CODE_NL):
    return data["streamingInfo"][region_code]["hbo"][0]["watchLink"]

def skyshowtime_availability_by_title(title:str):
    response = requests.request("GET", SKYSHOWTIME_API_URL+title, headers=SKYSHOWTIME_HEADERS)
    # Get title
    results = json.loads(response.text)
    title_results = next((x for x in results["results"] if x["t"].lower() == title.lower()), None)
    if title_results == None:
        return {"result": RESULT_CODE_UNAVAILABLE}
    return {"result": RESULT_CODE_AVAILABLE, "name":"skyshowtime", "title": skyshowtime_full_title(title_results), "watch_url": skyshowtime_watch_url(title_results), "data_titles":title_results}

def skyshowtime_full_title(data):
    data["t"]

def skyshowtime_watch_url(data):
    type = "movies"
    if data["uuidtype"] == "series":
        type = "tv"
    return "https://skyshowtime.com/watch/asset/" + type + "/" + data["t"].lower() + "/" + data["uuid"]

def viaplay_availability_by_title(title:str):
    response = requests.request("GET", VIAPLAY_URL+title, headers=VIAPLAY_HEADERS)
    # Get title
    results = json.loads(response.text)
    title_results = next((x for x in results["_embedded"]["viaplay:blocks"][0]["_embedded"]["viaplay:products"] if x["_links"]["self"]["title"].lower() == title.lower()), None)

    if title_results == None:
        return {"result": RESULT_CODE_UNAVAILABLE}
    return {"result": RESULT_CODE_AVAILABLE, "name":"viaplay", "data_titles":title_results}

#TODO
def viaplay_full_title(data):
    pass

def viaplay_watch_url(data):
    """Get viaplay watch url by title"""
    return data["_links"]["viaplay:page"]["href"]


def videoland_availability_by_title(title:str):
    response = requests.request("POST", VIDEOLAND_SEARCH_API_URL, headers=VIDEOLAND_HEADERS,data=json.dumps(videoland_make_query(title)))

    # Get title
    results = json.loads(response.text)
    title_results = next((x for x in results["results"][0]["hits"] if x["item"]["itemContent"]["title"].lower() == title.lower()), None)
    if title_results == None:
        return {"result": RESULT_CODE_UNAVAILABLE}
    return {"result": RESULT_CODE_AVAILABLE, "name":"videoland", "data_titles":title_results}

#TODO
def videoland_full_title(data):
    pass

#TODO
def videoland_watch_url(data):
    pass

def npo_availability_by_title(title:str):
    response = requests.request("GET", NPO_SEARCH_URL + title, headers=NPO_HEADERS)

    html = response.text
    tree = etree.HTML(html)
    items = tree.xpath("//div/ul/li[a/@class='npo-tile-link']")
    results = []
    for i in items:
        item_code = str(i.xpath("a/@data-ts-destination")[0])
        item_title = str(i.xpath("a/@title")[0])
        item_link = str(i.xpath("a/@href")[0])
        results.append({"code":item_code,"title":item_title,"link":item_link})

    title_results = next((x for x in results if x["title"].lower() == title.lower()), None)
    if title_results == None:
        return {"result": RESULT_CODE_UNAVAILABLE}
    return {"result": RESULT_CODE_AVAILABLE, "name":"npo", "data_titles":title_results, "title":title_results["title"], "watch_url":title_results["link"]}

def videoland_make_query(title:str):
    query = {
        "requests": [
            {
                "indexName": "videoland_prod_bedrock_layout_items_v2_rtlnl_main",
                "query": title,
                "params": "hitsPerPage=50&clickAnalytics=true&facetFilters=%5B%5B%22metadata.item_type%3Aprogram%22%5D%2C%5B%22metadata.platforms_assets%3Am6group_web%22%5D%5D"
            }
        ]
    }
    return query

def unogs_limit_reached():
    """Check if unogs API usage limit has been reached today"""
    curpath = os.path.abspath(os.curdir)
    f = open(os.path.join(curpath,UNOGS_RESET_FILE),"r")
    contents = f.read()
    try:
        reset_datetime = datetime.datetime.strptime(contents,DATE_FORMAT)
        return reset_datetime < datetime.datetime.now()
    except ValueError as err:
           return False

def unogs_update_request_reset(remaining: str, seconds: str):
    """Update reset date in file"""
    curpath = os.path.abspath(os.curdir)

    if(int(remaining) <= 0):
        reset = datetime.datetime.now() + datetime.timedelta(0,int(seconds))
        f = open(os.path.join(curpath,UNOGS_RESET_FILE),"w")
        f.write(datetime.datetime.strftime(reset,DATE_FORMAT))