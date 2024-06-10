import dataclasses
import os
from pathlib import Path
from tkinter import *
from tkinter import filedialog, messagebox, ttk

from .las2xyz import Las2XYZOperation


@dataclasses.dataclass
class Las2XYZFormData:
    """Form data."""

    input_file: StringVar = dataclasses.field(
        default_factory=lambda: StringVar(value=""),
    )
    tile_size: IntVar = dataclasses.field(default_factory=lambda: IntVar(value=100))
    parallel_count: IntVar = dataclasses.field(default_factory=lambda: IntVar(value=15))


class Las2XYZSection(ttk.Frame):
    """Las2XYZ utility UI."""

    class Form(ttk.Frame):
        """Form part of UI."""

        def __init__(
            self,
            master: Misc | None,
            form_data: Las2XYZFormData,
            **kwargs,
        ) -> None:
            super().__init__(master, **kwargs)
            self.form_data = form_data

            ttk.Label(self, text="Input Las File", style="H2.TLabel").grid(
                row=1,
                column=0,
                columnspan=2,
                sticky=W,
            )
            ttk.Button(self, text="Select", command=self.choose_input_file).grid(
                row=1,
                column=2,
                padx=5,
                sticky=W,
            )
            ttk.Label(self, textvariable=self.form_data.input_file).grid(
                row=2,
                column=0,
                columnspan=4,
                sticky=W,
            )
            ttk.Label(self, text="Tile size (m)", style="H2.TLabel").grid(
                row=3,
                column=0,
                padx=(0, 10),
                sticky=W,
            )
            ttk.Entry(self, textvariable=self.form_data.tile_size).grid(
                row=3,
                column=1,
                sticky=W,
                columnspan=2,
            )
            ttk.Label(self, text="Parallel count", style="H2.TLabel").grid(
                row=4,
                column=0,
                padx=(0, 10),
                sticky=W,
            )
            ttk.Entry(self, textvariable=self.form_data.parallel_count).grid(
                row=4,
                column=1,
                sticky=W,
                columnspan=2,
            )

        def choose_input_file(self):
            input_path = filedialog.askopenfilename(
                title="Select file",
                filetypes=(("Las files", "*.las"), ("all files", "*.*")),
            )
            self.form_data.input_file.set(input_path)

    class ButtonsRow(ttk.Frame):
        def __init__(
            self,
            master: Misc | None,
            **kwargs,
        ) -> None:
            super().__init__(master, **kwargs)

            self.start_button = ttk.Button(self, text="Start")
            self.start_button.pack(side=RIGHT)

    def __init__(self, master: Misc | None, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.form_data = Las2XYZFormData()
        self.converter = Las2XYZOperation()
        self.on_tile_size_changed()

        self.Form(self, self.form_data).pack(fill=X, pady=5, padx=10, expand=False)
        ttk.Separator(self, orient="horizontal").pack(fill=X, pady=5)
        self.log = Text(self, state="disabled")
        self.log.pack(fill=X, pady=5, expand=True)
        self.buttons_row = self.ButtonsRow(self)
        self.buttons_row.pack(fill=X, ipady=5, anchor=S, expand=True, padx=10)

        self.form_data.input_file.trace_add("write", self.on_input_changed)
        self.tile_size_trace_cb = self.form_data.tile_size.trace_add(
            "write",
            self.on_tile_size_changed,
        )
        self.parallel_count_trace_cb = self.form_data.parallel_count.trace_add(
            "write",
            self.on_parallel_count_changed,
        )

        self.buttons_row.start_button.configure(command=self.on_start)

    def on_input_changed(self, *_):
        path = Path(self.form_data.input_file.get())
        self.converter.set_input(path)

    def on_tile_size_changed(self, *_):
        size: int
        try:
            size = int(self.form_data.tile_size.get())
        except ValueError:
            self.form_data.tile_size.trace_remove("write", self.tile_size_trace_cb)
            size = 100
            self.form_data.tile_size.set(size)
            self.tile_size_trace_cb = self.form_data.tile_size.trace_add(
                "write",
                self.on_tile_size_changed,
            )

        self.converter.set_tile_size(size)

    def on_parallel_count_changed(self, *_):
        count: int
        try:
            count = int(self.form_data.parallel_count.get())
        except ValueError:
            self.form_data.parallel_count.trace_remove(
                "write",
                self.parallel_count_trace_cb,
            )
            count = 15
            self.form_data.parallel_count.set(count)
            self.parallel_count_trace_cb = self.form_data.parallel_count.trace_add(
                "write",
                self.on_parallel_count_changed,
            )

        self.converter.parallel_count = count

    def on_start(self):
        def on_done(output_path: Path):
            open_dir = messagebox.askokcancel("Success", str(output_path))
            if open_dir and os.name == "nt":
                os.system(f"explorer.exe /select,{output_path!s}")

        def on_progress(log_widget: Text, filename: str):
            print(filename)
            log_widget.configure(state="normal")
            log_widget.insert(END, filename + "\n")
            log_widget.configure(state="disabled")
            log_widget.see(END)
            log_widget.update()

        out_dir = filedialog.askdirectory(
            title="Select directory",
        )
        if not out_dir:
            return
        output_directory_path = Path(out_dir)

        self.converter.set_output_dir(output_directory_path)

        self.converter.start(
            lambda filename: on_progress(self.log, filename),
            on_done,
        )
