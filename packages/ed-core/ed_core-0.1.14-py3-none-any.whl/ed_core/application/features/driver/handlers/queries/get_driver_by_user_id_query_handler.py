from dataclasses import dataclass

from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import DriverDto
from ed_core.application.features.common.dtos.business_dto import LocationDto
from ed_core.application.features.common.dtos.car_dto import CarDto
from ed_core.application.features.driver.requests.queries import \
    GetDriverByUserIdQuery


@request_handler(GetDriverByUserIdQuery, BaseResponse[DriverDto])
@dataclass
class GetDriverByUserIdQueryHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(self, request: GetDriverByUserIdQuery) -> BaseResponse[DriverDto]:
        if driver := self._uow.driver_repository.get(user_id=request.user_id):
            return BaseResponse[DriverDto].success(
                "Driver fetched successfully.",
                DriverDto(
                    id=driver["id"],
                    first_name=driver["first_name"],
                    last_name=driver["last_name"],
                    profile_image=driver["profile_image"],
                    phone_number=driver["phone_number"],
                    email=driver.get("email", ""),
                    car=CarDto(
                        **self._uow.car_repository.get(
                            id=driver["car_id"],
                        ),  # type: ignore
                    ),
                    location=LocationDto(
                        **self._uow.location_repository.get(
                            id=driver["location_id"],
                        )  # type: ignore
                    ),
                ),
            )

        raise ApplicationException(
            Exceptions.NotFoundException,
            "Driver not found.",
            [f"Buisness with id {request.user_id} not found."],
        )
