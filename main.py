import os
import datetime
from pathlib import Path

import boto3
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
        try:
            result = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=self.input_list,
            )
            self.logs.append(result)
            self.input_list.append(
                {"role": "assistant", "content": result.choices[0].message.content}
            )
        except Exception as e:
            print(e)


# class Text2speech:
#     def __init__(self) -> None:
#         pass

#     def text2speech(self, text):
#         self.date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
#         save_path = Path("/tmp/tts1.mp3")

#         response = openai.audio.speech.create(model="tts-1", voice="nova", input=text)
#         response.stream_to_file(save_path)

#         s3 = AmazonS3()
#         s3.upload(save_path)

#         total_str_count = len(text)
#         char_cost = 0.015 / 1000
#         return total_str_count * char_cost


class AmazonS3:
    def __init__(self) -> None:
        self.boto3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION_NAME"),
        )
        self.date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

    def upload(self, file_path):
        self.boto3_client.upload_file(
            file_path, "discord-server", f"text_to_speech/tts1_{self.date}.mp3"
        )

    def download(self):
        self.boto3_client.download_file(
            "discord-server", f"text_to_speech/tts1_{self.date}.mp3", "/tmp/tts1.mp3"
        )


@client.event
async def on_ready():
    print("起動完了")


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.content.startswith("!h"):
        question = message.content[3:]
        api = ChatGPT(system_setting="あなたはアシスタントです。会話を開始します。")
        api.input_message(question)
        answer = api.input_list[-1]["content"]
        await message.channel.send(answer)
    # if message.content.startswith("!読んで"):
    #     question = message.content[4:]
    #     if len(question) > 4096:
    #         await message.channel.send("4096文字以下で入力してください。")
    #         return
    #     api = Text2speech()
    #     cost = api.text2speech(question)
    #     await message.channel.send(
    #         f"今回かかったコストは${cost:.6f}でした。",
    #         file=discord.File("/tmp/tts1.mp3", filename=f"tts1_{question[:15]}.mp3"),
    #     )
    if message.content.startswith("!0"):
        pass


if __name__ == "__main__":
    client.run(os.getenv("DISCORD_BOT_TOKEN"))
