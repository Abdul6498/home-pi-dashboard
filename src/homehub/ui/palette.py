from dataclasses import dataclass


@dataclass(frozen=True)
class DashboardPalette:
    window_bg: str
    panel_bg: str
    panel_gloss: str
    card_bg: str
    divider: str
    text_primary: str
    text_muted: str
    neon_lime: str
    neon_coral: str
    neon_cyan: str


THEME_PALETTES = {
    "crystal": DashboardPalette(
        window_bg="#d8e9f8",
        panel_bg="#0f1a2a",
        panel_gloss="#1a2f4a",
        card_bg="#132238",
        divider="#46638a",
        text_primary="#eaf5ff",
        text_muted="#b6cce6",
        neon_lime="#e7f55f",
        neon_coral="#ffab8b",
        neon_cyan="#62ddff",
    ),
    "aurora": DashboardPalette(
        window_bg="#1f2329",
        panel_bg="#12171f",
        panel_gloss="#1a202b",
        card_bg="#0f141c",
        divider="#3a4150",
        text_primary="#e9eef6",
        text_muted="#b9c2cf",
        neon_lime="#dce84a",
        neon_coral="#ff9b84",
        neon_cyan="#36d8ff",
    ),
    "sunrise": DashboardPalette(
        window_bg="#2a1f24",
        panel_bg="#1f161b",
        panel_gloss="#2b1b24",
        card_bg="#1a1218",
        divider="#4b3340",
        text_primary="#fff1e8",
        text_muted="#e2c7b6",
        neon_lime="#f4ea58",
        neon_coral="#ff9a76",
        neon_cyan="#54d8ff",
    ),
}


def get_palette(theme_name: str) -> DashboardPalette:
    return THEME_PALETTES.get(theme_name, THEME_PALETTES["aurora"])
