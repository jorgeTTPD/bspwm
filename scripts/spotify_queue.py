#!/usr/bin/env python3
"""
spotify_queue.py — Cola y playlists de Spotify para rofi (Super+S).

Usa las credenciales de ~/csv-to-spotify/.env (la app que ya funciona) y el
token de tus scripts de upload. Sin depender de spt ni de client.yml.

Modos:
  spotify_queue.py               cola de reproducción en rofi
  spotify_queue.py --playlists   lista tus playlists reales y reproduce
  spotify_queue.py --list        cola en texto plano (debug)
  spotify_queue.py --auth        (re)autorizar una vez (navegador + pegar código)
  spotify_queue.py --help
"""
import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ENV_FILE = os.path.expanduser("~/csv-to-spotify/.env")
CACHE_DIR = os.path.expanduser("~/.cache/spotify-queue")
TOKEN_FILE = os.path.join(CACHE_DIR, "token.json")
SEED_FILES = [
    os.path.expanduser("~/Escritorio/mis playlist spotify/.spotify_token.json"),
    os.path.expanduser("~/Escritorio/Manager_Spotify/.spotify_token.json"),
]
REDIRECT = "https://www.google.com/"  # redirect registrado de la app
SCOPES = ("user-read-playback-state user-read-currently-playing "
          "user-modify-playback-state playlist-read-private")
API = "https://api.spotify.com/v1"
ROFI_THEME = os.path.expanduser("~/.config/rofi/list.rasi")


def log(msg):
    print(msg, file=sys.stderr)


def show_error(msg):
    subprocess.run(["rofi", "-e", msg, "-theme", ROFI_THEME], check=False)


def notify(title, msg):
    subprocess.run(["notify-send", title, msg], check=False)


# ---------- auth ----------

def load_env():
    env = {}
    with open(ENV_FILE) as f:
        for line in f:
            line = line.strip()
            if line and "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    return env


