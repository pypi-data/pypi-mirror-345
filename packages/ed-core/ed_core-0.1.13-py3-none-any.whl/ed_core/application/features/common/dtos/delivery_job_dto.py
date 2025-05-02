from datetime import datetime
from typing import NotRequired, TypedDict
from uuid import UUID

from ed_domain.core.entities.delivery_job import DeliveryJobStatus

from ed_core.application.features.common.dtos.driver_payment_dto import \
    DriverPaymentDto
from ed_core.application.features.common.dtos.route_dto import RouteDto


class DeliveryJobDto(TypedDict):
    id: UUID
    route: RouteDto
    driver_id: NotRequired[UUID]
    driver_payment: NotRequired[DriverPaymentDto]
    status: DeliveryJobStatus
    estimated_payment: float
    estimated_completion_time: datetime
