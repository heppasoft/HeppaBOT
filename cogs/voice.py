import modules
import discord
import requests
import typing as t
from modules import constants
import speech_recognition as sr
from discord.ext import commands


class Voice(modules.MyCog):
    def __init__(self, client: modules.MyBot) -> None:
        self.client = client

def setup(client: modules.MyBot):
    client.add_cog(Voice(client))