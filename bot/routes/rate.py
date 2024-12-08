from aiogram import Router, F
from aiogram.types import CallbackQuery
from datetime import datetime

from utils.log import logger
from utils.tl_utils import MyCallback
from utils.parsers.gazprom import get_exchange_rate as get_gz_exchange_rate
from utils.parsers.google_finance import get_exchange_rate as get_google_exchange_rate
from utils.parsers.cbrf import get_exchange_rate as get_cbrf_exchange_rate
from utils.parsers import CBRFCodes, GoogleFinanceCodes


rate_router = Router()


@rate_router.callback_query(MyCallback.filter(F.action == "show_gz_rate"))
async def show_gz_rate(callback_query: CallbackQuery):
    user = callback_query.from_user
    waiting_msg = await callback_query.message.answer(
        "⏳ Waiting for server response, this may take some time..."
    )
    rate = await get_gz_exchange_rate()
    if rate is not None:
        rate_date = rate.date[:10]  # YYYY-MM-DD
        logger.info(
            f"User {user.id} requested Gazprombank CNY rates: buy_rate - {rate.value}, sell rate - {rate.sell_rate}, date - {rate_date}"
        )
        await waiting_msg.edit_text(
            f"🌐 *Gazprombank Exchange Rates*:\n🈸 CNY Exchange Rate:\n💹 Buy: {rate.value}₽, Sell: {rate.sell_rate}₽\n🕐 Date: {rate_date}"
        )
    else:
        await waiting_msg.delete()
        await callback_query.answer(
            "Currently, the information about the exchange rate is not available...",
        )


@rate_router.callback_query(MyCallback.filter(F.action == "show_google_rate"))
async def show_google_rate(callback_query: CallbackQuery):
    user = callback_query.from_user
    waiting_msg = await callback_query.message.answer(
        "⏳ Waiting for server response, this may take some time..."
    )
    usd_to_rub = await get_google_exchange_rate(
        GoogleFinanceCodes.USD, GoogleFinanceCodes.RUB
    )
    cny_to_rub = await get_google_exchange_rate(
        GoogleFinanceCodes.CNY, GoogleFinanceCodes.RUB
    )

    if usd_to_rub is not None and cny_to_rub is not None:
        rate_date = usd_to_rub.date
        logger.info(
            f"User {user.id} requested Google rates: USD/RUB = {usd_to_rub.value}, CNY/RUB = {cny_to_rub.value}, Date = {rate_date}"
        )
        await waiting_msg.edit_text(
            f"🌐 *Google Exchange Rates*:\n💰 USD: {usd_to_rub.value:.2f}₽\n🈸 CNY: {cny_to_rub.value:.2f}₽\n🕐 Date: {rate_date}",
        )
    else:
        logger.error(
            f"Exchange rates missing for user {user.id}. One or more fields are None."
        )
        await waiting_msg.delete()
        await callback_query.answer(
            "Currently, the information about the exchange rate is not available...",
        )


@rate_router.callback_query(MyCallback.filter(F.action == "show_cbr_rate"))
async def show_cbr_rate(callback_query: CallbackQuery):
    user = callback_query.from_user
    waiting_msg = await callback_query.message.answer(
        "⏳ Waiting for server response, this may take some time..."
    )
    usd_to_rub = await get_cbrf_exchange_rate(CBRFCodes.USD)
    cny_to_rub = await get_cbrf_exchange_rate(CBRFCodes.CNY)

    if usd_to_rub is not None and cny_to_rub is not None:
        rate_date = usd_to_rub.date
        rate_date_obj = datetime.strptime(rate_date, "%d.%m.%Y")
        rate_date_formatted = rate_date_obj.strftime("%Y-%m-%d")
        logger.info(
            f"User {user.id} requested CBRF rates: USD/RUB = {usd_to_rub.value}, CNY/RUB = {cny_to_rub.value}, Date = {rate_date_formatted}"
        )
        await waiting_msg.edit_text(
            f"🌐 *CBRF Rates:*\n💰 USD: {usd_to_rub.value:.2f}₽\n🈸 CNY: {cny_to_rub.value:.2f}₽\n🕐 Date: {rate_date_formatted}",
        )
    else:
        logger.error(
            f"Exchange rates missing for user {user.id}. One or more fields are None."
        )
        await waiting_msg.delete()
        await callback_query.answer(
            "Currently, the information about the exchange rate is not available...",
        )
