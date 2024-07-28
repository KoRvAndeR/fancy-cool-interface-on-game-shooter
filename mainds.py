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
bot.remove_command('help')
request_log_player = []
request_log_enemy = []

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


@bot.command(name='n')
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

# Определение сообщений на разных языках
messages = {
    "ru": {
        "start": "Ты идешь по улице, и видишь развилку. Что будешь делать?\n1. Пойти по тропинке\n2. Развернуться и вернуться домой",
        "stage_1": "Ты вошли в лес грибов с большими шляпками и видите дрочущего монстра. Что будешь делать?\n1. Помочь кончить\n2. Убежать нахуй",
        "stage_2": "После того как монстр кончил он указал тебе странную дорогу.  Что будешь делать?\n1. Пойдешь по странной дороге\n2. Убежать в страхе домой",
        "stage_3": "Ты идешь по тропинке и видишь как 13 гномов ебут барана.  Что будешь делать?\n1. Помочь барашке и избить этих уебков\n2. Резко запрыгнуть на баран и ускакать от них обратно домой",
        "stage_4": "Барашка привел тебя к великому Рамзану Кадырову.  Что будешь делать?\n1. Выслушать его",
        "stage_5": "Вы выслушали его величество и он поручил вам украсать золтую овечку.  Что будешь делать?\n1. Выполнить приказ\n2. Ослушаться и получить наказание",
        "stage_6": "Ты добираешься до скрытой долины под названием 'Пидрильщина'  Что будешь делать?\n1. Найти золотую овечку\n2. Сбежать и сохранить себе жизнь",
        "stage_7": "Ты находишь странный храм который охраняет 15 чеченцев.  Что будешь делать?\n1. Найти вход который никто не охраняет\n2. Побежать на пролом",
        "stage_8": "Ты нашел вход и вошел с черного входа, ты сразу увидел как какойто мужчина обнимает золотую овечку.  Что будешь делать?\n1. Окуратно подойдешь сзади и оглушишь мужчину взять овечку и убежать\n2. Подойдешь сзади и задушишь мужчину взять овечку и убежать",
        "stage_9": "Ты успешно украл овечку но мужчина из последних сил крикнул чечнцам что вы украли его жену.  Что будешь делать?\n1. Побежишь через дорогу которая кишит пауками и прибежишь к царю\n2. Побежишь через дорогу которая кишит бешеными собаками и оставь все себе",
        "end_win": "Поздравляем, вы выиграли!",
        "end_lose": "Конец игры, ты умер."
    },
    "en": {
        "start": "You are walking down the street and come across a fork. What will you do?\n1. Go down the path\n2. Turn around and go home",
        "stage_1": "You enter a mushroom forest with large caps and see a monster masturbating. What will you do?\n1. Help him finish\n2. Run away",
        "stage_2": "After the monster finishes, he points you to a strange path. What will you do?\n1. Follow the strange path\n2. Run away to the large mushrooms",
        "stage_3": "You walk down the path and see 13 gnomes having sex with a ram. What will you do?\n1. Help the ram and beat up the gnomes\n2. Quickly jump on the ram and escape back home",
        "stage_4": "The ram leads you to the great Ramzan Kadyrov. What will you do?\n1. Listen to him",
        "stage_5": "You have listened to his majesty and he has tasked you with capturing a golden sheep. What will you do?\n1. Carry out the order\n2. Disobey and face punishment",
        "stage_6": "You arrive at a hidden valley called 'Pidrilshchina'. What will you do?\n1. Find the golden sheep\n2. Flee and save your life",
        "stage_7": "You find a strange temple guarded by 15 Chechens. What will you do?\n1. Find an unguarded entrance\n2. Charge through",
        "stage_8": "You found the entrance and went in through the back, where you immediately saw a man hugging the golden sheep. What will you do?\n1. Carefully approach from behind, knock out the man, grab the sheep, and run\n2. Approach from behind and strangle the man, grab the sheep, and run",
        "stage_9": "You successfully stole the sheep, but the man, with his last strength, shouted to the Chechens that you stole his wife. What will you do?\n1. Run across the road infested with spiders and get to the king\n2. Run across the road infested with rabid dogs and keep everything for yourself",
        "end_win": "Congratulations, you won!",
        "end_lose": "The game is over, you died."
    }
}


