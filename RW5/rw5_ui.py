import dataclasses
import os
from pathlib import Path
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from typing import Callable, Optional

from .rw5_to_dat import ConvertOperation


@dataclasses.dataclass
class RW5FormData:
    input_file: StringVar = dataclasses.field(
        default_factory=lambda: StringVar(value="")
    )
    output_file: StringVar = dataclasses.field(
        default_factory=lambda: StringVar(value="")
    )


class Rw5Section(ttk.Frame):
    """
    .rw5 to .dat conversion
    """

    class PathSelectionForm(ttk.Frame):
        def __init__(
            self, master: Misc | None, form_data: RW5FormData, **kwargs
        ) -> None:
            super().__init__(master, **kwargs)
            self.form_data = form_data

            ttk.Label(self, text="Included Files", style="H1.TLabel").grid(
                row=0, column=0, columnspan=4, sticky=W, pady=5
            )
            ttk.Label(self, text="Input Rw5 data", style="H2.TLabel").grid(
                row=1, column=0, columnspan=2, sticky=W
            )
            ttk.Button(self, text="RW5 file", command=self.choose_input_file).grid(
                row=1, column=2, padx=5, sticky=W
            )
            ttk.Label(self, textvariable=self.form_data.input_file).grid(
                row=2, column=0, columnspan=4, sticky=W
            )
            ttk.Label(self, text="Output file", style="H2.TLabel").grid(
                row=3, column=0, columnspan=2, sticky=W
            )
            ttk.Button(
                self, text="Select output file", command=self.choose_output_file
            ).grid(row=3, column=2, padx=5, sticky=W)
            ttk.Label(self, textvariable=self.form_data.output_file).grid(
                row=4, column=0, columnspan=4, sticky=W
            )

        def choose_input_file(self):
            input_path = filedialog.askopenfilename(
                title="Select file",
                filetypes=(("RW5 files", "*.rw5"), ("all files", "*.*")),
            )
            self.form_data.input_file.set(input_path)
            output_path = input_path[: input_path.rfind(".")] + ".dat"
            self.form_data.output_file.set(output_path)

        def choose_output_file(self):
            input_filename: Optional[str] = None
            if input_path := self.form_data.input_file.get():
                _, input_filename = os.path.split(input_path)
                input_filename = input_filename[: input_filename.rfind(".")] + ".dat"
            self.form_data.output_file.set(
                filedialog.asksaveasfilename(
                    title="Select file",
                    filetypes=(("TXT files", "*.txt"), ("all files", "*.*")),
                    initialfile=input_filename,
                )
            )

    class ButtonsRow(ttk.Frame):
        def __init__(
            self,
            master: Misc | None,
            on_compute: Callable,
            on_reset: Callable,
            **kwargs,
        ) -> None:
            super().__init__(master, **kwargs)

            self.compute_button = ttk.Button(
                self, text="Compute", command=on_compute, state="disabled"
            )
            self.compute_button.pack(side=RIGHT)
            ttk.Button(self, text="Reset", style="Red.TButton", command=on_reset).pack(
                side=RIGHT, padx=5
            )

    def on_validate_form(self, *_) -> None:
        if not self.form_data.input_file.get() or not self.form_data.output_file.get():
            self.buttons_row.compute_button["state"] = "disabled"
        else:
            self.buttons_row.compute_button["state"] = "normal"

    def on_reset(self) -> None:
        self.form_data.input_file.set("")
        self.form_data.output_file.set("")

    def on_compute(self) -> None:
        try:
            co = ConvertOperation(
                Path(self.form_data.input_file.get()),
                Path(self.form_data.output_file.get()),
            )

            co.start()

            co.save()

            messagebox.showinfo(
                "Success",
                f"""
                Output saved to {self.form_data.output_file.get()}.
            """,
            )
        except Exception as err:
            retry = messagebox.askretrycancel(
                "Whoops",
                f"""
                There was an error when trying to save your results.\n
                rw5_to_dat threw: {err}
            """,
            )

            if retry:
                return self.on_compute()
            else:
                raise err

    def __init__(self, master: Misc | None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.form_data = RW5FormData()

        self.form_data.input_file.trace("w", self.on_validate_form)
        self.form_data.output_file.trace("w", self.on_validate_form)

        self.PathSelectionForm(self, self.form_data).pack(
            fill=X, pady=5, padx=10, expand=False
        )
        ttk.Separator(self, orient="horizontal").pack(fill=X, pady=5)

        self.buttons_row = self.ButtonsRow(self, self.on_compute, self.on_reset)
        self.buttons_row.pack(fill=X, ipady=5, anchor=S, expand=True, padx=10)
