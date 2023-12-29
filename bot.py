from discord import client, Message
from pathlib import Path
from bs4 import BeautifulSoup
from discord.ext import commands
import aiohttp
import datetime
import random
import requests
import time
import pyfiglet
import typing
import asyncio
import json
import humanize
import psutil
import discord
import subprocess

start_time = time.time()
intents = discord.Intents.default()
last_seen = {}
intents.members = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix=":", intents=discord.Intents.all())

@bot.event
async def on_message(message: Message):
    if message.author == bot.user: return
    num = random.randint(1,7) 
    if num == 1:
        message_split = message.content.split()
        if len(message_split) <= 1:
            return
        rand_word = random.choice(message_split)
        new_message = message.content.replace(rand_word, '<:ZULUL:1134535251239125042>', 1)
        await message.channel.send(new_message)

    if message.author == bot.user: return
    num1 = random.randint(1,12) 
    if num1 == 1:
        message_split = message.content.split()
        emoji = '💩'
        await message.add_reaction(emoji)

    if message.author == bot.user: return
    num2 = random.randint(1,10) 
    if num2 == 1:
        answer = ("нет", "да", "хуйня")
        await message.channel.send(random.choice(answer))

    if message.author == bot.user: return
    num3 = random.randint(1,25) 
    if num3 == 1:
        answer = ("пошёл нахуй", "пидарас", "завали ебало")
        await message.channel.send(random.choice(answer))

    user_id = message.author.id
    content = message.content
    time_ = datetime.datetime.now()
    last_seen[user_id] = (content, time_)
    
    last_seen_str = {k: (v[0], v[1].strftime("%Y-%m-%d %H:%M:%S")) for k, v in last_seen.items()}

    with open("last_seen.json", "w") as f:
        json.dump(last_seen_str, f)

    await bot.process_commands(message)

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name='BASED✅ FREE✅ WHITE✅ SUCKLESS✅ GIGACHAD✅ OPEN-SOURCE✅'))

@bot.command(aliases = ("p",))
async def ping(ctx):
    ram = (psutil.virtual_memory())
    cpu = psutil.cpu_percent()
    if cpu < 10:
        tab = "[|                ]"
    elif cpu < 30:
        tab = "[|||||            ]"
    elif cpu < 50:
        tab = "[|||||||||        ]"
    elif  cpu < 80:
        tab = "[|||||||||||||    ]"
    else:
        tab = "[|||||||||||||||||]"

    uptime = time.time() - start_time
    latency = bot.latency * 1000 
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.reply(f'```Uptime: {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds. \n Ping: {round(latency)} ms \n CPU: {cpu}% {tab}\n  RAM↴ \n	Used: {psutil.virtual_memory()[2]} MB \n	Available: {ram.available / 1024 / 1024 / 1024:.2f} GB \n	Total {ram.total / 1024 / 1024 / 1024:.4} GB```')

@commands.command()
async def calc(ctx: commands.Context):
    expression = ctx.message.content.split(ctx.prefix + ctx.command.name)[1].strip()
    expression = requests.utils.quote(expression)
    url = f'http://api.mathjs.org/v4/?expr={expression}'
    response = requests.get(url)
    data = response.json()
    number = data
    message = f'{number}'
    await ctx.reply(message)

@bot.command(aliases = ("w",))
async def weather(ctx, city: str = None):
    with open("locations.json", "r") as f:
        locations = json.load(f)
    if city is None:
        user_id = ctx.author.name
        if user_id in locations:
            city = locations[user_id]
        else:
            await ctx.reply(f'Please provide a city name or use !set to save your location.')
            return

    api_key = ''
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()

    if data['cod'] != 200:
        await ctx.reply(f'Sorry, I could not find the weather for {city}.')
        return

    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    cloudscover = data['clouds']['all']
    pressure = data['main']['pressure']
    description = data['weather'][0]['description']
    name = data['name']

    embed = discord.Embed(title=f"Current weather in {name}🏢", color=discord.Colour.green())
    embed.add_field(name="Description", value=f"{description}🌤", inline=True)
    embed.add_field(name="", value=f"", inline=False)
    embed.add_field(name="Temperature", value=f"{temp}°C", inline=False)
    embed.add_field(name="", value=f"", inline=False)
    embed.add_field(name="Feels like", value=f"{feels_like}°C", inline=False)
    embed.add_field(name="", value=f"", inline=False)
    embed.add_field(name="Humidity", value=f"{humidity}%", inline=True)
    embed.add_field(name="Air pressure", value=f"{pressure}hPa", inline=True)
    embed.add_field(name="Cloud cover", value=f"{cloudscover}%", inline=True)
    embed.add_field(name="Wind speed", value=f"{wind_speed}m/s", inline=True)
    await ctx.reply(embed=embed)

