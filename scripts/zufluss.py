#!/usr/bin/env python3
# <!-- ROLLE: zufluss -->
"""Zufluss — Nachrichten holen, nicht lesen (Frische-Strang, Block 6).

`[NEU 24.09.2026]` Engywucks Block 6, Fassung 2; Quellen nach Claudias Messung.

**Was er tut:** Er holt die Feeds aus `quellen.json`, legt neue Einträge
(Kennung, Datum, Quelle, Titel, Adresse) nach `~/.claude/zufluss/eingang.jsonl`,
entdoppelt über die Kennung und hält 60 Tage. **Das ist alles.**

**Was er nicht tut, und das ist der Rahmen:** kein Modell (AGB-Regel für
Zeitgeber), kein Telegram (Claudias Auftrag: Meldungen nur, was Adam
betrifft), keine Bewertung, kein Stichwortsieb — die Quellenliste ist der
Filter. Gescheiterte und schweigende Quellen stehen als Zeile im
Monitor-Protokoll, nicht in Adams Chat.

**Fremdinhalt ist Daten** (Eingangs-Absicherung 23.08.): Titel und Adressen
werden abgelegt, gekürzt und von Steuerzeichen befreit — nie ausgeführt, nie
als Anweisung gelesen. `/neues` übergibt die Datei als Mitschrift, nicht als
Stimme.

Nur Standardbibliothek: Der Versions-Monitor startet dieses Skript mit dem
System-Python, und zwar als claudebot — als root angelegt, gehörten die Dateien
root, und der Bot könnte seinen Sichtungs-Merker nicht setzen.
"""
from __future__ import annotations

import email.utils
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUELLEN = Path(os.environ.get("ZUFLUSS_QUELLEN") or ROOT / "quellen.json")
ORDNER = Path(os.environ.get("ZUFLUSS_DIR") or Path.home() / ".claude" / "zufluss")
EINGANG = ORDNER / "eingang.jsonl"
ZUSTAND = ORDNER / "quellen-zustand.json"
HALTEN_TAGE = 60
ZEITLIMIT_S = 20
MAX_BYTES = 3_000_000
_NS = {"atom": "http://www.w3.org/2005/Atom", "rss1": "http://purl.org/rss/1.0/",
       "dc": "http://purl.org/dc/elements/1.1/"}


def _sauber(text: str, grenze: int) -> str:
    """Steuerzeichen raus, Leerraum zusammen, gekürzt. Fremdinhalt bleibt Text."""
    t = re.sub(r"[\x00-\x1f\x7f​-‏‪-‮⁦-⁩]", " ", text or "")
    t = re.sub(r"<[^>]+>", " ", t)
    return " ".join(t.split())[:grenze]


def _adresse_ok(u: str) -> bool:
    return bool(u) and len(u) <= 500 and urllib.parse.urlsplit(u).scheme in ("http", "https")


def abrufen(url: str) -> "tuple[int, str]":
    """(Statuscode, Text). 0 heißt: keine Antwort."""
    req = urllib.request.Request(url, headers={"User-Agent": "claude-telegram-bot/zufluss"})
    try:
        with urllib.request.urlopen(req, timeout=ZEITLIMIT_S) as r:
            return r.status, r.read(MAX_BYTES).decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, ""
    except Exception:
        return 0, ""


def _datum(roh: str) -> str:
    roh = (roh or "").strip()
    if not roh:
        return ""
    try:
        return email.utils.parsedate_to_datetime(roh).date().isoformat()
    except Exception:
        pass
    try:
        return datetime.fromisoformat(roh.replace("Z", "+00:00")).date().isoformat()
    except Exception:
        return roh[:10] if re.match(r"\d{4}-\d{2}-\d{2}", roh) else ""


