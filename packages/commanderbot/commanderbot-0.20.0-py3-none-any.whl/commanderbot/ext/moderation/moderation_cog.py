from typing import Optional

from discord import Embed, Interaction, Member, Permissions
from discord.app_commands import (
    Choice,
    ContextMenu,
    allowed_contexts,
    allowed_installs,
    choices,
    command,
    default_permissions,
    describe,
)
from discord.app_commands.checks import bot_has_permissions
from discord.ext.commands import Bot, Cog
from discord.interactions import Interaction

from commanderbot.ext.moderation.moderation_exceptions import (
    CannotBanBotOrSelf,
    CannotBanElevatedUsers,
    CannotKickBotOrSelf,
    CannotKickElevatedUsers,
)

KICK_EMOJI: str = "👢"
KICK_COMPROMISED_EMOJI: str = "🤖"
BAN_EMOJI: str = "🔨"
UNBAN_EMOJI: str = "😇"
MESSAGE_SENT_EMOJI: str = "✉️"
ERROR_EMOJI: str = "🔥"


class ModerationCog(Cog, name="commanderbot.ext.moderation"):
    def __init__(self, bot: Bot):
        self.bot: Bot = bot

        self.ctx_menu_kick_compromised_user = ContextMenu(
            name="Kick compromised user",
            callback=self.cmd_kick_compromised_user,
        )

    async def cog_load(self):
        self.bot.tree.add_command(
            self.ctx_menu_kick_compromised_user,
        )

    async def cog_unload(self):
        self.bot.tree.remove_command(
            self.ctx_menu_kick_compromised_user.name,
            type=self.ctx_menu_kick_compromised_user.type,
        )

    def _user_is_bot_or_interaction_user(
        self, user: Member, interaction: Interaction
    ) -> bool:
        return user == self.bot.user or user == interaction.user

    def _is_elevated(self, user: Member) -> bool:
        return bool(user.guild_permissions & Permissions.elevated())

    # @@ COMMANDS

    # @@ kick
    @command(name="kick", description="Kick a user from this server")
    @describe(
        user="The user to kick",
        reason="The reason for the kick (This will also be sent as a DM to the user)",
    )
    @allowed_installs(guilds=True)
    @allowed_contexts(guilds=True)
    @default_permissions(kick_members=True)
    @bot_has_permissions(kick_members=True)
    async def cmd_kick(
        self, interaction: Interaction, user: Member, reason: Optional[str]
    ):
        # Make sure we aren't trying to kick the bot or the user running the command
        if self._user_is_bot_or_interaction_user(user, interaction):
            raise CannotKickBotOrSelf

        # Make sure we aren't trying to kick users with elevated permissions
        if self._is_elevated(user):
            raise CannotKickElevatedUsers

        # Create the kick embed that's sent to the channel
        channel_kick_embed = Embed(
            description=f"### {KICK_EMOJI} Kicked {user.mention}", color=0x00ACED
        )
        channel_kick_embed.add_field(
            name="Reason", value=reason if reason else "No reason given"
        )

        # Send the kick embed to the channel
        await interaction.response.send_message(embed=channel_kick_embed)
        response = await interaction.original_response()

        # Attempt to DM the user if a reason was included
        # We do this before kicking in case this is the only mutual server
        if reason:
            try:
                guild_name: str = interaction.guild.name  # type: ignore
                dm_kick_embed = Embed(
                    description=f"### {KICK_EMOJI} You were kicked from {guild_name}",
                    color=0x00ACED,
                )
                dm_kick_embed.add_field(name="Reason", value=reason)

                await user.send(embed=dm_kick_embed)
                await response.add_reaction(MESSAGE_SENT_EMOJI)
            except:
                pass

        # Actually kick the user
        try:
            await user.kick(reason=reason if reason else "No reason given")
            await response.add_reaction(KICK_EMOJI)
        except:
            await response.add_reaction(ERROR_EMOJI)

    # @@ ban
    @command(name="ban", description="Ban a user from this server")
    @describe(
        user="The user to ban",
        reason="The reason for the ban (This will also be sent as a DM to the user)",
        delete_message_history="The amount of message history to delete",
    )
    @choices(
        delete_message_history=[
            Choice(name="Don't delete any", value=0),
            Choice(name="Previous hour", value=3600),
            Choice(name="Previous 6 hours", value=21600),
            Choice(name="Previous 12 hours", value=43200),
            Choice(name="Previous 24 hours", value=86400),
            Choice(name="Previous 3 days", value=259200),
            Choice(name="Previous 7 days", value=604800),
        ]
    )
    @allowed_installs(guilds=True)
    @allowed_contexts(guilds=True)
    @default_permissions(ban_members=True)
    @bot_has_permissions(ban_members=True)
    async def cmd_ban(
        self,
        interaction: Interaction,
        user: Member,
        reason: Optional[str],
        delete_message_history: Optional[int],
    ):
        # Make sure we aren't trying to ban the bot or the user running the command
        if self._user_is_bot_or_interaction_user(user, interaction):
            raise CannotBanBotOrSelf

        # Make sure we aren't trying to ban users with elevated permissions
        if self._is_elevated(user):
            raise CannotBanElevatedUsers

        # Create the ban embed that's sent to the channel
        channel_ban_embed = Embed(
            description=f"### {BAN_EMOJI} Banned {user.mention}", color=0x00ACED
        )
        channel_ban_embed.add_field(
            name="Reason", value=reason if reason else "No reason given"
        )

        # Send the ban embed to the channel
        await interaction.response.send_message(embed=channel_ban_embed)
        response = await interaction.original_response()

        # Attempt to DM the user if a reason was included
        # We do this before banning in case this is the only mutual server
        if reason:
            try:
                guild_name: str = interaction.guild.name  # type: ignore
                dm_ban_embed = Embed(
                    description=f"### {BAN_EMOJI} You were banned from {guild_name}",
                    color=0x00ACED,
                )
                dm_ban_embed.add_field(name="Reason", value=reason)

                await user.send(embed=dm_ban_embed)
                await response.add_reaction(MESSAGE_SENT_EMOJI)
            except:
                pass

        # Actually ban the user
        try:
            await user.ban(
                delete_message_seconds=delete_message_history or 0,
                reason=reason if reason else "No reason given",
            )
            await response.add_reaction(BAN_EMOJI)
        except:
            await response.add_reaction(ERROR_EMOJI)

    # @@ CONTEXT MENU COMMANDS

    # @@ kick compromised user
    @allowed_installs(guilds=True)
    @allowed_contexts(guilds=True)
    @default_permissions(kick_members=True, ban_members=True)
    @bot_has_permissions(kick_members=True, ban_members=True)
    async def cmd_kick_compromised_user(self, interaction: Interaction, user: Member):
        # Make sure we aren't trying to kick the bot or the user running the command
        if self._user_is_bot_or_interaction_user(user, interaction):
            raise CannotKickBotOrSelf

        # Make sure we aren't trying to kick users with elevated permissions
        if self._is_elevated(user):
            raise CannotKickElevatedUsers

        # Create the kick embed that's sent to the channel
        reason: str = (
            f"Your account is compromised and sending scam messages. Feel free to rejoin once you've changed your password. For more information about scams and how to better protect your account, check out this article on the Discord support site: <https://support.discord.com/hc/en-us/articles/24160905919511-My-Discord-Account-was-Hacked-or-Compromised>."
        )
        channel_kick_embed = Embed(
            description=f"### {KICK_COMPROMISED_EMOJI} Kicked {user.mention}", color=0x00ACED
        )
        channel_kick_embed.add_field(name="Reason", value=reason)

        # Send the kick embed to the channel
        await interaction.response.send_message(
            embed=channel_kick_embed, ephemeral=True
        )
        response = await interaction.original_response()

        # Attempt to DM the user
        try:
            guild_name: str = interaction.guild.name  # type: ignore
            dm_kick_embed = Embed(
                description=f"### {KICK_COMPROMISED_EMOJI} You were kicked from {guild_name}",
                color=0x00ACED,
            )
            dm_kick_embed.add_field(name="Reason", value=reason)

            await user.send(embed=dm_kick_embed)
            await response.add_reaction(MESSAGE_SENT_EMOJI)
        except:
            pass

        # Actually "kick" the user
        try:
            #await user.ban(delete_message_seconds=7200, reason=reason)
            await response.add_reaction(BAN_EMOJI)
            #await user.unban(reason="Unbanned compromised account")
            await response.add_reaction(UNBAN_EMOJI)
        except:
            await response.add_reaction(ERROR_EMOJI)
