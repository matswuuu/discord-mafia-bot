from discord import ApplicationContext

import game
import utils
from config import MEMBERS_START
from discordroles import DiscordRoles


class Start:
    async def start(self: ApplicationContext, type: game.Type):
        if self.user.voice is None:
            await self.respond("Вы должны находиться в голосовом канале", ephemeral=True)
            return

        if await utils.check_permission(self): return

        members = []
        for m in self.user.voice.channel.members:
            if not (utils.get_role(self, DiscordRoles.HOST) in m.roles
                    or utils.get_role(self, DiscordRoles.OBSERVER) in m.roles):
                members.append(m)

        if len(members) < MEMBERS_START:
            await self.respond("Недостаточно игроков", ephemeral=True)
        elif game.HOST is not None:
            await self.respond("Игра уже идет", ephemeral=True)
        else:
            await self.respond("Поехали!", ephemeral=True)
            await game.start(self, members, self.user, type)
