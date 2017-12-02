import asyncio
import datetime
import discord
import json
import os
import sys
import time
import traceback
from discord.ext import commands
from icyparser import IcyParser
from random import choice

bot = commands.Bot(description=' ', command_prefix='r!')

owner_id = "154497072148643840"

startup_cogs = (
    'cogs.help',
)


with open("config.json") as f:
    data = json.load(f)
    token = data["token"]


@bot.event
async def on_ready():
    print('')
    print('     :::::::::      :::     ::::::::: ::::::::::: ::::::::  ')
    print('     :+:    :+:   :+: :+:   :+:    :+:    :+:    :+:    :+: ')
    print('     +:+    +:+  +:+   +:+  +:+    +:+    +:+    +:+    +:+ ')
    print('     +#++:++#:  +#++:++#++: +#+    +:+    +#+    +#+    +:+ ')
    print('     +#+    +#+ +#+     +#+ +#+    +#+    +#+    +#+    +#+ ')
    print('     #+#    #+# #+#     #+# #+#    #+#    #+#    #+#    #+# ')
    print('     ###    ### ###     ### ######### ########### ######## ')
    print(' ')
    print('            ╔═══ Logged in: ══╦═════ User ID: ═════╗')
    print('            ║       OK        ║ ' + bot.user.id + ' ║')
    print('            ╠═════════════════╩════════════════════╣')
    print('            ║          Discord.py Version          ║')
    print('            ║               ' + discord.__version__ + '                ║')
    print('            ╚══════════════════════════════════════╝')
    print('                            Invite:')
    print(discord.utils.oauth_url(bot.user.id))
    print('                Servers: ' + str(len(bot.servers)) + '          Users: ' + str(len(set(bot.get_all_members()))))
    print('')

    for cog in startup_cogs:
        try:
            bot.load_extension(cog)
        except Exception as e:
            print('Failed to load: {}'.format(cog))


