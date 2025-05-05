from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import DeliveryJobDto
from ed_core.application.features.common.dtos.route_dto import RouteDto
from ed_core.application.features.driver.requests.queries.get_driver_delivery_jobs_query import \
    GetDriverDeliveryJobsQuery
from ed_core.common.exception_helpers import ApplicationException, Exceptions


@request_handler(GetDriverDeliveryJobsQuery, BaseResponse[list[DeliveryJobDto]])
class GetDriverDeliveryJobsQueryHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: GetDriverDeliveryJobsQuery
    ) -> BaseResponse[list[DeliveryJobDto]]:
        if delivery_jobs := self._uow.delivery_job_repository.get_all(
            driver_id=request.driver_id
        ):
            return BaseResponse[list[DeliveryJobDto]].success(
                "DeliveryJob fetched successfully.",
                [
                    DeliveryJobDto(
                        **delivery_job,
                        route=RouteDto(
                            self._uow.route_repository.get(
                                id=delivery_job["route_id"]
                            ),  # type: ignore
                        ),
                    )
                    for delivery_job in delivery_jobs
                ],
            )

        raise ApplicationException(
            Exceptions.NotFoundException,
            "Delivery jobs not found.",
            [f"Delivery jobs for driver with id {request.driver_id} not found."],
        )
