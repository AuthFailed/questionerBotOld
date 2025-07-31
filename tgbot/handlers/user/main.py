import logging

from aiogram import Router
from aiogram.types import Message

from tgbot.config import load_config
from tgbot.services.logger import setup_logging

user_router = Router()

config = load_config(".env")

setup_logging()
logger = logging.getLogger(__name__)


@user_router.message()
async def main(
    message: Message,
):
    await message.answer(f"""Привет, <b>@{message.from_user.username}</b>!
        
Этот бот устарел, переходи в нового: @gipERquestioner_bot""")
