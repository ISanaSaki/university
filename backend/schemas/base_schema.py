from pydantic import BaseModel, ConfigDict


class InputModel(BaseModel):
    """Shared configuration for API input models.

    - trims surrounding whitespace from strings
    - rejects unknown fields instead of silently ignoring them
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
