from .schema_core import ValidationContext, ValidationSchema
from .validation_error import ValidationError


async def validate_object(schema: ValidationSchema, obj: object) -> None:
    context = ValidationContext.from_schema(schema)
    errors = await context.validate(obj)

    if len(errors) > 0:
        raise ValidationError(errors)
