from discord.ext import commands
from lib.bot import BrandonKnight
from discord import Embed
from .. import db as BrandonKnight_DB

class Commands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        #self.other_cog = bot.get_cog("OtherCog")

    def reload_cogs(self):
        #self.other_cog = self.bot.get_cog("OtherCog")
        if not self.bot.ready: #and self.other_cog
            self.bot.cogs_ready.ready_up("Commands")

    # def cog_unload(self):
    #     self.COG.stop()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready: #and self.other_cog
            self.bot.cogs_ready.ready_up("Commands")

    @commands.command()
    async def hi(self, ctx):
        await ctx.send(f"Hello, {ctx.author.mention}", delete_after=10)



def setup(bot):
    bot.add_cog(Commands(bot))
