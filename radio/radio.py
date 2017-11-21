import discord
import json
from discord.ext import commands
import asyncio
from icyparser import IcyParser

with open("config.json") as f:
    data = json.load(f)
    token = data["token"]

    bot = commands.Bot(command_prefix='r!', description='''Radio''')


    @bot.event
    async def on_ready():
        print('------')
        print('Logged in as')
        print(bot.user.name)
        print(bot.user.id)
        print('------')
        loop = bot.loop.create_task(status_loop())


    @bot.command(pass_context=True, no_pm=True)
    async def play(ctx, url, voice_channel: discord.Channel = None):
        """Play an icecast stream."""
        server = ctx.message.server
        author = ctx.message.author
        if voice_channel is None:
            voice_channel = author.voice_channel
        if voice_connected(server):
            await bot.say(
                "Already connected to a voice channel, use `ar!stop` to stop the radio.")
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

#  Not implemented yet. Kinda halfway there, was going to fine tune it later and add counting of server players, ie self.players
    async def status_loop():
        playing = {}
        for server in bot.servers:
            if server.id not in self.players:
                self.players[server.id] = None
        playing_servers = 0
            for server in playing:
                playing_servers += 1
            if playing_servers == 0:
                pass
            elif playing_servers == 1:
                try:
                    ip = IcyParser()
                    ip.getIcyInformation(url)
                    await asyncio.sleep(5)
                    streamtitle = ip.icy_streamtitle
                    if streamtitle is None:
                        ip.stop()
                        return
                    else:
                        streamtitle = str(streamtitle).replace(';StreamUrl=', '')
                        streamtitle = str(streamtitle).replace("'", "")
                        await bot.change_presence(game=discord.Game(name=streamtitle, type=2))
                except:
                    pass
            else:
                status = "music on {0} servers".format(playing_servers)
                await bot.change_presence(game=discord.Game(name=status, type=0))
        await asyncio.sleep(30)

    @bot.command()
    async def nowplaying(url):
        """Get the playing song!"""
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
        await bot.say("Now Playing: {}".format(streamtitle))
        ip.stop()


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

    # @bot.command(pass_context=True, no_pm=True)
    # async def shutdown(ctx):
        # """Stops playback."""
        # await _disconnect_voice_client(server)
        # await bot.say("Shutting down...")
        # loop.cancel()
        # await bot.shutdown()      #  lol there is no bot.shutdown wtf


    bot.run(token)
