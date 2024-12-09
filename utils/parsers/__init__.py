# codes support by CBR API: https://www.cbr.ru/scripts/XML_val.asp
from enum import Enum


class CBRFCodes(str, Enum):
    USD = "USD"
    CNY = "CNY"


class GazprombankCodes(str, Enum):
    USD = "USD"
    CNY = "CNY"


class GoogleFinanceCodes(str, Enum):
    CNY = "cny"
    USD = "usd"
    RUB = "rub"
