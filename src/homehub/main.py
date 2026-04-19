import tkinter as tk

from homehub.config import load_settings
from homehub.modules.clock import ClockModule
from homehub.modules.gps import GPSModule
from homehub.modules.weather import WeatherModule
from homehub.services.gps_service import GPSService
from homehub.services.weather_service import WeatherService
from homehub.ui.theme import THEMES


class DashboardApp:
    def __init__(self) -> None:
        self.settings = load_settings()
        self.theme = THEMES.get(self.settings.ui_theme, THEMES["aurora"])

        self.root = tk.Tk()
        self.root.title("Home Pi Dashboard")
        self.root.geometry("1024x600")
        self.root.configure(bg=self.theme["background"])

        self.clock = ClockModule()
        self.weather = WeatherModule(WeatherService(self.settings.weather_api_key))
        self.gps = GPSModule(
            GPSService(self.settings.default_lat, self.settings.default_lon)
        )

        self.time_label = tk.Label(
            self.root,
            text="",
            fg=self.theme["primary_text"],
            bg=self.theme["background"],
            font=("Helvetica", 56, "bold"),
        )
        self.date_label = tk.Label(
            self.root,
            text="",
            fg=self.theme["accent_text"],
            bg=self.theme["background"],
            font=("Helvetica", 20),
        )
        self.weather_label = tk.Label(
            self.root,
            text="",
            fg=self.theme["primary_text"],
            bg=self.theme["background"],
            font=("Helvetica", 18),
        )
        self.location_label = tk.Label(
            self.root,
            text="",
            fg=self.theme["primary_text"],
            bg=self.theme["background"],
            font=("Helvetica", 14),
        )

        self.time_label.pack(pady=(80, 10))
        self.date_label.pack(pady=(0, 30))
        self.weather_label.pack(pady=(0, 10))
        self.location_label.pack(pady=(0, 10))

    def refresh(self) -> None:
        clock_data = self.clock.update()
        weather_data = self.weather.update()
        gps_data = self.gps.update()

        self.time_label.config(text=clock_data.time_text)
        self.date_label.config(text=clock_data.date_text)
        self.weather_label.config(
            text=f"{weather_data.summary}  |  {weather_data.temperature_c}C"
        )
        self.location_label.config(
            text=f"{gps_data.location_name} ({gps_data.lat:.4f}, {gps_data.lon:.4f})"
        )

        self.root.after(1000, self.refresh)

    def run(self) -> None:
        self.refresh()
        self.root.mainloop()


if __name__ == "__main__":
    DashboardApp().run()
