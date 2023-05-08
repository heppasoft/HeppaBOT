import modules
import discord
import typing as t
from modules import constants
from discord.ext import commands


class Dev(modules.MyCog):
    def __init__(self, client: modules.MyBot) -> None:
        self.client = client
        
        self.update_params(roles=[constants.ADMIN_ROLE], channels=[constants.SERVER_BOT_DEV_CHANNEL_ID])
    
    
    @commands.command(name="log", help="Girilen metni konsolda gösterir.", channels="all")
    async def bott_log(self, ctx: commands.Context, *metin: str):
        """ Displays the entered text on the console. """

        text = " ".join(metin)
        await ctx.message.delete()
        modules.log(text)
    
    
    @commands.command(name="log_message", help="\"message\" değişkenini konsolda gösterir.", channels="all")
    async def log_message(self, ctx: commands.Context):
        """ Displays the message variable in the console. """

        await ctx.message.delete()
        modules.log(ctx.message)


def setup(client: modules.MyBot):
    client.add_cog(Dev(client))