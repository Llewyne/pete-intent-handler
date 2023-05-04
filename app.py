from rhasspyhermes_app import HermesApp, TopicData, ContinueSession, EndSession
from config import SECRET_MQTT_HOST, SECRET_MQTT_PORT, SECRET_MQTT_USER, SECRET_MQTT_PASS
import logging

_LOGGER = logging.getLogger("Piet")

HOST = SECRET_MQTT_HOST
MQTT_PORT = SECRET_MQTT_PORT
MQTT_USER = SECRET_MQTT_USER
MQTT_PASS = SECRET_MQTT_PASS
app = HermesApp("Piet", host=HOST, port=MQTT_PORT, username=MQTT_USER, password=MQTT_PASS)