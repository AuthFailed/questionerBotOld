from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from tgbot.keyboards.admin.main import AdminMenu


class MainMenu(CallbackData, prefix='menu'):
    menu: str


class QuestionQualitySpecialist(CallbackData, prefix='d_quality_spec'):
    answer: bool = False
    token: str = None
    return_dialog: bool = False

class QuestionQualityDuty(CallbackData, prefix='d_quality_duty'):
    answer: bool = False
    token: str = None
    return_dialog: bool = False


# Основная клавиатура для команды /start
def user_kb(is_role_changed: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🤔 Задать вопрос", callback_data=MainMenu(menu="ask").pack()),
            InlineKeyboardButton(text="🔄 Вернуть вопрос", callback_data=MainMenu(menu="ask").pack()),
        ]
    ]

    # Добавляем кнопку сброса если роль измененная
    if is_role_changed:
        buttons.append([
            InlineKeyboardButton(text="♻️ Сбросить роль", callback_data=AdminMenu(menu="reset").pack()),
        ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


# Клавиатура с кнопкой возврата в главное меню
def back_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="↩️ Назад", callback_data=MainMenu(menu="main").pack()),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


# Клавиатура с отменой вопроса и возвратом в главное меню
def cancel_question_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🙅‍♂️ Отменить вопрос", callback_data=MainMenu(menu="main").pack()),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


# Клавиатура с отменой вопроса и возвратом в главное меню
def finish_question_kb() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="✅️ Закрыть вопрос", callback_data=MainMenu(menu="main").pack()),
        ]
    ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


# Клавиатура оценки диалога
def dialog_quality_kb(token: str, role: str = "employee") -> InlineKeyboardMarkup:
    if role == "employee":
        buttons = [
            [
                InlineKeyboardButton(text="👍 Да", callback_data=QuestionQualitySpecialist(answer=True, token=token).pack()),
                InlineKeyboardButton(text="👎 Нет", callback_data=QuestionQualitySpecialist(answer=False, token=token).pack()),
            ],
            [
                InlineKeyboardButton(text="🔄 Вернуть вопрос", callback_data=QuestionQualitySpecialist(return_dialog=True, token=token).pack())
            ],[
                InlineKeyboardButton(text="🤔 Новый вопрос", callback_data=MainMenu(menu="ask").pack())
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data=MainMenu(menu="main").pack())
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="👎 Да",
                                     callback_data=QuestionQualityDuty(answer=False, token=token).pack()),
                InlineKeyboardButton(text="👍 Нет",
                                     callback_data=QuestionQualityDuty(answer=True, token=token).pack()),
            ],
            [
                InlineKeyboardButton(text="🔄 Вернуть вопрос", callback_data=QuestionQualityDuty(return_dialog=True, token=token).pack())
            ]
        ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def closed_dialog_kb(token: str, role: str = "employee") -> InlineKeyboardMarkup:
    if role == "employee":
        buttons = [
            [
                InlineKeyboardButton(text="🔄 Вернуть вопрос", callback_data=QuestionQualitySpecialist(return_dialog=True, token=token).pack())
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data=MainMenu(menu="main").pack())
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="🔄 Вернуть вопрос", callback_data=QuestionQualityDuty(return_dialog=True, token=token).pack())
            ]
        ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard