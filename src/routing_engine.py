"""
Maybe in the future I will add routing calculation to the system,
 but for now, I will just add the routing link generator.
"""

from enum import Enum

from .location import Geolocation
from urllib.parse import quote

BASE = 'https://www.openstreetmap.org/directions?engine=fossgis_osrm_{}&route='


class Vehicle(Enum):
    BICYCLE = 'bicycle'
    CAR = 'car'
    FOOT = 'foot'


def get_routing_link(x: Geolocation, y: Geolocation, vehicle: Vehicle) -> str:
    decoded_route = quote(f"{x};{y}")
    return BASE.format(vehicle.value) + decoded_route
