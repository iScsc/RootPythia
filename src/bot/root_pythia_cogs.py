import logging

from discord.ext import commands

NAME = "RootPythiaCommands"

class RootPythiaCommands(commands.Cog, name=NAME):
    """Define the commands that the bot will respond to, prefixed with the `command_prefix` defined at the bot init"""

    def __init__(self, bot, dbmanager):
        self.bot = bot
        logger = logging.getLogger(self.qualified_name)
        self.dbmanager = dbmanager

    # FIXME: this decorator won't work...
    def log_command_call(cmd):
        async def log_it(self, ctx, *args, **kwargs):
            self.logger.info("'%s' command triggered by '%s'", ctx.command, ctx.author)
            await cmd(self, ctx, *args, **kwargs)
        return log_it

    @commands.command(name='hey')
    async def hey(self, ctx):
        await ctx.message.channel.send("hey command works!!\nJust happy to be alive")

    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.message.channel.send("weird habit... but I guess: pong?...")

    # TODO: add a add_users command that would accept a list of ids
    @commands.command(name='adduser')
    async def add_user(self, ctx, id: int):
        user = self.dbmanager.add_user(id)
        await ctx.message.channel.send(f"{user.name} {user.id} added!\nPoints: {user.points}\n<some stats>")

    # TODO: add a loop for checking new solves, this calls the DB that calls the API with all the users