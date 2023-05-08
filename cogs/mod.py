import asyncio
import modules
import discord
import typing as t
from modules import constants
from discord.ext import commands


class Mod(modules.MyCog):
    def __init__(self, client: modules.MyBot) -> None:
        self.client = client
        
        self.update_params(roles=[constants.ADMIN_ROLE])
    
    
    @commands.command(name="setup", help="Bot ilk kurulum.", channels=[constants.SERVER_BOT_MOD_CHANNEL_ID])
    async def bott_setup(self, ctx: commands.Context):
        view = modules.VerifyView()
        channel = modules.get(ctx.guild.channels, id=constants.SERVER_WELCOME_CHANNEL_ID)
        await channel.send("Lütfen hesabınızı doğrulayın.", view=view)
    
    
    @commands.command(name="bot_mesaj", aliases=["b_m"], help="Bot ile mesaj göndermek için.", channels=[constants.SERVER_BOT_MOD_CHANNEL_ID])
    async def bott_message(self, ctx: commands.Context, channel: t.Optional[discord.TextChannel], *, content: str):
        """ To send a message with the bot. """

        await ctx.message.delete()

        if channel is None:
            channel = ctx.channel

        await channel.send(content)


    @commands.command(name="bot_embed_mesaj", aliases=["b_e_m"], help="Bot ile embed mesaj göndermek için.", channels=[constants.SERVER_BOT_MOD_CHANNEL_ID])
    async def bott_embed_message(self, ctx: commands.Context, channel: t.Optional[discord.TextChannel]):
        """ To send embed messages with bot. """

        embed_data = modules.load_json_file("datas/embed.json")

        embed = modules.create_embed(embed_data["options"]["title"], embed_data["options"]["description"])

        for field in embed_data:
            if field == "options":
                continue

            embed.add_field(field, embed_data[field][0], embed_data[field][1])

        await ctx.message.delete()

        if channel is None:
            channel = ctx.channel

        await channel.send(embed=embed)
    
    
    @commands.command(name="bot_duyuru", aliases=["b_d"], help="Bot ile duyuru yayınlamak için.", channels=[constants.SERVER_BOT_MOD_CHANNEL_ID])
    async def bott_duyuru(self, ctx: commands.Context, mentione_everyone: t.Optional[bool] = False, *, content: str):
        """ To post an announcement with the bot. """

        channel = ctx.guild.get_channel(constants.SERVER_ANNOUNCEMENT_CHANNEL_ID)

        if channel is None:
            return

        await ctx.message.delete()

        if mentione_everyone:
            await channel.send(f"{content}\n@everyone")
        else:
            await channel.send(content)
    
    
    @commands.command(name="bot_embed_duyuru", aliases=["b_e_d"], help="Bot ile embed duyuru yayınlamak için.", channels=[constants.SERVER_BOT_MOD_CHANNEL_ID])
    async def bott_embed_duyuru(self, ctx: commands.Context, mentione_everyone: t.Optional[bool] = False):
        """ To post an embed announcement with the bot. """

        channel: discord.TextChannel = ctx.guild.get_channel(constants.SERVER_ANNOUNCEMENT_CHANNEL_ID)

        if channel is None:
            return

        embed_data = modules.load_json_file("datas/embed.json")
        fields = embed_data["fields"]

        embed = modules.create_embed(embed_data["options"]["title"], embed_data["options"]["description"])

        for field in fields:
            inline = field["inline"] if "inline" in field else None
            embed.add_field(field["name"], field["value"], inline)

        await ctx.message.delete()

        if mentione_everyone:
            await channel.send("@everyone", embed=embed)
        else:
            await channel.send(embed=embed)


    @commands.command(name="bot_dm", aliases=["b_dm"], help="Bot ile DM göndermek için.", channels=[constants.SERVER_BOT_MOD_CHANNEL_ID])
    async def bott_dm(self, ctx: commands.Context, member: discord.Member, *, content: str):
        """ To send DM with bot. """

        content += f"\n\n```NOT: {constants.BOT_NAME}'a Atılan Mesajlar Bize Ulaşmamaktadır.```"

        await ctx.message.delete()

        await member.create_dm()

        await member.dm_channel.send(content)


    @commands.command(name="message_count", aliases=["mesaj_sayısı"], help="Metin kanalındaki toplam mesaj sayısını döndürür.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def message_count(self, ctx: commands.Context, channel: t.Optional[discord.TextChannel]):
        """ Returns the total number of messages in the text channel. """
        
        await ctx.message.delete()

        if channel is None:
            channel = ctx.channel
        
        messages = await channel.history(limit=None).flatten()

        await ctx.send(f"{channel.mention} kanalında toplam {len(messages)} mesaj bulunuyor.", delete_after=5)


    @commands.command(name="clear", aliases=["temizle", "c"], help="Metin kanalını temizler.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def clear(self, ctx: commands.Context, limit=100, channel: t.Optional[discord.TextChannel] = None):
        """ Clears the text channel. """
        
        await ctx.message.delete()

        if channel is None:
            channel = ctx.channel
            
        messages = await channel.history(limit=limit).flatten()

        await channel.delete_messages(messages)
        await asyncio.sleep(1)
        await ctx.send(f"{channel.mention} kanalından toplam {len(messages)} mesaj temizlendi.", delete_after=5)


    @commands.command(name="ban", aliases=["yasakla"], help="Bir kullanıcıyı sunucudan yasaklama.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def ban(self, ctx: commands.Context, member: discord.Member, *, reason: t.Optional[str]):
        """ Ban a user from the server. """
        
        channel = ctx.guild.get_channel(constants.SERVER_ANNOUNCEMENT_CHANNEL_ID)

        await member.ban(reason=reason)
        await channel.send(f"{member.mention} {ctx.message.author} tarafından sunucudan banlandı.")


    @commands.command(name="unban", aliases=["yasak_kaldır"], help="Bir kullanıcının sunucudaki yasağını kaldırın.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def unban(self, ctx: commands.Context, *, member):
        """ Unban a user from the server. """
        
        channel = ctx.guild.get_channel(constants.SERVER_ANNOUNCEMENT_CHANNEL_ID)

        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split("#")

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await channel.send(f"{user.mention} kullanıcısının sunucu banı {ctx.message.author} tarafından kaldırıldı.")
                return

        raise commands.MemberNotFound(member)


    @commands.command(name="kick", aliases=["at"], help="Bir kullanıcıyı sunucudan atın.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def kick(self, ctx: commands.Context, member: discord.Member, *, reason: t.Optional[str]):
        """ Kick a user from the server. """
        
        channel = ctx.guild.get_channel(constants.SERVER_ANNOUNCEMENT_CHANNEL_ID)

        await member.kick(reason=reason)
        await channel.send(f"{member.mention} {ctx.message.author} tarafından sunucudan atıldı.")
    
    
    @commands.command(name="add_role", aliases=["rol_ekle"], help="Kullanıcıya bir rol ekler.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def add_role(self, ctx: commands.Context, role: discord.Role, member: discord.Member, *, reason: t.Optional[str]):
        """ Add a role to the user. """
        
        channel = ctx.guild.get_channel(constants.SERVER_BOT_MOD_CHANNEL_ID)

        await ctx.message.delete()

        if modules.has_ayn_role(member, role.name):
            embed = modules.create_embed(":x: İşlem Başarısız", "Kullanıcı zaten bu role sahip.")
            await channel.send(embed=embed)
            return
        else:
            await member.add_roles(role, reason=reason)

            embed = modules.create_embed(":white_check_mark: İşlem Başarılı", f"{role.name} rolü {member.mention} kullanıcısına eklendi.")
            await channel.send(embed=embed)
            return
        
        
    @commands.command(name="remove_role", aliases=["rol_kaldır"], help="Kullanıcıdan bir rolü kaldırır.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def remove_role(self, ctx: commands.Context, role: discord.Role, member: discord.Member, *, reason: t.Optional[str]):
        """ Removes a role from the user. """
        
        channel = ctx.guild.get_channel(constants.SERVER_BOT_MOD_CHANNEL_ID)

        await ctx.message.delete()

        if not modules.has_ayn_role(member, role.name):
            embed = modules.create_embed(":x: İşlem Başarısız", "Kullanıcı zaten bu role sahip değil.")
            await channel.send(embed=embed)
            return
        else:
            await member.remove_roles(role, reason=reason)

            embed = modules.create_embed(":white_check_mark: İşlem Başarılı", f"{role.name} rolü {member.mention} kullanıcısından kaldırıldı.")
            await channel.send(embed=embed)
            return
    
    
    @commands.command(name="başvuru_listesi", aliases=["b_l"], help="Onay bekleyen üniversite rolü başvurularını listeler.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def basvuru_list(self, ctx: commands.Context):
        """ Lists pending university role applications. """
        
        channel = ctx.guild.get_channel(constants.SERVER_BOT_MOD_CHANNEL_ID)

        res = self.client.db.execute("SELECT * FROM applications")
        applications = res.fetchall()
        
        embed = modules.create_embed(":information_source: Bekleyen Başvurular:", "")

        if applications is None:
            await channel.send("Şuanda onay bekleyen başvuru bulunmamakta.")
        else:
            applications_msg = ""
            for application in applications:
                member: discord.Member = modules.get(ctx.guild.members, id=application[0])
                applications_msg += f"Kullanıcı: **{member.mention}**\nOnay Kodu: **{application[4]}**\n\n"
                
            embed.add_field("", applications_msg)

            await channel.send(embed=embed)
    
    
    @commands.command(name="başvuru_iptal", help="Üniversite rolü başvurunuzu iptal edin.", roles=[constants.MODERATOR_ROLE], channels="all")
    async def basvuru_ıptal(self, ctx: commands.Context, member: t.Optional[discord.Member]):
        """ Cancel your university role application. """
        
        channel = ctx.guild.get_channel(constants.SERVER_BOT_MOD_CHANNEL_ID)

        if member is None:
            member = ctx.author

        user_id = member.id
        
        res = self.client.db.execute("SELECT * FROM applications WHERE id=?",(user_id,))
        application = res.fetchone()

        if application is None:
            embed = modules.create_embed(":x: İşlem Başarısız", f"{member.mention} | Başvuru bulunamadı.")
            await channel.send(embed=embed)
            return

        await ctx.message.delete()

        embed = modules.create_embed(":white_check_mark: İşlem Başarılı", f"{member.mention} | Başvuru iptal edilmiştir.")
        await channel.send(embed=embed)

        self.client.db.execute("DELETE FROM applications WHERE id=?", (user_id,))
        self.client.db.commit()

def setup(client: modules.MyBot):
    client.add_cog(Mod(client))