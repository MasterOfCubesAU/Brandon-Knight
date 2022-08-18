from discord.ext import commands
from lib.bot import BrandonKnight, Cog_Exemptions, COGS
from datetime import datetime
from discord import Embed
from .. import db as BrandonKnight_DB

class CogManager(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    def reload_cogs(self):
        #self.other_cog = self.bot.get_cog("OtherCog")
        if not self.bot.ready: #and self.other_cog
            self.bot.cogs_ready.ready_up("CogManager")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("CogManager")

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def cog(self, ctx):
        embed = Embed(description="Below lists enabled/disabled modules.", timestamp=datetime.utcnow(), colour=0x2874A6).set_author(name="COG MANAGER", icon_url=self.bot.appinfo.icon_url)
        embed.add_field(name="Enabled", value=">>> {}".format('\n'.join([x for x in self.bot.cogs])), inline=True)
        if [x for x in COGS if x not in self.bot.cogs]:
            embed.add_field(name="Disabled", value=">>> {}".format('\n'.join([x for x in COGS if x not in self.bot.cogs])), inline=True)
        embed.add_field(name="\u200b", value=f"You may also use the following command to manage cogs.\n> `/cog [load|unload|reload] [cog*]`", inline=False)
        await ctx.send(embed=embed, delete_after=10)

    @cog.command()
    @commands.has_permissions(manage_guild=True)
    async def load(self, ctx, *extensions):
        for extension in extensions:
            try:
                self.bot.load_extension(f"lib.cogs.{extension}")
            except Exception as error:
                embed=Embed(title=None, description=f"Could not load {extension}. [{error}]", timestamp=datetime.utcnow(), colour=0x2874A6)
                await ctx.send(embed=embed, delete_after=10)
            else:
                embed=Embed(title=None, description=f"{extension} has loaded", timestamp=datetime.utcnow(), colour=0x2874A6)
                await ctx.send(embed=embed, delete_after=10)

    @cog.command()
    @commands.has_permissions(manage_guild=True)
    async def unload(self, ctx, *extensions):
        for extension in extensions:
            try:
                self.bot.unload_extension(f"lib.cogs.{extension}")
            except Exception as error:
                embed=Embed(title=None, description=f"Could not unload {extension}. [{error}]", timestamp=datetime.utcnow(), colour=0x2874A6)
                await ctx.send(embed=embed, delete_after=10)
            else:
                embed=Embed(title=None, description=f"{extension} has been unloaded", timestamp=datetime.utcnow(), colour=0x2874A6)
                await ctx.send(embed=embed, delete_after=10)

    @cog.command()
    @commands.has_permissions(manage_guild=True)
    async def reload(self, ctx, *extensions):
        for extension in extensions:
            try:
                self.bot.reload_extension(f"lib.cogs.{extension}")
            except Exception as error:
                embed=Embed(title=None, description=f"Could not reload {extension}. [{error}]", timestamp=datetime.utcnow(), colour=0x2874A6)
                await ctx.send(embed=embed, delete_after=10)
            else:
                embed=Embed(title=None, description=f"{extension} has reloaded", timestamp=datetime.utcnow(), colour=0x2874A6)
                await ctx.send(embed=embed, delete_after=10)


    @load.error
    @unload.error
    @reload.error
    @cog.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CheckFailure):
            LowPermsEMBED = Embed(title=None, description="{}, you do not have the correct permissions to execute this command!".format(ctx.message.author.mention), timestamp=datetime.utcnow(), colour=0x2874A6)
            LowPermsEMBED.set_author(name="BOT ERROR", icon_url=self.bot.appinfo.icon_url)

            await ctx.send(embed=LowPermsEMBED, delete_after=10)
        else:
            raise error


def setup(bot):
    bot.add_cog(CogManager(bot))