@bot.command(description="Set default location for weather")
async def set(ctx, city: str):

    with open("locations.json", "r") as f:
        locations = json.load(f)

    user_id = ctx.author.name
    locations[user_id] = city

    with open("locations.json", "w") as f:
        json.dump(locations, f)

    await ctx.reply(f'Your location has been set to {city}.')

def load_locations(self):

    try:
        with open('locations.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {} 

def save_locations(self):
    with open('locations.json', 'w') as f:
        json.dump(self.locations, f)

@bot.command(aliases = ("wi",))
async def wiki(ctx: commands.Context, language, *, search : str):
    url = f'https://{language}.wikipedia.org/api/rest_v1/page/summary/{search}'
    response = requests.get(url)
    data = response.json()

    title = data['titles']['normalized']
    more = data['description']
    link = data['content_urls']['desktop']['page']

    message = f'{title} - {more} | {link}'

    await ctx.reply(message)

@bot.command()
async def spam(ctx, count: int, *message):
    try:
        message = " ".join(message)
    except ValueError:
        return
    for i in range(count):
        await ctx.send(message)


@bot.command(aliases = ("t",))
async def tl(ctx: commands.Context):

    message = [x.strip() for x in ctx.message.content.split("|", maxsplit=2)] 

    target = message[0][len(ctx.prefix + ctx.command.name):] 

    language = message[1] 
        
    language1 = message[2] 

    url = f"https://api.mymemory.translated.net/get?q={target}&langpair={language}|{language1}" 
    response = requests.get(url) 
    data = response.json()
    translatedText = data["responseData"]["translatedText"]
    message = f"{translatedText}."

    await ctx.reply(message)


@bot.command(aliases = ("py",))
@commands.cooldown(1, 5, commands.BucketType.user)
async def pyramid(ctx, emote: str, num: int = 3):
    if num < 1 or num > 20:
        return

    messages = []

    for i in range(1, num + 1):

        message = (emote + " ") * i

        await ctx.send(message)

        messages.append(message)

    for message in reversed(messages[:-1]):
        await ctx.send(message)

@bot.command(aliases = ("re",))
async def remind(ctx):
    try:
        time, message = [x.strip() for x in ctx.message.content.split(maxsplit=2)[1:]]
        seconds = convert(time)
    except ValueError:
        await ctx.reply(f"Please provide a valid time and message.")
        return
    await ctx.reply(f"I will remind you in {time} < {message} >")
    await asyncio.sleep(seconds)
    await ctx.reply(f'{time} ago : < {message} >.')

def convert(time):
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800} 
    unit = time[-1]

    if unit not in time_dict:
        raise ValueError("Invalid time unit.")
    
    value = int(time[:-1])
    return value * time_dict[unit]

@bot.command()
async def site(ctx, site: str):
    url = f'https://sitecheck.sucuri.net/api/v3/?scan={site}'
    response = requests.get(url)
    data = response.json()
    try:
        site = data['site']['final_url']
    except KeyError:
        site = "Please enter a valid website URL. (e.g. www.example.com)"
    try:
        duration = data['scan']['duration']
    except KeyError:
        duration = ""
    try:
        warnings = data['warnings']['scan_failed'][0]['msg']
    except KeyError:
        warnings = "1"

    if warnings == "1":
        message = f'{site}, Scan time = {duration}s. Is available and has no errors.'
    else:
        message = f'{site} Has an error: {warnings} '

    await ctx.reply(message)

