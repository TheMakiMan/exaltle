#!/usr/bin/env python3
"""
Holt die aktuellen Path-of-Exile-2-Preise von poe.ninja und baut daraus die Daten für die Seite.

- Läuft einmal täglich über GitHub Actions (siehe .github/workflows/update.yml).
- Spieler fragen poe.ninja nie selbst ab: Nur dieses Skript holt die Daten, so wie poe.ninja es verlangt
  (eigener User-Agent, wenige Anfragen, Pausen dazwischen).
- Item-Bilder werden einmal heruntergeladen und von der eigenen Seite ausgeliefert.
- Das Tagesrätsel wird hier festgelegt und sein Preis für den ganzen Tag eingefroren.

Aufruf:
  python scripts/update_data.py                 # Preise + Bilder + Schriften aktualisieren
  python scripts/update_data.py --only-if-missing  # nur, wenn noch gar keine Daten da sind
  python scripts/update_data.py --fonts-only    # nur die Schriften sicherstellen
Nur Standardbibliothek, keine Installation nötig.
"""
import datetime as dt
import hashlib
import json
import os
import pathlib
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
DATA = SITE / "data"
IMG = SITE / "img"
FONTS = SITE / "fonts"

BASE = os.environ.get("POENINJA_BASE", "https://poe.ninja").rstrip("/")
CDN = os.environ.get("POECDN_BASE", "https://web.poecdn.com").rstrip("/")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
USER_AGENT = f"exaltle-fansite/1.0 (+https://github.com/{REPO})" if REPO else "exaltle-fansite/1.0"
DELAY = float(os.environ.get("REQUEST_DELAY", "1.5"))   # Pause zwischen Anfragen an poe.ninja (Sekunden)
MAX_LEAGUES = int(os.environ.get("MAX_LEAGUES", "6"))

# Börsen-Kategorien (Exchange) und Unique-Kategorien laut poe.ninja-Doku.
# Die Seite übersetzt diese Codes selbst in die Sprache des Besuchers.
EXCHANGE_TYPES = ["Currency", "Fragments", "Abyss", "UncutGems", "LineageSupportGems", "Essences", "SoulCores", "Idols",
                  "Runes", "Ritual", "Expedition", "Delirium", "Breach", "Verisium"]
UNIQUE_TYPES = ["UniqueWeapons", "UniqueArmours", "UniqueAccessories", "UniqueFlasks", "UniqueCharms", "UniqueJewels"]

# Mindest-Liquidität, damit Preise aussagekräftig sind
MIN_EXCHANGE_VOLUME_DIV = 1.0     # Handelsvolumen in Divine
MIN_UNIQUE_LISTINGS = 10          # Angebote
# Strengere Regeln für das Tagesrätsel (gut bekannte, verlässlich bepreiste Items)
DAILY_MIN_EXCHANGE_VOLUME_DIV = 5.0
DAILY_MIN_UNIQUE_LISTINGS = 20
DAILY_MIN_EX = 3.0                # kein Ramsch zum Grundpreis
HISTORY_DAYS = 90                 # so lange wiederholt sich ein Tages-Item nicht

FONT_FILES = {
    # Schriften unter SIL Open Font License, über das npm-Paket von Fontsource
    "cinzel-700.woff2": "https://cdn.jsdelivr.net/npm/@fontsource/cinzel@5/files/cinzel-latin-700-normal.woff2",
    "cinzel-800.woff2": "https://cdn.jsdelivr.net/npm/@fontsource/cinzel@5/files/cinzel-latin-800-normal.woff2",
    "alegreya-sans-400.woff2": "https://cdn.jsdelivr.net/npm/@fontsource/alegreya-sans@5/files/alegreya-sans-latin-400-normal.woff2",
    "alegreya-sans-500.woff2": "https://cdn.jsdelivr.net/npm/@fontsource/alegreya-sans@5/files/alegreya-sans-latin-500-normal.woff2",
    "alegreya-sans-700.woff2": "https://cdn.jsdelivr.net/npm/@fontsource/alegreya-sans@5/files/alegreya-sans-latin-700-normal.woff2",
    "alegreya-sans-cyrillic-400.woff2": "https://cdn.jsdelivr.net/npm/@fontsource/alegreya-sans@5/files/alegreya-sans-cyrillic-400-normal.woff2",
    "alegreya-sans-cyrillic-700.woff2": "https://cdn.jsdelivr.net/npm/@fontsource/alegreya-sans@5/files/alegreya-sans-cyrillic-700-normal.woff2",
}


def log(msg):
    print(msg, flush=True)


def http_get(url, binary=False, polite=True):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "*/*"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            body = r.read()
    finally:
        if polite:
            time.sleep(DELAY)
    return body if binary else json.loads(body.decode("utf-8"))


def api(path, **params):
    q = urllib.parse.urlencode(params)
    return http_get(f"{BASE}{path}" + (f"?{q}" if q else ""))


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or "liga"


