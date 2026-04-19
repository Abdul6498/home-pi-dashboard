from __future__ import annotations

import tkinter as tk

from homehub.ui.palette import DashboardPalette


class MetricPanel(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        palette: DashboardPalette,
        title: str,
        title_color: str,
        font_family: str,
    ) -> None:
        super().__init__(parent, bg=palette.panel_bg)
        self._palette = palette

        self.title_label = tk.Label(
            self,
            text=title,
            fg=title_color,
            bg=palette.panel_bg,
            font=(font_family, 14, "bold"),
        )
        self.humidity_label = tk.Label(
            self,
            text="HUM --%",
            fg=palette.text_primary,
            bg=palette.panel_bg,
            font=(font_family, 30, "bold"),
        )
        self.temp_label = tk.Label(
            self,
            text="-- C",
            fg=title_color,
            bg=palette.panel_bg,
            font=(font_family, 24, "bold"),
        )

        self.title_label.pack(anchor="w")
        self.humidity_label.pack(anchor="w", pady=(8, 4))
        self.temp_label.pack(anchor="w")

    def set_values(self, humidity_pct: int, temp_c: int) -> None:
        self.humidity_label.config(text=f"HUM {humidity_pct}%")
        self.temp_label.config(text=f"{temp_c} C")


class ForecastCard(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        palette: DashboardPalette,
        font_family: str,
    ) -> None:
        super().__init__(
            parent,
            bg=palette.card_bg,
            highlightbackground=palette.divider,
            highlightthickness=1,
        )

        self.day_label = tk.Label(
            self,
            text="---",
            fg=palette.text_muted,
            bg=palette.card_bg,
            font=(font_family, 14, "bold"),
        )
        self.icon_label = tk.Label(
            self,
            text="☁",
            fg=palette.neon_cyan,
            bg=palette.card_bg,
            font=(font_family, 32),
        )
        self.high_label = tk.Label(
            self,
            text="HI --C",
            fg=palette.neon_coral,
            bg=palette.card_bg,
            font=(font_family, 12, "bold"),
        )
        self.low_label = tk.Label(
            self,
            text="LO --C",
            fg=palette.neon_cyan,
            bg=palette.card_bg,
            font=(font_family, 12, "bold"),
        )

        self.day_label.pack(pady=(10, 4))
        self.icon_label.pack(pady=(0, 4))
        self.high_label.pack()
        self.low_label.pack(pady=(0, 10))

    def set_values(
        self,
        day_label: str,
        icon: str,
        high_c: int,
        low_c: int,
        icon_color: str | None = None,
    ) -> None:
        self.day_label.config(text=day_label)
        if icon_color:
            self.icon_label.config(text=icon, fg=icon_color)
        else:
            self.icon_label.config(text=icon)
        self.high_label.config(text=f"HI {high_c}C")
        self.low_label.config(text=f"LO {low_c}C")


class InfoBadge(tk.Frame):
    def __init__(
        self,
        parent: tk.Misc,
        palette: DashboardPalette,
        title: str,
        value_color: str,
        font_family: str,
    ) -> None:
        super().__init__(parent, bg=palette.panel_bg)
        self.title_label = tk.Label(
            self,
            text=title,
            fg=palette.text_muted,
            bg=palette.panel_bg,
            font=(font_family, 10, "bold"),
        )
        self.value_label = tk.Label(
            self,
            text="--",
            fg=value_color,
            bg=palette.panel_bg,
            font=(font_family, 22, "bold"),
        )
        self.title_label.pack()
        self.value_label.pack()

    def set_value(self, value: str) -> None:
        self.value_label.config(text=value)
