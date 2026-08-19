# <!-- ROLLE: botenpost -->
"""Eine Stelle, die ins Boten-Postfach legt — und jede Nachricht nennt ihren Absender.

**Der Anlass (Vorfall 26.07., 01:44):** Adam bekam nachts eine Meldung über ein
„Update von demo". Um herauszufinden, **wer sie geschrieben hatte**, habe ich
über eine Stunde gebraucht, drei Verdächtige gegengemessen und den richtigen
zuerst freigesprochen — weil ein abgekoppelter Prozess das Testende überlebte
und ich zu früh nachgesehen hatte.

**Die Nachricht selbst hätte es in einer Minute gesagt, wenn sie ihren Absender
genannt hätte.** Genau das ist Leitplanke 7 aus dem Freigabe-Postfach — *jede
Anfrage sagt, wer sie gestellt hat*. Das Boten-Postfach kannte sie nicht.
**Eine anonyme Nachricht darf es im eigenen Haus nicht geben.**

**Warum EIN Modul und nicht vier Korrekturen:** Vier Schreiber legten bisher
jeder für sich eine Datei ab, mit vier fast gleichen Codeblöcken. Der fünfte
hätte den Absender wieder vergessen. *Wo Struktur und Prüfer beide möglich
sind, gewinnt die Struktur* — ein Prüfer meldet Drift, eine gemeinsame Quelle
lässt sie nicht entstehen.

**Kein Geheimnis im Postfach.** Der Text wird vor dem Ablegen von allem
befreit, was nach Schlüssel oder Adresse aussieht — dieselbe Maske wie in der
Zustell-Marke, aus demselben Grund.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

POSTFACH = Path(os.environ.get("POSTFACH_DIR")
                or (Path.home() / "postfach")) / "outbox"

# Erlaubte Absender. Bewusst eine feste Liste und kein freies Feld: Ein
# Absender, den sich jeder ausdenken kann, belegt nichts.
ABSENDER = ("hora", "blume", "waechter", "fenster", "updater", "bot",
            "auftragsbuch", "wachposten", "probe")

_SCHLUESSEL = re.compile(
    r"(\d{6,}:[A-Za-z0-9_\-]{20,}|sk-[A-Za-z0-9_\-]{6,}|[A-Za-z0-9_\-]{40,})")


class Abgewiesen(Exception):
    """Die Nachricht verletzt eine Leitplanke und wird nicht abgelegt."""


def _saeubern(text: str) -> str:
    t = re.sub(r"https?://\S+", "«Adresse entfernt»", str(text or ""))
    return _SCHLUESSEL.sub("«…»", t)


def ziel_finden() -> str:
    """Adams Kennung — aus der Umgebung, sonst aus den Vorlieben."""
    ziel = (os.environ.get("ALLOWED_USER_IDS") or "").split(",")[0].strip()
    if ziel.isdigit():
        return ziel
    try:
        prefs = json.loads((Path.home() / ".config" / "claude-telegram-bot"
                            / "prefs.json").read_text(encoding="utf-8"))
        return next((str(k) for k in prefs if str(k).isdigit()), "")
    except Exception:
        return ""


def legen(text: str, absender: str, ziel: str | int | None = None,
          thread_id: int | None = None) -> Path | None:
    """Legt eine Nachricht ab. Rückgabe: der Pfad, oder None wenn kein Ziel.

    Der Absender steht **zweimal** drin — im Dateinamen und im Inhalt. Das ist
    Absicht: Der Dateiname ist das, was man beim Durchsehen eines vollen
    Ordners sieht, ohne eine einzige Datei zu öffnen.
    """
    if absender not in ABSENDER:
        raise Abgewiesen(
            f"unbekannter Absender {absender!r} — erlaubt sind: "
            + ", ".join(ABSENDER))
    ziel = str(ziel or ziel_finden())
    if not ziel.isdigit():
        return None
    try:
        POSTFACH.mkdir(parents=True, exist_ok=True)
        marke = time.time_ns()
        eintrag = {
            "target_chat_id": int(ziel),
            "text": _saeubern(text),
            "herkunft": absender,
            "gelegt": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        if thread_id is not None:
            eintrag["thread_id"] = thread_id
        tmp = POSTFACH / f".{absender}-{marke}.tmp"
        tmp.write_text(json.dumps(eintrag, ensure_ascii=False), encoding="utf-8")
        ziel_datei = POSTFACH / f"{absender}-{marke}.json"
        tmp.rename(ziel_datei)
        return ziel_datei
    except Exception:
        return None                # ein Meldeweg, der klemmt, darf nichts brechen
