import math
import json
import os
import sys


def resource_path(relative_path: str):
    """Function to find the Path of the given file in Relative Path.

    Args:
        relative_path (str): The Relative Path of the file.

    Returns:
        str: The Actual Path of the file.
    """

    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


with open(resource_path("data/data.json")) as file:
    data = json.load(file)


def calculate(
        weapon: dict,
        material: dict,
        modifier: str,
        durability: int,
        buffs: tuple,
        conditions: tuple
):

    """The main calculator function.

    Returns:
        tuple: (Damage per hit, list: [Combo Damage hits])
    """

    bp = weapon["Base Attack Power"]
    add = material["Fuse Attack Power (Sword)"]

    attackup, boneUp, gloom = buffs
    sneak, wet, flurry, hp = conditions

    if weapon["Name"] == "Master Sword" and gloom:
        bp += 15

    if weapon["Name"] in data["Gerudo"]:
        add *= 2

    if weapon["Name"] in data["Zonai"] and material["Name"] in data["isZonai"]:
        bp += data["Zonai"][weapon["Name"]]

    if modifier.startswith("Attack Up"):
        mod = modifier.replace("Attack Up+ ", "")
        mod = mod.replace("Attack Up++ ", "")
        mod = int(mod)
    else:
        mod = 0

    if weapon["Type"] == "Large Sword":
        dmg = bp + math.floor((add + mod) / 0.95)
        length = 1
        fcombo = 4

    elif weapon["Type"] == "Spear":
        dmg = bp + math.ceil((add + mod) / 1.33)
        length = 4
        fcombo = 10

    else:
        dmg = bp + add + mod
        length = 3
        fcombo = 7

    dmg *= attackup

    dmg *= sneak*2 if weapon["Name"] in data["Sheikah"] else sneak
    dmg *= wet if weapon["Name"] in data["Zora"] else 1

    if weapon["Name"] in data["Bone"] or material["Name"] in data["Bone"]:
        dmg *= boneUp

    if weapon["Name"] in data["RG"] and 0 < durability < 4:
        dmg *= 2

    if weapon["Name"] in data["Royal"] and flurry:
        dmg *= 2

    if weapon["Name"] in data["Knight"] and hp:
        dmg *= 2

    dmg = int(dmg)

    if durability == 1:
        return 2*dmg, [2*dmg]

    elif sneak == 8:
        return dmg, [dmg]

    elif 0 < durability <= length + 1:
        return dmg, [dmg for i in range(durability - 1)] + [2*dmg]

    elif flurry:
        if 0 < durability <= fcombo:
            return dmg, [dmg for i in range(durability - 1)] + [2*dmg]
        return dmg, [dmg for i in range(fcombo)]

    return dmg, [dmg for i in range(length)] + [
        2*dmg if modifier == "Critical Hit" else dmg]
