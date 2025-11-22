from src.nlp_assistant.helper import HomeAssistantRestManager

class HomeAssistantController:

    ha_manager: HomeAssistantRestManager
    device_list: list

    def __init__(self, ha_manager: HomeAssistantRestManager):
        self.ha_manager = ha_manager
        self.device_list = ha_manager.get_device_list()
        pass

    def post_action (self, action: dict) -> dict | None:
        return self.ha_manager.post_action(action_data=action, device_list=self.device_list)

    def get_device_list (self) -> list:
        return self.ha_manager.get_device_list()
