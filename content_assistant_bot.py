import discord
import os
import requests
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Validate environment variables
if not TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Missing DISCORD_TOKEN or OPENROUTER_API_KEY in environment variables.")

# Initialize client and slash command tree
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = discord.app_commands.CommandTree(client)

@client.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {client.user} and synced slash commands!")

# Slash command to ask coding questions
@tree.command(name="askcode", description="Ask a coding question about Angular, TypeScript, GitHub, etc.")
async def askcode(interaction: discord.Interaction, question: str):
    await interaction.response.defer(thinking=True)
    print(f"🧠 Received question: {question}")

    # Query OpenRouter
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": "https://github.com/YOUR_USERNAME/YOUR_REPO",
        "X-Title": "Content Assistant Bot"
    }

    payload = {
        "model": "qwen/qwen3-30b-a3b-04-28:free",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant for answering coding questions about Angular, TypeScript, GitHub, and similar topics."},
            {"role": "user", "content": question}
        ],
        "temperature": 0.4,
        "max_tokens": 800
    }

    try:
        response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        if response.status_code == 403:
            print("⚠️ Qwen failed with 403. Using fallback model.")
            payload["model"] = "deepseek/deepseek-r1-0528:free"
            response = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=payload)

        if response.status_code != 200:
            await interaction.followup.send(f"❌ Error: API returned {response.status_code}")
            return

        data = response.json()
        answer = data["choices"][0]["message"]["content"].strip()
        await interaction.followup.send(f"🧑‍💻 Answer:\n```{answer}```")

    except Exception as e:
        print("💥 ERROR:", str(e))
        await interaction.followup.send(f"❌ An error occurred: {e}")

client.run(TOKEN)
