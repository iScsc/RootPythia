import logging

import discord
from discord.ext import commands, tasks

from pngmaker import NewValidatedChallenge

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

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send("Command failed, please check logs for more details")

        # this dirty try + raise is mandatory because the exception stored in error has been captured
        # by discord.py so sys.exc_info() is empty, we re aise it on purpose to log properly
        try:
            raise error
        except:
            self.logger.exception("'%s' command failed", ctx.command)

    @commands.before_invoke(log_command_call)
    @commands.command(name="hey")
    async def hey(self, ctx):
        await ctx.message.channel.send("hey command works!!\nJust happy to be alive")

    @commands.before_invoke(log_command_call)
    @commands.command(name="ping")
    async def ping(self, ctx):
        await ctx.message.channel.send("weird habit... but I guess: pong?...")

    # TODO: add a add_users command that would accept a list of ids
    @commands.before_invoke(log_command_call)
    @commands.command(name="adduser")
    async def adduser(self, ctx, idx: int):
        user = await self.dbmanager.add_user(idx)

        if user is None:
            await ctx.message.channel.send(f"UserID {idx} already exists in database")
            return

        self.logger.info("Add user '%s'", user)
        await ctx.message.channel.send(f"{user} added!\nPoints: {user.score}")

    @commands.before_invoke(log_command_call)
    @commands.command(name="getuser")
    async def getuser(self, ctx, idx: int):
        user = self.dbmanager.get_user(idx)

        if user is None:
            self.logger.debug("DB Manager returned 'None' for UserID '%s'", idx)
            await ctx.message.channel.send(
                f"User id '{idx}' isn't in the database, you must add it first"
            )
            return

        self.logger.debug("Get user '%s' for id=%d", repr(user), idx)
        await ctx.message.channel.send(
            f"{user} \nPoints: {user.score}\nRank: {user.rank}\nLast Solves: <TO BE COMPLETED>"
        )

    # TODO: make the resfresh delay configurable
    @tasks.loop(seconds=10)
    async def check_new_solves(self):
        self.logger.info("Checking for new solves...")

        users = self.dbmanager.get_users()
        for user in users:
            async for solved_challenge in self.dbmanager.fetch_user_new_solves(user.idx):
                self.logger.info("%s solved '%s'", user, solved_challenge)

                # this context manager handles the file image creation and deletion
                # TODO: change this hardcoded order=2 and create an is_first_blood or solved_rank method in DB Manager
                with NewValidatedChallenge(user, solved_challenge, 2) as solve:
                    await self.bot.channel.send(file=discord.File(solve))

    @check_new_solves.error
    async def loop_error_handler(self, exc):
        await self.bot.channel.send(
            "check_new_solves loop failed, please check logs for more details"
        )
        # logging of the traceback is already handled by the asyncio package
        self.logger.error("check_new_solves loop failed")

        self.check_new_solves.restart()
