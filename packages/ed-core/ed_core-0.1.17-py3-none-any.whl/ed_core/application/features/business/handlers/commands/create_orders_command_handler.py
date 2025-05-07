from datetime import UTC, datetime

from ed_domain.core.entities import Bill, Consumer, Location, Order
from ed_domain.core.entities.order import OrderStatus
from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from ed_domain.core.value_objects.money import Currency, Money
from ed_domain.queues.ed_optimization.order_model import (BusinessModel,
                                                          ConsumerModel,
                                                          OrderModel)
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.message_queue.abc_producer import \
    ABCProducer
from ed_core.application.features.business.dtos import CreateLocationDto
from ed_core.application.features.business.dtos.create_orders_dto import \
    CreateConsumerDto
from ed_core.application.features.business.dtos.validators.create_orders_dto_validator import \
    CreateOrdersDtoValidator
from ed_core.application.features.business.requests.commands import \
    CreateOrdersCommand
from ed_core.application.features.common.dtos import ConsumerDto, OrderDto
from ed_core.common.generic_helpers import get_new_id
from ed_core.common.logging_helpers import get_logger

LOG = get_logger()


@request_handler(CreateOrdersCommand, BaseResponse[list[OrderDto]])
class CreateOrdersCommandHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork, producer: ABCProducer[OrderModel]):
        self._uow = uow
        self._producer = producer

    async def handle(
        self, request: CreateOrdersCommand
    ) -> BaseResponse[list[OrderDto]]:
        business_id = request.business_id
        dto = request.dto
        dto_validator = CreateOrdersDtoValidator().validate(request.dto)

        if not dto_validator.is_valid:
            return BaseResponse[list[OrderDto]].error(
                "Orders cannot be created.",
                dto_validator.errors,
            )

        consumers = await self._create_or_get_consumers(
            [order["consumer"] for order in dto["orders"]]
        )
        bill = await self._create_bill()
        created_orders = self._uow.order_repository.create_many(
            [
                Order(
                    id=get_new_id(),
                    consumer_id=consumer["id"],
                    business_id=business_id,
                    bill_id=bill["id"],
                    latest_time_of_delivery=order["latest_time_of_delivery"],
                    parcel=order["parcel"],
                    order_status=OrderStatus.PENDING,
                    create_datetime=datetime.now(UTC),
                    update_datetime=datetime.now(UTC),
                    deleted=False,
                )
                for consumer, order in zip(consumers, dto["orders"])
            ]
        )

        await self._publish_orders(created_orders, consumers)

        return BaseResponse[list[OrderDto]].success(
            "Order created successfully.",
            [
                OrderDto(
                    **order,
                    consumer=ConsumerDto(**consumer),  # type: ignore
                )
                for order, consumer in zip(created_orders, consumers)
            ],
        )

    async def _publish_orders(
        self, orders: list[Order], consumers: list[Consumer]
    ) -> None:
        for order, consumer in zip(orders, consumers):
            self._producer.publish(
                OrderModel(
                    **order,  # type: ignore
                    consumer=ConsumerModel(**consumer),  # type: ignore
                    business=BusinessModel(
                        **self._uow.business_repository.get(
                            id=order["business_id"],
                        )  # type: ignore
                    ),
                )
            )

    async def _create_bill(self) -> Bill:
        return self._uow.bill_repository.create(
            Bill(
                id=get_new_id(),
                amount=Money(
                    amount=10,
                    currency=Currency.ETB,
                ),
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
                paid=False,
            )
        )

    async def _create_or_get_consumers(
        self, consumers: list[CreateConsumerDto]
    ) -> list[Consumer]:
        return [
            self._uow.consumer_repository.get(
                phone_number=consumer["phone_number"])
            or self._uow.consumer_repository.create(
                Consumer(
                    **consumer,  # type: ignore
                    id=get_new_id(),
                    user_id=get_new_id(),
                    notification_ids=[],
                    active_status=True,
                    created_datetime=datetime.now(UTC),
                    updated_datetime=datetime.now(UTC),
                    location_id=(await self._create_location(consumer["location"]))[
                        "id"
                    ],
                )
            )
            for consumer in consumers
        ]

    async def _create_location(self, location: CreateLocationDto) -> Location:
        return self._uow.location_repository.create(
            Location(
                **location,
                id=get_new_id(),
                city="Addis Ababa",
                country="Ethiopia",
                create_datetime=datetime.now(UTC),
                update_datetime=datetime.now(UTC),
                deleted=False,
            )
        )
