from uuid import UUID

from fastapi import APIRouter, Depends
from rmediator.decorators.request_handler import Annotated
from rmediator.mediator import Mediator

from ed_core.application.features.common.dtos import OrderDto
from ed_core.application.features.order.requests.queries import (
    GetOrderQuery, GetOrdersQuery)
from ed_core.common.logging_helpers import get_logger
from ed_core.webapi.common.helpers import GenericResponse, rest_endpoint
from ed_core.webapi.dependency_setup import mediator

LOG = get_logger()
router = APIRouter(prefix="/orders", tags=["Order Feature"])


@router.get("", response_model=GenericResponse[list[OrderDto]])
@rest_endpoint
async def get_orders(
    mediator: Annotated[Mediator, Depends(mediator)],
):
    LOG.info("Satisfying get_orders request")
    return await mediator.send(GetOrdersQuery())


@router.get("/{order_id}", response_model=GenericResponse[OrderDto])
@rest_endpoint
async def get_order(
    order_id: UUID,
    mediator: Annotated[Mediator, Depends(mediator)],
):
    LOG.info("Satisfying get_order request")
    return await mediator.send(GetOrderQuery(order_id=order_id))
