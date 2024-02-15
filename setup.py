import sys # Imports are automatically detected (normally) in the script to freeze
import os 
import cx_Freeze

base = None 

os.environ["TCL_LIBRARY"] = "C:\\Users\\jlong\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tcl8.6"
os.environ["TK_LIBRARY"] = "C:\\Users\\jlong\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tk8.6"

if sys.platform=='win32':
    base = "Win32GUI"


executables = [cx_Freeze.Executable("dmse.py", base=base)]    

cx_Freeze.setup(
        name = "DMSE Utilities",
        options = {"build_exe":{"packages":["tkinter"],"include_files":["icon.ico", "C:\\Users\\jlong\\AppData\\Local\\Programs\\Python\\Python311\\DLLs\\tcl86t.dll", "C:\\Users\\jlong\\AppData\\Local\\Programs\\Python\\Python311\\DLLs\\tk86t.dll"]}},
        version="0.4",
        executables=executables) 