#!/usr/bin/env python3
# <!-- ROLLE: auftragsbuch -->
"""B8 Stufe 1 — der Weg, auf dem ein Auftrag ohne Adams Hände ankommt.

**Das Problem, das gelöst wird** (Konzept vom 28.07., Adams Ansage 10:56):
Heute ist Adam die Leitung zwischen den Sitzungen. Ein Bauauftrag entsteht auf
dem Server, er lädt ihn herunter, trägt ihn zur nächsten Sitzung, holt das
Ergebnis ab, bringt es zur Prüfung, trägt den Befund zurück. Vier Wege, jeder
von Hand. **Der Inhalt der Arbeit dauert Minuten, der Transport Stunden** — und
bindet genau die Zeit, um derentwillen das System gebaut wird.

Sein Bild dafür: Wenn die Entwicklung ihn bindet, hat er die grauen Herren
durch die Hintertür hereingelassen.

**Die Gegenrichtung zum Botenpostfach.** Dort legt eine Sitzung etwas ab, das
zu Adam hinaus soll. Hier legt sie etwas ab, das ins System hinein soll. Gleiche
Bauart, gleiche Zurückhaltung: eine Ablagestelle, feste Absenderliste, jede
Nachricht nennt ihren Absender.

**NICHT SCHARFGESTELLT.** Die Verrohrung steht, die Einstufung ist geprüft —
aber `uebernehmen()` verweigert die Übergabe an Horas Auftragsliste, solange
`SCHARF` auf `False` steht. Das ist Connis ausdrückliche Auflage und deckt sich
mit dem Deckel für Adams Abwesenheit: Was wacht, braucht seine Gegenprüfung
vorher; was ruht, darf warten.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

# ---------------------------------------------------------------- Verrohrung
SCHARF = os.environ.get("AUFTRAGSBUCH_SCHARF") == "ja"

BUCH = Path(os.environ.get("AUFTRAGSBUCH_DIR")
            or (Path.home() / ".claude" / "auftragsbuch"))
EINGANG = BUCH / "eingang"
ABGELEGT = BUCH / "abgelegt"

# Feste Absenderliste — ein Absender, den sich jeder ausdenken kann, belegt
# nichts. Dieselbe Überlegung wie beim Botenpostfach.
ABSENDER = ("claudia", "conni", "mick", "hora", "stundenblume")


# ------------------------------------------------------------------- Ampel --
#
# **Hier liegt die eigentliche Sicherheitsfrage dieser Stufe, nicht in der
# Technik.** Das Konzept benennt den gefährlichsten Fall selbst: „Ich stufe
# einen Auftrag falsch als grün ein — etwas wird gebaut, das Adam so nicht
# wollte, und NIEMAND merkt es, bis es auffällt."
#
# Das Gegenmittel steht ebenfalls dort und wird hier wörtlich umgesetzt:
# **Grün gilt nur für eine benannte, geschlossene Liste von Auftragsarten —
# nicht nach dem Urteil im Einzelfall.** Ein Auftrag mit unbekannter Art ist
# NICHT grün; er ist gelb. Wer eine neue grüne Art will, trägt sie hier ein,
# und der Eintrag trägt sein Prüfdatum.
#
# Die Liste ist absichtlich kurz. Jede Erweiterung ist eine Entscheidung, die
# Adam gehört.
GRUENE_ARTEN: dict[str, str] = {
    "fehlerbehebung": "2026-07-28",   # ein belegter Defekt wird behoben
    "test": "2026-07-28",             # eine Prüfung wird ergänzt oder geschärft
    "aufraeumen": "2026-07-28",       # tote Pfade, Doppelungen, Formatarbeit
    "zeichenwechsel": "2026-07-28",   # Beschriftungen, Emojis, Wortlaut
    "doku": "2026-07-28",             # Register, Blaupause, Drehbuch-Stand
}

# Worte, bei denen die Ampel unabhängig von der Art auf Rot springt. Sie sind
# eine ZUSÄTZLICHE Bremse, kein Ersatz für die geschlossene Liste: Eine
# Wortsuche kann man umgehen, ohne es zu wollen.
#
# **KEINE schließende Wortgrenze — und das ist der ganze Punkt.** Der erste
# Entwurf hatte `\b…\b`, und die eigene Prüfung fiel sofort darüber: „Klient"
# schlug an, „Klientendaten" nicht. Ausgerechnet beim heikelsten Wort. Deutsche
# Zusammensetzungen hängen ihr Bestimmungswort vorn an, und eine Wortgrenze
# dahinter macht die Suche für genau die Fälle blind, für die sie da ist —
# Kundenliste, Passwortdatei, Löschauftrag, Kostenstelle.
#
# Der Preis ist ein gelegentlicher Fehlalarm („Absender" enthält kein Muster,
# aber „Abospur" träfe auf `abo`). Bei einer Bremse ist das die richtige
# Richtung: **Lieber einmal zu oft rot als einmal zu wenig.**
ROTE_WORTE = re.compile(
    r"\b(root|sudo|schlüssel|schluessel|token|secret|passwort|kennwort|"
    r"firewall|webhook|öffentlich|oeffentlich|kosten|bezahl|abo|api[_-]?key|"
    r"lösch|loesch|klient|kunde)", re.IGNORECASE)


def einstufen(auftrag: dict) -> tuple[str, str]:
    """(ampel, begründung) — deterministisch, ohne Modell, ohne Urteil.

    Die Reihenfolge ist Absicht: **Rot schlägt Grün.** Ein Aufräum-Auftrag, der
    das Wort „Token" enthält, ist kein Aufräum-Auftrag mehr.
    """
    text = " ".join(str(auftrag.get(f, "")) for f in
                    ("titel", "aktion", "begruendung", "befehl"))
    treffer = ROTE_WORTE.search(text)
    if treffer:
        return ("rot", f"enthält [{treffer.group(0)}] — Sicherheit, Geld oder "
                       "fremde Daten berührt")
    art = str(auftrag.get("art") or "").strip().lower()
    if art in GRUENE_ARTEN:
        return ("gruen", f"Art [{art}] steht seit {GRUENE_ARTEN[art]} auf der "
                         "geschlossenen Grün-Liste")
    if not art:
        return ("gelb", "keine Art angegeben — ohne Art kein Grün")
    return ("gelb", f"Art [{art}] steht nicht auf der Grün-Liste")


# ------------------------------------------------------------------ Ablegen --
def _sicher(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", name.lower()).strip("-") or "ohne-namen"


def legen(auftrag: dict, absender: str) -> Path:
    """Legt einen Auftrag in den Eingang. Gibt den Pfad zurück.

    Der Absender steht **zweimal** darin, im Dateinamen und im Inhalt — der
    Dateiname ist das, was man in einem vollen Ordner sieht, ohne eine Datei zu
    öffnen. Gelernt aus der anonymen Meldung vom 26.07., deren Urheber über eine
    Stunde Suche gekostet hat.
    """
    if absender not in ABSENDER:
        raise ValueError(f"unbekannter Absender: {absender}")
    if not auftrag.get("titel"):
        raise ValueError("ein Auftrag ohne Titel ist keiner")
    ampel, grund = einstufen(auftrag)
    satz = dict(auftrag)
    satz.update({
        "herkunft": absender,
        "ampel": ampel,
        "ampel_grund": grund,
        # Die Einstufung wird MITGESCHRIEBEN, nicht bei jedem Lesen neu
        # gerechnet: Ändert sich die Grün-Liste später, soll nachvollziehbar
        # bleiben, unter welcher Regel dieser Auftrag hereinkam.
        "eingang_am": time.strftime("%Y-%m-%d %H:%M:%S"),
        "braucht_zustimmung": ampel != "gruen",
    })
    EINGANG.mkdir(parents=True, exist_ok=True)
    ziel = EINGANG / f"{time.strftime('%Y%m%d-%H%M%S')}-{absender}-{_sicher(satz['titel'])[:40]}.json"
    ziel.write_text(json.dumps(satz, ensure_ascii=False, indent=2), encoding="utf-8")
    return ziel


def eingang() -> list[dict]:
    """Alles, was wartet — nach Eingangszeit, ältestes zuerst."""
    if not EINGANG.is_dir():
        return []
    raus = []
    for datei in sorted(EINGANG.glob("*.json")):
        try:
            satz = json.loads(datei.read_text(encoding="utf-8"))
        except Exception:
            continue                       # unlesbar: liegen lassen, nicht raten
        satz["_datei"] = str(datei)
        raus.append(satz)
    return raus


def uebersicht() -> str:
    """Eine Zeile je Auftrag — das, was Adam im Chat sehen soll.

    Das Konzept verspricht ihm **eine Zeile** statt eines Dokuments: worum es
    geht, Ampelfarbe, ein Knopf. Mehr wäre wieder Transport.
    """
    wartend = eingang()
    if not wartend:
        return "📋 Auftragsbuch: nichts offen."
    zeichen = {"gruen": "🟢", "gelb": "🟡", "rot": "🔴"}
    zeilen = [f"📋 Auftragsbuch — {len(wartend)} offen:"]
    for a in wartend:
        zeilen.append(f"{zeichen.get(a.get('ampel'), '🟡')} {a['titel']} "
                      f"· von {a.get('herkunft', '?')}")
    if not SCHARF:
        zeilen.append("\n⏸️ Die Übergabe an Hora ist noch nicht scharfgestellt — "
                      "die Aufträge liegen, es läuft nichts von allein an.")
    return "\n".join(zeilen)


# --------------------------------------------------------------- Übergeben --
def uebernehmen(hora_liste: Path | None = None) -> tuple[int, str]:
    """Reicht **grüne** Aufträge an Horas Liste weiter. (Anzahl, Meldung)

    **Der Riegel.** Solange `SCHARF` nicht gesetzt ist, geschieht hier nichts —
    und zwar mit Meldung, nicht stillschweigend. Ein Übergang, der leise
    nichts tut, sähe aus wie ein Übergang, der leise alles tut; von außen ist
    beides dieselbe Ruhe.

    Gelb und Rot werden **nie** hier übergeben. Sie warten auf Adams Daumen
    über die Freigabe-Leitung (9.4) — der Knopf ist ein Vorgang, kein Vortrag.
    """
    wartend = [a for a in eingang() if a.get("ampel") == "gruen"]
    if not SCHARF:
        return (0, f"nicht scharfgestellt — {len(wartend)} grüne Aufträge "
                   "warten, es wurde nichts übergeben")
    if not wartend:
        return (0, "nichts Grünes im Eingang")

    ziel = hora_liste or Path(os.environ.get("HORA_LISTE")
                              or (Path.home() / ".claude" / "hora" / "auftragsliste.json"))
    try:
        daten = json.loads(ziel.read_text(encoding="utf-8"))
        if not isinstance(daten, list):
            daten = []
    except Exception:
        daten = []
    vorhanden = {a.get("titel") for a in daten if isinstance(a, dict)}

    uebernommen = 0
    for a in wartend:
        if a["titel"] in vorhanden:
            continue                       # schon in der Liste: nicht doppeln
        satz = {k: v for k, v in a.items() if not k.startswith("_")}
        daten.append(satz)
        uebernommen += 1
        ABGELEGT.mkdir(parents=True, exist_ok=True)
        Path(a["_datei"]).replace(ABGELEGT / Path(a["_datei"]).name)
    ziel.parent.mkdir(parents=True, exist_ok=True)
    tmp = ziel.with_suffix(".tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(ziel)
    return (uebernommen, f"{uebernommen} grüne Aufträge an Hora übergeben")


if __name__ == "__main__":
    print(uebersicht())
