import discord
from discord.ext import commands
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("CONTENT_ASSISTANT_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

PRIMARY_MODEL = "qwen/qwen3-30b-a3b-04-28:free"
FALLBACK_MODEL = "deepseek/deepseek-r1-0528:free"
API_URL = "https://openrouter.ai/api/v1/chat/completions"

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
    print(f"{bot.user} is online")

@bot.command(name="ask")
async def ask(ctx, *, prompt: str):
    await ctx.trigger_typing()
    print(f"🧠 Question received: {prompt}")

    # Try primary model
    reply = await query_model(prompt, PRIMARY_MODEL)

    # Fallback if needed
    if reply is None:
        print("❌ Primary model failed. Using fallback.")
        reply = await query_model(prompt, FALLBACK_MODEL)

    await ctx.reply(reply or "Both models failed. Time to cry into your console.")

bot.run(DISCORD_TOKEN)
