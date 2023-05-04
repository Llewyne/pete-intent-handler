from app import app
import io
import json
import logging
import subprocess
import tempfile
import wave
import requests
import typing
# import paho.mqtt.client as mqtt
from rhasspyhermes.nlu import NluIntent, NluIntentNotRecognized
from rhasspyhermes_app import HermesApp, TopicData, ContinueSession, EndSession
from rhasspysilence import WebRtcVadRecorder, SilenceMethod
from skills.Tasks.reminders import *


from rhasspy import *
# from skills.Tasks.tasks import *
from skills.Streaming.streaming import *

# initiate skills
reminders = ReminderSkill(app)
app.run()