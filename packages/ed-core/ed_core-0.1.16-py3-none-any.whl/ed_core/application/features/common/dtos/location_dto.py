from typing import TypedDict


class LocationDto(TypedDict):
    address: str
    latitude: float
    longitude: float
    postal_code: str
    city: str