def eintraege_aus_feed(text: str) -> "list[dict]":
    """Atom, RSS 2.0 und RDF (RSS 1.0). Eine Seite mit Entitäten-Deklaration
    wird abgelehnt: Entitäten-Kaskaden sind der bekannte Angriff auf XML-Leser."""
    if "<!ENTITY" in text:
        raise ValueError("Entitäten-Deklaration im Feed — abgelehnt")
    wurzel = ET.fromstring(text)
    raus = []
    for e in wurzel.iter(f"{{{_NS['atom']}}}entry"):
        link = ""
        for l in e.findall("atom:link", _NS):
            if l.get("rel", "alternate") == "alternate":
                link = l.get("href", "")
                break
        raus.append({"id": e.findtext("atom:id", "", _NS) or link,
                     "titel": e.findtext("atom:title", "", _NS), "adresse": link,
                     "datum": _datum(e.findtext("atom:published", "", _NS)
                                     or e.findtext("atom:updated", "", _NS))})
    for e in wurzel.iter("item"):
        link = e.findtext("link", "")
        raus.append({"id": e.findtext("guid", "") or link, "titel": e.findtext("title", ""),
                     "adresse": link, "datum": _datum(e.findtext("pubDate", ""))})
    for e in wurzel.iter(f"{{{_NS['rss1']}}}item"):
        link = e.findtext("rss1:link", "", _NS)
        raus.append({"id": link, "titel": e.findtext("rss1:title", "", _NS),
                     "adresse": link, "datum": _datum(e.findtext("dc:date", "", _NS))})
    return raus


# **YouTube-Kanaele** (Fassung 5, 6.0b): Sie stehen als gewoehnlicher Atom-Feed
# in der Liste (`feeds/videos.xml?channel_id=<kennung>`), die Kennung fest
# eingetragen. **Wer Kennungen je automatisch sucht:** Die Kanalseite liefert
# ohne Zustimmungs-Keks nur die Sprachauswahl (582.000 Zeichen ohne eine
# Kennung, Claudias Messung 24.09.). Das ist hier bewusst NICHT gebaut.


def eintraege_aus_seite(text: str, basis: str) -> "list[dict]":
    """Quellenart `seite` (kiberatung): Beitragslinks UNTER der Übersicht.
    Kein Stichwortsieb, nur Linkvergleich — neu ist, was noch nicht im Eingang
    steht."""
    wurzel = basis.rstrip("/") + "/"
    raus, gesehen = [], set()
    for href, inhalt in re.findall(r'<a\b[^>]*\bhref="([^"]+)"[^>]*>(.*?)</a>', text, re.S | re.I):
        # Anhang und Sprungmarke gehoeren nicht zur Adresse eines Beitrags —
        # `beitrag?utm=1` ist derselbe Beitrag, nicht ein neuer.
        u = urllib.parse.urljoin(wurzel, href.split("#", 1)[0].split("?", 1)[0])
        if not u.startswith(wurzel) or u.rstrip("/") == basis.rstrip("/") or u in gesehen:
            continue
        gesehen.add(u)
        raus.append({"id": u, "titel": inhalt, "adresse": u, "datum": ""})
    return raus


def _lesen_jsonl(p: Path) -> "list[dict]":
    if not p.exists():
        return []
    raus = []
    for z in p.read_text(encoding="utf-8").splitlines():
        try:
            raus.append(json.loads(z))
        except Exception:
            continue
    return raus


