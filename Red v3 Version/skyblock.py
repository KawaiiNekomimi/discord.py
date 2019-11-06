import asyncio
import datetime
import json
import os
import re
import time
import discord
import requests

from typing import Any, Union
from discord.utils import get
from discord.ext.commands import MemberConverter

from redbot.core.data_manager import bundled_data_path
from redbot.core import Config, checks, commands
from redbot.core.utils.chat_formatting import pagify, box
from redbot.core.utils.predicates import MessagePredicate
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS

from redbot.core.bot import Red


Cog: Any = getattr(commands, "Cog", object)

listener = getattr(commands.Cog, "listener", None)
if listener is None:

    def listener(name=None):
        return lambda x: x

class Skyblock(Cog):
    """
    SB Auction Checker
    """
    def __init__(self, bot: Red):
        self.bot = bot
        self.config = Config.get_conf(
            self, identifier=16548964843212310, force_registration=True
        )
        #Registers users with blank string defaults
        self.config.register_member(
            api_key="",
            name="",
            profile_name=""
        )

    #Builds url for api access
    #Credit: hisuie08
    def getendpointurl(self,key,name,profilename,endpoint):
        url = str("https://api.hypixel.net/player?key=" + (key) + "&name=" + (name))
        headers = {"content-type": "application/json"}
        r = requests.get(url, headers=headers)
        data = r.json()
        profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
        for profs in profiles.values():#SBのｴﾝﾄﾞﾎﾟｲﾝﾄの取得にはﾌﾟﾛﾌｧｲﾙ名ではなくﾌﾟﾛﾌｧｲﾙIDっていうのを使うらしく二度手間()
            if (profs["cute_name"]) == profilename:
                url = str("https://api.hypixel.net/" + (endpoint)+  "?key=" + (key) + "&name=" + (name) + "&profile=" + str(profs["profile_id"]))
                return url

    #Builds embed for Auction House items
    #Adapted from hisuie08's code
    def getmyauction(self, key, name, profilename):
        endpoint = "skyblock/auction"
        url = self.getendpointurl(key, name,profilename, endpoint)
        headers = {"content-type": "application/json"}
        r = requests.get(url, headers=headers)
        data = r.json()
        myauction = list(data["auctions"])
        total_coins = 0
        ahembed=discord.Embed(title="Auction House", color=0x00ff00)
        for unclaimed in myauction:
            if (unclaimed["claimed"]) == False:#回収されていないものを選別
                item = str(unclaimed["item_name"])
                end = int(((unclaimed["end"])//1000)-time.time())#ﾊｲﾋﾟAPIでは時刻はUNIXｴﾎﾟｯｸ時間のﾐﾘ秒で提供されるので秒に揃えて現在の時間との差分を算出
                delta = datetime.timedelta(seconds=int(end))#UNIXｴﾎﾟｯｸ時間の単位は秒だから脳死割り算で日、時間、分を出せる便利
                deltam, deltas = divmod(delta.seconds, 60)#分
                deltah, deltam = divmod(deltam, 60)#時間
                deltad,deltah = divmod(deltah,24)#日
                highbid = "{:,}".format(int(unclaimed["highest_bid_amount"]))
                if end > 0:#ここからはbidの状態判定。まず終了しているかどうか
                    ahembed.add_field(name=f":arrows_counterclockwise: Item: {item}", value=f"**Time Left**: {deltad}d {deltah}h {deltam}m {deltas}s\n**Highest bid**: {highbid} coins", inline=False)
                    highbid = highbid.replace(",", "")
                    total_coins = total_coins + int(highbid)
                else:
                    if int(unclaimed["highest_bid_amount"]) == 0:#終了していればbidの有無を判定してそれぞれ出力するﾒｯｾｰｼﾞに入れ込みます
                        ahembed.add_field(name=f":warning: Item: {item}", value=f"**Time Left**: Ended\n**Highest bid**: No bids :(", inline=False)
                    else:
                        ahembed.add_field(name=f":white_check_mark: Item: {item}", value=f"**Time Left**: Ended\n**Highest bid**: {highbid} coins", inline=False)
                        highbid = highbid.replace(",", "")
                        total_coins = total_coins + int(highbid)
        #Added to show total coins of all items
        ahembed.add_field(name=":moneybag: Total Coins:", value="{:,}".format(int(total_coins)))
        return ahembed

    @commands.command()
    @commands.guild_only()
    async def ah(self, ctx: commands.Context):
        """Check your Hypixel SB Auctions"""
        key = str(await self.config.member(ctx.author).api_key())
        name = str(await self.config.member(ctx.author).name())
        profilename = str(await self.config.member(ctx.author).profile_name())
        try:
            self.getmyauction(key, name, profilename)
            ahembed = self.getmyauction(key, name, profilename)
            await ctx.send(embed=ahembed)
        except KeyError:
            await ctx.send(f"{ctx.author.mention}\n:warning: Either the API key you entered was invalid, or you need to use `!register`.")
        return

    @commands.command(aliases=["add"])
    @commands.guild_only()
    async def register(self, ctx: commands.Context, key: str, name: str, profilename: str):
        """Registers a user's API key"""
        await self.config.member(ctx.author).api_key.set(f"{key}")
        await self.config.member(ctx.author).name.set(f"{name}")
        await self.config.member(ctx.author).profile_name.set(f"{profilename}")
        await ctx.send(f"Successfully Registered for your {profilename} profile.")
        return
