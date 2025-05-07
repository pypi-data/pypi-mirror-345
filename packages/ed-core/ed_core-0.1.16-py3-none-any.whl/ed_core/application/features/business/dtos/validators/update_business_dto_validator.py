from ed_core.application.features.business.dtos.update_business_dto import \
    UpdateBusinessDto
from ed_core.application.features.common.dtos.validators.abc_dto_validator import (
    ABCDtoValidator, ValidationResponse)
from ed_core.application.features.driver.dtos.validators.create_driver_dto_validator import \
    CreateLocationDtoValidator


class UpdateBusinessDtoValidator(ABCDtoValidator[UpdateBusinessDto]):
    def validate(self, dto: UpdateBusinessDto) -> ValidationResponse:
        errors = []

        if "location" in dto:
            errors.extend(
                CreateLocationDtoValidator().validate(dto["location"]).errors,
            )

        if len(errors):
            return ValidationResponse.invalid(errors)

        return ValidationResponse.valid()
