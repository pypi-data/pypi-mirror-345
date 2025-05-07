from uuid import UUID

from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import DeliveryJobDto, OrderDto
from ed_core.application.features.common.dtos.route_dto import (RouteDto,
                                                                WayPointDto)
from ed_core.application.features.delivery_job.requests.queries.get_delivery_job_query import \
    GetDeliveryJobQuery
from ed_core.common.exception_helpers import ApplicationException, Exceptions


@request_handler(GetDeliveryJobQuery, BaseResponse[DeliveryJobDto])
class GetDeliveryJobQueryHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: GetDeliveryJobQuery
    ) -> BaseResponse[DeliveryJobDto]:
        if delivery_job := self._uow.delivery_job_repository.get(
            id=request.delivery_job_id
        ):
            return BaseResponse[DeliveryJobDto].success(
                "Delivery jobs fetched successfully.",
                DeliveryJobDto(
                    **delivery_job,
                    route=await self.get_route_dto(
                        delivery_job["route_id"],
                    ),  # type: ignore
                ),
            )

        raise ApplicationException(
            Exceptions.NotFoundException,
            "Delivery jobs not found.",
            [f"Delivery jobs for driver with id {request.delivery_job_id} not found."],
        )

    async def get_route_dto(self, route_id: UUID) -> RouteDto | None:
        if route := self._uow.route_repository.get(id=route_id):

            return RouteDto(
                estimated_distance_in_kms=route["estimated_distance_in_kms"],
                estimated_time_in_minutes=route["estimated_time_in_minutes"],
                waypoints=[
                    WayPointDto(
                        **waypoint,  # type: ignore
                        order=OrderDto(
                            **self._uow.order_repository.get(
                                id=waypoint["order_id"],
                            )  # type: ignore
                        ),
                    )
                    for waypoint in route["waypoints"]
                ],
            )

        return None
