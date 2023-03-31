import config
import disnake
from urllib.request import urlopen
import json
import re
import asyncio
import datetime


def is_admin(ctx):
    if ctx.guild.id not in config.admin_ids or ctx.author.id not in config.admin_ids[ctx.guild.id]:
        return False
    return True


def get_nickname(member):
    if member.nick:
        return member.nick
    else:
        return member.name


def get_duration(duration):
    ans = ""
    hours = duration // 3600
    minutes = (duration // 60) - hours*60
    seconds = duration % 60
    if hours == 0:
        ans += "00"
    elif hours < 10:
        ans += "0"+str(hours)
    else:
        ans += str(hours)

    if minutes == 0:
        ans += ":00"
    elif minutes < 10:
        ans += ":0"+str(minutes)
    else:
        ans += ":"+str(minutes)

    if seconds == 0:
        ans += ":00"
    elif seconds < 10:
        ans += ":0"+str(seconds)
    else:
        ans += ":"+str(seconds)
    return ans


def song_embed_builder(ctx, info, text):
    embed = disnake.Embed(
        title=info['title'],
        url=info['webpage_url'],
        description=text,
        color=disnake.Colour.from_rgb(0, 0, 0),
        timestamp=datetime.datetime.now())

    embed.set_author(name=info['uploader'])
    embed.set_thumbnail(url=f"https://img.youtube.com/vi/{info['id']}/0.jpg")
    embed.add_field(name="*Duration*",
                    value=get_duration(info['duration']), inline=True)
    embed.add_field(name="*Requested by*",
                    value=get_nickname(ctx.author), inline=True)
    return embed


async def radio_message(ctx):
    url = "http://anison.fm/status.php?widget=true"
    name = ""
    while True:
        response = urlopen(url)
        data_json = json.loads(response.read())
        duration = data_json["duration"] - 13
        if re.search("151; (.+?)</span>", data_json['on_air']).group(1) == name:
            await asyncio.sleep(duration - 1)
            continue
        name = re.search("151; (.+?)</span>", data_json['on_air']).group(1)
        anime = re.search("blank'>(.+?)</a>", data_json['on_air']).group(1)
        await ctx.channel.send(f"Now playing: {anime} - {name}")
        await asyncio.sleep(duration - 1)
