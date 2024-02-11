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
import asyncio 

# Intents
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.members = True

# Starts the timer for uptime in the "ping" command
start_time = time.time()
# Temporary dictionary for the "ls" command
last_seen = {} 


bot = commands.Bot(command_prefix=":", intents=discord.Intents.all()) # Start and prefix


@bot.event 
async def on_message(message: Message):
    ##
    ## first on_message - with chance of 1 in X replaces random word from last posted message. It does that in all servers and all channels, but you can restrict it to work only in your server.
    ##
    if message.author == bot.user: return
    
    num = random.randint(1,100) # Chance of message
    
    if num == 1:
        message_split = message.content.split() # Get last message
        if len(message_split) <= 1: # If less than 2 words - return
            return

        rand_word = random.choice(message_split) # choice random word to replace
        new_message = message.content.replace(rand_word, '<:ZULUL:1134535251239125042>', 1) # New word
        await message.channel.send(new_message) # Send changed message
    ##
    ## Second on_message - Puts a reaction on last posted message, again, works everywhere.
    ##
    if message.author == bot.user: return
    
    num1 = random.randint(1,100) # Chance of message
    
    if num1 == 1:
        message_split = message.content.split() # Get last message
        emoji = '💩' # Emote (The main thing is it's must to be supported by discord api)
        await message.add_reaction(emoji) # Post reaction
    ##
    ## Third on_message - Sends a random word from the list with chance of 1 in X. (it's all it does fr fr)
    ##
    if message.author == bot.user: return
    num2 = random.randint(1,100) # Chance of message
    
    if num2 == 1:
        answer = ("1", "2", "3", "4") # List of words
        await message.channel.send(random.choice(answer)) # Send the word
    ##
    ##  The same thing but I used it to set a different chance. you can ignore it
    ##
    if message.author == bot.user: return
    num3 = random.randint(1,100) 
    
    if num3 == 1:
        answer = ("1", "2", "3", "4", "5", "6")
        await message.channel.send(random.choice(answer))
    ##
    ##
    ## This one saves the last message from users for the "ls" command, honestly, this should be replaced with json file, because it doesn't save messages after restart.
    ##
    ##
    user_id = message.author.id # User name
    content = message.content # Content of message 
    time_ = datetime.datetime.now() # Date of message
    last_seen[user_id] = (content, time_) 
    
    last_seen_str = {k: (v[0], v[1].strftime("%Y-%m-%d %H:%M:%S")) for k, v in last_seen.items()} # Time format

    with open("last_seen.json", "w") as f:
        json.dump(last_seen_str, f)

    await bot.process_commands(message) # After this line the bot will execute the rest of the code

## This was used for dynamicly change the presence, but it crashes after some time (3 hours or smth). And I dont know why
#async def presenceUwU():
#    while True:
#        random_status_text = ("1", "☭", "2") # List 
#        prikol = random.choice(random_status_text) # Random choice from list
#        await bot.change_presence(activity=discord.Game(name=prikol), status=discord.Status.dnd) # Change presence
#        await asyncio.sleep(15) # Sleep for X seconds then do it again
##

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name=""), status=discord.Status.dnd)
#    bot.loop.create_task(presenceUwU()) # Uncomment this and "async def presenceUwU():" if you anyway want to use dynamic presence changing.

    ##
    ##
    ## Finally, commands
    ##
    ##

@bot.command(aliases = ("p",)) # Ping command, you can change or add more aliases
async def ping(ctx):
    ram = (psutil.virtual_memory()) # Get ram data
    cpu = psutil.cpu_percent() # Get average cpu load in percents

    # My soydev try to make a graph of cpu load, Not much accurate but it works
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
    #

    uptime = time.time() - start_time # Get uptime from "start_time"
    latency = bot.latency * 1000 # Get latency
    hours, remainder = divmod(uptime, 3600) # Convert the time to hours
    minutes, seconds = divmod(remainder, 60) # Convert the time to minutes
    await ctx.reply(f'```Uptime: {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds. \n Ping: {round(latency)} ms \n CPU: {cpu}% {tab}\n RAM↴ \n    Used: {psutil.virtual_memory()[2]} MB \n    Available: {ram.available / 1024 / 1024 / 1024:.2f} GB \n    Total {ram.total / 1024 / 1024 / 1024:.4} GB```') # Send message



@commands.command() # Just a calculator
async def calc(ctx: commands.Context):
    expression = ctx.message.content.split(ctx.prefix + ctx.command.name)[1].strip() # Get expression
    expression = requests.utils.quote(expression)
    url = f'http://api.mathjs.org/v4/?expr={expression}' # Url
    response = requests.get(url)
    data = response.json()
    number = data # Get responce from url
    message = f'{number}'
    await ctx.reply(message) # Send message



