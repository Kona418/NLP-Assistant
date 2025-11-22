import os

from dotenv import load_dotenv

from src.nlp_assistant.helper import HomeAssistantRestManager
from src.nlp_assistant.pipelineParts.TempIntentRecognizer import IntentRecognizer
from src.nlp_assistant.pipelineParts.HomeAssistantController import HomeAssistantController


def main():
    load_dotenv()
    ha_manager: HomeAssistantRestManager = HomeAssistantRestManager(ha_bearer_token=os.getenv("HA_TOKEN"), ha_base_url="http://homeassistant.local:8123")
    ha_controller: HomeAssistantController = HomeAssistantController(ha_manager=ha_manager)

    intent_recognizer: IntentRecognizer = IntentRecognizer()

    print(intent_recognizer.predict("Ich aktiviere das Licht in der Küche sofort"))

if __name__ == '__main__':
    main()