class AdventureGame:
    def __init__(self, language="en"):
        self.stage = 0
        self.language = language
        self.messages = messages

    def start_game(self):
        self.stage = 0
        return self.get_current_stage_message()

    def advance_stage(self, choice):
        print(f"Current stage: {self.stage}, Choice: {choice}")

        if self.stage == 0:
            if choice == "1":
                self.stage = 1
            else:
                return self.end_game()
        elif self.stage == 1:
            if choice == "1":
                self.stage = 2
            else:
                return self.end_game()
        elif self.stage == 2:
            if choice == "1":
                self.stage = 3
            else:
                return self.end_game()
        elif self.stage == 3:
            if choice == "1":
                self.stage = 4
            else:
                return self.end_game()
        elif self.stage == 4:
            if choice == "1":
                self.stage = 5
            else:
                return self.end_game()
        elif self.stage == 5:
            if choice == "1":
                self.stage = 6
            else:
                return self.end_game()
        elif self.stage == 6:
            if choice == "1":
                self.stage = 7
            else:
                return self.end_game()
        elif self.stage == 7:
            if choice == "1":
                self.stage = 8
            else:
                return self.end_game()
        elif self.stage == 8:
            if choice == "1":
                self.stage = 9
            else:
                self.stage = 10
        elif self.stage == 9:
            if choice == "1":
                self.stage = 10
            else:
                return self.end_game()

        if self.stage == 10:
            return self.end_game(win=True)

        print(f"New stage: {self.stage}")
        return self.get_current_stage_message()

    def get_current_stage_message(self):
        stage_messages = {
            0: self.messages[self.language]["start"],
            1: self.messages[self.language]["stage_1"],
            2: self.messages[self.language]["stage_2"],
            3: self.messages[self.language]["stage_3"],
            4: self.messages[self.language]["stage_4"],
            5: self.messages[self.language]["stage_5"],
            6: self.messages[self.language]["stage_6"],
            7: self.messages[self.language]["stage_7"],
            8: self.messages[self.language]["stage_8"],
            9: self.messages[self.language]["stage_9"],
        }
        return stage_messages.get(self.stage, self.messages[self.language]["end_lose"])

    def end_game(self, win=False):
        if win:
            return self.messages[self.language]["end_win"]
        else:
            return self.messages[self.language]["end_lose"]


games = {}  # Словарь для отслеживания текущих игр для каждого игрока

@bot.command(name="start")
async def start(ctx, lang="en"):
    if lang not in messages:
        await ctx.send("Can't find this language. Supported languages are: 'en', 'ru'.")
        return
    game = AdventureGame(language=lang)
    games[ctx.author.id] = game
    await ctx.send(game.start_game())

@bot.command(name="continue")
async def continue_game(ctx, choice):
    game = games.get(ctx.author.id)
    if game:
        response = game.advance_stage(choice)
        await ctx.send(response)
    else:
        await ctx.send("You haven't started a game yet. Use $start to begin.")




games = {}  # Словарь для хранения игр пользователей

import random
games = {}  # Словарь для хранения игр пользователей

