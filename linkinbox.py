# <!-- ROLLE: link-inbox -->
"""5.14 — Link-Inbox: erst ablegen, dann auf Knopfdruck verarbeiten.

**Das Problem, das sie löst:** Adam schickt Links im Vorbeigehen — ein Video,
einen Artikel, einen Beitrag. Bisher löste jeder Link sofort einen vollen
Modelllauf aus: abrufen, lesen, zusammenfassen. Das kostet Kontingent für
etwas, das er vielleicht nur ablegen wollte, und es dauert, während er längst
weitergezogen ist.

**Deshalb zwei Stufen** — dieselbe Zweistufigkeit wie bei Videos (Überblick
sofort, Tiefe auf Abruf) und beim Wartungsfenster (vormerken, dann handeln):

1. **Beim Eingang nur ein schlanker Eintrag** — Titel, Quelle, Art, Zeitpunkt.
   **Deterministisch, ohne Modell-Aufruf**: Was sich aus der Adresse ableiten
   lässt, wird abgeleitet, nicht erfragt.
2. **Verarbeitung erst auf Knopfdruck** — zusammenfassen, vertiefen oder (bei
   Video) volles Transkript.

**Bewusst ohne Netzabruf in dieser Stufe.** Der Eintrag entsteht aus der Adresse
selbst; nichts wird geladen, solange Adam nicht drückt. Das hält den Eingang
schnell und vermeidet, dass ein bloß abgelegter Link schon Spuren nach außen
zieht.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, asdict
from pathlib import Path

ABLAGE = Path(os.environ.get("LINK_INBOX_DIR")
              or (Path.home() / ".claude" / "link-inbox"))
DATEI = ABLAGE / "inbox.json"

_URL = re.compile(r"https?://[^\s<>\"')\]]+", re.IGNORECASE)

# Quellen-Erkennung: rein aus dem Adressnamen, ohne Abruf.
_QUELLEN: tuple[tuple[str, str, str], ...] = (
    ("youtube.com", "YouTube", "video"),
    ("youtu.be", "YouTube", "video"),
    ("vimeo.com", "Vimeo", "video"),
    ("instagram.com", "Instagram", "beitrag"),
    ("tiktok.com", "TikTok", "video"),
    ("x.com", "X", "beitrag"),
    ("twitter.com", "X", "beitrag"),
    ("facebook.com", "Facebook", "beitrag"),
    ("reddit.com", "Reddit", "beitrag"),
    ("github.com", "GitHub", "code"),
    ("wikipedia.org", "Wikipedia", "artikel"),
    ("spotify.com", "Spotify", "audio"),
)


@dataclass
class Eintrag:
    url: str
    quelle: str
    art: str          # video | beitrag | artikel | code | audio | seite
    titel: str        # aus der Adresse abgeleitet, bis etwas Besseres vorliegt
    empfangen: str
    chat_id: int | None = None
    message_id: int | None = None
    erledigt: bool = False
    notiz: str = ""

    def lesbar(self) -> str:
        art_wort = {"video": "Video", "beitrag": "Beitrag", "artikel": "Artikel",
                    "code": "Code", "audio": "Audio"}.get(self.art, "Seite")
        return f"{self.quelle} · {art_wort} · {self.titel}"


def urls_in(text: str) -> list[str]:
    """Alle Adressen einer Nachricht, Reihenfolge erhalten, ohne Doppelte."""
    gesehen, raus = set(), []
    for m in _URL.finditer(text or ""):
        u = m.group(0).rstrip(".,;:!?)")
        if u not in gesehen:
            gesehen.add(u)
            raus.append(u)
    return raus


def _host(url: str) -> str:
    ohne = re.sub(r"^https?://", "", url, flags=re.I)
    return ohne.split("/", 1)[0].lower().removeprefix("www.")


def einordnen(url: str) -> tuple[str, str]:
    """(Quelle, Art) — allein aus der Adresse, ohne Netzabruf."""
    h = _host(url)
    for muster, quelle, art in _QUELLEN:
        if muster in h:
            return quelle, art
    return h or "Web", "seite"


def _titel_aus_adresse(url: str) -> str:
    """Ein brauchbarer Behelfstitel, bis der Inhalt gelesen wurde.

    Bewusst ein **Behelf** und als solcher erkennbar: Ein aus der Adresse
    geratener Titel darf nicht wie ein gelesener aussehen — sonst glaubt man
    ihm mehr, als er wert ist (dieselbe Lehre wie beim Auflösungs-Budget).
    """
    pfad = re.sub(r"^https?://[^/]+/?", "", url).split("?", 1)[0].strip("/")
    if not pfad:
        return _host(url)
    letzter = pfad.rsplit("/", 1)[-1]
    letzter = re.sub(r"\.(html?|php|aspx?)$", "", letzter, flags=re.I)
    schön = re.sub(r"[-_+]+", " ", letzter).strip()
    if len(schön) < 3 or schön.isdigit():
        return _host(url)
    return schön[:80]


def _laden() -> list[dict]:
    try:
        return json.loads(DATEI.read_text(encoding="utf-8"))
    except Exception:
        return []


def _speichern(liste: list[dict]) -> None:
    ABLAGE.mkdir(parents=True, exist_ok=True)
    tmp = DATEI.with_suffix(".tmp")
    tmp.write_text(json.dumps(liste, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(DATEI)


def ablegen(url: str, chat_id: int | None = None,
            message_id: int | None = None) -> Eintrag:
    """Legt einen Link ab — ohne ihn abzurufen."""
    quelle, art = einordnen(url)
    e = Eintrag(url=url, quelle=quelle, art=art,
                titel=_titel_aus_adresse(url),
                empfangen=time.strftime("%Y-%m-%d %H:%M"),
                chat_id=chat_id, message_id=message_id)
    liste = _laden()
    # Denselben Link nicht doppelt führen — Adam schickt gern nach.
    liste = [x for x in liste if x.get("url") != url]
    liste.append(asdict(e))
    _speichern(liste)
    return e


def offene() -> list[Eintrag]:
    return [Eintrag(**{k: v for k, v in x.items() if k in Eintrag.__annotations__})
            for x in _laden() if not x.get("erledigt")]


def finden(url: str) -> Eintrag | None:
    for x in _laden():
        if x.get("url") == url:
            return Eintrag(**{k: v for k, v in x.items()
                              if k in Eintrag.__annotations__})
    return None


def abhaken(url: str, notiz: str = "") -> bool:
    liste = _laden()
    getroffen = False
    for x in liste:
        if x.get("url") == url:
            x["erledigt"] = True
            if notiz:
                x["notiz"] = notiz[:300]
            getroffen = True
    if getroffen:
        _speichern(liste)
    return getroffen


def entfernen(url: str) -> bool:
    liste = _laden()
    neu = [x for x in liste if x.get("url") != url]
    if len(neu) == len(liste):
        return False
    _speichern(neu)
    return True


def uebersicht(grenze: int = 20) -> str:
    liste = offene()
    if not liste:
        return "🔗 Die Link-Ablage ist leer."
    zeilen = [f"• {e.lesbar()}  ({e.empfangen})" for e in liste[:grenze]]
    rest = len(liste) - len(zeilen)
    kopf = f"🔗 Abgelegte Links ({len(liste)}):"
    fuss = f"\n… und {rest} weitere." if rest > 0 else ""
    return kopf + "\n" + "\n".join(zeilen) + fuss
