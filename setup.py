import sys  # Imports are automatically detected (normally) in the script to freeze
import os
import cx_Freeze

base = None

os.environ["TCL_LIBRARY"] = (
    "C:\\Users\\jlong\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tcl8.6"
)
os.environ["TK_LIBRARY"] = (
    "C:\\Users\\jlong\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tk8.6"
)

if sys.platform == "win32":
    base = "Win32GUI"


include_files = [
    "icon.ico",
    "C:\\Users\\jlong\\AppData\\Local\\Programs\\Python\\Python311\\DLLs\\tcl86t.dll",
    "C:\\Users\\jlong\\AppData\\Local\\Programs\\Python\\Python311\\DLLs\\tk86t.dll",
    "helpers/las2txt.exe",
]
packages = ["tkinter"]
executables = [cx_Freeze.Executable("app.py", base=base)]

cx_Freeze.setup(
    name="DMSE Utilities",
    options={"build_exe": {"packages": packages, "include_files": include_files}},
    version="0.5",
    executables=executables,
)
