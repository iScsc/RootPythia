import discord
from discord.ext.commands import HelpCommand


class RootPythiaHelpCommand(HelpCommand):
    """
    Implementation of HelpCommand

    HelpCommand.send_bot_help(mapping) that gets called with <prefix>help
    HelpCommand.send_command_help(command) that gets called with <prefix>help <command>
    HelpCommand.send_group_help(group) that gets called with <prefix>help <group>
    HelpCommand.send_cog_help(cog) that gets called with <prefix>help <cog>
    """

    def get_command_signature(self, command):
        return f"{command.qualified_name} {command.signature}"

    async def send_bot_help(self, mapping):
        # color attribute sets color of the border on the left
        embed = discord.Embed(title="Help", color=discord.Color.blurple())

        for cog, cmds in mapping.items():
            # Commands a user can't use are filtered
            filtered_cmds = await self.filter_commands(cmds, sort=True)
            cmd_signatures = [self.get_command_signature(cmd) for cmd in filtered_cmds]

            if cmd_signatures:
                cog_name = getattr(cog, "qualified_name", "No Category")
                embed.add_field(name=cog_name, value="\n".join(cmd_signatures), inline=False)

        await self.get_destination().send(embed=embed)

    async def send_command_help(self, command):
        embed = discord.Embed(
                title=self.get_command_signature(command),
                color=discord.Color.blurple())

        if command.help:
            embed.description = command.help
        if alias := command.aliases:
            embed.add_field(name="Aliases", value=", ".join(alias), inline=False)

        await self.get_destination().send(embed=embed)

    async def send_group_help(self, group):
        embed = discord.Embed(
                title=self.get_command_signature(group),
                description=group.help,
                color=discord.Color.blurple())

        if filtered_commands := await self.filter_commands(group.commands):
            for command in filtered_commands:
                embed.add_field(
                        name=self.get_command_signature(command),
                        value=command.help or "No Help Message Found... ")

        await self.get_destination().send(embed=embed)

    async def send_cog_help(self, cog):
        embed = discord.Embed(
                title=cog.qualified_name or "No Category",
                description=cog.description,
                color=discord.Color.blurple())

        if filtered_commands := await self.filter_commands(cog.get_commands()):
            for command in filtered_commands:
                embed.add_field(
                        name=self.get_command_signature(command),
                        value=command.help or "No Help Message Found... ",
                        inline=False)

        await self.get_destination().send(embed=embed)

    async def send_error_message(self, error):
        embed = discord.Embed(title="Error", description=error, color=discord.Color.red())
        channel = self.get_destination()

        await channel.send(embed=embed)
