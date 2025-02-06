from aiogram import types, Router, Bot, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import aiohttp
import ujson
import asyncio
from telegram.keyboards.admin import approve_mailing_inline
from db import database
from telegram.routes.admin.mailing.sender import MailingTask
from db.models import User

mailing_router = Router(name=__name__)


