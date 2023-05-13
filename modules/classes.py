import json
import pickle
import sqlite3
import asyncio
import discord
import modules
import typing as t
from modules import constants
from discord.ext import commands

__all__ = [
    "MyBot",
    "MyCog",
    "MyEmbed",
    "Namespace",
    "VerifyView",
    "LevelMeter",
    "SQLDatabase",
    "SuggestionView",
]


class Namespace:
    """Simple object for storing attributes.

    Implements equality by attribute names and values, and provides a simple
    string representation.
    """

    def __init__(self, data: dict = None, **kwargs) -> None:
        if data is not None and isinstance(data, dict):
            for name in data:
                self.__setattr__(name, data[name])
        else:
            for name in kwargs:
                self.__setattr__(name, kwargs[name])

    def __contains__(self, key: str) -> bool:
        return key in self.__dict__

    def __eq__(self, other: "Namespace") -> bool:
        if not isinstance(other, Namespace):
            return NotImplemented
        return vars(self) == vars(other)

    def __repr__(self):
        type_name = type(self).__name__
        arg_strings = []
        star_args = {}
        for arg in self._get_args():
            arg_strings.append(repr(arg))
        for name, value in self._get_kwargs():
            if name.isidentifier():
                arg_strings.append(f"{name}={value}")
            else:
                star_args[name] = value
        if star_args:
            arg_strings.append(f"**{repr(star_args)}")
        return f"{type_name}({', '.join(arg_strings)})"

    def _get_kwargs(self):
        return sorted(self.__dict__.items())

    def _get_args(self):
        return []

    def get(self, name: str) -> t.Any:
        """Get attributes

        :param name: Attributes name
        :type name: str
        """
        return self.__dict__.get(name, None)

    def get_all(self) -> dict:
        """ Get all attributes 
            
            :return: Attributes
            :rtype: dict
        """
        return self.__dict__

    def update(self, data: dict = None, **kwargs) -> None:
        """
            Update attributes

            :param data: Attributes dict, defaults to None
            :type data: dict, optional
        """
        if data is not None and isinstance(data, dict):
            for name in data:
                self.__setattr__(name, kwargs[name])

        for name in kwargs:
            self.__setattr__(name, kwargs[name])

    def delete(self, *args, names: list = None) -> None:
        """
            Delete attributes

            :param names: Name list defaults to None
            :type names: list, optional
        """
        if names is not None and (isinstance(names, list) or isinstance(names, tuple)):
            for name in names:
                self.__delattr__(name)

        if names is not None and isinstance(names, str):
            self.__delattr__(names)

        for name in args:
            self.__delattr__(name)

    def keys(self) -> list:
        """
            Return attributes keys

            :return: Attributes keys
            :rtype: list
        """
        return list(self.__dict__.keys())

    @classmethod
    def from_json_file(cls, filePath: str) -> "Namespace":
        """
            Load object from json file

            :param filePath: File path.
            :type filePath: str
            :return: Object loaded from json file.
            :rtype: Namespace
        """
        with open(filePath) as fp:
            data = json.load(fp)
        return cls(data=data)

    def dump(self) -> bytes:
        """
            Dump object to data

            :return: Dumped data
            :rtype: bytes
        """
        return pickle.dumps(self)

    @staticmethod
    def load(data: bytes) -> t.Any:
        """
            Load object from data

            :param data: Data to load the object
            :type data: bytes
            :return: Object loaded from data
            :rtype: Any
        """
        return pickle.loads(data)


class Member(Namespace):
    id: int
    level: int
    exp: int
    total_exp: int
    rank: int


