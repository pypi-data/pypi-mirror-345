# Evolis SDK for Python
#
# THIS CODE AND INFORMATION IS PROVIDED "AS IS" WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND/OR FITNESS FOR A
# PARTICULAR PURPOSE.

r'''
# What is Evolis SDK for Python ?

**Evolis SDK for Python** is a wrapper for the underlying C library called
**libevolis**. Be sure to have that library in your path in order to have the
present wrapper to work.

# Quickstart

A connection to the printer is opened with the help of `evolis.Connection`
object. To print, you will have to use `evolis.PrintSession` object.

Here is a very simple example showing how to open a context to your printer
and print an image to your card. Explore [examples](#examples) and API of
`evolis.Connection` and `evolis.PrintSession` to go further.

```python
co = evolis.Connection("Evolis Primacy 2")
if co.is_open():
    ps = evolis.PrintSession(co)
    ps.set_image(evolis.CardFace.FRONT, "<PATH-TO-YOUR-BITMAP-FILE>")
    ps.print()
```

# Examples

## send-command.py

```python
.. include:: ../examples/send-command.py
```

## print-KO.py

```python
.. include:: ../examples/print-KO.py
```

## get-status.py

```python
.. include:: ../examples/get-status.py
```

## kc-max.py

```python
.. include:: ../examples/kc-max.py
```

## get-info.py

```python
.. include:: ../examples/get-info.py
```

## bezel.py

```python
.. include:: ../examples/bezel.py
```

## print-YMCKO.py

```python
.. include:: ../examples/print-YMCKO.py
```

## scan.py

```python
.. include:: ../examples/scan.py
```

## mag-encoding.py

```python
.. include:: ../examples/mag-encoding.py
```

## workflow.py

```python
.. include:: ../examples/workflow.py
```

## print-RW.py

```python
.. include:: ../examples/print-RW.py
```

## quantum

```python
.. include:: ../examples/quantum
```

'''

from .BezelBehavior import BezelBehavior
from .CardFace import CardFace
from .CardPos import CardPos
from .CleaningInfo import CleaningInfo
from .Connection import Connection
from .Device import Device
from .Dpi import Dpi
from .ErrorManagement import ErrorManagement
from .ErrorManagementLocker import ErrorManagementLocker
from .Evolis import Evolis
from .Feeder import Feeder
from .InputTray import InputTray
from .LaminatorFilmInfo import LaminatorFilmInfo
from .LaminatorFilmType import LaminatorFilmType
from .LaminatorIndex import LaminatorIndex
from .LaminatorInfo import LaminatorInfo
from .LaminatorMode import LaminatorMode
from .LogLevel import LogLevel
from .MagCoercivity import MagCoercivity
from .MagFormat import MagFormat
from .MagSession import MagSession
from .Mark import Mark
from .Model import Model
from .OpenMode import OpenMode
from .OutputTray import OutputTray
from .PrintSession import PrintSession
from .PrinterInfo import PrinterInfo
from .ReturnCode import ReturnCode
from .RibbonInfo import RibbonInfo
from .RibbonType import RibbonType
from .RwCardType import RwCardType
from .ScanImage import ScanImage
from .ScanOption import ScanOption
from .ScanSession import ScanSession
from .Service import Service
from .ServiceAction import ServiceAction
from .SettingKey import SettingKey
from .State import State
from .Status import Status
from .Type import Type

import struct
import platform

def __get_platform():
    p = platform.system().lower()
    s = struct.calcsize("P") * 8
    machine = platform.machine()

    if p == "windows":
        return p + ("-x86" if s == 32 else "-x86_64")
    if p == "darwin":
        return "macos"
    if machine.__contains__("arm"):
        return p + "-armv7-lts"
    return p + "-" + machine

def __get_libname():
    p = platform.system().lower()

    if p == "windows":
        return "evolis.dll"
    if p == "darwin":
        return "libevolis.dylib"
    return "libevolis.so"

if not Evolis.wrapper:
    from os import path
    currdir = path.dirname(__file__)
    libname = __get_libname()
    libdir = path.join("lib", __get_platform())

    lib = path.join(currdir, libdir, libname)
    if not path.exists(lib):
        lib = path.join(currdir, libname)
    Evolis.set_library_path(lib)
