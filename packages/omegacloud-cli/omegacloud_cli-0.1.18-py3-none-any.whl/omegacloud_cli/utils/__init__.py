from typing import List


def split_commands(commands: str) -> List[str]:
    """
    Split commands by ; or &
    """
    cmds = []
    parts = commands.split(";")
    for part in parts:
        sub_parts = part.split("&")
        cmds.extend(sub_part.strip() for sub_part in sub_parts)

    return cmds