class MyBot(commands.Bot):
    db: "SQLDatabase"
    is_in_development: bool
    level_meter: "LevelMeter"
    chatbot: "modules.ChatBot"
    
    def __init__(self,**options):
        self.level_meter = options.pop("level_meter")
        self.is_in_development = options.pop("is_in_development")
        self.db = options.pop("database")
        self.chatbot = options.pop("chatbot")
        super().__init__(**options)
    
    async def process_commands(self: commands.Bot, message: discord.Message):
        if message.author.bot:
            return

        ctx: commands.Context = await self.get_context(message)

        if ctx.command is not None:
            channels = ctx.command.__original_kwargs__.get("channels", [])
            
            if isinstance(channels, list) and len(channels) == 0:
                channels = [constants.SERVER_BOT_COMMAND_CHANNEL]
            
            if isinstance(channels, str):
                if channels == "all":
                    channels = []
                else:
                    channels = [channels]
            
            for channel in channels:
                if isinstance(channel, str):
                    channels.append(int(channel))

            if message.channel.id not in channels and len(channels) > 0:
                await message.delete()
                self.dispatch("command_error", ctx, modules.errors.InvalidCommandChannel())
                return

            roles = ctx.command.__original_kwargs__.get("roles", [])
            if not modules.has_ayn_role(message.author, roles) and len(roles) > 0 and not modules.has_ayn_role(message.author, constants.ADMIN_ROLE):
                self.dispatch("command_error", ctx, commands.MissingAnyRole(roles))
                return

        await message.channel.trigger_typing()
        await asyncio.sleep(1)
        await self.invoke(ctx)


class MyCog(commands.Cog):
    def update_params(self, **kwargs):
        commandds = list(self.__cog_commands__)
        for idx, command in enumerate(commandds):
            for key, val in kwargs.items():
                if key in command.__original_kwargs__:
                    if isinstance(command.__original_kwargs__[key], list):
                        command.__original_kwargs__[key].extend(val)
                        
                    elif isinstance(command.__original_kwargs__[key], dict):
                        command.__original_kwargs__[key].update(val)
                else:
                    command.__original_kwargs__[key] = val
            
            commandds[idx] = command
        self.__cog_commands__ = tuple(commandds)


class MyEmbed(discord.Embed):
    def add_field(self, name: t.Any, value: t.Any, inline: bool = False):
        return super().add_field(name=name, value=value, inline=inline)


class Database:
    def __init__(self, filePath: str):
        self.filePath = filePath
        if not modules.is_exists(filePath):
            modules.create_data_files(filePath)

    @property
    def datas(self) -> dict:
        """ Returns datas in database file """
        return modules.load_data_files(self.filePath)

    @datas.setter
    def datas(self, datas: t.Any):
        """ Change datas in database file """
        modules.dump_data_files(self.filePath, datas)

    def get(self, key: str) -> t.Union[t.Any, None]:
        """ Returns any key value if exists else returns None """
        return self.datas.get(key, None)

    def update(self, key: str, value: t.Any):
        """ Update key value """
        datas = self.datas
        datas[key] = value
        
        self.datas = datas

    def delete(self, key:str):
        """ Delete key """
        datas = self.datas

        del datas[key]
        self.datas = datas


class SQLDatabase:
    def __init__(self, db_path: str) -> None:
        self.con = sqlite3.connect(db_path, check_same_thread=False)
    
    def execute(self, sql: str, parameters: set = ()):
        cur = self.con.cursor()
        res = cur.execute(sql, parameters)
        return res
    
    def commit(self):
        self.con.commit()
        