class ShooterGame:
    def __init__(self, player_health=105, enemy_health=100, enemy_potions=1):
        self.player_health = player_health
        self.enemy_health = enemy_health
        self.player_potions = 2
        self.enemy_potions = enemy_potions
        self.request_log_enemy = []
        self.request_log_player = []

    def attack(self):
        return f"📃Battle results:"
    def dodge(self):
        if random.random() < 0.5:
            return "You successfully dodged the enemy's attack!"
        else:
            enemy_damage = random.randint(5, 25)
            self.player_health -= enemy_damage
            damage_embed = discord.Embed(description=f"**-{enemy_damage} damage**", color=discord.Color.red())
            health_embed = discord.Embed(description=f"**Your {self.player_health} hp**", color=discord.Color.green())
            text = "**🏹The enemy attacked and inflicted:**"
            text_1 = "**🔋Your current health:**"
            return "You failed to dodge! The enemy hit you!", text, damage_embed,text_1, health_embed



    def use_potion(self):
        if self.player_potions > 0:
            heal_amount = random.randint(15, 30)
            self.player_health += heal_amount
            self.player_potions -= 1
            heal_embed = discord.Embed(description=f"**+{heal_amount} hp**", color=discord.Color.green())
            potions_embed = discord.Embed(description=f"**{self.player_potions} potions remaining**", color=discord.Color.green())
            heal_text = "You used the potion and restored:"
            heal_text_2 = "Potions remaining:"
            return heal_text, heal_embed, heal_text_2, potions_embed
        else:
            return "You have no potions left!", None, None, None

    def enemy_use_potion(self):
        self.enemy_health += 10
        self.enemy_potions -= 1
        text = "The enemy used a potion and restored 10 hp."
        text_2 = f"Enemy potions remaining: {self.enemy_potions}"
        heals = discord.Embed(description=f"**+10 hp**", color=discord.Color.red())
        potions_embed = discord.Embed(description=text_2, color=discord.Color.green())
        return text, heals, text_2, potions_embed

@bot.command(name="start_shooter")
async def start_shooter(ctx):
    if ctx.author.id in games:
        await ctx.send("🔄You already have an ongoing game.")
    else:
        games[ctx.author.id] = ShooterGame()
        await ctx.send("🎌Game has started! Use the *$attack* command to attack the enemy.")


@bot.command(name="attack")
async def attack(ctx):
    if ctx.author.id not in games:
        await ctx.send("📛First, start the game using the *$start_shooter* command.")
        return

    game = games[ctx.author.id]
    result = game.attack()
    await ctx.send(result)

    if game.enemy_health <= 0:
        win_embed = discord.Embed(description="🎉**You won the game!**", color=discord.Color.green())
        await ctx.send(embed=win_embed)
        del games[ctx.author.id]
        return
    if game.player_health <= 0:
        lost_embed = discord.Embed(description="😥**You lost the game!**", color=discord.Color.red())
        await ctx.send(embed=lost_embed)
        del games[ctx.author.id]
        return

    # Enemy's turn
    if game.enemy_potions > 0 and random.random() < 0.3:
        text, heals, text_2, potions_embed = game.enemy_use_potion()
        await ctx.send(text)
        await ctx.send(embed=heals)
        await ctx.send(text_2)
        await ctx.send(embed=potions_embed)
    else:
        enemy_damage = random.randint(5, 25)
        player_damage = random.randint(5, 25)
        damage_embed = discord.Embed(description=f"**-{enemy_damage} damage**", color=discord.Color.red())
        damage_player_embed = discord.Embed(description=f"**{player_damage} hp's**", color=discord.Color.blue())
        game.player_health -= enemy_damage
        game.enemy_health -= player_damage
        health_embed = discord.Embed(description=f"**Your {game.player_health} hp | Enemy {game.enemy_health} hp's**", color=discord.Color.green())
        await ctx.send("**🏹The enemy attacked and inflicted:**")
        await ctx.send(embed=damage_embed)
        await ctx.send("**🔪You have inflicted to your enemy:**")
        await ctx.send(embed=damage_player_embed)
        await ctx.send("**🔋Current health:**")
        await ctx.send(embed=health_embed)

        if game.player_health < 0:
                lost_embed = discord.Embed(description="😥**You lost the game!**", color=discord.Color.red())
                await ctx.send(embed=lost_embed)
                del games[ctx.author.id]
                return
        elif game.enemy_health <= 0:
                win_embed = discord.Embed(description="🎉**You won the game!**", color=discord.Color.green())
                await ctx.send(embed=win_embed)
                del games[ctx.author.id]
                return

