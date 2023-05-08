import modules
import discord
import typing as t
from modules import constants
from discord.ext import commands


class Gen(modules.MyCog):
    def __init__(self, client:modules.MyBot) -> None:
        self.client = client
    
    
    @commands.command(name="selamla", help="Mesajı gönderen kişiyi ya da etiketlenen kişiyi selamlar.")
    async def greeting(self, ctx: commands.Context, member: t.Optional[discord.Member]):
        """ Greets the person who sent the message or the person tagged. """

        if member is None:
            member = ctx.author

        await ctx.message.delete()

        text = f":heart_eyes: :heart_eyes: :heart_eyes:\nSelaaammm {member.mention}"

        await ctx.send(text)
    
    
    @commands.command(name="öneri", help="Öneri kanalında bir öneri oylaması başlatın.")
    async def suggestion_f(self, ctx: commands.Context, *, suggestion: str):
        """ Start a suggestion vote in the suggestion channel. """
        
        channel = ctx.guild.get_channel(constants.SERVER_SUGGESTION_CHANNEL_ID)

        if suggestion == "":
            embed = modules.create_embed(":x: İşlem Başarısız", "Lütfen bir öneri girin.")
            await ctx.send(embed=embed)
            return

        await ctx.message.delete()

        if channel is None:
            return

        embed = modules.create_embed(":information_source: Bilgilendirme", "Yeni Öneri")
        embed.add_field("Öneren:", ctx.author.mention)
        embed.add_field("Öneri:", suggestion)
        
        view = modules.SuggestionView(embed)
        
        await channel.send(embed=embed, view=view)
    
    
    @commands.command(name="başvuru", help="Üniversite rolü için başvurun.", channels=[constants.SERVER_APPLICATIONS_CHANNEL_ID])
    async def basvuru(self, ctx: commands.Context, email: str, university: str, department: str, member: t.Optional[discord.Member]):
        """ Apply for the university role. """

        if member is None:
            member = ctx.author
        
        await ctx.message.delete()

        user_id, user_name = member.id, member.name

        verification_code = modules.generate_random_code()
        
        res = self.client.db.execute("SELECT * FROM applications WHERE id=?",(user_id,))
        application = res.fetchone()

        if modules.has_ayn_role(member, constants.UNIVERSITY_ROLE):
            embed = modules.create_embed(":x: İşlem Başarısız", f"{member.mention} | Zaten \"{constants.UNIVERSITY_ROLE}\" rolünüz bulunmakta.")
            await ctx.send(embed=embed)
            return

        if application is not None:
            embed = modules.create_embed(":x: İşlem Başarısız", f"{member.mention} | Zaten bir başvurunuz bulunmakta, lütfen <#${constants.SERVER_APPLICATIONS_CHANNEL_ID}> kanalında \"başvuru_onay\" komutu ile onaylayın.\nEğer başvuru ile ilgili bir sıkıntı yaşıyorsanız lütfen Yetkililer ile iletişime geçin.")
            await ctx.send(embed=embed)
            return

        if not modules.validate_university_email(email):
            embed = modules.create_embed(":x: İşlem Başarısız", f"{member.mention} | Lütfen geçerli bir üniversite e-posta adresi girin.\nEğer başvuru ile ilgili bir sıkıntı yaşıyorsanız lütfen Yetkililer ile iletişime geçin.")
            await ctx.send(embed=embed)
            return

        res = self.client.db.execute("SELECT * FROM applications WHERE email=?",(email,))
        application = res.fetchone()
        if application is not None:
            embed = modules.create_embed(":x: İşlem Başarısız", f"{member.mention} | Bu email adresi ile daha önce başvuru yapılmış.\nEğer başvuru ile ilgili bir sıkıntı yaşıyorsanız lütfen Yetkililer ile iletişime geçin.")
            await ctx.send(embed=embed)
            return
        
        channel:discord.TextChannel = modules.get(ctx.guild.channels, id=constants.SERVER_APPLICATIONS_CHANNEL_ID)
        modules.send_verifaction_email(user_name, email, verification_code, channel.name)

        self.client.db.execute("INSERT INTO applications VALUES(?, ?, ?, ?, ?)", (user_id, email, university, department, verification_code))
        self.client.db.commit()

        embed = modules.create_embed(":white_check_mark: İşlem Başarılı", f"{member.mention} | Üniversite rolü başvurunuz alınmıştır, lütfen e-posta adresinizi kontrol ediniz.\nEğer başvurunuz iptal etmek istiyorsanız lütfen etkili biri ile iletişime geçin.")
        await ctx.send(embed=embed)
    
    
    @commands.command(name="başvuru_doğrula", aliases=["başvuru_onay"], help="Üniversite rolü başvurunuzu doğrulayın.", channels=[constants.SERVER_APPLICATIONS_CHANNEL_ID])
    async def basvuru_dogrula(self, ctx: commands.Context, verifaction_code: str, member: t.Optional[discord.Member]):
        """ Verify your university role application. """

        if member is None:
            member = ctx.author

        mod_role:discord.Role = modules.get(ctx.guild.roles, name=constants.MODERATOR_ROLE)
        uni_role:discord.Role = modules.get(ctx.guild.roles, name=constants.UNIVERSITY_ROLE)

        channel = ctx.guild.get_channel(constants.SERVER_BOT_MOD_CHANNEL_ID)

        user_id = member.id
        
        res = self.client.db.execute("SELECT * FROM applications WHERE id=?",(user_id,))
        application = res.fetchone()

        if application is None:
            embed = modules.create_embed(":x: İşlem Başarısız", f"{member.mention} | Başvurunuz bulunamadı, lütfen önce <#${constants.SERVER_APPLICATIONS_CHANNEL_ID}> kanalında \"başvuru\" komutu ile başvuruda bulunun.")
            await ctx.send(embed=embed)
            return

        if application[4] != verifaction_code:
            embed = modules.create_embed(":x: İşlem Başarısız", f"{member.mention} | Girdiğiniz kod hatalı, lütfen tekrar deneyiniz.")
            await ctx.send(embed=embed)
            return

        await ctx.message.delete()
        
        await ctx.message.author.add_roles(uni_role)

        embed = modules.create_embed(":white_check_mark: İşlem Başarılı", f"{member.mention} | Başvurunuz onaylanmıştır. Lütfen bir yetkilinin rolünüzü vermesini bekleyin.")
        await ctx.send(embed=embed)

        embed = modules.create_embed(":warning: Üniversite Rolü Başvurusu Onaylandı", f"Başvuran: {member.mention}\nE-Posta Adresi: {application[1]}\nÜniversite: {application[2]}\nBölümü: {application[3]}\nLütfen kullanıcının bölüm rölünün verin.\n{mod_role.mention}")
        await channel.send(embed=embed)

        self.client.db.execute("DELETE FROM applications WHERE id=?", (user_id,))
        self.client.db.commit()


def setup(client: modules.MyBot):
    client.add_cog(Gen(client))