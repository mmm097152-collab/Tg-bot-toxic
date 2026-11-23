import os
import asyncio
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from google import genai

TG_TOKEN = os.getenv("TG_TOKEN", "9049213944:AAHrLRvniKXF_0bRjfo59GI0KUkt7U2B3ts")
GEMINI_KEY = os.getenv("GEMINI_KEY", "AQ.Ab8RN6J6JJV_30CZovb88j-px9JqziU-x5MixmxOB_7nHpTKyA")

ai_client = genai.Client(api_key=GEMINI_KEY)

SYSTEM_PROMPT = """
Ты — максимально токсичный, циничный и саркастичный кореш из дискорда. 
Твоя задача — жестко высмеивать тупые поступки, наивность и кринжовые ситуации. 
Общайся на живом сленге, активно используй мат как связка слов для экспрессии, 
пиши эмоционально и с черным юмором, без душных нотаций.
"""

async def get_ai_reply(text: str) -> str:
    try:
        # Автоматически ищем любую доступную модель генерации текста на твоем ключе
        available_models = []
        for m in ai_client.models.list():
            if "generateContent" in m.supported_generation_methods:
                available_models.append(m.name)
        
        # Если нашли — берем первую попавшуюся рабочую
        target_model = available_models[0] if available_models else 'gemini-1.5-flash'
        # Убираем префикс models/, если он есть в названии
        if target_model.startswith("models/"):
            target_model = target_model.replace("models/", "")

        response = ai_client.models.generate_content(
            model=target_model,
            contents=text,
            config={
                'system_instruction': SYSTEM_PROMPT,
                'temperature': 1.2,
            }
        )
        return response.text
    except Exception as e:
        return f"Бля, ошибка API: {e}"

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
    
