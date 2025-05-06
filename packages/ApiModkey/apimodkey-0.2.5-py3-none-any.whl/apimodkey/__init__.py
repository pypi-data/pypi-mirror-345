import requests

class ModKey:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = 'https://modkey.space/api/v1/action'

    def _request(self, method: str, **kwargs):
        data = {'method': method, 'api_key': self.api_key}
        data.update(kwargs)

        try:
            response = requests.post(self.base_url, data=data)
            return response.json()
        except requests.RequestException as e:
            return {"status": False, "error": str(e)}

    def create_key(self, days: int, devices: int, key_type: str):
        return self._request(
            'create-key',
            days=days,
            devices=devices,
            type=key_type
        )

    def edit_key_max_devices(self, key: str, new_max_devices: int):
        return self._request(
            'edit-key-max-devices',
            key=key,
            new_max_devices=new_max_devices
        )

    def edit_user_key(self, key: str, new_key: str):
        return self._request(
            'edit-user-key',
            key=key,
            new_user_key=new_key
        )

    def info_key(self, key: str):
        return self._request(
            'get-key-info',
            key=key
        )

    def edit_key_status(self, key: str, new_status: str):
        return self._request(
            'edit-key-status',
            key=key,
            type=new_status
        )

    def info_api(self):
        return self._request('get-me')