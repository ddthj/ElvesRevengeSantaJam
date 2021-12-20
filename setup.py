import sys
from cx_Freeze import setup, Executable


build_options = {'includes': ["DGR.Shapes"], 'packages': ["pygame"], 'excludes': ["cx-Freeze", "cx-Logging", "importlib-metadata", "pip", "setuptools", "zipp"]}

base = 'Win32GUI' if sys.platform == 'win32' else None

setup(name='ElvesRevengeSantaJam',
      version='0.1',
      description='2021 Santa Jam',
      options={'build_exe': build_options},
      executables=[Executable('ElvesRevengeSantaJam.py', base=base)])
