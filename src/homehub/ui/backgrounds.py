from __future__ import annotations

from pathlib import Path

try:
    from PIL import Image
except ModuleNotFoundError:  # pragma: no cover - optional dependency for image assets
    Image = None


def prepare_background_asset(
    *,
    source_path: Path,
    cache_dir: Path,
    width: int,
    height: int,
) -> Path | None:
    """Create a Pi-friendly wallpaper derivative sized for the display."""
    if Image is None:
        return None
    if not source_path.exists():
        return None

    cache_dir.mkdir(parents=True, exist_ok=True)
    target_name = f"{source_path.stem}_{width}x{height}.jpg"
    target_path = cache_dir / target_name

    if target_path.exists() and target_path.stat().st_mtime >= source_path.stat().st_mtime:
        return target_path

    try:
        with Image.open(source_path) as source:
            fitted = _cover_resize(source, width=width, height=height)
            fitted.save(target_path, format="JPEG", quality=82, optimize=True)
    except OSError:
        return None

    return target_path


def bundled_background_path(filename: str) -> Path:
    repo_root = Path(__file__).resolve().parents[3]
    return repo_root / "assets" / "seasonal" / filename


def resolve_background_path(image_name: str) -> Path | None:
    if not image_name.strip():
        return None

    candidate = Path(image_name).expanduser()
    if candidate.is_absolute():
        return candidate if candidate.exists() else None

    repo_root = Path(__file__).resolve().parents[3]
    search_paths = [
        repo_root / image_name,
        repo_root / "assets" / image_name,
        repo_root / "assets" / "seasonal" / image_name,
    ]
    for path in search_paths:
        if path.exists():
            return path
    return None


def _cover_resize(source: Image.Image, width: int, height: int) -> Image.Image:
    src_w, src_h = source.size
    scale = max(width / src_w, height / src_h)
    resized = source.resize(
        (int(src_w * scale), int(src_h * scale)),
        Image.Resampling.LANCZOS,
    )

    left = (resized.width - width) // 2
    top = (resized.height - height) // 2
    return resized.crop((left, top, left + width, top + height))
