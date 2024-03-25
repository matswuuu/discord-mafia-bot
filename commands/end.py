from discord import ApplicationContext

import game
import utils


class End:
    async def end(self: ApplicationContext):
        if await utils.check_permission(self): return
        if await utils.check_game(self): return

        game.end()

        await self.send("gg")

