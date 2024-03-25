import random
from enum import Enum

import discord
from discord import Member, ApplicationContext, ui
from discord.utils import get

import utils
from discordroles import DiscordRoles

HOST = None
T = None
players = []
night = False
first_don = True


class Util:
    healedPlayer = None
    killedPlayer = None
    lastHealed = None

    last_shot = None
    shots_amount = 0

    mafia_list = []


class Type(Enum):
    # mafia, commissioner, doctor
    CLASSIC = (3, 1, 0)
    CITY = (3, 1, 1)


class Roles(Enum):
    MAFIA = "Мафия"
    COMMISSIONER = "Комиссар"
    DOCTOR = "Доктор"

    DON_MAFIA = "Дон мафии"

    CITIZEN = "Мирный житель"

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))


class MafiaPlayer:
    def __init__(self, member: Member, role: Roles):
        self.member = member
        self.role = role


class SelectMenu(ui.Select):
    def __init__(self):
        super().__init__(placeholder="???",
                         options=[
                             discord.SelectOption(
                                 label=p.member.nick,
                                 value=str(p.member.id)
                             ) for p in players])


class DoctorMenu(SelectMenu):
    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.values[0])
        player = utils.get_player_by_id(user_id)

        if Util.lastHealed == player:
            await interaction.message.delete()
            await interaction.user.send(f"Вы не можете вылечить одного игрока 2 раза подряд.")

            doctor = utils.get_player_by_role(Roles.DOCTOR)
            await doctor.member.send("Выберите игрока", view=PlayerView(DoctorMenu()))
            return

        Util.healedPlayer = player
        if Util.killedPlayer == Util.healedPlayer:
            Util.killedPlayer = None

        Util.lastHealed = player

        await interaction.message.delete()
        await interaction.user.send(f"Вы вылечили игрока <@{user_id}>")
        await HOST.send(f"<@{interaction.user.id}>: вылечил <@{user_id}>")


class CommissionerMenu(SelectMenu):
    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.values[0])
        player = utils.get_player_by_id(user_id)

        if player.role == Roles.MAFIA or player.role == Roles.DON_MAFIA:
            message = f"<@{user_id}> черный!"
        else:
            message = f"<@{user_id}> красный!"

        await interaction.message.delete()
        await interaction.user.send(message)
        await HOST.send(f"<@{interaction.user.id}>: " + message)


class DonMafiaShotMenu(SelectMenu):
    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.values[0])
        player = utils.get_player_by_id(user_id)

        Util.killedPlayer = player

        if Util.killedPlayer == Util.healedPlayer:
            Util.killedPlayer = None

        await interaction.message.delete()
        await interaction.user.send(f"Вы выстрелили в игрока <@{user_id}>")
        await HOST.send(f"<@{interaction.user.id}>: выстрелил в <@{user_id}>")

        if first_don:
            don_mafia = utils.get_player_by_role(Roles.DON_MAFIA)
            await don_mafia.member.send("Выберите игрока", view=PlayerView(DonMafiaCheckMenu()))


class DonMafiaCheckMenu(SelectMenu):
    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.values[0])
        player = utils.get_player_by_id(user_id)

        if player.role == Roles.COMMISSIONER:
            message = f"<@{user_id}> комиссар!"
        else:
            message = f"<@{user_id}> не комиссар!"

        await interaction.message.delete()
        await interaction.user.send(message)
        await HOST.send(f"<@{interaction.user.id}>: " + message)


class ClassicMafiaShotMenu(SelectMenu):
    async def callback(self, interaction: discord.Interaction):
        user_id = int(self.values[0])
        player = utils.get_player_by_id(user_id)

        Util.shots_amount += 1
        if Util.last_shot is None:
            Util.last_shot = player
        else:
            if Util.last_shot != player:
                Util.killedPlayer = None
                await HOST.send("несострел")
            elif Util.shots_amount == len(Util.mafia_list):
                Util.killedPlayer = Util.last_shot

        await interaction.message.delete()
        await interaction.user.send(f"Вы выстрелили в игрока <@{user_id}>")
        await HOST.send(f"<@{interaction.user.id}>: выстрелил в <@{user_id}>")

        don = utils.get_player_by_role(Roles.DON_MAFIA)
        if interaction.user.id == don.member.id:
            don_mafia = utils.get_player_by_role(Roles.DON_MAFIA)
            await don_mafia.member.send("Выберите игрока для проверки на комиссара", view=PlayerView(DonMafiaCheckMenu()))


