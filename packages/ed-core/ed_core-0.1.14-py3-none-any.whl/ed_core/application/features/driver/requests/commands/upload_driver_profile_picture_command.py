from dataclasses import dataclass
from uuid import UUID

from rmediator.decorators import request
from rmediator.mediator import Request

from ed_core.application.common.responses.base_response import BaseResponse
from ed_core.application.contracts.infrastructure.files.abc_image_uploader import \
    InputImage
from ed_core.application.features.common.dtos import DriverDto


@request(BaseResponse[DriverDto])
@dataclass
class UploadDriverProfilePictureCommand(Request):
    id: UUID
    file: InputImage
