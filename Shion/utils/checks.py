from discord.ext import commands

def is_owner_check(ctx):
    if ctx.author.id in [180325351392673794, 123468845749895170]:
        return True
    else:
        return False

def is_owner():
    return commands.check(is_owner_check)

def is_admin(user):
    for i in range(len(user.roles)):
        if user.roles[i].name in ["Bartender"]:
            return True
    return False

def is_mod(user):
    for i in range(len(user.roles)):
        if user.roles[i].name in ["Runner"]:
            return True
    return False

def is_helper(user):
    for i in range(len(user.roles)):
        if user.roles[i].name in ["Staff"]:
            return True
    return False
