from enum import Enum


class DiscordRoles(Enum):
    PLAYER = "Игрок"
    OBSERVER = "Наблюдатель"
    HOST = "Ведущий"

    @classmethod
    def values(cls):
        return list(map(lambda c: c.value, cls))
