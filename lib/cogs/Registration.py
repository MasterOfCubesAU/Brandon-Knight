from discord.ext import commands
from lib.bot import BrandonKnight
from discord import Embed, Object, DMChannel
from .. import db as BrandonKnight_DB
from asyncio import sleep
import datetime
import uuid

class Registration(commands.Cog):

    rosterChannelID = 811555017869361152

    def __init__(self, bot):
        self.bot = bot
        #self.other_cog = bot.get_cog("OtherCog")

    def reload_cogs(self):
        #self.other_cog = self.bot.get_cog("OtherCog")
        if not self.bot.ready: #and self.other_cog
            self.bot.cogs_ready.ready_up("Registration")

    # def cog_unload(self):
    #     self.COG.stop()

    async def createRoster(self, ID, registrants, type):
        if type == "PROPOSED":
            if registrants:
                rosterEmbed = Embed(title="PROPOSED ROSTER", description=f"Registration {ID} has concluded.", timestamp=datetime.datetime.utcnow(), colour=0xffa500)
                rosterEmbed.add_field(name="\u200b", value="```{}```".format('\n'.join('{0}. {1}'.format(num, "{}".format(f"{name} ({name.nick})" if name.nick else name)) for num, name in enumerate(registrants, start=1))))
                rosterEmbed.set_footer(text=ID)
                rosterMessage = await self.bot.get_channel(self.rosterChannelID).send(embed=rosterEmbed)
                BrandonKnight_DB.execute("INSERT INTO Rosters (ID, Type, MessageID, ChannelID) VALUES (?, ?, ?, ?)", ID, type, rosterMessage.id, rosterMessage.channel.id)
                await rosterMessage.add_reaction("✅")
                await rosterMessage.add_reaction("❎")
        elif type == "CONFIRMED":
            if registrants:
                rosterEmbed = Embed(title="CONFIRMED ROSTER", description=f"Roster {ID} has been finalised.", timestamp=datetime.datetime.utcnow(), colour=0x00ff00)
                rosterEmbed.add_field(name="\u200b", value="```{}```".format('\n'.join('{0}. {1}'.format(num, "{}".format(f"{name} ({name.nick})" if name.nick else name)) for num, name in enumerate(registrants, start=1))))
                rosterEmbed.set_footer(text=ID)
                rosterMessage = await self.bot.get_channel(self.rosterChannelID).send(embed=rosterEmbed)
                return rosterMessage.id, rosterMessage.channel.id

    async def paymentSuccess(self, userID: int, code):
        paymentSuccessEmbed = Embed(description=f"Thank you for your payment! On the day of the event, simply present the code below to one of our coordinators to gain entry into the court. See you there!\n\n>>> **CODE: {code}**", timestamp=datetime.datetime.utcnow(), colour=0x00ff00)
        await self.bot.get_guild(806490820889935892).get_member(userID).send(embed=paymentSuccessEmbed)


    @commands.Cog.listener()
    async def on_ready(self):
        if not self.bot.ready: #and self.other_cog
            self.bot.cogs_ready.ready_up("Registration")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction = payload.emoji
        if not isinstance(channel, DMChannel):
            message_id = payload.message_id
            guild = self.bot.get_guild(channel.guild.id)
            user = guild.get_member(payload.user_id)
            message_obj = await channel.fetch_message(message_id)
            if not user.bot:
                if message_id in BrandonKnight_DB.column("SELECT MessageID FROM Registration"):
                    BrandonKnight_DB.execute("INSERT INTO Registrants (ID, Registrant) VALUES (?, ?)", message_obj.embeds[0].footer.text, user.id)
                    registerSuccessEmbed = Embed(description="Thankyou! Your expression of interest has been confirmed. A confirmation message will be sent prior to the event date.\n\n**If you change your mind, you can opt-out by unreacting to the registration message.**\n", timestamp=datetime.datetime.utcnow(), colour=0x00ff00)
                    await user.send(embed=registerSuccessEmbed)
                elif message_id in BrandonKnight_DB.column("SELECT MessageID FROM Rosters"):
                    if str(reaction) == "✅":
                        ID = message_obj.embeds[0].footer.text
                        await message_obj.delete()
                        registrants = BrandonKnight_DB.column("SELECT Registrant FROM Registrants WHERE ID = ?", ID)
                        for member in registrants:
                            rosterConfirmEmbed = Embed(description="Your recent expression of interest resulted in confirmed entry into the roster. Please refer below on how to pay for your entry.\n\nOnce payment has been confirmed, you will receive instructions on what to do on the day.", timestamp=datetime.datetime.utcnow(), colour=0x2874A6)
                            rosterConfirmEmbed.add_field(name="\u200b", value=f"**[PAY HERE](https://mqbc.masterofcubesau.com/pay?id={member})**")
                            await guild.get_member(member).send(embed=rosterConfirmEmbed)
                            await sleep(5)
                        messageID, channelID = await self.createRoster(ID, [self.bot.get_guild(806490820889935892).get_member(name) for name in registrants], "CONFIRMED")
                        BrandonKnight_DB.execute("UPDATE Rosters SET Type = ?, MessageID = ?, ChannelID = ? WHERE ID = ?", "CONFIRMED", messageID, channelID, ID)
                    else:
                        ID = message_obj.embeds[0].footer.text
                        registrants = BrandonKnight_DB.column("SELECT Registrant FROM Registrants WHERE ID = ?", ID)
                        query = BrandonKnight_DB.record("SELECT * FROM Rosters WHERE MessageID = ?", message_id)
                        rosterMessage = await self.bot.get_channel(query[3]).fetch_message(query[2])
                        await rosterMessage.delete()
                        BrandonKnight_DB.execute("DELETE FROM Rosters WHERE MessageID = ?", message_id)
                        BrandonKnight_DB.execute("DELETE FROM Registrants WHERE ID = ?", ID)
                        rosterRejectEmbed = Embed(description="The registration that you recently signed up for has unfortunately been cancelled. We apologise that this has occured.", timestamp=datetime.datetime.utcnow(), colour=0x2874A6)
                        for member in registrants:
                            await guild.get_member(member).send(embed=rosterRejectEmbed)
                            await sleep(5)

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        reaction = payload.emoji
        if not isinstance(channel, DMChannel):
            message_id = payload.message_id
            guild = self.bot.get_guild(channel.guild.id)
            user = guild.get_member(payload.user_id)
            message_obj = await channel.fetch_message(message_id)
            if not user.bot:
                if message_id in BrandonKnight_DB.column("SELECT MessageID FROM Registration"):
                    BrandonKnight_DB.execute("DELETE FROM Registrants WHERE Registrant = ?", user.id)
                    optOutEmbed = Embed(description="You have successfully opted out of the registration.", timestamp=datetime.datetime.utcnow(), colour=0x00ff00)
                    await user.send(embed=optOutEmbed)

    @commands.group(invoke_without_command=False, aliases=["r"])
    @commands.has_permissions(manage_guild=True)
    async def registration(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send(f'{ctx.author.mention}, please use `/register [create|close|delete]`', delete_after=5)

    @registration.command()
    @commands.has_permissions(manage_guild=True)
    async def create(self, ctx):
        ID = str(uuid.uuid4())[:8]
        registerEmbed = Embed(description="React below to express your interest.", timestamp=datetime.datetime.utcnow(), colour=0x2874A6)
        registerEmbed.set_footer(text=ID)
        registerMessage = await ctx.send(embed=registerEmbed)
        BrandonKnight_DB.execute("INSERT INTO Registration (ID, MessageID, ChannelID) VALUES (?, ?, ?)", ID, registerMessage.id, ctx.channel.id)
        await registerMessage.add_reaction("✅")

    @registration.command()
    @commands.has_permissions(manage_guild=True)
    async def close(self, ctx, ID):
        if ID in BrandonKnight_DB.column("SELECT ID FROM Registration"):
            query = BrandonKnight_DB.record("SELECT * FROM Registration WHERE ID = ?", ID)
            registerMessage = await self.bot.get_channel(query[2]).fetch_message(query[1])
            registrants = await registerMessage.reactions[0].users().flatten()
            await self.createRoster(ID, [user for user in registrants if user.bot is False], "PROPOSED")
            await registerMessage.delete()
            BrandonKnight_DB.execute("DELETE FROM Registration WHERE ID = ?", ID)
        else:
            await ctx.send(f'{ctx.author.mention}, the ID `{ID}` does not exist.', delete_after=5)

    @registration.command()
    @commands.has_permissions(manage_guild=True)
    async def delete(self, ctx, ID):
        if ID in BrandonKnight_DB.column("SELECT ID FROM Rosters"):
            query = BrandonKnight_DB.record("SELECT * FROM Rosters WHERE ID = ?", ID)
            if query[1] == "CONFIRMED":
                registerMessage = await self.bot.get_channel(query[3]).fetch_message(query[2])
                await registerMessage.delete()
                BrandonKnight_DB.execute("DELETE FROM Rosters WHERE ID = ?", ID)
                BrandonKnight_DB.execute("DELETE FROM Registrants WHERE ID = ?", ID)
            else:
                await ctx.send(f'{ctx.author.mention}, you can only delete confirmed rosters..', delete_after=5)
        else:
            await ctx.send(f'{ctx.author.mention}, the ID `{ID}` does not exist.', delete_after=5)




def setup(bot):
    bot.add_cog(Registration(bot))
