from datetime import datetime
from typing import TypedDict
from uuid import UUID

from ed_domain.core.entities.route import WayPoint


class CreateRouteDto(TypedDict):
    waypoints: list[WayPoint]
    estimated_distance_in_kms: float
    estimated_time_in_minutes: int


class CreateDeliveryJobDto(TypedDict):
    order_ids: list[UUID]
    route: CreateRouteDto
    estimated_payment: float
    estimated_completion_time: datetime
