import os

from dotenv import load_dotenv

from src.nlp_assistant.helper import HomeAssistantRestManager
<<<<<<< HEAD
from src.nlp_assistant.pipelineParts.TempIntentRecognizer import IntentRecognizer
=======
>>>>>>> 321f866efd8cb27667925a007715781ca836cca2
from src.nlp_assistant.pipelineParts.HomeAssistantController import HomeAssistantController


def main():
    load_dotenv()
    ha_manager: HomeAssistantRestManager = HomeAssistantRestManager(ha_bearer_token=os.getenv("HA_TOKEN"), ha_base_url="http://homeassistant.local:8123")
    ha_controller: HomeAssistantController = HomeAssistantController(ha_manager=ha_manager)
<<<<<<< HEAD

    intent_recognizer: IntentRecognizer = IntentRecognizer()

    print(intent_recognizer.predict("Ich aktiviere das Licht in der Küche sofort"))
=======
    print("Hello World")
>>>>>>> 321f866efd8cb27667925a007715781ca836cca2

if __name__ == '__main__':
    main()
