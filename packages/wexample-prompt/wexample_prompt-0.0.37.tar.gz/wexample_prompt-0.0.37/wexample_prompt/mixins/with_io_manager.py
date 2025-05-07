from typing import Optional

from wexample_prompt.common.io_manager import IoManager


class WithIoManager:
    _io: Optional[IoManager] = None

    def __init__(self, io: Optional[IoManager] = None) -> None:
        self._io = io

    @property
    def io(self) -> IoManager:
        return self._io

    @io.setter
    def io(self, manager: IoManager) -> None:
        """Set the IoManager instance."""
        self._io = manager

    def _init_io_manager(self):
        self._io = IoManager()
