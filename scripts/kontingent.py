#!/usr/bin/env python3
# <!-- ROLLE: kontingent-abrufer -->
"""Kontingent-Stand abfragen — A2. **ÜBERHOLT, NICHT IN BETRIEB.**

⚠️ **BERICHTIGT 20.08.2026:** Die Begründung unten — das Ereignis feuere
nur bei einem *Zustandswechsel* — **ist falsch**, und sie war der Grund,
warum A2 als nicht baubar galt. Im CLI-Bündel gemessen: Der Setzer läuft
unter ``if(!isEqual(alt, neu))``, einem **tiefen Wertvergleich**. Es genügt,
dass sich ``utilization`` ändert — und das tut sie mit jeder Anfrage.

Die Zahl steht ohnehin in den Kopfzeilen jeder Antwort
(``anthropic-ratelimit-unified-<fenster>-utilization``). **Es gibt nichts
abzufragen.** Der Bau sitzt in ``bot.py`` (``_limit_letzten_merken``,
``cmd_kontingent``), der Prüfer in ``scripts/test_kontingent_a2.py``.

Diese Datei bleibt als Beleg des gescheiterten Wegs stehen und wird beim
Abschluss-Audit (Phase 10, Entrümpelung) entfernt — nicht früher, weil
Aufräumen die gefährlichere Art von Arbeit ist.

Ursprünglicher Kopf:


**Wofür:** Adams einzige Warnung kam bei 97 Prozent, Sekunden bevor nichts mehr
ging. Er will Stufen bei **80, 85, 90 und 95**.

**Warum der bisherige Weg das nicht hergibt:** Das `RateLimitEvent` des SDK
feuert nur bei einem **Zustandswechsel** (`allowed` → `allowed_warning` →
`rejected`). Es gibt genau einen Warnzustand, und wann er auslöst, bestimmt der
Anbieter. Und ein eigener Zähler im Bot sähe nicht, was Adam am Desktop oder im
Browser verbraucht — sein berechtigter Einwand vom 20.08., 09:57.

**Der Weg, der bleibt — und seine Sollbruchstelle, offen benannt:** Es gibt
einen **undokumentierten** Endpunkt, der am Konto hängt statt an einer Sitzung.
Damit zählen Desktop und Browser mit. Undokumentiert heißt: **Anthropic kann
ihn jederzeit ändern, und dann verstummt der Abrufer** — genau die Fehlerklasse,
gegen die A1 gebaut wurde. Deshalb meldet er seinen eigenen Ausfall (siehe
`AUSFALL_SCHWELLE`), und die Anbieter-Warnung im Bot bleibt als Rückfallebene
unangetastet.

**💰 Keine Kosten:** derselbe Zugang, den Claude Code ohnehin benutzt, derselbe
Anbieter, ein GET auf einen Zählerstand. Keine Token-Abrechnung, kein
Drittdienst, kein zusätzlicher Datenabfluss.

**🔐 Das Token wird gelesen, nie gezeigt:** ausschließlich aus der Umgebung,
nie als Argument, nie in einer Protokollzeile, nie in einer Fehlermeldung.
Deshalb fängt der Aufruf jede Ausnahme selbst ab — eine durchgereichte
`HTTPError` kann die Anfrage samt Kopfzeilen enthalten.

## ⚠️ NICHT IN BETRIEB (Stand 20.08.2026)

**Der Probeaufruf ist gescheitert: HTTP 403 in drei Kopfzeilen-Varianten.**
Nicht 404 (der Endpunkt existiert), nicht 401 (das Token wird erkannt) —
403 heißt erkannt und **nicht berechtigt**. Der Bot läuft mit einem
**Setup-Token** (`sk-ant-oat…`); der Endpunkt ist offenbar für das
Sitzungs-Token aus `claude login` gedacht.

Dieses Modul ist **nirgends eingebunden** — kein Zeitgeber, kein Aufruf aus
dem Bot, keine Schwellenlogik. Es bleibt als fertiger Rückweg liegen, falls
der Zugang je verfügbar wird. Maßgebliche Auskunft:
`docs/befund-a2-kontingent.md`.

Aufruf: ``python3 scripts/kontingent.py [--probe]``
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

USAGE_URL = "https://api.anthropic.com/api/oauth/usage"
BETA_HEADER = "oauth-2025-04-20"
ZEITGRENZE_S = 15

# Nach so vielen erfolglosen Abrufen in Folge geht EINE Meldung an Adam,
# danach Ruhe bis zur Besserung. Ein Abrufer, der bei jedem Fehlversuch meldet,
# wird beim ersten Netzwackler zur Störquelle; einer, der nie meldet, verstummt
# unbemerkt — und das ist der Fehler, gegen den er gebaut wurde.
AUSFALL_SCHWELLE = 2


class NichtVerfuegbar(RuntimeError):
    """Der Endpunkt antwortet nicht wie erwartet — mit knappem Grund.

    **Der Grund ist bewusst knapp.** Er wandert in Protokolle und Meldungen;
    eine durchgereichte Ausnahme des HTTP-Moduls kann die Anfrage samt
    Kopfzeilen enthalten, und dort steht das Token.
    """


def _token() -> str:
    """Das Abo-Token aus der Umgebung — **niemals aus einer Datei im Repo.**"""
    tok = (os.environ.get("CLAUDE_CODE_OAUTH_TOKEN") or "").strip()
    if not tok:
        raise NichtVerfuegbar("kein Abo-Token in der Umgebung")
    return tok


def abrufen(timeout: float = ZEITGRENZE_S) -> dict:
    """Die drei Auslastungen holen. Wirft `NichtVerfuegbar`, sonst ein dict.

    Rückgabe je Fenster: `{"utilization": 0.42, "resets_at": "…"}` — die Form
    bestimmt der Anbieter, nicht wir. Deshalb wird sie beim Auswerten geprüft
    und nicht vorausgesetzt.
    """
    anfrage = urllib.request.Request(USAGE_URL, headers={
        "Authorization": f"Bearer {_token()}",
        "anthropic-beta": BETA_HEADER,
        "Accept": "application/json",
    })
    try:
        with urllib.request.urlopen(anfrage, timeout=timeout) as antwort:
            roh = antwort.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        # NUR der Code, nicht die Ausnahme: Ihre Darstellung kann die Anfrage
        # samt Authorization-Kopfzeile enthalten.
        raise NichtVerfuegbar(f"HTTP {e.code}") from None
    except Exception as e:
        raise NichtVerfuegbar(f"nicht erreichbar ({type(e).__name__})") from None
    try:
        daten = json.loads(roh)
    except Exception:
        raise NichtVerfuegbar("Antwort ist kein JSON") from None
    if not isinstance(daten, dict):
        raise NichtVerfuegbar("Antwort hat eine unerwartete Form")
    return daten


def _prozent(eintrag) -> float | None:
    """Die Auslastung als Prozentwert — oder None, wenn die Form nicht passt.

    **Die Form wird geprüft, nicht vorausgesetzt.** Ein undokumentierter
    Endpunkt darf sie ändern; dann soll der Abrufer schweigen und nicht raten.
    """
    if not isinstance(eintrag, dict):
        return None
    wert = eintrag.get("utilization")
    if isinstance(wert, (int, float)):
        # Der Anbieter liefert 0..1; ein Wert über 1 wäre bereits Prozent.
        return float(wert) * 100.0 if wert <= 1.0 else float(wert)
    return None


def stand() -> dict[str, float]:
    """Fenster-Name → Auslastung in Prozent. Leer, wenn nichts lesbar war."""
    daten = abrufen()
    raus = {}
    for name, eintrag in daten.items():
        p = _prozent(eintrag)
        if p is not None:
            raus[str(name)] = p
    return raus


def main() -> int:
    probe = "--probe" in sys.argv
    try:
        werte = stand()
    except NichtVerfuegbar as e:
        print(f"NICHT VERFÜGBAR: {e}")
        # Für den Probelauf ist das ein gültiges Ergebnis, kein Absturz:
        # Claudias Auftrag sagt ausdrücklich, dann ende er als „nicht baubar".
        return 0 if probe else 1
    if not werte:
        print("NICHT VERFÜGBAR: Antwort enthielt keine lesbare Auslastung")
        return 0 if probe else 1
    for name, p in sorted(werte.items()):
        print(f"{name}: {p:.1f} %")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
