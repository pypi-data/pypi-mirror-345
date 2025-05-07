from uuid import UUID

from fastapi import APIRouter, Depends
from rmediator.decorators.request_handler import Annotated
from rmediator.mediator import Mediator

from ed_core.application.features.common.dtos.delivery_job_dto import \
    DeliveryJobDto
from ed_core.application.features.common.dtos.driver_dto import DriverDto
from ed_core.application.features.delivery_job.requests.commands import \
    ClaimDeliveryJobCommand
from ed_core.application.features.driver.dtos import (CreateDriverDto,
                                                      UpdateDriverDto)
from ed_core.application.features.driver.requests.commands import (
    CreateDriverCommand, UpdateDriverCommand)
from ed_core.application.features.driver.requests.queries import (
    GetAllDriversQuery, GetDriverByUserIdQuery, GetDriverDeliveryJobsQuery,
    GetDriverQuery)
from ed_core.common.logging_helpers import get_logger
from ed_core.webapi.common.helpers import GenericResponse, rest_endpoint
from ed_core.webapi.dependency_setup import mediator

LOG = get_logger()
router = APIRouter(prefix="/drivers", tags=["Driver Feature"])


@router.get("", response_model=GenericResponse[list[DriverDto]])
@rest_endpoint
async def get_all_drivers(
    mediator: Annotated[Mediator, Depends(mediator)],
):
    LOG.info("Satisfying get_all_drivers request")
    return await mediator.send(GetAllDriversQuery())


@router.post("", response_model=GenericResponse[DriverDto])
@rest_endpoint
async def create_driver(
    request_dto: CreateDriverDto,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    LOG.info(f"Satisfying request {request_dto}")
    return await mediator.send(CreateDriverCommand(dto=request_dto))


@router.get(
    "/{driver_id}/delivery-jobs", response_model=GenericResponse[list[DeliveryJobDto]]
)
@rest_endpoint
async def driver_delivery_jobs(
    driver_id: UUID,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(GetDriverDeliveryJobsQuery(driver_id=driver_id))


@router.get("/{driver_id}", response_model=GenericResponse[DriverDto])
@rest_endpoint
async def get_driver(
    driver_id: UUID,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(GetDriverQuery(driver_id=driver_id))


@router.put("/{driver_id}", response_model=GenericResponse[DriverDto])
@rest_endpoint
async def update_driver(
    driver_id: UUID,
    dto: UpdateDriverDto,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(UpdateDriverCommand(driver_id=driver_id, dto=dto))


@router.get("/users/{user_id}", response_model=GenericResponse[DriverDto])
@rest_endpoint
async def get_driver_by_user_id(
    user_id: UUID,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(GetDriverByUserIdQuery(user_id=user_id))


@router.post(
    "/{driver_id}/claim/{delivery_job_id}",
    response_model=GenericResponse[DeliveryJobDto],
)
@rest_endpoint
async def claim_delivery_job(
    driver_id: UUID,
    delivery_job_id: UUID,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    return await mediator.send(
        ClaimDeliveryJobCommand(
            driver_id=driver_id,
            delivery_job_id=delivery_job_id,
        )
    )
