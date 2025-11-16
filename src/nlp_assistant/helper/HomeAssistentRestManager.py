import requests
import json


ha_base_url: str = "http://homeassistant.local:8123"


headers: dict = {
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiI2M2Q5ZjIyN2NkNzE0MWJlYTA2NGI5Y2NiMzk1MDE2OSIsImlhdCI6MTc2MzMxOTA5NiwiZXhwIjoyMDc4Njc5MDk2fQ.QiaWVCcqCv1Au-67-eCm1UIzndyMuef3SQx7KXrwENc",
    "content-type": "application/json",
}

services_response: requests.Response = requests.get(f"{ha_base_url}/api/services", headers=headers)
services_data: list = services_response.json()

states_response: requests.Response = requests.get(f"{ha_base_url}/api/states", headers=headers)
states_data: list = states_response.json()

supported_devices: list = ["light", "switch"]

service_map: dict = {}
for domain_item in services_data:
    domain_name: str = domain_item.get("domain")
    if domain_name in supported_devices:
        service_map[domain_name] = list(domain_item.get("services"))


final_device_list: list = []
for entity in states_data:

    entity_id: str = entity.get("entity_id")
    domain: str = entity_id.split('.')[0]

    if domain in supported_devices:
        attributes: dict = entity.get("attributes", {})

        device_dict: dict = {
            "name": attributes.get("friendly_name", entity_id),
            "entity_id": entity_id,
            "type": domain,
            "actions": service_map[domain],
            "capabilities": {}
        }

        if domain == "light":
            supported_modes: list = attributes.get("supported_color_modes", [])

            if any(mode in supported_modes for mode in ['brightness', 'color_temp', 'hs', 'xy', 'rgb', 'rgbw', 'rgbww']):
                device_dict["capabilities"]["can_set_brightness"] = True

                if 'color_temp' in supported_modes:
                    device_dict["capabilities"]["can_set_color_temp"] = True
                    device_dict["capabilities"]["min_temp_kelvin"] = attributes.get('min_color_temp_kelvin')
                    device_dict["capabilities"]["max_temp_kelvin"] = attributes.get('max_color_temp_kelvin')

                if any(mode in supported_modes for mode in ['hs', 'xy', 'rgb', 'rgbw', 'rgbww']):
                    device_dict["capabilities"]["can_set_color"] = True

        final_device_list.append(device_dict)

print(json.dumps(final_device_list, indent=2, ensure_ascii=False))