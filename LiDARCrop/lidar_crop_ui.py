import dataclasses
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from typing import Callable, cast


LIDAR_SECTION_LABEL = "LiDAR"
GPSPPP_SECTION_LABEL = "GPS PPP"
RW5_SECTION_LABEL = "Rw5"


@dataclasses.dataclass
class LidarCropFormData:
    easting_min: StringVar = dataclasses.field(default_factory=lambda: StringVar())
    northing_min: StringVar = dataclasses.field(default_factory=lambda: StringVar())
    easting_max: StringVar = dataclasses.field(default_factory=lambda: StringVar())
    northing_max: StringVar = dataclasses.field(default_factory=lambda: StringVar())

    input_files: StringVar = dataclasses.field(
        default_factory=lambda: StringVar(value="")
    )
    """newline separated"""
    output_file: StringVar = dataclasses.field(
        default_factory=lambda: StringVar(value="")
    )


class LiDARCropSection(ttk.Frame):
    """
    LiDAR Processing
    """

    class LimitsForm(ttk.Frame):
        def __init__(
            self, master: Misc | None, form_data: LidarCropFormData, **kwargs
        ) -> None:
            super().__init__(master, **kwargs)
            self.form_data = form_data

            ttk.Label(self, text="LiDAR Limits", style="H1.TLabel").grid(
                row=0, column=0, columnspan=4, sticky=W, pady=5
            )
            ttk.Label(self, text="Lower left corner", style="H2.TLabel").grid(
                row=1, column=0, columnspan=4, sticky=W
            )
            ttk.Label(self, text="Easting").grid(row=2, column=0, padx=(0, 10))
            ttk.Entry(self, textvariable=self.form_data.easting_min).grid(
                row=2,
                column=1,
            )
            ttk.Label(self, text="Northing").grid(row=2, column=2, padx=(10, 10))
            ttk.Entry(self, textvariable=self.form_data.northing_min).grid(
                row=2, column=3
            )

            ttk.Label(self, text="Upper right corner", style="H2.TLabel").grid(
                row=3, column=0, columnspan=4, sticky=W
            )
            ttk.Label(self, text="Easting").grid(row=4, column=0, padx=(0, 10))
            ttk.Entry(self, textvariable=self.form_data.easting_max).grid(
                row=4, column=1
            )
            ttk.Label(self, text="Northing").grid(row=4, column=2, padx=(10, 10))
            ttk.Entry(self, textvariable=self.form_data.northing_max).grid(
                row=4, column=3
            )

    class PathSelectionForm(ttk.Frame):
        def __init__(
            self,
            master: Misc | None,
            form_data: LidarCropFormData,
            on_select_input: Callable,
            on_select_output: Callable,
            **kwargs,
        ) -> None:
            super().__init__(master, **kwargs)
            self.form_data = form_data

            ttk.Label(self, text="Included Files", style="H1.TLabel").grid(
                row=0, column=0, columnspan=4, sticky=W, pady=5
            )
            ttk.Label(self, text="Input files", style="H2.TLabel").grid(
                row=1, column=0, columnspan=2, sticky=W
            )
            ttk.Button(self, text="Add file", command=on_select_input).grid(
                row=1, column=2, padx=5, sticky=W
            )
            ttk.Label(self, textvariable=self.form_data.input_files).grid(
                row=2, column=0, columnspan=4, sticky=W
            )
            ttk.Label(self, text="Output file", style="H2.TLabel").grid(
                row=3, column=0, columnspan=2, sticky=W
            )
            ttk.Button(self, text="Select output file", command=on_select_output).grid(
                row=3, column=2, padx=5, sticky=W
            )
            ttk.Label(self, textvariable=self.form_data.output_file).grid(
                row=4, column=0, columnspan=4, sticky=W
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

    def __init__(self, master: Misc | None = None, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.form_data = LidarCropFormData()

        self.form_data.easting_max.trace("w", self.on_validate_form)
        self.form_data.easting_max.trace("w", self.on_validate_form)
        self.form_data.easting_max.trace("w", self.on_validate_form)
        self.form_data.easting_max.trace("w", self.on_validate_form)
        self.form_data.easting_max.trace("w", self.on_validate_form)
        self.form_data.easting_max.trace("w", self.on_validate_form)

        self.limits_form = self.LimitsForm(self, self.form_data)
        self.limits_form.pack(fill=X, pady=5, padx=10)
        ttk.Separator(self, orient="horizontal").pack(fill=X, pady=5)

        self.path_selection_form = self.PathSelectionForm(
            self,
            self.form_data,
            on_select_input=self.on_select_input,
            on_select_output=self.on_select_output,
        )
        self.path_selection_form.pack(fill=X, pady=5, padx=10, expand=False)
        ttk.Separator(self, orient="horizontal").pack(fill=X, pady=5)

        self.buttons_row = self.ButtonsRow(
            self, on_compute=self.on_compute, on_reset=self.on_reset
        )
        self.buttons_row.pack(fill=X, ipady=5, anchor=S, expand=True, padx=10)

    def on_compute(self) -> None:
        # open output file
        east_min = float(self.form_data.easting_min.get())
        east_max = float(self.form_data.easting_max.get())
        north_min = float(self.form_data.northing_min.get())
        north_max = float(self.form_data.northing_max.get())

        output: list[str] = []
        retry = False
        # create output
        try:
            for i_file in self.form_data.input_files.get().splitlines():
                with open(i_file, "r") as input_file:
                    for line in input_file:
                        instr = line.split(" ")
                        east_in = float(instr[0])
                        if east_in > east_min and east_in < east_max:
                            north_in = float(instr[1])
                            if north_in > north_min and north_in < north_max:
                                output.append(line)
        except OSError as err:
            retry = messagebox.askretrycancel(
                "Whoops",
                f"""
                There was an error when trying to parse the input files you provided.\n
                OSError: {err}
            """,
            )
        except Exception as err:
            retry = messagebox.askretrycancel(
                "Whoops",
                f"""
                There was an error when trying to parse the input files you provided.\n
                The issue may also involve your inputs (we just don't know).\n
                Unexpected error: {err}
            """,
            )
        if retry:
            return self.on_compute()

        # write output to the output file
        try:
            with open(self.form_data.output_file.get(), "w") as output_file:
                output_file.writelines(output)
        except OSError as err:
            retry = messagebox.askretrycancel(
                "Whoops",
                f"""
                There was an error when trying to save your results.\n
                OSError: {err}
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

    def on_reset(self) -> None:
        self.form_data.easting_max.set("")
        self.form_data.northing_max.set("")
        self.form_data.easting_min.set("")
        self.form_data.northing_min.set("")
        self.form_data.input_files.set("")
        self.form_data.output_file.set("")

    def on_select_input(self) -> None:
        filenames = cast(
            list[str],
            filedialog.askopenfilenames(
                title="Select file",
                filetypes=(("XYZ files", "*.xyz"), ("all files", "*.*")),
            ),
        )

        self.form_data.input_files.set("\n".join(filenames))

    def on_select_output(self) -> None:
        filename = filedialog.asksaveasfilename(
            title="Select file",
            filetypes=(("XYZ files", "*.xyz"), ("all files", "*.*")),
            defaultextension="xyz",
            initialfile="dmse-output.xyz",
        )

        self.form_data.output_file.set(filename)

    def on_validate_form(self, *_) -> None:
        if (
            (
                len(self.form_data.easting_min.get()) <= 0
                or len(self.form_data.easting_max.get()) <= 0
                or len(self.form_data.northing_min.get()) <= 0
                or len(self.form_data.northing_max.get()) <= 0
            )
            or (
                float(self.form_data.easting_min.get())
                >= float(self.form_data.easting_max.get())
            )
            or (
                float(self.form_data.northing_min.get())
                >= float(self.form_data.northing_max.get())
            )
            or not self.form_data.input_files.get()
            or not self.form_data.output_file.get()
        ):
            self.buttons_row.compute_button["state"] = "disabled"
        else:
            self.buttons_row.compute_button["state"] = "normal"
