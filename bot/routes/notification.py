from aiogram import Router, F, Bot
from aiogram.types import Message
from aiogram.filters.callback_data import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup, StateFilter
from db.session import async_session
from schemas.user import UserThresholdUpdateSchema, UserNotificationUpdateSchema
from utils.db.user import (
    get_user_by_id,
    update_user_threshold,
    update_user_notifications,
)
from utils.tl_utils import (
    MyCallback,
    get_notification_config_menu,
    get_threshold_keyboard,
    get_toggle_notifications_keyboard,
)
from utils.log import logger

notification_router = Router()


class ThresholdState(StatesGroup):
    setting_threshold = State()
    waiting_for_value = State()


@notification_router.callback_query(MyCallback.filter(F.action == "notifications"))
async def notification_menu(callback_query: CallbackQuery):
    user = callback_query.from_user
    logger.info("User with id {} entered notifications menu".format(user.id))

    await callback_query.message.edit_text(
        f"This is the notifications menu. Choose an option:",
        reply_markup=get_notification_config_menu(),
    )


@notification_router.callback_query(
    MyCallback.filter(F.action == "back_to_notification_menu")
)
async def back_to_notification_menu(callback_query: CallbackQuery):
    user = callback_query.from_user
    logger.info(
        "User with id {} is returning to the notifications menu".format(user.id)
    )

    await callback_query.message.edit_text(
        "This is the notifications menu. Choose an option:",
        reply_markup=get_notification_config_menu(),
    )


@notification_router.callback_query(
    MyCallback.filter(F.action == "show_toggle_notifications")
)
async def toggle_notifications(callback_query: CallbackQuery):
    user = callback_query.from_user
    logger.info("User with id {} is toggling notifications".format(user.id))

    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)
        if user_data:
            status_text = (
                f"Gazprombank notifications: {'Enabled' if user_data.gz_notify else 'Disabled'}\n"
                f"Google notifications: {'Enabled' if user_data.google_notify else 'Disabled'}\n"
                f"CBR notifications: {'Enabled' if user_data.cbrf_notify else 'Disabled'}"
            )

            await callback_query.message.edit_text(
                f"Current notifications status:\n\n{status_text}\n\n"
                f"Select which notifications to toggle:",
                reply_markup=get_toggle_notifications_keyboard(),
            )


@notification_router.callback_query(MyCallback.filter(F.action == "toggle_gz_notify"))
async def toggle_gz_notify(callback_query: CallbackQuery):
    user = callback_query.from_user
    logger.info("User with id {} is toggling Gazprombank notifications".format(user.id))

    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)
        if user_data:
            new_gz_notify = not user_data.gz_notify

            await update_user_notifications(
                session,
                UserNotificationUpdateSchema(id=user.id, gz_notify=new_gz_notify),
            )
            status_text = (
                f"Gazprombank notifications: {'Enabled' if new_gz_notify else 'Disabled'}\n"
                f"Google notifications: {'Enabled' if user_data.google_notify else 'Disabled'}\n"
                f"CBR notifications: {'Enabled' if user_data.cbrf_notify else 'Disabled'}"
            )
            await callback_query.message.edit_text(
                f"Current notifications status:\n\n{status_text}\n\n"
                f"Select which notifications to toggle:",
                reply_markup=get_toggle_notifications_keyboard(),
            )


@notification_router.callback_query(
    MyCallback.filter(F.action == "toggle_google_notify")
)
async def toggle_google_notify(callback_query: CallbackQuery):
    user = callback_query.from_user
    logger.info("User with id {} is toggling Google notifications".format(user.id))

    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)
        if user_data:
            current_google_notify = user_data.google_notify
            new_google_notify = not current_google_notify

            await update_user_notifications(
                session,
                UserNotificationUpdateSchema(
                    id=user.id, google_notify=new_google_notify
                ),
            )
            status_text = (
                f"Gazprombank notifications: {'Enabled' if user_data.gz_notify else 'Disabled'}\n"
                f"Google notifications: {'Enabled' if new_google_notify else 'Disabled'}\n"
                f"CBR notifications: {'Enabled' if user_data.cbrf_notify else 'Disabled'}"
            )
            await callback_query.message.edit_text(
                f"Current notifications status:\n\n{status_text}\n\n"
                f"Select which notifications to toggle:",
                reply_markup=get_toggle_notifications_keyboard(),
            )


@notification_router.callback_query(MyCallback.filter(F.action == "toggle_cbrf_notify"))
async def toggle_cbrf_notify(callback_query: CallbackQuery):
    user = callback_query.from_user
    logger.info("User with id {} is toggling CBR notifications".format(user.id))

    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)
        if user_data:
            new_cbrf_notify = not user_data.cbrf_notify

            await update_user_notifications(
                session,
                UserNotificationUpdateSchema(id=user.id, cbrf_notify=new_cbrf_notify),
            )
            status_text = (
                f"Gazprombank notifications: {'Enabled' if user_data.gz_notify else 'Disabled'}\n"
                f"Google notifications: {'Enabled' if user_data.google_notify else 'Disabled'}\n"
                f"CBR notifications: {'Enabled' if new_cbrf_notify else 'Disabled'}"
            )
            await callback_query.message.edit_text(
                f"Current notifications status:\n\n{status_text}\n\n"
                f"Select which notifications to toggle:",
                reply_markup=get_toggle_notifications_keyboard(),
            )


