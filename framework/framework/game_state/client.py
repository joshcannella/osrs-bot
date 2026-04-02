"""
GameStateClient — reads game state from a memory-mapped file written by
the RuneLite "State Export" plugin.

IPC protocol: The plugin writes a 64KB memory-mapped file at
~/.runelite/osrsbot_state.dat with a lock-free sequence counter:

    [0..3]         sequence_before  (int32 LE)
    [4..7]         data_length      (int32 LE)
    [8..N]         JSON payload     (UTF-8)
    [65532..65535] sequence_after   (int32 LE)

Reader checks sequence_before == sequence_after to detect torn writes.
If they differ, the read is discarded (plugin was mid-write).
"""

import json
import logging
import mmap
import os
import struct

logger = logging.getLogger(__name__)

BUFFER_SIZE = 65536
SEQ_BEFORE_OFFSET = 0
DATA_LEN_OFFSET = 4
DATA_START_OFFSET = 8
SEQ_AFTER_OFFSET = BUFFER_SIZE - 4


class GameStateClient:
    def __init__(self, path: str | None = None):
        if path is None:
            path = os.path.join(
                os.environ.get("USERPROFILE", os.path.expanduser("~")),
                ".runelite",
                "osrsbot_state.dat",
            )
        self._path = path
        self._fh = None
        self._mm = None

    def _ensure_open(self) -> bool:
        """Open the mmap if not already open. Returns False if file doesn't exist."""
        if self._mm is not None:
            return True
        if not os.path.exists(self._path):
            return False
        try:
            self._fh = open(self._path, "r+b")
            self._mm = mmap.mmap(self._fh.fileno(), BUFFER_SIZE, access=mmap.ACCESS_READ)
            return True
        except Exception as e:
            logger.debug("Failed to open mmap at %s: %s", self._path, e)
            self._fh = None
            self._mm = None
            return False

    def _read_snapshot(self) -> dict | None:
        """
        Read the current game state snapshot from shared memory.

        Returns None if: file doesn't exist, plugin hasn't written yet,
        torn write detected, or JSON parse fails.
        """
        if not self._ensure_open():
            return None

        try:
            seq_before = struct.unpack_from("<i", self._mm, SEQ_BEFORE_OFFSET)[0]
            if seq_before == 0:
                # Plugin not active or shut down — close so we can re-open
                # if the plugin restarts with a new file
                self.close()
                return None

            data_len = struct.unpack_from("<i", self._mm, DATA_LEN_OFFSET)[0]
            if data_len <= 0 or data_len > BUFFER_SIZE - 12:
                return None

            payload = self._mm[DATA_START_OFFSET:DATA_START_OFFSET + data_len]
            seq_after = struct.unpack_from("<i", self._mm, SEQ_AFTER_OFFSET)[0]

            if seq_before != seq_after:
                return None  # Torn write — plugin was mid-update

            return json.loads(payload)
        except Exception as e:
            logger.debug("GameStateClient read failed: %s", e)
            return None

    def is_available(self) -> bool:
        """Check if the plugin is running and writing valid data."""
        return self._read_snapshot() is not None

    def get_player(self) -> dict | None:
        s = self._read_snapshot()
        return s.get("player") if s else None

    def get_inventory(self) -> list[dict]:
        s = self._read_snapshot()
        return s.get("inventory", []) if s else []

    def get_npcs(self) -> list[dict]:
        s = self._read_snapshot()
        return s.get("npcs", []) if s else []

    def get_objects(self) -> list[dict]:
        s = self._read_snapshot()
        return s.get("objects", []) if s else []

    def get_stats(self) -> dict | None:
        s = self._read_snapshot()
        return s.get("stats") if s else None

    def get_ground_items(self) -> list[dict]:
        s = self._read_snapshot()
        return s.get("ground_items", []) if s else []

    def close(self):
        """Release mmap and file handle."""
        if self._mm:
            try:
                self._mm.close()
            except Exception:
                pass
            self._mm = None
        if self._fh:
            try:
                self._fh.close()
            except Exception:
                pass
            self._fh = None
