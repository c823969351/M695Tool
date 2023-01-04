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

# http://msdn.microsoft.com/en-us/library/windows/desktop/aa371847(v=vs.85).aspx
shortcut_table = [
    ("DesktopShortcut",        # Shortcut
     "DesktopFolder",          # Directory_
     "M695 Tool",           # Name that will be show on the link
     "TARGETDIR",              # Component_
     "[TARGETDIR]m695tool.exe",# Target exe to exexute
     None,                     # Arguments
     None,                     # Description
     None,                     # Hotkey
     None,                     # Icon
     None,                     # IconIndex
     None,                     # ShowCmd
     'TARGETDIR'               # WkDir
     )
    ]

# Now create the table dictionary
msi_data = {"Shortcut": shortcut_table}

# Change some default MSI options and specify the use of the above defined tables
bdist_msi_options = {'data': msi_data}

build_exe_options = {
    'build_exe': {
        "includes": includes,
        "include_files": include_files,
        "packages": packages,
        "zip_include_packages": zip_include_packages,
        "no_compress": True
    },
    "bdist_msi": bdist_msi_options,
}
setup(name="M695 Tool",
      version="0.1",
      description="My GUI application!",
      options=build_exe_options,
      executables=executables)
