#!/usr/bin/env python3

import asyncio, json, threading, websockets, os
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
from gi.repository import Gtk, GLib, Gdk

WS_URL = 'ws://127.0.0.1:23560/poll'

class LyricFetcher:
    def __init__(self):
        self._loop = asyncio.new_event_loop()
        self._ws = None
        self.current = ""
        self._running = True
        t = threading.Thread(target=self._run, daemon=True)
        t.start()

    def _run(self):
        asyncio.set_event_loop(self._loop)
        self._loop.run_until_complete(self._poll_loop())

    async def _poll_loop(self):
        while self._running:
            try:
                async with websockets.connect(WS_URL, open_timeout=0.5) as ws:
                    while self._running:
                        await ws.send(json.dumps({}))
                        msg = await asyncio.wait_for(ws.recv(), timeout=0.5)
                        d = json.loads(msg)
                        status = d.get('playback_status', '')
                        lyrics = d.get('lyrics')
                        if status != 'playing' or not lyrics:
                            self.current = ''
                        else:
                            line = (lyrics.get('current_lyric', '') or '').split('|')[0].strip()
                            self.current = line
                        await asyncio.sleep(0.3)
            except:
                await asyncio.sleep(1)

    def stop(self):
        self._running = False

fetcher = LyricFetcher()

class LyricWindow:
    def __init__(self):
        self.win = Gtk.Window(type=Gtk.WindowType.POPUP)
        self.win.set_decorated(False)
        self.win.set_resizable(False)
        self.win.set_skip_taskbar_hint(True)
        self.win.set_keep_above(True)
        self.win.stick()
        self.win.set_accept_focus(False)
        self.win.set_type_hint(Gdk.WindowTypeHint.NOTIFICATION)

        display = Gdk.Display.get_default()
        monitor = display.get_primary_monitor() if display else None
        geo = monitor.get_geometry() if monitor else None
        scr_w = geo.width if geo else 1366
        scr_h = geo.height if geo else 768
        win_w = 600
        win_h = 28
        pos_x = (scr_w - win_w) // 2
        pos_y = 34

        css = b"""
        window {
            background: #1e1e2e;
            border-radius: 14px;
        }
        label {
            font-family: JetBrainsMono Nerd Font, monospace;
            font-size: 11px;
            color: #89b4fa;
            padding: 2px 16px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(
            Gdk.Screen.get_default(), provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

        self.label = Gtk.Label()
        self.label.set_text("")
        self.win.add(self.label)
        self.win.set_default_size(win_w, -1)
        self.win.move(pos_x, pos_y)

        self.current = ""
        GLib.timeout_add(200, self.update)

    def update(self):
        t = fetcher.current
        if t != self.current:
            self.current = t
            if t:
                self.label.set_text(t)
                self.win.show_all()
                self.win.set_keep_above(True)
            else:
                self.win.hide()
        return True

    def run(self):
        try:
            Gtk.main()
        finally:
            fetcher.stop()

if __name__ == "__main__":
    LyricWindow().run()
