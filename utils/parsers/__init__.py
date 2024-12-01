# codes support by CBR API: https://www.cbr.ru/scripts/XML_val.asp
from enum import Enum


class CBRFCodes(str, Enum):
    CNY = "CNY"
    USD = "USD"


class GoogleFinanceCodes(str, Enum):
    CNY = "cny"
    USD = "usd"
    RUB = "rub"
