import os
import re
import sys

import discord

import shion_lib

class MyClient(discord.Client):

    async def on_ready(self):
        await client.change_presence(activity=discord.Game(name='!sbhelp'))

    async def on_message(self, message):
        if message.author == self.user:
            return

        if re.compile(r"!soul").match(message.content):
            if shion_lib.check_blacklist(message):
                await shion_lib.message_in_blacklist(message)
                return
            try:
                await shion_lib.get_soul_count(message)
            except ValueError:
                await shion_lib.message_profile_not_found(message)
            except FileNotFoundError:
                await shion_lib.message_userdata_not_found(message)
            return

        if re.compile(r"!ah").match(message.content):
            if shion_lib.check_blacklist(message):
                await shion_lib.message_in_blacklist(message)
                return
            try:
                await shion_lib.get_my_auction(message)
            except ValueError:
                await shion_lib.message_profile_not_found(message)
            except FileNotFoundError:
                await shion_lib.message_userdata_not_found(message)
            return

        if re.compile(r"(!add )(.+)( )(.+)").match(message.content):
            if shion_lib.check_blacklist(message):
                await shion_lib.message_in_blacklist(message)
                return
            try:
                await shion_lib.add_new_user(message)
            except ValueError:
                await shion_lib.message_profile_not_found(message)

        if re.compile(r"!minion").match(message.content):
            if shion_lib.check_blacklist(message):
                await shion_lib.message_in_blacklist(message)
                return
            try:
                await shion_lib.get_minions_unlock(message)
            except ValueError:
                await shion_lib.message_profile_not_found(message)
            except FileNotFoundError:
                await shion_lib.message_userdata_not_found(message)


        unpublished_channels = shion_lib.unpublished_channels
        if message.channel.id in unpublished_channels:
            if re.match(r"(!newyear|!ny)", message.content):
                result = shion_lib.get_event("New Years Event",
                                             "https://hypixel-api.inventivetalent.org/api/skyblock/newyear/estimate")
                await message.channel.send(message.author.mention + result)
            elif re.match(r"(!spooky|!sp)", message.content):
                result = shion_lib.get_event("Spooky Festival",
                                             "https://hypixel-api.inventivetalent.org/api/skyblock/spookyFestival/estimate")
                await message.channel.send(message.author.mention + result)
            elif re.match(r"(!magmaboss|!mb)", message.content):
                result = shion_lib.get_event("Magma Boss Spawn",
                                             "https://hypixel-api.inventivetalent.org/api/skyblock/bosstimer/magma/estimatedSpawn")
                await message.channel.send(message.author.mention + result)
            elif re.match(r"(!darkah|!da)", message.content):
                result = shion_lib.get_event("Dark Auction",
                                             "https://hypixel-api.inventivetalent.org/api/skyblock/darkauction/estimate")
                await message.channel.send(message.author.mention + result)
            elif re.match(r"!bank", message.content):
                result = shion_lib.get_event("Bank Interest",
                                             "https://hypixel-api.inventivetalent.org/api/skyblock/bank/interest/estimate")
                await message.channel.send(message.author.mention + result)
            else:
                pass

        if re.compile(r"(!seen )(.+)").match(message.content):
            await shion_lib.get_player_session(message)

        if re.compile(r"!news").match(message.content):
            if shion_lib.check_blacklist(message):
                await shion_lib.message_in_blacklist(message)
                return
            await shion_lib.get_sb_news(message)

        if re.compile(r"!patch|!jerry|!update").match(message.content):
            if shion_lib.check_blacklist(message):
                await shion_lib.message_in_blacklist(message)
                return
            await shion_lib.get_sb_patch(message)

        if re.compile(r"!sbhelp").match(message.content):
            if shion_lib.check_blacklist(message):
                await shion_lib.message_in_blacklist(message)
                return
            await shion_lib.sb_help(message)

        if re.compile(r"(!addblacklist )(.+)( )(.+)").match(message.content):  #This command is needed 2 args Discord users.id and reason.
            author_id = message.author.id  #(you shouldn't use blank in reason. For ex. "!addblacklist 00000000 spam_chat")
            if not author_id == owner_id:
                return
            await shion_lib.add_blacklist(message)
        
        global_notice = shion_lib.global_notice_from
        notice = shion_lib.global_notice_to
        if message.channel.id == global_notice:
            for channel in notice:
                notice_channel = client.get_channel(channel)
                if not notice_channel == None:
                    await notice_channel.send(message.content)
        
        #Change bot's code on during it run and use this command then bot will restart itself. Special Thanks: kawaiinekomimi
        if re.compile(r"!reload").match(message.content):
            #Basic version, will be improved in the future.
            author_id = message.author.id
            if not author_id == owner_id:
                return
            await message.channel.send(":white_check_mark: Reloaded!")
            os.execl(sys.executable, sys.executable, * sys.argv)


owner_id = shion_lib.owner_id
client = MyClient()
token = shion_lib.token
client.run(token)
