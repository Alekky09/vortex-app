import requests
from django.conf import settings


class HunterClient:
    base_url = 'https://api.hunter.io/v2/email-verifier'

    def __init__(self, *args, **kwargs):
        assert settings.HUNTER_API_KEY, 'HunterClient called without HUNTER_API_KEY set.'

    def form_url(self, email: str):
        return f'{self.base_url}?email={email}&api_key={settings.HUNTER_API_KEY}'

    def is_email_valid(self, email: str):
        res = requests.get(self.form_url(email))
        if res.ok:
            return res.json().get('data', {}).get('status') != 'invalid'
        return True
