from datetime import datetime
from typing import TypedDict

from ed_domain.core.entities.route import WayPointType

from ed_core.application.features.common.dtos.order_dto import OrderDto


class WayPointDto(TypedDict):
    order: OrderDto
    type: WayPointType
    eta: datetime
    sequence: int


class RouteDto(TypedDict):
    waypoints: list[WayPointDto]
    estimated_distance_in_kms: float
    estimated_time_in_minutes: int
