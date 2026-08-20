#!/usr/bin/env python3
# <!-- ROLLE: erinnerungs-laeufer -->
"""Der Erinnerungs-Läufer — Punkt 7.2. **RUHEND, siehe unten.**

**Wofür:** Termine und fällige Erinnerungen sollen von selbst kommen, statt
dass Adam `/termine` tippen muss. Der Kalender liegt seit dem 25.07. bereit
(`kalender.py`); was fehlte, war der regelmäßige Blick hinein.

## ⚠️ Warum er nicht läuft

**Zwei Dinge fehlen, beide bei Adam:**

1. **Der iCloud-Zugang** (7.3) — ohne ihn liest der Läufer nichts. Er sagt das
   dann auch und tut nicht so, als sei der Kalender leer.
2. **Der Erinnerungskanal** (7.1) — **ohne ihn hat er kein Ziel.** Bis dahin
   legt er in Adams Chat und **nennt das ausdrücklich in der Meldung**, statt
   Vollständigkeit vorzutäuschen.

Der Zeitgeber liegt als Vorlage in `docs/befehlsbloecke-root.md` mit dem
Vermerk **NOCH NICHT EINSPIELEN**.

## Drei Bauentscheidungen, die nicht offensichtlich sind

**Kein Modell im Pfad.** Ein Zeit-Trigger, der ein Modell startet, ist
AGB-Grauzone (`CLAUDE.md`, Auth-Passage) — und Adams Linien-Entscheid vom
20.08. deckt ausdrücklich **nur** den nachgeholten Lauf nach einem Limit ab,
nicht das Beginnen von Arbeit. Hier wird gelesen und formuliert, nicht gedacht.

**Eine Meldung je Lauf, nicht eine je Termin.** Die Postfach-Obergrenze liegt
bei fünf Nachrichten je Stunde und Absender; ein Tag mit sechs Terminen wäre
genau der Fall, in dem sie greift — und dann würde ausgerechnet die
Erinnerung zurückgehalten, für die der Läufer gebaut wurde. Gebündelt gibt es
das Problem nicht.

**Gedämpft über den Inhalt, nicht über die Zeit.** Derselbe Terminsatz wird
innerhalb der Wiedervorlagefrist nur einmal gemeldet. Der Schlüssel ist ein
Hash der Termin-Kennungen — **kein Text, keine Uhrzeit**: Am 28.07. hebelte
ein Zeitstempel im Meldungstext einen Dämpfer aus, weil jede Meldung neu
aussah.

Aufruf: ``python3 scripts/erinnerungen.py [--trocken] [--stunden N]``
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
import botenpost  # noqa: E402
import kalender  # noqa: E402

ZUSTAND = Path(os.environ.get("ERINNERUNG_DIR")
               or (Path.home() / ".claude" / "erinnerungen"))
MARKE = ZUSTAND / "stand.json"

# Wie weit nach vorn geschaut wird. Vier Stunden passen zu einem Lauf je
# Stunde: Jeder Termin wird mehrfach gesehen, bevor er ansteht — der Dämpfer
# sorgt dafür, dass er trotzdem nur einmal gemeldet wird.
VORSCHAU_STUNDEN = int(os.environ.get("ERINNERUNG_VORSCHAU") or 4)

# Derselbe Satz frühestens nach dieser Frist erneut.
WIEDERVORLAGE_S = int(os.environ.get("ERINNERUNG_WIEDERVORLAGE") or 10800)

# Mehr als das liest niemand in einer Vorschau-Meldung.
MAX_ZEILEN = 6

# Das Ziel: Sobald der Erinnerungskanal steht (7.1), trägt diese Variable
# seine Kennung. Solange sie leer ist, geht die Meldung an Adam — mit Hinweis.
ZIEL_KANAL = (os.environ.get("ERINNERUNG_KANAL") or "").strip()


def _stand_laden() -> dict:
    try:
        return json.loads(MARKE.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return {}
    except Exception:
        # Unlesbar heißt: von vorn — und es wird GEMELDET, nicht verschwiegen
        # (Lehre des Versions-Monitors, 18.08.).
        return {"_beschaedigt": True}


def _stand_schreiben(stand: dict) -> None:
    try:
        ZUSTAND.mkdir(parents=True, exist_ok=True)
        tmp = MARKE.with_suffix(".tmp")
        tmp.write_text(json.dumps(stand, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        tmp.replace(MARKE)
    except Exception as e:
        print(f"WARNUNG: Stand nicht gesichert ({type(e).__name__})")


def _schluessel(zeilen: list[str]) -> str:
    """Woran ein bereits gemeldeter Satz erkannt wird.

    **Über den Inhalt, nicht über die Zeit.** Trüge der Schlüssel einen
    Zeitstempel, sähe jede Meldung neu aus und der Dämpfer liefe leer — genau
    das ist am 28.07. passiert.
    """
    roh = "\n".join(sorted(zeilen))
    return hashlib.sha256(roh.encode("utf-8")).hexdigest()[:16]


def _faellige(stunden: int) -> tuple[list[str], str]:
    """Was ansteht — und ehrlich, wenn nichts gelesen werden konnte.

    Rückgabe: (Zeilen, Hinweis). Der Hinweis ist leer, wenn alles glatt lief.
    """
    if not kalender.zugang_vorhanden():
        return ([], "Kalender-Zugang fehlt (7.3) — ich sehe gerade nichts.")
    zeilen: list[str] = []
    hinweise: list[str] = []
    # Termine und Aufgaben getrennt holen: Fällt eine Quelle aus, soll die
    # andere trotzdem melden. Ein Ausfall, der beide mitnimmt, wäre die
    # Stille, gegen die der Läufer gebaut ist.
    try:
        tage = max(1, (stunden + 23) // 24)
        for t in kalender.termine_lesen(None, tage):
            zeilen.append("📅 " + t.lesbar())
    except Exception as e:
        hinweise.append(f"Termine nicht lesbar ({type(e).__name__})")
    try:
        for a in kalender.aufgaben_lesen():
            zeilen.append("✅ " + a.lesbar())
    except Exception as e:
        hinweise.append(f"Erinnerungen nicht lesbar ({type(e).__name__})")
    return (zeilen, " · ".join(hinweise))


def lauf(stunden: int | None = None, trocken: bool = False) -> int:
    """Ein Durchgang. Rückgabe: Zahl der gemeldeten Zeilen (0 = still)."""
    stunden = stunden or VORSCHAU_STUNDEN
    stand = _stand_laden()
    kopf = ""
    if stand.pop("_beschaedigt", False):
        kopf = ("⚠️ Mein Merkzettel war unlesbar — ich fange von vorn an und "
                "melde deshalb womöglich Bekanntes.\n\n")

    zeilen, hinweis = _faellige(stunden)
    # Ist der Hinweis die EINZIGE Auskunft, wird er zur Meldung — sonst hängt
    # er unten an. Diese Unterscheidung war zuerst an der Zeilenzahl
    # festgemacht (`> 1`), und der Prüfer hat es sofort gefunden: Überlebte
    # genau eine Aufgabe, fiel der Ausfall-Hinweis weg. **Die Zahl war nie das
    # Kriterium — die Frage ist, ob der Hinweis schon dasteht.**
    hinweis_ist_die_meldung = False
    if not zeilen:
        if hinweis:
            # Ein Ausfall ist ein Befund. Er wird gemeldet, aber gedämpft wie
            # alles andere — sonst meldet ein fehlender Zugang stündlich.
            zeilen = [f"⚠️ {hinweis}"]
            hinweis_ist_die_meldung = True
        else:
            if not trocken:
                _stand_schreiben(stand)
            return 0

    schluessel = _schluessel(zeilen)
    bekannt = stand.setdefault("_gemeldet", {})
    jetzt = time.time()
    if jetzt - float(bekannt.get(schluessel, 0)) < WIEDERVORLAGE_S:
        if not trocken:
            _stand_schreiben(stand)
        return 0

    rest = len(zeilen) - MAX_ZEILEN
    text = kopf + "🕰️ Was ansteht:\n\n" + "\n".join(zeilen[:MAX_ZEILEN])
    if rest > 0:
        text += f"\n\n(und {rest} weitere)"
    if hinweis and not hinweis_ist_die_meldung:
        text += f"\n\n⚠️ {hinweis}"
    if not ZIEL_KANAL:
        # **Ehrlich statt vollständig-wirkend:** Ohne Kanal (7.1) landet das
        # hier im Bot-Chat. Das zu verschweigen hieße, einen Zustand als
        # Endzustand auszugeben.
        text += ("\n\n(Noch ohne eigenen Erinnerungskanal — das kommt mit "
                 "Punkt 7.1 in einen eigenen Kanal.)")

    if trocken:
        print(text)
        return len(zeilen)

    try:
        botenpost.legen(text, absender="blume", ziel=ZIEL_KANAL or None)
    except Exception as e:
        # Stand NICHT fortschreiben: Der nächste Lauf soll es erneut versuchen.
        print(f"WARNUNG: Meldung fehlgeschlagen ({type(e).__name__}) — "
              f"Stand NICHT fortgeschrieben")
        return len(zeilen)

    bekannt[schluessel] = jetzt
    # Der Merkzettel darf nicht unbegrenzt wachsen.
    if len(bekannt) > 200:
        for k in [k for k, v in bekannt.items()
                  if jetzt - float(v) > WIEDERVORLAGE_S * 4]:
            bekannt.pop(k, None)
    _stand_schreiben(stand)
    return len(zeilen)


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--trocken", action="store_true",
                   help="nur anzeigen, nichts legen und nichts merken")
    p.add_argument("--stunden", type=int, default=None,
                   help=f"Vorschau-Fenster (Vorgabe {VORSCHAU_STUNDEN})")
    args = p.parse_args()
    n = lauf(args.stunden, args.trocken)
    print(f"{n} Zeile(n)." if n else "Nichts anzusagen.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
