import json
import subprocess
import tempfile
import requests
from rhasspyhermes_app import TopicData
from app import HOST,app,_LOGGER
from config import SECRET_RASA_URL, WHISPER_APP_PATH, WHISPER_MODEL_PATH

recorder = None
listening = ""

chunk_size = 960
sample_rate = 16000
sample_width = 2
channels = 1

@app.on_topic("hermes/nlu/query")
async def handle_query(data: TopicData, payload:bytes):
    newdata = json.loads(payload)

    # intercept query request from sat2
    # TODO: variable site id
    if(newdata["siteId"] == "sat2"):
        if newdata["asrConfidence"] == 1:
            # let rhasspy handle intent recognition immediately
            # use api to get intent
            handle_intent_rasa(newdata["input"],newdata["sessionId"],"sat2")

        # _LOGGER.info("sat2")
        # handle_intent_rhasspy(newdata["input"],newdata["sessionId"],"sat2")

        else:
            # use whisper transcription
            global listening
            listening = newdata["sessionId"]

def handle_intent_rhasspy(input, sessionId, siteId):
    url = "http://"+HOST+":12101/api/text-to-intent"
    response = json.loads(requests.post(url ,input).text)
    # _LOGGER.info(response)
    # make intent json
    output = {"input": response["raw_text"],
              "intent":
                  {
                      "intentName": response["intent"]["name"],
                      "confidenceScore": 1.0
                  },
              "siteId": siteId,
              "slots": response["entities"],
              "sessionId": sessionId,
              "customData":"rhasspy-whisper"}


    # publish intent
    if response["intent"]["name"] != "":
        app.mqtt_client.publish("hermes/nlu/intentParsed", json.dumps(output))
        app.mqtt_client.publish("hermes/intent/"+response["intent"]["name"], json.dumps(output))
        app.mqtt_client.publish("piet/request", response["raw_text"].capitalize())

def handle_intent_rasa(input, sessionId, siteId):
    url = SECRET_RASA_URL + "/model/parse"
    if not isinstance(input, str):
        input = input.decode('ascii')
    response = requests.post(url ,json.dumps({"text":input}))

    # _LOGGER.info(response.text)
    response = json.loads(response.text)
    # make intent json
    output = {"input": response["text"],
              "intent":
                  {
                      "intentName": response["intent"]["name"],
                      "confidenceScore": 1.0
                  },
              "siteId": siteId,
              "slots": parse_rasa_slots(response["entities"]),
              "sessionId": sessionId,
              "customData":"rasa-whisper"}

    # _LOGGER.info(json.dumps(output))
    # publish intent
    if response["intent"]["name"] != "":
        app.mqtt_client.publish("hermes/nlu/intentParsed", json.dumps(output))
        app.mqtt_client.publish("hermes/intent/"+response["intent"]["name"], json.dumps(output))
        app.mqtt_client.publish("piet/request", response["text"].capitalize())

def parse_rasa_slots(slots):
    output = []
    for slot in slots:
        output.append({
            "entity": slot["entity"].lower(),
            "value": {"kind": "Unknown", "value": slot["value"]},
            "slotName": slot["entity"].lower(),
            "rawValue": slot["value"],
            "confidence": 1.0,
            "range": {
                "start": slot["start"],
                "end": slot["end"],
                "rawStart": slot["start"],
                "rawEnd": slot["end"]
                }
        })
    return output

@app.on_topic("rhasspy/asr/{siteId}/{sessionId}/audioCaptured")
async def capture_topic(data: TopicData, payload:bytes):
    _LOGGER.info("AudioCaptured " + data.data.get("sessionId"))
    with tempfile.NamedTemporaryFile(suffix=".wav", mode="wb") as wav_file:
        wav_file.write(payload)
        wav_file.seek(0)
        _LOGGER.info(wav_file.name)
        subprocess.call([WHISPER_APP_PATH, wav_file.name, "-m", WHISPER_MODEL_PATH, "-otxt"])
        f = open(wav_file.name + ".txt","r")
        text = f.read()
        if text:
            _LOGGER.info(text)
            app.mqtt_client.publish("hermes/asr/textCaptured", json.dumps({"text": text.strip(), "likelihood": 1.0, "seconds": 0.0, "sessionId": data.data.get("sessionId"), "customData":"whisper"}))
            app.mqtt_client.publish("whisper/transcription/" + data.data.get("sessionId"), text.strip())


@app.on_topic("whisper/transcription/{sessionId}")
async def whisper_transcription(data: TopicData, payload:bytes):
    _LOGGER.info("whisper topic")
    global listening
    if listening == data.data.get("sessionId"):
        handle_intent_rasa(payload, data.data.get("sessionId"),"piet")
        listening = ""