import logging
from io import BytesIO

import pandas as pd
from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery
from numpy.random.mtrand import Sequence

from infrastructure.database.models import Question
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import load_config
from tgbot.filters.admin import AdminFilter
from tgbot.keyboards.admin.main import AdminMenu
from tgbot.keyboards.admin.stats_extract import MonthStatsExtract, extract_kb
from tgbot.services.logger import setup_logging

stats_router = Router()
stats_router.message.filter(AdminFilter())
stats_router.callback_query.filter(AdminFilter())

config = load_config(".env")

setup_logging()
logger = logging.getLogger(__name__)


@stats_router.callback_query(AdminMenu.filter(F.menu == "stats_extract"))
async def extract_stats(callback: CallbackQuery) -> None:
    await callback.message.edit_text(
        f"""<b>📥 Выгрузка статистики</b>

Выгрузка будет содержать вопросы за указанный промежуток времени для направления <b>{config.tg_bot.division}</b>

<i>Выбери период выгрузки используя меню</i>""",
        reply_markup=extract_kb(),
    )
    await callback.answer()


@stats_router.callback_query(MonthStatsExtract.filter(F.menu == "month"))
async def admin_extract_month(
    callback: CallbackQuery,
    callback_data: MonthStatsExtract,
    questions_repo: RequestsRepo,
) -> None:
    month = callback_data.month
    year = callback_data.year

    questions: Sequence[
        Question
    ] = await questions_repo.questions.get_questions_by_month(
        month, year, division=config.tg_bot.division
    )

    data = []
    for question_row in questions:
        question = question_row[0]

        match question.QualityEmployee:
            case None:
                quality_employee = "Нет оценки"
            case True:
                quality_employee = "Хорошо"
            case False:
                quality_employee = "Плохо"
            case _:
                quality_employee = "Неизвестно"

        match question.quality_duty:
            case None:
                quality_duty = "Нет оценки"
            case True:
                quality_duty = "Хорошо"
            case False:
                quality_duty = "Плохо"
            case _:
                quality_duty = "Неизвестно"

        match question.status:
            case "open":
                status = "Открыт"
            case "in_progress":
                status = "В работе"
            case "closed":
                status = "Закрыт"
            case "lost":
                status = "Потерян"
            case "fired":
                status = "Удален"
            case _:
                status = "Закрыт"

        match question.allow_return:
            case True:
                allow_return = "Доступен"
            case False:
                allow_return = "Запрещен"
            case _:
                allow_return = "Неизвестно"

        data.append(
            {
                "Токен": question.token,
                "Специалист": question.employee_fullname,
                "Старший": question.topic_duty_fullname,
                "Текст вопроса": question.QuestionText,
                "Время вопроса": question.StartTime,
                "Время завершения": question.EndTime,
                "Ссылка на БЗ": question.CleverLink,
                "Оценка специалиста": quality_employee,
                "Оценка дежурного": quality_duty,
                "Статус чата": status,
                "Возможность возврата": allow_return,
            }
        )

    if not data:
        await callback.message.answer("Не найдено данных для указанного месяца.")
        return

    # Создаем файл excel в памяти
    df = pd.DataFrame(data)
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(
            writer, sheet_name=f"{config.tg_bot.division} - {month}_{year}", index=False
        )

    excel_buffer.seek(0)

    # Создаем имя файла
    month_names = {
        1: "январь",
        2: "февраль",
        3: "март",
        4: "апрель",
        5: "май",
        6: "июнь",
        7: "июль",
        8: "август",
        9: "сентябрь",
        10: "октябрь",
        11: "ноябрь",
        12: "декабрь",
    }

    filename = (
        f"История вопросов {config.tg_bot.division} - {month_names[month]} {year}.xlsx"
    )

    # Сохраняем файл в буфер
    excel_file = BufferedInputFile(excel_buffer.getvalue(), filename=filename)

    await callback.message.answer_document(
        excel_file, caption=f"{month_names[month]} {year}"
    )

    await callback.answer()
