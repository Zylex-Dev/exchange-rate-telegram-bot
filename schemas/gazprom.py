from pydantic import BaseModel


class ExchangeRateSchema(BaseModel):
    value: float
    sell_rate: float
    date: str
