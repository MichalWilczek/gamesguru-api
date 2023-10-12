from pydantic import BaseModel, HttpUrl


class ElementData(BaseModel):
    name: str
    price: float
    currency: str
    url: HttpUrl

