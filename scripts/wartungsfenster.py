#!/usr/bin/env python3
# <!-- ROLLE: wartungsfenster -->
"""B2 + B3 — Wartungsfenster, gekoppelt an den 04:00-Hygiene-Neustart.

**Der Gedanke:** Gelbe (gepinnte) und rote (Major-) Updates brauchen Adams
Einzel-Freigabe. Bisher musste er danach selbst neu starten. Das Fenster nimmt
ihm den Neustart ab — aber nur den, nicht die Entscheidung: Eingespielt wird
**ausschließlich**, was er vorgemerkt hat.

**Warum es an den 04:00-Neustart gekoppelt ist:** Dort wird ohnehin neu
gestartet (Hygiene gegen Langzeit-Degradation). Ein zusätzlicher Neustart wäre
eine zweite Unterbrechung ohne Gewinn.

**Die drei Auflagen (Adam/Conni), alle umgesetzt:**

a) **Vorgemerktes ist in `/updates` sichtbar und stornierbar** — die Vormerkung
   liegt in einer eigenen Datei, die der Bot liest und schreibt.
b) **Nachprüfung zur Ausführungszeit:** Es wird genau die freigegebene Fassung
   eingespielt. Ist inzwischen eine andere verfügbar, wird **nicht** eingespielt,
   sondern neu gefragt — dieselbe Regel wie A3 im Updater.
c) **Morgenmeldung auch dann, wenn nichts lief.** Stille wäre nicht von
   „Fenster kaputt" zu unterscheiden.

**Und die Auflage aus Connis Freigabe — der Probelauf:** B1 ist grün, hat aber
noch nie in einer echten Lage gehandelt; seine drei Schwächen kamen aus einem
Trockenlauf. Ein scharfes Fenster hieße, dass sein erster Ernstfall nachts um
vier stattfindet, während Adam schläft. Deshalb laufen die ersten Läufe als
**Probelauf in Produktion**: Das Fenster prüft, entscheidet und meldet, **was es
getan hätte** — und spielt nichts ein.

**Zum Scharfschalten:** Nach drei sauberen Probeläufen meldet das Fenster, dass
es bereit ist, und **fragt**. Scharf wird es erst, wenn die Marke
`scharf` gesetzt ist. Bewusst kein Selbst-Scharfschalten: Der Schritt, der Adam
aus der Schleife nimmt, ist genau der, den er selbst tun soll.

Deterministisch, ohne Modell-Aufruf (AGB-Leitplanke), ohne Kosten.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import botenpost  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))

STATE_DIR = Path(os.environ.get("UPDATER_STATE_DIR")
                 or (Path.home() / ".claude" / "updater"))
VORGEMERKT = STATE_DIR / "vorgemerkt.json"
PROBELAUF = STATE_DIR / "probelauf.json"
SCHARF = STATE_DIR / "scharf"
POSTFACH = Path(os.environ.get("POSTFACH_DIR")
                or (Path.home() / "postfach")) / "outbox"
PROBELAEUFE_NOETIG = 3


# ------------------------------------------------------------- Vormerkungen --
def vormerkungen() -> list[dict]:
    try:
        daten = json.loads(VORGEMERKT.read_text(encoding="utf-8"))
        return [e for e in daten if isinstance(e, dict) and e.get("name")]
    except Exception:
        return []


def vormerken(name: str, version: str, ampel: str = "gelb") -> None:
    """Trägt eine Freigabe fürs nächste Fenster ein (aus dem Bot aufgerufen)."""
    liste = [e for e in vormerkungen() if e.get("name") != name]
    liste.append({"name": name, "version": version, "ampel": ampel,
                  "freigegeben_am": time.strftime("%Y-%m-%d %H:%M")})
    _schreiben(liste)


def stornieren(name: str) -> bool:
    """(a) Stornieren — solange das Fenster nicht gelaufen ist."""
    liste = vormerkungen()
    neu = [e for e in liste if e.get("name") != name]
    if len(neu) == len(liste):
        return False
    _schreiben(neu)
    return True


def _schreiben(liste: list[dict]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    tmp = VORGEMERKT.with_suffix(".tmp")
    tmp.write_text(json.dumps(liste, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(VORGEMERKT)


def uebersicht() -> str:
    """Für `/updates`: was liegt fürs Fenster bereit? (a)"""
    liste = vormerkungen()
    if not liste:
        return ""
    zeilen = [f"• {e['name']} → {e['version']} "
              f"({'gepinnt' if e.get('ampel') == 'gelb' else 'Major'}, "
              f"freigegeben {e.get('freigegeben_am', '?')})" for e in liste]
    modus = "scharf" if SCHARF.exists() else "Probelauf"
    return ("🌙 Fürs nächste Wartungsfenster (04:00) vorgemerkt — Modus: "
            f"{modus}:\n" + "\n".join(zeilen)
            + "\nStornieren mit /updates und dem Storno-Knopf.")


# ------------------------------------------------------------------ Melden ---
def melden(text: str) -> None:
    """Meldet über die gemeinsame Botenpost — mit Absender.

    Vorher legte jeder Schreiber seine Datei selbst ab, mit vier fast
    gleichen Codeblöcken und OHNE Absender. Als am 26.07. nachts eine
    Meldung bei Adam ankam, kostete die Suche nach ihrem Urheber über
    eine Stunde — die Nachricht hätte es selbst sagen können.
    """
    botenpost.legen(text, "fenster")


def _probelauf_zaehler(sauber: bool) -> int:
    """Zählt saubere Probeläufe; ein unsauberer setzt zurück."""
    try:
        n = int(json.loads(PROBELAUF.read_text(encoding="utf-8")).get("sauber", 0))
    except Exception:
        n = 0
    n = (n + 1) if sauber else 0
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        PROBELAUF.write_text(json.dumps({"sauber": n,
                                         "zuletzt": time.strftime("%Y-%m-%d %H:%M")}),
                             encoding="utf-8")
    except Exception:
        pass
    return n


# ------------------------------------------------------------------- Lauf ----
def lauf() -> int:
    """Ein Fensterlauf. Rückgabe 0 = alles gut, 1 = es gibt etwas zu melden."""
    import updater as upd                              # noqa: PLC0415

    liste = vormerkungen()
    scharf = SCHARF.exists()
    modus = "scharf" if scharf else "Probelauf"

    if not liste:
        # (c) Auch Stille wird gemeldet — sonst ist „nichts vorgemerkt" nicht
        # von „Fenster gar nicht gelaufen" zu unterscheiden.
        melden(f"🌙 Wartungsfenster gelaufen ({modus}) — nichts war vorgemerkt, "
               "es wurde nichts angefasst.")
        return 0

    # (b) Nachprüfung zur Ausführungszeit: genau die freigegebene Fassung.
    try:
        verfuegbar = {u["name"]: u for u in upd.classify()}
    except Exception as e:
        melden(f"🌙 Wartungsfenster ({modus}): Die Update-Prüfung ist "
               f"fehlgeschlagen ({e}). Es wurde nichts angefasst; die "
               "Vormerkungen bleiben liegen.")
        return 1

    passend, abweichend, verschwunden = [], [], []
    for e in liste:
        u = verfuegbar.get(e["name"])
        if u is None:
            verschwunden.append(e)
        elif u["latest"] != e["version"]:
            abweichend.append((e, u["latest"]))
        else:
            passend.append(e)

    meldung: list[str] = [f"🌙 Wartungsfenster ({modus})"]
    if verschwunden:
        meldung.append("• Nicht mehr angeboten (übersprungen): "
                       + ", ".join(f"{e['name']} {e['version']}"
                                   for e in verschwunden))
    if abweichend:
        meldung.append("• Inzwischen eine andere Fassung verfügbar — **nicht** "
                       "eingespielt, ich frage neu: "
                       + ", ".join(f"{e['name']}: freigegeben {e['version']}, "
                                   f"jetzt {neu}" for e, neu in abweichend))

    if not passend:
        meldung.append("• Nichts blieb übrig, das eingespielt werden durfte.")
        melden("\n".join(meldung))
        _schreiben([e for e, _ in abweichend])          # Abweichende bleiben
        return 1

    namen = [e["name"] for e in passend]
    erwartet = {e["name"]: e["version"] for e in passend}

    if not scharf:
        # Der Probelauf: prüfen, entscheiden, melden — aber NICHTS einspielen.
        n = _probelauf_zaehler(True)
        meldung.append("• Ich HÄTTE jetzt eingespielt: "
                       + ", ".join(f"{e['name']} → {e['version']}" for e in passend))
        meldung.append("• Eingespielt wurde nichts — das Fenster läuft als "
                       f"Probelauf ({n} von {PROBELAEUFE_NOETIG} sauber).")
        if n >= PROBELAEUFE_NOETIG:
            meldung.append("\n✅ Drei Probeläufe sind sauber durch. Soll ich das "
                           "Fenster scharf schalten? Dann spielt es Vorgemerktes "
                           "künftig selbst ein — Start-Wächter und Rückweg "
                           "greifen wie immer. Sag Bescheid; von selbst tue ich "
                           "diesen Schritt nicht.")
        melden("\n".join(meldung))
        return 1

    # Scharf: einspielen. Der Updater bringt Grundlinie, Freeze, Rollback,
    # Wiederhol-Schutz und den Start-Wächter selbst mit (A1–A7, B1).
    ergebnis = upd.apply_updates(namen, erwartet)
    meldung.append(f"• {ergebnis.get('msg', '(keine Meldung)')}")
    if ergebnis.get("ok"):
        _schreiben([e for e, _ in abweichend])
        meldung.append("• Der Neustart läuft mit der 04:00-Hygiene mit — kein "
                       "zusätzlicher Unterbruch.")
    else:
        meldung.append("• Die Vormerkungen bleiben liegen, damit nichts "
                       "unbemerkt verfällt.")
        _probelauf_zaehler(False)
    melden("\n".join(meldung))
    return 0 if ergebnis.get("ok") else 1


if __name__ == "__main__":
    sys.exit(lauf())
