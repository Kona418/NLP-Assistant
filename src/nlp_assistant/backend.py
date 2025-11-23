import os
import time
from dotenv import load_dotenv

from src.nlp_assistant.helper import HomeAssistantRestManager
from src.nlp_assistant.pipelineParts.IntentRecognizer import IntentRecognizer
from src.nlp_assistant.pipelineParts.HomeAssistantController import HomeAssistantController
from src.nlp_assistant.pipelineParts.deviceMatcher import DeviceMatcher

# Deine Imports (angepasst, falls nötig)

class AssistantEngine:
    def __init__(self):
        """
        Initialisiert alle schweren Komponenten einmalig.
        """
        print("--- Initializing Assistant Engine ---")
        load_dotenv()
        
        # Token und URL sicher laden
        token = os.getenv("HA_TOKEN")
        if not token:
            raise ValueError("HA_TOKEN nicht in .env gefunden!")

        self.ha_manager = HomeAssistantRestManager(
            ha_bearer_token=token, 
            ha_base_url="http://homeassistant.local:8123"
        )
        self.ha_controller = HomeAssistantController(ha_manager=self.ha_manager)
        
        # Modell laden (das dauert am längsten, daher im init)
        self.intent_recognizer = IntentRecognizer()
        self.intent_recognizer.load_model()
        
        self.device_matcher = DeviceMatcher()
        
        # Geräteliste cachen
        self.device_list = self.ha_controller.get_device_list()
        print("--- Initialization Complete ---")

    def process_command(self, user_input: str) -> dict:
        """
        Verarbeitet einen einzelnen Befehl.
        """
        start_time = time.time()
        result_log = {}

        # 1. Intent erkennen
        intent = self.intent_recognizer.predict(user_input)[0]
        result_log["intent"] = intent

        # 2. Gerätenamen finden
        raw_device_name = self.device_matcher.extractDeviceNamesFromCommands(user_input)
        device_match = self.device_matcher.findBestDeviceMatch(
            targetDeviceName=raw_device_name, 
            deviceList=self.device_list
        )
        
        if not device_match:
            return {"status": "error", "message": "Kein passendes Gerät gefunden."}

        result_log["device"] = device_match["name"]

        # 3. Aktion ausführen
        # HINWEIS: Syntaxfehler in f-strings korrigiert (Single quotes innen, Double außen)
        action_input = {
            "domain": f"{device_match['type']}", 
            "service": f"{intent}",
            "name": f"{device_match['name']}"
        }
        
        response = self.ha_controller.post_action(action_input)
        result_log["execution_time"] = time.time() - start_time
        result_log["ha_response"] = response
        result_log["status"] = "success"
        
        return result_log