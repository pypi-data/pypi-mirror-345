from ed_domain.services.common.base_endpoint import BaseEndpoint
from ed_domain.services.common.endpoint_description import EndpointDescription
from ed_domain.services.common.http_method import HttpMethod

from ed_core.application.features.business.dtos import (CreateBusinessDto,
                                                        CreateOrdersDto,
                                                        OrderDto)
from ed_core.application.features.common.dtos import (BusinessDto,
                                                      DeliveryJobDto,
                                                      DriverDto)
from ed_core.application.features.delivery_job.dtos import CreateDeliveryJobDto
from ed_core.application.features.driver.dtos import CreateDriverDto


class CoreEndpoint(BaseEndpoint):
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._descriptions: list[EndpointDescription] = [
            # Business endpoints
            {
                "name": "get_all_businesses",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/businesses",
                "response_model": list[BusinessDto],
            },
            {
                "name": "create_business",
                "method": HttpMethod.POST,
                "path": f"{self._base_url}/businesses",
                "request_model": CreateBusinessDto,
                "response_model": BusinessDto,
            },
            {
                "name": "get_business",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/businesses/{{business_id}}",
                "path_params": {"business_id": str},
                "response_model": BusinessDto,
            },
            {
                "name": "get_business_by_user_id",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/businesses/users/{{user_id}}",
                "path_params": {"user_id": str},
                "response_model": BusinessDto,
            },
            {
                "name": "get_business_orders",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/businesses/{{business_id}}/orders",
                "path_params": {"business_id": str},
                "response_model": list[OrderDto],
            },
            {
                "name": "create_business_orders",
                "method": HttpMethod.POST,
                "path": f"{self._base_url}/businesses/{{business_id}}/orders",
                "path_params": {"business_id": str},
                "request_model": CreateOrdersDto,
                "response_model": OrderDto,
            },
            # Driver endpoints
            {
                "name": "get_drivers",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/drivers",
                "response_model": list[DriverDto],
            },
            {
                "name": "create_driver",
                "method": HttpMethod.POST,
                "path": f"{self._base_url}/drivers",
                "request_model": CreateDriverDto,
                "response_model": DriverDto,
            },
            {
                "name": "get_driver_delivery_jobs",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/drivers/{{driver_id}}/delivery-jobs",
                "path_params": {"driver_id": str},
                "response_model": list[DeliveryJobDto],
            },
            {
                "name": "upload_driver_profile",
                "method": HttpMethod.POST,
                "path": f"{self._base_url}/drivers/{{driver_id}}/upload",
                "path_params": {"driver_id": str},
                "response_model": DriverDto,
            },
            {
                "name": "get_driver",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/drivers/{{driver_id}}",
                "path_params": {"driver_id": str},
                "response_model": DriverDto,
            },
            {
                "name": "get_driver_by_user_id",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/drivers/users/{{user_id}}",
                "path_params": {"user_id": str},
                "response_model": DriverDto,
            },
            {
                "name": "claim_delivery_job",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/{{driver_id}}/claim/{{delivery_job_id}}",
                "path_params": {"driver_id": str, "delivery_job_id": str},
                "response_model": DeliveryJobDto,
            },
            # Delivery job endpoints
            {
                "name": "get_delivery_jobs",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/delivery-jobs",
                "response_model": list[DeliveryJobDto],
            },
            {
                "name": "get_delivery_job",
                "method": HttpMethod.GET,
                "path": f"{self._base_url}/delivery-jobs/{{delivery_job_id}}",
                "path_params": {"delivery_job_id": str},
                "response_model": DeliveryJobDto,
            },
            {
                "name": "create_delivery_job",
                "method": HttpMethod.POST,
                "path": f"{self._base_url}/delivery-jobs",
                "request_model": CreateDeliveryJobDto,
                "response_model": DeliveryJobDto,
            },
        ]

    @property
    def descriptions(self) -> list[EndpointDescription]:
        return self._descriptions
