import datetime
import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from infrastructure.database.models import Question, User
from infrastructure.database.repo.requests import RequestsRepo
from tgbot.config import load_config
from tgbot.filters.topic import IsTopicMessageWithCommand
from tgbot.keyboards.group.main import dialog_quality_duty_kb, FinishedQuestion
from tgbot.keyboards.user.main import dialog_quality_specialist_kb
from tgbot.misc import dicts
from tgbot.services.logger import setup_logging
from tgbot.services.scheduler import (
    stop_inactivity_timer,
)

topic_cmds_router = Router()

config = load_config(".env")

setup_logging()
logger = logging.getLogger(__name__)


@topic_cmds_router.message(IsTopicMessageWithCommand("end"))
async def end_q_cmd(message: Message, user: User, repo: RequestsRepo):
    question: Question = await repo.questions.get_question(
        topic_id=message.message_thread_id
    )

    if question is not None:
        if question.Status != "closed" and question.TopicDutyFullname == user.FIO:
            # Останавливаем таймер неактивности
            stop_inactivity_timer(question.Token)

            await repo.questions.update_question_status(
                token=question.Token, status="closed"
            )
            await repo.questions.update_question_end(
                token=question.Token, end_time=datetime.datetime.now()
            )

            if question.QualityDuty is not None:
                if question.QualityDuty:
                    await message.bot.send_message(
                        chat_id=config.tg_bot.forum_id,
                        message_thread_id=question.TopicId,
                        text=f"""<b>🔒 Вопрос закрыт</b>

👮‍♂️ Старший: <b>{question.TopicDutyFullname}</b>
👍 Специалист <b>не мог решить вопрос самостоятельно</b>""",
                        reply_markup=dialog_quality_duty_kb(
                            token=question.Token,
                            show_quality=None,
                            allow_return=question.AllowReturn,
                        ),
                    )
                else:
                    await message.bot.send_message(
                        chat_id=config.tg_bot.forum_id,
                        message_thread_id=question.TopicId,
                        text=f"""<b>🔒 Вопрос закрыт</b>
                        
👮‍♂️ Старший: <b>{question.TopicDutyFullname}</b>
👎 Специалист <b>мог решить вопрос самостоятельно</b>""",
                        reply_markup=dialog_quality_duty_kb(
                            token=question.Token,
                            show_quality=None,
                            allow_return=question.AllowReturn,
                        ),
                    )
            else:
                await message.bot.send_message(
                    chat_id=config.tg_bot.forum_id,
                    message_thread_id=question.TopicId,
                    text=f"""<b>🔒 Вопрос закрыт</b>
                    
👮‍♂️ Старший: <b>{question.TopicDutyFullname}</b>
Оцени, мог ли специалист решить его самостоятельно""",
                    reply_markup=dialog_quality_duty_kb(
                        token=question.Token,
                        show_quality=True,
                        allow_return=question.AllowReturn,
                    ),
                )

            await message.bot.edit_forum_topic(
                chat_id=config.tg_bot.forum_id,
                message_thread_id=question.TopicId,
                name=question.Token,
                icon_custom_emoji_id=dicts.topicEmojis["closed"],
            )
            await message.bot.close_forum_topic(
                chat_id=config.tg_bot.forum_id, message_thread_id=question.TopicId
            )

            employee: User = await repo.users.get_user(
                fullname=question.EmployeeFullname
            )

            await message.bot.send_message(
                chat_id=employee.ChatId,
                text="<b>🔒 Вопрос закрыт</b>",
                reply_markup=ReplyKeyboardRemove(),
            )

            await message.bot.send_message(
                chat_id=employee.ChatId,
                text=f"""Старший <b>{user.FIO}</b> закрыл вопрос
Оцени, помогли ли тебе решить его""",
                reply_markup=dialog_quality_specialist_kb(token=question.Token),
            )

            logger.info(
                f"[Вопрос] - [Закрытие] Пользователь {message.from_user.username} ({message.from_user.id}): Закрыт вопрос {question.Token} со специалистом {question.EmployeeFullname}"
            )
        elif question.Status != "closed" and question.TopicDutyFullname != user.FIO:
            await message.reply("""<b>⚠️ Предупреждение</b>

Это не твой чат!

<i>Твое сообщение не отобразится специалисту</i>""")
            logger.warning(
                f"[Вопрос] - [Закрытие] Пользователь {message.from_user.username} ({message.from_user.id}): Попытка закрытия вопроса {question.Token} неуспешна. Вопрос принадлежит другому дежурному"
            )
        elif question.Status == "closed":
            await message.reply("<b>🔒 Вопрос был закрыт</b>")
            await message.bot.close_forum_topic(
                chat_id=config.tg_bot.forum_id, message_thread_id=question.TopicId
            )
            logger.warning(
                f"[Вопрос] - [Закрытие] Пользователь {message.from_user.username} ({message.from_user.id}): Попытка закрытия вопроса {question.Token} неуспешна. Вопрос уже закрыт"
            )

    else:
        await message.answer("""<b>⚠️ Ошибка</b>

Не удалось найти текущую тему в базе""")
        logger.error(
            f"[Вопрос] - [Закрытие] Пользователь {message.from_user.username} ({message.from_user.id}): Попытка закрытия вопроса неуспешна. Не удалось найти вопрос в базе с TopicId = {message.message_id}"
        )