def token_request(env, params):
    form = urllib.parse.urlencode(params).encode()
    req = urllib.request.Request("https://accounts.spotify.com/api/token",
                                 data=form, method="POST")
    req.add_header("Content-Type", "application/x-www-form-urlencoded")
    req.add_header("Authorization", "Basic " + base64.b64encode(
        "{}:{}".format(env["CLIENT_ID"], env["CLIENT_SECRET"]).encode()).decode())
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def save_token(data):
    os.makedirs(CACHE_DIR, mode=0o700, exist_ok=True)
    fd = os.open(TOKEN_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(data, f)


def seed_token():
    """Copia el refresh token del proyecto de uploads (ya autorizado)."""
    if os.path.exists(TOKEN_FILE):
        return
    for path in SEED_FILES:
        try:
            t = json.load(open(path))
            if t.get("refresh_token"):
                save_token(t)
                log("Token semilla copiado de {}".format(path))
                return
        except Exception:
            continue
    log("Sin token semilla: ejecuta 'spotify_queue.py --auth' una vez.")


def refresh_access(env):
    t = json.load(open(TOKEN_FILE))
    data = token_request(env, {
        "grant_type": "refresh_token",
        "refresh_token": t["refresh_token"],
    })
    t["access_token"] = data["access_token"]
    if "refresh_token" in data:
        t["refresh_token"] = data["refresh_token"]
    save_token(t)
    return t["access_token"]


def authorize(env):
    """Flujo OAuth con redirect https://www.google.com/ (el registrado):
    abres el navegador, autorizas, te lleva a Google con ?code=... y pegas
    el código en rofi."""
    auth_url = "https://accounts.spotify.com/authorize?" + urllib.parse.urlencode({
        "client_id": env["CLIENT_ID"],
        "response_type": "code",
        "redirect_uri": REDIRECT,
        "scope": SCOPES,
        "show_dialog": "true",
    })
    subprocess.Popen(["xdg-open", auth_url])
    code = subprocess.run(
        ["rofi", "-dmenu", "-p", "Pega el código de Spotify",
         "-theme", ROFI_THEME,
         "-mesg", "Autoriza en el navegador; te llevará a Google con ?code=... "
                  "— copia ese código y pégalo aquí (Ctrl+V)"],
        capture_output=True, text=True).stdout.strip()
    if not code:
        raise RuntimeError("No se pegó ningún código. Cancelado.")
    data = token_request(env, {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT,
    })
    save_token(data)
    return data["access_token"]


def get_token(env):
    seed_token()
    if not os.path.exists(TOKEN_FILE):
        return authorize(env)
    try:
        return refresh_access(env)
    except Exception:
        return authorize(env)


# ---------- API ----------

def api(method, url, token=None, body=None):
    req = urllib.request.Request(url, method=method)
    req.add_header("Accept", "application/json")
    if body is not None:
        req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    data = json.dumps(body).encode() if body is not None else None
    try:
        with urllib.request.urlopen(req, data=data, timeout=15) as resp:
            raw = resp.read()
            return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            return e.code, json.loads(raw) if raw else {}
        except Exception:
            return e.code, {}


def active_device(token):
    s, d = api("GET", "{}/me/player/devices".format(API), token)
    if s != 200:
        return None
    devs = d.get("devices") or []
    for dev in devs:
        if dev.get("is_active"):
            return dev.get("id")
    return devs[0].get("id") if devs else None


def play(token, body):
    dev = active_device(token)
    url = "{}/me/player/play".format(API)
    if dev:
        url += "?device_id=" + urllib.parse.quote(dev)
    s, _ = api("PUT", url, token, body)
    return s


def feedback(status, what):
    if status in (200, 202, 204):
        notify("🎵 Música", what)
    elif status == 403:
        notify("🎵 Música", "Falta permiso: corre 'spotify_queue.py --auth' una vez")
    elif status == 404:
        notify("🎵 Música", "No hay dispositivo activo (inicia ncspot o spotifyd)")
    else:
        notify("🎵 Música", "Error HTTP {}".format(status))


# ---------- rofi ----------

def rofi_pick(lines, metas, prompt, mesg):
    """Menú rofi: devuelve la meta de la fila elegida. Se usa -format i
    (índice) y se mapea por posición, porque -format d (meta) no funciona
    en rofi 2.0.0 (el rewrite)."""
    # Limpia rofi previos: un pidfile stale (por un rofi matado con
    # timeout/SIGTERM) bloquea el lanzamiento del siguiente menú.
    subprocess.run(["pkill", "-x", "rofi"], capture_output=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    tmp = os.path.join(CACHE_DIR, "menu.txt")
    with open(tmp, "w") as f:
        for line in lines:
            f.write(line + "\n")
    proc = subprocess.run(
        ["rofi", "-dmenu", "-i", "-format", "i", "-p", prompt,
         "-theme", ROFI_THEME, "-mesg", mesg],
        stdin=open(tmp), capture_output=True, text=True)
    sel = proc.stdout.strip()
    try:
        idx = int(sel)
        return metas[idx] if 0 <= idx < len(metas) else ""
    except (ValueError, IndexError):
        return ""


def fmt_dur(ms):
    s = max(0, int(ms) // 1000)
    return "{}:{:02d}".format(s // 60, s % 60)


def track_line(t, now=False, n=0):
    name = t.get("name", "?")
    artists = ", ".join(a.get("name", "?") for a in t.get("artists", []))
    dur = fmt_dur(t.get("duration_ms", 0))
    prefix = "▶ " if now else "{}.".format(n)
    return "{} {} — {}  [{}]".format(prefix, name, artists, dur)


# ---------- detección de playback ----------

def detect_playback(token):
    """Devuelve ('api', nombre) si Spotify ve playback activo (spotifyd/Connect),
    ('mpris', player) si suena un reproductor local tipo ncspot,
    ('none', None) si no suena nada."""
    s, d = api("GET", "{}/me/player/currently-playing".format(API), token)
    if s == 200 and d.get("item"):
        dev = (d.get("device") or {}).get("name") or "Connect"
        return "api", dev
    try:
        players = subprocess.run(["playerctl", "-l"], capture_output=True,
                                 text=True, timeout=5).stdout.split()
    except Exception:
        players = []
    for p in players:
        try:
            st = subprocess.run(["playerctl", "-p", p, "status"], capture_output=True,
                                text=True, timeout=5).stdout.strip()
            if st == "Playing":
                return "mpris", p
        except Exception:
            continue
    return "none", None


def pause_local_players():
    """Pausa reproductores MPRIS locales (p.ej. ncspot) que estén sonando,
    SIN pausar spotifyd (es el dispositivo donde reproduce la API)."""
    try:
        players = subprocess.run(["playerctl", "-l"], capture_output=True,
                                 text=True, timeout=5).stdout.split()
    except Exception:
        return
    for p in players:
        if p.startswith("spotifyd"):
            continue  # spotifyd es el objetivo de la API, no se toca
        try:
            st = subprocess.run(["playerctl", "-p", p, "status"], capture_output=True,
                                text=True, timeout=5).stdout.strip()
            if st == "Playing":
                # play-pause (toggle) + verificación con reintento: ncspot
                # ignora 'pause' a secas y a veces necesita dos intentos
                for _ in range(2):
                    subprocess.run(["playerctl", "-p", p, "play-pause"], capture_output=True, timeout=5)
                    time.sleep(0.6)
                    st = subprocess.run(["playerctl", "-p", p, "status"], capture_output=True,
                                        text=True, timeout=5).stdout.strip()
                    if st != "Playing":
                        break
        except Exception:
            continue


def handoff_to_spotifyd(token, player):
    """Toma la canción actual de un reproductor MPRIS local (p.ej. ncspot),
    la busca en Spotify y la reproduce en el dispositivo Connect (spotifyd),
    pausando el reproductor local para no duplicar audio."""
    try:
        title = subprocess.run(["playerctl", "-p", player, "metadata", "--format", "{{title}}"],
                               capture_output=True, text=True, timeout=5).stdout.strip()
        artist = subprocess.run(["playerctl", "-p", player, "metadata", "--format", "{{artist}}"],
                                capture_output=True, text=True, timeout=5).stdout.strip()
    except Exception:
        return False
    if not title:
        return False
    q = urllib.parse.quote("{} {}".format(title, artist))
    s, d = api("GET", "{}/search?q={}&type=track&limit=1".format(API, q), token)
    if s != 200 or not (d.get("tracks") or {}).get("items"):
        return False
    uri = d["tracks"]["items"][0]["uri"]
    if play(token, {"uris": [uri]}) in (200, 202, 204):
        pause_local_players()
        return True
    return False


# ---------- comandos ----------

def cmd_queue(token):
    st, who = detect_playback(token)
    if st != "api":
        if st == "mpris":
            pick = rofi_pick(
                ["▶ Continuar en Spotify (spotifyd)", "Salir"],
                ["migrate", "exit"],
                "Cola de reproducción",
                "{} reproduce en local: Spotify no ve su cola.\n"
                "Migra la canción a spotifyd y la cola aparecerá aquí.".format(who))
            if pick == "migrate":
                if handoff_to_spotifyd(token, who):
                    time.sleep(1.5)
                    return cmd_queue(token)
                show_error("No pude migrar la canción a spotifyd.\n"
                           "¿Está corriendo spotifyd? Si falta permiso, corre "
                           "'spotify_queue.py --auth' una vez.")
            return 0
        show_error("Nada suena ahora.\nReproduce algo en ncspot o spotifyd y vuelve a abrir la cola.")
        return 0

    s, data = api("GET", "{}/me/player/queue".format(API), token)
    if s == 401:
        return "reauth"
    if s == 204:
        now, queue = None, []
    elif s == 200:
        now = data.get("currently_playing")
        queue = data.get("queue") or []
    else:
        show_error("Error de Spotify (HTTP {})".format(s))
        return 0

    if not now and not queue:
        show_error("La cola está vacía.\nAbre una playlist desde el menú 📃 Playlists y vuelve.")
        return 0

    lines, uris = [], []
    if now:
        lines.append(track_line(now, now=True))
        uris.append(now.get("uri"))
    for i, t in enumerate(queue, 1):
        lines.append(track_line(t, n=i))
        uris.append(t.get("uri"))

    total = len(queue) + (1 if now else 0)
    mesg = "{} en cola · Enter reproduce · Esc sale".format(total)
    sel = rofi_pick(lines, uris, "Cola de reproducción", mesg)
    if sel.startswith("spotify:"):
        feedback(play(token, {"uris": [sel]}), "Reproduciendo la selección...")
    return 0


def cmd_playlists(token):
    items, offset = [], 0
    while True:
        s, d = api("GET", "{}/me/playlists?limit=50&offset={}".format(API, offset), token)
        if s == 401:
            return "reauth"
        if s != 200:
            show_error("Error de Spotify (HTTP {})".format(s))
            return 0
        batch = d.get("items") or []
        items.extend(batch)
        if len(batch) < 50 or offset > 200:
            break
        offset += 50

    if not items:
        show_error("No tienes playlists en tu cuenta.")
        return 0

    lines, uris = [], []
    for pl in items:
        name = pl.get("name") or "(sin nombre)"
        n = (pl.get("tracks") or {}).get("total")
        lines.append("{}  [{} canciones]".format(name, n) if n is not None else name)
        uris.append(pl.get("uri") or "")
    mesg = "{} playlists · Enter reproduce (en spotifyd) · Esc sale".format(len(lines))
    sel = rofi_pick(lines, uris, "Playlists", mesg)
    if sel.startswith("spotify:playlist:"):
        status = play(token, {"context_uri": sel})
        if status in (200, 202, 204):
            pause_local_players()  # evita que ncspot siga sonando a la vez
            notify("🎵 Música", "Reproduciendo en spotifyd...")
            time.sleep(1.5)
            return cmd_queue(token)  # muestra la cola de la playlist recién lanzada
        feedback(status, "Reproduciendo playlist...")
    return 0


def main():
    args = sys.argv[1:]
    if "--help" in args:
        print("Uso: spotify_queue.py [--playlists|--list|--auth]")
        print("  (sin args)     cola de reproducción en rofi")
        print("  --playlists    lista tus playlists reales y reproduce")
        print("  --list         cola en texto plano (debug)")
        print("  --auth         (re)autorizar una vez con el navegador")
        return 0

    try:
        env = load_env()
    except FileNotFoundError:
        show_error("No está ~/csv-to-spotify/.env")
        return 1

    if "--auth" in args:
        try:
            authorize(env)
            notify("🎵 Música", "¡Autorizado! Ya puedes usar la cola y playlists.")
        except Exception as e:
            show_error(str(e))
        return 0

    try:
        token = get_token(env)
    except Exception as e:
        show_error(str(e))
        return 1

    if "--list" in args:
        s, data = api("GET", "{}/me/player/queue".format(API), token)
        if s == 200:
            now = data.get("currently_playing")
            queue = data.get("queue") or []
            if now:
                print(track_line(now, now=True))
            for i, t in enumerate(queue, 1):
                print(track_line(t, n=i))
        else:
            print("HTTP {}".format(s))
        return 0

    r = cmd_playlists(token) if "--playlists" in args else cmd_queue(token)
    if r == "reauth":
        try:
            token = authorize(env)
        except Exception as e:
            show_error(str(e))
            return 1
        cmd_playlists(token) if "--playlists" in args else cmd_queue(token)
    return 0


if __name__ == "__main__":
    sys.exit(main())
