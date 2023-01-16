"""The QGIS way of HTTP requests.

It is recommended to not just rely on Python's `requests` library or similar solutions. This may result in problems
with QGIS proxy and authentication settings - see the documentation. QgsBlockingNetworkRequest is one of the solutions
to these problems.
"""

import json
from qgis.core import QgsBlockingNetworkRequest

from PyQt5.QtCore import QUrl
from PyQt5.QtNetwork import QNetworkRequest

API_GEOCODE = '/v1/geocode/search'
API_REVERSE_GEOCODE = '/v1/geocode/reverse'


class QgsGeoapifyClient:
    def __init__(self, api_key: str):
        self._api_key = api_key
        self._headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}

    def geocode(self, text: str = None) -> dict:
        """Returns geocoding results as a dictionary.

        Arguments:
            text: free text search of a location.

        Returns:
            Structured, geocoded, and enriched address record.
        """
        request_url = (geoapify_endpoint_url(api=API_GEOCODE, api_key=self._api_key)
                       + f'&text={text}&format=geojson&limit=1')

        return self._qgis_get_request(url=request_url)['features'][0]

    def reverse_geocode(self, longitude: float, latitude: float) -> dict:
        """Returns reverse geocoding results as a dictionary.

        Arguments:
            latitude: float representing latitude.
            longitude: float representing longitude.

        Returns:
            Structured, reverse geocoded, and enriched address record.
        """
        request_url = (geoapify_endpoint_url(api=API_REVERSE_GEOCODE, api_key=self._api_key)
                       + f'&lat={latitude}&lon={longitude}&format=geojson')

        return self._qgis_get_request(url=request_url)['features'][0]

    @staticmethod
    def _qgis_get_request(url: str) -> dict:
        request = QgsBlockingNetworkRequest()
        code = request.get(QNetworkRequest(QUrl(url)))

        if code == QgsBlockingNetworkRequest.NoError:
            response = request.reply()
            return json.loads(response.content().data())
        else:
            print(code)
            return {}


def geoapify_endpoint_url(api: str, api_key: str) -> str:
    return f'https://api.geoapify.com{api}?apiKey={api_key}'
