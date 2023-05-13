import json
import modules
import datetime
import requests
import typing as t


__all__ = [
    "Godbolt",
    "GodboltLanguage",
    "GodboltCompiler"
]

class GodboltLanguage(modules.Namespace):
    id: str
    name: str
    monaco: str
    extensions: list
    alias: list
    example: str
    default_compiler: "GodboltCompiler"
    
class GodboltCompiler(modules.Namespace):
    id: str
    name: str
    lang: str
    alias: list
    
    def __repr__(self):
        return self.id
    
    @property
    def compilationUrl(self) -> str:
        return f"https://godbolt.org/api/compiler/{self.id}/compile"

class Godbolt:
    last_cache_langs_update: datetime.date
    last_cache_compilers_update: datetime.date
    
    def __init__(self, db: modules.SQLDatabase) -> None:
        self.baseUrl = "https://godbolt.org/api/"
        self.headers = {
            "Content-Type":"application/json; charset=utf-8",
            "Accept":"application/json"
        }
        
        self.db = db
        self.db.execute("CREATE TABLE IF NOT EXISTS godbolt_langs (id VARCHAR, name VARCHAR, monaco VARCHAR, extensions VARCHAR, alias VARCHAR, example VARCHAR, default_compiler VARCHAR)")
        self.db.commit()
        
        self.db.execute("CREATE TABLE IF NOT EXISTS godbolt_compilers (id VARCHAR, name VARCHAR, lang VARCHAR, alias VARCHAR)")
        self.db.commit()
        
        res = self.db.execute("SELECT config FROM bot_configs WHERE name=?", ("godbolt",))
        config = res.fetchone()
        today = datetime.date.today()
        
        if config is None:
            self.db.execute("INSERT INTO bot_configs VALUES(?,?)", ("godbolt", json.dumps({"last_cache_langs_update": today.isoformat(), "last_cache_compilers_update": today.isoformat()})))
            self.db.commit()
            self.last_cache_langs_update = today - datetime.timedelta(days=1)
            self.last_cache_compilers_update = today - datetime.timedelta(days=1)
            self.compilers
            self.langs
        else:
            config = json.loads(config[0])
            self.last_cache_compilers_update = datetime.date.fromisoformat(config["last_cache_compilers_update"])
            self.last_cache_langs_update = datetime.date.fromisoformat(config["last_cache_langs_update"])
    
    
    @property
    def langs(self) -> list[GodboltLanguage]:
        
        last_uptade_dif = (datetime.date.today() - self.last_cache_langs_update).days
        
        langs: list[GodboltLanguage] = []
        
        if last_uptade_dif >= 1:
            req = requests.get(
                                f"{self.baseUrl}languages?fields=id,name,monaco,extensions,alias,example,defaultCompiler",
                                headers=self.headers
                            )
            
            for lang in req.json():
                dc = lang["defaultCompiler"]
                lang["default_compiler"] = self.get_compiler(dc)
                self.db.execute("INSERT INTO godbolt_langs VALUES(?,?,?,?,?,?,?)", (lang["id"],lang["name"],lang["monaco"],json.dumps(lang["extensions"]),json.dumps(lang["alias"]),lang["example"],lang["defaultCompiler"]))
                self.db.commit()
                langs.append(GodboltLanguage(lang))
                
            self.last_cache_langs_update = datetime.date.today()
            self.db.execute("UPDATE bot_configs SET config=? WHERE name = ?", (json.dumps({"last_cache_langs_update": self.last_cache_langs_update.isoformat(), "last_cache_compilers_update": self.last_cache_compilers_update.isoformat()}), "godbolt"))
            self.db.commit()
        else:
            res = self.db.execute("SELECT * FROM godbolt_langs")
            for l in res.fetchall():
                langs.append(GodboltLanguage({"id": l[0], "name": l[1], "monaco": l[2], "extensions": json.loads(l[3]), "alias": json.loads(l[4]), "example": l[5], "default_compiler": l[6]}))
        
        langs.sort(key=lambda l: l.name)
        return langs
    
    @property
    def compilers(self) -> list[GodboltCompiler]:
        last_uptade_dif = (datetime.date.today() - self.last_cache_compilers_update).days
        
        compilers: list[GodboltCompiler] = []
        
        if last_uptade_dif >= 1:
            req = requests.get(
                                f"{self.baseUrl}compilers?fields=id,name,lang,alias",
                                headers=self.headers
                            )
            
            for compiler in req.json():
                self.db.execute("INSERT INTO godbolt_compilers VALUES(?,?,?,?)", (compiler["id"],compiler["name"],compiler["lang"],json.dumps(compiler["alias"])))
                self.db.commit()
                compilers.append(GodboltCompiler(compiler))
        
            self.last_cache_compilers_update = datetime.date.today()
            self.db.execute("UPDATE bot_configs SET config=? WHERE name = ?", (json.dumps({"last_cache_langs_update": self.last_cache_langs_update.isoformat(), "last_cache_compilers_update": self.last_cache_compilers_update.isoformat()}), "godbolt"))
            self.db.commit()
        else:
            res = self.db.execute("SELECT * FROM godbolt_compilers")
            for c in res.fetchall():
                compilers.append(GodboltCompiler({"id": c[0], "name": c[1], "lang": c[2], "alias": json.loads(c[3])}))
        
        compilers.sort(key=lambda c: c.name)
        return compilers
    
    def get_language(self, id: str) -> t.Union[GodboltLanguage, None]:
        return modules.find(lambda l: l.id == id, self.langs, only_first=True) or self.get_language_by_alias(id)
    
    def get_language_by_alias(self, alias: str) -> t.Union[GodboltLanguage, None]:
        return modules.find(lambda l: l.monaco == alias or l.name.lower() == alias or alias in l.alias, self.langs, only_first=True)
    
    def get_language_by_extension(self, ext: str) -> t.Union[GodboltLanguage, None]:
        if not ext.startswith("."): ext = f".{ext}"
        return modules.find(lambda l: ext in l.extensions, self.langs, only_first=True)
    
    def get_compiler(self, id: str) -> t.Union[GodboltCompiler, None]:
        return modules.find(lambda c: c.id == id, self.compilers, only_first=True)
    
    def is_valid_lang(self, id: str) -> bool:
        return modules.find(lambda l: l.id == id, self.langs) != None
    
    def is_valid_compiler(self, id: str) -> bool:
        return modules.find(lambda c: c.id == id, self.compilers) != None
        
    def compile(self, code: str, compiler: str, args: list[str] = [], stdin: str = "", libraries: list[dict[str,str]] = [], compiler_option_raw: str = "") -> t.Tuple[t.Union[str, None], t.Union[str, None]]:
        if not self.is_valid_compiler(compiler):
            lang = self.get_language_by_alias(compiler)
            
            if lang is None:
                raise modules.errors.CompilationError("Invalid language or compiler")
            
            compiler = lang.default_compiler.id
        
        newArgs = []
        
        for arg in args:
            if not isinstance(arg, str):
                arg = str(arg)
            
            newArgs.append(arg)
        
        args = newArgs
        
        if not isinstance(libraries, list):
            raise modules.errors.CompilationError("libraries type must be list")
        
        json = {
            "compiler": compiler,
            "source": code,
            "options": {
                "userArguments": compiler_option_raw,
                "executeParameters": {
                    "args": args,
                    "stdin": stdin
                },
                "compilerOptions": {
                    "executorRequest": True
                },
                "filters": {
                    "execute": True
                },
                "libraries": libraries
            },
            "allowStoreCodeDebug": True
        }
        
        req = requests.post(
                            self.get_compiler(compiler).compilationUrl,
                            json=json,
                            headers=self.headers
                        )
                
        res = req.json()
        
        if not req.ok:
            if "error" in res:
                raise modules.errors.CompilationError(f"Godbolt compilation error: {res['message']}")
            raise modules.errors.GodboltError(f"Godbolt replied with response code {req.status_code}.\nThis could mean Godbolt is experiencing an outage or a network connection error has occured")
        
        errors = []
        for error in res["stderr"]:
            errors.append(error["text"])
        
        outs = []
        for outt in res["stdout"]:
            outs.append(outt["text"])
        
        return ("\n".join(errors) if len(errors) > 0 else None, "\n".join(outs) if len(outs) > 0 else None)