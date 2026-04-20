from __future__ import annotations

import shutil
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path

try:
    import pygame  # type: ignore[import]
except ImportError:  # pragma: no cover
    pygame = None  # type: ignore[assignment]


@dataclass(frozen=True)
class AdhanTrack:
    path: Path
    title: str

    def exists(self) -> bool:
        return self.path.exists()


class AdhanAudioService:
    """Play bundled Fajr and regular adhan audio when a salah begins."""

    def __init__(self, *, volume: float = 1.0) -> None:
        self.volume = max(0.0, min(volume, 1.0))
        self._lock = threading.Lock()
        self._mixer_ready = False
        self._external_process: subprocess.Popen[str] | None = None
        media_dir = Path(__file__).resolve().parents[1] / "media"
        self._fajr_track = AdhanTrack(media_dir / "fajr_adhan.mp3", "Fajr Adhan")
        self._regular_track = AdhanTrack(media_dir / "normal_adhan.mp3", "Normal Adhan")

    def is_available(self) -> bool:
        return self._fajr_track.exists() and self._regular_track.exists()

    def play_for_salah(self, salah_name: str) -> bool:
        if not self.is_available():
            return False
        track = self._fajr_track if salah_name.lower() == "fajr" else self._regular_track
        if self._play_with_pygame(track):
            return True
        return self._play_with_external_backend(track)

    def stop(self) -> None:
        with self._lock:
            if pygame is not None and self._mixer_ready:
                pygame.mixer.music.stop()
            if self._external_process is not None and self._external_process.poll() is None:
                self._external_process.terminate()
            self._external_process = None

    def is_playing(self) -> bool:
        pygame_busy = bool(pygame.mixer.music.get_busy()) if pygame is not None and self._mixer_ready else False
        process_busy = self._external_process is not None and self._external_process.poll() is None
        return pygame_busy or process_busy

    def _play_with_pygame(self, track: AdhanTrack) -> bool:
        if pygame is None:
            return False
        try:
            self._ensure_mixer()
            with self._lock:
                pygame.mixer.music.load(str(track.path))
                pygame.mixer.music.play()
            return True
        except Exception:
            return False

    def _play_with_external_backend(self, track: AdhanTrack) -> bool:
        commands = [
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(track.path)],
            ["mpg123", "-q", str(track.path)],
            ["cvlc", "--play-and-exit", "--quiet", str(track.path)],
        ]
        for command in commands:
            if shutil.which(command[0]) is None:
                continue
            try:
                with self._lock:
                    self._external_process = subprocess.Popen(
                        command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        text=True,
                    )
                return True
            except Exception:
                continue
        return False

    def _ensure_mixer(self) -> None:
        if pygame is None or self._mixer_ready:
            return
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        self._mixer_ready = True
