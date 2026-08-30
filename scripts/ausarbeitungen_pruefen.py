#!/usr/bin/env python3
# <!-- ROLLE: ausarbeitungen-pruefer -->
"""Zustand am Papier — der Pruefer gegen Karteileichen.

**Claudias Bauauftrag vom 28.08., Auftrag 1.** Der Anlass ist ihr eigener
Fehler, und sie benennt ihn selbst: Am 27.08. hat Adam ein Pruefverfahren mit
absichtlich eingebauten Maengeln abgelehnt, sie hat die Streichung schriftlich
bestaetigt — **und die Vorlage blieb unveraendert.** Einen Tag spaeter baute
sie den Bauauftrag aus dieser Vorlage und schrieb den abgelehnten Punkt wieder
hinein. Gefunden hat es erst die Gegenpruefung.

**Die Fehlerklasse:** Eine Entscheidung wurde *angenommen*, aber nicht
*abgelegt*. Das Gespraech verging, das Dokument blieb — und beim naechsten
Zugriff gewann das Dokument.

**Warum kein Register anschlug:** Register verzeichnen, was existiert. Ein
ueberholter Satz in einem gueltig aussehenden Papier existiert weiterhin und
ist von einem richtigen Satz maschinell nicht zu unterscheiden.

**Was dieser Pruefer deshalb NICHT kann, und das gehoert vorn hingeschrieben:**
Den Vorfall oben haette er nicht gefunden — das Papier war einen Tag alt. Er
misst **Alter und Anwesenheit eines Zustandskopfes**, nicht Inhalt. Das findet
Karteileichen unabhaengig davon, worum es geht; es findet keine frischen
Widersprueche. *Claudias Auftrag 2 ist deshalb der wichtigere.*

## Die Daempfung, und sie ist der Grund, warum der Pruefer ueberlebt

Beim ersten Lauf haetten **45 von 46** Papieren keinen Zustandskopf. Eine
Meldung mit 45 Zeilen wird einmal gelesen und danach nie wieder — und mit ihr
die eine Zeile, die spaeter zaehlt. Deshalb:

* **Erster Lauf:** nur die Grundlinie als Zahl, keine Namensliste.
* **Danach:** gemeldet wird, was **neu** in die Vorlage-Liste rutscht — nicht,
  was darin steht. Dieselbe Daempfung wie bei der Stundenblume.

Deterministisch, ohne Modell-Aufruf. Aufruf ohne Argumente; Ausgabe leer heisst
„nichts Neues".
"""
import json
import os
import re
import sys
import time
from pathlib import Path

# **Der Ort kommt aus der Umgebung, mit einem Rueckfall je Maschine.** Auf dem
# Server liegt das Log-Repo unter `LOG_SYNC_REPO`, am Mac im Arbeitsklon.
_REPO = os.environ.get("LOG_SYNC_REPO")
ORDNER = Path(os.environ.get("AUSARBEITUNGEN_DIR")
              or ((_REPO + "/ausarbeitungen") if _REPO
                  else Path.home() / "Projects/claude-bot-logs/ausarbeitungen"))
STAND = Path(os.environ.get("AUSARBEITUNGEN_STAND")
             or (Path.home() / ".claude" / "ausarbeitungen-stand.json"))

#: Ab wann ein Papier auf „gueltig" zur Sichtung vorgelegt wird.
#: **Claudias Setzung, von ihr selbst als solche benannt** — hier ueber die
#: Umgebung verstellbar, damit sich das Mass messen laesst, ohne den Code
#: anzufassen.
ALTER_TAGE = float(os.environ.get("AUSARBEITUNGEN_ALTER_TAGE") or 21)

#: Der Zustandskopf steht **oben**, sonst ist er keiner. Zehn Zeilen Spielraum
#: fuer Titel und Leerzeilen; wer ihn ans Ende schreibt, hat ihn nicht gesetzt.
_KOPFZEILEN = 10
_STAND_RE = re.compile(r"^STAND:\s*(.+?)\s*$", re.M)


def _zustand(text: str) -> str | None:
    """Der Zustandskopf eines Papiers, falls er oben steht."""
    kopf = "\n".join(text.splitlines()[:_KOPFZEILEN])
    m = _STAND_RE.search(kopf)
    return m.group(1) if m else None


def pruefen(jetzt: float | None = None) -> dict:
    """Misst den Ordner. Rueckgabe: die beiden Mengen, ungefiltert.

    **Gemessen wird ueber eine Menge, nicht ueber eine Liste** — jede `.md` im
    Ordner, nicht eine gepflegte Aufzaehlung. Eine Aufzaehlung waere binnen
    zwei Wochen unvollstaendig, und ein Papier, das der Pruefer nicht kennt,
    ist genau die Karteileiche, um die es geht.
    """
    now = jetzt or time.time()
    ohne_kopf: list[str] = []
    zu_alt: list[str] = []
    if not ORDNER.is_dir():
        return {"ordner": str(ORDNER), "erreichbar": False,
                "ohne_kopf": [], "zu_alt": [], "gesamt": 0}
    for p in sorted(ORDNER.glob("*.md")):
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        zustand = _zustand(text)
        if zustand is None:
            ohne_kopf.append(p.name)
            continue
        # **Das Altersmass gilt fuer „gueltig", nicht fuer jeden Kopf.** Ein
        # Papier, das ausdruecklich als ueberholt oder gebaut vermerkt ist,
        # braucht keine Sichtung — es ist ja bereits eingeordnet.
        if zustand.lower().startswith("gültig") or zustand.lower().startswith("gueltig"):
            alter = (now - p.stat().st_mtime) / 86400
            if alter > ALTER_TAGE:
                zu_alt.append(p.name)
    return {"ordner": str(ORDNER), "erreichbar": True, "gesamt":
            len(list(ORDNER.glob("*.md"))),
            "ohne_kopf": ohne_kopf, "zu_alt": zu_alt}