@bot.command(name="use_potion")
async def use_potion(ctx):
    if ctx.author.id not in games:
        await ctx.send("📛First, start the game using the *$start_shooter* command.")
        return
    game = games[ctx.author.id]
    heal_text, heal_embed, heal_text_2, potions_embed = game.use_potion()
    await ctx.send(heal_text)
    if heal_embed:
        await ctx.send(embed=heal_embed)
    if heal_text_2:
        await ctx.send(heal_text_2)
    if potions_embed:
        await ctx.send(embed=potions_embed)

@bot.command(name="dodge")
async def dodge(ctx):
    if ctx.author.id not in games:
        await ctx.send("📛First, start the game using the *$start_shooter* command.")
        return
    game = games[ctx.author.id]
    result = game.dodge()
    if isinstance(result, tuple):
        message, damage_embed, health_embed = result
        await ctx.send(message)
        await ctx.send(embed=damage_embed)
        await ctx.send(embed=health_embed)
    else:
        await ctx.send(result)


@bot.command(name="flip")
async def flip(ctx):
    outcome = random.choice(["Heads", "Tails"])
    await ctx.send(outcome)


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



@bot.command(name='help')
async def help_command(ctx):
    embed = discord.Embed(
            title="💾Main information abt bot:",
        description=(
            "ㅤMain prefix is {$} below you can find out many commands:"),color=0x009dff)

    embed.add_field(
        name="🎶Music commands:",
        value="ㅤ$p | $n | $l | $s",
        inline=False
    )

    embed.add_field(
        name="🎈Funny commands to play with ur friend:",
        value="ㅤ$start\n"
              "ㅤ$flip\n"
              "ㅤ$start ru\n"
              "ㅤ$continue\n"
              "ㅤ$start_shooter\n"
              "ㅤ$attack\n"
              "ㅤ$use_potion\n"
              "ㅤ$dodge",
        inline=False
    )
    embed.add_field(
        name="📋 Info Abt Us:",
        value=" ㅤInfo abt our group and process of doing bot: [bot page](https://rt.pornhub.com/)\n",
        inline=False
    )
    embed.set_footer(text="📜for detailed information send: $info_help")
    await ctx.send(embed=embed)

@bot.command(name='help_info')
async def help_info(ctx):
    embed = discord.Embed(
        title="🔮Detailed information abt bot:",
        description=(
            "ㅤEvery command has his own usability and this is info ant them:"), color=0x0091eb)

    embed.add_field(
        name="🎼Music info commands:",
        value="ㅤ$p - Send this to play your track then space and your url to youtube video\n"
              "ㅤ$n - Send this to skip your track\n"
              "ㅤ$s - Send this to stop ur track\n"
              "ㅤ$l - Send this to just leave bot from vc",
        inline=False
    )
    embed.add_field(
        name="🎈Funny game's detailed info:",
        value="ㅤ$start - Command to start a game on based EN language\n"
              "ㅤ$start ru - Command to start a game on RU language\n"
              "ㅤ$continue - Command to continue your adventure in game\n"
              "ㅤ$start_shooter - Command to start play shooter text game\n"
              "ㅤ$attack - Command to attack your enemy's in shooter game\n"
              "ㅤ$use_potion - Command to use your poison in shooter game\n"
              "ㅤ$dodge - Command to dodge enemy's in shooter game\n"
              "ㅤ$flip - Command to start play common game {Heads and Tails}",
        inline=False
    )
    embed.set_footer(text="ㅤ©prod by: cywwee, korvander, artimok")
    await ctx.send(embed=embed)


bot.run(token_ds)