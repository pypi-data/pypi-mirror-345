from abc import ABCMeta, abstractmethod

from ed_domain.documentation.common.api_response import ApiResponse

from ed_core.application.features.business.dtos import (CreateBusinessDto,
                                                        CreateOrdersDto,
                                                        UpdateBusinessDto)
from ed_core.application.features.common.dtos import (BusinessDto,
                                                      DeliveryJobDto,
                                                      DriverDto, OrderDto)
from ed_core.application.features.delivery_job.dtos.create_delivery_job_dto import \
    CreateDeliveryJobDto
from ed_core.application.features.driver.dtos import (CreateDriverDto,
                                                      UpdateDriverDto)


class ABCCoreApiClient(metaclass=ABCMeta):
    # Driver features
    @abstractmethod
    def get_drivers(self) -> ApiResponse[list[DriverDto]]: ...

    @abstractmethod
    def create_driver(
        self, create_driver_dto: CreateDriverDto
    ) -> ApiResponse[DriverDto]: ...

    @abstractmethod
    def get_driver_delivery_jobs(
        self, driver_id: str
    ) -> ApiResponse[list[DeliveryJobDto]]: ...

    @abstractmethod
    def get_driver(self, driver_id: str) -> ApiResponse[DriverDto]: ...

    @abstractmethod
    def update_driver(
        self, driver_id: str, update_driver_dto: UpdateDriverDto
    ) -> ApiResponse[DriverDto]: ...

    @abstractmethod
    def get_driver_by_user_id(
        self, user_id: str) -> ApiResponse[DriverDto]: ...

    @abstractmethod
    def claim_delivery_job(
        self, driver_id: str, delivery_job_id: str
    ) -> ApiResponse[DeliveryJobDto]: ...

    # Business features
    @abstractmethod
    def get_all_businesses(self) -> ApiResponse[list[BusinessDto]]: ...

    @abstractmethod
    def create_business(
        self, create_business_dto: CreateBusinessDto
    ) -> ApiResponse[BusinessDto]: ...

    @abstractmethod
    def get_business(self, business_id: str) -> ApiResponse[BusinessDto]: ...

    @abstractmethod
    def update_business(
        self, business_id: str, update_business_dto: UpdateBusinessDto
    ) -> ApiResponse[BusinessDto]: ...

    @abstractmethod
    def get_business_by_user_id(
        self, user_id: str) -> ApiResponse[BusinessDto]: ...

    @abstractmethod
    def get_business_orders(
        self, business_id: str) -> ApiResponse[list[OrderDto]]: ...

    @abstractmethod
    def create_business_orders(
        self, business_id: str, create_orders_dto: CreateOrdersDto
    ) -> ApiResponse[list[OrderDto]]: ...

    # Delivery job features
    @abstractmethod
    def get_delivery_jobs(self) -> ApiResponse[list[DeliveryJobDto]]: ...

    @abstractmethod
    def get_delivery_job(
        self, delivery_job_id: str) -> ApiResponse[DeliveryJobDto]: ...

    @abstractmethod
    def create_delivery_job(
        self, create_delivery_job_dto: CreateDeliveryJobDto
    ) -> ApiResponse[DeliveryJobDto]: ...

    # Order features
    @abstractmethod
    def get_orders(self) -> ApiResponse[list[OrderDto]]: ...

    @abstractmethod
    def get_order(self, order_id: str) -> ApiResponse[OrderDto]: ...
