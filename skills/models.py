from rhasspyhermes.nlu import NluIntent
import json
from dataclasses import dataclass

from app import _LOGGER

@dataclass
class SkillResult:
    """
    Class to store the result of a skill
    """
    success: bool
    message: str = None
    data: dict = None

class Skill:
    """
    Base class for all virtual assistant skills
    """

    def __init__(self, app, intent: str):
        self.intent = intent
        self.app = app
        # Create decorator for intent
        self.intent_decorator = app.on_intent(intent)(self.handle)
        pass
    
    def can_handle(self, user_input):
        """
        Returns a boolean indicating if the skill can handle the user input
        """
        raise NotImplementedError
    
    async def handle(self, intent: NluIntent):
        """
        Handles the user input and returns a response
        """
        _LOGGER.debug("Handling intent " + self.intent)
        if not self.can_handle(intent.input):
            response = self.generate_cant_handle_response()
        else:
            result = self.perform(intent)
            self.app.mqtt_client.publish("piet/" + self.intent + "/result", json.dumps(result.__dict__))
            if result.success:
                response = self.generate_success_response(result)
            else:
                response = self.generate_failure_response(result)
        
        # publish result and response to MQTT
        self.app.mqtt_client.publish("piet/" + self.intent + "/response", json.dumps(response.__dict__))
        return response
    
    def perform(self, intent):
        """
        Performs the skill
        """
        raise NotImplementedError
    
    def generate_success_response(self):
        """
        Generates a success response
        """
        raise NotImplementedError
    
    def generate_cant_handle_response(self):
        """
        Generates a response when the skill can't handle the user input
        """
        raise NotImplementedError
    
    def generate_failure_response(self):
        """
        Generates a failure response
        """
        raise NotImplementedError