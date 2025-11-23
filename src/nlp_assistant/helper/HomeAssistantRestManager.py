import json

import requests

class HomeAssistantRestManager():
    supported_devices: list = ["light", "switch"]

    ha_base_url: str
    headers: dict

    def __init__(self, ha_base_url: str, ha_bearer_token: str):
        self.ha_base_url = ha_base_url
        self.headers = {
            "Authorization": f"Bearer {ha_bearer_token}",
            "content-type": "application/json",
        }

    def post_action(self, action_data: dict, device_list: list) -> dict | None:
        try:
            domain: str = action_data.pop("domain")
            service: str = action_data.pop("service")
        except KeyError:
            print("Action_data muss 'domain' und 'service' enthalten")
            return None

        payload: dict = action_data

        target_name: str | None = payload.pop("name", None)
        target_id: str | None = payload.get("entity_id", None)

        if target_name and not target_id:
            found_id: str | None = None
            for device in device_list:
                if device.get("name") == target_name:
                    found_id = device.get("entity_id")

            if found_id:
                payload["entity_id"] = found_id
                print(f"Name '{target_name}' aufgelöst zu ID '{found_id}'")
            else:
                print(f"Kein Gerät mit Namen '{target_name}' in der Geräteliste gefunden")
                return None

        elif not target_id:
            print("Action_data muss 'entity_id' oder 'name' enthalten")
            return None

        action_url: str = f"{self.ha_base_url}/api/services/{domain}/{service}"

        try:
            response: requests.Response = requests.post(action_url, headers=self.headers, json=payload)
            response.raise_for_status()

            print(f"Aktion '{domain}.{service}' auf '{payload.get('entity_id')}' erfolgreich ausgeführt")
            return response.json()

        except requests.exceptions.HTTPError as e:
            print(f"HTTP Fehler beim Aufruf von {action_url}: {e}")
        except requests.exceptions.RequestException as e:
            print(f"Fehler bei der Anfrage: {e}")

        return None

    def get_device_list(self) -> list:
        services_response: requests.Response = requests.get(f"{self.ha_base_url}/api/services", headers=self.headers)
        services_data: list = services_response.json()

        states_response: requests.Response = requests.get(f"{self.ha_base_url}/api/states", headers=self.headers)
        states_data: list = states_response.json()

        service_map: dict = {}
        for domain_item in services_data:
            domain_name: str = domain_item.get("domain")
            if domain_name in self.supported_devices:
                service_map[domain_name] = list(domain_item.get("services"))


        final_device_list: list = []
        for entity in states_data:

            entity_id: str = entity.get("entity_id")
            domain: str = entity_id.split('.')[0]

            if domain in self.supported_devices:
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
        # print(json.dumps(obj=final_device_list, indent=4))
        return final_device_list
