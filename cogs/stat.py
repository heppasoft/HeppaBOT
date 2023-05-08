import modules
import discord
import typing as t
from io import BytesIO
from modules import constants
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont


class Stat(modules.MyCog):
    def __init__(self, client: modules.MyBot) -> None:
        self.client = client
        self.level_meter:modules.LevelMeter = client.level_meter
    
    def new_exp_bar(self, draw: ImageDraw.ImageDraw, member_id: int, x: int = 65, y: int = 640, width: int = 220, height: int = 25, bg=(85,85,95), fg=(190,190,190)):
        progress = ((self.level_meter.get_member_exp(member_id) / self.level_meter.get_member_next_level_requirements(member_id)) * 100)
        exp_text = f"{self.level_meter.get_member_exp(member_id)}/{self.level_meter.get_member_next_level_requirements(member_id)}"
        font = ImageFont.truetype("datas/assets/Roboto-Bold.ttf", 27)
        w, h = draw.textsize(exp_text, font=font)
        text_x = ((x + width - w) / 1.3)
        # Draw the background
        draw.rectangle((x+(height/2), y, x+width+(height/2), y+height), fill=bg, width=10)
        draw.ellipse((x+width, y, x+height+width, y+height), fill=bg)
        draw.ellipse((x, y, x+height, y+height), fill=bg)
        width = float(progress*width)/100
        # Draw the part of the progress bar that is actually filled
        draw.rectangle((x+(height/2), y, x+width+(height/2), y+height), fill=fg, width=10)
        draw.ellipse((x+width, y, x+height+width, y+height), fill=fg)
        draw.ellipse((x, y, x+height, y+height), fill=fg)
        draw.text((text_x, y-3), exp_text, font=font, fill=(0,0,0))
    
    @commands.command(name="profil", aliases=["profile", "p"], help="Kullanıcının profilini gösterir.")
    async def profile(self, ctx: commands.Context, member: t.Optional[discord.Member] = None):
        """ Displays the user's profile. """

        if member is None:
            member: discord.Member = ctx.author

        name, nick, status = str(member), member.display_name, str(member.status)

        status = status.replace("online", "Çevrimiçi").replace("offline", "Çevrimdışı").replace("idle", "Boşta")
        status = status.replace("dnd", "Rahatsız Etmeyin").replace("do_not_disturb¶", "Rahatsız Etmeyin").replace("invisible", "Görünmez")

        if member.bot:
            rank, level, exp = "-", "-", "-"
        elif modules.has_ayn_role(member, [constants.ADMIN_ROLE, constants.MODERATOR_ROLE]):
            rank, level, exp = "-", "-", "-"
        else:
            rank, level, exp = f"{self.level_meter.get_member_rank(member.id)}", f"{self.level_meter.get_member_level(member.id)}", ""

        created_at = modules.strftime_translate(member.created_at.strftime("%d %b %Y"))
        joined_at = modules.strftime_translate(member.joined_at.strftime("%d %b %Y"))

        pfp = member.guild_avatar.with_size(256) if member.guild_avatar is not None else member.avatar.with_size(256)  # get member avatar
        pfp_data = BytesIO(await pfp.read())
        pfp: Image.Image = Image.open(pfp_data).convert("RGBA")
        pfp = modules.get_circled_image(pfp)

        guild_banner = None
        guild_icon = None

        if ctx.guild.banner is not None:  # get guild banner if is not None
            guild_banner = ctx.guild.banner.with_size(256)
            guild_banner_data = BytesIO(await guild_banner.read())
            guild_banner: Image.Image = Image.open(guild_banner_data).convert("RGBA")
            guild_banner = guild_banner.resize((230, 230), Image.ANTIALIAS)

        guild_icon = ctx.guild.icon.with_size(256)  # get guild icon
        guild_icon_data = BytesIO(await guild_icon.read())
        guild_icon: Image.Image = Image.open(guild_icon_data).convert("RGBA")
        guild_icon = guild_icon.resize((230, 230), Image.ANTIALIAS)

        base: Image.Image = Image.open("datas/assets/ProfieUI/base.png").convert("RGBA")  # open base image
        bg: Image.Image = Image.open("datas/assets/ProfieUI/white_background.png").convert("RGBA")  # open background image

        name = f"{name[:14]}.." if len(name) > 16 else name  # if name len long than 16 resize name
        nick = f"{nick[:15]}.." if len(nick) > 17 else nick  # if nick len long than 17 resize nick

        # load fonts
        font = ImageFont.truetype("datas/assets/Roboto-Bold.ttf", 38)
        nick_font = ImageFont.truetype("datas/assets/Roboto-Bold.ttf", 30)
        sub_font = ImageFont.truetype("datas/assets/Roboto-Bold.ttf", 25)

        # draw text on image
        draw = ImageDraw.Draw(base)
        draw.text((280, 240), name, font=font)
        draw.text((270, 315), nick, font=nick_font)
        draw.text((65, 490), rank, font=sub_font)
        draw.text((405, 490), status, font=sub_font)
        if exp == "-":
            draw.text((65, 635), exp, font=sub_font)
        else:
            self.new_exp_bar(draw=draw, member_id=member.id)
        draw.text((405, 635), level, font=sub_font)
        draw.text((65, 785), created_at, font=sub_font)
        draw.text((405, 785), joined_at, font=sub_font)
        base.paste(pfp, (56, 158), pfp)

        if guild_banner is not None:
            bg.paste(guild_banner, (0, 0), guild_banner)
        else:
            bg.paste(guild_icon, (int(bg.size[0]/2-guild_icon.size[0]/2), 0), guild_icon)

        bg.paste(base, (0, 0), base)

        # save image to BytesIO and send image to channel
        with BytesIO() as fp:
            bg.save(fp, "PNG")
            fp.seek(0)
            await ctx.send(file=discord.File(fp, "profil.png"))
    
    
    @commands.command(name="sunucu", aliases=["server", "s"], help="Sunucu bilgisini gösterir.")
    async def server(self, ctx: commands.Context):
        """ Shows server information. """

        show_members = True
        guild = ctx.guild
        owner = await guild.fetch_member(guild.owner_id)
        name, ID, owner, member_count, bot_count, channel_count = guild.name, str(guild.id), str(owner.name), str(modules.member_count(guild)), str(modules.bot_count(guild)), str(len(guild.channels))
        created_at = modules.strftime_translate(guild.created_at.strftime("%d %b %Y"))

        members = f"Üye: {member_count}\nBot: {bot_count}"

        guild_banner = None
        guild_icon = None

        if ctx.guild.banner is not None:  # get guild banner if is not None
            guild_banner = ctx.guild.banner.with_size(256)
            guild_banner_data = BytesIO(await guild_banner.read())
            guild_banner: Image.Image = Image.open(guild_banner_data).convert("RGBA")
            guild_banner = guild_banner.resize((230, 230), Image.ANTIALIAS)

        guild_icon = ctx.guild.icon.with_size(256)  # get guild icon
        guild_icon_data = BytesIO(await guild_icon.read())
        guild_icon: Image.Image = Image.open(guild_icon_data).convert("RGBA")

        pfp = modules.get_circled_image(guild_icon)

        guild_icon = guild_icon.resize((230, 230), Image.ANTIALIAS)

        # open base image
        if show_members:
            base: Image.Image = Image.open("datas/assets/ServerUI/base2.png").convert("RGBA")
        else:
            base: Image.Image = Image.open("datas/assets/ServerUI/base.png").convert("RGBA")

        bg: Image.Image = Image.open("datas/assets/ServerUI/white_background.png").convert("RGBA")  # open background image

        name = f"{name[:14]}.." if len(name) > 16 else name  # if name len long than 16 resize name

        # load fonts
        font = ImageFont.truetype("datas/assets/Roboto-Bold.ttf", 38)
        sub_font = ImageFont.truetype("datas/assets/Roboto-Bold.ttf", 25)

        # draw text on image
        draw = ImageDraw.Draw(base)
        draw.text((280, 240), name, font=font)
        draw.text((65, 490), ID, font=sub_font)
        draw.text((405, 490), owner, font=sub_font)
        draw.text((65, 635), member_count, font=sub_font)
        draw.text((405, 635), channel_count, font=sub_font)

        if show_members:
            draw.text((65, 785), created_at, font=sub_font)
            draw.text((405, 770), members, font=sub_font)
        else:
            draw.text((240, 785), created_at, font=sub_font)

        base.paste(pfp, (56, 158), pfp)

        if guild_banner is not None:
            bg.paste(guild_banner, (0, 0), guild_banner)
        else:
            bg.paste(guild_icon, (int(bg.size[0]/2-guild_icon.size[0]/2), 0), guild_icon)

        bg.paste(base, (0, 0), base)

        # save image to BytesIO and send image to channel
        with BytesIO() as fp:
            bg.save(fp, "PNG")
            fp.seek(0)
            await ctx.send(file=discord.File(fp, "server.png"))
    
    
    @commands.command(name="exp_ekle", help="Bir kullanıcıya exp ekler.", roles=[constants.MODERATOR_ROLE])
    async def add_exp(self, ctx: commands.Context, amount: int, member: t.Optional[discord.Member] = None):
        is_author = False
        
        if member is None:
            is_author = True
            member: discord.Member = ctx.author
        
        channel = ctx.guild.get_channel(constants.SERVER_BOT_MOD_CHANNEL_ID)
        
        await ctx.message.delete()
        
        try:
            await self.level_meter.add_exp_bot(ctx.guild, member.id, amount)
        except modules.errors.UnknownUser:
            embed = modules.create_embed(":x: İşlem Başarısız", "Girilen kullanıcı bulunamadı.")
            await channel.send(embed=embed)
            return
        
        embed = modules.create_embed(":white_check_mark: İşlem Başarılı", f"{member.mention} kullanıcısına {amount} EXP eklendi.")
        await channel.send(embed=embed)
        return
    
    
    @commands.command(name="exp_sil", help="Bir kullanıcıdan exp siler.", roles=[constants.MODERATOR_ROLE])
    async def remove_exp(self, ctx: commands.Context, amount: int, member: t.Optional[discord.Member] = None):
        is_author = False
        
        if member is None:
            is_author = True
            member: discord.Member = ctx.author
        
        channel = ctx.guild.get_channel(constants.SERVER_BOT_MOD_CHANNEL_ID)
        
        await ctx.message.delete()
        
        try:
            await self.level_meter.remove_exp_bot(ctx.guild, member.id, amount)
        except modules.errors.UnknownUser:
            embed = modules.create_embed(":x: İşlem Başarısız", "Girilen kullanıcı bulunamadı.")
            await channel.send(embed=embed)
            return
        
        embed = modules.create_embed(":white_check_mark: İşlem Başarılı", f"{member.mention} kullanıcısından {amount} EXP silindi.")
        await channel.send(embed=embed)
        return
    

def setup(client: modules.MyBot):
    client.add_cog(Stat(client))