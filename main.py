import customtkinter
import json
from PIL import Image, ImageTk
from customtkinter import CTkImage
import requests
from io import BytesIO
import difflib
import dmgCalc
from widgets import CTkDropdown, Lables, Options, Checks, CTkToolTip
import tkinter
import threading
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


def set_icon():
    icon = ImageTk.PhotoImage(Image.open(resource_path("data/icon.png")))
    app.iconphoto(False, icon)


# customtkinter initializing
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")
customtkinter.deactivate_automatic_dpi_awareness()

# main window
app = customtkinter.CTk()
app.title("Weapon Damage Calculator")
app.geometry("800x600")
app.resizable(False, False)
app.after(200, set_icon)

# open the data files
with open(resource_path("data/weapons_data.json")) as file:
    data = json.load(file)

with open(resource_path("data/materials_data.json")) as mfile:
    materials = json.load(mfile)

with open(resource_path("data/armours_head.json")) as head:
    headpiece = json.load(head)

with open(resource_path("data/armours_body.json")) as body:
    bodypiece = json.load(body)

with open(resource_path("data/armours_leg.json")) as leg:
    legpiece = json.load(leg)

# weapon data
keys = list(data.keys())
keys_lower = [option.lower() for option in keys]
original_options = {option.lower(): option for option in keys}

# material data
mKeys = list(materials.keys())
mKeys.remove("No Results")
mKeys_lower = [option.lower() for option in mKeys]
mOriginal = {option.lower(): option for option in mKeys}

# globals
current = "Master Sword"
after_id = None
current_material = "Apple"
mAfter_id = None
tabButtons = []
calc_timer = None


def link_to_image(link, label: customtkinter.CTkLabel):

    """Update the icons of the selected items."""

    if link:
        response = requests.get(link)
        image = Image.open(BytesIO(response.content))
        photo = CTkImage(image, size=(80, 80))
    else:
        photo = None

    label.configure(image=photo)


def update_combobox_options(*args):

    """Function to get closest match in-case enter key is pressed
    instead of selecting from dropdown. (Weapons)"""

    global current

    search_term = combobox.get().lower()
    match = difflib.get_close_matches(search_term, keys_lower, n=1)

    if match:
        toSet = original_options[match[0]]
        combobox.update(toSet)
        current = toSet

    else:
        combobox.update(current)


def update_weapon(name):

    """Function to update all the fileds associated with weapon on select.
    Also call the calculator."""

    global current
    current = name

    # update weapon icon
    link = data[name]["Inventory Icon 1"]
    threading.Thread(target=link_to_image, args=(link, image_label)).start()

    # add the gloom checkbox only when weapon is master sword
    if name == "Master Sword":
        gloomChoice.place(x=160, y=115)
    else:
        gloomChoice.place_forget()

    # other configures
    if data[name]["Base Attack Power (UI)"]:
        bp = data[name]["Base Attack Power (UI)"]
    else:
        bp = data[name]["Base Attack Power"]

    bpLabel.configure(
        text=f"Shown Attack Power: {bp}"
    )
    truBALabel.configure(
        text=f"True Attack Power: {data[name]['Base Attack Power']}"
    )

    typeLabel.configure(
        text=f"Type: {data[name]['Type']}"
    )

    durEntry.delete(0, customtkinter.END)
    durEntry.insert(0, data[name]["Durability"])

    tooltipMsg = data[name]["Caption"]

    if data[name]["Property 1"]:
        tooltipMsg += "\n\n» " + data[name]["Property 1"]

    if data[name]["Property 2"]:
        tooltipMsg += "\n» " + data[name]["Property 2"]

    if data[name]["Property 3"]:
        tooltipMsg += "\n» " + data[name]["Property 3"]

    weapon_tooltip.configure(
        text=tooltipMsg
    )

    if not data[name]["Base Attack Up Lv1 Range"]:
        modifierChoice.configure(state="disabled")
    else:
        modifierChoice.configure(state="normal")

    # call the calc
    schedule_update()


def validate_durability(value):

    """Check the input of the durability entry to be only int.

    Returns:
        bool: True if valid else False
    """

    if value == "":
        return True

    try:
        int(value)
        return True
    except Exception:
        app.bell()
        return False


def schedule_update(event=None):

    """Only call the calculator once in a series of event."""

    global after_id

    if event:
        if isinstance(event, tkinter.Event):
            if ((event.char and event.char.isprintable() and event.state == 0)
               or event.keysym == 'BackSpace'):

                if after_id:
                    app.after_cancel(after_id)
                after_id = app.after(1000, calc)
                return

    if after_id:
        app.after_cancel(after_id)
    after_id = app.after(1000, calc)


validate_dur = app.register(validate_durability)


def update_mCombobox_options(*args):

    """Function to get closest match in-case enter key is pressed
    instead of selecting from dropdown. (Materials)"""

    global current_material

    search_term = mCombobox.get().lower()
    match = difflib.get_close_matches(search_term, mKeys_lower, n=1)

    if match:
        toSet = mOriginal[match[0]]
        mCombobox.update(toSet)
        current_material = toSet

    else:
        mCombobox.update(current_material)


