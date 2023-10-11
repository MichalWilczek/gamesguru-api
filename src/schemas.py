from pydantic import BaseModel, HttpUrl


class ElementData(BaseModel):
    name: str
    link: HttpUrl
    price: float
    currency: str
