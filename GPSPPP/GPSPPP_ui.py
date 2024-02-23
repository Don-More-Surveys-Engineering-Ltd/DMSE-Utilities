import dataclasses
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from typing import Callable

from .GPSPPP import GPS_PPP_Calc


@dataclasses.dataclass
class GPSPPPFormData:
    SUM_file: StringVar = dataclasses.field(default_factory=lambda: StringVar(value=""))
    LOC_file: StringVar = dataclasses.field(default_factory=lambda: StringVar(value=""))
    REF_file: StringVar = dataclasses.field(default_factory=lambda: StringVar(value=""))
    output_file: StringVar = dataclasses.field(
        default_factory=lambda: StringVar(value="")
    )


class GPSPPPSection(ttk.Frame):
    """
    GPSPPP Processing
    """

    class PathSelectSection(ttk.Frame):
        def __init__(
            self, master: Misc | None, form_data: GPSPPPFormData, **kwargs
        ) -> None:
            super().__init__(master, **kwargs)
            self.form_data = form_data

            ttk.Label(self, text="Included Files", style="H1.TLabel").grid(
                row=0, column=0, columnspan=4, sticky=W, pady=5
            )
            ttk.Label(self, text="REF file", style="H2.TLabel").grid(
                row=1, column=0, columnspan=2, sticky=W
            )
            ttk.Button(self, text="Choose file", command=self.choose_ref_file).grid(
                row=1, column=2, padx=5, sticky=W
            )
            ttk.Label(self, textvariable=self.form_data.REF_file).grid(
                row=2, column=0, columnspan=4, sticky=W
            )
            ttk.Label(self, text="SUM file", style="H2.TLabel").grid(
                row=3, column=0, columnspan=2, sticky=W
            )
            ttk.Button(self, text="Choose file", command=self.choose_sum_file).grid(
                row=3, column=2, padx=5, sticky=W
            )
            ttk.Label(self, textvariable=self.form_data.SUM_file).grid(
                row=4, column=0, columnspan=4, sticky=W
            )
            ttk.Label(self, text="LOC file (Optional)", style="H2.TLabel").grid(
                row=5, column=0, columnspan=2, sticky=W
            )
            ttk.Button(self, text="Choose file", command=self.choose_loc_file).grid(
                row=5, column=2, padx=5, sticky=W
            )
            ttk.Label(self, textvariable=self.form_data.LOC_file).grid(
                row=6, column=0, columnspan=4, sticky=W
            )
            ttk.Label(self, text="Output file", style="H2.TLabel").grid(
                row=7, column=0, columnspan=2, sticky=W
            )
            ttk.Button(
                self, text="Choose save file", command=self.choose_output_file
            ).grid(row=7, column=2, padx=5, sticky=W)
            ttk.Label(self, textvariable=self.form_data.output_file).grid(
                row=8, column=0, columnspan=4, sticky=W
            )

        def choose_sum_file(self):
            self.form_data.SUM_file.set(
                filedialog.askopenfilename(
                    title="Select file",
                    filetypes=(("SUM files", "*.sum"), ("all files", "*.*")),
                )
            )

        def choose_ref_file(self):
            self.form_data.REF_file.set(
                filedialog.askopenfilename(
                    title="Select file",
                    filetypes=(("REF files", "*.ref"), ("all files", "*.*")),
                )
            )

        def choose_loc_file(self):
            self.form_data.LOC_file.set(
                filedialog.askopenfilename(
                    title="Select file",
                    filetypes=(("LOC files", "*.loc"), ("all files", "*.*")),
                )
            )

        def choose_output_file(self):
            path = filedialog.asksaveasfilename(
                title="Select file",
                filetypes=(("TXT files", "*.txt"), ("all files", "*.*")),
            )
            if path[path.rfind("/") + 1 :].find(".txt") == -1:
                path += ".txt"
            self.form_data.output_file.set(path)

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

    def __init__(self, master: Misc | None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.form_data = GPSPPPFormData()

        self.form_data.REF_file.trace("w", self.on_validate_form)
        self.form_data.SUM_file.trace("w", self.on_validate_form)
        self.form_data.output_file.trace("w", self.on_validate_form)

        self.PathSelectSection(self, self.form_data).pack(
            fill=X, pady=5, padx=10, expand=False
        )
        ttk.Separator(self, orient="horizontal").pack(fill=X, pady=5)

        self.buttons_row = self.ButtonsRow(self, self.on_compute, self.on_reset)
        self.buttons_row.pack(fill=X, ipady=5, anchor=S, expand=True, padx=10)

    def on_validate_form(self, *_) -> None:
        if (
            not self.form_data.REF_file.get()
            or not self.form_data.SUM_file.get()
            or not self.form_data.output_file.get()
        ):
            self.buttons_row.compute_button["state"] = "disabled"
        else:
            self.buttons_row.compute_button["state"] = "normal"

    def on_reset(self) -> None:
        self.form_data.REF_file.set("")
        self.form_data.SUM_file.set("")
        self.form_data.LOC_file.set("")
        self.form_data.output_file.set("")

    def on_compute(self) -> None:
        try:
            GPS_PPP_Calc(
                self.form_data.REF_file.get(),
                self.form_data.SUM_file.get(),
                self.form_data.LOC_file.get(),
                self.form_data.output_file.get(),
            )
        except Exception as err:
            retry = messagebox.askretrycancel(
                "Whoops",
                f"""
                There was an error when trying to save your results.\n
                GPS_PPP_calc threw: {err}
            """,
            )

            if retry:
                return self.on_compute()

        messagebox.showinfo(
            "Success",
            f"""
            Output saved to {self.form_data.output_file.get()}.
        """,
        )
