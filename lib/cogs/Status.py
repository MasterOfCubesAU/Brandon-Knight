from discord.ext import commands, tasks
from datetime import datetime
from lib.bot import BrandonKnight
from discord import Embed, Game
from itertools import cycle

class Status(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.statuschange.start()

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Status")

    def reload_cogs(self):
        #self.other_cog = self.bot.get_cog("OtherCog")
        if not self.bot.ready: #and self.other_cog
            self.bot.cogs_ready.ready_up("Status")

    def cog_unload(self):
        self.statuschange.stop()

    @tasks.loop(minutes=2)
    async def statuschange(self):
        await self.bot.change_presence(activity=Game(next(self.statuses)))

    @statuschange.before_loop
    async def before_statuschange(self):
        await self.bot.wait_until_ready()
        self.statuses = cycle(["Space Jam"] + ["MQU Basketball"] + ["Basketball"])

def setup(bot):
    bot.add_cog(Status(bot))
