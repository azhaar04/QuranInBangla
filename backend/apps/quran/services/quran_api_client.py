import time

import requests
from django.conf import settings

OAUTH_TOKEN_URL = 'https://oauth2.quran.foundation/oauth2/token'
API_BASE_URL = 'https://apis.quran.foundation/content/api/v4'


class QuranAPIClient:
    """Client for the Quran Foundation content API (OAuth2 client_credentials)."""

    def __init__(self):
        self._token = None
        self._token_expires_at = 0

    def _get_token(self):
        if self._token and time.time() < self._token_expires_at:
            return self._token

        response = requests.post(
            OAUTH_TOKEN_URL,
            data={'grant_type': 'client_credentials', 'scope': 'content'},
            auth=(settings.QURAN_API_CLIENT_ID, settings.QURAN_API_CLIENT_SECRET),
            timeout=15,
        )
        response.raise_for_status()
        data = response.json()
        self._token = data['access_token']
        # Refresh a minute early so we never send a request with a token
        # that expires mid-flight.
        self._token_expires_at = time.time() + data['expires_in'] - 60
        return self._token

    def _headers(self):
        token = self._get_token()
        return {
            'Authorization': f'Bearer {token}',
            'x-auth-token': token,
            'x-client-id': settings.QURAN_API_CLIENT_ID,
        }

    def _get(self, path, params=None):
        response = requests.get(
            f'{API_BASE_URL}{path}', headers=self._headers(), params=params, timeout=30
        )
        response.raise_for_status()
        return response.json()

    def get_chapters(self, language='bn'):
        """Return all 114 chapters, with translated_name in the given language."""
        return self._get('/chapters', params={'language': language})['chapters']

    def get_verses_by_chapter(self, chapter_number, with_words=False):
        """Return every verse of a chapter (per_page=300 covers even Al-Baqarah)."""
        params = {'per_page': 300, 'fields': 'text_uthmani'}
        if with_words:
            params['words'] = 'true'
            params['word_fields'] = 'text_uthmani'
        return self._get(f'/verses/by_chapter/{chapter_number}', params=params)['verses']
