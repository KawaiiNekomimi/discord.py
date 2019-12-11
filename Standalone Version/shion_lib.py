import base64
import datetime
import io
import json
import os
import re
import time

import discord
import requests
from nbt import nbt


def ValueErrorMessage(profile_name):
    return f":warning: Profile Error\nProfile {profile_name} wasn't found.\nPlease check the profile name and use `!add` again."
def FileNotFoundErrorMessage():
    return f":warning: Information Error\nYou haven't registered your info yet. Please use the following command:\n```!add [Minecraft Name] [Profile Name]```\nUse `!sbhelp` for more information"

def help():
    embed = discord.Embed(title="Shion (Skyblock Assistant) Help Menu", color=0x00ff00)
    embed.add_field(name="!ah", value="Shows all ongoing and ended auctions in your Auction House", inline=False)
    embed.add_field(name="!minion", value="Shows your minion progress", inline=False)
    embed.add_field(name="!news", value="Shows the latest Skyblock patch notes", inline=False)
    embed.add_field(name="!add [MCID] [Profile]", value=f"Registeres needed info for some commands such as !ah\nExample usage: `!add CuteNekoLoli Raspberry`",inline=False)
    embed.add_field(name="!sbhelp", value="Displays this help message")
    #embed.add_field(name="Contact", value="ヘルプを見てもわからないときは開発者にメンションしてください", inline=False)
    embed.add_field(name="Bot Developer", value="翡翠#8249", inline=False)
    embed.add_field(name="Translated by", value="Fear#3939 (Report translation errors to me)")
    return embed

def get_event(event_name, url):
    data = requests.get(url, headers={"content-type": "application/json"}).json()
    delta = datetime.timedelta(seconds=int(((data["estimate"]) // 1000) - time.time()))
    deltam, deltas = divmod(delta.seconds, 60)
    deltah, deltam = divmod(deltam, 60)
    deltad = delta.days
    result = str(f"Next **{event_name}** starts in {deltad}d {deltah}h {deltam}m {deltas}s!")
    return result

def get_sb_news():
    news = requests.get(f"https://api.hypixel.net/skyblock/news?key={api_key}", headers = {"content-type": "application/json"}).json()
    ver = news["items"][0]["title"]
    embed = discord.Embed(title=f"Patch Notes **{ver}**", color=0x00ff00)
    text = str(news["items"][0]["text"])
    com = re.search(r"(.*)(\s\s)(.*)",text,re.S)
    release = com.group(1)
    cont = com.group(3)
    link = news["items"][0]["link"]
    embed.add_field(name="Update: ", value=f"**{cont}**", inline=True)
    embed.add_field(name="Released on: ", value=release, inline=False)
    embed.add_field(name="Forum: ", value=link, inline=False)
    return embed


def get_minions_unlock(name, profile_id):
    data = requests.get(f"https://api.hypixel.net/skyblock/profile?key={api_key}&profile={profile_id}", headers={"content-type": "application/json"}).json()
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
    embed.add_field(name=f":information_source: Total times minions were created/upgraded", value=f"**{total}** 回")
    embed.add_field(name=f":free: Number of minions that can be placed", value=f"**{result}** 枠")
    embed.add_field(name=f":up: Next minion slot", value=f"**{next}** 回")
    return embed

def get_myauction(name, profile_id):
    r = requests.get(f"https://api.hypixel.net/skyblock/auction?key={api_key}&name={name}&profile={profile_id}", headers = {"content-type": "application/json"})
    data = r.json()
    myauction = list(data["auctions"])
    embed = discord.Embed(title=f"**{name}** さんのオークション", color=0x00ff00)
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
                embed.add_field(name=f":arrows_counterclockwise: Item: {count}×{item}", value=f"Time Remaining: {deltad}d {deltah}h {deltam}m {deltas}s\n**Highest Bid**: {highbid} coin", inline=False)
                highbid = highbid.replace(",", "")
                total_coins = total_coins + int(highbid)
            else:
                if int(unclaimed["highest_bid_amount"]) == 0:
                    embed.add_field(name=f":warning: Item: {count}×{item}", value=f"**Time Remaining**: Ended\n**Highest Bid**: No bid", inline=False)
                else:
                    embed.add_field(name=f":white_check_mark: Item: {count}×{item}", value=f"**Time Remaining**: Ended\n**Highest Bid**: {highbid} coin", inline=False)
                    highbid = highbid.replace(",", "")
                    total_coins = total_coins + int(highbid)
    if not embed.fields:
        embed.add_field(name = f":information_source: No auctions",value =f"There aren't any uncollected auctions",inline=False)
    embed.add_field(name=":moneybag: 売上総額:", value="{: ,} ".format(int(total_coins)) +" coin", inline=False)
    return embed

def addnewusr(author, name, profile_name):
    data = requests.get(f"https://api.hypixel.net/player?key={api_key}&name={name}", headers = {"content-type": "application/json"}).json()
    profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
    for profs in profiles.values():
        if (profs["cute_name"]) == profile_name:
            profile_id = profs["profile_id"]
            newfile = "usrdata/"+ author +".json"
            with open(newfile, "w") as nf:
                data = {"name": name, "profile_name": profile_name, "profile_id": profile_id}
                json.dump(data, nf, ensure_ascii=False)
                return name, profile_name, profile_id
    raise ValueError

api_key = "API_KEY"
