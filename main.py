import discord
from discord.ext import commands
from datetime import datetime
import pytz

# ===== INFO =====
TOKEN = os.getenv("raven")
GUILD_ID = 1449034375634354311
TARGET_USER_ID = 1125449260037574760
LOG_CHANNEL_ID = 1455171567737634867
# =================

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# ===== FORMAT TIME =====
def format_times():
    vn_time = datetime.now()
    de_tz = pytz.timezone("Europe/Berlin")
    de_time = datetime.now(de_tz)

    vn = vn_time.strftime("%A | %d/%m/%Y | %H:%M:%S.%f")[:-3]
    de = de_time.strftime("%A | %d/%m/%Y | %H:%M:%S.%f")[:-3]

    return vn, de

# ===== GET VOICE MEMBERS =====
def get_voice_members(channel):
    if channel is None:
        return "*No channel*"

    members = [f"• {m.display_name}" for m in channel.members]
    text = "\n".join(members)

    if len(text) > 1020:
        text = text[:1020] + "\n..."

    return text if text else "*No one*"

@bot.event
async def on_ready():
    print("Bot online")

# ===== LOG MESSAGE =====
@bot.event
async def on_message(message):
    if not message.guild:
        return
    if message.guild.id != GUILD_ID:
        return
    if message.author.id != TARGET_USER_ID:
        return

    vn_time, de_time = format_times()
    log = bot.get_channel(LOG_CHANNEL_ID)

    embed = discord.Embed(title="📨 MESSAGE SENT", color=0x2ecc71)
    embed.set_thumbnail(url=message.author.display_avatar.url)

    embed.add_field(name="👤 User", value=f"{message.author} ({message.author.id})", inline=False)
    embed.add_field(name="📍 Channel", value=message.channel.mention, inline=False)
    embed.add_field(name="🕒 Time", value=f"🇻🇳 {vn_time}\n🇩🇪 {de_time}", inline=False)
    embed.add_field(name="💬 Content", value=message.content or "*[No text]*", inline=False)

    await log.send(embed=embed)
    await bot.process_commands(message)

# ===== LOG DELETE =====
@bot.event
async def on_message_delete(message):
    if not message.guild:
        return
    if message.guild.id != GUILD_ID:
        return
    if not message.author or message.author.id != TARGET_USER_ID:
        return

    vn_time, de_time = format_times()
    log = bot.get_channel(LOG_CHANNEL_ID)

    embed = discord.Embed(title="🗑️ MESSAGE DELETED", color=0xe74c3c)
    embed.set_thumbnail(url=message.author.display_avatar.url)

    embed.add_field(name="👤 User", value=f"{message.author}", inline=False)
    embed.add_field(name="📍 Channel", value=message.channel.mention, inline=False)
    embed.add_field(name="🕒 Time", value=f"🇻🇳 {vn_time}\n🇩🇪 {de_time}", inline=False)
    embed.add_field(name="💬 Content", value=message.content or "*[No cache]*", inline=False)

    await log.send(embed=embed)

# ===== VOICE + STREAM =====
@bot.event
async def on_voice_state_update(member, before, after):
    if member.guild.id != GUILD_ID:
        return
    if member.id != TARGET_USER_ID:
        return

    vn_time, de_time = format_times()
    log = bot.get_channel(LOG_CHANNEL_ID)

    # ===== JOIN =====
    if before.channel is None and after.channel is not None:
        embed = discord.Embed(title="🔊 VOICE JOIN", color=0x3498db)
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="👤 User", value=f"{member}", inline=False)
        embed.add_field(
            name="📍 Channel",
            value=f"{after.channel.name} ({len(after.channel.members)} users)",
            inline=False
        )
        embed.add_field(
            name="👥 Members",
            value=get_voice_members(after.channel),
            inline=False
        )
        embed.add_field(name="🕒 Time", value=f"🇻🇳 {vn_time}\n🇩🇪 {de_time}", inline=False)

        await log.send(embed=embed)

    # ===== LEAVE =====
    if before.channel is not None and after.channel is None:
        embed = discord.Embed(title="🔇 VOICE LEAVE", color=0xe67e22)
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="👤 User", value=f"{member}", inline=False)
        embed.add_field(
            name="📍 Channel",
            value=f"{before.channel.name} ({len(before.channel.members)} users)",
            inline=False
        )
        embed.add_field(
            name="👥 Members",
            value=get_voice_members(before.channel),
            inline=False
        )
        embed.add_field(name="🕒 Time", value=f"🇻🇳 {vn_time}\n🇩🇪 {de_time}", inline=False)

        await log.send(embed=embed)

    # ===== SWITCH =====
    if before.channel and after.channel and before.channel != after.channel:
        embed = discord.Embed(title="🔁 VOICE SWITCH", color=0x9b59b6)
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="👤 User", value=f"{member}", inline=False)
        embed.add_field(
            name="📍 Channel",
            value=f"{before.channel.name} ➜ {after.channel.name}",
            inline=False
        )
        embed.add_field(
            name="👥 Members",
            value=get_voice_members(after.channel),
            inline=False
        )
        embed.add_field(name="🕒 Time", value=f"🇻🇳 {vn_time}\n🇩🇪 {de_time}", inline=False)

        await log.send(embed=embed)

    # ===== STREAM START =====
    if not before.self_stream and after.self_stream:
        embed = discord.Embed(title="📡 STREAM STARTED", color=0x1abc9c)
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="👤 User", value=f"{member}", inline=False)
        embed.add_field(name="📍 Channel", value=after.channel.name, inline=False)
        embed.add_field(name="🕒 Time", value=f"🇻🇳 {vn_time}\n🇩🇪 {de_time}", inline=False)

        await log.send(embed=embed)

    # ===== STREAM STOP =====
    if before.self_stream and not after.self_stream:
        embed = discord.Embed(title="📴 STREAM STOPPED", color=0xc0392b)
        embed.set_thumbnail(url=member.display_avatar.url)

        embed.add_field(name="👤 User", value=f"{member}", inline=False)
        embed.add_field(name="📍 Channel", value=before.channel.name, inline=False)
        embed.add_field(name="🕒 Time", value=f"🇻🇳 {vn_time}\n🇩🇪 {de_time}", inline=False)

        await log.send(embed=embed)

bot.run(TOKEN)