class LevelMeter:
    def __init__(self, db: SQLDatabase):
        self.db = db
        self.db.execute("CREATE TABLE IF NOT EXISTS level_meter_members (id INTEGER, level INTEGER, exp INTEGER, total_exp INTEGER)")
        self.db.commit()
        
        self.level_requirements = {2: 200, 3: 400, 4: 800, 5: 1600, 6: 3200, 7: 6400, 8: 12800, 9: 25600, 10: 51200}
        self.max_level = 10
    
    def get_member(self, member_id: int) -> Member:
        """ Return member """
        res = self.db.execute("SELECT * FROM level_meter_members WHERE id=?",(member_id,))
        m = res.fetchone()
        
        if m == None:
            raise modules.errors.UnknownUser()
        
        m = list(m)
        member = Member(id = m[0], level = m[1], exp = m[2], total_exp = m[3])
        return member
    
    def update_member(self, member_id: int, member: Member):
        """ Update member """
        
        self.db.execute("UPDATE level_meter_members SET level = ?, exp = ?, total_exp = ? WHERE id = ?", (member.level, member.exp, member.total_exp, member_id))
        self.db.commit()

    def new_member(self, member_id: int):
        """ Add new member """
        
        try:
           self.get_member(member_id)
        except modules.errors.UnknownUser:
            self.db.execute("INSERT INTO level_meter_members VALUES(?, ?, ?, ?)", (member_id, 1, 0, 0))
            self.db.commit()
        
        return

    def delete_member(self, member_id: int):
        """ Delete a member """
        self.get_member(member_id)

        self.db.execute("DELETE FROM level_meter_members WHERE id=?", (member_id,))
        self.db.commit()

    def get_member_level(self, member_id: int) -> int:
        """ Get member level """

        member = self.get_member(member_id)
        return member.level

    def get_member_exp(self, member_id: int) -> int:
        """ Get member exp """

        member =  self.get_member(member_id)
        return member.exp

    def get_level_requirements(self, level: int) -> t.Union[int, None]:
        """ Get any level requirements """

        return self.level_requirements.get(level, None)

    def get_member_next_level_requirements(self, member_id: int) -> t.Union[int, None]:
        """ Get member next level requirements """

        member = self.get_member(member_id)
        return self.get_level_requirements(member.level+1)

    def add_exp(self, member_id: int, amount: int):
        """ Add exp to member without sending message """

        member = self.get_member(member_id)
        member.exp += amount
        member.total_exp += amount

        next_level_requirements = self.get_level_requirements(member.level+1)

        while next_level_requirements is not None and member.exp >= next_level_requirements:
            member.level += 1
            member.exp -= next_level_requirements

            if member.level == self.max_level:
                break

            next_level_requirements = self.get_level_requirements(member.level+1)

        if member.exp < 0:
            member.exp = 0

        self.update_member(member_id, member)

    async def add_exp_bot(self, guild: discord.Guild, member_id: int, amount: int):
        """ Add exp to member """

        old_level = self.get_member_level(member_id)

        self.add_exp(member_id=member_id, amount=amount)
        
        new_level  = self.get_member_level(member_id)

        if old_level != new_level:
            channel = guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)
            guild_member = await guild.fetch_member(member_id)
            if new_level == self.max_level:
                await channel.send(f"{guild_member.mention} maksimum seviyeye ulaştı. Tebrikler {guild_member.mention}.")
            else:
                await channel.send(f"{guild_member.mention} {new_level} seviyesine yükseldi. Tebrikler {guild_member.mention}.")
    
    def remove_exp(self, member_id: int, amount: int):
        """ Remove exp from member """

        member = self.get_member(member_id)
        
        member.total_exp -= amount
        
        if member.total_exp < 0: member.total_exp = 0
        
        if member.total_exp == 0:
            self.reset_member(member_id)
            return
        
        else:
            member.level = 1
            member.exp = member.total_exp
            
            next_level_requirements = self.get_level_requirements(member.level+1)

            while next_level_requirements is not None and member.exp >= next_level_requirements:
                member.level += 1
                member.exp -= next_level_requirements

                if member.level == self.max_level:
                    break

                next_level_requirements = self.get_level_requirements(member.level+1)
        
        self.update_member(member_id, member)
    
    async def remove_exp_bot(self, guild: discord.Guild, member_id: int, amount: int):
        """ Remove exp to member """

        old_level = self.get_member_level(member_id)

        self.remove_exp(member_id=member_id, amount=amount)
        
        new_level  = self.get_member_level(member_id)

        if old_level != new_level:
            channel = guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)
            guild_member = await guild.fetch_member(member_id)
            await channel.send(f"{guild_member.mention} {new_level} seviyesine düştü.")

    def increase_level(self, member_id: int, amount: int):
        """ Increase member level """

        member = self.get_member(member_id)
        member.level += amount

        if member.level > self.max_level:
            member.level = self.max_level

        self.update_member(member_id, member)

    def decrease_level(self, member_id: int, amount: int):
        """ Decrease member level """

        member = self.get_member(member_id)
        member.level -= amount

        if member.level < 0:
            member.level = 0

        self.update_member(member_id, member)

    def reset_member(self, member_id: int):
        """ Reset member level and exp """
        self.get_member(member_id)

        self.update_member(member_id, Member(id = member_id, level = 1, exp = 0, total_exp = 0))
    
    def get_ranks(self, limit: t.Union[int, None] = None) -> dict:
        res = self.db.execute("SELECT * FROM level_meter_members ORDER BY total_exp DESC")
        
        all_members =[Member(id=r[0], level=r[1], exp=r[2], total_exp=r[3]) for r in res.fetchall()]
        
        ranks = list(map(lambda m: m.id, all_members))[:limit]
        
        return dict(enumerate(ranks, 1))
    
    def get_member_rank(self, member_id: int) -> int:
        self.get_member(member_id)
        ranks = self.get_ranks()
        
        for k, v in ranks.items():
            if v == member_id:
                return k
    
    def top10(self) -> dict:
        return self.get_ranks(10)


