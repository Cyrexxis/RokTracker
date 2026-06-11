from tkinter import CENTER

import ttkbootstrap as ttk


class InfoDialog(ttk.Toplevel):
    def __init__(
        self,
        display_title,
        display_text,
        size="300x400",
        close_cb=lambda: None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self._running: bool = False
        self._title = display_title
        self._text = display_text
        self.close_cb = close_cb

        self.title(self._title)
        self.geometry(size)
        self.lift()
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)
        self.resizable(False, False)
        self.grab_set()

    def _create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = ttk.Message(
            master=self,
            width=300,
            text=self._text,
            justify=CENTER,
        )
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._ok_button = ttk.Button(
            master=self,
            text="Ok",
            command=self._ok_event,
        )
        self._ok_button.grid(
            row=1, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew"
        )

    def _ok_event(self, event=None):
        self.grab_release()
        self.destroy()
        self.close_cb()

    def _on_closing(self):
        self.grab_release()
        self.destroy()
        self.close_cb()

    def wait_for_close(self):
        self.master.wait_window(self)


class ConfirmDialog(ttk.Toplevel):
    def __init__(self, display_title, display_text, size="300x400", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._user_input: bool = False
        self._running: bool = False
        self._title = display_title
        self._text = display_text

        self.title(self._title)
        self.geometry(size)
        self.lift()
        self.attributes("-topmost", True)
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
        self.after(10, self._create_widgets)
        self.resizable(False, False)
        self.grab_set()

    def _create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self._label = ttk.Message(
            master=self,
            width=300,
            text=self._text,
            justify=CENTER,
        )
        self._label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self._ok_button = ttk.Button(
            master=self,
            text="Yes",
            command=self._ok_event,
        )
        self._ok_button.grid(
            row=1,
            column=0,
            columnspan=1,
            padx=(20, 10),
            pady=(0, 20),
            sticky="ew",
        )

        self._cancel_button = ttk.Button(
            master=self,
            text="No",
            command=self._cancel_event,
        )
        self._cancel_button.grid(
            row=1,
            column=1,
            columnspan=1,
            padx=(10, 20),
            pady=(0, 20),
            sticky="ew",
        )

    def _ok_event(self, event=None):
        self._user_input = True
        self.grab_release()
        self.destroy()

    def _on_closing(self):
        self.grab_release()
        self.destroy()

    def _cancel_event(self):
        self._user_input = False
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self._user_input
