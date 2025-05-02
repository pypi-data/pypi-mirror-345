from datetime import datetime
from typing import TypedDict
from uuid import UUID

from ed_domain.core.entities.driver_payment import (DriverPaymentDetail,
                                                    DriverPaymentStatus)


class DriverPaymentDto(TypedDict):
    id: UUID
    amount: float
    status: DriverPaymentStatus
    date: datetime
    detail: DriverPaymentDetail
