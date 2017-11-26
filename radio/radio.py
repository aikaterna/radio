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

with open("config.json") as f:
    data = json.load(f)
    token = data["token"]

    bot = commands.Bot(description='Radio', command_prefix='r!')

    owner_id = "154497072148643840"

    @bot.event
    async def on_ready():
        dpy_ver = discord.__version__
        print('')
        print('     :::::::::      :::     ::::::::: ::::::::::: ::::::::  ')
        print('     :+:    :+:   :+: :+:   :+:    :+:    :+:    :+:    :+: ')
        print('     +:+    +:+  +:+   +:+  +:+    +:+    +:+    +:+    +:+ ')
        print('     +#++:++#:  +#++:++#++: +#+    +:+    +#+    +#+    +:+ ')
        print('     +#+    +#+ +#+     +#+ +#+    +#+    +#+    +#+    +#+')
        print('     #+#    #+# #+#     #+# #+#    #+#    #+#    #+#    #+# ')
        print('     ###    ### ###     ### ######### ########### ######## ')
        print(' ')
        print('            ╔═══ Logged in: ══╦═════ User ID: ═════╗')
        print('            ║       OK        ║ ' + bot.user.id + ' ║')
        print('            ╠═════════════════╩════════════════════╣')
        print('            ║          Discord.py Version          ║')
        print('            ║               ' + discord.__version__ + '                ║')
        print('            ╚══════════════════════════════════════╝')
        print('	                    Invite:')
        print(discord.utils.oauth_url(bot.user.id))
        print('                Servers: ' + str(len(bot.servers)) + '          Users: ' + str(len(set(bot.get_all_members()))))
        print('')

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
    async def play(ctx, url=None, voice_channel: discord.Channel=None):
        """Play an icecast stream."""
        server = ctx.message.server
        author = ctx.message.author
        if url is None:
            await bot.say('What url?')
            urlm = await bot.wait_for_message(timeout=35, author=author)
            if urlm is None:
                await bot.say("Provide a valid URL next time.")
                return
            url=urlm.content

        if voice_channel is None:
            voice_channel = author.voice_channel
        if voice_connected(server):
            await bot.say(
                "Already connected to a voice channel, use `r!stop` to stop the radio.")
        else:
            Channel = ctx.message.channel
            await bot.say("Fetching stream...")
            voice = await bot.join_voice_channel(voice_channel)
            player = voice.create_ffmpeg_player(url)
            player.start()
        ip = IcyParser()
        ip.getIcyInformation(url)
        await asyncio.sleep(5)
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

    @bot.command(pass_context=True, no_pm=True)
    async def stop(ctx):
        """Stops playback."""
        server = ctx.message.server
        author = ctx.message.author
        await _disconnect_voice_client(server)
        await bot.say("Stopping playback...")

    @bot.command(pass_context=True, aliases=["nowplaying", "song"], no_pm=True)
    async def np(ctx, url=None):
        """Now playing."""
        author = ctx.message.author
        if url is None:
            await bot.say('What url?')
            urlm = await bot.wait_for_message(timeout=35, author=author)
            if urlm is None:
                await bot.say("Provide a valid URL next time.")
                return
            url=urlm.content
        ip = IcyParser()
        await bot.say("Fetching Song Information...")
        try:
            ip.getIcyInformation(url)
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
    async def ping(ctx):
        """Pong."""
        channel = ctx.message.channel
        t1 = time.perf_counter()
        await bot.send_typing(channel)
        t2 = time.perf_counter()
        await bot.say("Pong: {}ms".format(round((t2-t1)*1000)))

    @bot.command(pass_context=True)
    async def sharedservers(ctx, user : discord.Member = None):
        """[Owner] Shows shared server info. Defaults to author."""
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

    # @bot.command()
    # async def status(url):
        # ip = IcyParser()   
        # ip.getIcyInformation(url)
        # await asyncio.sleep(5)
        # game = ip.icy_streamtitle
        # game = game.replace("';StreamUrl='", "")
        # if game is None:
            # return
        # else:
            # await bot.change_presence(game=game)
        # ip.stop()

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
