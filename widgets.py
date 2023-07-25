import customtkinter
from typing import Callable
import time


class CTkDropdown(customtkinter.CTkToplevel):

    def __init__(
            self,
            master: any,
            text_color: str = ("gray14", "#FFFFFF"),
            font: tuple = ("Garamond", 16),
            command: Callable = None,
            ucommand: Callable = None,
            values: list = None,
            placex: int = 0,
            placey: int = 0,
            height: int = 300,
            width: int = 220,
            list_show: int = 10,
            default: str = "None",
            *args,
            **kwargs
    ):

        super().__init__(
            master
        )

        self.overrideredirect(True)
        self.withdraw()
        self.bind("<FocusOut>", self.focusOut)

        self.after_id = None
        self.values = values
        self.height = height
        self.changed = height
        self.listShow = list_show
        self.command = command
        self.default = default

        self.combobox = customtkinter.CTkComboBox(
            master,
            command=self.update,
            font=font,
            text_color=text_color,
            width=width,
            dcommand=self.show_dropdown
        )

        self.combobox.bind('<KeyRelease>', self.schedule_update)
        self.combobox.bind('<Return>', ucommand)
        self.combobox.place(x=placex, y=placey)

        self.listbox = CTkListBox(
            self,
            command=self.update
        )
        self.listbox.pack(fill=customtkinter.BOTH, expand=True)
        for value in values:
            self.listbox.insert(value)
        self.listbox.initial()

    def show_dropdown(self):
        if self.state() == "withdrawn":

            dropdownX = self.master.winfo_x() + self.combobox.winfo_x() + 7
            dropdownY = self.master.winfo_y() + self.combobox.winfo_y() + 62
            self.geometry(
                f'{self.combobox.cget("width")}x'
                f'{self.changed}+{dropdownX}+{dropdownY}'
            )
            self.deiconify()
            self.focus()

        else:
            self.withdraw()

    def schedule_update(self, event):

        if ((event.char and event.char.isprintable() and event.state == 0)
           or event.keysym == 'BackSpace'):

            if self.after_id:
                self.master.after_cancel(self.after_id)
            self.after_id = self.master.after(1000, self.update_listbox)

    def update_listbox(self, *event):
        self.listbox.delete()
        search_term = self.combobox.get().lower()
        matching_options = [option for option in self.values
                            if search_term in option.lower()]

        length = len(matching_options)

        if length == 0:
            matching_options = ["No Results"]
            height = 40
        elif length >= self.listShow:
            height = self.height
        else:
            height = length * 25 + 15

        self.changed = height

        for option in matching_options:
            self.listbox.insert(option)
        dropdownX = self.master.winfo_x() + self.combobox.winfo_x() + 7
        dropdownY = self.master.winfo_y() + self.combobox.winfo_y() + 62

        self.geometry(
            f'{self.combobox.cget("width")}x{height}+{dropdownX}+{dropdownY}'
        )

        self.deiconify()

    def get(self):
        return self.combobox.get()

    def update(self, value=None):

        if not value or value == "No Results":
            value = self.default

        self.withdraw()
        self.combobox.set(value)

        if self.command:
            self.command(value)

    def focusOut(self, *event):
        self.withdraw()


class Lables(customtkinter.CTkLabel):

    def __init__(
            self, master, font=("Garamond", 16), *args, **kwargs
    ):
        customtkinter.CTkLabel.__init__(
            self,
            master,
            font=font,
            text_color=("gray14", "#FFFFFF"),
            anchor=customtkinter.W,
            justify=customtkinter.LEFT,
            *args,
            **kwargs
        )


class Checks(customtkinter.CTkCheckBox):

    def __init__(self, *args, **kwargs):
        customtkinter.CTkCheckBox.__init__(
            self,
            font=("Garamond", 16),
            checkbox_height=20,
            checkbox_width=20,
            onvalue=True,
            offvalue=False,
            *args,
            **kwargs
        )

        self.variable = customtkinter.BooleanVar()
        self.variable.set(False)
        self.configure(variable=self.variable)

    def value(self):
        return self.variable.get()

    def set_value(self, value: bool = False):
        self.variable.set(value)


class Options(customtkinter.CTkOptionMenu):

    def __init__(self, *args, **kwargs):
        comboTheme = customtkinter.ThemeManager.theme["CTkComboBox"]

        customtkinter.CTkOptionMenu.__init__(
            self,
            font=("Garamond", 15),
            fg_color=comboTheme["fg_color"],
            button_color=comboTheme["button_color"],
            button_hover_color=comboTheme["button_hover_color"],
            dropdown_font=("Garamond", 14),
            *args,
            **kwargs
        )


class CTkListBox(customtkinter.CTkScrollableFrame):

    def __init__(
            self,
            master: any,
            text_color: str = ("gray14", "#FFFFFF"),
            font: tuple = ("Garamond", 15),
            command: Callable = None,
            border_width: int = 3,
            *args,
            **kwargs
    ):

        super().__init__(
            master,
            border_width=border_width
        )
        self._scrollbar.grid_configure(padx=(0, border_width))

        self.text_color = text_color
        self.font = font

        self.buttons: list[customtkinter.CTkButton] = []
        self.command = command
        self.selected: customtkinter.CTkButton = None

    def insert(self, value):

        idx = len(self.buttons)

        button = customtkinter.CTkButton(
            self,
            text=value,
            fg_color="transparent",
            text_color=self.text_color,
            font=self.font,
            height=25,
            anchor="nw",
            command=lambda num=idx: self.select(num)
        )
        button.grid(row=idx, column=0, sticky="ew")

        self.buttons.append(button)

    def delete(self):

        for button in self.buttons:
            button.destroy()

        self.selected = None

    def select(self, idx):
        if self.selected:
            self.selected.configure(fg_color="transparent", hover=True)
        self.selected: customtkinter.CTkButton = self.buttons[idx]
        self.selected.configure(fg_color="#14375e", hover=False)

        if self.command:
            self.command(self.selected.cget("text"))

    def initial(self):
        self.selected: customtkinter.CTkButton = self.buttons[0]
        self.selected.configure(fg_color="#14375e", hover=False)


class CTkToolTip(customtkinter.CTkToplevel):

    def __init__(
            self,
            widget: any,
            text: str = None,
            delay: int = 500,
            font=("Garamond", 15)
    ):

        super().__init__(
            widget
        )

        self.widget = widget
        self.text = text
        self.delay = delay
        self.move = None
        self.out = False

        self.overrideredirect(True)
        self.focus()
        self.transient()
        self.attributes("-alpha", 0.8)
        self.withdraw()
        self.wm_attributes("-topmost", True)

        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.hide_tooltip)
        self.widget.bind("<Motion>", self.on_enter)

        self.frame = customtkinter.CTkFrame(
            self,
            border_width=3
        )
        self.frame.pack(fill=customtkinter.BOTH, expand=True)

        self.label = customtkinter.CTkLabel(
            self.frame,
            text=text,
            font=font,
            justify="left"
        )
        self.label.pack(padx=5, pady=5, fill=customtkinter.BOTH, expand=True)

    def on_enter(self, event):

        self.out = False
        self.move = time.time()
        self.withdraw()

        self.geometry(
            f"+{event.x_root + 10}+{event.y_root + 15}"
        )
        self.after(self.delay, self.show_tooltip)

    def show_tooltip(self):
        if not self.out and time.time() - self.move >= (self.delay / 1000):
            if self.text:
                self.deiconify()

    def hide_tooltip(self, event):
        self.out = True
        self.withdraw()

    def configure(self, text: str = None):

        if self.label:
            self.label.configure(text=text)
            self.text = text
