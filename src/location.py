from typing import NamedTuple


class Address(NamedTuple):
    city: str
    street: str
    house: int
    country: str = 'IL'


class Geolocation(NamedTuple):
    latitude: float
    longitude: float

    def __str__(self):
        return f'{self.latitude}, {self.longitude}'

    @classmethod
    def from_str(cls, s: str):
        latitude, longitude = s.split(',')
        return cls(float(latitude), float(longitude))
