from dataclasses import dataclass

from ed_domain.core.repositories.abc_unit_of_work import ABCUnitOfWork
from rmediator.decorators import request_handler
from rmediator.types import RequestHandler

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.files.abc_image_uploader import \
    ABCImageUploader
from ed_core.application.features.common.dtos import DriverDto
from ed_core.application.features.common.dtos.business_dto import LocationDto
from ed_core.application.features.common.dtos.car_dto import CarDto
from ed_core.application.features.driver.requests.commands.upload_driver_profile_picture_command import \
    UploadDriverProfilePictureCommand


@request_handler(UploadDriverProfilePictureCommand, BaseResponse[DriverDto])
@dataclass
class UploadDriverProfilePictureCommandHandler(RequestHandler):
    def __init__(self, uow: ABCUnitOfWork, image_uploader: ABCImageUploader):
        self._uow = uow
        self._image_uploader = image_uploader

    async def handle(
        self, request: UploadDriverProfilePictureCommand
    ) -> BaseResponse[DriverDto]:
        file = await self._image_uploader.upload(request.file)
        if driver := self._uow.driver_repository.get(id=request.id):
            driver["profile_image"] = file["url"]
            self._uow.driver_repository.update(driver["id"], driver)

            car = self._uow.car_repository.get(id=driver["car_id"])
            location = self._uow.location_repository.get(
                id=driver["location_id"],
            )

            return BaseResponse[DriverDto].success(
                "Image uploaded successfully.",
                DriverDto(
                    **driver,
                    car=CarDto(**car),  # type: ignore
                    location=LocationDto(**location),  # type: ignore
                ),
            )

        return BaseResponse[DriverDto].error(
            "Image couldn't be uploaded.",
            [f"Driver with id {request.id} does not exist."],
        )
