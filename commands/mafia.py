from discord import ApplicationContext, Member

import game
import utils


class Mafia:
    async def set_don(self: ApplicationContext, member: Member):
        if await utils.check_permission(self): return
        if await utils.check_game(self): return

        if utils.get_player_by_role(game.Roles.DON_MAFIA) is not None:
            await self.respond("Дон мафии уже назначен", ephemeral=True)
            return

        player = utils.get_player_by_member(member)

        if player is None or player.role != game.Roles.MAFIA:
            await self.respond("Доном мафии можно назначить только члена мафии", ephemeral=True)
            return

        player.role = game.Roles.DON_MAFIA
        await self.respond("Успешно", ephemeral=True)