@bot.listen()
async def on_command_error(error, ctx):
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author, 'No.')
    elif isinstance(error, commands.CommandInvokeError):
        print('Error in {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print('{0.__class__.__name__}: {0}'.format(error.original), file=sys.stderr)


@bot.listen()
async def on_message(message: discord.Message):
    if not message.channel.is_private or message.channel.user.id == owner_id:
        return

    # if message.content == "?ignoredpmcommand":
        # pass

    embed = discord.Embed()
    if message.author == bot.user:
        embed.title = 'Sent PM to {}#{} ({}).'.format(message.channel.user.name, message.channel.user.discriminator, message.channel.user.id)
    else:
        embed.set_author(name=message.author, icon_url=message.author.avatar_url or message.author.default_avatar_url)
        embed.title = '{} messaged me:'.format(message.channel.user.id)
    embed.description = message.content
    embed.timestamp = message.timestamp

    owner = discord.utils.get(bot.get_all_members(), id=owner_id)
    await bot.send_message(owner, embed=embed)


@bot.command(pass_context=True)
async def pm(ctx, user: discord.User, *, content: str):
    """[Owner] PMs a person."""
    if ctx.message.author.id == owner_id:
        await bot.send_message(user, content)
        await bot.send_message(ctx.message.channel, "Message sent.")


@bot.command(pass_context=True, no_pm=True)
async def play(ctx, message: discord.Message=None, timeout: int=30):
    """Choose a stream to play."""

    # expected = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣", "7⃣", "8⃣", "9⃣", "🔟"]
    # buttons = {
        # "soma1": "1⃣",
        # "soma2": "2⃣",
        # "soma3": "3⃣",
        # "soma4": "4⃣",
        # "soma5": "5⃣",
        # "soma6": "6⃣",
        # "soma7": "7⃣",
        # "soma8": "8⃣",
        # "soma9": "9⃣",
        # "soma10": "🔟"
    # }

    channel = ctx.message.channel
    if bot.user.bot:
        def to_delete(m):
            if "Now Playing" in m.content:
                return True
            else:
                return False
        try:
            await bot.purge_from(channel, limit=50, check=to_delete)
        except discord.errors.Forbidden:
            await bot.say("I need permissions to manage messages "
                                                   "in this channel.")
    await bot.delete_message(ctx.message)

    buttons = {
        "soma1": "1⃣",
        "soma2": "2⃣",
        "soma3": "3⃣",
        "soma4": "4⃣",
        "ytstream1": "5⃣",
        "ytstream2": "6⃣"
    }

    expected = ["1⃣", "2⃣", "3⃣", "4⃣", "5⃣", "6⃣"]

    colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
    embed = discord.Embed(colour=int(colour, 16))

    embed.add_field(name="Radio Stations", value="1. **Groove Salad** - A nicely chilled plate of ambient, downtempo beats and grooves.\n2. **The Trip** - Progressive house and trance. Tip top tunes.\n3. **DEFCON** - The DEF CON 25 Channel.\n4. **Spacestation** - Spaced-out ambient and mid-tempo electronica.\n5. **Lofi Hip Hop Radio 24/7** - Chill Gaming / Study Beats\n6. Provide your own YouTube Live link.", inline=False)
    # embed.set_footer(text="Powered by SomaFM.")

    message = await bot.send_message(ctx.message.channel, embed=embed)
    for i in range(6):
        await bot.add_reaction(message, expected[i])
    react = await bot.wait_for_reaction(message=message, user=ctx.message.author, timeout=timeout, emoji=expected)
    if react is None:
        await bot.delete_message(message)
        await bot.say("Try again later.")
        return
    reacts = {v: k for k, v in buttons.items()}
    react = reacts[react.reaction.emoji]
    if react == "soma1":
        url = "http://ice1.somafm.com/groovesalad-128-mp3"
        await bot.delete_message(message)
        await playicecast(ctx=ctx, url=url, voice_channel=None)
    elif react == "soma2":
        url = "http://ice1.somafm.com/thetrip-128-mp3"
        await bot.delete_message(message)
        await playicecast(ctx=ctx, url=url, voice_channel=None)
    elif react == "soma3":
        url = "http://ice1.somafm.com/defcon-128-mp3"
        await bot.delete_message(message)
        await playicecast(ctx=ctx, url=url, voice_channel=None)
    elif react == "soma4":
        url = "http://ice1.somafm.com/spacestation-128-mp3"
        await bot.delete_message(message)
        await playicecast(ctx=ctx, url=url, voice_channel=None)
    elif react == "ytstream1":
        url = "https://www.youtube.com/watch?v=AQBh9soLSkI"
        await bot.delete_message(message)
        await playytstream(ctx=ctx, url=url, voice_channel=None)
    elif react == "ytstream2":
        url = None
        await bot.delete_message(message)
        await playytstream(ctx=ctx, url=url, voice_channel=None)
    global gurl
    gurl = url


async def playicecast(ctx, url=None, voice_channel: discord.Channel=None):
    """Play an icecast stream."""
    server = ctx.message.server
    author = ctx.message.author
    if url is None:
        await bot.say('What url?')
        urlm = await bot.wait_for_message(timeout=30, author=author)
        if urlm is None:
            await bot.say("Provide a valid URL next time.")
            return
        url = urlm.content

    if voice_channel is None:
        voice_channel = author.voice_channel
    if voice_connected(server):
        await _disconnect_voice_client(server)
        Channel = ctx.message.channel
        fetch = await bot.say("Fetching stream...")
        voice = await bot.join_voice_channel(voice_channel)
        player = voice.create_ffmpeg_player(url)
        player.start()
    else:
        Channel = ctx.message.channel
        fetch = await bot.say("Fetching stream...")
        voice = await bot.join_voice_channel(voice_channel)
        player = voice.create_ffmpeg_player(url)
        player.start()
    ip = IcyParser()
    ip.getIcyInformation(url)
    await asyncio.sleep(5)
    await bot.delete_message(fetch)
    streamtitle = ip.icy_streamtitle
    if streamtitle is None:
        ip.stop()
        await bot.say("Starting playback...")
        return
    else:
        streamtitle = str(streamtitle).replace(';StreamUrl=', '')
        streamtitle = str(streamtitle).replace("'", "")
        await bot.say("Now Playing: {}".format(streamtitle))
        await bot.change_presence(game=discord.Game(name=streamtitle, type=2))
    ip.stop()


async def playytstream(ctx, url=None, voice_channel: discord.Channel=None):
    """Play a YouTube live stream."""
    server = ctx.message.server
    author = ctx.message.author
    if url is None:
        await bot.say('What url?')
        urlm = await bot.wait_for_message(timeout=30, author=author)
        if urlm is None:
            await bot.say("Provide a valid URL next time.")
            return
        url = urlm.content

    if voice_channel is None:
        voice_channel = author.voice_channel
    if voice_connected(server):
        await _disconnect_voice_client(server)
        Channel = ctx.message.channel
        fetch = await bot.say("Fetching stream...")
        voice = await bot.join_voice_channel(voice_channel)
        options = '-b:a 64k -bufsize 64k'
        ytdl_options = {'format': '95'}
        player = await voice.create_ytdl_player(url, ytdl_options=ytdl_options, options=options)
        await bot.say("Now Playing: {}".format(player.title))
        await asyncio.sleep(1)
        await bot.delete_message(fetch)
    else:
        Channel = ctx.message.channel
        fetch = await bot.say("Fetching stream...")
        voice = await bot.join_voice_channel(voice_channel)
        options = '-b:a 64k -bufsize 64k'
        ytdl_options = {'format': '95'}
        player = await voice.create_ytdl_player(url, ytdl_options=ytdl_options, options=options)
        player.start()
        await bot.say("Now Playing: {}".format(player.title))
        await asyncio.sleep(1)
        await bot.delete_message(fetch)
        # await bot.change_presence(game=discord.Game(name=streamtitle, type=2))


@bot.command(pass_context=True, no_pm=True)
async def stop(ctx):
    """Stops playback."""
    server = ctx.message.server
    author = ctx.message.author
    await _disconnect_voice_client(server)
    await bot.say("Stopping playback...")


@bot.command(pass_context=True, aliases=["nowplaying", "song"], no_pm=True)
async def np(ctx):
    """Now playing. (Icecast only.)"""
    author = ctx.message.author
    ip = IcyParser()
    await bot.say("Fetching Song Information...")
    try:
        ip.getIcyInformation(gurl)
    except Exception as error:
        bot.say(error)
        return
    await asyncio.sleep(5)
    streamtitle = ip.icy_streamtitle
    streamtitle = str(streamtitle).replace(';StreamUrl=', '')
    streamtitle = str(streamtitle).replace("'", "")
    await bot.change_presence(game=discord.Game(name=streamtitle, type=2))
    await bot.say("Now Playing: {}".format(streamtitle))
    ip.stop()


@bot.command(pass_context=True, no_pm=True)
async def info(ctx, message: discord.Message=None, timeout: int=30):
    """Radio info."""
    await bot.delete_message(ctx.message)
    buttons = {"delete": "❌"}

    expected = ["❌"]

    colour = ''.join([choice('0123456789ABCDEF') for x in range(6)])
    embed = discord.Embed(colour=int(colour, 16))

    embed.add_field(name="Radio Info", value="**Radio** is a discord.py bot, built to play icecast streams.\nFuture plans: YouTube live streams.\nAuthor: aikaterna#1393\nHelp command modified from [Thane's help for Red v2/v3](https://github.com/SirThane/Thane-Cogs).\nPowered by [SomaFM](http://www.somafm.com/) - over 30 unique channels of listener-supported, commercial-free, underground/alternative radio.", inline=False)

    message = await bot.send_message(ctx.message.channel, embed=embed)
    for i in range(1):
        await bot.add_reaction(message, expected[i])
    react = await bot.wait_for_reaction(message=message, user=ctx.message.author, timeout=timeout, emoji=expected)
    if react is None:
        await bot.delete_message(message)
        return
    reacts = {v: k for k, v in buttons.items()}
    react = reacts[react.reaction.emoji]
    if react == "delete":
        await bot.delete_message(message)


@bot.command(pass_context=True, no_pm=True)
async def ping(ctx):
    """Pong."""
    channel = ctx.message.channel
    t1 = time.perf_counter()
    await bot.send_typing(channel)
    t2 = time.perf_counter()
    await bot.say("Pong: {}ms".format(round((t2-t1)*1000)))


@bot.command(pass_context=True)
async def sharedservers(ctx, user: discord.Member=None):
    """[Owner] Shows shared server info."""
    author = ctx.message.author
    server = ctx.message.server
    if ctx.message.author.id == owner_id:
        if not user:
            user = author
        seen = len(set([member.server.name for member in bot.get_all_members() if member.name == user.name]))
        sharedservers = str(set([member.server.name for member in bot.get_all_members() if member.name == user.name]))
        for shared in sharedservers:
            shared = "".strip("'").join(sharedservers).strip("'")
            shared = shared.strip("{").strip("}")
        data = "```ini\n"
        data += "[Servers]:     {} shared\n".format(seen)
        data += "[In Servers]:  {}```".format(shared)
        await bot.say(data)


#  Not implemented yet. Kinda halfway there, was going to fine tune it later and add counting of server players, ie self.players
# async def status_loop():
    # playing = {}
    # for server in bot.servers:
        # if server.id not in self.players:
            # self.players[server.id] = None
    # playing_servers = 0
        # for server in playing:
            # playing_servers += 1
        # if playing_servers == 0:
            # pass
        # elif playing_servers == 1:
            # try:
                # ip = IcyParser()
                # ip.getIcyInformation(url)
                # await asyncio.sleep(5)
                # streamtitle = ip.icy_streamtitle
                # if streamtitle is None:
                    # ip.stop()
                    # return
                # else:
                    # streamtitle = str(streamtitle).replace(';StreamUrl=', '')
                    # streamtitle = str(streamtitle).replace("'", "")
                    # await bot.change_presence(game=discord.Game(name=streamtitle, type=2))
            # except:
                # pass
        # else:
            # status = "music on {0} servers".format(playing_servers)
            # await bot.change_presence(game=discord.Game(name=status, type=0))
    # await asyncio.sleep(30)

def voice_client(server):
    return bot.voice_client_in(server)


def voice_connected(server):
    if bot.is_voice_connected(server):
        return True
    return False


async def _disconnect_voice_client(server):
    if not voice_connected(server):
        return

    vc = voice_client(server)

    await vc.disconnect()


@bot.command(pass_context=True, no_pm=True)
async def shutdown(ctx):
    """[Owner] Shutdown the bot."""
    server = ctx.message.server
    if ctx.message.author.id == owner_id:
        await _disconnect_voice_client(server)
        await bot.say("Shutting down...")
        await bot.logout()
        await bot.close()


bot.run(token)
