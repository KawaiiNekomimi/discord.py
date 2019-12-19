import discord
from discord.ext import commands
import datetime
import traceback
import os
import json

path = os.path.dirname(os.path.abspath(__file__))
prefix = "!"
bot = commands.AutoShardedBot(command_prefix=[prefix], description='Shion', pm_help=None)
wrap = "```py\n{}\n```"
modules = ["cogs." + x.replace(".py", "") for x in os.listdir(path + "/cogs") if ".py" in x]
colour_code = 0x00ff00 # Default Embed color. Color codes are 0x[color hex]

def config_load():
    with open(path + '/data/config.json', 'r', encoding='utf-8-sig') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)

config = config_load()

if str(config['token']) == "TOKEN":
    print("It looks like this is your first time running the bot. Before continuing, some information is needed. The bot will automatically start up after this setup is complete.\n")
    token = input("What is your bot token? (Found in the Discord Developer Portal under 'My Applications')\n>")
    api_num = input("How many Hypixel API keys would you like to use? (Only type a number )")
    api_key = input("What is your Hypixel API Key? You can find this in-game by typing '/api' or '/api new'.\n>")
    owner_id = input("What is your Discord ID?\n>")
    config['token'] = f"{token}"
    config['api_key'] = f"{api_key}"
    config['owner_id'] = f"{owner_id}"
    if config['notify_channel'] == "None":
        print("/!\-------------------------------/!\")
        print("If you want to have a notification channel, please open shion.py (in the cogs folder) and add a notification id on line 36.")
        print("/!\-------------------------------/!\")
        config['notify_channel'] = f"Done"
    with open(path + '/data/config.json', 'w', encoding='utf-8-sig') as f:
        json.dump(config, f)

admin_ids = [int(config['owner_id'])]

@bot.event
async def on_ready():
    print(f"{bot.user.name}#{str(bot.user.discriminator)}")
    print(f"Connected with {len(bot.guilds)} guilds")
    print(f"Watching over {len(set(bot.get_all_members()))} users")
    print(f"Shard Count: {bot.shard_count}")
    setattr(bot, "uptime", datetime.datetime.utcnow().timestamp())
    for extension in modules:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print(f'Couldn\'t load {extension}\n{type(e).name}: {e}')

@bot.event
async def on_message_edit(before, after):
    if after.author.bot:
        return
    elif before.content == after.content:
        return
    else:
        await bot.process_commands(after)

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error, *args, **kwargs):
    channel = ctx.channel
    if isinstance(error, commands.CheckFailure):
        await ctx.send("You are missing permisisons to use this command.")
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.send("Commands are not available in direct messages!")
    elif isinstance(error, commands.DisabledCommand):
        await ctx.send(f"**{ctx.command}** is currently disabled!")
    elif isinstance(error, commands.CommandOnCooldown):
        m, s = divmod(error.retry_after, 60)
        h, m = divmod(m, 60)
        if h == 0:
            time = "%d minutes %d seconds" % (m, s)
        elif h == 0 and m == 0:
            time = "%d seconds" % (s)
        else:
            time = "%d hours %d minutes %d seconds" % (h, m, s)
        return await channel.send("This command is on cooldown! Try again in {}".format(time))
    elif isinstance(error, commands.MissingRequiredArgument):
        msg = ""
        if not ctx.command.usage:
            for x in ctx.command.params:
                if x != "ctx":
                    if x != "self":
                        if "None" in str(ctx.command.params[x]):
                            msg += "[{}] ".format(x)
                        else:
                            msg += "<{}> ".format(x)
        else:
            msg += ctx.command.usage
        e=discord.Embed(title="Example", description="{}{} {}".format(ctx.prefix, ctx.command, msg), colour=colour_code)
        e.set_author(name="{}".format(ctx.command), icon_url=bot.user.avatar_url)
        e.set_footer(text="{}".format(ctx.command.help))
        await channel.send(embed=e)
    elif isinstance(error, commands.CommandNotFound):
        pass
    elif isinstance(error, commands.BotMissingPermissions):
        if bin(error.missing.value).count("1") == 1:  # Only one perm mis
                plural = ""
        else:
            plural = "s"
        await ctx.send(f"I require the {error.missing} permission{plural} to execute that command.")
    elif isinstance(error, commands.BadArgument):
        msg = ""
        if not ctx.command.usage:
            for x in ctx.command.params:
                if x != "ctx":
                    if x != "self":
                        if "None" in str(ctx.command.params[x]):
                            msg += "[{}] ".format(x)
                        else:
                            msg += "<{}> ".format(x)
        else:
            msg += ctx.command.usage
        e=discord.Embed(title="Example", description="{}{} {}".format(ctx.prefix, ctx.command, msg), colour=colour_code)
        e.set_author(name="{}".format(ctx.command), icon_url=bot.user.avatar_url)
        e.set_footer(text="{}".format(ctx.command.help))
        await channel.send(embed=e)
    elif isinstance(error, commands.CommandInvokeError):

        message = "Error in command '{}'. Please check your console.".format(
            ctx.command.qualified_name
        )
        exception_log = "Exception in command '{}'\n" "".format(ctx.command.qualified_name)
        exception_log += "".join(traceback.format_exception(type(error), error, error.__traceback__))
        bot._last_exception = exception_log
        #await ctx.send(f"{message}")
        print("".join(traceback.format_exception(type(error), error, error.__traceback__)))
        e=discord.Embed(description="Reason: {}".format(str(error)), colour=colour_code)
        e.set_author(name="Command Error!", icon_url=bot.user.avatar_url)
        await channel.send(embed=e)

bot.run(config['token'], reconnect=True)
