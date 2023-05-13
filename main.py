import os
import sys
import discord
import modules
import traceback
import typing as t
from modules import constants
from discord.ext import commands


db = modules.SQLDatabase("datas/database.db")

db.execute("CREATE TABLE IF NOT EXISTS bot_configs (name VARCHAR, config VARCHAR)")
db.commit()
db.execute("CREATE TABLE IF NOT EXISTS applications (id INTEGER, email VARCHAR, university VARCHAR, department VARCHAR, verification_code VARCHAR)")
db.commit()

level_meter = modules.LevelMeter(db=db)

chatbot = modules.ChatBot(db=db)

intents = discord.Intents.all()
client = modules.MyBot(command_prefix=constants.COMMAND_PREFIX, intents=intents, level_meter=level_meter, database=db, chatbot=chatbot, is_in_development=True)

cogs: list[str] = []
for dirpath, dirnames, filenames in os.walk("./cogs"):
    cogs.extend(os.path.normpath(os.path.join(dirpath,f)) for f in filenames if f.endswith((".py")))

for c in cogs:
    c = c.replace(os.sep, ".")
    client.load_extension(c[:-3])


@client.event
async def on_ready():
    """ The function that will run when the bot is ready. """

    activity = discord.Activity(type=discord.ActivityType.playing,
                                name=f" {constants.BOT_NAME} | {constants.COMMAND_PREFIX} ")

    await client.change_presence(status=discord.Status.online, activity=activity)

    modules.log(f"Bot {client.user} olarak Discord'a bağlandı!")


@client.event
async def on_member_join(member: discord.Member):
    """ When a new user joins the server, it sends a message on the specified channel. """

    channel = member.guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)

    if member.bot:
        return

    client.level_meter.new_member(member.id)

    if channel is not None:
        await channel.send(f"Aramıza yeni biri katıldı. Sunucumuza hoş geldin {member.mention}.")


@client.event
async def on_member_remove(member: discord.Member):
    """ When a user leaves the server, it sends a message on the specified channel. """

    channel = member.guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)

    if member.bot:
        return

    client.level_meter.delete_member(member.id)

    if channel is not None:
        await channel.send(f"{member.name} aramızdan ayrıldı. Hoşçakal {member.name}.")


async def process_message(message: discord.Message):
    if not message.author.bot:
        try:
            client.level_meter.get_member(message.author.id)
        except modules.errors.UnknownUser:
            client.level_meter.new_member(message.author.id)
            
        if message.content.startswith(client.command_prefix):
            await client.process_commands(message)
        else:
            if modules.has_ayn_role(message.author, [constants.ADMIN_ROLE, constants.MODERATOR_ROLE]):
                client.level_meter.reset_member(message.author.id)
            else:
                await client.level_meter.add_exp_bot(message.guild, message.author.id, constants.LEVEL_METER_MESSAGE_EXP_POINT)
            
            if client.user.mentioned_in(message):
                await message.channel.trigger_typing()
                msg = message.content.replace(f"{client.user.mention} ", "").replace(f" {client.user.mention}", "").replace(f"{client.user.mention}", "")
                res = client.chatbot.chat(msg)
                await message.reply(res)


@client.event
async def on_message(message: discord.Message):
    await process_message(message)


@client.event
async def on_message_edit(messageB: discord.Message, messageA: discord.Message):
    await process_message(messageA)


@client.event
async def on_command_error(ctx: commands.Context, error: t.Union[commands.CommandError, modules.errors.BaseError]):
    """ Sends a message to the user when an error is encountered. """

    if isinstance(error, commands.MissingAnyRole):
        embed = modules.create_embed(":x: İşlem Başarısız", "Bunu yapmaya yetkiniz yok.")
        await ctx.send(embed=embed, delete_after=3)

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = modules.create_embed(":x: İşlem Başarısız", "Lütfen gerekli Paremetreleri girin.\nYardım için \"`help`\" komutunu girin.")
        await ctx.send(embed=embed, delete_after=3)

    elif isinstance(error, commands.CommandNotFound):
        embed = modules.create_embed(":x: İşlem Başarısız", "Bilinmeyen bir komut girdiniz.\nYardım için \"`help`\" komutunu girin.")
        await ctx.send(embed=embed, delete_after=3)

    elif isinstance(error, commands.MemberNotFound):
        embed = modules.create_embed(":x: İşlem Başarısız", "Kullanıcı bulunamadı.")
        await ctx.send(embed=embed, delete_after=3)
    
    elif isinstance(error, modules.errors.InvalidCommandChannel):
        embed = modules.create_embed(":x: İşlem Başarısız", "Hatalı kanal. Lütfen komutu doğru kalanda kullandığınızdan emin olun.")
        await ctx.send(embed=embed, delete_after=4)

    else:
        embed = modules.create_embed(":x: İşlem Başarısız", "Bir hata oluştu.")
        embed.add_field("Hata:", f"{str(error)}")
        embed.add_field(":information_source: Bilgilendirme", "Hata yetkili kişilere bildirildi.")
        await ctx.send(embed=embed, delete_after=3)

        channel = modules.get(ctx.guild.channels, id=constants.SERVER_BOT_MOD_CHANNEL_ID)
        admin_role = modules.get(ctx.guild.roles, name=constants.ADMIN_ROLE)
        mod_role = modules.get(ctx.guild.roles, name=constants.MODERATOR_ROLE)
        if channel is not None:
            err_embed = modules.create_embed(":warning: Bir Hata Oluştu",
                                            f"Komutu Giren: {ctx.author.mention}\nKomut: {ctx.command.name}\nHata: {str(error)}\nHata Sınıfı: {error.__class__.__name__}")
            await channel.send(f"{admin_role.mention} {mod_role.mention}", embed=err_embed)

    if client.is_in_development:
        tb = "".join(traceback.format_tb(error.__traceback__))
        modules.log(f"{tb if tb != '' else str(error)}", "error")
        print(str(error))


def main():
    client.run(os.getenv("BOT_TOKEN"))


if __name__ == "__main__":
    main()