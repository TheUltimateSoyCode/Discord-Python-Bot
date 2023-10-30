import datetime
from discord import client, Message
import aiohttp
import random
import time
import typing
import json
import humanize
import discord
from discord.ext import commands 

start_time = time.time()
intents = discord.Intents.default()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

ffmpeg_options = {
  'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
  'options': '-vn',
  'format': 'bestaudio[ext=m4a]'
}

@bot.event
async def on_guild_join(ctx, guild):
    channel = guild.system_channel    
    if channel is not None:
        await channel.send(f'Successfully joined! You can find a command list here - https://v1ss0nd.github.io/discord-help , \nYou have to create "Moderator" role to use bot moderation feature, make sure you gave it to your server moderators!')

@bot.event
async def on_message(message: Message):
    if message.author == bot.user: return
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
    await bot.change_presence(activity=discord.Game(name='Type "!help" to DM with me to see a list with supported commands'))

@bot.command()
async def stalk(ctx, user: discord.Member):
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
        await ctx.reply(f"{user.mention} was last seen in chat {delta_str}, their last message: {content}")
    else:
        await ctx.reply(f"i havent seen any messages from {user.mention}.")

@bot.command()
async def ping(ctx):
    uptime = time.time() - start_time
    latency = bot.latency * 1000 
    hours, remainder = divmod(uptime, 3600)
    minutes, seconds = divmod(remainder, 60)
    await ctx.reply(f'pong! Current uptime is {int(hours)} hours {int(minutes)} minutes {int(seconds)} seconds. Latency is {round(latency)} ms')

bot.remove_command('help')

class CustomHelpCommand(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        embed = discord.Embed(title="https://v1ss0nd.github.io/discord-help", url="https://v1ss0nd.github.io/discord-help")
        for page in self.paginator.pages:
            embed.description = page
        await destination.send(embed=embed)

bot.help_command = CustomHelpCommand()

@bot.command()
@commands.has_role("Moderator")
async def spam(ctx, count: int, *message):
    try:
        message = " ".join(message)
    except ValueError:
        return
    for i in range(count):
        await ctx.send(message)

@bot.command(description="info about provided user")  
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
    await ctx.reply("Please specify a valid subcommand: list, create, delete, give, remove, color, rename")

@role.command()
async def display(ctx, role_name: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:

        await ctx.reply(f"Role {role_name} not found")
        return
    current_hoist = role.hoist
    new_hoist = not current_hoist
    await role.edit(hoist=new_hoist)
    await ctx.reply(f"Separate displaying of {role_name} switched to {new_hoist}.")

@role.command()
async def create(ctx, name, color: discord.Color):
  await ctx.guild.create_role(name=name, color=color)
  await ctx.reply(f"Created role {name}")

@role.command()
async def delete(ctx, *, name):
  role = discord.utils.get(ctx.guild.roles, name=name)
  if role:
    await role.delete()
    await ctx.reply(f"Deleted role {name}")
  else:
    await ctx.reply(f"Role {name} not found")

@role.command()
async def give(ctx, role: discord.Role, member: discord.Member,):
  await member.add_roles(role)
  await ctx.reply(f"Gave {role.name} to {member.name}")

@role.command()
async def remove(ctx, role: discord.Role, member: discord.Member, ):
  await member.remove_roles(role)
  await ctx.reply(f"Removed {role.name} from {member.name}")

@role.command()
async def list(ctx):
  rolelist = [role.name for role in ctx.guild.roles] 
  roles = ", ".join(rolelist)
  await ctx.reply(f"{roles}")

@role.command()
async def color(ctx, role: discord.Role, color: discord.Color):
  await role.edit(color=color)
  await ctx.reply(f"Changed the color of {role.name} to {color}")

@role.command()
async def rename(ctx, role: discord.Role, *, name: str):
  await role.edit(name=name)
  await ctx.reply(f"Changed the name of {role.mention} to {name}")

@role.command()
async def move(ctx, role_name: str, direction: str):
    guild = ctx.guild
    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        await ctx.reply(f"Role not found.")
        return
    if direction not in ["top", "bottom"]:
        await ctx.reply(f"Invalid direction. Please use 'top' or 'bottom'.")
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
    await ctx.reply(f"{member} has been banned for {reason}.")

@member.command()
async def unban(ctx, id: int):
    user = await client.fetch_user(id)
    await ctx.guild.unban(user)
    await ctx.reply(f"{user} has been unbanned.")

@member.command()
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    await ctx.reply(f'User {member} has been kicked.')

@member.command() 
@commands.has_permissions(manage_messages=True)
async def mute(ctx, member: discord.Member):
  role = discord.utils.get(ctx.guild.roles, name="Muted")
  guild = ctx.guild
  if role not in guild.roles:
    perms = discord.Permissions(send_messages=False, speak=False)
    await guild.create_role(name="Muted", permissions=perms)
    await member.add_roles(role)
    await ctx.reply("Successfully created Muted role and assigned it to mentioned user.")
  else:
    await member.add_roles(role)
    await ctx.reply(f"Has been muted {member}")

@bot.command()
async def join(context: commands.Context) -> discord.VoiceProtocol:
    if context.author.voice is None:
        return await context.reply("You are not in a voice channel.")
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
    await ctx.reply("I am not in a voice channel.")

@bot.command()
async def play(ctx, path: str, repeat: bool = False):
    vc = await join(ctx)
    if path.startswith("http"):
        song = pafy.new(path)
        audio = song.getbestaudio()
        source = discord.FFmpegPCMAudio(audio.url)
    else:
        source = discord.FFmpegPCMAudio(path)
    vc.loop = repeat
    vc.play(source)
    await ctx.reply(f"Playing {path}")

@bot.command()
async def stop(ctx):
  vc = ctx.voice_client
  if vc and vc.is_connected():
    vc.stop()
    await ctx.reply("Stopped playing.")
  else:
    await ctx.reply("There is nothing playing.")

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

bot.run('TOKEN')
