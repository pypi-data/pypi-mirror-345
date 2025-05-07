from typing import NotRequired, TypedDict

from ed_domain.core.entities.business import BillingDetail

from ed_core.application.features.business.dtos.create_location_dto import \
    CreateLocationDto


class UpdateBusinessDto(TypedDict):
    phone_number: NotRequired[str]
    email: NotRequired[str]
    location: NotRequired[CreateLocationDto]
    billing_details: NotRequired[list[BillingDetail]]
