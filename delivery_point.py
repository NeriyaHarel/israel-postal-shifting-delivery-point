from dataclasses import dataclass
from typing import NamedTuple

from geolocation import Geolocation

GENERIC_STREET = ('רחוב ראשי', 'ראשי', 'חדר דואר', 'לב הישוב')


class Address(NamedTuple):
    city: str
    street: str
    house: int
    country: str = 'IL'

@dataclass
class DeliveryPoint:
    address: Address
    description: str
    branch_name: str
    geolocation: Geolocation = None

    @property
    def city(self):
        return self.address.city

    @property
    def street(self):
        return self.address.street

    @property
    def house(self):
        return self.address.house

    def __eq__(self, other):
        if not isinstance(other, DeliveryPoint):
            return False
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    def __str__(self):
        if all([self.city, self.street, self.house]):
            return f'{self.city}, {self.street}, {self.house}'
        if all([self.city, self.street]) and self.street not in GENERIC_STREET:
            return f'{self.city}, {self.street}'
        return self.city

    def __repr__(self):
        return str(self)

    @classmethod
    def from_dict(cls, data):

        geolocation = data.get('geolocation')
        if geolocation:
            geolocation = Geolocation.from_str(geolocation)
        return cls(
            Address(data['city'], data['street'] or '', int(data['house'])),
            data['addressdesc'],
            data['branchname'],
            geolocation=geolocation
        )

    def to_dict(self):
        d = {
            'city': self.city,
            'street': self.street,
            'house': self.house,
            'addressdesc': self.description,
            'branchname': self.branch_name,
        }
        if self.geolocation:
            d['geolocation'] = str(self.geolocation)
        return d