@bot.command(aliases = ("w",)) # Weather report. to make it work you will need to use your own api key
async def weather(ctx, city: str = None): # If there is nothing after command = either send an error message or send actual weather if user's city is in locations.json
    with open("locations.json", "r") as f: # Open the file
        locations = json.load(f)
    
    if city is None: # If there's nothing after command
        user_id = ctx.author.name # Get user id
        if user_id in locations: # Check if user is in the list 
            city = locations[user_id] # If in the list - Continue
        else: # If not
            await ctx.reply(f'Please provide a city name or use !set to save your location.')
            return

    api_key = '' # openweathermap api key
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric'
    response = requests.get(url)
    data = response.json()

    if data['cod'] != 200: # if city doesnt exist or the api is down
        await ctx.reply(f'Sorry, I could not find the weather for {city}.')
        return

    # Get weather data from api
    temp = data['main']['temp']
    feels_like = data['main']['feels_like']
    humidity = data['main']['humidity']
    wind_speed = data['wind']['speed']
    cloudscover = data['clouds']['all']
    pressure = data['main']['pressure']
    description = data['weather'][0]['description']
    name = data['name']
    #

    # Format in embed, hypothetically you can make it look much better
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
    #

    await ctx.reply(embed=embed) #Send a message




@bot.command(description="Set default location for weather") # Save location for the weather command
async def set(ctx, city: str):

    with open("locations.json", "r") as f: #Load
        locations = json.load(f)

    user_id = ctx.author.name # Get user name 
    locations[user_id] = city # Get message content

    with open("locations.json", "w") as f: #Save
        json.dump(locations, f)

    await ctx.reply(f'Your location has been set to {city}.') # Send confirmation, 
##

def load_locations(self):

    try:
        with open('locations.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {} 

def save_locations(self):
    with open('locations.json', 'w') as f:
        json.dump(self.locations, f)
##

@bot.command() # Wikipedia
async def wiki(ctx: commands.Context, language, *, search : str =None):
    try: 
        if search is None: # If there's only a search promt, it will use English wikipedia by default.
            url1 = f'https://en.wikipedia.org/api/rest_v1/page/summary/{language}'
            response1 = requests.get(url1)
            data1 = response1.json()
		
            title1 = data1['titles']['normalized']
            more1 = data1['description']
            link1 = data1['content_urls']['desktop']['page']

            message1 = f'{title1} - {more1} | {link1}'
            await ctx.reply(message1)
            return
		
	# If you want to search in specific language
        url = f'https://{language}.wikipedia.org/api/rest_v1/page/summary/{search}'
        response = requests.get(url)
        data = response.json()
            
        title = data['titles']['normalized']
        more = data['description']
        link = data['content_urls']['desktop']['page']

        message = f'{title} - {more} | {link}'

        await ctx.reply(message)
    except Exception as e: # Exception if there's an error or nothing found
        await ctx.reply(f"Nothing found")
    return

@bot.command() # Spam command, since discord are assholes, it spams very slow 
async def spam(ctx, count: int, *message):
    try:
        message = " ".join(message) # message
    except ValueError:
        return
    for i in range(count): # Loop
        await ctx.send(message)


@bot.command(aliases = ("t",)) # Translator command. api is free but has some restrictions, 5k words per day or something
async def tl(ctx: commands.Context):

    message = [x.strip() for x in ctx.message.content.split("|", maxsplit=2)] 

    target = message[0][len(ctx.prefix + ctx.command.name):] # Get "from" and "to" languages

    language = message[1] # from 
        
    language1 = message[2] # to

    url = f"https://api.mymemory.translated.net/get?q={target}&langpair={language}|{language1}" 
    response = requests.get(url) 
    data = response.json()
    translatedText = data["responseData"]["translatedText"]
    message = f"{translatedText}."

    await ctx.reply(message) #Send



@bot.command(aliases = ("py",)) # Pyramid, the same thing as spam = slow as fuck, don't use it with large numbers 
@commands.cooldown(1, 5, commands.BucketType.user)
async def pyramid(ctx, emote: str, num: int = 3):
    if num < 1 or num > 20: # 20 messages limit (double the number for a real deal, for instance, here is the output, and it will be 40 messages long)
        return

    messages = []

    for i in range(1, num + 1): # Loop, adds +1 object every message

        message = (emote + " ") * i 

        await ctx.send(message)

        messages.append(message) # first stage of pyramid

    for message in reversed(messages[:-1]): # Reverse previous result
        await ctx.send(message) # Second and complete pyramid



@bot.command(aliases = ("re",)) # Simple reminder
async def remind(ctx):
    try:
        time, message = [x.strip() for x in ctx.message.content.split(maxsplit=2)[1:]] # Get time and message
        seconds = convert(time) # Convert the time
    except ValueError:
        await ctx.reply(f"Please provide a valid time and message.") # If user sent an incorrect format
        return

    await ctx.reply(f"I will remind you in {time} < {message} >") # It will remind them in X time
    await asyncio.sleep(seconds) # Wait X time
    await ctx.reply(f'{time} ago : < {message} >.') # It reminded fr fr

#
def convert(time): # Time the bot can understand
    time_dict = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800} 
    unit = time[-1]

    if unit not in time_dict:
        raise ValueError("Invalid time unit.")
    
    value = int(time[:-1])
    return value * time_dict[unit]
