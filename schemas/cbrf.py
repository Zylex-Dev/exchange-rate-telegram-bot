from pydantic import BaseModel


class ExchangeRateSchema(BaseModel):
    currency: str
    value: float
    date: str
