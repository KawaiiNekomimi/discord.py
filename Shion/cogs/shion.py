import base64
import datetime
import glob
import io
import json
import os
import random
import re
import time
from time import mktime

import discord
import feedparser
import requests
from nbt import nbt
from discord.ext import commands # Imports command handling from Discord.

import datetime # Imports a tool to work with date and time.

path = os.path.dirname(os.path.abspath(__file__))

def config_load():
    path = os.path.dirname(os.path.abspath(__file__)) #needed to define again for Windows users
    path = path.strip("cogs")
    with open(path + 'data/config.json', 'r', encoding='utf-8-sig') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)

def global_id_load():
    with open(path + '/global_notification/global_ids.json', 'r', encoding='utf-8-sig') as doc:
        return json.load(doc)

global_ids = global_id_load()
config = config_load()
# Add channel ID here to notify channels from
notification_id = 123456789012345678

class Shion(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot: #Ignores all bots656896858807074837
            return
        # Example on how to add regex to a command
        #if re.compile(r"!ny").match(message.content):
        #    ctx = await self.bot.get_context(message)
        #    ny_command = self.bot.get_command("newyear")
        #    await ctx.invoke(ny_command)
        #    return
        if message.channel.id == notification_id and int(config['owner_id']) == int(message.author.id):
            notice = global_ids['channel_list']
            for channel in notice:
                notice_channel = self.bot.get_channel(channel)
                if not notice_channel == None:
                    await notice_channel.send(message.content)

    @commands.command()
    @commands.guild_only()
    async def addnotification(self, ctx, channel: int = None):
        if not channel:
            return
        global_ids['channel_list'].append(channel)
        with open(path + '/global_notification/global_ids.json', 'w', encoding='utf-8-sig') as doc:
            json.dump(global_ids, doc)
        await ctx.send(f"Added {channel} to notification list.")


    @commands.command()
    @commands.guild_only()
    async def notify(self, ctx, *, message: str = None):
        if not message:
            return
        notice = global_ids['channel_list']
        for channel in notice:
            notice_channel = self.bot.get_channel(channel)
            if not notice_channel == None:
                await notice_channel.send(message)

    @commands.command()
    @commands.guild_only()
    async def add(self, ctx, name: str = None, profile_name: str = None):
        if await self.check_blacklist(ctx, ctx.author):
            await self.message_in_blacklist(ctx)
            return
        if not name or not profile_name:
            await ctx.send("Please use this command in the following format:\n```!add (mcid) (profile name)```")
            return
        try:
            await self.add_new_user(ctx, name, profile_name)
        except ValueError:
            await ctx.send("Something you entered wasn't correct! Please try again.")

    @commands.command(aliases=["souls"])
    @commands.guild_only()
    async def soul(self, ctx):
        check_blacklist = await self.check_blacklist(ctx, ctx.author)
        if check_blacklist:
            await self.message_in_blacklist(ctx)
            return
        try:
            await self.get_soul_count(ctx)
        except ValueError:
            await self.message_profile_not_found(ctx)
        except FileNotFoundError:
            await self.message_userdata_not_found(ctx)
        return

    @commands.command(aliases=["jerry", "update"])
    @commands.guild_only()
    async def patch(self, ctx):
        await self.get_sb_patch(ctx)

    @commands.command(aliases=["auctions", "auctionhouse"])
    @commands.guild_only()
    async def ah(self, ctx):
        try:
            await self.get_my_auction(ctx)
        except ValueError:
            await self.message_profile_not_found(ctx)
        except FileNotFoundError:
            await self.message_userdata_not_found(ctx)
        return

    @commands.command()
    @commands.guild_only()
    async def minion(self, ctx):
        try:
            await self.get_minions_unlock(ctx)
        except ValueError:
            await self.message_profile_not_found(ctx)
        except FileNotFoundError:
            await self.message_userdata_not_found(ctx)

    @commands.command()
    @commands.guild_only()
    async def seen(self, ctx, name: str = None):
        await self.get_player_session(ctx, name)

    @commands.command()
    @commands.guild_only()
    async def sbhelp(self, ctx):
        await self.sb_help(ctx)

    @commands.command()
    @commands.guild_only()
    async def newyear(self, ctx):
        result = await self.get_event("New Years Event",
            "https://hypixel-api.inventivetalent.org/api/skyblock/newyear/estimate")
        await ctx.send(result)

    @commands.command()
    @commands.guild_only()
    async def spooky(self, ctx):
        result = await self.get_event("Spooky Festival",
            "https://hypixel-api.inventivetalent.org/api/skyblock/spookyFestival/estimate")
        await ctx.send(result)

    @commands.command()
    @commands.guild_only()
    async def magmaboss(self, ctx):
        result = await self.get_event("Magma Boss Spawn",
            "https://hypixel-api.inventivetalent.org/api/skyblock/bosstimer/magma/estimatedSpawn")
        await ctx.send(result)

    @commands.command()
    @commands.guild_only()
    async def darkauction(self, ctx):
        result = await self.get_event("Dark Auction",
            "https://hypixel-api.inventivetalent.org/api/skyblock/darkauction/estimate")
        await ctx.send(result)

    @commands.command()
    @commands.guild_only()
    async def bank(self, ctx):
        result = await self.get_event("Bank Interest",
            "https://hypixel-api.inventivetalent.org/api/skyblock/bank/interest/estimate")
        await ctx.send(result)

    async def check_blacklist(self, ctx, author): #Blacklist is a directory contains text files named [user.id]. The reason you set is written in these files.
        author = str(ctx.author.id)
        check = path + "/blacklist/" + author +".txt"
        blacklist = glob.glob(f"{path}/blacklist/*.txt")
        for f in blacklist:
            if f == check:
                return True

    async def get_event(self, event_name, url):
        data = requests.get(url, headers={"content-type": "application/json"}).json()
        delta = datetime.timedelta(seconds=int(((data["estimate"]) // 1000) - time.time()))
        deltam, deltas = divmod(delta.seconds, 60)
        deltah, deltam = divmod(deltam, 60)
        deltad = delta.days
        result = str(f"Next **{event_name}** starts in {deltad}d {deltah}h {deltam}m {deltas}s!")
        return result

    async def message_in_blacklist(self, ctx):
        author = str(ctx.author.id)
        check = path + "/blacklist/" + author +".txt"
        reason = open(check,"r").read()
        await ctx.send(ctx.author.mention + f":warning: You are blacklisted from using commands!\nReason: {reason}")
        return 

    async def sb_help(self, ctx):
        embed = discord.Embed(title="Shion (Skyblock Assistant) Help Menu", color=0x00ff00)
        embed.add_field(name="!ah", value="Shows all ongoing and ended auctions in your Auction House", inline=False)
        embed.add_field(name="!minion", value="Shows your minion progress", inline=False)
        embed.add_field(name="!news", value="Show the latest Skyblock release notes", inline=False)
        embed.add_field(name="!patch", value="Shows the latest Skyblock patch notes", inline=False)
        embed.add_field(name="!soul", value="Shows your fairy souls progress", inline=False)
        embed.add_field(name="!seen [MCID]", value="Show [MCID]'s recent activity in server")
        embed.add_field(name="!add [MCID] [Profile]", value=f"Registeres needed info for some commands such as !ah\nExample usage: `!add hisuie08 Mango`",inline=False)
        embed.add_field(name="!sbhelp", value="Displays this help message")
        #embed.add_field(name="Bot Manager", value=f"{owner_name}")
        embed.add_field(name="Bot Developer", value="翡翠#8249", inline=False)
        await ctx.send(ctx.author.mention, embed = embed)
        return

    async def get_player_session(self, ctx, name):
        uuid = await self.get_uuid(name)
        data = requests.get(f"https://api.hypixel.net/player?key=536a6eda-ef2a-4e24-b518-27e1c9ba16a9&uuid={uuid}", headers={"content-type": "application/json"}).json()
        if data["player"]["lastLogin"] < data["player"]["lastLogout"]:
            session = "Offline"
            embed = discord.Embed(title=f"{name}",color = 0x00ff00)
            embed.add_field(name="Status",value=session,inline=False)
            end = int(time.time() - (data["player"]["lastLogin"] // 1000))
            delta = datetime.timedelta(seconds=int(end))
            deltam, deltas = divmod(delta.seconds, 60)
            deltah, deltam = divmod(deltam, 60)
            deltad = delta.days
            embed.add_field(name="Last Login",value=f"{deltad}d {deltah}h {deltam}m {deltas}s ago.")
        else:
            session = "Online"
            embed.add_field(name="Status",value=session,inline=False)
            if "mostRecentGameType" in data["player"].keys():
                joining_game = data["player"]["mostRecentGameType"]
            else:
                joining_game = "The player doesn't play any minigames."
                embed.add_field(name="Now Playng", value=joining_game, inline=False)
        await ctx.send(ctx.author.mention, embed=embed)
        return
    async def get_minions_unlock(self, ctx):
        author = str(ctx.author.id)
        usrdata = path + "/usrdata/" + author + ".json"
        f = open(usrdata)
        usr = json.load(f)
        name = str(usr["name"])
        profile_id = str(usr["profile_id"])
        data = requests.get(f"https://api.hypixel.net/skyblock/profile?key={config['api_key']}&profile={profile_id}", headers={"content-type": "application/json"}).json()
        total = 0
        minions_data = []
        for members in data["profile"]["members"]:
            if "crafted_generators" in data["profile"]["members"][members]:
                for minion in data["profile"]["members"][members]["crafted_generators"]:
                    minions_data.append(minion)
        minions = list(set(minions_data))
        total = len(minions)
        result = 5
        for i in [5, 15, 30, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275, 300, 350, 400, 450, 500, 550]:
            if i <= total:
                result = result + 1
            else:
                next = (i - total)
                break
        embed = discord.Embed(title=f"**{name}**'s Minions", color=0x00ff00)
        embed.add_field(name=f":information_source: Minions upgraded/unlocked", value=f"**{total}** times")
        embed.add_field(name=f":free: Minion slots unlocked", value=f"**{result}** slots")
        embed.add_field(name=f":up: Next minion slot", value=f"**{next}** times")
        await ctx.send(ctx.author.mention,embed=embed)
        return

    async def get_my_auction(self, ctx):
        author = str(ctx.author.id)
        usrdata = path + "/usrdata/" + author + ".json"
        f = open(usrdata)
        usr = json.load(f)
        name = str(usr["name"])
        profile_id = str(usr["profile_id"])
        r = requests.get(f"https://api.hypixel.net/skyblock/auction?key={config['api_key']}&name={name}&profile={profile_id}", headers = {"content-type": "application/json"})
        data = r.json()
        myauction = list(data["auctions"])
        embed = discord.Embed(title=f"**{name}**'s Auctions", color=0x00ff00)
        total_coins = 0
        for unclaimed in myauction:
            if (unclaimed["claimed"]) == False:
                item = str(unclaimed["item_name"])
                raw = str(re.sub(r"\u003d", r"=", str(unclaimed["item_bytes"]["data"])))
                nbtobj = nbt.NBTFile(fileobj=io.BytesIO(base64.b64decode(raw)))
                for tag in nbtobj['i'].tags:
                    count = tag['Count'].valuestr()
                end = int(((unclaimed["end"]) // 1000) - time.time())
                delta = datetime.timedelta(seconds=int(end))
                deltam, deltas = divmod(delta.seconds, 60)
                deltah, deltam = divmod(deltam, 60)
                deltad = delta.days
                highbid = "{:,}".format(int(unclaimed["highest_bid_amount"]))
                if end > 0:
                    embed.add_field(name=f":arrows_counterclockwise: Item: {count}×{item}", value=f"Time Remaining: {deltad}d {deltah}h {deltam}m {deltas}s\n**Highest Bid**: {highbid} coins", inline=False)
                    highbid = highbid.replace(",", "")
                    total_coins = total_coins + int(highbid)
                else:
                    if int(unclaimed["highest_bid_amount"]) == 0:
                        embed.add_field(name=f":warning: Item: {count}×{item}", value=f"**Time Remaining**: Ended\n**Highest Bid**: No bid", inline=False)
                    else:
                        embed.add_field(name=f":white_check_mark: Item: {count}×{item}", value=f"**Time Remaining**: Ended\n**Highest Bid**: {highbid} coins", inline=False)
                        highbid = highbid.replace(",", "")
                        total_coins = total_coins + int(highbid)
        if not embed.fields:
            embed.add_field(name = f":information_source: No auctions",value =f"There aren't any uncollected auctions",inline=False)
        embed.add_field(name=":moneybag: Total Coins:", value="{: ,} ".format(int(total_coins)) +" coins", inline=False)
        await ctx.send(ctx.author.mention,embed=embed)
        return

    async def message_profile_not_found(self, ctx):
        await ctx.send(ctx.author.mention + f":warning: Profile Error\nProfile wasn't found.\nPlease check the profile name and use `!add` again.")

    async def message_userdata_not_found(self, ctx):
        await ctx.send(ctx.author.mention
            + f":warning: Information Error\nYou haven't registered your info yet. Please use the following command:\n```!add [Minecraft Name] [Profile Name]```\nUse `!sbhelp` for more information")

    async def get_uuid(self, name):
        return (requests.get(f"https://api.mojang.com/users/profiles/minecraft/{name}", headers={"content-type": "application/json"}).json())["id"]

    async def get_soul_count(self, ctx):
        author = str(ctx.author.id)
        f = open(path + "/usrdata/" + author + ".json")
        usr = json.load(f)
        name = str(usr["name"])
        profile_id = str(usr["profile_id"])
        sbdata = requests.get(f"https://api.hypixel.net/skyblock/profile?key={config['api_key']}&name={name}&profile={profile_id}", headers={"content-type": "application/json"}).json()
        uuid = await self.get_uuid(name)
        myinfo = (sbdata["profile"]["members"][uuid])
        fairy_souls_collected= (myinfo["fairy_souls_collected"])
        fairy_exchanges = (myinfo["fairy_exchanges"])
        fairy_souls = (myinfo["fairy_souls"])
        embed = discord.Embed(title=f"**{name}**'s Fairy Souls",color=0xff00ff)
        embed.add_field(name=f":gem: Total Found Souls", value=f"**{fairy_souls_collected}**")
        embed.add_field(name=f":scales: Souls Exchanged", value=f"**{fairy_exchanges}** times")
        embed.add_field(name=f":handbag: Unexchanged Souls", value=f"**{fairy_souls}**")
        await ctx.send(ctx.author.mention, embed=embed)
        return

    async def add_new_user(self, ctx, name, profile_name):
        author = str(ctx.author.id)
        data = requests.get(f"https://api.hypixel.net/player?key={config['api_key']}&name={name}", headers = {"content-type": "application/json"}).json()
        profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
        for profs in profiles.values():
            if (profs["cute_name"]) == profile_name:
                profile_id = profs["profile_id"]
                newfile = path + "/usrdata/" + author +".json"
                with open(newfile, "w") as nf:
                    data = {"name": name, "profile_name": profile_name, "profile_id": profile_id}
                    json.dump(data, nf, ensure_ascii=False)
                await ctx.send(ctx.author.mention + f"Registeration complete.\nMCID: {name}\nProfile: {profile_name}\nSee `!sbhelp` for a list of commands.")
                return
        raise ValueError

    async def get_sb_patch(self, ctx):
        p = feedparser.parse("https://hypixel.net/forums/skyblock-patch-notes.158/index.rss")
        entry = feedparser.FeedParserDict(p.entries[0])
        title = entry.title
        link = entry.link
        embed = discord.Embed(title=f"The Latest Patch Note {title}", color=0xffa550)
        embed.add_field(name=f"Link to Forum", value=f"{link}",inline=False)
        embed.add_field(name="previous Pathes are here", value=f"https://hypixel.net/forums/skyblock-patch-notes.158/",inline=False)
        await ctx.send(embed=embed)
        return

def setup(bot):
    n = Shion(bot)
    bot.add_cog(n)
