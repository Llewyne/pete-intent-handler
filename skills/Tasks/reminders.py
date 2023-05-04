import subprocess
from skills.models import Skill, SkillResult
from rhasspyhermes_app import EndSession
from rhasspyhermes.nlu import NluIntent

class ReminderSkill(Skill):

    def __init__(self, app):
        super().__init__(app, "PietRemindMe")

    def can_handle(self, user_input):
        return user_input.startswith("remind me")

    def perform(self, intent):
        text = intent.input.lower()
        if text.startswith("remind me"):
            text = (text.split("remind me"))[1]
        if text.startswith(" to"):
            text = (text.split(" to"))[1]
        text = text.capitalize()
        text = text.strip(".")
        if text != "":
            output = subprocess.check_output(["task", "add", "project:pietdata", "+reminder", text])
            return SkillResult(True)
        else:
            return SkillResult(False)

    def generate_cant_handle_response(self):
        return EndSession("No reminder set")

    def generate_failure_response(self):
        return EndSession("No reminder set")

    def generate_success_response(self):
        return EndSession("Reminder set")
    
# @app.on_intent("PietRemindMe")
# async def handle_intent(intent: NluIntent):
#     if intent.site_id != "sat2":
#         return
#     # Get reminder text
#     text = intent.input.lower()
#     if text.startswith("remind me"):
#         text = (text.split("remind me"))[1]
#     if text.startswith(" to"):
#         text = (text.split(" to"))[1]
#     text = text.capitalize()
#     text = text.strip(".")

#     # Create task
#     if text != "":
#         output = subprocess.check_output(["task", "add", "project:pietdata", "+reminder", text])