from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.order.dtos import OrderDto
from ed_core.application.features.order.dtos.order_dto import ConsumerDto
from ed_core.application.features.order.requests.queries import GetOrderQuery


@request_handler(GetOrderQuery, BaseResponse[OrderDto])
class GetOrderQueryHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(self, request: GetOrderQuery) -> BaseResponse[OrderDto]:
        if order := self._uow.order_repository.get(id=request.order_id):
            return BaseResponse[OrderDto].success(
                "Order fetched successfully.",
                OrderDto(
                    business_id=order["business_id"],
                    consumer=ConsumerDto(
                        **self._uow.consumer_repository.get(
                            id=order["consumer_id"],
                        )  # type: ignore
                    ),
                ),
            )

        return BaseResponse[OrderDto].error(
            "Order not found.",
            [f"Buisness with id {request.order_id} not found."],
        )