def _gemeldet_lesen() -> dict:
    try:
        return json.loads(STAND.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _gemeldet_schreiben(daten: dict) -> None:
    STAND.parent.mkdir(parents=True, exist_ok=True)
    tmp = STAND.with_suffix(".tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(STAND)


def meldung(jetzt: float | None = None) -> str:
    """Was zu melden ist — leer, wenn nichts NEU ist.

    **Der Zustand wird auch dann fortgeschrieben, wenn nichts gemeldet wird.**
    Sonst waere ein Papier, das seinen Kopf bekommt, beim naechsten Verlust
    wieder „neu" — und die Meldung erschiene doppelt.
    """
    befund = pruefen(jetzt)
    if not befund["erreichbar"]:
        return (f"⚠️ Ausarbeitungen nicht erreichbar ({befund['ordner']}) — "
                "der Zustandspruefer hat NICHTS gemessen.")
    alt = _gemeldet_lesen()
    erster_lauf = not alt
    neu_ohne = sorted(set(befund["ohne_kopf"]) - set(alt.get("ohne_kopf", [])))
    neu_alt = sorted(set(befund["zu_alt"]) - set(alt.get("zu_alt", [])))
    _gemeldet_schreiben({"ohne_kopf": befund["ohne_kopf"],
                         "zu_alt": befund["zu_alt"],
                         "gemessen_am": time.strftime(
                             "%Y-%m-%d %H:%M", time.localtime(jetzt or time.time()))})
    if erster_lauf:
        # **Grundlinie statt Lawine.** Namen erst ab dem zweiten Lauf.
        return (f"📋 Zustandspruefer eingerichtet: {befund['gesamt']} Papiere, "
                f"davon {len(befund['ohne_kopf'])} ohne Zustandskopf und "
                f"{len(befund['zu_alt'])} laenger als {ALTER_TAGE:.0f} Tage auf "
                "[gültig]. Ab jetzt melde ich nur noch Zugaenge.")
    teile = []
    if neu_ohne:
        teile.append("ohne Zustandskopf: " + ", ".join(neu_ohne[:8])
                     + (f" (+{len(neu_ohne) - 8})" if len(neu_ohne) > 8 else ""))
    if neu_alt:
        teile.append(f"laenger als {ALTER_TAGE:.0f} Tage auf [gültig]: "
                     + ", ".join(neu_alt[:8])
                     + (f" (+{len(neu_alt) - 8})" if len(neu_alt) > 8 else ""))
    if not teile:
        return ""
    return "📋 Neu zur Sichtung — " + " · ".join(teile)


def ins_auftragsbuch(text: str) -> str:
    """Legt den Befund fuer die KONTROLLE ab, nicht fuer Adam.

    **Claudias Empfaenger-Vorgabe, und sie ist begruendet:** Nach der
    Meldewege-Regel vom 21.08. ist das hier technisch und wird ohnehin
    bearbeitet. Adam erfaehrt davon nur, wenn eine Entscheidung von ihm noetig
    wird — sonst waere es eine taegliche Zeile ueber Papierpflege in einer
    Meldung, die er wegen der wichtigen Zeilen liest.

    Dublettenschutz ueber die Marke, wie beim Sichtungs-Vermerk: Liegt schon
    ein offener Eintrag, entsteht kein zweiter. **Ein Stapel gleichlautender
    Eintraege wird als Ganzes ignoriert** — dann haette der Pruefer sich selbst
    abgeschaltet.
    """
    # **Die Wurzel kommt aus dem eigenen Ort, nicht aus der Umgebung.** Der
    # Tagescheck setzt `PYTHONPATH`; ein Handaufruf tut das nicht — und
    # scheiterte dann mit „Auftragsbuch nicht ladbar", was nach einem kaputten
    # Auftragsbuch aussieht statt nach einem fehlenden Suchpfad. Im Prüfer
    # gemessen, nicht im Betrieb aufgefallen.
    wurzel = str(Path(__file__).resolve().parent.parent)
    if wurzel not in sys.path:
        sys.path.insert(0, wurzel)
    try:
        import auftragsbuch as ab
    except Exception as e:
        return f"FEHLER Auftragsbuch nicht ladbar: {type(e).__name__}"
    marke = "ausarbeitungen-zustand"
    try:
        if any(a.get("marke") == marke for a in ab.eingang()):
            return "SCHON-DA"
        ab.legen({
            "titel": "Zustand der Ausarbeitungen sichten",
            "art": "zustandspruefung",
            "marke": marke,
            "beschreibung": text,
        }, absender="claudia")
        return "GELEGT"
    except Exception as e:
        return f"FEHLER {type(e).__name__}"


if __name__ == "__main__":
    text = meldung()
    if not text:
        sys.exit(0)
    if "--ins-auftragsbuch" in sys.argv:
        print(ins_auftragsbuch(text))
    else:
        print(text)
    sys.exit(0)
