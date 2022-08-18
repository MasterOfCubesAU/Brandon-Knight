from discord.ext.commands import Bot as BotBase
from .. import db as BrandonKnight_DB
from os.path import abspath, dirname
from asyncio import sleep
from glob import glob
import requests
import datetime
import discord
import asyncio
import os
import yaml


COGS = [path.split("/")[-1][:-3] for path in glob("./lib/cogs/*.py")]
Cog_Exemptions = []

with open("./config.yml", "r") as f:
    config = yaml.safe_load(f)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS if cog not in Cog_Exemptions])

    def is_ready(self, cog):
        return getattr(self, cog)

class BrandonKnight(BotBase):
    def __init__(self):
        self.cogs_ready = Ready()
        self.ready = False
        intents = discord.Intents.all()
        super().__init__(command_prefix="/", intents=intents)

    def setup(self):
        for cog in COGS:
            if cog not in Cog_Exemptions:
                try:
                    self.load_extension(f"lib.cogs.{cog}")
                except Exception as error:
                    print(f"Could not load {cog} cog. [{error}]")

    def run(self, version):
        self.VERSION = version
        self.setup()
        super().run(config["TOKENS"]["PRODUCTION"], reconnect=True)

    async def on_connect(self):
        self.appinfo = await super().application_info()

    async def on_disconnect(self):
        pass

    async def on_ready(self):
        if not self.ready:
            timer = 1
            while not self.cogs_ready.all_ready():
                # await sleep(timer)
                print(f">>> Waiting for {[cog for cog in self.cogs if self.cogs_ready.is_ready(cog) is False]} cog(s).")
                super().get_cog([cog for cog in self.cogs if self.cogs_ready.is_ready(cog) is False][0]).reload_cogs()
                timer += 2
            os.system('cls' if os.name == 'nt' else 'clear')
            self.ready = True
            print("I am connected on {} | d.py v{} | IP: {} | DB Connection Status: {}".format(self.user.name, str(discord.__version__), requests.get('https://api.ipify.org').text, True))
            print ("BOT STARTED: {}".format(datetime.datetime.now().strftime("%I:%M:%S%p | %d/%m/%Y")))

    async def on_message(self, message):
        if not message.author.bot:
            if isinstance(message.channel, discord.DMChannel):
                pass
            else:
                await self.process_commands(message)

    async def on_command(self, ctx):
        await ctx.message.delete()



BrandonKnight = BrandonKnight()
