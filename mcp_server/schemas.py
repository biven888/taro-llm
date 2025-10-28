from pydantic import BaseModel, ConfigDict


class CardPydantic(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: int
    name: str
    arcane: str
    suit: str | None


class OneCardPydantic(BaseModel):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: int
    name: str
    arcane: str
    suit: str | None
    image: str
