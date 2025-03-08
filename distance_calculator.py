from typing import Protocol

from geolocation import Geolocation

from geopy import distance
from enum import Enum


class DistanceUnit(Enum):
    KM = 1
    METERS = 1000
    MILES = 0.621371

    def __str__(self):
        return self.name.lower()


class Distance:
    """
    Represents the distance between two points it can be compared to other distances
    """

    def __init__(self, value: float, unit: DistanceUnit):
        self.value = value
        self.unit = unit

    @property
    def value_in_meter(self) -> float:
        return self.convert_value(DistanceUnit.METERS)

    def __eq__(self, other):
        return self.value_in_meter == other.value_in_meter

    def __lt__(self, other):
        return self.value_in_meter < other.value_in_meter

    def __str__(self):
        return f'{self.value:.2f} {self.unit}'

    def __repr__(self):
        return str(self)

    def to_json(self):
        return {
            'value': self.value,
            'unit': self.unit
        }

    def convert_value(self, unit: DistanceUnit) -> float:
        return self.value * self.unit.value / unit.value

    @classmethod
    def convert(cls, distance: 'Distance', unit: DistanceUnit) -> 'Distance':
        if distance.unit == unit:
            return distance
        return Distance(distance.convert_value(unit), unit)


class DistanceCalc(Protocol):
    def distance(self, x: Geolocation, y: Geolocation) -> Distance:
        """
        Calculate the distance between two points as long as the return value is a distance
        """


class HaversineDistanceCalc(DistanceCalc):
    """
    Calculate the geographical distance between two points using the haversine formula
    """

    def distance(self, x: Geolocation, y: Geolocation) -> Distance:
        return Distance(distance.distance(x, y).kilometers,DistanceUnit.KM)