def update_material(name):

    """Function to update all the fileds associated with materials on select.
    Also call the calculator"""

    global current_material
    current_material = name

    # update material icon
    link = materials[name]["Inventory Icon"]
    threading.Thread(target=link_to_image, args=(link, mImage_label)).start()

    # other configurations
    power.configure(
        text=f"Fuse Additional Power: {materials[name]['Fuse Attack Power (Sword)']}"       # noqa: E501
    )

    tooltipMsg = materials[name]["Caption"]
    if materials[name]["Element"]:
        tooltipMsg += "\n\n» Elemental Damage: " + materials[name]["Element"]

        if materials[name]["Destroyed on Hit"]:
            tooltipMsg += "\n» One time use"

    elif materials[name]["Destroyed on Hit"]:
        tooltipMsg += "\n\n» One time use"

    material_tooltip.configure(
        text=tooltipMsg
    )

    # call the calc
    schedule_update()


def calc(*event):

    """Get all the data from various field and call the calculator function."""

    attackbuff = {
        0: 1,
        1: 1.2,
        2: 1.3,
        3: 1.5
    }

    weapon = data[current]
    material = materials[current_material]
    modifier = modifierChoice.get()
    durability = int(durEntry.get())

    sneakBuff = 8 if sneak.value() else 1
    wetBuff = 2 if isWet.value() else 1
    isFlurry = flurry.value()
    isLow = hp.value()
    gloom = gloomChoice.value()

    if current == "Master Sword":
        if gloom:
            link_to_image(weapon["Inventory Icon 4"], image_label)
        else:
            link_to_image(weapon["Inventory Icon 1"], image_label)

    attackUpLevel, boneUp = update_armour()

    if attackup.get() == "CTkComboBox":
        attup = 0
    else:
        attup = int(attackup.get())

    attackUpLevel += attup

    attbuff = (attackbuff[attackUpLevel]
               if attackUpLevel in attackbuff and attackUpLevel < 4 else 1.5)

    buffs = (attbuff, boneUp, gloom)
    conditions = (sneakBuff, wetBuff, isFlurry, isLow)

    update_after_calc(dmgCalc.calculate(
        weapon,
        material,
        modifier,
        durability,
        buffs,
        conditions
    ))


def update_after_calc(data):

    """Update the damage outputs after calculation."""

    global tabButtons
    single, combo = data

    perHit.configure(text=f"Damage Per Hit: {single}")
    comboDmg.configure(text=f"Combo Damage: {sum(combo)}")

    for i in tabButtons:
        i.grid_forget()

    tabButtons = []

    if len(combo) < 4:
        width = 70
    elif len(combo) == 4:
        width = 60
    else:
        width = 50

    for i, attack in enumerate(combo):
        hit = customtkinter.CTkButton(
            comboTable,
            text=attack,
            width=width,
            font=("Garamond", 16),
            text_color=("gray14", "#FFFFFF"),
            fg_color="transparent",
            border_color="#FFFFFF",
            border_width=2,
            hover=False
        )
        if i < 5:
            hit.grid(row=0, column=i, padx=5, pady=5)
        else:
            hit.grid(row=2, column=i-5, padx=5, pady=5)

        tabButtons.append(hit)


def update_armour(name=None):

    """Get the armour boosts.

    Returns:
        tuple: (Attack Up Level, Bone Damage Multiplier)
    """

    attackUpLevel = 0
    boneUp = 1

    head = headArmour.get()
    body = bodyArmour.get()
    leg = legArmour.get()

    if head == "None" or body == "None" or leg == "None":
        return attackUpLevel, boneUp

    if (headpiece[head]["Set"] == bodypiece[body]["Set"]
            == legpiece[leg]["Set"]):
        if headpiece[head]["Set Bonus"]:
            if headpiece[head]["Set Bonus"] == "Attack Up":
                attackUpLevel += 1
            elif headpiece[head]["Set Bonus"] == "Disguise; Bone Weap. Prof.":
                boneUp = 1.8

    if headpiece[head]["Effect"] == "Attack Up":
        attackUpLevel += 1
    if bodypiece[body]["Effect"] == "Attack Up":
        attackUpLevel += 1
    if legpiece[leg]["Effect"] == "Attack Up":
        attackUpLevel += 1

    return attackUpLevel, boneUp


bwLabel = customtkinter.CTkLabel(
    app,
    text="Base Weapon",
    font=("Garamond", 18),
    text_color=("gray14", "#FFFFFF")
)
bwLabel.place(x=80, y=15)

image_label = customtkinter.CTkLabel(
    app,
    text="",
    height=80,
    width=80
)
image_label.place(x=40, y=50)

weapon_tooltip = CTkToolTip(
    image_label
)

combobox = CTkDropdown(
    app,
    command=update_weapon,
    ucommand=update_combobox_options,
    values=keys,
    placex=160,
    placey=50,
    default="Master Sword"
)

