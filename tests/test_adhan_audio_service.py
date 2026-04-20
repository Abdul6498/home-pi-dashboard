from __future__ import annotations

from homehub.services import adhan_audio_service as audio_module
from homehub.services.adhan_audio_service import AdhanAudioService


class _FakeMusic:
    def __init__(self) -> None:
        self.stopped = False

    def stop(self) -> None:
        self.stopped = True

    def get_busy(self) -> bool:
        return False


class _FakeMixer:
    def __init__(self) -> None:
        self.music = _FakeMusic()
        self.quit_called = False

    def quit(self) -> None:
        self.quit_called = True


class _FakePygame:
    def __init__(self) -> None:
        self.mixer = _FakeMixer()


class _FakeProcess:
    def __init__(self) -> None:
        self.terminated = False
        self.killed = False
        self.wait_calls = 0

    def poll(self) -> None:
        return None

    def terminate(self) -> None:
        self.terminated = True

    def wait(self, timeout: int | float | None = None) -> int:
        self.wait_calls += 1
        return 0

    def kill(self) -> None:
        self.killed = True


def test_stop_shuts_down_pygame_and_external_process(monkeypatch) -> None:
    fake_pygame = _FakePygame()
    monkeypatch.setattr(audio_module, "pygame", fake_pygame)

    service = AdhanAudioService()
    service._mixer_ready = True  # noqa: SLF001
    fake_process = _FakeProcess()
    service._external_process = fake_process  # noqa: SLF001

    service.stop()

    assert fake_pygame.mixer.music.stopped is True
    assert fake_pygame.mixer.quit_called is True
    assert service._mixer_ready is False  # noqa: SLF001
    assert fake_process.terminated is True
    assert fake_process.wait_calls == 1
    assert service._external_process is None  # noqa: SLF001
