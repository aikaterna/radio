import discord
from discord.ext import commands

owner_id = "154497072148643840"

class Servers:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def listchannels(self, ctx, server_id):
        """[Owner] Lists channels."""
        server = self.bot.get_server(server_id)
        msg = "```ini\n"
        # msg += "\n"
        count = 0
        if ctx.message.author.id == owner_id:
            for channel in server.channels:
                if channel.type != "voice":
                    channelname = channel.name.replace("_", "-")
                    msg += "{} [ {} ]\n".format(channel.id, channelname)
                    count += 1
        await self.bot.say("{} has {} channels:".format(server.name, count))
        await self.bot.say(msg + "```")

    @commands.command(pass_context=True)
    async def listservers(self, ctx):
        """[Owner] Lists servers."""
        servers = self.bot.servers
        await self.bot.say("```ini\nThe bot is in the following {} server(s):\n```".format(str(len(self.bot.servers))))
        msg = "```ini\n"
        msg2 = "```ini\n"
        msg3 = "```ini\n"
        msg4 = "```ini\n"
        # msg += "\n"

        messages = [msg, msg2, msg3, msg4]
        count = 0
        if ctx.message.author.id == owner_id:
            for server in servers:
                if len(server.members) < 10:
                    messages[count] += "{:<1} [ 000{} users ] {}".format(server.id, len(server.members), server.name)
                elif len(server.members) < 100:
                    messages[count] += "{:<1} [ 00{} users ] {}".format(server.id, len(server.members), server.name)
                elif len(server.members) < 1000:
                    messages[count] += "{:<1} [ 0{} users ] {}".format(server.id, len(server.members), server.name)
                else:
                    messages[count] += "{:<1} [ {} users ] {}".format(server.id, len(server.members), server.name)
                messages[count] += "\n"
                if len(messages[count]) > 1500:
                    count = count + 1

        for message in messages:
            if len(message) > 30:
                await self.bot.say(message + "\n```")

    @commands.command(pass_context=True)
    async def sharedservers(self, ctx, user: discord.Member=None):
        """[Owner] Shows shared server info."""
        author = ctx.message.author
        server = ctx.message.server
        if ctx.message.author.id == owner_id:
            if not user:
                user = author
            seen = len(set([member.server.name for member in self.bot.get_all_members() if member.name == user.name]))
            sharedservers = str(set([member.server.name for member in self.bot.get_all_members() if member.name == user.name]))
            for shared in sharedservers:
                shared = "".strip("'").join(sharedservers).strip("'")
                shared = shared.strip("{").strip("}")
            data = "```ini\n"
            data += "[Servers]:     {} shared\n".format(seen)
            data += "[In Servers]:  {}```".format(shared)
            await self.bot.say(data)

		
def setup(bot):
    bot.add_cog(Servers(bot))
