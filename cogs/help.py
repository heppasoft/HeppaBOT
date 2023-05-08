import modules
import discord
import typing as t
from modules import constants
from discord.ext import commands, pages

class Help(modules.MyCog):
    def __init__(self, client: modules.MyBot):
        self.client = client
        self.client.remove_command("help")
        self.turkish_keys = {
                                "member": "kullanıcı",
                                "content": "içerik",
                                "channel": "kanal",
                                "mentione_everyone": "herkesten_bahset",
                                "suggestion": "öneri",
                                "university": "üniversite",
                                "department": "bölüm",
                                "verifaction_code": "onay_kodu",
                                "role": "rol",
                                "amount": "miktar",
                                "reason": "sebep",
                                "pos": "konum"
                            }
        
        self.cog_names = {
            "Gen": "Genel",
            "Mod": "Moderasyon",
            "Compiler": "Derleyici",
            "Help": "Yardım",
            "Dev": "Geliştirme",
            "Stat": "Durum"
        }

    def syntax(self, command: commands.Command) -> str:
        """
            Get command syntax string.

            :param command: Command.
            :type command: commands.Command
            :returns: Command syntax string.
            :rtype: str
        """
        cmd_and_aliases = "|".join([str(command), *command.aliases])
        params = []

        if "help_params" not in command.__original_kwargs__:
            for key, value in command.params.items():
                for tk in self.turkish_keys:  # translate key to Turkish
                    if tk in key:
                        key = key.replace(tk, self.turkish_keys[tk])

                if key not in ("self", "ctx"):
                    params.append(f"[{key}]" if "NoneType" in str(value) or "Optional" in str(value) else f"<{key}>")
        
        else:
            for key, value in command.__original_kwargs__["help_params"].items():
                for tk in self.turkish_keys:  # translate key to Turkish
                    if tk in key:
                        key = key.replace(tk, self.turkish_keys[tk])

                if key not in ("self", "ctx"):
                    params.append(f"[{key}]" if "NoneType" in str(value) or "Optional" in str(value) else f"<{key}>")

        params = " ".join(params)

        return f"`{cmd_and_aliases} {params}`"

    async def cmd_help(self, ctx: commands.Context, command):
        embed = modules.create_embed(title=f"`{command}` için yardım",
                                    description=self.syntax(command),
                                    colour=ctx.author.colour
                                    )

        embed.add_field(name="Komut açıklaması", value=command.help)
        await ctx.send(embed=embed)

    @commands.command(cls=commands.Command, name="help", aliases=["h", "yardım", "y"], help="Yardım mesajını gösterir.", channels=[938514102433742978])
    async def show_help(self, ctx: commands.Context, cmd: t.Optional[str]):
        """ Show help message """
        if cmd is None:
            
            cogs: list[commands.Cog] = self.client.cogs.values()
            
            pagess = []
            pagessD = {}
            pagessCN = []
            
            for cog in list(cogs):
                cog_name = self.cog_names.get(cog.qualified_name, cog.qualified_name)
                fields = {}
                keys = []
                for entry in list(cog.get_commands()):
                    roles = entry.__original_kwargs__.get("roles", [])
                    if not modules.has_ayn_role(ctx.author, roles) and len(roles) > 0 and not  modules.has_ayn_role(ctx.author, constants.ADMIN_ROLE):
                        continue
                    
                    fields[entry.name] = (entry.help or "Açıklama yok", self.syntax(entry))
                    keys.append(entry.name)
                embed = modules.create_embed(title="Yardım menüsü",
                                        description=f"Sayfa: **{cog_name}**",
                                        colour=ctx.author.colour)
                embed.set_thumbnail(url=ctx.guild.me.avatar.url)
                
                if len(keys) == 0:
                    continue
                
                keys.sort()

                for key in keys:
                    name, value = fields[key]
                    embed.add_field(name=name, value=value, inline=True)
                    
                pagessD[cog_name] = embed
                pagessCN.append(cog_name)
            
            pagessCN.sort()
            
            for cn in pagessCN:
                pagess.append(pagessD[cn])

            paginator = pages.Paginator(pages=pagess)
            await paginator.send(ctx)
        
        else:
            if (command := discord.utils.get(self.client.commands, name=cmd)) or (command := self.client.prefixed_commands.get(cmd, None)):
                await self.cmd_help(ctx, command)

            else:
                embed = modules.create_embed(":x: İşlem Başarısız", "Böyle bir komut mevcut değil.")
                await ctx.send(embed=embed)


def setup(client: modules.MyBot):
    client.add_cog(Help(client))