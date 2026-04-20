from __future__ import annotations

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
        media_dir = Path(__file__).resolve().parents[1] / "media"
        self._fajr_track = AdhanTrack(media_dir / "fajr_adhan.mp3", "Fajr Adhan")
        self._regular_track = AdhanTrack(media_dir / "normal_adhan.mp3", "Normal Adhan")

    def is_available(self) -> bool:
        return (
            pygame is not None
            and self._fajr_track.exists()
            and self._regular_track.exists()
        )

    def play_for_salah(self, salah_name: str) -> bool:
        if not self.is_available():
            return False
        track = self._fajr_track if salah_name.lower() == "fajr" else self._regular_track
        self._ensure_mixer()
        with self._lock:
            pygame.mixer.music.load(str(track.path))
            pygame.mixer.music.play()
        return True

    def stop(self) -> None:
        if pygame is None or not self._mixer_ready:
            return
        with self._lock:
            pygame.mixer.music.stop()

    def is_playing(self) -> bool:
        if pygame is None or not self._mixer_ready:
            return False
        return bool(pygame.mixer.music.get_busy())

    def _ensure_mixer(self) -> None:
        if pygame is None or self._mixer_ready:
            return
        pygame.mixer.init()
        pygame.mixer.music.set_volume(self.volume)
        self._mixer_ready = True
