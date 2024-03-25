from discord import ApplicationContext

import game
import utils
from discordroles import DiscordRoles


class Night:
    async def night(self: ApplicationContext):
        if await utils.check_permission(self): return
        if await utils.check_game(self): return

        if game.night:
            await self.respond("Ночь уже наступила!", ephemeral=True)
            return

        don = utils.get_player_by_role(game.Roles.DON_MAFIA)

        if don is None:
            await self.respond("Нет дона мафии!", ephemeral=True)
            return

        for m in self.user.voice.channel.members:
            if not (utils.get_role(self, DiscordRoles.HOST) in m.roles
                    or utils.get_role(self, DiscordRoles.OBSERVER) in m.roles):
                await m.edit(mute=True)

        await self.send("Наступила ночь :full_moon:")

        await game.start_night()