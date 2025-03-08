from enum import Enum

from geolocation import Geolocation
from urllib.parse import quote
BASE = 'https://www.openstreetmap.org/directions?engine=fossgis_osrm_{}&route='

class Vehicle(Enum):
    BICYCLE = 'bicycle'
    CAR = 'car'
    FOOT = 'foot'



def get_routing_link(x: Geolocation,y: Geolocation, vehicle: Vehicle) -> str:
    decoded_route = quote(f"{x};{y}")
    return BASE.format(vehicle.value) + decoded_route
