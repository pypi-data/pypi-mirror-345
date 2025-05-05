from __future__ import annotations
from pathlib import Path
import threading
import subprocess
from sys import argv
from . import geom, geom2d


from .bindings import (
    __doc__,
    Visualizer as Visualizer_internal,
    Canvas,
    Scene,
    # geom,
    spawn_window as spawn_window_internal,
)


def _executable_path():
    executable_path = Path(__file__).parent / "slamd_window"

    if not executable_path.exists():
        print("Executable path not found! Assuming dev install, passing None")
        executable_path = None

    return executable_path


class Visualizer:
    def __init__(self, name: str, spawn=True, port: int = 5555) -> None:
        self._impl = Visualizer_internal(name, port)

        if spawn:
            spawn_window(port)

    def hang_forever(self):
        threading.Event().wait()

    def add_scene(self, name: str, scene: Scene) -> None:
        return self._impl.add_scene(name, scene)

    def add_canvas(self, name: str, canvas: Canvas) -> None:
        return self._impl.add_canvas(name, canvas)

    def canvas(self, name: str) -> Canvas:
        return self._impl.canvas(name)

    def scene(self, name: str) -> Scene:
        return self._impl.scene(name)

    def delete_scene(self, name: str) -> None:
        self._impl.delete_scene(name)

    def delete_canvas(self, name: str) -> None:
        self._impl.delete_canvas(name)


def spawn_window(port: int = 5555) -> None:
    executable_path = _executable_path()

    spawn_window_internal(
        port,
        str(executable_path) if executable_path is not None else None,
    )


def _window_cli():
    exe_path = _executable_path()

    if exe_path is None:
        raise RuntimeError("Can't find exe path")

    subprocess.run([exe_path, *argv[1:]])


__all__ = [
    "__doc__",
    "Visualizer",
    "Canvas",
    "Scene",
    "geom",
    "geom2d",
    "spawn_window",
    "_window_cli",
]
