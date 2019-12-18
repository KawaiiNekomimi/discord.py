import discord
from discord.ext import commands
import os
import json

path = os.path.dirname(os.path.abspath(__file__))

def config_load():
    path = os.path.dirname(os.path.abspath(__file__)) #needed to define again for Windows users
    path = path.strip("cogs")
    with open(path + 'data/config.json', 'r', encoding='utf-8-sig') as doc:
        #  Please make sure encoding is correct, especially after editing the config file
        return json.load(doc)

config = config_load()
path = os.path.dirname(os.path.abspath(__file__))
colour_code = 0x00ff00
admin_ids = [int(config['owner_id'])] 
wrap = "```py\n{}\n```"
modules = ["cogs." + x.replace(".py", "") for x in os.listdir(path) if ".py" in x]

class main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cogs(self, ctx):
        "Shows all the cogs."
        modules = [x.replace(".py", "") for x in os.listdir(path) if ".py" in x]
        loaded = [c.__module__.split(".")[-1] for c in self.bot.cogs.values()]
        unloaded = [c.split(".")[-1] for c in modules if c.split(".")[-1] not in loaded]
        total_modules = len(modules)
        embed=discord.Embed(colour=colour_code, title=f"Modules - {total_modules}")
        embed.add_field(name=f"Loaded Modules - {len(loaded)}", value=", ".join(loaded) if loaded != [] else "None", inline=False)
        embed.add_field(name=f"Unloaded Modules - {len(unloaded)}", value=", ".join(unloaded) if unloaded != [] else "None", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def load(self, ctx, *, module: str):
        """Load a bot module."""
        author = ctx.author
        modules = [x.replace(".py", "") for x in os.listdir(path) if ".py" in x]
        loaded_modules = [c.__module__.split(".")[-1] for c in self.bot.cogs.values()]
        if author.id in admin_ids:
            if module.lower() == "all":
                i = 0
                for m in modules:
                    if m not in loaded_modules:
                        try:
                            self.bot.load_extension("cogs."+m)
                        except:
                            i += 1
                            await ctx.send("Couldn't load **{}**.".format(module))
                if i == 0:
                    await ctx.send("Successfully loaded all the modules.")
                else:
                    await ctx.send("Successfully loaded **{}** modules".format(len(modules)-i))
                return
            m = "cogs." + module
            try:
                if module in modules:
                    if module in loaded_modules:
                        await ctx.send("Cog is already loaded!")
                        return
                    self.bot.load_extension(m)
                    await ctx.send(f"Successfully loaded **{module}**")
                else:
                    await ctx.send(f"Couldn't find the module named **{module}**")
            except Exception as e:
                e=discord.Embed(description="Error:" + wrap.format(type(e).name + ': ' + str(e)), colour=colour_code)
                await ctx.send(embed=e)

    @commands.command()
    async def unload(self, ctx, *, module: str):
        """unloads a part of the bot."""
        author = ctx.author
        loaded_modules = [c.__module__.split(".")[-1] for c in self.bot.cogs.values()]
        if author.id in admin_ids:
            modules = [x.replace(".py", "") for x in os.listdir(path) if ".py" in x]
            if author.id in admin_ids:
                if module.lower() == "all":
                    i = 0
                    for m in modules:
                        if m == "owner":
                            pass
                        else:
                            try:
                                self.bot.unload_extension("cogs."+m)
                            except:
                                i += 1
                                await ctx.send("Couldn't unload **{}**.\n*".format(module))
                    if i == 0:
                        await ctx.send("Successfully unloaded all the modules.")
                    else:
                        await ctx.send("Successfully unloaded **{}** modules".format(len(modules)-i))
                    return
            m = "cogs." + module
            try:
                if module in modules:
                    if module == "owner":
                        await ctx.send("Can't unload owner cog.")
                        return
                    if module not in loaded_modules:
                        await ctx.send("Cog is already unloaded!")
                        return
                    self.bot.unload_extension(m)
                    await ctx.send(f"Successfully unloaded **{module}**.")
                else:
                    await ctx.send(f"Couldn't find the module named **{module}**.")
            except Exception as e:
                e=discord.Embed(description="Error:" + wrap.format(type(e).name + ': ' + str(e)), colour=colour_code)
                await ctx.send(embed=e)

    @commands.command(hidden=True)
    async def reload(self, ctx, *, module: str):
        """Reloads a part of the bot."""
        author = ctx.author
        modules = [x.replace(".py", "") for x in os.listdir(path) if ".py" in x]
        loaded_modules = [c.__module__.split(".")[-1] for c in self.bot.cogs.values()]
        if author.id in admin_ids:
            if module.lower() == "all":
                i = 0
                for m in modules:
                    if m in loaded_modules:
                        try:
                            self.bot.unload_extension("cogs."+m)
                        except:
                            pass
                    try:
                        self.bot.load_extension("cogs."+m)
                    except:
                        i += 1
                        await ctx.send("Couldn't reload **{}**.".format(module))
                if i == 0:
                    await ctx.send("Successfully reloaded all the modules.")
                else:
                    await ctx.send("Successfully reloaded **{}** modules".format(len(modules)-i))
                return
            m = "cogs." + module
            try:
                if module in modules:
                    self.bot.unload_extension(m)
                    self.bot.load_extension(m)
                    await ctx.send(f"Successfully reloaded **{module}**.")
                else:
                    await ctx.send(f"Couldn't find a module named **{module}**.")
            except Exception as e:
                await ctx.send("Failed to load the cog, check logs!")
                print(f'Couldn\'t load {m}\n{type(e).name}: {e}')

    @commands.command(hidden=True)
    async def blacklist(self, ctx, target: discord.User, *, reason: str):
        if ctx.author.id not in admin_ids:
            return
        target = str(target.id)
        with open(path + "/blacklist/" + target + ".txt", "w") as bl:
            bl.write(reason)
        await ctx.send(ctx.author.mention + f"I've added the user to the blacklist. They will no longer be able to use commands.\n. UserID: {target} Reason: {reason}")

def setup(bot):
    n = main(bot)
    bot.add_cog(n)