def read_json(path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")


def abs_image_url(u):
    if not u:
        return None
    if u.startswith("//"):
        return "https:" + u
    if u.startswith("/"):
        return CDN + u
    return u if u.startswith("http") else None


def local_image(url):
    """Lädt ein Item-Bild einmal herunter und gibt den Pfad relativ zur Seite zurück (oder None)."""
    url = abs_image_url(url)
    if not url:
        return None
    ext = ".webp" if url.lower().split("?")[0].endswith(".webp") else ".png"
    name = hashlib.sha1(url.encode()).hexdigest()[:16] + ext
    target = IMG / name
    if not target.exists():
        try:
            data = http_get(url, binary=True, polite=False)
            time.sleep(0.2)
            if len(data) < 64 or len(data) > 2_000_000:
                return None
            IMG.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        except (urllib.error.URLError, OSError, ValueError) as e:
            log(f"    Bild nicht geladen: {url} ({e})")
            return None
    return f"img/{name}"


def rates_from(core):
    """Wandelt poe.ninjas Referenzwährung um: wie viele Exalted ist eine Einheit der Referenzwährung wert, und wie viele Exalted ist 1 Divine."""
    primary = (core or {}).get("primary", "divine")
    rates = dict((core or {}).get("rates", {}))
    rates[primary] = 1.0
    ex_per_primary = float(rates.get("exalted", 0) or 0)
    div_per_primary = float(rates.get("divine", 0) or 0)
    if ex_per_primary <= 0 or div_per_primary <= 0:
        raise ValueError(f"Wechselkurse unvollständig: primary={primary}, rates={rates}")
    return ex_per_primary, ex_per_primary / div_per_primary


def fetch_league(league_id, league_name):
    log(f"Liga: {league_name}")
    cur = api("/poe2/api/economy/exchange/current/overview", league=league_id, type="Currency")
    ex_per_primary, ex_per_div = rates_from(cur.get("core"))
    items = []
    seen = set()

    def add_exchange(payload, code):
        meta = {str(i.get("id")): i for i in payload.get("items", []) if isinstance(i, dict)}
        for core_item in (payload.get("core") or {}).get("items", []) or []:
            if isinstance(core_item, dict):
                meta.setdefault(str(core_item.get("id")), core_item)
        for line in payload.get("lines", []):
            iid = str(line.get("id", ""))
            m = meta.get(iid, {})
            name = m.get("name") or m.get("text")
            value = float(line.get("primaryValue") or 0)
            vol = float(line.get("volumePrimaryValue") or 0)
            if not name or value <= 0 or iid in ("divine", "exalted"):
                continue
            vol_div = vol * ex_per_primary / ex_per_div
            if vol_div < MIN_EXCHANGE_VOLUME_DIV:
                continue
            key = "x:" + iid
            if key in seen:
                continue
            seen.add(key)
            items.append({"k": key, "n": name, "c": code, "u": 0, "e": round(value * ex_per_primary, 4),
                          "v": round(vol_div, 2), "i": local_image(m.get("image") or m.get("icon"))})

    add_exchange(cur, "Currency")
    log(f"  Currency: {len(items)} Items")
    for t in EXCHANGE_TYPES:
        if t == "Currency":
            continue
        try:
            before = len(items)
            add_exchange(api("/poe2/api/economy/exchange/current/overview", league=league_id, type=t), t)
            log(f"  {t}: {len(items) - before} Items")
        except (urllib.error.URLError, ValueError, KeyError, TypeError) as e:
            log(f"  {t}: übersprungen ({e})")

    for t in UNIQUE_TYPES:
        try:
            payload = api("/poe2/api/economy/stash/current/item/overview", league=league_id, type=t)
        except (urllib.error.URLError, ValueError) as e:
            log(f"  {t}: übersprungen ({e})")
            continue
        best = {}
        for line in payload.get("lines", []):
            name = line.get("name")
            value = float(line.get("primaryValue") or 0)
            listings = int(line.get("listingCount") or 0)
            if not name or value <= 0 or line.get("corrupted") or listings < MIN_UNIQUE_LISTINGS:
                continue
            if name not in best or listings > best[name]["listingCount"]:
                best[name] = {**line, "listingCount": listings}
        for name, line in best.items():
            key = "u:" + slugify(name)
            if key in seen:
                continue
            seen.add(key)
            items.append({"k": key, "n": name, "b": line.get("baseType") or "", "c": t, "u": 1,
                          "e": round(float(line["primaryValue"]) * ex_per_primary, 4), "v": int(line["listingCount"]),
                          "i": local_image(line.get("icon"))})
        log(f"  {t}: {len(best)} Uniques")

    log(f"  {len(items)} Items, 1 Divine = {ex_per_div:.1f} Exalted")
    return {"exPerDiv": round(ex_per_div, 2), "items": items}


def daily_candidates(data):
    out_x, out_u = [], []
    for it in data["items"]:
        if it["e"] < DAILY_MIN_EX:
            continue
        if it["u"] and it["v"] >= DAILY_MIN_UNIQUE_LISTINGS:
            out_u.append(it)
        elif not it["u"] and it["v"] >= DAILY_MIN_EXCHANGE_VOLUME_DIV:
            out_x.append(it)
    return out_x, out_u


def pick_daily(slug, data, today, launch, history, previous):
    # Läuft das Skript am selben Tag nochmal, bleibt das Tagesrätsel samt Preis gleich
    if previous and previous.get("date") == today:
        return previous
    used = set(history.get(slug, []))
    rng = random.Random(f"{today}:{slug}")
    cx, cu = daily_candidates(data)
    cx = [i for i in cx if i["k"] not in used] or cx
    cu = [i for i in cu if i["k"] not in used] or cu
    pools = [p for p in (cx, cu) if p]
    if not pools:
        return previous
    pick = rng.choice(rng.choice(pools))
    history[slug] = (history.get(slug, []) + [pick["k"]])[-HISTORY_DAYS:]
    no = (dt.date.fromisoformat(today) - dt.date.fromisoformat(launch)).days + 1
    return {"date": today, "no": no, "item": pick}


def ensure_fonts():
    FONTS.mkdir(parents=True, exist_ok=True)
    for name, url in FONT_FILES.items():
        target = FONTS / name
        if target.exists():
            continue
        try:
            target.write_bytes(http_get(url, binary=True, polite=False))
            log(f"Schrift geladen: {name}")
        except (urllib.error.URLError, OSError) as e:
            log(f"Schrift nicht geladen: {name} ({e}). Die Seite nutzt dann Systemschriften.")


def write_seo(base):
    """Setzt die echte Adresse der Seite ein (Link-Vorschau, Google) und schreibt robots.txt und sitemap.xml.
    Läuft nur beim Veröffentlichen, die Änderungen werden nicht ins Repository gespeichert."""
    base = base.strip().rstrip("/") + "/"
    if not base.startswith("http"):
        log(f"Ungültige Adresse für SEO: {base!r}")
        return 1
    index = SITE / "index.html"
    index.write_text(index.read_text(encoding="utf-8").replace("__SITE_URL__", base), encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {base}sitemap.xml\n", encoding="utf-8")
    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    (SITE / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"  <url><loc>{base}</loc><lastmod>{today}</lastmod><changefreq>daily</changefreq></url>\n"
        "</urlset>\n", encoding="utf-8")
    log(f"SEO-Dateien für {base} geschrieben.")
    return 0


def main():
    args = sys.argv[1:]
    if "--seo" in args:
        i = args.index("--seo")
        return write_seo(args[i + 1] if i + 1 < len(args) else "")
    args = set(args)
    if "--fonts-only" in args:
        ensure_fonts()
        return 0
    if "--only-if-missing" in args and (DATA / "leagues.json").exists():
        log("Daten vorhanden, nichts zu tun.")
        return 0

    today = dt.datetime.now(dt.timezone.utc).date().isoformat()
    meta = read_json(DATA / "meta.json", {})
    meta.setdefault("launch", today)
    history = read_json(DATA / "history.json", {})

    leagues_raw = api("/poe2/api/economy/leagues")
    leagues_raw = [l for l in leagues_raw if isinstance(l, dict) and l.get("id")][:MAX_LEAGUES]
    if not leagues_raw:
        log("Keine Ligen gefunden.")
        return 1

    leagues_out, ok = [], 0
    now = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    for l in leagues_raw:
        lid, name = l["id"], l.get("name") or l["id"]
        slug = slugify(lid)
        path = DATA / f"{slug}.json"
        previous = read_json(path, {})
        try:
            data = fetch_league(lid, name)
            if len(data["items"]) < 10:
                raise ValueError("zu wenige Items")
            data.update({"league": name, "id": lid, "slug": slug, "updated": now})
            data["daily"] = pick_daily(slug, data, today, meta["launch"], history, previous.get("daily"))
            write_json(path, data)
            ok += 1
        except (urllib.error.URLError, ValueError, KeyError, TypeError) as e:
            log(f"  Fehler bei {name}: {e}. Die alten Daten bleiben bestehen.")
            if not path.exists():
                continue
        leagues_out.append({"id": lid, "name": name, "slug": slug,
                            "updated": read_json(path, {}).get("updated", now)})

    if not leagues_out:
        log("Keine Liga erfolgreich geladen.")
        return 1
    write_json(DATA / "leagues.json", {"default": leagues_out[0]["slug"], "leagues": leagues_out})
    write_json(DATA / "meta.json", meta)
    write_json(DATA / "history.json", history)
    ensure_fonts()
    log(f"Fertig: {ok} von {len(leagues_raw)} Ligen aktualisiert.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
