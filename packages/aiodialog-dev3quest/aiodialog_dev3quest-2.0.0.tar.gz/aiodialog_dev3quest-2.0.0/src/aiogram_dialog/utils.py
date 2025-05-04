from logging import getLogger
from typing import Optional, Tuple

from aiogram.types import (
    CallbackQuery, Chat, ChatMemberUpdated, Message, User,
)

from aiogram_dialog.api.entities import (
    ChatEvent, DialogUpdateEvent, MediaId, NewMessage,
)

logger = getLogger(__name__)

CB_SEP = "\x1D"


def get_chat(event: ChatEvent) -> Chat:
    if isinstance(event, (Message, DialogUpdateEvent, ChatMemberUpdated)):
        return event.chat
    elif isinstance(event, CallbackQuery):
        if not event.message:
            return Chat(id=event.from_user.id, type="")
        return event.message.chat


def is_chat_loaded(chat: Chat) -> bool:
    """
    Check if chat is correctly loaded from telegram.

    For internal events it can be created with no data inside as a FakeChat
    """
    return getattr(chat, "fake", False)


def is_user_loaded(user: User) -> bool:
    """
    Check if user is correctly loaded from telegram.

    For internal events it can be created with no data inside as a FakeUser
    """
    return getattr(user, "fake", False)


def get_media_id(message: Message) -> Optional[MediaId]:
    media = (
        message.audio or
        message.animation or
        message.document or
        (message.photo[-1] if message.photo else None) or
        message.video
    )
    if not media:
        return None
    return MediaId(
        file_id=media.file_id,
        file_unique_id=media.file_unique_id,
    )


def intent_callback_data(
        intent_id: str, callback_data: Optional[str],
) -> Optional[str]:
    if callback_data is None:
        return None
    prefix = intent_id + CB_SEP
    if callback_data.startswith(prefix):
        return callback_data
    return prefix + callback_data


def add_indent_id(message: NewMessage, intent_id: str):
    if not message.reply_markup:
        return
    for row in message.reply_markup.inline_keyboard:
        for button in row:
            button.callback_data = intent_callback_data(
                intent_id, button.callback_data,
            )


def remove_indent_id(callback_data: str) -> Tuple[Optional[str], str]:
    if CB_SEP in callback_data:
        intent_id, new_data = callback_data.split(CB_SEP, maxsplit=1)
        return intent_id, new_data
    return None, callback_data
