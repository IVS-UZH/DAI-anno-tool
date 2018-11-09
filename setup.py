# Copyright 2018 Taras Zakharko (taras.zakharko)
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
 py2app/py2exe build script for MyApplication.

 Will automatically ensure that all build prerequisites are available
 via ez_setup

 Usage (Mac OS X):
     python setup.py py2app

 Usage (Windows):
     python setup.py py2exe
"""
import sys
from distutils.core import setup
import os

mainscript = 'src/AnnotatorItaloRom.py'

if sys.platform == 'darwin':
    import py2app
    
    extra_options = dict(
        setup_requires=['py2app'],
        app=[mainscript],
        # Cross-platform applications generally expect sys.argv to
        # be used for opening files.
        options=dict(py2app=dict(argv_emulation=True)),
    )
elif sys.platform == 'win32':
    from distutils.core import setup
    import GUI.py2exe
    import py2exe
    
    mfcdir = "C:\Python27\Lib\site-packages\pythonwin\\"
    mfcfiles = [os.path.join(mfcdir, i) for i in ["mfc90.dll", "mfc90u.dll", "mfcm90.dll", "mfcm90u.dll", "Microsoft.VC90.MFC.manifest"]]
    data_files = [("Microsoft.VC90.MFC", mfcfiles)]
    
    extra_options = dict(
        setup_requires=['py2exe'],
        windows = [mainscript],
        options = {'py2exe': {'bundle_files': 3,  'dll_excludes': [ "mswsock.dll", "powrprof.dll" ]}},
        data_files = data_files
    )
else:    
     extra_options = dict(
         # Normally unix-like platforms will use "setup.py install"
         # and install the main script as such
         scripts=[mainscript],
     )

setup(
    name="AnnotatorItaloRom",
    **extra_options
)