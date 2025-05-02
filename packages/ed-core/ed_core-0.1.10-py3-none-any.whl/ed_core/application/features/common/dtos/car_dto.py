from typing import TypedDict


class CarDto(TypedDict):
    make: str
    model: str
    year: int
    color: str
    seats: int
    license_plate: str
    registration_number: str
