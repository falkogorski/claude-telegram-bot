#!/usr/bin/env python3
# <!-- ROLLE: wachmuster -->
"""Die Muster, auf die der Log-Wachposten anschlägt — **eine Quelle**.

**Warum eine eigene Datei** (Vorbild `authmarke.py`, G1-Lehre): Eine zweite
Liste über dieselbe Frage driftet. Am 26.07. gingen die Anmelde-Marken um genau
ein Wort auseinander (`oauth token expired` gegen `oauth token **has**
expired`) — der Wächter hätte den Fall, für den er gebaut wurde, nicht erkannt.

**Beidseitig offene Wortgrenzen** (Stichwort-Filter-Regel, 18.08.): Deutsche
Zusammensetzungen hängen ihr Bestimmungswort vorn an, das Grundwort steht
hinten. `\\bkosten\\b` verfehlt „Zusatzkosten" ebenso wie „Kostenstelle". Also
keine Grenze auf keiner Seite — der Preis sind Fehlalarme, und die fängt die
kurze Ausnahmeliste unten ab.
"""
from __future__ import annotations

import re

# Jede Gruppe trägt eine **Kennung** (für den Dämpfer) und eine **Anzeige**
# (für Adam). Die Kennung wandert ins Gedächtnis, die Anzeige in die Meldung —
# dieselbe Trennung wie bei den Stundenblumen, wo ein Zeitstempel im Befundtext
# am 28.07. den Dämpfer aushebelte.
MUSTER: list[tuple[str, str, re.Pattern]] = [
    ("absturz", "Ein Absturz oder Fehlerabbruch",
     re.compile(r"(Traceback|Unhandled|FATAL|CRITICAL)")),
    ("fehlerzeile", "Eine als Fehler markierte Zeile",
     re.compile(r"(❌|✗|FEHLGESCHLAGEN|fehlgeschlagen)")),
    ("api-stoerung", "Eine Störung beim Anbieter",
     re.compile(r"(API Error|api error|\b5\d{2}\b\s*(Server|Error|Overloaded)"
                r"|Overloaded|rate limit|Bad Gateway)")),
    ("kosten", "Ein Wort, das nach Geld klingt",
     re.compile(r"(kosten|gebuehr|gebühr|abrechnung|rechnung|bezahl|"
                r"ANTHROPIC_API_KEY|pay-per|billing)", re.IGNORECASE)),
    ("geheimnis", "Ein Wort, das nach einem Geheimnis klingt",
     re.compile(r"(passwort|kennwort|token|secret|api[_-]?key|"
                r"schluessel|schlüssel|credential)", re.IGNORECASE)),
    ("freigabe-offen", "Eine Freigabe-Anfrage, die auf Antwort wartet",
     re.compile(r"(wartet auf (deine |Adams )?(Freigabe|Zustimmung|Daumen)|"
                r"unbeantwortet|zur Freigabe vorgelegt)", re.IGNORECASE)),
]

# **Wörter, die ein Muster nur ZUFÄLLIG enthalten.** Bewusst kurz: Eine lange
# Ausnahmeliste höhlt die Wache aus, und jede Zeile hier ist eine Entscheidung,
# kein Automatismus. Sie werden VOR der Suche entfernt — sonst verdeckte ein
# einzelnes „kostenlos" einen echten Treffer im selben Satz.
#
# Auch hier KEINE schließende Wortgrenze: „kostenlose" trägt eine
# Beugungsendung, und genau daran ist die Ausnahmeliste des Auftragsbuchs am
# 18.08. beim ersten Anlauf gescheitert.
AUSNAHMEN = re.compile(
    r"\b(kostenlos|kostenfrei|kostenguenstig|kostengünstig|unentgeltlich|"
    r"tokenisier|Tokenizer|token_count|schluesselfertig|schlüsselfertig)",
    re.IGNORECASE)


# **Die Quelle bestimmt die Schwelle** — gemessen am 19.08. an echten Daten.
#
# Der erste Entwurf ließ eine reale Zeile aus `bot-errors.log` durchfallen:
# `2026-08-16 | postfach send | TimedOut: Timed out`. Kein Muster traf, und das
# war kein Musterfehler, sondern ein Denkfehler: **In einer Fehlerdatei ist
# jede neue Zeile bereits der Befund.** Dort nach Fehlermerkmalen zu suchen,
# heißt zu prüfen, ob ein Fehler auch wirklich einer ist.
#
# Im Gesprächsprotokoll ist es umgekehrt — dort sind fast alle Zeilen harmlos,
# und nur die Muster machen eine auffällig.
IMMER_MELDEN = {"bot-errors.log"}


def treffer(zeile: str, quelle: str = "") -> list[tuple[str, str]]:
    """(kennung, anzeige) je angeschlagenem Muster. Leer = unauffällig.

    `quelle` ist der Dateiname: Steht er in `IMMER_MELDEN`, gilt jede
    nichtleere Zeile als Befund — auch wenn kein Muster greift.
    """
    text = AUSNAHMEN.sub(" ", zeile or "")
    gefunden = [(k, a) for k, a, muster in MUSTER if muster.search(text)]
    if gefunden:
        return gefunden
    if quelle in IMMER_MELDEN and (zeile or "").strip():
        return [("fehlerdatei", "Eine neue Zeile in der Fehlerdatei")]
    return []
