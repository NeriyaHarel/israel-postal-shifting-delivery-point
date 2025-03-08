import logging
from typing import Protocol
import requests
from .delivery_point import Address
from .exceptions import GeocoderError
from .location import Geolocation


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
    """
    A geocoder that uses the Nominatim API to search for geolocations
    Make sure to read the usage policy of the Nominatim API
    https://operations.osmfoundation.org/policies/nominatim/
    specifically the rate limiting:
     - No heavy uses (an absolute maximum of 1 request per second).
    """

    def __init__(self, base_url='https://nominatim.openstreetmap.org'):
        self.base_url = base_url
        self.session = requests.Session()
        # from the usage policy:
        # "Provide a valid HTTP Referer or User-Agent identifying the application
        # (stock User-Agents as set by http libraries will not do)."
        self.session.headers.update({'User-Agent': 'Python-Geocoder'})

    def make_request(self, method: str, url: str, raise_for_status: bool = True,
                     return_json: bool = True, **kwargs) -> requests.Response | dict:
        """
        Make a request using the session object and return the response
        Args:
            method: HTTP method to use (GET, POST, PUT, DELETE)
            url: The URL to make the request to
            raise_for_status: Raise an exception if the response is not ok
            return_json: Parse the response as JSON and return it,
                          if False return the response object
                          make sure you use it with raise_for_status=True
            **kwargs: Additional arguments to pass to the request method
        Returns:
            requests.Response | dict: The response object or the parsed JSON response
        """
        response = self.session.request(method, url, **kwargs)
        if raise_for_status:
            if not response.ok:
                logging.error(f'Error {response.status_code} - {response.text}')
            response.raise_for_status()
        if return_json:
            return response.json()
        return response

    def search_string(self, address: str) -> Geolocation:
        """
        Search for the geolocation of the given address using the Nominatim API
        Args:
            address: The address to search for
        Returns:
            Geolocation: The geolocation of the address

        """
        params = {'q': address, 'format': 'json', 'limit': 1}
        res = self.make_request("GET", self.base_url + '/search', params=params)
        if not res:
            raise GeocoderError(f'No results for address {address}')
        res = res[0]
        return Geolocation(res['lat'], res['lon'])

    def preprocess_street(self, address: Address) -> str:
        """
        Preprocess the address to be used in the search
        Args:
            address: The address to preprocess
        Returns:
            str: The preprocessed address
        """
        street = address.street
        if not street:
            return ''

        # some minor preprocessing to increase the chances of finding the address
        street = (
            street.removeprefix("שד' ")
                  .removeprefix("שד ")
                  .removeprefix("רח' ")
                  .removeprefix("רח ")
            .strip()
        )

        # add the house number if available
        if address.house:
            street += f' {address.house}'
        return street

    def search_structured(self, address: Address) -> Geolocation:
        """
        Search for the geolocation of the given address using the Nominatim API
        Args:
            address: The address to search for
        Returns:
            Geolocation: The geolocation of the address

        """
        params = {
            'city': address.city,
            'country': address.country,
            'format': 'json',
            'limit': 1
        }

        if address.street:
            params['street'] = self.preprocess_street(address)
        res = self.make_request("GET", self.base_url + '/search', params=params)
        if not res:
            raise GeocoderError(f'No results for address {address}')
        res = res[0]
        return Geolocation(res['lat'], res['lon'])