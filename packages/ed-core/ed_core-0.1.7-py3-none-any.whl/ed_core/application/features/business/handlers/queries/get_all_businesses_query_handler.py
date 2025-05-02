from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.business.requests.queries import \
    GetBusinessQuery
from ed_core.application.features.common.dtos import BusinessDto, LocationDto


@request_handler(GetBusinessQuery, BaseResponse[list[BusinessDto]])
class GetAllBusinessesQueryHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: GetBusinessQuery
    ) -> BaseResponse[list[BusinessDto]]:
        businesses = self._uow.business_repository.get_all()

        return BaseResponse[list[BusinessDto]].success(
            "Business fetched successfully.",
            [
                BusinessDto(
                    **business,
                    location=LocationDto(
                        **self._uow.location_repository.get(
                            id=business["location_id"],
                        )  # type: ignore
                    ),
                )
                for business in businesses
            ],
        )
