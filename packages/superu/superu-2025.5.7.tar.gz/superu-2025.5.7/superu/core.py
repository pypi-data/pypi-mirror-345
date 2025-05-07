import plivo
import requests
import json

class CallWrapper:
    def __init__(self, real_calls):
        self._real = real_calls

    def create(self, from_, to_, answer_url, answer_method='GET', **kwargs):
        # Call the real method
        create_call = self._real.create(
            from_=from_,
            to_=to_,
            answer_url=answer_url,
            answer_method=answer_method,
            **kwargs
        )

        create_call['call_uuid'] = create_call['request_uuid']
        return create_call
    
    def analysis(self, call_uuid , vapi_private_key , custom_fields = None):
        if not custom_fields:
            response = requests.request("GET", f'https://shared-service.superu.ai/calls_analysis/{call_uuid}/{vapi_private_key}')
            return response.json()
        else:
            required_keys = {"field", "definition", "outputs_options"}
            for i, field in enumerate(custom_fields):
                if not isinstance(field, dict):
                    raise ValueError(f"custom_fields[{i}] is not a dictionary")
                
                missing_keys = required_keys - field.keys()
                if missing_keys:
                    raise ValueError(f"custom_fields[{i}] is missing keys: {missing_keys}")

                if not isinstance(field["field"], str):
                    raise ValueError(f"custom_fields[{i}]['field'] must be a string")
                if not isinstance(field["definition"], str):
                    raise ValueError(f"custom_fields[{i}]['definition'] must be a string")
                if not isinstance(field["outputs_options"], list) or not all(isinstance(opt, str) for opt in field["outputs_options"]):
                    raise ValueError(f"custom_fields[{i}]['outputs_options'] must be a list of strings")

            # All validations passed
            response = requests.request(
                "POST",
                f'https://shared-service.superu.ai/calls_analysis/{call_uuid}/{vapi_private_key}',
                json={"custom_fields": custom_fields}
            )
            return response.json()


    def __getattr__(self, name):
        # Delegate all other methods/attributes
        return getattr(self._real, name)

class AssistantWrapper:
    def __init__(self, vapi_private_key , vapi_public_key):
        self.base_url = "https://api.vapi.ai/assistant"
        self.vapi_private_key = vapi_private_key
        self.vapi_public_key = vapi_public_key

    def create(self, name, transcriber, model, voice):
        payload = {
            "name": name,
            "transcriber": transcriber,
            "model": model,
            "voice": voice
        }

        headers = {
            "Authorization": f"Bearer {self.vapi_private_key}",
            "Content-Type": "application/json"
        }

        response = requests.post(self.base_url, headers=headers, data=json.dumps(payload))
        if response.status_code != 200:
            raise Exception(f"Failed to create assistant: {response.status_code}, {response.text}")
        return response.json()


class SuperU:
    def __init__(self, api_key):
        api_keys = self.validate_api_key(api_key)['api_keys']
        self.plivo_auth_id = api_keys['plivo_auth_id']
        self.plivo_auth_token = api_keys['plivo_auth_token']
        self.vapi_public_key = api_keys['vapi_public_key']
        self.vapi_private_key = api_keys['vapi_private_key']


        self._client = plivo.RestClient(self.plivo_auth_id, self.plivo_auth_token)
        self.calls = CallWrapper(self._client.calls)
        self.assistants = AssistantWrapper(self.vapi_private_key, self.vapi_public_key)

    def validate_api_key(self, api_key):
        response = requests.post(
            'https://shared-service.superu.ai/api_key_check',
            headers={'Content-Type': 'application/json'},
            json={'api_key': api_key}
        )
        if response.status_code != 200:
            raise Exception(f"Invalid API key: {response.status_code}, {response.text}")
        return response.json()
    
    def __getattr__(self, name):
        return getattr(self._client, name)