import datetime
import json
import os
import re
import time
import shion_lib
import discord
import requests


class MyClient(discord.Client):

    async def on_ready(self):
        await client.change_presence(activity=discord.Game(name='!sbhelp'))

    async def on_message(self, message):
        path = os.path.dirname(os.path.abspath(__file__))
        if message.author == self.user:
            return
        blacklist = []
        if message.author.id in blacklist:
            return

        if re.compile(r"!ah").match(message.content):
            author = str(message.author.id)
            try:
                usrdata = path + "/usrdata/" + author +".json"
                f = open(usrdata)
                usr = json.load(f)
                name = str(usr["name"])
                profile_name = str(usr["profile_name"])
                profile_id = str(usr["profile_id"])
                embed = shion_lib.get_myauction(name, profile_id)
                await message.channel.send(message.author.mention,embed=embed)
            except ValueError:
                await message.channel.send(message.author.mention + shion_lib.ValueErrorMessage(profile_name))
            except FileNotFoundError:
                await message.channel.send(message.author.mention + shion_lib.FileNotFoundErrorMessage())
            return

        if re.compile(r"(!add )(.+)( |,)(.+)").match(message.content):
            author = str(message.author.id)
            com = re.match("(!add )(.+)( |,)(.+)", message.content)
            name = com.group(2)
            profile_name = com.group(4).capitalize()
            try:
                shion_lib.addnewusr(author, name, profile_name)
                await message.channel.send(f"{message.author.mention} Registration Completed.\nMinecraft Name: {name}\nProfile: {profile_name}")
            except ValueError:
                await message.channel.send(shion_lib.ValueErrorMessage(profile_name))
                
        if re.compile(r"!minion").match(message.content):
            author = str(message.author.id)
            try:
                usrdata = path + "/usrdata/" + author +".json"
                f = open(usrdata)
                usr = json.load(f)
                name = str(usr["name"])
                profile_id = str(usr["profile_id"])
                embed = shion_lib.get_minions_unlock(name, profile_id)
                await message.channel.send(message.author.mention,embed=embed)
            except ValueError:
                await message.channel.send(shion_lib.ValueErrorMessage(profile_name))
            except FileNotFoundError:
                await message.channel.send(message.author.mention + shion_lib.FileNotFoundErrorMessage())

        event_channels = []
        if message.author == self.user:
            return
        if message.channel.id in event_channels:
            if re.match(r"(!newyear|!ny)", message.content):
                result = shion_lib.get_event("New Years Event", "https://hypixel-api.inventivetalent.org/api/skyblock/newyear/estimate")
                await message.channel.send(message.author.mention + result)
            elif re.match(r"(!spooky|!sp)", message.content):
                result = shion_lib.get_event("Spooky Festival", "https://hypixel-api.inventivetalent.org/api/skyblock/spookyFestival/estimate")
                await message.channel.send(message.author.mention + result)
            elif re.match(r"(!magmaboss|!mb)", message.content):
                result = shion_lib.get_event("Magma Boss Spawn", "https://hypixel-api.inventivetalent.org/api/skyblock/bosstimer/magma/estimatedSpawn")
                await message.channel.send(message.author.mention + result)
            elif re.match(r"(!darkah|!da)", message.content):
                result = shion_lib.get_event("Dark Auction", "https://hypixel-api.inventivetalent.org/api/skyblock/darkauction/estimate")
                await message.channel.send(message.author.mention + result)
            elif re.match(r"!bank", message.content):
                result = shion_lib.get_event("Bank Interest", "https://hypixel-api.inventivetalent.org/api/skyblock/bank/interest/estimate")
                await message.channel.send(message.author.mention + result)
            else:
                pass
        
        if re.compile(r"!news").match(message.content):
            embed = shion_lib.get_sb_news()
            await message.channel.send(embed = embed)

        if re.compile(r"!sbhelp").match(message.content):
            embed = shion_lib.help()
            await message.channel.send(message.author.mention, embed=embed)


client = MyClient()
token = ("TOKEN")
client.run(token)
path = os.path.dirname(os.path.abspath(__file__))