#


@bot.command() # Check if given website is down
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
	#

    await ctx.reply(message)



@bot.command(aliases = ("u",)) # Get user info  
async def user(ctx, user: typing.Optional[commands.UserConverter] = None):
    if user is None: # If user wasn't given - use author's name
        user = ctx.author
	#
    guild = ctx.guild
    member = guild.get_member(user.id)
	#
    embed = discord.Embed()
    embed.title = f"{user.name}#{user.discriminator}" # Since discord removed discriminators, it puts just zero after # (but only for regular accounts, bots still have them)
    embed.description = f"{user.mention}" # I dont know if I can fetch users bio, i just put a mention then, if you dont want to ping someone remove it.
    embed.color = discord.Color.random() 
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Created at", value=user.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    if member is not None: # If user on server
        embed.add_field(name="Nickname", value=member.nick or "None")
        embed.add_field(name="Joined at", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S"))
        embed.add_field(name="Roles", value=", ".join(role.name for role in member.roles[1:]) or "None")
	#    
	await ctx.reply(embed=embed) # Send embed

###
### Role commands
###
@bot.group() # Group for role commands
@commands.has_role("Moderator") # Access role
async def role(ctx):
  if ctx.invoked_subcommand is None:
    await ctx.reply("Specify a valid subcommand: list, display, create, delete, give, remove, color, rename")
####
####
@role.command() # Turn on or off role displaying in users list
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
####
####
@role.command() # Create a new role. DO NOT USE SPACES. ROLE WILL BE CREATED WITHOUT PING PERMISSIONS. It means that you wont be able to ping it
async def create(ctx, name, color: discord.Color = None):
    if color is None:
        await ctx.guild.create_role(name=name, color=discord.Color.random()) # Make a new role with a random color
        await ctx.reply(f"Created {name}") 
    else:
        await ctx.guild.create_role(name=name, color=color) # Make a new role with some color
        await ctx.reply(f"Created {name}")
####
####
@role.command() # Delete a role
async def delete(ctx, *, name):
  role = discord.utils.get(ctx.guild.roles, name=name)
  if role:
    await role.delete()
    await ctx.reply(f"Deleted {name}") # if deleted
  else:
    await ctx.reply(f"{name} not found") # if not found
####
####
@role.command() #Give a role to someone
async def give(ctx, role: discord.Role, member: discord.Member,): 
  await member.add_roles(role)
  await ctx.reply(f"{member.name} now has {role.name} role")
####
####
@role.command() # Take a role from someone
async def remove(ctx, role: discord.Role, *, member: discord.Member, ):
  await member.remove_roles(role)
  await ctx.reply(f"Removed {role.name} from {member.name}")
####
####
@role.command() # Sends a list of roles, more information about roles can be added in the list
async def list(ctx):
  rolelist = [role.name for role in ctx.guild.roles] 
  roles = ", \n".join(rolelist)
  await ctx.reply(f"```{roles}```") # Don't remove a "code formatting". It pings a whole server by @everyone
####
####
@role.command() # Change color of role
async def color(ctx, role: discord.Role, color: discord.Color):
  await role.edit(color=color)
  await ctx.reply(f"Color of {role.name} changed to {color}")
####
####
@role.command()
async def rename(ctx, role: discord.Role, *, name: str):
  await role.edit(name=name)
  await ctx.reply(f"Name of {role.name} changed to {name}")
####
####
@role.command() # Move role in the role list, to bottom or top
async def move(ctx, role_name: str, direction: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        await ctx.reply(f"Role not found.") # If no role found
        return
    if direction not in ["top", "bottom"]:
        await ctx.reply(f'Invalid direction. Use "top" and "bottom".') # If no direction, or direction is incorrect
        return
    bot_member = guild.get_member(bot.user.id)
    bot_top_role = bot_member.top_role
    if direction == "top": # If to top
        position = bot_top_role.position - 1
    else: # If to bottom
        position = min(r.position for r in guild.roles if not r.managed) + 1
    await role.edit(position=position) # Save
    await ctx.reply(f"{role_name} moved to {direction}.")
####


@bot.group() # Management of members
@commands.has_role("Moderator") # Access role
async def member(ctx):
  if ctx.invoked_subcommand is None:
    await ctx.reply("Please specify a valid subcommand: mute, ban, unban, kick")
####
####
@member.command() # Ban someone (forever)
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    await ctx.send(f"{member} has been banned for {reason}.")
####
####
#@member.command() # DOES NOT WORK. it can't unban
#async def unban(ctx, id: int):
#    user = await client.fetch_user(id)
#    await ctx.guild.unban(user)
#    await ctx.send(f"{user} has been unbanned.")
####
####
@member.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.send(f'{member} has been kicked.')
####
####
@member.command() # Mute someone, it will create a new role, if you already have any role for mute, use this name in the code below
@commands.has_permissions(manage_messages=True) 
async def mute(ctx, member: discord.Member): 
  role = discord.utils.get(ctx.guild.roles, name="Muted") # This *
  guild = ctx.guild
  if role not in guild.roles:
    perms = discord.Permissions(send_messages=False, speak=False)
    await guild.create_role(name="Muted", permissions=perms) # And this *
    await member.add_roles(role)
    await ctx.reply('Role "Muted" has been created and assigned to {member}')
  else:
    await member.add_roles(role)
    await ctx.reply(f"{member} has been muted")
####
####
@bot.command(aliases = ("stalk",)) # Get last message from user
async def ls(ctx, user: discord.Member):
    with open("last_seen.json", "r") as f: 
        last_seen = json.load(f)

    user_id = str(user.id) 
    
    if user_id in last_seen:
        content, time = last_seen[user_id] # Time
        time_dt = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        now = datetime.datetime.now()
        delta = now - time_dt # Delta
        delta_str = humanize.precisedelta(delta)
        delta_str = delta_str.replace(",", "").strip() + " ago" # Humanize the time
        await ctx.reply(f"[{delta_str}] {user.mention} : {content}") # If there is a user in logs
    else:
        await ctx.reply(f"There's no messages from {user.mention}.") # if there is no
####



@bot.command() # I dont know if it works on Windows, but make sure that only you can execute this command, since subrocess is basicly a shell, someone can jsut run "rm -rf /" and destroy your system.
async def cmd(ctx: commands.Context, *, command): 
    if ctx.author.name == "v1ss0nd": # Your discord name
        try: # It's also possible to allow this command only in bot's DM, if you will
            message = subprocess.getoutput(f'{command}') 
            await ctx.send(f"```{message}```") # Get output
        except Exception as e:   
            await ctx.send(f"{e}") # Error message
        return
    else: # If someone else executes this command
        return



@bot.command() # Joins the bot to a voice channel
async def join(context: commands.Context) -> discord.VoiceProtocol:
    if context.author.voice is None: # Connects to the same voice channel as author in
        return await context.reply("You are not in voice channel.")
    channel = context.author.voice.channel

    client = context.voice_client
    if client is None:
        client = await channel.connect()
    if client.is_connected() and client.channel != channel:
        await client.move_to(channel) 

    return client


@bot.command() # Leave from voice channel
async def leave(ctx):
  guild = ctx.guild
  if guild.voice_client is not None:
    await guild.voice_client.disconnect()
    await ctx.reply(f"Left from the voice channel")
  else:
    await ctx.reply("I am not in any voice channel.")


@bot.command() # Stop playing everything, I tried to make a pause command but it didn't work in the way I expected
async def stop(ctx):
  vc = ctx.voice_client
  if vc and vc.is_connected():
    vc.stop()
    await ctx.reply("Stopped playing")
  else:
    await ctx.reply("Nothing playing rn")


	## Not my code, all credits to solarless
@bot.command() # Plays attached audio file, saves the download files in main bot's folder, you can create a special folder for it, or delete it automaticly after disconnect from voice channel.
async def playfile(context: commands.Context, repeat: bool = False) -> None:
    client = await join(context)

    attachment = context.message.attachments[0] # Get attachment
    filename = await download_audio(attachment.url)

    client.loop = repeat
    client.play(discord.FFmpegPCMAudio(filename))
    await context.reply(f"Playing __{attachment.filename.replace('_', ' ')}__") #Play audio

async def download_audio(url: str) -> str: # Download audio
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            content = await response.read()
            extension = response.url.suffix

    filename = f"audio{random.randint(1000, 9999)}{extension}"

    with open(filename, "wb") as file:
        file.write(content)

    return filename

bot.run('') # Bot token
