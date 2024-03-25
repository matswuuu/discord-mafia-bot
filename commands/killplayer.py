from discord import ApplicationContext, Member

import game
import utils
from discordroles import DiscordRoles


class KillPlayer:
    async def kill_player(self: ApplicationContext, member: Member):
        if await utils.check_permission(self): return
        if await utils.check_game(self): return

        player = utils.get_player_by_member(member)
        await game.remove_player(self, player)

        await self.send(f"Игрок <@{member.id}> умер.")