@bot.command(aliases = ("u",))  
async def user(ctx, user: typing.Optional[commands.UserConverter] = None):
    if user is None:
        user = ctx.author
    guild = ctx.guild
    member = guild.get_member(user.id)
    embed = discord.Embed()
    embed.title = f"{user.name}#{user.discriminator}"
    embed.description = f"{user.mention}"
    embed.color = discord.Color.random()
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Created at", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    if member is not None:
        embed.add_field(name="Nickname", value=member.nick or "None")
        embed.add_field(name="Joined at", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Roles", value=", ".join(role.name for role in member.roles[1:]) or "None")
    await ctx.reply(embed=embed)

@bot.group()
@commands.has_role("Moderator")
async def role(ctx):
  if ctx.invoked_subcommand is None:
    await ctx.reply("Specify a valid subcommand: list, display, create, delete, give, remove, color, rename")

@role.command()
async def display(ctx, role_name: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:

        await ctx.reply(f"{role_name} not found")
        return
    current_hoist = role.hoist
    new_hoist = not current_hoist
    await role.edit(hoist=new_hoist)
    await ctx.reply(f"Displaying of {role_name} switched to {new_hoist}.")

@role.command()
async def create(ctx, name, color: discord.Color):
  await ctx.guild.create_role(name=name, color=color)
  await ctx.reply(f"Created {name}")

@role.command()
async def delete(ctx, *, name):
  role = discord.utils.get(ctx.guild.roles, name=name)
  if role:
    await role.delete()
    await ctx.reply(f"Deleted {name}")
  else:
    await ctx.reply(f"{name} not found")

@role.command()
async def give(ctx, role: discord.Role, member: discord.Member,):
  await member.add_roles(role)
  await ctx.reply(f"{member.name} now has {role.name} role")

@role.command()
async def remove(ctx, role: discord.Role, *, member: discord.Member, ):
  await member.remove_roles(role)
  await ctx.reply(f"Removed {role.name} from {member.name}")

@role.command()
async def list(ctx):
  rolelist = [role.name for role in ctx.guild.roles] 
  roles = ", \n".join(rolelist)
  await ctx.reply(f"```{roles}```")

@role.command()
async def color(ctx, role: discord.Role, color: discord.Color):
  await role.edit(color=color)
  await ctx.reply(f"Color of {role.name} changed to {color}")

@role.command()
async def rename(ctx, role: discord.Role, *, name: str):
  await role.edit(name=name)
  await ctx.reply(f"Name of {role.name} changed to {name}")

@role.command()
async def move(ctx, role_name: str, direction: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        await ctx.reply(f"Role not found.")
        return
    if direction not in ["top", "bottom"]:
        await ctx.reply(f'Invalid direction. Use "top" and "bottom".')
        return
    bot_member = guild.get_member(bot.user.id)
    bot_top_role = bot_member.top_role
    if direction == "top":
        position = bot_top_role.position - 1
    else:
        position = min(r.position for r in guild.roles if not r.managed) + 1
    await role.edit(position=position)
    await ctx.reply(f"{role_name} moved to {direction}.")

@bot.group()
@commands.has_role("Moderator")
async def member(ctx):
  if ctx.invoked_subcommand is None:
    await ctx.reply("Please specify a valid subcommand: mute, ban, unban, kick")

@member.command()
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} has been banned for {reason}.")

@member.command()
async def unban(ctx, id: int):
    user = await client.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.send(f"{user} has been unbanned.")

@member.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} has been kicked.')

@member.command() 
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member):
  role = discord.utils.get(ctx.guild.roles, name="Muted")
  guild = ctx.guild
  if role not in guild.roles:
    perms = discord.Permissions(send_messages=False, speak=False)
    await guild.create_role(name="Muted", permissions=perms)
    await member.add_roles(role)
    await ctx.reply('Role "Muted" has been created and assigned to {member}')
  else:
    await member.add_roles(role)
    await ctx.reply(f"{member} has been muted")

@bot.command(aliases = ("stalk",))
async def ls(ctx, user: discord.Member):
    with open("last_seen.json", "r") as f:
        last_seen = json.load(f)

    user_id = str(user.id) 
    
    if user_id in last_seen:
        content, time = last_seen[user_id]
        time_dt = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        delta = now - time_dt
        delta_str = humanize.precisedelta(delta)
        delta_str = delta_str.replace(",", "").strip() + " ago"
        await ctx.reply(f"[{delta_str}] {user.mention} : {content}")
    else:
        await ctx.reply(f"There's no messages from {user.mention}.")

@bot.command()
async def cmd(ctx: commands.Context, *, name):
    if ctx.author.name == "v1ss0nd":
        try: 
            message = subprocess.getstatusoutput(f'{name}')
            await ctx.send(f"```{message}```")
        except Exception as e:   
            await ctx.send(f"{e}")
        return
    else:
        return

@bot.command()
async def join(context: commands.Context) -> discord.VoiceProtocol:
    if context.author.voice is None:
        return await context.reply("You are not in voice channel.")
    channel = context.author.voice.channel

    client = context.voice_client
    if client is None:
        client = await channel.connect()
    if client.is_connected() and client.channel != channel:
        await client.move_to(channel)

    return client

@bot.command()
async def leave(ctx):
  guild = ctx.guild
  if guild.voice_client is not None:
    await guild.voice_client.disconnect()
    await ctx.reply(f"Left from the voice channel")
  else:
    await ctx.reply("I am not in any voice channel.")

@bot.command()
async def stop(ctx):
  vc = ctx.voice_client
  if vc and vc.is_connected():
    vc.stop()
    await ctx.reply("Stopped playing")
  else:
    await ctx.reply("Nothing playing rn")

@bot.command()
async def playfile(context: commands.Context, repeat: bool = False) -> None:
    client = await join(context)

    attachment = context.message.attachments[0]
    filename = await download_audio(attachment.url)

    client.loop = repeat
    client.play(discord.FFmpegPCMAudio(filename))
    await context.reply(f"Playing __{attachment.filename.replace('_', ' ')}__")

async def download_audio(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.read()
            extension = response.url.suffix

    filename = f"audio{random.randint(1000, 9999)}{extension}"

    with open(filename, "wb") as file:
        file.write(content)

    return filename

bot.run('')
