import logging

from discord.ext import commands, tasks

NAME = "RootPythiaCommands"

class RootPythiaCommands(commands.Cog, name=NAME):
    """Define the commands that the bot will respond to, prefixed with the `command_prefix` defined at the bot init"""

    def __init__(self, bot, dbmanager):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.dbmanager = dbmanager

        self.check_new_solves.start()

    async def log_command_call(self, ctx):
        # Maybe we should use the on_command event
        # https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=cog#discord.discord.ext.commands.on_command
        # the logging would be implicit, no need of a redundant @commands.before_invoke(...) on each command
        # But right now I prefer to stick with this explicit solution
        self.logger.info("'%s' command triggered by '%s'", ctx.command, ctx.author)

    @commands.before_invoke(log_command_call)
    @commands.command(name='hey')
    async def hey(self, ctx):
        await ctx.message.channel.send("hey command works!!\nJust happy to be alive")

    @commands.before_invoke(log_command_call)
    @commands.command(name='ping')
    async def ping(self, ctx):
        await ctx.message.channel.send("weird habit... but I guess: pong?...")

    # TODO: add a add_users command that would accept a list of ids
    @commands.before_invoke(log_command_call)
    @commands.command(name='adduser')
    async def adduser(self, ctx, idx: int):
        user = await self.dbmanager.add_user(idx)

        if user is None:
            await ctx.message.channel.send(f"UserID {idx} already exists in database")
            return

        self.logger.info("Add user '%s'", user)
        await ctx.message.channel.send(f"{user} added!\nPoints: {user.score}")

    @commands.before_invoke(log_command_call)
    @commands.command(name='getuser')
    async def getuser(self, ctx, idx: int):
        user = self.dbmanager.get_user(idx)

        if user is None:
            self.logger.debug("DB Manager returned 'None' for UserID '%s'", idx)
            await ctx.message.channel.send(f"User id '{idx}' isn't in the database, you must add it first")
            return

        self.logger.debug("Get user '%s' for id=%d", repr(user), idx)
        await ctx.message.channel.send(f"{user} \nPoints: {user.score}\nRank: {user.rank}\nLast Solves: <TO BE COMPLETED>")

    # TODO: make the resfresh delay configurable
    @tasks.loop(seconds=10)
    async def check_new_solves(self):
        self.logger.info("Checking for new solves...")

        users = self.dbmanager.get_users()
        for user in users:
            async for solve in self.dbmanager.fetch_user_new_solves(user.idx):
                self.logger.info("%s solved '%s'", user, solve)
                await self.bot.channel.send(solve)