@notification_router.callback_query(
    MyCallback.filter(F.action == "toggle_all_notifications_off")
)
async def toggle_all_notifications_off(callback_query: CallbackQuery):
    user = callback_query.from_user
    logger.info("User with id {} is toggling all notifications off".format(user.id))

    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)
        if user_data:
            await update_user_notifications(
                session,
                UserNotificationUpdateSchema(
                    id=user.id, gz_notify=False, google_notify=False, cbrf_notify=False
                ),
            )
            status_text = (
                f"Gazprombank notifications: Disabled\n"
                f"Google notifications: Disabled\n"
                f"CBR notifications: Disabled"
            )
            await callback_query.message.edit_text(
                f"Current notifications status:\n\n{status_text}\n\n"
                f"Select which notifications to toggle:",
                reply_markup=get_toggle_notifications_keyboard(),
            )


@notification_router.callback_query(MyCallback.filter(F.action == "show_threshold"))
async def threshold_menu(callback_query: CallbackQuery):
    user = callback_query.from_user
    logger.info("User with id {} is setting notification thresholds".format(user.id))

    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)
        if user_data:
            threshold_text = (
                f"Gazprombank Threshold: {user_data.gz_threshold}\n"
                f"Google Threshold: {user_data.google_threshold}\n"
                f"CBR Threshold: {user_data.cbrf_threshold}"
            )

            await callback_query.message.edit_text(
                f"Current thresholds:\n\n{threshold_text}\n\n"
                "Select a service to set the notification threshold:",
                reply_markup=get_threshold_keyboard(),
            )


@notification_router.callback_query(MyCallback.filter(F.action == "set_gz_threshold"))
async def set_gz_threshold(callback_query: CallbackQuery, state: FSMContext):
    user = callback_query.from_user
    logger.info(f"User with id {user.id} is setting Gazprombank threshold")

    await state.update_data(service_name="gazprombank")
    await state.set_state(ThresholdState.waiting_for_value)
    message = await callback_query.message.edit_text(
        "Please send me the new Gazprombank threshold value (a number)."
    )
    await state.update_data(last_message_id=message.message_id)
    await callback_query.answer()


@notification_router.callback_query(
    MyCallback.filter(F.action == "set_google_threshold")
)
async def set_google_threshold(callback_query: CallbackQuery, state: FSMContext):
    user = callback_query.from_user
    logger.info(f"User with id {user.id} is setting Google threshold")

    await state.update_data(service_name="google")
    await state.set_state(ThresholdState.waiting_for_value)
    message = await callback_query.message.edit_text(
        "Please send me the new Google threshold value (a number)."
    )
    await state.update_data(last_message_id=message.message_id)
    await callback_query.answer()


@notification_router.callback_query(MyCallback.filter(F.action == "set_cbrf_threshold"))
async def set_cbrf_threshold(callback_query: CallbackQuery, state: FSMContext):
    user = callback_query.from_user
    logger.info(f"User with id {user.id} is setting CBR threshold")

    await state.update_data(service_name="cbrf")
    await state.set_state(ThresholdState.waiting_for_value)
    message = await callback_query.message.edit_text(
        "Please send me the new Central Bank of Russia threshold value (a number)."
    )
    await state.update_data(last_message_id=message.message_id)
    await callback_query.answer()


@notification_router.message(StateFilter(ThresholdState.waiting_for_value))
async def receive_threshold_input(message: Message, state: FSMContext, bot: Bot):
    user = message.from_user
    user_data = await state.get_data()
    last_message_id = user_data.get("last_message_id")
    await bot.delete_message(chat_id=user.id, message_id=last_message_id)
    try:
        threshold_value = float(message.text)
        if threshold_value < 0:
            raise ValueError
    except ValueError:
        message = await message.reply("Please send a valid number for the threshold.")
        await state.update_data(last_message_id=message.message_id)
        return

    service = await state.get_data()
    service_name = service.get("service_name")

    logger.info(f"service name: {service_name}; value: {threshold_value}")
    async with async_session() as session:
        if service_name == "gazprombank":
            await update_user_threshold(
                session,
                UserThresholdUpdateSchema(id=user.id, gz_threshold=threshold_value),
            )
        elif service_name == "google":
            await update_user_threshold(
                session,
                UserThresholdUpdateSchema(id=user.id, google_threshold=threshold_value),
            )
        elif service_name == "cbrf":
            await update_user_threshold(
                session,
                UserThresholdUpdateSchema(id=user.id, cbrf_threshold=threshold_value),
            )

    # Fetch updated threshold values
    async with async_session() as session:
        user_data = await get_user_by_id(session, user.id)
        if user_data:
            threshold_text = (
                f"Gazprombank Threshold: {user_data.gz_threshold}\n"
                f"Google Threshold: {user_data.google_threshold}\n"
                f"CBR Threshold: {user_data.cbrf_threshold}"
            )

            await message.answer(
                f"Thresholds updated:\n\n{threshold_text}\n\n"
                "Select a service to set the notification threshold:",
                reply_markup=get_threshold_keyboard(),
            )

    await state.clear()
