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
        self._reminder_process: subprocess.Popen[str] | None = None
        media_dir = Path(__file__).resolve().parents[1] / "media"
        self._fajr_track = AdhanTrack(media_dir / "fajr_adhan.mp3", "Fajr Adhan")
        self._regular_track = AdhanTrack(media_dir / "normal_adhan.mp3", "Normal Adhan")
        self._beep_track = AdhanTrack(media_dir / "prayer_alert_beep.wav", "Prayer Alert Beep")
        self._reminder_track = AdhanTrack(media_dir / "reminder.mp3", "Prayer Reminder")
        self._beep_sound = None
        self._reminder_using_music = False

    def is_available(self) -> bool:
        return self._fajr_track.exists() and self._regular_track.exists()

    def play_for_salah(self, salah_name: str) -> bool:
        if not self.is_available():
            return False
        self.stop_prayer_reminder()
        track = self._fajr_track if salah_name.lower() == "fajr" else self._regular_track
        if self._play_with_pygame(track):
            return True
        return self._play_with_external_backend(track)

    def stop(self) -> None:
        self.stop_prayer_reminder()
        with self._lock:
            if pygame is not None and self._mixer_ready:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                self._mixer_ready = False
                self._beep_sound = None
                self._reminder_using_music = False
            if self._external_process is not None and self._external_process.poll() is None:
                self._external_process.terminate()
                try:
                    self._external_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._external_process.kill()
                    self._external_process.wait(timeout=2)
            self._external_process = None

    def is_playing(self) -> bool:
        pygame_busy = bool(pygame.mixer.music.get_busy()) if pygame is not None and self._mixer_ready else False
        process_busy = self._external_process is not None and self._external_process.poll() is None
        return pygame_busy or process_busy

    def play_soft_beep(self) -> bool:
        if not self._beep_track.exists() or pygame is None:
            return False
        try:
            self._ensure_mixer()
            with self._lock:
                if self._beep_sound is None:
                    self._beep_sound = pygame.mixer.Sound(str(self._beep_track.path))
                    self._beep_sound.set_volume(min(0.22, max(0.06, self.volume * 0.22)))
                self._beep_sound.play()
            return True
        except Exception:
            return False

    def start_prayer_reminder(self) -> bool:
        if not self._reminder_track.exists():
            return False

        if self._start_external_reminder_once():
            return True

        if pygame is not None:
            try:
                self._ensure_mixer()
                with self._lock:
                    if self._reminder_using_music and pygame.mixer.music.get_busy():
                        return True
                    pygame.mixer.music.load(str(self._reminder_track.path))
                    pygame.mixer.music.set_volume(min(0.35, max(0.10, self.volume * 0.35)))
                    pygame.mixer.music.play(loops=-1)
                    self._reminder_using_music = True
                return True
            except Exception:
                pass
        return False

    def _start_external_reminder_once(self) -> bool:
        commands = [
            ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(self._reminder_track.path)],
            ["mpg123", "-q", str(self._reminder_track.path)],
            ["cvlc", "--play-and-exit", "--quiet", str(self._reminder_track.path)],
        ]
        for command in commands:
            if shutil.which(command[0]) is None:
                continue
            try:
                with self._lock:
                    if self._reminder_process is not None and self._reminder_process.poll() is None:
                        return True
                    process = subprocess.Popen(
                        command,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        text=True,
                    )
                    if process.poll() is not None:
                        continue
                    self._reminder_process = process
                return True
            except Exception:
                continue
        return False

    def stop_prayer_reminder(self) -> None:
        with self._lock:
            if pygame is not None and self._mixer_ready and self._reminder_using_music:
                try:
                    pygame.mixer.music.stop()
                except Exception:
                    pass
                self._reminder_using_music = False
            if self._reminder_process is not None and self._reminder_process.poll() is None:
                self._reminder_process.terminate()
                try:
                    self._reminder_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._reminder_process.kill()
                    self._reminder_process.wait(timeout=2)
            self._reminder_process = None

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
