from __future__ import annotations
from f3d.pyf3d import Camera
from f3d.pyf3d import CameraState
from f3d.pyf3d import Engine
from f3d.pyf3d import Image
from f3d.pyf3d import InteractionBind
from f3d.pyf3d import Interactor
from f3d.pyf3d import LibInformation
from f3d.pyf3d import Log
from f3d.pyf3d import Mesh
from f3d.pyf3d import Options
from f3d.pyf3d import ReaderInformation
from f3d.pyf3d import Scene
from f3d.pyf3d import Utils
from f3d.pyf3d import Window
import os as os
import pathlib
from pathlib import Path
import re as re
import sys as sys
import warnings as warnings
from . import pyf3d
__all__ = ['Camera', 'CameraState', 'Engine', 'F3D_ABSOLUTE_DLLS', 'F3D_RELATIVE_DLLS', 'Image', 'InteractionBind', 'Interactor', 'LibInformation', 'Log', 'Mesh', 'Options', 'Path', 'ReaderInformation', 'Scene', 'Utils', 'Window', 'abs_path', 'os', 'pyf3d', 're', 'root', 'sys', 'warnings']
def _add_deprecation_warnings():
    ...
def _deprecated_decorator(f, reason):
    ...
def _f3d_options_update(self, arg: typing.Union[typing.Mapping[str, typing.Any], typing.Iterable[tuple[str, typing.Any]]]) -> None:
    ...
F3D_ABSOLUTE_DLLS: list = ['D:/a/f3d-superbuild/f3d-superbuild/fsbb/install/bin', 'D:/a/f3d-superbuild/f3d-superbuild/fsbb/install/lib', 'C:/Users/runneradmin/AppData/Local/Temp/tmpt34mbf_r/build/bin']
F3D_RELATIVE_DLLS: list = list()
__version__: str = '3.1.0'
abs_path: str = 'C:/Users/runneradmin/AppData/Local/Temp/tmpt34mbf_r/build/bin'
root: pathlib.WindowsPath  # value = WindowsPath('C:/Users/runneradmin/AppData/Local/Temp/tmpt34mbf_r/build/f3d')
