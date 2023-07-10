import disnake
from datetime import datetime, timezone
import time
import re
import public_config
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

import private_config


def is_admin(member):
    if (member.guild) and (member.guild.id not in private_config.admin_ids or member.id not in private_config.admin_ids[member.guild.id]):
        return False
    return True


def get_duration(info):
    if "live_status" in info and info['live_status'] == "is_live" or info['duration'] == 0:
        ans = "Live"
    else:
        ans = time.strftime('%H:%M:%S', time.gmtime(info['duration']))
    return ans


def is_mentioned(member, message):
    for role in message.role_mentions:
        if role in member.roles:
            return True
    if member in message.mentions:
        return True
    return False


async def create_private(member):

    if member.guild.id not in private_config.categories_ids:
        return
    possible_channel_name = f"{member.display_name}'s private"

    guild = member.guild
    category = disnake.utils.get(
        guild.categories, id=private_config.categories_ids[guild.id])

    tmp_channel = await category.create_voice_channel(name=possible_channel_name)

    await tmp_channel.set_permissions(guild.default_role, view_channel=False)

    await member.move_to(tmp_channel)

    perms = tmp_channel.overwrites_for(member)
    perms.view_channel = True
    perms.manage_permissions = True
    perms.manage_channels = True
    await tmp_channel.set_permissions(member, overwrite=perms)
    await tmp_channel.edit(bitrate=public_config.temporary_channels_settings['bitrate'])


async def unmute_bots(member):
    ff = False
    if member.id in private_config.bot_ids.values():
        if member.voice.mute:
            await member.edit(mute=False)
            ff = True
        if member.voice.deaf:
            await member.edit(deafen=False)
            ff = True
    return ff


async def unmute_admin(member):
    ff = False
    if member.guild.id in private_config.supreme_beings_ids and member.id in private_config.supreme_beings_ids[member.guild.id]:
        if member.voice.mute:
            await member.edit(mute=False)
            ff = True
        if member.voice.deaf:
            await member.edit(deafen=False)
            ff = True

        entry = await member.guild.audit_logs(limit=2, action=disnake.AuditLogAction.member_update).flatten()
        entry = entry[1]
        delta = datetime.now(timezone.utc) - entry.created_at
        if entry.user != member and entry.user.id not in private_config.bot_ids.values() and (delta.total_seconds() < 2) and entry.user.id not in private_config.supreme_beings_ids[member.guild.id]:
            await entry.user.move_to(None)
            try:
                await entry.user.timeout(duration=60, reason="Attempt attacking The Supreme Being")
            except:
                pass
    return ff


def get_guild_name(guild):
    if guild.name == "Nazarick":
        return "the Great Tomb of Nazarick"
    return guild.name


def get_welcome_time(date):
    delta = datetime.now(timezone.utc) - date
    amount = delta.days // 365
    if amount > 0:
        if amount == 1:
            return "a year ago"
        else:
            return f"{amount} years ago"

    amount = delta.days // 30
    if amount > 0:
        if amount == 1:
            return "a month ago"
        else:
            return f"{amount} months ago"

    amount = delta.days // 7
    if amount > 0:
        if amount == 1:
            return "a week ago"
        else:
            return f"{amount} weeks ago"

    amount = delta.days
    if amount > 0:
        if amount == 1:
            return "a day ago"
        else:
            return f"{amount} days ago"

    amount = delta.hours
    if amount > 0:
        if amount == 1:
            return "an hour ago"
        else:
            return f"{amount} hours ago"

    amount = delta.minutes
    if amount <= 1:
        return "a minute ago"
    return f"{amount} minutes ago"


def get_members_count(members):
    cnt = len(members)
    for member in members:
        if member.bot:
            cnt -= 1
    return cnt


def split_into_chunks(msg: list[str], chunk_size: int = 1990) -> list[str]:
    source = msg.split("\n")
    pattern = r'```[a-zA-Z]*\n'
    chunks = []
    chunk = ""
    length = 0
    for line in source:
        if length + len(line) > chunk_size:
            if chunk.count('`') % 2 == 1:
                prefix = re.findall(pattern, chunk)
                chunk += '```'
                chunks.append(chunk)

                chunk = prefix[-1]
                length = len(chunk)
            else:
                chunks.append(chunk)
                chunk = ""
                length = 0

        if (line.count('`') % 6 == 0):
            line = line.replace('```', '\`\`\`')

        chunk += line
        length += len(line)

        if (line[-3:] != '```'):
            chunk += '\n'
            length += 1

    if chunk != "":
        chunks.append(chunk)
    return chunks


def parse_key(key):
    s = key.split('_')
    res = ""
    for i in range(0, len(s)):
        res += ((s[i][0].upper() + s[i][1:]) if i == 0 else s[i]) + " "
    return res


def ytdl_extract_info(url, download=True):
    with YoutubeDL(public_config.YTDL_OPTIONS) as ytdl:
        return ytdl.extract_info(url, download=download)


def yt_search(query, max_results=5):
    return YoutubeSearch(query, max_results=max_results).to_dict()


async def set_bitrate(guild):
    voice_channels = guild.voice_channels
    bitrate_value = public_config.bitrate_values[guild.premium_tier]
    for channel in voice_channels:
        if channel.bitrate != bitrate_value:
            await channel.edit(bitrate=bitrate_value)
