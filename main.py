import os

import openai
import discord

from dotenv import load_dotenv

load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Set Discord bot token
intents = discord.Intents.all()
client = discord.Client(intents=intents)


class ChatGPT:
    def __init__(self, system_setting):
        self.system = {"role": "system", "content": system_setting}
        self.input_list = [self.system]
        self.logs = []

    def input_message(self, input_text):
        self.input_list.append({"role": "user", "content": input_text})
        result = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=self.input_list,
        )
        self.logs.append(result)
        self.input_list.append(
            {"role": "assistant", "content": result.choices[0].message.content}
        )


@client.event
async def on_ready():
    print("起動完了")


@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!h"):
        question = message.content[3:]
        api = ChatGPT(system_setting="あなたはアシスタントです。会話を開始します。")
        api.input_message(question)
        answer = api.input_list[-1]["content"]
        await message.channel.send(answer)


if __name__ == "__main__":
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
