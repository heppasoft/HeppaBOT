import os
import json
import openai
import modules
import datetime
import typing as t
from modules import constants

__all__ = ["ChatBot"]

openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatBot:
    def __init__(self, db:modules.SQLDatabase) -> None:
        self.db = db
        
        self.db.execute("CREATE TABLE IF NOT EXISTS chatbot_messages (role VARCHAR, content VARCHAR)")
        self.db.commit()
        
        res = self.db.execute("SELECT config FROM bot_configs WHERE name=?", ("chatbot",))
        config = res.fetchone()
        today = datetime.date.today()
        
        self.default_config = {
            "model": "gpt-3.5-turbo",
            "temp": 1,
            "tokens": 520,
            "top_p": 1,
            "freq_pen": 0,
            "pres_pen": 0,
            "stop": ["\nUser:"],
            "last_messages_reset_date": today.isoformat()
        }
        
        if config is None:
            self.config = self.default_config
            self.db.execute("INSERT INTO bot_configs VALUES(?, ?)", ("chatbot", json.dumps(self.config)))
            self.db.commit()
            self.reset_message_history()
        else:
            self.config = json.loads(config[0])
        
        self.messages:list[dict[str, str]] = []
        self.model:str = self.config.get("model")
        self.temp:float = self.config.get("temp")
        self.tokens:int = self.config.get("tokens")
        self.top_p:float = self.config.get("top_p")
        self.freq_pen:float = self.config.get("freq_pen")
        self.pres_pen:float = self.config.get("pres_pen")
        self.stop:list[str] = self.config.get("stop")
        self.last_messages_reset_date:datetime.date = datetime.date.fromisoformat(self.config.get("last_messages_reset_date"))
        
        
        res = self.db.execute("SELECT * FROM chatbot_messages",)
        messages = res.fetchall()
        if len(messages) > 0:
            for m in messages:
                self.messages.append({"role": m[0], "content": m[1]})
        
    
    def chat(self, message:str) -> str:
        last_reset_dif = (datetime.date.today() - self.last_messages_reset_date).days
        if last_reset_dif >= 1:
            self.messages.clear()
            self.last_messages_reset_date = datetime.date.today()
            self.config["last_messages_reset_date"] = self.last_messages_reset_date.isoformat()
            self.update_db_config()
        
        self.messages.append({"role": "user", "content": message})
        self.db.execute("INSERT INTO chatbot_messages VALUES(?,?)", ("user", message))
        self.db.commit()
        
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": constants.CHAT_BOT_SYSTEM_MESSAGE.format(prefix=constants.COMMAND_PREFIX)
                }
            ] + self.messages,
            temperature=self.temp,
            max_tokens=self.tokens,
            top_p=self.top_p,
            frequency_penalty=self.freq_pen,
            presence_penalty=self.pres_pen,
            stop=self.stop,
        )
        
        out_text = response["choices"][0]["message"]["content"]
        
        self.messages.append({"role": "assistant", "content": out_text})
        self.db.execute("INSERT INTO chatbot_messages VALUES(?,?)", ("assistant", out_text))
        self.db.commit()
        
        return out_text
    
    def reset_message_history(self):
        today = datetime.date.today()
        self.config["last_messages_reset_date"] = today.isoformat()
        self.last_messages_reset_date = today
            
        self.db.execute("UPDATE bot_configs SET config=? WHERE name = ?", (json.dumps(self.config), "chatbot"))
        self.db.commit()
        
        self.db.execute("DELETE FROM chatbot_messages")
        self.db.commit()