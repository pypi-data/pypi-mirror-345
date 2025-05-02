from datetime import datetime
from typing import NotRequired, TypedDict
from uuid import UUID

from ed_domain.core.entities.order import OrderStatus, Parcel


class ConsumerDto(TypedDict):
    first_name: str
    last_name: str
    phone_number: str
    email: NotRequired[str]


class OrderDto(TypedDict):
    id: UUID
    consumer: ConsumerDto
    latest_time_of_delivery: datetime
    parcel: Parcel
    order_status: OrderStatus
    delivery_job_id: NotRequired[UUID]
