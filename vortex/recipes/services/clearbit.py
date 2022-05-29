import requests
from django.conf import settings

class ClearbitClient:
    base_url = 'https://person.clearbit.com/v2/combined/find'

    def __init__(self, *args, **kwargs):
        assert settings.CLEARBIT_API_KEY, 'ClearbitClient called without CLEARBIT_API_KEY set.'

    def get_headers(self):
        return {'Authorization': f'Bearer {settings.CLEARBIT_API_KEY}'}

    def form_url(self, email: str):
        return f'{self.base_url}?email={email}'

    def get_person_info(self, email: str):
        res = requests.get(self.form_url(email), headers=self.get_headers())
        if res.ok:
            return res.json()
        return None
