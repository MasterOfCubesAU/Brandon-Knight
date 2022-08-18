from discord.ext import commands
from lib.bot import BrandonKnight
from discord import Embed, Object
from .. import db as BrandonKnight_DB

class GuildEvents(commands.Cog):

    BenchwarmerRole = Object(id=806493252194533377)

    def __init__(self, bot):
        self.bot = bot
        #self.other_cog = bot.get_cog("OtherCog")

    def reload_cogs(self):
        #self.other_cog = self.bot.get_cog("OtherCog")
        if not self.bot.ready: #and self.other_cog
            self.bot.cogs_ready.ready_up("GuildEvents")

    # def cog_unload(self):
    #     self.COG.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready: #and self.other_cog
            self.bot.cogs_ready.ready_up("GuildEvents")

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not member.bot:
            await member.add_roles(self.BenchwarmerRole, reason="New Member")



def setup(bot):
    bot.add_cog(GuildEvents(bot))
