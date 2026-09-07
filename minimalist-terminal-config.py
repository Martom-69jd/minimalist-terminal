#!/usr/bin/env python3
import os
import sys
import json
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Vte', '2.91')
from gi.repository import Gtk, Vte, GLib, Pango, Gdk

CONFIG_DIR = os.path.expanduser("~/.config/minimalist-terminal")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "font": "JetBrains Mono 11",
    "bg_color": "#1e1e2e",
    "fg_color": "#cdd6f4",
    "cursor_color": "#f38ba8",
    "opacity": 1.0,
    "padding": 12,
    "scrollback_lines": 10000
}

def load_config():
    if not os.path.exists(CONFIG_DIR):
        os.makedirs(CONFIG_DIR)
    
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        return DEFAULT_CONFIG
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            user_config = json.load(f)
            # Объединяем дефолтные настройки с пользовательскими
            config = DEFAULT_CONFIG.copy()
            config.update(user_config)
            return config
    except Exception as e:
        print(f"Ошибка чтения конфига, используются настройки по умолчанию: {e}")
        return DEFAULT_CONFIG

def hex_to_rgba(hex_str, alpha=1.0):
    hex_str = hex_str.lstrip('#')
    if len(hex_str) == 6:
        r = int(hex_str[0:2], 16) / 255.0
        g = int(hex_str[2:4], 16) / 255.0
        b = int(hex_str[4:6], 16) / 255.0
        return Gdk.RGBA(r, g, b, alpha)
    return Gdk.RGBA(0, 0, 0, alpha)

class MinimalistTerminal(Gtk.Window):
    def __init__(self, config):
        super().__init__(title="minimalist-terminal")
        self.set_default_size(800, 600)
        
        # Настройка прозрачности окна, если требуется
        if config["opacity"] < 1.0:
            screen = self.get_screen()
            visual = screen.get_rgba_visual()
            if visual and screen.is_composited():
                self.set_visual(visual)
                self.set_app_paintable(True)

        self.terminal = Vte.Terminal()
        
        # Применяем конфигурацию
        self.apply_config(config)
        
        # Отступы (Padding), как в современных терминалах
        padding = config.get("padding", 0)
        self.terminal.set_margin_top(padding)
        self.terminal.set_margin_bottom(padding)
        self.terminal.set_margin_left(padding)
        self.terminal.set_margin_right(padding)

        # Запуск оболочки (bash, zsh и т.д.)
        shell = os.environ.get("SHELL", "/bin/bash")
        self.terminal.spawn_async(
            Vte.PtyFlags.DEFAULT,
            os.environ.get("HOME", "/"),
            [shell],
            None,
            GLib.SpawnFlags.DEFAULT,
            None, None, -1, None,
            None
        )

        # Обработка событий
        self.terminal.connect("child-exited", Gtk.main_quit)
        self.connect("destroy", Gtk.main_quit)

        self.add(self.terminal)
        self.show_all()

    def apply_config(self, config):
        # Шрифты
        font_desc = Pango.FontDescription.from_string(config["font"])
        self.terminal.set_font(font_desc)

        # Цвета
        bg = hex_to_rgba(config["bg_color"], config["opacity"])
        fg = hex_to_rgba(config["fg_color"])
        cursor = hex_to_rgba(config["cursor_color"])

        self.terminal.set_color_background(bg)
        self.terminal.set_color_foreground(fg)
        self.terminal.set_color_cursor(cursor)
        
        # Буфер
        self.terminal.set_scrollback_lines(config["scrollback_lines"])

if __name__ == "__main__":
    config = load_config()
    win = MinimalistTerminal(config)
    Gtk.main()