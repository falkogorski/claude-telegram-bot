#!/usr/bin/env python3
# <!-- ROLLE: hora -->
"""Hora — der autonome Läufer.

**Wofür:** Adam ist ab Dienstag rund vierzehn Tage nicht erreichbar. Ein
Zeitgeber auf dem **VPS** startet zweimal täglich eine **frische**,
nicht-interaktive Sitzung, die eine **vorab freigegebene** Auftragsliste
abarbeitet, berichtet und endet.

**Warum nicht auf dem Mac:** Ein Rechner, der vierzehn Tage wach bleiben muss,
ist das zerbrechlichste Glied der Kette.

**Warum je Lauf eine frische Sitzung:** Eine Sitzung, die vierzehn Tage lebt,
stirbt sicher. Hora liest seinen Zustand stattdessen aus Drehbuch, Status-Zeilen,
Auftragsliste und `WIEDERANLAUF.md` — also aus dem, was ohnehin die Wahrheit ist.

**Kein Widerspruch zu 8.7:** Die Repo-Schreibsperre gilt der **Bot-Sitzung**,
nicht jedem Prozess auf dem Server. Hora ist eine getrennte Instanz mit eigenem
Auftragsbuch.

## Die fünf Bedingungen — jede im Code, nicht nur im Text

1. **Nur vorab freigegebene Arbeit, keine neuen Entscheidungen.** Was Adams
   Zustimmung bräuchte, wird über **9.4 geparkt**, nicht entschieden.
2. **Die Liste muss voll sein, bevor Adam geht** — ist sie leer, meldet Hora das
   und tut nichts.
3. **Jeder Lauf endet grün oder rollt zurück.** Der Regressionslauf ist das Maß;
   ein roter Stand wird nicht stehen gelassen.
4. **Abbruchkriterium:** Nach drei Fehlläufen in Folge wird **gemeldet statt
   weitergearbeitet**. Ein Läufer, der gegen dieselbe Wand rennt, richtet mehr
   Schaden an als einer, der stehen bleibt.
5. **Tagesbericht ins Postfach** — auch wenn nichts zu tun war.

## Zur Kontingent-Frage — bewusst ohne Annahme gebaut

Die Wochengrenzen des Abos lassen sich von hier aus **nicht** messen. Statt sie
zu raten, ist Hora so gebaut, dass er sie **nicht kennen muss**. Die
Limit-Behandlung des Bots (5.31) trägt den Rest — beim Anschlagen wird pausiert
und später fortgesetzt.

**[KORRIGIERT 2026-07-25] „Einer je Lauf" war eine Über-Korrektur.** Zwei Läufe
täglich mal vierzehn Tage sind achtundzwanzig Aufträge — das wäre die Obergrenze
für zwei Wochen gewesen, und von einem Fünf-Stunden-Fenster bliebe fast alles
ungenutzt. Vor allem aber war „einer je Lauf" **selbst eine Annahme**, nämlich
die, dass das Kontingent knapp ist. Genau davon wollte der Entwurf frei sein.

Neu: **Frische Sitzung je Auftrag** (die Isolation bleibt, sie war richtig) —
aber **verkettet, bis die Liste leer ist**, die Kontingent-Pause greift oder die
Fehlserie zuschlägt. Keine Zahl zum Nachjustieren: Es läuft, bis es nicht mehr
kann.

## Fragen sind Wegsteine, keine Halteschilder [NEU 2026-07-25]

**Hora wartet nie.** Braucht ein Auftrag Adams Zustimmung: **parken (9.4),
melden, sofort mit dem nächsten unabhängigen Auftrag weiter.** Ist nichts
Unabhängiges mehr zu tun, endet der Lauf mit Bericht — er steht nicht im
Leerlauf herum. Ein geparkter Punkt blockiert auch den **nächsten** Lauf nicht.

Damit braucht es keine Vorhersage über Adams Verfügbarkeit: **immer fragen, nie
warten.** Die Antwort holt den Läufer später ein, nicht umgekehrt.

Daraus folgt eine Anforderung an die Auftragsliste: **Abhängigkeiten werden
markiert** (`haengt_an: ["<Titel>"]`). Nur so weiß Hora, was unabhängig
weiterlaufen darf, wenn ein Vorgänger geparkt oder gescheitert ist.

Aufruf: ``python3 scripts/hora.py [--liste …] [--trocken]``
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import auftragsbuch  # noqa: E402
import botenpost  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import freigaben  # noqa: E402

ZUSTAND = Path(os.environ.get("HORA_DIR") or (Path.home() / ".claude" / "hora"))
LISTE = Path(os.environ.get("HORA_LISTE") or (ZUSTAND / "auftragsliste.json"))
PROTOKOLL = ZUSTAND / "laeufe.jsonl"
POSTFACH = Path(os.environ.get("POSTFACH_DIR")
                or (Path.home() / "postfach")) / "outbox"
FEHLGRENZE = 3
REGRESSION = REPO / "scripts" / "regressionstest.sh"

# Wortlaute, an denen ein erreichtes Kontingent erkennbar ist. Bewusst hier
# gespiegelt statt aus bot.py importiert: Hora soll ohne dessen Umgebung laufen.
_LIMIT = ("usage limit", "session limit", "rate limit", "limit reached",
          "quota exceeded", "kontingent", "too many requests", "429")


def _kontingent_erschoepft(text: str) -> bool:
    t = (text or "").lower()
    return any(n in t for n in _LIMIT)


# ---------------------------------------------------------- Lauf-Schloss ----
# **Warum es das braucht (Conni, 28.07., zum Zweistunden-Takt):** Ein
# verketteter Lauf kann länger dauern als der Abstand zum nächsten. Ohne
# Schloss liefe der zweite **parallel in dieselbe Liste** — doppelte
# Sitzungen, zwei Läufe, die denselben Auftrag abhaken wollen, und Kontingent
# doppelt belastet. Bei zweimal täglich war das theoretisch; bei zwölfmal ist
# es eine Frage der Zeit.
#
# **Bauart aus dem Updater gespiegelt (A4), nicht neu erfunden** — samt der
# Alterung: Ein abgestürzter Lauf darf das Schloss nicht ewig halten, sonst
# schweigt Hora bis zur Rückkehr, und niemand merkt es.
SCHLOSS = ZUSTAND / "lauf.lock"
SCHLOSS_ALT_S = int(os.environ.get("HORA_SCHLOSS_ALT") or 4 * 3600)


def _schloss_nehmen() -> bool:
    ZUSTAND.mkdir(parents=True, exist_ok=True)
    try:
        if SCHLOSS.exists():
            alter = time.time() - SCHLOSS.stat().st_mtime
            if alter < SCHLOSS_ALT_S:
                return False
            SCHLOSS.unlink(missing_ok=True)      # verwaistes Schloss räumen
        fd = os.open(str(SCHLOSS), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, f"{os.getpid()} {time.strftime('%Y-%m-%d %H:%M:%S')}\n".encode())
        os.close(fd)
        return True
    except FileExistsError:
        return False
    except Exception:
        return True          # ein Schloss darf den Betrieb nie ganz blockieren


def _schloss_geben() -> None:
    SCHLOSS.unlink(missing_ok=True)


# ------------------------------------------------- Dämpfer für den Leerlauf --
# **Auch das eine Folge des Takts:** `lauf()` meldet bei leerer Liste jedes Mal,
# dass nichts zu tun war. Zweimal täglich ist das eine Auskunft — zwölfmal
# täglich über vierzehn Tage sind **168 gleichlautende Nachrichten**, und wer
# gelernt hat, diesen Absender zu überlesen, überliest auch die eine, die zählt.
#
# Dieselbe Lösung wie bei den Stundenblumen: **erste Meldung sofort**, danach
# frühestens einmal am Tag, solange sich nichts ändert.
LEERLAUF_MARKE = ZUSTAND / "leerlauf.json"
LEERLAUF_STILLE_S = int(os.environ.get("HORA_LEERLAUF_STILLE") or 24 * 3600)


def _leerlauf_melden(jetzt: float | None = None) -> bool:
    """Darf der Leerlauf gemeldet werden? Beim ersten Mal ja, dann täglich."""
    now = jetzt or time.time()
    try:
        zuletzt = float(json.loads(
            LEERLAUF_MARKE.read_text(encoding="utf-8")).get("zuletzt", 0))
    except Exception:
        zuletzt = 0.0
    if now - zuletzt < LEERLAUF_STILLE_S:
        return False
    try:
        ZUSTAND.mkdir(parents=True, exist_ok=True)
        LEERLAUF_MARKE.write_text(json.dumps({"zuletzt": now}), encoding="utf-8")
    except Exception:
        pass
    return True


def _leerlauf_entwarnen() -> None:
    """Sobald wieder Arbeit da war, gilt die nächste Leere als neue Auskunft."""
    LEERLAUF_MARKE.unlink(missing_ok=True)


# **Die Ausnahmen kommen vor der Suche** — dieselbe Bauart wie beim
# Stichwort-Filter: Grenzen offen, dafür eine kurze, ausdrücklich benannte
# Ausnahmeliste. Ohne sie meldete „✓ fehlerfrei durchgelaufen" einen Fehler.
_ROT_AUSNAHMEN = re.compile(
    r"(fehlerfrei|fehlerlos|keine\s+fehler|ohne\s+fehler|null\s+fehler|"
    r"0\s+fehler|fehler:\s*0|fehlgeschlagen:\s*0|0\s+error|no\s+error)",
    re.IGNORECASE)

# Woran eine auffällige Zeile erkennbar ist. Bewusst breit: Unsere Prüfskripte
# benutzen ✗ und ❌, Python meldet Traceback und Error, bash meldet „command not
# found". Ein zu enges Muster fände genau die Ausgabe nicht, die neu ist.
#
# **F-2: Es war trotzdem zu eng — und zwar auf Deutsch.** Gemessen waren sechs
# von acht typischen Fehlerzeilen blind, darunter `Fehler:`, `ERROR:` (das
# Muster lief ohne IGNORECASE) und `failed`. In einem durchweg
# deutschsprachigen Projekt fand die Fehlersuche das deutsche Wort für Fehler
# nicht. Die Grenzen bleiben nach der Stichwort-Regel **beidseitig offen** —
# „Startfehler" trägt das Grundwort hinten.
_ROT_ZEILE = re.compile(
    r"(✗|❌|fehlgeschlagen|fehler|traceback|error|failed|failure|"
    r"abgebrochen|abbruch|not found|nicht gefunden|no such file|"
    r"permission denied|verweigert|refused|timeout|zeitüberschreitung)",
    re.IGNORECASE)


def _ist_rot(zeile: str) -> bool:
    """Auffällig — nach Abzug der Ausnahmen."""
    return bool(_ROT_ZEILE.search(_ROT_AUSNAHMEN.sub(" ", zeile or "")))


# Wie viel Ausgabe wir überhaupt festhalten. Der Wert ist großzügig, weil die
# MELDUNG ohnehin auf drei Zeilen à 160 Zeichen gedeckelt ist — hier geht es
# nur darum, dass die Suche etwas zu suchen hat.
_AUSGABE_GRENZE = 200_000


def _verdichten(text: str) -> str:
    """Begrenzt die Ausgabe, **ohne den Anfang wegzuwerfen** (F-2).

    Vorher wurde auf die letzten 1200 Zeichen gekürzt, **bevor** `_fehlgrund`
    darin suchte. Gemessen: Eine rote Zeile im Kopf, 200 Zeilen Geschwätz
    danach — gemeldet wurde „der Befehl meldete: ok, alles gut". Korrekt und
    vollkommen nutzlos, also genau der Halt vom 28.07., den der Kommentar in
    `_fehlgrund` beschreibt. Die Kürzung hatte die Positionsannahme, die dort
    beseitigt wurde, durch die Hintertür wieder eingeführt.

    Deshalb bleiben **beide Enden** stehen: Der Anfang trägt meist die
    Ursache, das Ende die Wirkung.
    """
    if len(text) <= _AUSGABE_GRENZE:
        return text
    haelfte = _AUSGABE_GRENZE // 2
    fehlt = len(text) - 2 * haelfte
    return (text[:haelfte]
            + f"\n[… {fehlt} Zeichen ausgelassen …]\n"
            + text[-haelfte:])


def _fehlgrund(erfolg: bool, nachher_ok: bool, ausgabe: str,
               lage: str) -> str:
    """Sagt, **woran** es lag — und unterscheidet die zwei Fälle.

    Ein Auftrag kann auf zwei ganz verschiedene Arten scheitern, und sie
    verlangen verschiedene Antworten: Entweder der **Befehl** ging schief (dann
    zählt seine Ausgabe), oder der Befehl lief und hat dabei **etwas anderes
    kaputtgemacht** (dann zählt der Regressionsstand — und das ist der weit
    ernstere Fall, weil er den Rückweg verlangt).
    """
    if not erfolg:
        text = (ausgabe or "").strip()
        if not text:
            return ("der Befehl endete mit einem Fehler, ohne etwas zu sagen "
                    "(kein Text auf beiden Ausgabekanälen)")
        # **Die letzte Zeile ist eine Positionsannahme, kein Inhaltsmerkmal**
        # (Halt vom 28.07., 16:15). Der Selbstcheck gibt neunundzwanzig Zeilen
        # aus, eine davon rot — und die stand mittendrin. Gemeldet wurde
        # stattdessen die letzte, eine grüne. Die Aussage war damit korrekt und
        # vollkommen nutzlos: „der Befehl meldete: ✓ Medien-Eingangsschutz".
        #
        # Adam hätte in seiner Abwesenheit keine Möglichkeit gehabt, das
        # aufzulösen; jede Diagnose hätte eine Hand gebraucht, die nicht da ist.
        # Also werden die AUFFÄLLIGEN Zeilen gesucht, nicht die letzte.
        auffaellig = [z.strip() for z in text.splitlines()
                      if _ist_rot(z)]
        if auffaellig:
            # Höchstens drei — eine Meldung, die dreißig rote Zeilen mitschleppt,
            # wird nicht gelesen, und die ersten sagen ohnehin das Meiste.
            gekuerzt = [z[:160] for z in auffaellig[:3]]
            rest = len(auffaellig) - len(gekuerzt)
            schluss = f" (und {rest} weitere)" if rest > 0 else ""
            return "der Befehl meldete: " + " · ".join(gekuerzt) + schluss
        return "der Befehl meldete: " + text.splitlines()[-1][:200]
    if not nachher_ok:
        return (f"der Befehl lief durch, aber DANACH war der Regressionslauf "
                f"rot ({lage}) — hier hat die Arbeit etwas anderes beschädigt")
    return f"unklar ({lage})"


def _urteil_einholen(auftrag: dict) -> tuple[str, str]:
    """Die Parkstrecke — **und der Weg zurück.**

    **Der Fund, dem diese Funktion ihr Dasein verdankt (Echtlauf 26.07., 01:45):**
    Ein geparkter Auftrag wurde vorher **abgehakt**. Er verschwand damit aus der
    Liste — und Adams Zustimmung wäre ins Leere gelaufen, weil niemand die
    Aktion danach je ausgeführt hätte. Die Meldung sagte „ich lege es dir wieder
    vor", und der Code hatte den Auftrag bereits weggeräumt. Der Grundsatz
    lautet „die Antwort holt ihn später ein, nicht umgekehrt" — dafür muss
    etwas da sein, das eingeholt werden kann.

    Rückgabe: (Lage, Text). Lagen:
    * ``wartet`` — Anfrage liegt (neu gestellt oder noch unbeantwortet)
    * ``freigegeben`` — Adam hat zugestimmt, der Auftrag darf jetzt laufen
    * ``abgelehnt`` — Adam hat abgelehnt; damit ist der Auftrag erledigt
    * ``unparkbar`` — die Anfrage verletzt eine Leitplanke (z. B. Geheimnis)
    """
    kennung = auftrag.get("freigabe_kennung")
    if kennung:
        urteil = freigaben.urteil_lesen(kennung)
        if urteil:
            return (("freigegeben", "von dir freigegeben")
                    if urteil.get("urteil") == "freigegeben"
                    else ("abgelehnt", "von dir abgelehnt"))
        # Kein Urteil und keine offene Anfrage mehr? Dann ist sie verlorengegangen
        # — neu stellen ist richtiger als schweigen.
        if freigaben.finden(kennung) is not None:
            return "wartet", "liegt bei dir"
    try:
        a = freigaben.stellen(
            titel=auftrag["titel"],
            aktion=auftrag.get("aktion") or auftrag["titel"],
            ampel=auftrag.get("ampel", "gelb"),
            herkunft="Hora",
            begruendung=auftrag.get("begruendung", ""),
            rueckweg=auftrag.get("rueckweg", ""))
    except freigaben.Abgewiesen as e:
        return "unparkbar", str(e)
    _vermerken(auftrag["titel"], freigabe_kennung=a.kennung,
               geparkt_am=time.strftime("%Y-%m-%d %H:%M"))
    return "wartet", "neu vorgelegt"


# ------------------------------------------------- E3: Wiederkehrende Läufe --
#
# **Adams Entscheid vom 18.08., vier Festlegungen — hier alle im Code.**
#
# Ein wiederkehrender Auftrag wird beim Abhaken nicht beendet, sondern auf seine
# nächste Fälligkeit gesetzt. Vor der Fälligkeit wird er übersprungen, **ohne zu
# melden** — sonst wäre die Liste ein Dauerfunk.
#
# **Die geschlossene Liste ist der ganze Riegel.** Nur lesende Prüf-Arten dürfen
# wiederkehren; alles Verändernde bleibt einmalig, ohne Ausnahme. Der Grund ist
# nicht Vorsicht, sondern Arithmetik: Ein verändernder Auftrag, der alle drei
# Tage von selbst wieder anläuft, ist keine Aufgabe mehr, sondern ein Prozess —
# und den hat niemand beschlossen.
WIEDERKEHR_ARTEN: dict[str, str] = {
    "kette-bewerten": "2026-08-18",    # liest die Belegkette und urteilt
    "register-pruefen": "2026-08-18",  # liest Register und Prüfbefehle
    "vorraete": "2026-08-18",          # liest Speicher, Platte, Auslagerung
    "pruefen": "2026-08-18",           # allgemeiner Prüflauf, rein lesend
}


def wiederkehr_erlaubt(auftrag: dict) -> tuple[bool, str]:
    """(erlaubt, Begründung) — **geprüft am ÜBERGANG, nicht am Eintrag.**

    Dieselbe Bauart wie der Riegel im Auftragsbuch, und aus demselben Grund:
    Dort las `uebernehmen()` die Ampel aus der Datei, und eine handgelegte
    Grün-Behauptung rutschte durch. **Die Angabe im Auftrag ist ein Vorschlag,
    nie eine Wahrheit** — maßgeblich ist die Einstufung in dem Moment, in dem
    sie wirkt. Das fängt zugleich den zweiten Fall: Wird eine Art später aus
    dieser Liste entfernt, weil sie sich als verändernd erwies, hören auch
    bereits liegende Aufträge auf zu wiederkehren.
    """
    tage = auftrag.get("wiederkehrend")
    if not tage:
        return (False, "kein Wiederkehr-Feld")
    art = str(auftrag.get("art") or "")
    if art not in WIEDERKEHR_ARTEN:
        return (False, f"Art [{art or 'ohne'}] steht nicht auf der "
                       "geschlossenen Liste lesender Prüf-Arten")
    try:
        n = int(tage)
    except (TypeError, ValueError):
        return (False, f"unverständlicher Wiederkehr-Wert [{tage}]")
    if n < 1:
        return (False, f"Wiederkehr-Wert [{n}] ergibt keinen Takt")
    return (True, f"Art [{art}] ist lesend, Takt {n} Tage")


def _faellig(auftrag: dict, jetzt: float | None = None) -> bool:
    """Ist ein wiederkehrender Auftrag wieder an der Reihe?

    Ohne `naechste_faelligkeit` ist er es (erster Lauf). Ein unverständlicher
    Zeitstempel gilt ebenfalls als fällig — **stillstehen ist die schlechteste
    Antwort**, das war die Lehre des Versions-Monitors, wo ein kaputtes Datum
    einen Eintrag dauerhaft stumm legte.
    """
    marke = auftrag.get("naechste_faelligkeit")
    if not marke:
        return True
    try:
        return (jetzt or time.time()) >= time.mktime(
            time.strptime(str(marke), "%Y-%m-%d %H:%M"))
    except Exception:
        return True


# **Adams Festlegung (d), präzisiert — und die Präzisierung ist nötig.**
#
# Sein Wortlaut: „Ein dauerhaft roter Wiederkehrer zählt in die Fehlserie, damit
# er nicht ewig gegen dieselbe Wand rennt." Die Absicht ist eindeutig. Die
# GLOBALE Fehlserie erfüllt sie aber **nicht**: Sie wird bei jedem Erfolg
# genullt (`_fehlserie(True)`). Steht neben dem roten Wiederkehrer auch nur ein
# grüner Auftrag, erreicht der Zähler die Grenze nie — und der Wiederkehrer
# liefe unbegrenzt weiter, alle drei Tage, gegen dieselbe Wand.
#
# Deshalb ein **eigener Zähler je Auftrag**, im Auftrag selbst. Er erfüllt
# Adams Zweck, ohne die globale Bremse zu verändern: Nach drei eigenen
# Fehlläufen wird die Wiederkehr **ausgesetzt und gemeldet** — der Auftrag ist
# dann ein normaler, erledigter Eintrag mit Begründung, kein stiller Dauerläufer.
WIEDERKEHR_FEHLGRENZE = 3


def _blockiert(auftrag: dict, ausgefallen: set[str]) -> str | None:
    """Hängt der Auftrag an etwas, das geparkt oder gescheitert ist?

    Ohne diese Angabe müsste Hora raten — und ein Läufer, der auf einem nicht
    fertigen Vorgänger aufbaut, richtet mehr Schaden an als einer, der ihn
    überspringt. Fehlt die Angabe, gilt der Auftrag als unabhängig; das ist die
    ehrlichere Vorgabe, weil sie nichts unterstellt.
    """
    for t in (auftrag.get("haengt_an") or []):
        if t in ausgefallen:
            return str(t)
    return None


# ------------------------------------------------------------ Auftragsliste --
def auftraege() -> list[dict]:
    try:
        daten = json.loads(LISTE.read_text(encoding="utf-8"))
    except Exception:
        return []
    offen = [a for a in daten if isinstance(a, dict) and a.get("titel")
             and not a.get("erledigt")]
    # **Noch nicht fällig = übersprungen, OHNE Meldung** (Adams Festlegung).
    # Ein wiederkehrender Auftrag, der zwölfmal am Tag meldet, dass er noch
    # nicht dran ist, macht die Liste unlesbar.
    return [a for a in offen if _faellig(a)]


def _liste_schreiben(daten: list[dict]) -> None:
    ZUSTAND.mkdir(parents=True, exist_ok=True)
    tmp = LISTE.with_suffix(".tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(LISTE)


def abhaken(titel: str, ergebnis: str) -> None:
    try:
        daten = json.loads(LISTE.read_text(encoding="utf-8"))
    except Exception:
        return
    for a in daten:
        if a.get("titel") == titel:
            a["ergebnis"] = ergebnis[:400]
            a["erledigt_am"] = time.strftime("%Y-%m-%d %H:%M")
            erlaubt, grund = wiederkehr_erlaubt(a)
            if erlaubt:
                # **Nicht beenden, sondern vertagen.** Der Auftrag bleibt in der
                # Liste und ruht bis zur nächsten Fälligkeit.
                a["erledigt"] = False
                a["naechste_faelligkeit"] = time.strftime(
                    "%Y-%m-%d %H:%M",
                    time.localtime(time.time() + int(a["wiederkehrend"]) * 86400))
            else:
                a["erledigt"] = True
                if a.get("wiederkehrend"):
                    # **Verweigert, aber nicht verschwiegen.** Wer eine
                    # Wiederkehr beantragt und keine bekommt, muss erfahren
                    # warum — sonst wundert er sich still.
                    a["wiederkehr_verweigert"] = grund
    _liste_schreiben(daten)


def _vermerken(titel: str, **felder) -> None:
    """Schreibt Felder an einen Auftrag, OHNE ihn abzuhaken.

    Gebraucht für die Parkstrecke: Ein geparkter Auftrag ist **nicht erledigt**,
    er wartet. Siehe `_urteil_einholen`.
    """
    try:
        daten = json.loads(LISTE.read_text(encoding="utf-8"))
    except Exception:
        return
    for a in daten:
        if a.get("titel") == titel:
            a.update(felder)
    _liste_schreiben(daten)


# ------------------------------------------------------------------ Messen ---
def regression() -> tuple[bool, str]:
    """Bedingung 3: Der Regressionslauf ist das Maß, nicht das Gefühl."""
    try:
        p = subprocess.run(["bash", str(REGRESSION)], cwd=str(REPO),
                           capture_output=True, text=True, timeout=1800)
        letzte = [z for z in (p.stdout or "").splitlines() if "Ergebnis:" in z]
        return p.returncode == 0, (letzte[-1] if letzte else "(keine Ausgabe)")
    except Exception as e:
        return False, f"Testlauf-Fehler: {e}"


def _fehlserie(neu: bool | None = None) -> int:
    """Zählt Fehlläufe in Folge (Bedingung 4)."""
    p = ZUSTAND / "fehlserie.json"
    try:
        n = int(json.loads(p.read_text(encoding="utf-8")).get("n", 0))
    except Exception:
        n = 0
    if neu is not None:
        n = 0 if neu else n + 1
        try:
            ZUSTAND.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"n": n, "zuletzt": time.strftime("%Y-%m-%d %H:%M")}),
                         encoding="utf-8")
        except Exception:
            pass
    return n


def melden(text: str) -> None:
    """Meldet ueber die gemeinsame Botenpost — mit Absender.

    Vorher legte jeder Schreiber seine Datei selbst ab, mit vier fast
    gleichen Codebloecken und OHNE Absender. Als am 26.07. nachts eine
    Meldung bei Adam ankam, kostete die Suche nach ihrem Urheber ueber
    eine Stunde. Die Nachricht haette es selbst sagen koennen.
    """
    botenpost.legen(text, "hora")


def _protokollieren(eintrag: dict) -> None:
    try:
        ZUSTAND.mkdir(parents=True, exist_ok=True)
        with PROTOKOLL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    except Exception:
        pass


# -------------------------------------------------------------------- Lauf ---
def lauf(trocken: bool = False) -> int:
    """Ein Hora-Lauf — mit Schloss, damit nie zwei zugleich laufen.

    Das ``finally`` ist der wichtige Teil: Auch ein Absturz mitten im Lauf gibt
    das Schloss wieder her. Sonst schwiege Hora bis zur Rückkehr, und niemand
    wüsste warum.
    """
    if not _schloss_nehmen():
        return 0                   # ein anderer Lauf arbeitet noch — still gehen
    try:
        return _lauf(trocken)
    finally:
        _schloss_geben()


def _lauf(trocken: bool = False) -> int:
    """Rückgabe 0 = gut, 1 = gemeldet, 2 = angehalten."""
    beginn = time.strftime("%Y-%m-%d %H:%M")

    # --- Das Auftragsbuch speist die Liste, bevor sie gelesen wird ----------
    #
    # **GEFUNDEN 18.08.2026 beim Scharfstellen (E1):** `uebernehmen()` hatte
    # ueberhaupt keinen Aufrufer - kein Zeitgeber, kein Skript, nur die
    # Pruefungen. "SCHARF an" allein haette also NICHTS bewirkt, und die
    # Probewoche waere eine Woche gewesen, in der nichts geschieht. Genau die
    # Sorte gebaut-und-wirkungslos, gegen die dieses Projekt heute den ganzen
    # Tag gearbeitet hat.
    #
    # Hier statt in einem eigenen Zeitgeber, aus drei Gruenden: Das
    # Auftragsbuch speist ohnehin genau DIESE Liste; Hora laeuft bereits im
    # richtigen Takt; und ein zusaetzlicher Zeitgeber waere ein weiterer
    # Traeger, der selbst bewacht werden muesste.
    #
    # Ein Fehlschlag hier darf den Lauf NICHT verhindern: Die vorhandenen
    # Auftraege sind wichtiger als die neuen.
    if not trocken:
        try:
            anzahl, meldung = auftragsbuch.uebernehmen()
            if anzahl:
                _protokollieren({"zeit": beginn, "titel": "(Auftragsbuch)",
                                 "ergebnis": "uebernommen", "regression": meldung})
        except Exception as e:
            _protokollieren({"zeit": beginn, "titel": "(Auftragsbuch)",
                             "ergebnis": "fehler", "regression": f"{type(e).__name__}: {e}"})

    # Bedingung 4 zuerst: Wer schon dreimal gescheitert ist, fängt nicht wieder an.
    if _fehlserie() >= FEHLGRENZE:
        melden(f"⏸️ Hora hält an ({beginn}): {FEHLGRENZE} Fehlläufe in Folge. "
               "Ich arbeite nicht weiter, bis du hingesehen hast — ein Läufer, "
               "der gegen dieselbe Wand rennt, richtet mehr Schaden an als einer, "
               "der stehen bleibt.\nZum Fortsetzen die Datei "
               f"{ZUSTAND / 'fehlserie.json'} entfernen.")
        return 2

    offen = auftraege()
    if not offen:
        # Bedingung 2 + 5: Auch Leerlauf wird berichtet — aber gedämpft, sonst
        # sind es bei Zweistunden-Takt zwölf gleichlautende Nachrichten am Tag.
        if _leerlauf_melden():
            melden(f"🕰️ Hora ({beginn}): Die Auftragsliste ist leer — ich habe "
                   "nichts angefasst. Wenn etwas laufen soll, trag es in die "
                   "Liste ein; ohne Eintrag entscheide ich nichts von selbst. "
                   "(Solange sie leer bleibt, melde ich das höchstens einmal "
                   "am Tag.)")
        return 0
    _leerlauf_entwarnen()          # es gibt wieder Arbeit

    # Bedingung 3, erste Hälfte: Auf rotem Fundament wird nicht gearbeitet
    # (dieselbe Regel wie A5 im Updater).
    vorher_ok, vorher = regression()
    if not vorher_ok:
        _fehlserie(False)
        melden(f"🔴 Hora ({beginn}): Der Regressionslauf war schon **vor** der "
               f"Arbeit rot ({vorher}). Ich habe nichts angefasst — auf einem "
               "roten Fundament zu bauen macht die Ursachensuche unmöglich.")
        return 1

    # ---- Die Kette: Auftrag um Auftrag, bis die Liste leer ist oder etwas
    # ---- den Läufer anhält. Kein Zeitwert, keine Stückzahl zum Nachjustieren.
    ausgefallen: set[str] = set()        # geparkt oder gescheitert
    erledigt: list[str] = []
    geparkt: list[str] = []
    uebersprungen: list[str] = []
    gescheitert: list[str] = []
    freigegeben_jetzt: list[str] = []
    probe: list[str] = []                # nur im Probelauf
    abbruch = ""
    letzte_lage = vorher

    for auftrag in offen:
        titel = auftrag["titel"]

        # Wegstein eines gestolperten Vorgängers — überspringen, nicht warten.
        vorgaenger = _blockiert(auftrag, ausgefallen)
        if vorgaenger:
            uebersprungen.append(f"{titel} (hängt an „{vorgaenger}“)")
            continue

        # Bedingung 1: Braucht der Auftrag eine Entscheidung, wird er GEPARKT —
        # und Hora geht SOFORT weiter. Fragen sind Wegsteine, keine Halteschilder.
        if auftrag.get("braucht_zustimmung"):
            lage, text = _urteil_einholen(auftrag)
            if lage == "wartet":
                geparkt.append(f"{titel} ({text})")
                ausgefallen.add(titel)
                continue
            if lage == "abgelehnt":
                abhaken(titel, "von Adam abgelehnt")
                uebersprungen.append(f"{titel} (abgelehnt)")
                ausgefallen.add(titel)
                continue
            if lage == "unparkbar":
                abhaken(titel, f"nicht parkbar: {text}")
                uebersprungen.append(f"{titel} (nicht parkbar: {text})")
                ausgefallen.add(titel)
                continue
            # lage == "freigegeben": weiter unten normal ausführen — die Antwort
            # hat den Auftrag eingeholt, genau wie vorgesehen.
            freigegeben_jetzt.append(titel)

        if trocken:
            probe.append(titel)
            continue

        befehl = auftrag.get("befehl")
        if not befehl:
            abhaken(titel, "kein ausführbarer Befehl hinterlegt")
            uebersprungen.append(f"{titel} (kein ausführbarer Befehl hinterlegt)")
            ausgefallen.add(titel)
            continue

        # Frische Sitzung je Auftrag — die Isolation bleibt.
        try:
            p = subprocess.run(["bash", "-lc", befehl], cwd=str(REPO),
                               capture_output=True, text=True, timeout=7200)
            ausgabe = _verdichten((p.stdout or "") + (p.stderr or ""))
            erfolg = p.returncode == 0
        except Exception as e:
            ausgabe, erfolg = str(e), False

        # Kontingent erschöpft: anhalten, nicht scheitern. Der Auftrag bleibt
        # offen und der nächste Lauf nimmt ihn wieder auf — genau das, wofür
        # die Liste da ist.
        if not erfolg and _kontingent_erschoepft(ausgabe):
            abbruch = ("Kontingent erschöpft — ich habe angehalten, nichts "
                       "abgehakt und nichts verloren.")
            break

        nachher_ok, letzte_lage = regression()
        if erfolg and nachher_ok:
            _fehlserie(True)
            if auftrag.get("wiederkehr_fehler"):
                # Ein gelungener Lauf setzt den eigenen Zähler zurück - sonst
                # summierte er über Wochen und setzte die Wiederkehr irgendwann
                # aus, obwohl sie längst wieder trägt.
                _vermerken(titel, wiederkehr_fehler=0)
            abhaken(titel, f"erledigt · {letzte_lage}")
            erledigt.append(titel)
            _protokollieren({"zeit": beginn, "titel": titel,
                             "ergebnis": "gruen", "regression": letzte_lage})
            continue

        n = _fehlserie(False)
        ausgefallen.add(titel)
        # Adams Festlegung (d): Ein Wiederkehrer, der immer wieder scheitert,
        # darf nicht ewig wiederkommen. Sein eigener Zähler ist der Riegel —
        # der globale wird von jedem grünen Auftrag daneben genullt.
        if wiederkehr_erlaubt(auftrag)[0]:
            eigen = int(auftrag.get("wiederkehr_fehler") or 0) + 1
            if eigen >= WIEDERKEHR_FEHLGRENZE:
                _vermerken(titel, wiederkehr_fehler=eigen, erledigt=True,
                           wiederkehr_verweigert=(
                               f"nach {eigen} eigenen Fehllaeufen ausgesetzt - "
                               "ein Wiederkehrer, der immer wieder scheitert, "
                               "rennt sonst ewig gegen dieselbe Wand"))
                gescheitert.append(
                    f"{titel} — Wiederkehr nach {eigen} Fehllaeufen ausgesetzt")
            else:
                _vermerken(titel, wiederkehr_fehler=eigen)
        # **Fund aus dem Echtlauf (26.07.):** Hier stand `letzte_lage`, also das
        # Ergebnis des Regressionslaufs. Die Meldung las sich dadurch als
        # „gescheitert (30/30 bestanden)" — die Zahl war richtig und die Aussage
        # sinnlos, weil sie die falsche Frage beantwortet. Wer nachts eine
        # Fehlermeldung liest, will wissen, **woran der Auftrag scheiterte**,
        # nicht, wie es dem Fundament geht.
        gescheitert.append(f"{titel} — {_fehlgrund(erfolg, nachher_ok, ausgabe, letzte_lage)}")
        _protokollieren({"zeit": beginn, "titel": titel, "ergebnis": "rot",
                         "regression": letzte_lage, "ausgabe": ausgabe[-400:]})
        if n >= FEHLGRENZE:
            abbruch = (f"{FEHLGRENZE} Fehlläufe in Folge — ich halte an. "
                       f"Letzte Ausgabe:\n{ausgabe[-400:]}")
            break

    # Bedingung 5: Bericht, auch wenn nichts zu tun war.
    teile = [f"🕰️ Hora ({beginn}) — Lauf beendet."]
    if probe:
        teile.append(f"🧪 Probelauf: Ich HÄTTE {len(probe)} Auftrag/Aufträge "
                     "bearbeitet — " + " · ".join(probe)
                     + ". Es wurde nichts getan.")
    if erledigt:
        teile.append(f"✅ Erledigt ({len(erledigt)}): " + " · ".join(erledigt))
    if freigegeben_jetzt:
        teile.append(f"🔓 Nach deiner Freigabe ausgeführt "
                     f"({len(freigegeben_jetzt)}): "
                     + " · ".join(freigegeben_jetzt))
    if geparkt:
        teile.append(f"🗝️ Wartet auf dein Urteil ({len(geparkt)}): "
                     + " · ".join(geparkt)
                     + "\n   Ohne Antwort geschieht nichts — und nichts gilt "
                       "als abgelehnt. Der Auftrag bleibt in der Liste und "
                       "läuft, sobald du zustimmst.")
    if uebersprungen:
        teile.append(f"⏭️ Übersprungen ({len(uebersprungen)}): "
                     + " · ".join(uebersprungen))
    if gescheitert:
        teile.append(f"🔴 Nicht sauber durchgelaufen ({len(gescheitert)}): "
                     + " · ".join(gescheitert)
                     + "\n   Diese Aufträge bleiben offen, abgehakt ist nichts.")
    if abbruch:
        teile.append("⏸️ " + abbruch)
    teile.append(f"Fundament zuletzt: {letzte_lage}")
    teile.append(f"Noch offen in der Liste: {len(auftraege())}")
    melden("\n".join(teile))

    if abbruch:
        return 2
    return 1 if (gescheitert or uebersprungen) else 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Hora — autonomer Läufer")
    ap.add_argument("--liste", help="andere Auftragsliste verwenden")
    ap.add_argument("--trocken", action="store_true",
                    help="prüfen und melden, aber nichts ausführen")
    a = ap.parse_args()
    if a.liste:
        globals()["LISTE"] = Path(a.liste)
    return lauf(trocken=a.trocken)


if __name__ == "__main__":
    sys.exit(main())
