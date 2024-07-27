import discord
from discord.ext import commands
import random
import json
import os
import yt_dlp as youtube_dl
import asyncio
import deepl

try:
    with open('config.json', 'r', encoding='utf-8') as file:
        config = json.load(file)
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(f"failed: {e}")
    exit(1)

token_ds = config["token_ds"]
DEEPL_API_KEY = config["DEEPL_API_KEY"]
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents, command_prefix="$")

# cywe func begin

# configuration for yt-dlp
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}
ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class MusicPlayer:
    def __init__(self):
        self.queue = []
        self.is_playing = False

    async def from_url(self, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return filename

    async def play_next(self, ctx):
        if len(self.queue) > 0:
            self.is_playing = True
            url = self.queue.pop(0)
            filename = await self.from_url(url, stream=True)
            ctx.voice_client.play(discord.FFmpegPCMAudio(executable="ffmpeg", source=filename, **ffmpeg_options), after=lambda e: self.bot.loop.create_task(self.play_next(ctx)))
            await ctx.send(f'Now playing: {url}')
        else:
            self.is_playing = False

    async def add_to_queue(self, ctx, url):
        self.queue.append(url)
        if not self.is_playing:
            await self.play_next(ctx)
        else:
            await ctx.send(f'Queued: {url}')


music_player = MusicPlayer()


@bot.command(name='p')
async def play(ctx, url):
    if not ctx.voice_client:
        if not ctx.message.author.voice:
            await ctx.send("You're not currently in a voice channel")
            return
        channel = ctx.message.author.voice.channel
        await channel.connect()
    await music_player.add_to_queue(ctx, url)


@bot.command(name='l')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()


@bot.command(name='s')
async def stop(ctx):
    if ctx.voice_client:
        ctx.voice_client.stop()
        music_player.queue = []
        music_player.is_playing = False

# korvander's func begin


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    await bot.process_commands(message)

    if bot.user.mentioned_in(message):
        random_response = random.choice(config["responses"])
        await message.reply(random_response)

    elif "слава украине" in message.content.lower():
        await message.reply("в составе РОССИИ!!!")

    elif "слава россии" in message.content.lower():
        await message.reply("Героям Слава!!")

    elif "ИДИ НАХУЙ" in message.content.lower():
        await message.reply("Своим помахуй")
    else:
        pass
# korvander's func finish



translator = deepl.Translator(DEEPL_API_KEY)
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command(name='tr')
async def translate(ctx, lang_to: str, *, text: str):
    supported_langs = ["BG", "CS", "DA", "DE", "EL", "EN", "ES", "ET", "FI", "FR", "HU", "ID", "IT", "JA", "KO", "LT", "LV", "NB", "NL", "PL", "PT", "RO", "RU", "SK", "SL", "SV", "TR", "UK", "ZH", "AR"]
    lang_to = lang_to.upper()
    if lang_to not in supported_langs:
        await ctx.send(f"Ошибка: Язык '{lang_to}' не поддерживается. Пожалуйста, используйте один из следующих языков: {', '.join(supported_langs)}")
        return
    try:
        result = translator.translate_text(text, target_lang=lang_to)
        await ctx.send(result.text)
    except Exception as e:
        await ctx.send(f"Ошибка: {str(e)}")


bot.run(token_ds)