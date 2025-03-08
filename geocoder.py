import logging
from dataclasses import dataclass
from typing import Protocol
import requests

from delivery_point import Address
from exceptions import GeocoderError
from geolocation import Geolocation


class Geocoder(Protocol):
    def search_string(self, address: str) -> Geolocation:
        """
        Search for the geolocation of the given address
        """

    def search_structured(self, address: Address) -> Geolocation:
        """
        Search for the geolocation of the given address
        """


class NominatimGeocoder(Geocoder):
    ENDPOINT_SEARCH = '/search'

    def __init__(self, base_url=' https://nominatim.openstreetmap.org'):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': 'Python-Geocoder'})

    def make_request(self,method:str, url: str, raise_for_status: bool = True,
                     return_json: bool = True, **kwargs) -> requests.Response | dict:
        response = self.session.request(method, url, **kwargs)
        if raise_for_status:
            if not response.ok:
                logging.error(f'Error {response.status_code} - {response.text}')
            response.raise_for_status()
        if return_json:
            return response.json()
        return response

    def search_string(self, address: str) -> Geolocation:
        params={'q': address, 'format': 'json', 'limit': 1}
        res = self.make_request("GET", self.base_url + self.ENDPOINT_SEARCH, params=params)
        if not res:
            raise GeocoderError(f'No results for address {address}')
        res = res[0]
        return Geolocation(res['lat'], res['lon'])