@topic_cmds_router.message(IsTopicMessageWithCommand("release"))
async def release_q_cmd(message: Message, user: User, repo: RequestsRepo):
    question: Question = await repo.questions.get_question(
        topic_id=message.message_thread_id
    )

    if question is not None:
        if (
            question.TopicDutyFullname is not None
            and question.TopicDutyFullname == user.FIO
        ):
            await repo.questions.update_question_duty(
                token=question.Token, topic_duty=None
            )
            await repo.questions.update_question_status(
                token=question.Token, status="open"
            )

            employee: User = await repo.users.get_user(
                fullname=question.EmployeeFullname
            )

            await message.bot.edit_forum_topic(
                chat_id=config.tg_bot.forum_id,
                message_thread_id=question.TopicId,
                icon_custom_emoji_id=dicts.topicEmojis["open"],
            )
            await message.answer("""<b>🕊️ Вопрос освобожден</b>

Для взятия вопроса в работу напишите сообщение в эту тему""")

            await message.bot.send_message(
                chat_id=employee.ChatId,
                text=f"""<b>🕊️ Старший покинул чат</b>

Старший <b>{user.FIO}</b> освободил вопрос. Ожидай повторного подключения старшего""",
            )
            logger.info(
                f"[Вопрос] - [Освобождение] Пользователь {message.from_user.username} ({message.from_user.id}): Вопрос {question.Token} освобожден"
            )
        elif (
            question.TopicDutyFullname is not None
            and question.TopicDutyFullname != user.FIO
        ):
            await message.reply("""<b>⚠️ Предупреждение</b>

Это не твой чат!

<i>Твое сообщение не отобразится специалисту</i>""")
            logger.warning(
                f"[Вопрос] - [Освобождение] Пользователь {message.from_user.username} ({message.from_user.id}): Попытка закрытия вопроса {question.Token} неуспешна. Вопрос принадлежит другому старшему"
            )
        elif question.TopicDutyFullname is None:
            await message.reply("""<b>⚠️ Предупреждение</b>

Это чат сейчас никем не занят!""")
            logger.warning(
                f"[Вопрос] - [Освобождение] Пользователь {message.from_user.username} ({message.from_user.id}): Попытка освобождения вопроса {question.Token} неуспешна. Вопрос {question.Token} никем не занят"
            )
    else:
        await message.answer("""<b>⚠️ Ошибка</b>

Не удалось найти текущую тему в базе, закрываю""")
        await message.bot.close_forum_topic(
            chat_id=config.tg_bot.forum_id,
            message_thread_id=message.message_thread_id,
        )
        logger.error(
            f"[Вопрос] - [Освобождение] Пользователь {message.from_user.username} ({message.from_user.id}): Попытка освобождения вопроса неуспешна. Не удалось найти вопрос в базе с TopicId = {message.message_thread_id}"
        )


@topic_cmds_router.callback_query(FinishedQuestion.filter(F.action == "release"))
async def release_q_cb(callback: CallbackQuery, repo: RequestsRepo):
    question: Question = await repo.questions.get_question(
        topic_id=callback.message.message_thread_id
    )

    if question is not None:
        await repo.questions.update_question_duty(token=question.Token, topic_duty=None)
        await repo.questions.update_question_status(token=question.Token, status="open")

        await callback.message.answer("""<b>🕊️ Вопрос освобожден</b>

Для взятия вопроса в работу напишите сообщение в эту тему""")
        logger.info(
            f"[Вопрос] - [Освобождение] Пользователь {callback.from_user.username} ({callback.from_user.id}): Вопрос {question.Token} освобожден"
        )
    else:
        await callback.message.answer("""<b>⚠️ Ошибка</b>

Не удалось найти текущую тему в базе, закрываю""")
        await callback.bot.close_forum_topic(
            chat_id=config.tg_bot.forum_id,
            message_thread_id=callback.message.message_thread_id,
        )
        logger.error(
            f"[Вопрос] - [Освобождение] Пользователь {callback.from_user.username} ({callback.from_user.id}): Попытка освобождения вопроса неуспешна. Не удалось найти вопрос в базе с TopicId = {callback.message.message_thread_id}"
        )
