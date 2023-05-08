import modules
import typing as t
from modules import constants
from discord.ext import commands, pages

    
class Compiler(modules.MyCog):
    def __init__(self, client: modules.MyBot) -> None:
        self.client = client
        
        self.update_params(roles=[constants.CODER_ROLE], channels=[constants.SERVER_DEVELOPER_BOT_COMMAND_CHANNEL_ID])
        
        self.godbolt = modules.Godbolt(self.client.db)
    
    
    @commands.command(name="compiler_langs", aliases=["derleyici_dilleri", "c_l", "d_d"], help="Derleyicinin desteklediği dilleri gösterir.")
    async def compiler_langs(self, ctx: commands.Context, limit: t.Union[int, str, None] = None):
        langs = self.godbolt.langs
        pagess = []
            
        top_langs = sorted(["python", "csharp", "c", "c++", "javascript", "assembly", "go", "objc", "java", "objc"])
        
        if isinstance(limit, str):
            if limit == "all" or limit == "hepsi":
                limit = None
        elif limit is None:
            pass
        else:
            limit = int(limit)
        
        if limit == "top10":
            embed = modules.create_embed("Desteklenen Diller", "Derleyici tarafından desteklenen diller:")
            for lang in top_langs:
                l = self.godbolt.get_language(lang)
                embed.add_field(f"{l.name.capitalize()}", f"ID: {l.id}\nUzantılar: [ {', '.join(l.extensions)} ]\nVarsayılan Derleyici: {l.default_compiler}\nÖrnek Kod:\n`{l.example}`")
            pagess.append(embed)
        else:
            langss = []
            for l in langs[:limit]:
                langss.append([f"{l.name.capitalize()}", f"ID: `{l.id}`\nUzantılar: `[ {', '.join(l.extensions)} ]`\nVarsayılan Derleyici: `{l.default_compiler}`"])
            
            s = int(len(langss) / 10)
            if len(langss) % 10 > 0: s += 1
            for i in range(0,s):
                embed = modules.create_embed("Desteklenen Diller", f"Sayfa **{i+1}**")
                for l in langss[i*10:(i+1)*10]:
                    embed.add_field(l[0], l[1])
                
                pagess.append(embed)
            
        paginator = pages.Paginator(pages=pagess)
        await paginator.send(ctx)
    
    
    @commands.command(name="compilers", aliases=["derleyiciler"], help="Desteklenen derleyicileri gösterir.")
    async def compilers(self, ctx: commands.Context, limit: int = 10):
        embed = modules.create_embed("Desteklenen Derleyiciler", "Desteklenen derleyiciler:")
        
        compilers = self.godbolt.compilers
            
        top_langs = sorted(["python", "csharp", "c", "c++", "javascript", "assembly", "go", "objc", "java", "carbon"])
        
        if limit <= 10:
            for lang in top_langs[:limit]:
                c = modules.find(lambda c: c.lang == lang, compilers)
                if isinstance(c, modules.GodboltCompiler):
                    embed.add_field(f"{c.name.capitalize()}", f"ID: {c.id}\nDil: {c.lang.capitalize()}\nTakma Adlar: [ {', '.join(c.alias)} ]")
                else:
                    c = self.godbolt.get_compiler(self.godbolt.get_languages(lang).default_compiler)
                    embed.add_field(f"{c.name.capitalize()}", f"ID: {c.id}\nDil: {c.lang.capitalize()}\nTakma Adlar: [ {', '.join(c.alias)} ]")
        else:
            for c in compilers[:limit]:
                embed.add_field(f"{c.name.capitalize()}", f"ID: {c.id}\nDil: {c.lang.capitalize()}\nTakma Adlar: [ {', '.join(c.alias)} ]")
        
        await ctx.send(embed=embed)
    
    
    @commands.command(name="compile", aliases=["derle"], help="Girilen kod metnini veya dosyayı derler.", help_params={"metin": "Optional"})
    async def compile(self, ctx: commands.Context, *, code: t.Optional[str]):
        discord_supported_languages = [ "1c", "abnf", "accesslog", "actionscript", "ada", "apache", "applescript",
        "arduino", "armasm", "asciidoc", "aspectj", "autohotkey", "autoit", "avrasm",
        "awk", "axapta", "bash", "basic", "bnf", "brainfuck", "bf", "c", "cal", "capnproto", "ceylon",
        "clean", "clojure-repl", "clojure", "cmake", "coffeescript", "coq", "cos",
        "cpp", "c++", "crmsh", "crystal", "cs", "c#", "csharp", "csp", "css", "d", "dart", "delphi", "diff",
        "django", "dns", "dockerfile", "dos", "dsconfig", "dts", "dust", "ebnf",
        "elixir", "elm", "erb", "erlang-repl", "erlang", "excel", "fix", "flix", "fortran",
        "fsharp", "gams", "gauss", "gcode", "gherkin", "glsl", "go", "golo", "gradle", "groovy",
        "haml", "handlebars", "haskell", "haxe", "hsp", "htmlbars", "http", "hy", "inform7",
        "ini", "irpf90", "java", "javascript", "jboss-cli", "json", "js", "julia-repl", "julia",
        "kotlin", "lasso", "ldif", "leaf", "less", "lisp", "livecodeserver", "livescript",
        "llvm", "lsl", "lua", "makefile", "markdown", "mathematica", "matlab", "maxima",
        "mel", "mercury", "mipsasm", "mizar", "mojolicious", "monkey", "moonscript", "n1ql",
        "nginx", "nimrod", "nix", "nsis", "objectivec", "ocaml", "openscad", "oxygene",
        "parser3", "perl", "pf", "php", "pony", "powershell", "processing", "profile",
        "prolog", "protobuf", "puppet", "purebasic", "python", "py", "q", "qml", "r", "rs", "rib",
        "roboconf", "routeros", "rsl", "ruby", "ruleslanguage", "rust", "scala", "scheme",
        "scilab", "scss", "shell", "smali", "smalltalk", "sml", "sqf", "sql", "stan", "stata",
        "step21", "stylus", "subunit", "swift", "taggerscript", "tap", "tcl", "tex", "thrift",
        "tp", "twig", "typescript", "vala", "vbnet", "vbscript-html", "vbscript", "verilog",
        "vhdl", "vim", "x86asm", "xl", "xml", "xquery", "yaml", "zephir"]
        lang = None
        
        if code is None:
            if len(ctx.message.attachments) > 1:
                embed = modules.create_embed(":x: İşlem Başarısız", "Birden fazla dosya derlenememekte, lütfen yanlızca bir dosya yükleyiniz.")
                await ctx.send(embed=embed)
                return
            if len(ctx.message.attachments) == 1:
                file = ctx.message.attachments[0]
                code =  bytes(await file.read()).decode()
                lang = self.godbolt.get_language_by_extension(file.filename.split(".")[-1])
        else:
            lang = modules.find(lambda l: code.startswith(f"```{l} ") or code.startswith(f"```{l}\n") or code.startswith(f"``` {l} ") or code.startswith(f"``` {l}\n"), discord_supported_languages)
            code = code.replace(f"```{lang} ", "").replace(f"```{lang}\n", "").replace(f"```{lang}", "").replace(f"``` {lang} ", "").replace(f"``` {lang}\n", "").replace(f"``` {lang}", "").replace(f" ```", "").replace(f"\n```", "").replace(f"```", "")
            lang = self.godbolt.get_language(lang.replace("c#","cs"))
        
        if code is None:
            embed = modules.create_embed(":x: İşlem Başarısız", "Lütfen bir kod dosyası ekleyin yada kod bloğunu girin. ")
            await ctx.send(embed=embed)
        elif not isinstance(lang, modules.GodboltLanguage):
            embed = modules.create_embed(":x: İşlem Başarısız", "Lütfen desteklenen bir programlama dili girin. ")
            await ctx.send(embed=embed)
        else:
            embed = modules.create_embed(":warning: Bilgilendirme", "Kodunuz derleniyor...")
            msg = await ctx.send(embed=embed)
            err, out = self.godbolt.compile(code,lang.default_compiler)
            await msg.delete()
            if err is not None:
                embed = modules.create_embed(":x: İşlem Başarısız", "Kodunuz derlenirken bir hata oluştu.")
                embed.add_field("Programlama Dili:", f"**`{lang.name.capitalize()}`**")
                embed.add_field("Kod:", f"**`{code}`**")
                embed.add_field("Hata:", f"**`{err}`**")
                await ctx.send(embed=embed)
            else:
                embed = modules.create_embed(":white_check_mark: İşlem Başarılı", "Kodunuz derlendi.")
                embed.add_field("Programlama Dili:", f"**`{lang.name.capitalize()}`**")
                embed.add_field("Kod:", f"**`{code}`**")
                embed.add_field("Çıktı:", f"**`{out}`**")
                await ctx.send(embed=embed)


def setup(client: modules.MyBot):
    client.add_cog(Compiler(client))