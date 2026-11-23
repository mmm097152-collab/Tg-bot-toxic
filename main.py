import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from openai import OpenAI

TG_TOKEN = os.getenv("TG_TOKEN", "9049213944:AAHrLRvniKXF_0bRjfo59GI0KUkt7U2B3ts")
# Твой найденный ключ NIM
NVIDIA_KEY = os.getenv("NVIDIA_KEY", "SxgaOnbaZhPdd1ODjMdwEBgEZgZCDa2h")

# Клиент настроен на эндпоинт NVIDIA NIM
client = OpenAI(
    api_key=NVIDIA_KEY,
    base_url="https://integrate.api.nvidia.com/v1"
)

SYSTEM_PROMPT = """
Ты — максимально токсичный, циничный и саркастичный кореш из дискорда. 
Твоя задача — жестко высмеивать тупые поступки, наивность и кринжовые ситуации. 
Общайся на живом сленге, активно используй мат как связка слов для экспрессии, 
пиши эмоционально и с черным юмором, без душных нотаций.
"""

async def get_ai_reply(text: str) -> str:
    try:
        response = client.chat.completions.create(
            # Модель из каталога NVIDIA NIM (например, Llama 3 или другая доступная)
            model="meta/llama-3.1-70b-instruct",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text}
            ],
            temperature=1.2,
            max_tokens=512,
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Бля, ошибка NVIDIA NIM API: {e}"

tg_bot = Bot(token=TG_TOKEN)
dp = Dispatcher()

@dp.message(F.text)
async def tg_handler(msg: types.Message):
    if msg.text.startswith("/"):
        return
    reply = await get_ai_reply(msg.text)
    await msg.reply(reply)

async def handle_ping(request):
    return web.Response(text="Бот пашет!")

async def start_web_server():
    app = web.Application()
    app.router.add_get("/", handle_ping)
    runner = web.AppRunner(app)
    await runner.setup()
    port = int(os.environ.get("PORT", 10000))
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()

async def main():
    await asyncio.gather(
        start_web_server(),
        dp.start_polling(tg_bot)
    )

if __name__ == "__main__":
    asyncio.run(main())
    