class SuggestionView(discord.ui.View):
    def __init__(self, embed: MyEmbed):
        self.embed = embed
        self.accepts = []
        self.denys = []
        super().__init__()
    
    @discord.ui.button(label="👍", custom_id="suggestion:accept", style=discord.ButtonStyle.success)
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        # await interaction.response.defer()
        
        userID = interaction.user.id
        if userID not in self.accepts:
            self.accepts.append(userID)
        
            if userID in self.denys:
                self.denys.remove(userID)
        
        await self.update(interaction)
    
    @discord.ui.button(label="👎", custom_id="suggestion:deny", style=discord.ButtonStyle.danger)
    async def deny(self, button: discord.ui.Button, interaction: discord.Interaction):
        # await interaction.response.defer()
        
        userID = interaction.user.id
        if userID not in self.denys:
            self.denys.append(userID)
        
            if userID in self.accepts:
                self.accepts.remove(userID)
        
        await self.update(interaction)
    
    async def update(self, interaction: discord.Interaction):
        self.children[0].label = f"👍 {len(self.accepts)}"
        self.children[1].label = f"👍 {len(self.denys)}"
        
        channel = interaction.guild.get_channel(constants.SERVER_BOT_LOG_CHANNEL_ID)
        
        if len(self.accepts) >= constants.SERVER_SUGGESTION_VOTES_APPROVAL:
            ab = discord.ui.Button(label="✅", style=discord.ButtonStyle.primary)
            self.add_item(ab)
            self.disable_all_items()
            
            embed = modules.create_embed(":information_source: Bilgilendirme", "Bir öneri oylama ile kabul edildi.")
            embed.add_field("Öneren:", self.embed.fields[0].value)
            embed.add_field("Öneri:", self.embed.fields[1].value)
            await channel.send(embed=embed)
        
        elif len(self.denys) >= constants.SERVER_SUGGESTION_VOTES_APPROVAL:
            ab = discord.ui.Button(label="❌", style=discord.ButtonStyle.primary)
            self.add_item(ab)
            self.disable_all_items()
            
            embed = modules.create_embed(":information_source: Bilgilendirme", "Bir öneri oylama ile red edildi.")
            embed.add_field("Öneren:", self.embed.fields[0].value)
            embed.add_field("Öneri:", self.embed.fields[1].value)
            await channel.send(embed=embed)
        
        await interaction.response.edit_message(view=self)


class VerifyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    
    @discord.ui.button(label=constants.VERIFY_BUTTON_TEXT, custom_id="verify:verify", style=discord.ButtonStyle.success)
    async def accept(self, button: discord.ui.Button, interaction: discord.Interaction):
        verify_role = modules.get(interaction.guild.roles, name=constants.VERIFY_ROLE)
        member = interaction.user
        
        if modules.has_ayn_role(member, verify_role.name):
            embed = modules.create_embed(":x: İşlem Başarısız", "Hesabınız zaten doğrulanmış.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed = modules.create_embed(":white_check_mark: İşlem Başarılı", "Hesabınız doğrulanmıştır.")
            await interaction.response.send_message(embed=embed, ephemeral=True)
            await asyncio.sleep(2)
            await member.add_roles(verify_role)