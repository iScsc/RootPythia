import logging

from discord.ext import commands

NAME = "RootPythiaCommands"
LOG_STR_LEN_LIMIT = 600
TRUNCATE = True

# FIXME: c'est degueu faut intégrer ca au formatter du root logger je pense
def truncate(data):
    if not TRUNCATE:
        return data
    str_data = str(data)
    if len(str_data) > LOG_STR_LEN_LIMIT:
        if len(str_data) > LOG_STR_LEN_LIMIT + 60:
            return str_data[:600] + " ...[TRUNCATED]... " + str_data[-40:]
    return str_data

class RootPythiaCommands(commands.Cog, name=NAME):
    """Define the commands that the bot will respond to, prefixed with the `command_prefix` defined at the bot init"""

    def __init__(self, bot, dbmanager):
        self.bot = bot
        self.logger = logging.getLogger(self.qualified_name)
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
    async def add_user(self, ctx, idx: int):
        user = await self.dbmanager.add_user(idx)

        if user is None:
            await ctx.message.channel.send(f"UserID {idx} already exists in database")
            return

        self.logger.debug("Add user: '%s'", repr(user))
        await ctx.message.channel.send(f"{user.username} {user.idx} added!\nPoints: {user.score}")

    @commands.command(name='getuser')
    async def get_user(self, ctx, idx: int):
        user = self.dbmanager.get_user(idx)
        self.logger.debug("Get user '%s' for id=%d", repr(user), idx)
        await ctx.message.channel.send(f"{user.username} {user.idx} \nPoints: {user.score}\nRank: {user.rank}\nLast Solves: <TO BE COMPLETED>")

    # TODO: add a loop for checking new solves, this calls the DB that calls the API with all the users