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


###############################################
###   Set these fields before running bot   ###
###############################################

#Keep all written it in PRIVATE! Or your bot could be hacked! 
token = "Bot Token"
api_list = ["Hypixel API Key", "Hypixel API Key 2 (Optional)", "Hypixel API Key 3 (Optional"]  #Delete any unused slots

#Lets the bot know who the owner is for owner-only commands
owner_name = "User#0000" #Set your Discord name and tag.
owner_id = 000000000000000000  #Set your discord unique id as int.

#Useful if you want to run the bot in multiple guilds
global_notice_from = 0000000000000000  #Channel ID of the channel you will send announcements from. The bot will accept input and...
global_notice_to = [111111111111, 222222222222, 3333333333]  #Re-send it to all channels in this list.

#If you want to allow to use command in only parts of channels, use this. In default event command is set.
unpublished_channels = [111111111111, 222222222222, 3333333333]
###############################################
##########        End Setting        ##########
###############################################


def add_blacklist(message):
    author = re.match("(!addblacklist )(.+)( )(.+)", message.content).group(2)
    reason = re.match("(!addblacklist )(.+)( )(.+)", message.content).group(4)
    with open(path + "/blacklist/" + author + ".txt", "w") as bl:
        bl.write(reason)
    return message.channel.send(message.author.mention + f"I've added the user to the blacklist. They will no longer be able to use commands.\n. UserID: {author} Reason: {reason}")


def add_new_user(message):
    author = str(message.author.id)
    com = re.match("(!add )(.+)( |,)(.+)", message.content)
    name = com.group(2)
    profile_name = com.group(4).capitalize()
    data = requests.get(f"https://api.hypixel.net/player?key={api_key}&name={name}", headers = {"content-type": "application/json"}).json()
    profiles = (data["player"]["stats"]["SkyBlock"]["profiles"])
    for profs in profiles.values():
        if (profs["cute_name"]) == profile_name:
            profile_id = profs["profile_id"]
            newfile = path + "/usrdata/" + author +".json"
            with open(newfile, "w") as nf:
                data = {"name": name, "profile_name": profile_name, "profile_id": profile_id}
                json.dump(data, nf, ensure_ascii=False)
            base_message = f"Registeration complete.\nMCID: {name}\nProfile: {profile_name}\nSee `!sbhelp` for a list of commands."
            return message.channel.send(message.author.mention + base_message)
    raise ValueError


def check_blacklist(message): #Black list is a directory contains text files named [user.id]. The reason you set is written in these files.
    author = str(message.author.id)
    check = path + "/blacklist/" + author +".txt"
    blacklist = glob.glob(f"{path}/blacklist/*.txt")
    for f in blacklist:
        if f == check:
            return True


def message_in_blacklist(message):
    author = str(message.author.id)
    check = path + "/blacklist/" + author +".txt"
    reason = open(check,"r").read()
    return message.channel.send(message.author.mention + f":warning: You are blacklisted from using commands!\nReason: {reason}")
def message_profile_not_found(message):
    return message.channel.send(message.author.mention + f":warning: Profile Error\nProfile wasn't found.\nPlease check the profile name and use `!add` again.")
def message_userdata_not_found(message):
    return message.channel.send(message.author.mention
        + f":warning: Information Error\nYou haven't registered your info yet. Please use the following command:\n```!add [Minecraft Name] [Profile Name]```\nUse `!sbhelp` for more information")