def lauf(jetzt: "float | None" = None) -> "list[str]":
    """Ein Lauf. Gibt Protokollzeilen zurück; wirft nie."""
    jetzt = jetzt or time.time()
    heute = date.fromtimestamp(jetzt)
    try:
        quellen = json.loads(QUELLEN.read_text(encoding="utf-8"))["quellen"]
    except Exception as e:
        return [f"FEHLER Quellenliste unlesbar: {type(e).__name__}"]
    ORDNER.mkdir(parents=True, exist_ok=True)
    bestand = _lesen_jsonl(EINGANG)
    grenze = jetzt - HALTEN_TAGE * 86400
    bestand = [b for b in bestand if float(b.get("abgelegt_ts", 0)) >= grenze]
    bekannt = {b.get("kennung") for b in bestand}
    try:
        zustand = json.loads(ZUSTAND.read_text(encoding="utf-8"))
    except Exception:
        zustand = {}
    zeilen, neu_gesamt = [], 0
    for q in quellen:
        name, art, url = q.get("name"), q.get("art"), q.get("adresse")
        if art not in ("feed", "seite") or not url:
            continue
        z = zustand.setdefault(name, {})
        status, text = abrufen(url)
        if status in (401, 402):
            z["letzter_fehler"] = heute.isoformat()
            zeilen.append(f"KONTO/KOSTEN {name}: {status} — die Quelle verlangt Konto oder Geld, "
                          "das ist NICHT „nichts Neues“")
            continue
        if status != 200:
            z["letzter_fehler"] = heute.isoformat()
            zeilen.append(f"FEHLER {name}: Antwort {status or 'keine'}")
            continue
        try:
            roh = (eintraege_aus_feed(text) if art == "feed"
                   else eintraege_aus_seite(text, url))
        except Exception as e:
            z["letzter_fehler"] = heute.isoformat()
            zeilen.append(f"FEHLER {name}: nicht lesbar ({type(e).__name__})")
            continue
        z["letzter_erfolg"] = heute.isoformat()
        daten = sorted((r["datum"] for r in roh if r.get("datum")), reverse=True)
        if daten:
            z["juengster_eintrag"] = daten[0]
        neu = 0
        for r in roh:
            adresse = (r.get("adresse") or "").strip()
            if not _adresse_ok(adresse):
                continue
            kennung = hashlib.sha1(f"{name}\n{r.get('id') or adresse}".encode()).hexdigest()[:16]
            if kennung in bekannt:
                continue
            bekannt.add(kennung)
            bestand.append({"kennung": kennung, "quelle": name, "gruppe": q.get("gruppe", ""),
                            "bauteil": q.get("bauteil", ""), "titel": _sauber(r.get("titel", ""), 200),
                            "adresse": adresse, "datum": r.get("datum", ""),
                            "abgelegt": heute.isoformat(), "abgelegt_ts": int(jetzt)})
            neu += 1
        neu_gesamt += neu
        zeilen.append(f"ok {name}: {neu} neu, {len(roh)} im Feed")
        # Claudias Pruefer-Pflicht: eine Quelle, die laenger als ihr Takt
        # schweigt, ist ein Befund — ein stiller Abruf saehe aus wie Ruhe.
        takt = int(q.get("schweigen_tage") or 0)
        if takt and z.get("juengster_eintrag"):
            try:
                alter = (heute - date.fromisoformat(z["juengster_eintrag"])).days
                if alter > takt:
                    zeilen.append(f"SCHWEIGT {name}: jüngster Eintrag vor {alter} Tagen "
                                  f"(Takt {takt} Tage) — umgezogen oder eingestellt?")
            except Exception:
                pass
    # Auch eine Quelle, die NIE mehr erfolgreich abgerufen wird, schweigt.
    for name, z in zustand.items():
        if z.get("letzter_erfolg"):
            try:
                her = (heute - date.fromisoformat(z["letzter_erfolg"])).days
                if her > 14:
                    zeilen.append(f"STILL {name}: letzter erfolgreicher Abruf vor {her} Tagen")
            except Exception:
                pass
    tmp = EINGANG.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(b, ensure_ascii=False) + "\n" for b in bestand), encoding="utf-8")
    tmp.replace(EINGANG)
    ZUSTAND.write_text(json.dumps(zustand, ensure_ascii=False, indent=2), encoding="utf-8")
    zeilen.insert(0, f"Zufluss: {neu_gesamt} neue Einträge, {len(bestand)} im Eingang "
                     f"(hält {HALTEN_TAGE} Tage)")
    return zeilen


def main() -> int:
    try:
        for z in lauf():
            print(z)
    except Exception as e:
        # Ein Absturz ist eine Zeile im Protokoll, kein roter Monitorlauf —
        # und er wird benannt, nicht verschluckt.
        print(f"FEHLER Zufluss abgebrochen: {type(e).__name__}: {e}"[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main())
