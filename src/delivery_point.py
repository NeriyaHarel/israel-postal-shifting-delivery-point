from dataclasses import dataclass
from .location import Geolocation, Address

# A list of generic street names that are not relevant for the address
# it makes sense to ignore them completely as they dont add any value
# in addition they can cause issues with the geocoding
GENERIC_STREET = ('רחוב ראשי', 'ראשי', 'חדר דואר', 'לב הישוב')


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
        if all([self.city, self.street]):
            return f'{self.city}, {self.street}'
        return self.city

    def __repr__(self):
        return str(self)

    @classmethod
    def from_dict(cls, data):
        geolocation = data.get('geolocation')
        if geolocation:
            geolocation = Geolocation.from_str(geolocation)
        street = data['street'] or ''
        street = street.strip()
        if street in GENERIC_STREET:
            street = ''
        city = data['city'].strip()
        house = int(data['house'])
        return cls(
            Address(city, street, house),
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