def get_event(event_name, url):
    data = requests.get(url, headers={"content-type": "application/json"}).json()
    delta = datetime.timedelta(seconds=int(((data["estimate"]) // 1000) - time.time()))
    deltam, deltas = divmod(delta.seconds, 60)
    deltah, deltam = divmod(deltam, 60)
    deltad = delta.days
    result = str(f"Next **{event_name}** starts in {deltad}d {deltah}h {deltam}m {deltas}s!")
    return result


def get_minions_unlock(message):
    author = str(message.author.id)
    usrdata = path + "/usrdata/" + author + ".json"
    f = open(usrdata)
    usr = json.load(f)
    name = str(usr["name"])
    profile_id = str(usr["profile_id"])
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
    embed.add_field(name=f":information_source: Minions upgraded/unlocked", value=f"**{total}** times")
    embed.add_field(name=f":free: Minion slots unlocked", value=f"**{result}** slots")
    embed.add_field(name=f":up: Next minion slot", value=f"**{next}** times")
    return message.channel.send(message.author.mention,embed=embed)


def get_my_auction(message):
    author = str(message.author.id)
    usrdata = path + "/usrdata/" + author + ".json"
    f = open(usrdata)
    usr = json.load(f)
    name = str(usr["name"])
    profile_id = str(usr["profile_id"])
    r = requests.get(f"https://api.hypixel.net/skyblock/auction?key={api_key}&name={name}&profile={profile_id}", headers = {"content-type": "application/json"})
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
    return message.channel.send(message.author.mention,embed=embed)


def get_player_session(message):
    name = re.match("(!seen )(.+)",message.content).group(2)
    embed = discord.Embed(title=f"{name}",color = 0x00ff00)
    uuid = get_uuid(name)
    data = requests.get(f"https://api.hypixel.net/player?key=536a6eda-ef2a-4e24-b518-27e1c9ba16a9&uuid={uuid}", headers={"content-type": "application/json"}).json()
    if data["player"]["lastLogin"] < data["player"]["lastLogout"]:
        session = "Offline"
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
    return message.channel.send(message.author.mention, embed=embed)


def get_sb_news(message):
    news = requests.get(f"https://api.hypixel.net/skyblock/news?key={api_key}", headers = {"content-type": "application/json"}).json()
    ver = news["items"][0]["title"]
    embed = discord.Embed(title=f"{ver} Released!", color=0x00ff00)
    text = str(news["items"][0]["text"])
    com = re.search(r"(.*)(\s\s)(.*)",text,re.S)
    release = com.group(1)
    cont = com.group(3)
    link = news["items"][0]["link"]
    embed.add_field(name="Update: ", value=f"**{cont}**", inline=True)
    embed.add_field(name="Released on: ", value=release, inline=False)
    embed.add_field(name="Forum: ", value=link, inline=False)
    return message.channel.send(embed=embed)


def get_sb_patch(message):
    p = feedparser.parse("https://hypixel.net/forums/skyblock-patch-notes.158/index.rss")
    entry = feedparser.FeedParserDict(p.entries[0])
    title = entry.title
    link = entry.link
    embed = discord.Embed(title=f"The Latest Patch Note {title}", color=0xffa550)
    embed.add_field(name=f"Link to Forum", value=f"{link}",inline=False)
    embed.add_field(name="previous Pathes are here", value=f"https://hypixel.net/forums/skyblock-patch-notes.158/",inline=False)
    return message.channel.send(embed = embed)


def get_soul_count(message):
    author = str(message.author.id)
    f = open(path + "/usrdata/" + author + ".json")
    usr = json.load(f)
    name = str(usr["name"])
    profile_id = str(usr["profile_id"])
    sbdata = requests.get(f"https://api.hypixel.net/skyblock/profile?key={api_key}&name={name}&profile={profile_id}", headers={"content-type": "application/json"}).json()
    uuid = get_uuid(name)
    myinfo = (sbdata["profile"]["members"][uuid])
    fairy_souls_collected= (myinfo["fairy_souls_collected"])
    fairy_exchanges = (myinfo["fairy_exchanges"])
    fairy_souls = (myinfo["fairy_souls"])
    embed = discord.Embed(title=f"**{name}**'s Fairy Souls",color=0xff00ff)
    embed.add_field(name=f":gem: Total Found Souls", value=f"**{fairy_souls_collected}**")
    embed.add_field(name=f":scales: Souls Exchanged", value=f"**{fairy_exchanges}** times")
    embed.add_field(name=f":handbag: Unexchanged Souls", value=f"**{fairy_souls}**")
    return message.channel.send(message.author.mention,embed=embed)


def get_uuid(name):
    return (requests.get(f"https://api.mojang.com/users/profiles/minecraft/{name}", headers={"content-type": "application/json"}).json())["id"]


def sb_help(message):
    embed = discord.Embed(title="Shion (Skyblock Assistant) Help Menu", color=0x00ff00)
    embed.add_field(name="!ah", value="Shows all ongoing and ended auctions in your Auction House", inline=False)
    embed.add_field(name="!minion", value="Shows your minion progress", inline=False)
    embed.add_field(name="!news", value="Show the latest Skyblock release notes", inline=False)
    embed.add_field(name="!patch", value="Shows the latest Skyblock patch notes", inline=False)
    embed.add_field(name="!soul", value="Shows your fairy souls progress", inline=False)
    embed.add_field(name="!seen [MCID]", value="Show [MCID]'s recent activity in server")
    embed.add_field(name="!add [MCID] [Profile]", value=f"Registeres needed info for some commands such as !ah\nExample usage: `!add hisuie08 Mango`",inline=False)
    embed.add_field(name="!sbhelp", value="Displays this help message")
    embed.add_field(name="Bot Manager", value=f"{owner_name}")
    embed.add_field(name="Bot Developer", value="翡翠#8249", inline=False)
    return message.channel.send(message.author.mention, embed = embed)


path = os.path.dirname(os.path.abspath(__file__))
api_key = random.choice(api_list)
