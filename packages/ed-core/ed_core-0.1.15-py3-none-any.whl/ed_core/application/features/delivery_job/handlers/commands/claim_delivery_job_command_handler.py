from uuid import UUID

from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import DeliveryJobDto, OrderDto
from ed_core.application.features.common.dtos.route_dto import (RouteDto,
                                                                WayPointDto)
from ed_core.application.features.delivery_job.requests.commands.claim_delivery_job_command import \
    ClaimDeliveryJobCommand
from ed_core.common.exception_helpers import ApplicationException, Exceptions


@request_handler(ClaimDeliveryJobCommand, BaseResponse[DeliveryJobDto])
class ClaimDeliveryJobCommandHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(
        self, request: ClaimDeliveryJobCommand
    ) -> BaseResponse[DeliveryJobDto]:
        delivery_job = self._uow.delivery_job_repository.get(
            id=request.delivery_job_id)
        if not delivery_job:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Delivery job not claimed.",
                [f"Delivery job with id {request.delivery_job_id} not found."],
            )

        driver = self._uow.driver_repository.get(id=request.driver_id)
        if not driver:
            raise ApplicationException(
                Exceptions.NotFoundException,
                "Delivery job not claimed.",
                [f"Drier with id {request.driver_id} not found."],
            )

        if "driver_id" in delivery_job and delivery_job["driver_id"] is not None:
            if delivery_job["driver_id"] != request.driver_id:
                raise ApplicationException(
                    Exceptions.BadRequestException,
                    "Delivery job already claimed.",
                    [
                        f"Delivery job with id {request.delivery_job_id} is already claimed by another driver."
                    ],
                )

            return BaseResponse[DeliveryJobDto].success(
                "Delivery job already claimed by this driver.",
                DeliveryJobDto(
                    **delivery_job,
                    route=await self.get_route_dto(
                        delivery_job["route_id"],
                    ),  # type: ignore
                ),
            )

        delivery_job["driver_id"] = driver["id"]
        self._uow.delivery_job_repository.update(
            request.delivery_job_id,
            delivery_job,
        )

        return BaseResponse[DeliveryJobDto].success(
            "Delivery job Claimed successfully.",
            DeliveryJobDto(
                **delivery_job,
                route=RouteDto(
                    self._uow.route_repository.get(
                        id=delivery_job["route_id"]
                    ),  # type: ignore
                ),
            ),
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