class PlayerView(ui.View):
    def __init__(self, select):
        super().__init__(select)


async def start(ctx: ApplicationContext, members: list[Member], host: Member, t: Type):
    global HOST
    HOST = host

    global T
    T = t

    global first_don
    first_don = True

    await host.send("Поехали!")

    possible_roles = {
        Roles.MAFIA: t.value[0],
        Roles.COMMISSIONER: t.value[1],
        Roles.DOCTOR: t.value[2]
    }

    def get_role(role):
        return get(ctx.guild.roles, name=role.value)

    global players
    players = []
    nums = [i for i in range(len(members))]

    random.shuffle(members)

    for m in members:
        await m.add_roles(get_role(DiscordRoles.PLAYER))

        num = nums[random.randrange(len(nums))]
        nums.remove(num)
        await m.edit(nick=f"[{num + 1}] {m.name}")

        player_role = Roles.CITIZEN
        for r in possible_roles:
            if possible_roles[r] > 0:
                player_role = r
                possible_roles[r] -= 1

                break

        mafiaPlayer = MafiaPlayer(m, player_role)
        if player_role == Roles.MAFIA:
            Util.mafia_list.append(mafiaPlayer)

        players.append(mafiaPlayer)

        await host.send(f"Игрок <@{m.id}>: **{player_role.value}.**")

        try:
            await m.send(f"Роль: **{player_role.value}.**")
        except Exception:
            pass


def end():
    global HOST
    HOST = None

    global T
    T = None

    global players
    players = []

    global night
    night = False

    global first_don
    first_don = False

    Util.killedPlayer = None
    Util.healedPlayer = None
    Util.lastHealed = None
    Util.last_shot = None
    Util.shots_amount = 0
    Util.mafia_list = []


async def start_night():
    Util.sent_check_message = False
    Util.last_shot = None
    Util.killedPlayer = None
    Util.healedPlayer = None

    await HOST.send("Ночь :full_moon:")

    doctor = utils.get_player_by_role(Roles.DOCTOR)
    if utils.get_player_by_role(Roles.DOCTOR) is not None:
        await doctor.member.send("Выберите игрока", view=PlayerView(DoctorMenu()))

    commissioner = utils.get_player_by_role(Roles.COMMISSIONER)
    if utils.get_player_by_role(Roles.COMMISSIONER) is not None:
        await commissioner.member.send("Выберите игрока", view=PlayerView(CommissionerMenu()))

    if T == Type.CLASSIC:
        for mafia in Util.mafia_list:
            await mafia.member.send("Выберите игрока", view=PlayerView(ClassicMafiaShotMenu()))
    else:
        don_mafia = utils.get_player_by_role(Roles.DON_MAFIA)
        await don_mafia.member.send("Выберите игрока", view=PlayerView(DonMafiaShotMenu()))


async def remove_player(ctx: ApplicationContext, player: MafiaPlayer):
    await player.member.remove_roles(utils.get_role(ctx, DiscordRoles.PLAYER))

    if player.role == Roles.DON_MAFIA or player.role == Roles.MAFIA:
        Util.mafia_list.remove(player)

    if player.role == Roles.DON_MAFIA:
        mafia = utils.get_player_by_role(Roles.MAFIA)

        if mafia is not None:
            mafia.role = Roles.DON_MAFIA

            global first_don
            first_don = False

    mafia = len(utils.get_players_by_role(Roles.MAFIA))
    mafia += len(utils.get_players_by_role(Roles.DON_MAFIA))
    citizens = len(players) - mafia

    if mafia >= citizens:
        await ctx.send("Победа мафии")
        end()
    elif mafia == 0:
        await ctx.send("Победа мирных игроков")
        end()
