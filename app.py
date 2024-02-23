from tkinter import *
from tkinter import ttk
from GPSPPP.GPSPPP_ui import GPSPPPSection
from LiDARCrop.lidar_crop_ui import LiDARCropSection
from RW5.rw5_ui import Rw5Section
from las2xyz.las2xyz_ui import Las2XYZSection

LIDAR_SECTION_LABEL = "LiDAR"
GPSPPP_SECTION_LABEL = "GPS PPP"
RW5_SECTION_LABEL = "Rw5"
LAS2XYZ_SECTION_LABEL = "Las to XYZ"


class App(Tk):
    """
    Main App
    """

    sections: dict[str, ttk.Frame]

    def __init__(
        self,
        screenName: str | None = None,
        baseName: str | None = None,
        className: str = "Tk",
        useTk: bool = True,
        sync: bool = False,
        use: str | None = None,
    ) -> None:
        super().__init__(screenName, baseName, className, useTk, sync, use)

        s = ttk.Style()
        s.configure(
            "H1.TLabel",
            font=(
                "Helvetica",
                12,
            ),
        )
        s.configure(
            "H2.TLabel",
            font=(
                "Helvetica",
                10,
            ),
        )

        s.configure("Red.TButton", foreground="red")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=BOTH, expand=True)

        self.sections = dict()
        self.sections[LIDAR_SECTION_LABEL] = LiDARCropSection(self.notebook)
        self.sections[LIDAR_SECTION_LABEL].pack(fill=BOTH, expand=True)
        self.sections[GPSPPP_SECTION_LABEL] = GPSPPPSection(self.notebook)
        self.sections[GPSPPP_SECTION_LABEL].pack(fill=BOTH, expand=True, padx=10)
        self.sections[RW5_SECTION_LABEL] = Rw5Section(self.notebook)
        self.sections[RW5_SECTION_LABEL].pack(fill=BOTH, expand=True, padx=10)
        self.sections[LAS2XYZ_SECTION_LABEL] = Las2XYZSection(self.notebook)
        self.sections[LAS2XYZ_SECTION_LABEL].pack(fill=BOTH, expand=True, padx=10)

        self.title("DMSE Utilities")
        self.minsize(520, 300)
        self.iconbitmap("icon.ico")

        for label, section in self.sections.items():
            self.notebook.add(section, text=label)


if __name__ == "__main__":
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
    root = App()
    root.mainloop()