modifierLabel = Lables(
    app,
    text="Modifier: "
)
modifierLabel.place(x=160, y=85)

modifiers = ["Attack Up+ "+str(i) if i < 6 else "Attack Up++ "+str(i)
             for i in range(3, 11)]
modifierChoice = Options(
    app,
    width=150,
    values=["None", "Critical Hit"] + modifiers,
    command=schedule_update
)
modifierChoice.set("None")
modifierChoice.place(x=232, y=85)

gloomChoice = Checks(
    app,
    text="Gloom",
    command=schedule_update
)

bpLabel = Lables(
    app,
    text="Shown Attack Power: "
)
bpLabel.place(x=480, y=50)

truBALabel = Lables(
    app,
    text="True Attack Power: "
)
truBALabel.place(x=480, y=75)

durLabel = Lables(
    app,
    text="Durability: "
)
durLabel.place(x=480, y=100)

typeLabel = Lables(
    app,
    text="Type: "
)
typeLabel.place(x=480, y=125)

durEntry = customtkinter.CTkEntry(
    app,
    width=30,
    font=("Garamond", 15),
    text_color=("gray14", "#FFFFFF"),
    validate="key",
    validatecommand=(validate_dur, "%P"),
)
durEntry.place(x=560, y=100)
durEntry.bind('<KeyRelease>', schedule_update)

# Fuse Material
abLabel = customtkinter.CTkLabel(
    app,
    text="Fuse Material",
    font=("Garamond", 20),
    text_color=("gray14", "#FFFFFF")
)
abLabel.place(x=80, y=150)

mImage_label = customtkinter.CTkLabel(
    app,
    text="",
    height=80,
    width=80
)
mImage_label.place(x=40, y=200)

material_tooltip = CTkToolTip(
    mImage_label
)

mCombobox = CTkDropdown(
    app,
    command=update_material,
    ucommand=update_mCombobox_options,
    values=mKeys,
    placex=160,
    placey=225
)

power = Lables(
    app,
    text="Fuse Additional Power: "
)
power.place(x=480, y=150)

perHit = Lables(
    app
)
perHit.place(x=480, y=200)

comboDmg = Lables(
    app,
    text="Combo Damage: "
)
comboDmg.place(x=480, y=225)

comboTable = customtkinter.CTkFrame(
    app,
    width=160,
    height=50
)
comboTable.place(x=480, y=250)

buffLabel = customtkinter.CTkLabel(
    app,
    text="Other Modifiers",
    font=("Garamond", 18),
    text_color=("gray14", "#FFFFFF")
)
buffLabel.place(x=80, y=300)

armLabel = Lables(
    app,
    text="Armour",
    font=("Garamond", 18)
)
armLabel.place(x=40, y=325)

headLabel = Lables(
    app,
    text="Head Piece:"
)
headLabel.place(x=40, y=350)

headArmour = CTkDropdown(
    app,
    values=["None"] + list(headpiece.keys()),
    width=200,
    placex=130,
    placey=350,
    command=schedule_update
)

bodyLabel = Lables(
    app,
    text="Body Piece:"
)
bodyLabel.place(x=40, y=380)

bodyArmour = CTkDropdown(
    app,
    values=["None"] + list(bodypiece.keys()),
    width=200,
    placex=130,
    placey=380,
    command=schedule_update
)

legLabel = Lables(
    app,
    text="Head Piece:"
)
legLabel.place(x=40, y=410)

legArmour = CTkDropdown(
    app,
    values=["None"] + list(legpiece.keys()),
    width=200,
    placex=130,
    placey=410,
    command=schedule_update
)


attackupLabel = Lables(
    app,
    text="Attack Up:"
)
attackupLabel.place(x=40, y=450)

attackup = CTkDropdown(
    app,
    values=[0, 1, 2, 3],
    width=200,
    placex=130,
    placey=450,
    height=120,
    default=0,
    command=schedule_update
)

sneak = Checks(
    app,
    text="Sneakstrike",
    command=schedule_update
)
sneak.place(x=40, y=490)
CTkToolTip(
    sneak,
    text="» 8x Attack Power\n» 16x Attack Power with Eightfold Blade"
)

isWet = Checks(
    app,
    text="Wet",
    command=schedule_update
)
isWet.place(x=200, y=490)
CTkToolTip(
    isWet,
    text="» 2x Attack Power with Zora Weapons"
)

flurry = Checks(
    app,
    text="Flurry Rush",
    command=schedule_update
)
flurry.place(x=40, y=520)
CTkToolTip(
    flurry,
    text="» 2x Attack Power with Royal Weapons"
)

hp = Checks(
    app,
    text="Low HP",
    command=schedule_update
)
hp.place(x=200, y=520)
CTkToolTip(
    hp,
    text="» 2x Attack Power with Knight's Weapon"
)

combobox.update()
mCombobox.update()
headArmour.update()
bodyArmour.update()
legArmour.update()
attackup.update()

app.mainloop()
