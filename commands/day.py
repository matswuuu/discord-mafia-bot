from discord import ApplicationContext

import game
import utils
from discordroles import DiscordRoles


class Day:
    async def day(self: ApplicationContext):
        if await utils.check_permission(self): return
        if await utils.check_game(self): return

        if game.Util.killedPlayer is None:
            message = "Никто не умер этой ночью!"
        else:
            await game.remove_player(self, game.Util.killedPlayer)
            message = f"Этой ночью умер <@{game.Util.killedPlayer.member.id}>!"

        game.night = False

        for m in self.user.voice.channel.members:
            if not (utils.get_role(self, DiscordRoles.HOST) in m.roles
                    or utils.get_role(self, DiscordRoles.OBSERVER) in m.roles):
                await m.edit(mute=False)

        await self.send("Наступило утро :sunny:\n" + message)
