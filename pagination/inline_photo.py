from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from pagination.callback_datas import photo_callback


def get_photo_keyboard(photo_dict: dict, page: int = 0) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    has_next_page = len(photo_dict) > page + 1

    if page != 0:
        keyboard.add(
            InlineKeyboardButton(
                text="< Назад",
                callback_data=photo_callback.new(page=page - 1)
            )
        )

    keyboard.add(
        InlineKeyboardButton(
            text=f"• {page + 1}",
            callback_data="dont_click_me"
        )
    )

    if has_next_page:
        keyboard.add(
            InlineKeyboardButton(
                text="Вперёд >",
                callback_data=photo_callback.new(page=page + 1)
            )
        )

    return keyboard
