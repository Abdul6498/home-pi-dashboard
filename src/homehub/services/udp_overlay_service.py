from __future__ import annotations

from dataclasses import dataclass
import json
import socket


@dataclass(frozen=True)
class OverlayFrameState:
    current_rakat: int
    completed_rakats: int
    progress_stage_key: str
    prayer_name: str
    fsm_state: str


class UdpOverlayService:
    _FSM_STAGE_MAP = {
        "QIYAM": "qiyam",
        "QIYAM_NEXT": "qiyam",
        "RUKU": "ruku",
        "QAUMA": "itidal",
        "SUJUD_1": "sajda_1",
        "JALSA": "jalsa",
        "SUJUD_2": "sajda_2",
        "TASHAHHUD": "taslim",
        "TASLIM": "taslim",
    }

    def __init__(self, *, enabled: bool, bind_host: str, port: int) -> None:
        self._enabled = enabled
        self._bind_host = bind_host
        self._port = port
        self._socket: socket.socket | None = None
        self._last_state: OverlayFrameState | None = None
        if self._enabled:
            self._socket = self._open_socket()

    def close(self) -> None:
        if self._socket is None:
            return
        try:
            self._socket.close()
        finally:
            self._socket = None

    def poll_latest(self) -> OverlayFrameState | None:
        if self._socket is None:
            return self._last_state

        while True:
            try:
                payload, _address = self._socket.recvfrom(65535)
            except BlockingIOError:
                break
            except OSError:
                self.close()
                break

            state = self._parse_packet(payload)
            if state is not None:
                self._last_state = state

        return self._last_state

    def _open_socket(self) -> socket.socket | None:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((self._bind_host, self._port))
            sock.setblocking(False)
            return sock
        except OSError:
            return None

    def _parse_packet(self, payload: bytes) -> OverlayFrameState | None:
        start = payload.find(b"{")
        end = payload.rfind(b"}")
        if start < 0 or end < start:
            return None

        try:
            message = json.loads(payload[start : end + 1].decode("utf-8", errors="ignore"))
        except json.JSONDecodeError:
            return None

        if not isinstance(message, dict):
            return None
        if message.get("event") != "overlay_frame":
            return None

        fsm_state = str(message.get("fsm_state", "")).strip().upper()
        stage_key = self._FSM_STAGE_MAP.get(fsm_state)
        if stage_key is None:
            return None

        try:
            current_rakat = int(message.get("current_rakat", 1))
        except (TypeError, ValueError):
            current_rakat = 1
        try:
            completed_rakats = int(message.get("completed_rakats", 0))
        except (TypeError, ValueError):
            completed_rakats = 0

        return OverlayFrameState(
            current_rakat=max(1, current_rakat),
            completed_rakats=max(0, completed_rakats),
            progress_stage_key=stage_key,
            prayer_name=str(message.get("prayer_name", "")).strip(),
            fsm_state=fsm_state,
        )
