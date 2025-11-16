import requests
import json

api_url: str = "http://homeassistant.local:8123/api/services"

headers: dict = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2M2Q5ZjIyN2NkNzE0MWJlYTA2NGI5Y2NiMzk1MDE2OSIsImlhdCI6MTc2MzMxOTA5NiwiZXhwIjoyMDc4Njc5MDk2fQ.QiaWVCcqCv1Au-67-eCm1UIzndyMuef3SQx7KXrwENc",
    "content-type": "application/json",
}

response: requests.Response = requests.get(api_url, headers=headers)

response_data: list = response.json()

my_domain_list: list = []

i: int = 0
supported_domains: list = ["switch", "light"]

all_domains: list = []

# for item in response_data:
#     all_domains.append(item.get("domain"))
# print(all_domains)
# ['persistent_notification', 'homeassistant', 'logger', 'system_log', 'frontend', 'recorder', 'hassio', 'ffmpeg', 'switch', 'update', 'backup', 'conversation', 'tts', 'cloud', 'camera', 'scene', 'script', 'zone', 'logbook', 'input_boolean', 'input_select', 'automation', 'timer', 'input_number', 'group', 'light', 'input_button', 'person', 'file', 'schedule', 'shopping_list', 'input_datetime', 'cast', 'counter', 'input_text', 'notify', 'device_tracker', 'fan', 'number', 'todo', 'alarm_control_panel', 'button', 'climate', 'cover', 'humidifier', 'select', 'siren', 'vacuum', 'valve', 'weather', 'media_player', 'image', 'remote']


# services -> 

# item: dict
# for item in response_data:
#     if(item.get("domain")) in supported_domains:
#         print(f"~~~~~ {item.get("domain")} ~~~~~")
#         current_services: dict = item.get("services")
#         current_service:dict
#         services_item: dict = item.get("services")
#         for current_service in current_services:
#             current_service_entry:dict = services_item.get(current_service)
#             for item in current_service_entry:
#                 print("~~~~~~~~~~")
#                 print(item)

print(response_data)

root_item: dict
for root_item in response_data:
    domain_item: dict = root_item.get("domain")
    if domain_item in supported_domains:
        service_group_item: dict = root_item.get("services")
        service_item: dict
        for service_item in service_group_item.values():
            ...
            # print(service_item)