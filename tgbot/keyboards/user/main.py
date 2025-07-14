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


class ReturnQuestion(CallbackData, prefix='return_q'):
    action: str
    token: str = None


# Основная клавиатура для команды /start
def user_kb(is_role_changed: bool = False) -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(text="🤔 Задать вопрос", callback_data=MainMenu(menu="ask").pack()),
            InlineKeyboardButton(text="🔄 Возврат вопроса", callback_data=MainMenu(menu="return").pack()),
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
                InlineKeyboardButton(text="👍 Да",
                                     callback_data=QuestionQualitySpecialist(answer=True, token=token).pack()),
                InlineKeyboardButton(text="👎 Нет",
                                     callback_data=QuestionQualitySpecialist(answer=False, token=token).pack()),
            ],
            [
                InlineKeyboardButton(text="🔄 Вернуть вопрос",
                                     callback_data=QuestionQualitySpecialist(return_dialog=True, token=token).pack())
            ], [
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
                InlineKeyboardButton(text="🔄 Вернуть вопрос",
                                     callback_data=QuestionQualityDuty(return_dialog=True, token=token).pack())
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
                InlineKeyboardButton(text="🤔 Новый вопрос", callback_data=MainMenu(menu="ask").pack()),
                InlineKeyboardButton(text="🔄 Вернуть вопрос",
                                     callback_data=QuestionQualitySpecialist(return_dialog=True, token=token).pack())
            ],
            [
                InlineKeyboardButton(text="🏠 Главное меню", callback_data=MainMenu(menu="main").pack())
            ]
        ]
    else:
        buttons = [
            [
                InlineKeyboardButton(text="🔄 Вернуть вопрос",
                                     callback_data=QuestionQualityDuty(return_dialog=True, token=token).pack())
            ]
        ]

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=buttons,
    )
    return keyboard


def questions_list_kb(questions) -> InlineKeyboardMarkup:
    """Клавиатура со списком последних вопросов"""
    buttons = []

    for question in questions:
        # Используем EndTime вместо StartTime для отображения времени закрытия
        date_str = question.EndTime.strftime("%d.%m.%Y %H:%M") if question.EndTime else question.StartTime.strftime("%d.%m.%Y")
        buttons.append([
            InlineKeyboardButton(
                text=f"📅 {date_str}",
                callback_data=ReturnQuestion(action="show", token=question.Token).pack()
            )
        ])

    buttons.append([
        InlineKeyboardButton(text="↩️ Назад", callback_data=MainMenu(menu="main").pack())
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def question_confirm_kb(token: str) -> InlineKeyboardMarkup:
    """Клавиатура для подтверждения возврата вопроса"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Да, вернуть",
                                 callback_data=ReturnQuestion(action="confirm", token=token).pack()),
        ],
        [
            InlineKeyboardButton(text="↩️ Назад", callback_data=MainMenu(menu="return").pack())
        ]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
