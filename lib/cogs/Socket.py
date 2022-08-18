from discord.ext import commands, tasks
from datetime import datetime
from lib.bot import BrandonKnight
from discord import Embed, Object
from .. import db as BrandonKnight_DB
import asyncio
import socket
from socket import socket as Socket
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Callable

from discord.ext import commands, tasks

class Socket(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.thread_pool = ThreadPoolExecutor(5)
        self.buffer_size = 5000
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(('0.0.0.0', 10231))
        self.server.listen(8)
        self.server.setblocking(False)
        self._start_server()
        #self.other_cog = bot.get_cog("OtherCog")

    def reload_cogs(self):
        self.Registration = self.bot.get_cog("Registration")
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Socket")

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("Socket")

    async def paymentSuccess(self, userID, code, orderID):
        paymentSuccessEmbed = Embed(description=f"Thank you for your payment! On the day of the event, simply present the code below to our coordinator on the day to gain entry into the court. See you there!\n\n>>> **CODE: {code}**", timestamp=datetime.utcnow(), colour=0x00ff00)
        paymentSuccessEmbed.set_footer(text=orderID)
        user = self.bot.get_guild(806490820889935892).get_member(int(userID))
        ID = BrandonKnight_DB.field("SELECT ID FROM Registrants WHERE Registrant = ?", int(userID))
        await self.updateRoster(ID)
        await user.send(embed=paymentSuccessEmbed)

    async def updateRoster(self, ID):
        guild = self.bot.get_guild(806490820889935892)
        roster = BrandonKnight_DB.record("SELECT * FROM Rosters WHERE ID = ?", ID)
        rosterMessage = await self.bot.get_channel(roster[3]).fetch_message(roster[2])
        query = BrandonKnight_DB.records("SELECT * FROM Registrants WHERE ID = ?", ID)
        embed = rosterMessage.embeds[0]
        newText = ">>> "
        for row in query:
            user = guild.get_member(row[1])
            newText += ("• {} [{}]\n{}".format("{}".format(f"{user} ({user.nick})" if user.nick else user), user.id, ("NOT PAID []" if row[2] is None else f"PAID [{row[2]}]")) if newText == ">>> " else "\n\n• {} [{}]\n{}".format("{}".format(f"{user} ({user.nick})" if user.nick else user), user.id, ("NOT PAID []" if row[2] is None else f"PAID [{row[2]}]")))
        if newText == ">>> ":
            newText = ">>> Roster empty. Once a user has registered, they will appear here."
        embed.set_field_at(0, name="\u200b", value=newText)
        await rosterMessage.edit(embed=embed)

    async def _complete_in_thread(self, func: Callable):
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.thread_pool, func)

    async def handle_client(self, socket: Socket):
        data = None
        while data is None:
            try:
                data = await asyncio.gather(self._complete_in_thread(lambda: socket.recv(self.buffer_size)))
            except Exception as e:
                pass
            else:
                data = data[0].decode("utf-8").split(";")
                await self.paymentSuccess(data[0], data[1], data[2])
                await asyncio.sleep(5)
                socket.close()

    async def _server_loop(self):
        while True:
            client, _ = await self.loop.sock_accept(self.server)
            self.loop.create_task(self.handle_client(client))

    def _start_server(self):
        self.loop = asyncio.get_event_loop()
        self.loop.create_task(self._server_loop())

def setup(bot):
    bot.add_cog(Socket(bot))
