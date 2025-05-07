from typing import Annotated

from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from ed_infrastructure.persistence.mongo_db.db_client import DbClient
from ed_infrastructure.persistence.mongo_db.unit_of_work import UnitOfWork
from fastapi import Depends
from rmediator.mediator import Mediator

from ed_core.application.contracts.infrastructure.message_queue.abc_producer import \
    ABCProducer
from ed_core.application.contracts.infrastructure.message_queue.abc_subscriber import \
    ABCSubscriber
from ed_core.application.features.business.handlers.commands import (
    CreateBusinessCommandHandler, CreateOrdersCommandHandler,
    UpdateBusinessCommandHandler)
from ed_core.application.features.business.handlers.queries import (
    GetAllBusinessesQueryHandler, GetBusinessByUserIdQueryHandler,
    GetBusinessOrdersQueryHandler, GetBusinessQueryHandler)
from ed_core.application.features.business.requests.commands import (
    CreateBusinessCommand, CreateOrdersCommand, UpdateBusinessCommand)
from ed_core.application.features.business.requests.queries import (
    GetAllBusinessQuery, GetBusinessByUserIdQuery, GetBusinessOrdersQuery,
    GetBusinessQuery)
from ed_core.application.features.delivery_job.handlers.commands import (
    ClaimDeliveryJobCommandHandler, CreateDeliveryJobCommandHandler)
from ed_core.application.features.delivery_job.handlers.queries import (
    GetDeliveryJobQueryHandler, GetDeliveryJobsQueryHandler)
from ed_core.application.features.delivery_job.requests.commands import (
    ClaimDeliveryJobCommand, CreateDeliveryJobCommand)
from ed_core.application.features.delivery_job.requests.queries import (
    GetDeliveryJobQuery, GetDeliveryJobsQuery)
from ed_core.application.features.driver.handlers.commands import (
    CreateDriverCommandHandler, UpdateDriverCommandHandler)
from ed_core.application.features.driver.handlers.queries import (
    GetAllDriversQueryHandler, GetDriverByUserIdQueryHandler,
    GetDriverDeliveryJobsQueryHandler, GetDriverQueryHandler)
from ed_core.application.features.driver.requests.commands import (
    CreateDriverCommand, UpdateDriverCommand)
from ed_core.application.features.driver.requests.queries import (
    GetAllDriversQuery, GetDriverByUserIdQuery, GetDriverDeliveryJobsQuery,
    GetDriverQuery)
from ed_core.application.features.order.handlers.queries import (
    GetOrderQueryHandler, GetOrdersQueryHandler)
from ed_core.application.features.order.requests.queries import (
    GetOrderQuery, GetOrdersQuery)
from ed_core.common.generic_helpers import get_config
from ed_core.common.typing.config import Config, TestMessage
from ed_core.infrastructure.rabbitmq.producer import RabbitMQProducer
from ed_core.infrastructure.rabbitmq.subscriber import RabbitMQSubscriber


def get_db_client(config: Annotated[Config, Depends(get_config)]) -> DbClient:
    return DbClient(
        config["mongo_db_connection_string"],
        config["db_name"],
    )


def get_uow(db_client: Annotated[DbClient, Depends(get_db_client)]) -> ABCUnitOfWork:
    return UnitOfWork(db_client)


def get_producer(config: Annotated[Config, Depends(get_config)]) -> ABCProducer:
    producer = RabbitMQProducer[TestMessage](
        config["rabbitmq_url"],
        config["rabbitmq_queue"],
    )
    producer.start()

    return producer


def get_subscriber(config: Annotated[Config, Depends(get_config)]) -> ABCSubscriber:
    subscriber = RabbitMQSubscriber[TestMessage](
        config["rabbitmq_url"],
        config["rabbitmq_queue"],
        lambda x: print(x),
    )
    subscriber.start()

    return subscriber


def mediator(
    uow: Annotated[ABCUnitOfWork, Depends(get_uow)],
    producer: Annotated[ABCProducer, Depends(get_producer)],
) -> Mediator:
    mediator = Mediator()

    handlers = [
        # Delivery job handler
        (CreateDeliveryJobCommand, CreateDeliveryJobCommandHandler(uow)),
        (ClaimDeliveryJobCommand, ClaimDeliveryJobCommandHandler(uow)),
        (GetDeliveryJobsQuery, GetDeliveryJobsQueryHandler(uow)),
        (GetDeliveryJobQuery, GetDeliveryJobQueryHandler(uow)),
        # Driver handlers
        (CreateDriverCommand, CreateDriverCommandHandler(uow)),
        (GetDriverDeliveryJobsQuery, GetDriverDeliveryJobsQueryHandler(uow)),
        (GetDriverQuery, GetDriverQueryHandler(uow)),
        (GetDriverByUserIdQuery, GetDriverByUserIdQueryHandler(uow)),
        (GetAllDriversQuery, GetAllDriversQueryHandler(uow)),
        (UpdateDriverCommand, UpdateDriverCommandHandler(uow)),
        # Business handlers
        (CreateBusinessCommand, CreateBusinessCommandHandler(uow)),
        (CreateOrdersCommand, CreateOrdersCommandHandler(uow, producer)),
        (GetBusinessQuery, GetBusinessQueryHandler(uow)),
        (GetBusinessByUserIdQuery, GetBusinessByUserIdQueryHandler(uow)),
        (GetBusinessOrdersQuery, GetBusinessOrdersQueryHandler(uow)),
        (GetAllBusinessQuery, GetAllBusinessesQueryHandler(uow)),
        (UpdateBusinessCommand, UpdateBusinessCommandHandler(uow)),
        # Order handlers
        (GetOrdersQuery, GetOrdersQueryHandler(uow)),
        (GetOrderQuery, GetOrderQueryHandler(uow)),
    ]
    for command, handler in handlers:
        mediator.register_handler(command, handler)

    return mediator
