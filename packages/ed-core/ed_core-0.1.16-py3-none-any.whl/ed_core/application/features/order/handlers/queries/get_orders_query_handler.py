from ed_domain.common.exceptions import ApplicationException, Exceptions
from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.features.common.dtos import ConsumerDto, OrderDto
from ed_core.application.features.order.requests.queries import GetOrdersQuery


@request_handler(GetOrdersQuery, BaseResponse[list[OrderDto]])
class GetOrdersQueryHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork):
        self._uow = uow

    async def handle(self, request: GetOrdersQuery) -> BaseResponse[list[OrderDto]]:
        try:
            order_dtos = [
                OrderDto(
                    **order,
                    consumer=ConsumerDto(
                        **self._uow.consumer_repository.get(
                            id=order["consumer_id"],
                        )  # type: ignore
                    ),
                )
                for order in self._uow.order_repository.get_all()
            ]
            return BaseResponse[list[OrderDto]].success(
                "Orders fetched successfully.",
                order_dtos,
            )

        except Exception as e:
            raise ApplicationException(
                Exceptions.InternalServerException, "Error fetching orders", [
                    str(e)]
            ) from e
