# <!-- ROLLE: zustell-marke -->
"""Erreicht Telegram uns überhaupt noch? — die Marke dazu.

**Die Lücke, die dieses Modul schließt:** Alle unsere Wächter prüfen, ob *wir*
leben. Keiner prüfte, ob **die Zustellung** noch ankommt. Fällt sie aus — ein
abgelaufenes Zertifikat, ein Adresswechsel, eine Firewall-Regel, ein verstellter
Webhook —, dann **schweigt der Bot, ohne dass irgendetwas kaputt aussieht.** Er
läuft ja. Der Prozess ist da, der Selbstcheck grün, die Belegkette wächst weiter.
Vierzehn Tage lang.

Das ist die unangenehmste Sorte Ausfall: einer, bei dem jede Anzeige auf Grün
steht.

## Warum im Bot und nicht in den Stundenblumen

Der Bot hat den Telegram-Schlüssel **ohnehin**. Gäbe man ihn auch den Blumen,
gäbe es einen **zweiten Ort für ein Geheimnis** — genau das, was bei 5.34 mit
den Zugangsdaten des eigenen Bot-API-Servers bewusst vermieden wurde. Also:
Der Bot fragt nach und **schreibt eine Marke**; die Blume liest die Marke und
meldet. Dieselbe Bauart wie bei der Anmeldung (`authmarke`), nur ein anderer
Anlass — **eine Bauart, zwei Anwendungen.**

## ⚠️ Der Schlüssel steht im Aufruf-Pfad

Telegram nimmt den Schlüssel als **Teil der Adresse** entgegen
(`api.telegram.org/bot<SCHLÜSSEL>/…`). Damit steht er in jeder Fehlermeldung,
die eine Adresse enthält — und Fehlermeldungen wandern in Protokolle, in
Marken, in Telegram-Nachrichten. **Derselbe Fund wie bei 5.34, nur diesmal bei
uns selbst.** Deshalb wird hier **niemals eine Adresse weitergereicht**: Jede
Ausnahme wird auf ihren Typ eingedampft, und die Marke kennt nur Zustände.

Nutzen über den Anlass hinaus: Die Antwort nennt die eingetragene Adresse mit,
also fällt auch ein **Adresswechsel des Servers** auf — die Falle beim späteren
Umzug. Und sie macht die Firewall-Beschränkung (Schritt 4c) überhaupt erst
sicher gehbar: Schneidet die Regel zu viel ab, sagt es die nächste Nachfrage.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

MARKE = Path(os.environ.get("ZUSTELL_MARKE")
             or (Path.home() / ".claude" / "zustellung-gestoert"))

# Ab wann ein Rückstau kein Zufall mehr ist. Bewusst nicht bei eins: Ein
# einzelnes liegengebliebenes Update kann ein Neustart im falschen Augenblick
# sein. Bei zwanzig ist es keiner mehr.
STAU_GRENZE = int(os.environ.get("ZUSTELL_STAU_GRENZE") or 20)

# Wie alt ein gemeldeter Fehler höchstens sein darf, um noch zu zählen. Ein
# Fehler von vorgestern, nach dem alles wieder lief, ist Geschichte.
FEHLER_FRISCH_S = int(os.environ.get("ZUSTELL_FEHLER_FRISCH") or 3 * 3600)

# Alles, was nach Schlüssel aussieht — inklusive des Telegram-Formats
# `123456:AAH…`, das in keiner unserer anderen Masken vorkam.
_SCHLUESSEL = re.compile(r"(\d{6,}:[A-Za-z0-9_\-]{20,}|[A-Za-z0-9_\-]{40,})")


def saeubern(text: str, grenze: int = 200) -> str:
    """Nimmt einer Zeichenkette alles, was ein Zugang sein könnte.

    Zuerst werden **ganze Adressen** entfernt — nicht nur der Schlüssel darin.
    Eine Adresse ohne Schlüssel wäre zwar harmlos, aber die Maske könnte ein
    unbekanntes Schlüsselformat verfehlen; eine Adresse gar nicht erst
    durchzulassen ist der sichere Weg.
    """
    t = re.sub(r"https?://\S+", "«Adresse entfernt»", str(text or ""))
    return _SCHLUESSEL.sub("«…»", t)[:grenze]


def _befund(info: dict, jetzt: float | None = None) -> tuple[bool, str]:
    """Beurteilt die Auskunft von Telegram. Rückgabe: (gestört?, Klartext).

    Vier Dinge können hier schiefstehen, und sie bedeuten Verschiedenes:
    """
    now = jetzt or time.time()
    adresse = (info.get("url") or "").strip()
    stau = int(info.get("pending_update_count") or 0)
    fehler = (info.get("last_error_message") or "").strip()
    fehler_zeit = float(info.get("last_error_date") or 0)

    # (1) Gar keine Adresse eingetragen: Im Webhook-Betrieb heißt das, dass
    # Telegram niemanden mehr zu benachrichtigen weiß — der stillste aller
    # Ausfälle.
    if not adresse:
        return True, ("Bei Telegram ist keine Zustelladresse eingetragen. "
                      "Im Webhook-Betrieb erreicht uns damit nichts mehr.")

    # (2) Ein frischer Fehler: Telegram hat es versucht und ist gescheitert.
    if fehler and (now - fehler_zeit) < FEHLER_FRISCH_S:
        vorher = int((now - fehler_zeit) / 60)
        return True, (f"Telegram konnte vor {vorher} Minuten nicht zustellen: "
                      f"{saeubern(fehler, 120)}")

    # (3) Rückstau: Telegram hat etwas für uns und wird es nicht los.
    if stau >= STAU_GRENZE:
        return True, (f"{stau} Nachrichten liegen bei Telegram und kommen nicht "
                      "durch. Der Bot läuft — die Zustellung nicht.")

    return False, f"Zustellung in Ordnung ({stau} unterwegs)."


def bewerten(info: dict, jetzt: float | None = None) -> tuple[bool, str]:
    """Öffentlicher Name für `_befund` — getrennt, damit Tests ihn direkt rufen."""
    return _befund(info, jetzt)


def setzen(grund: str, adresse_gleich: bool = True) -> None:
    """Legt die Marke. **Ohne Adresse, ohne Schlüssel** — nur Zustand."""
    try:
        MARKE.parent.mkdir(parents=True, exist_ok=True)
        tmp = MARKE.with_suffix(".tmp")
        tmp.write_text(json.dumps(
            {"zeit": time.time(),
             "menschlich": time.strftime("%Y-%m-%d %H:%M:%S"),
             "grund": saeubern(grund, 300),
             "adresse_unveraendert": bool(adresse_gleich)},
            ensure_ascii=False), encoding="utf-8")
        tmp.replace(MARKE)
    except Exception:
        pass                  # eine Marke, die nicht geht, darf nichts brechen


def loeschen() -> None:
    """Zustellung trägt wieder."""
    try:
        MARKE.unlink()
    except OSError:
        pass


def gesetzt() -> dict | None:
    try:
        return json.loads(MARKE.read_text(encoding="utf-8"))
    except Exception:
        return None
