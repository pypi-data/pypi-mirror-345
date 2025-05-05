from pydantic import BaseModel, Field, ConfigDict


class BotatoBase(BaseModel):
    """
    Base model for Botato.
    """

    model_config = ConfigDict(
        extra="allow",
        arbitrary_types_allowed=True,
        json_encoders={
            set: lambda v: list(v),
        },
    )