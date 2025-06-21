import discord
import aiohttp
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("CONTENT_ASSISTANT_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

PRIMARY_MODEL = "qwen/qwen3-30b-a3b-04-28:free"
FALLBACK_MODEL = "deepseek/deepseek-r1-0528:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

async def query_model(message_content, model_name):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": message_content}],
        "temperature": 0.4,
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(API_URL, headers=headers, json=payload) as response:
            if response.status == 403:
                return None
            data = await response.json()
            return data["choices"][0]["message"]["content"]

@bot.event
async def on_ready():
    print(f"{bot.user} reporting for nerd duty.")

@bot.slash_command(name="askcode", description="Ask coding questions about Angular, TypeScript, GitHub, etc.")
async def askcode(ctx: discord.ApplicationContext, question: str):
    await ctx.defer()
    print(f"🧠 Slash command received: {question}")

    reply = await query_model(question, PRIMARY_MODEL)
    if reply is None:
        reply = await query_model(question, FALLBACK_MODEL)

    await ctx.respond(reply or "Both models failed. The AI gods are displeased.")

bot.run(DISCORD_TOKEN)
