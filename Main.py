import os
import asyncio
import logging
from aiohttp import web
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from google import genai

BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
ai_client = genai.Client(api_key=GEMINI_API_KEY)

class StudioStates(StatesGroup):
    waiting_for_topic = State()

def get_menu():
    buttons = [
        [KeyboardButton(text="🎬 Ssenariy & Promt Studio")],
        [KeyboardButton(text="👤 Profil & Balans")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

@dp.message(CommandStart())
async def start_handler(message: Message):
    await message.answer(
        f"Salom, {message.from_user.first_name}! 🎬\n\n"
        "Mobilograflar uchun AI Studio botiga xush kelibsiz!",
        reply_markup=get_menu()
    )

@dp.message(F.text == "🎬 Ssenariy & Promt Studio")
async def ask_topic(message: Message, state: FSMContext):
    await message.answer("Qanday video olmoqchisiz? Mavzu va mahsulot nomini yozing:")
    await state.set_state(StudioStates.waiting_for_topic)

@dp.message(StudioStates.waiting_for_topic)
async def make_scenario(message: Message, state: FSMContext):
    wait_msg = await message.answer("⏳ AI ssenariy va promtlarni tayyorlamoqda...")
    prompt = (
        "Siz mobilograflar uchun professional visual-direktorsiz. "
        "Ushbu mavzu bo'yicha Reels uchun kadrlar rejasi va "
        "AI video generatorlar (Luma, Kling, Runway) uchun inglizcha promtlar yozib bering:\n\n"
        f"Mavzu: {message.text}"
    )
    response = ai_client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    await wait_msg.delete()
    await message.answer(response.text)
    await state.clear()

@dp.message(F.text == "👤 Profil & Balans")
async def profile(message: Message):
    await message.answer(f"Sizning ID: `{message.from_user.id}`\nBalans: 10 ta bepul kredit", parse_mode="Markdown")

async def handle_ping(request):
    return web.Response(text="Bot ishlamoqda!")

async def start_web_server():
    app = web.Application()
    app.router.add_get('/', handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.getenv("PORT", 8080))
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()

async def main():
    await start_web_server()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

