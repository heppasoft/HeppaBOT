import random
import modules
import discord
import datetime
import typing as t
from modules import constants
from discord.ext import commands, tasks

class TicTacToe(modules.MyCog):
    lap = 0
    player1: discord.Member = None
    player2: discord.Member = None
    turn: discord.Member = None
    game_over = True
    start_datetime = None

    board:list[int] = [
                        "0","0","0",
                        "0","0","0",
                        "0","0","0"
                    ]
    
    messages:list[discord.Message] = []

    winning_conditions = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ]
    def __init__(self, client: modules.MyBot) -> None:
        self.client = client
        self.update_params(channels=[constants.SERVER_TICTACTOE_CHANNEL_ID])
    
    @commands.command(name="tictactoe", help="Yeni bir TicTacToe oyunu başlatır.")
    async def tictactoe(self, ctx: commands.Context, p1: discord.Member, p2: t.Optional[discord.Member]):
        if not self.game_over:
            embed = modules.create_embed(":x: İşlem Başarısız", "Zaten şuanda devam etmekte olan bir oyun bulunmakta. Lütfen oyunun bitmesini bekleyin.")
            await ctx.send(embed=embed)
            return
        
        self.lap = 0
        self.turn = None
        self.game_over = False
        self.player1 = p1
        self.player2 = p2 if p2 != None else ctx.message.author
        self.start_datetime = datetime.datetime.now()
        
        board:str = ""
        for c in range(0,len(self.board),3):
            board+=" ".join(self.board[c:c+3])
            board = board.replace("0",":white_large_square:")
            msg = await ctx.send(board)
            self.messages.append(msg)
            board=""
        
        self.turn = random.choice([self.player1,self.player2])
        msg = await ctx.send(f"Hamle sırası: {self.turn.mention}")
        self.messages.append(msg)
    
    
    @commands.command(name="place", aliases=["yerleştir"], help="Devam eden bir TicTacToe oyununda karakter yerleştirir.")
    async def place(self, ctx: commands.Context, pos: int):
        if self.game_over:
            embed = modules.create_embed(":x: İşlem Başarısız", "Devam eden bir oyun bulunmuyor. Lütfen yeni bir oyun başlatın.")
            await ctx.send(embed=embed)
            return
        
        if ctx.author != self.turn:
            await ctx.send(f"Sıra sende değil, lütfen sıranı bekle.", delete_after=2)
            return
        
        if pos < 1 or pos > 9:
            await ctx.send("Lütfen 1 ile 9 arasında bir rakam seç.", delete_after=2)
            return
        
        mark = ""
        
        if  self.turn == self.player1:
            mark = "1"
        elif self.turn == self.player2:
            mark = "2"
        
        if self.board[pos - 1] != "0":
            await ctx.send("Seçtiğiniz konum zaten dolu!!!", delete_after=2)
            return
        
        self.board[pos-1] = mark
        self.lap += 1
        
        board:str = ""
        for c in range(0,len(self.board),3):
            board+=" ".join(self.board[c:c+3])
            board = board.replace("0",":white_large_square:").replace("1",":regional_indicator_x:").replace("2",":o2:")
            if c == 0:  msg_o = self.messages[0]
            elif c == 3:  msg_o = self.messages[1]
            elif c == 6:  msg_o = self.messages[2]
            msg = await msg_o.edit(board)
            if c == 0: self.messages[0] = msg
            elif c == 3: self.messages[1] = msg
            elif c == 6: self.messages[2] = msg
            board=""
        
        for condition in self.winning_conditions:
            if self.board[condition[0]] == mark and self.board[condition[1]] == mark and self.board[condition[2]] == mark:
                self.game_over = True
        
        if self.game_over:
            await ctx.send(f"{self.turn.mention} kazandı!!!")
        elif self.lap >= 9:
            self.game_over = True
            await ctx.send("Berabere!!!!")
        
        self.turn = self.player1 if self.turn != self.player1 else self.player2
        msg_o = self.messages[3]
        msg = await msg_o.edit(f"Hamle sırası: {self.turn.mention}")
        self.messages[3] = msg
    
    
    @commands.command(name="tictactoe_stop", aliases=["tictactoe_durdur"], help="Devam eden bir TicTacToe oyununu sonlandırır.", roles=[constants.MODERATOR_ROLE])
    async def tictactoe_stop(self, ctx: commands.Context):
        if self.game_over:
            embed = modules.create_embed(":x: İşlem Başarısız", "Devam eden bir oyun bulunmuyor.")
            await ctx.send(embed=embed)
        else:
            embed = modules.create_embed(":white_check_mark: İşlem Başarılı", "Devam eden TicTacToe oyununu sonlandırıldı.")
            await ctx.send(embed=embed)
    
    
    @tasks.loop(minutes=5.0)
    async def check_timeout(self):
        if not self.game_over:
            td:datetime.timedelta = (datetime.datetime.now() - self.start_datetime)
            time_delta = int(divmod(td.total_seconds(), 60)[0])
            if time_delta > 30:
                self.game_over = True
    
    def cog_unload(self):
        self.check_timeout.cancel()


def setup(client: modules.MyBot):
    client.add_cog(TicTacToe(client))