from logging import getLogger
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from datetime import datetime

from db.session import async_session
from utils.db.user import (
    create_or_update_user,
    update_user,
    get_user_by_id,
)
from utils.log import logger
from utils.tl_utils import (
    get_main_menu_keyboard,
    get_back_to_main_menu_keyboard,
    MyCallback,
)
from utils.parsers.gazprom import get_exchange_rate as get_gz_exchange_rate
from utils.parsers.google_finance import get_exchange_rate as get_google_exchange_rate
from utils.parsers.cbrf import get_exchange_rate as get_cbrf_exchange_rate
from utils.parsers import CBRFCodes, GoogleFinanceCodes
from schemas.user import UserCreateSchema, UserUpdateSchema


log = getLogger("bot")

start_router = Router()


@start_router.message(Command("start"))
async def index(message: Message):
    user = message.from_user

    async with async_session() as session:
        schema = UserCreateSchema(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            lang=user.language_code,
        )
        await create_or_update_user(session, schema)

    await message.answer(
        "Welcome! This is a bot for checking CNY exchange rate, choose desirable option:",
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.callback_query(MyCallback.filter(F.action == "show_gz_rate"))
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
            f"🌐 Gazprombank Exchange Rates:\n🈸 CNY Exchange Rate:\n💹 Buy: {rate.value}₽, Sell: {rate.sell_rate}₽\n🕐 Date: {rate_date}"
        )
    else:
        await waiting_msg.edit_text(
            "Currently, the information about the exchange rate is not available...",
            reply_markup=get_back_to_main_menu_keyboard(),
        )


@start_router.callback_query(MyCallback.filter(F.action == "show_google_rate"))
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
            f"🌐 Google Exchange Rates:\n💰 USD: {usd_to_rub.value:.2f}₽\n🈸 CNY: {cny_to_rub.value:.2f}₽\n🕐 Date: {rate_date}",
        )
    else:
        logger.error(
            f"Exchange rates missing for user {user.id}. One or more fields are None."
        )
        await waiting_msg.edit_text(
            "Currently, the information about the exchange rates is not available...",
            reply_markup=get_back_to_main_menu_keyboard(),
        )


@start_router.callback_query(MyCallback.filter(F.action == "show_cbr_rate"))
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
            f"🌐 CBRF Rates:\n💰 USD: {usd_to_rub.value:.2f}₽\n🈸 CNY: {cny_to_rub.value:.2f}₽\n🕐 Date: {rate_date_formatted}",
        )
    else:
        logger.error(
            f"Exchange rates missing for user {user.id}. One or more fields are None."
        )
        await waiting_msg.edit_text(
            "Currently, the information about the exchange rates is not available...",
            reply_markup=get_back_to_main_menu_keyboard(),
        )


@start_router.callback_query(MyCallback.filter(F.action == "back_to_main_menu"))
async def back_to_main_menu(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Welcome! This is a bot for checking CNY exchange rate, choose desirable option:",
        reply_markup=get_main_menu_keyboard(),
    )


@start_router.callback_query(MyCallback.filter(F.action == "donate"))
async def handle_donate(callback_query: CallbackQuery):
    await callback_query.message.edit_text(
        "Coming soon... Stay tuned for donation options!",
        reply_markup=get_back_to_main_menu_keyboard(),
    )
    user = callback_query.from_user
    logger.info(f"User {user.id} requested donation information.")


@start_router.callback_query(MyCallback.filter(F.action == "toggle_notify"))
async def toggle_notify(callback_query: CallbackQuery):
    user = callback_query.from_user

    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)

        if user_data is None:
            await callback_query.answer(
                "Error: user is not found in the database.", show_alert=True
            )
            return

        new_notify_value = not user_data.get("notify", False)

        schema = UserUpdateSchema(id=user.id, notify=new_notify_value)

        await update_user(session, schema)
        log.info(
            "User with id {} toggled {} their notifications".format(
                user.id, "on" if new_notify_value else "off"
            )
        )
        await callback_query.message.edit_text(
            f"Notifications {'toggled on' if new_notify_value else 'toggled off'}.",
            reply_markup=get_back_to_main_menu_keyboard(),
        )
