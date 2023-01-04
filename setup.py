import sys
from cx_Freeze import setup, Executable

# base="Win32GUI" should be used only for Windows GUI app
base = None
if sys.platform == "win32":
    base = "Win32GUI"

packages = []
includes = []
include_files = ["libs","powerconfig.conf"]
zip_include_packages = []
executables = [Executable("main.py", targetName='m695tool.exe', base=base, icon="Setting.ico")]

build_exe_options = {
    'build_exe': {
        "includes": includes,
        "include_files": include_files,
        "packages": packages,
        "zip_include_packages": zip_include_packages,
        "no_compress": True
    },
}
setup(name="M695 Tool",
      version="0.1",
      description="My GUI application!",
      options=build_exe_options,
      executables=executables)
