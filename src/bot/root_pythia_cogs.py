import logging

from os import getenv

import discord
from discord.ext import commands, tasks

from pngmaker import NewValidatedChallenge

REFRESH_DELAY = int(getenv("REFRESH_DELAY") or "10")  # in seconds !

NAME = "RootPythiaCommands"


class RootPythiaCommands(commands.Cog, name=NAME):
    """
    Define the commands that the bot will respond to, prefixed with '!' \
    defined at the bot init
    """

    def __init__(self, bot, dbmanager):
        self.bot = bot
        self.logger = logging.getLogger(__name__)
        self.dbmanager = dbmanager

        # pylint: disable-next=no-member
        self.check_new_solves.start()

    async def log_command_call(self, ctx):
        # Maybe we should use the on_command event
        # https://discordpy.readthedocs.io/en/stable/ext/commands/api.html?highlight=cog#discord.discord.ext.commands.on_command
        # the logging would be implicit, no need of a redundant @commands.before_invoke(...) on
        # each command. But right now I prefer to stick with this explicit solution
        self.logger.info("'%s' command triggered by '%s'", ctx.command, ctx.author)

    @commands.before_invoke(log_command_call)
    @commands.command(name="status")
    async def status(self, ctx):
        """
            Give info on bot status
        """
        rate_limiter = self.dbmanager.api_manager.rate_limiter
        check = ":white_check_mark:"
        cross = ":x:"
        rl_alive = cross if rate_limiter.task.done() else check
        rl_paused = check if rate_limiter.is_paused() else cross
        rl_idle = check if rate_limiter.is_idle() else cross
        # pylint: disable-next=no-member
        bot_loop_alive = check if self.check_new_solves.is_running() else cross
        await ctx.send(
            f"RootMe API's Rate Limiter status:\n"
            f"- alive: {rl_alive}\n"
            f" - paused: {rl_paused}\n"
            f" - idle: {rl_idle}\n"
            f"Bot's `check_new_solves` loop:\n"
            f"- alive: {bot_loop_alive}\n"
        )

    @commands.command(name="resume")
    async def resume(self, ctx):
        """
            The bot leaves its idle state
        """
        rate_limiter = self.dbmanager.api_manager.rate_limiter
        if not rate_limiter.is_idle():
            await ctx.message.channel.send("The Rate Limiter isn't idle, no need to resume.")
            return

        rate_limiter.exit_idle()
        await ctx.message.channel.send(
            "Resumed successfully from idle state, requests can be sent again."
        )

    async def base_add_one_user(self, ctx, user_id: int):
        # TODO: except 404 error -> if the request in add_user fails
        # try:
        #     user = await self.dbmanager.add_user(idx)
        # except 404Error as 404_err: # Error coming from add_user() method
        #     pass
        user = await self.dbmanager.add_user(user_id)

        if user is None:
            await ctx.message.channel.send(f"UserID {user_id} already exists in database")
            self.logger.warning("UserID '%s' already exists in database", user_id)
            return

        self.logger.info("Add user '%s'", user)
        await ctx.message.channel.send(f"{user} added!\nPoints: {user.score}")

    @commands.before_invoke(log_command_call)
    @commands.command(name="addusers")
    async def addusers(self, ctx, *user_ids):
        """
            Add several rootme users with [user_ids...] to the tracked users 
            (each id is separated by a whitespace when using the command)
        """
        self.logger.info("command `addusers` received '%s' arguments: '%s'", len(user_ids), user_ids)
        for user_id in user_ids:
            try:
                user_id = int(user_id)
            except ValueError as value_err:  # Error coming from the int() cast
                self.logger.error("command `addusers` received: '%s'", value_err)
                await ctx.message.channel.send(
                    f"invalid argument received: `{user_id}`; a UserId is expected, ignoring it..."
                )
                continue

            # TODO: except 404 error -> if the request in add_user fails, we
            # should continue here (ex: multiple users but only one can be wrong)
            await self.base_add_one_user(ctx, user_id)

    @commands.before_invoke(log_command_call)
    @commands.command(name="adduser")
    async def adduser(self, ctx, user_id: int):
        """
            Add rootme user with <user_id> to the tracked users
        """
        await self.base_add_one_user(ctx, user_id)

    @commands.before_invoke(log_command_call)
    @commands.command(name="getuser")
    async def getuser(self, ctx, user_id: int):
        """
            Get rootme user info with <user_id>
        """
        user = self.dbmanager.get_user(user_id)

        if user is None:
            self.logger.debug("DB Manager returned 'None' for UserID '%s'", user_id)
            await ctx.message.channel.send(
                f"User id '{user_id}' isn't in the database, you must add it first"
            )
            return

        self.logger.debug("Get user '%s' for id=%d", repr(user), user_id)
        await ctx.message.channel.send(
            f"{user} \nPoints: {user.score}\nRank: {user.rank}\nLast Solves: <TO BE COMPLETED>"
        )

    @tasks.loop(seconds=REFRESH_DELAY)
    async def check_new_solves(self):
        self.logger.info("Checking for new solves...")

        users = self.dbmanager.get_users()
        for user in users:
            async for solved_challenge in self.dbmanager.fetch_user_new_solves(user.idx):
                self.logger.info("%s solved '%s'", user, solved_challenge)

                # this context manager handles the file image creation and deletion
                # TODO: change this hardcoded order=2 and create an is_first_blood or solved_rank
                # method in DB Manager
                with NewValidatedChallenge(user, solved_challenge, 2) as solve:
                    await self.bot.channel.send(file=discord.File(solve))

    async def verbose_if_idle(self, channel):
        rate_limiter = self.dbmanager.api_manager.rate_limiter
        if rate_limiter.is_idle():
            await channel.send(
                f"RateLimiter has entered idle state you should check logs first "
                f"but you can resume it with `{self.bot.command_prefix}resume`"
            )

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        await ctx.send("Command failed, please check logs for more details")
        await self.verbose_if_idle(ctx)

        # this dirty try + raise is mandatory because the exception stored in error has been
        # captured by discord.py so sys.exc_info() is empty, we re aise it on purpose to log
        # properly
        try:
            raise error
        except Exception:
            self.logger.exception("'%s' command failed", ctx.command)

    @check_new_solves.error
    async def loop_error_handler(self, exc):
        await self.bot.channel.send(
            "check_new_solves loop failed, please check logs for more details"
        )
        await self.verbose_if_idle(self.bot.channel)

        # logging of the traceback is already handled by the asyncio package
        self.logger.error("check_new_solves loop failed")

        # pylint: disable-next=no-member
        self.check_new_solves.restart()
