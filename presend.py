"""Pre-Send-Hook (Migrations-Punkt 8.5) — prüft Bot-Antworten, BEVOR sie rausgehen.

Adam-Spec (16.07.2026), drei Schutzgeländer:
  1. Was deterministisch SICHER fixbar ist (Wochentag↔Datum) → der Hook korrigiert
     direkt selbst: keine Schleife, keine Latenz.
  2. Mechanisch verifizierbare, aber nicht auto-fixbare Befunde (Vollständigkeit)
     → EINE Korrekturrunde an Claude; greift sie nicht, wird die Antwort MIT
     sichtbarem ⚠️-Vermerk gesendet — nie eine hängende Antwort riskieren.
  3. Tentativ-Sprache ist KEIN harter Fehler (Hedging kann berechtigt sein) →
     läuft nur als Log/Kennzahl mit, ohne Korrektur und ohne Vermerk.
Alle Treffer werden geloggt (wie die Ampel) → Fehlalarm-Quote messbar, nachschärfbar.

v1 BEWUSST ENG (Analyse-Befunde 17.07.2026):
  • Nachrichten-Bezugs-Prüfung ist mit der heutigen Datenlage NICHT fehlalarm-frei
    machbar → v2. Gründe: BOT_MSGS hält bei Antworten >4096 Zeichen nur die erste
    Chunk-ID, ist RAM-only + FIFO-gedeckelt (400); die echte Empfangszeit einer
    Nachricht bekommt das Modell nie zu sehen.
  • Sicherheits-Gegencheck (e) → v2, und dort im Gründlich-Modus (starkes Modell),
    NICHT über Phi-4-Mini (das schwächste Modell soll nicht das stärkste prüfen).
  • Relative Zeitaussagen ("heute ist Freitag") werden nur geloggt, nicht korrigiert:
    Mitternachts-Drift + Referenzzeit-Fragen machen sie fehlalarm-anfällig. Die
    Wochentag↔Datum-Paarung dagegen ist SELBSTTRAGEND (date(y,m,d).weekday()
    braucht kein Systemdatum) → deshalb dort Auto-Korrektur.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import date
from pathlib import Path

log = logging.getLogger("claude-tg-bot.presend")

# Einzige Quelle der deutschen Wochentagsnamen — bot.py referenziert diese Liste,
# damit die beiden nicht auseinanderdriften (Analyse-Hinweis 17.07.).
WEEKDAYS_DE = ("Montag", "Dienstag", "Mittwoch", "Donnerstag",
               "Freitag", "Samstag", "Sonntag")

# "Sonnabend" ist ein gültiges Synonym für Samstag — nicht fälschlich "korrigieren".
_WD_SYNONYM = {"sonnabend": "Samstag"}

_MONTHS_DE = {
    "januar": 1, "februar": 2, "märz": 3, "maerz": 3, "april": 4, "mai": 5,
    "juni": 6, "juli": 7, "august": 8, "september": 9, "oktober": 10,
    "november": 11, "dezember": 12,
}

_WD_ALT = "Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonnabend|Sonntag"

# Muster A1: "Freitag, den 17.07.2026" / "Montag 17.7.2026"
_RE_WD_NUM = re.compile(
    rf"\b(?P<wd>{_WD_ALT})\b\s*,?\s*(?:den|dem|der)?\s*"
    rf"(?P<d>\d{{1,2}})\.\s*(?P<m>\d{{1,2}})\.\s*(?P<y>\d{{4}})\b"
)
# Muster A2: "Freitag, 17. Juli 2026"
_RE_WD_MON = re.compile(
    rf"\b(?P<wd>{_WD_ALT})\b\s*,?\s*(?:den|dem|der)?\s*"
    rf"(?P<d>\d{{1,2}})\.\s*(?P<mon>Januar|Februar|März|Maerz|April|Mai|Juni|Juli|"
    rf"August|September|Oktober|November|Dezember)\s*(?P<y>\d{{4}})\b",
    re.IGNORECASE,
)
# Muster B (nur Log): "heute ist Freitag", "gestern war Donnerstag"
_RE_REL_WD = re.compile(
    rf"\b(?P<rel>heute|gestern|morgen|übermorgen|vorgestern)\s+(?:ist|war|wird)\s+"
    rf"(?:der\s+)?(?P<wd>{_WD_ALT})\b",
    re.IGNORECASE,
)
# Muster D (nur Log): Tentativ-/Hedging-Sprache
_RE_TENTATIV = re.compile(
    r"\b(müsste eigentlich|sollte eigentlich|dürfte (?:wohl|eigentlich)|"
    r"vermutlich schon|ich glaube schon|müsste passen|sollte passen|"
    r"vermutlich richtig|denke ich mal)\b",
    re.IGNORECASE,
)

# ⑧ Verben, die in einem Befehlsblock einen Blick wert sind, bevor Adam ihn
# ins Terminal einfügt. **Bewusst kurz gehalten.** Eine lange Liste erzeugt
# Warnungen bei jedem zweiten Block, und eine Warnung, die immer kommt, wird
# überlesen — dann warnt sie nicht mehr, sie schmückt nur noch.
#
# Aufgenommen ist, was **löscht, überschreibt, Rechte ändert oder Fremdes
# ausführt**. Nicht aufgenommen: `git`, `ls`, `cat`, `systemctl` — die stehen
# in fast jedem Block, den wir uns gegenseitig schicken.
_SCHARFE_MUSTER = (
    # `[BERICHTIGT 31.08., F-10]` **Ein Filter mit 48 % Fehlalarm ist bereits
    # abgeschaltet, auch wenn er noch läuft.** Hier stand `-?\w*[rf]` — das
    # Fragezeichen machte den Bindestrich **optional**, und damit traf das
    # Muster jedes Wort mit einem `r` oder `f` darin. Gemessen an den 311
    # echten Dateinamen dieses Repos: **151 Fehlalarme**, darunter jede Datei
    # namens `bericht`, `ANTWORT-SPIEGEL.md`, `bauauftrag-*`.
    #
    # **Und die Gegenrichtung war ebenso kaputt, das stand in keinem Befund:**
    # `\w` kennt keine Bindestriche, also verfehlte das Muster `rm --recursive`
    # und `rm --force` vollständig — die ausgeschriebenen Formen derselben
    # Gefahr. Ein Filter, der die Hälfte der Dateinamen anschlägt und die
    # Langform durchlässt, ist in beide Richtungen falsch.
    #
    # Jetzt muss ein Wort **mit einem Bindestrich beginnen**, um als Flag zu
    # zählen. Gemessen nach der Änderung: **0 von 311** Fehlalarmen, und alle
    # acht echten Formen treffen (`-rf`, `-r`, `-f`, `-R`, `-vrf`,
    # `--recursive`, `--force`, Flag hinter dem Dateinamen).
    (re.compile(r"\brm\b(?:\s+[^\s;|&]+)*?\s+-{1,2}[a-z]*[rf]", re.I),
     "rm mit -r oder -f (löscht Verzeichnisse)"),
    (re.compile(r"\b(curl|wget)\b[^\n|]*\|\s*(ba)?sh", re.I), "Herunterladen und direkt Ausführen"),
    (re.compile(r"\bbase64\s+-d\b[^\n|]*\|", re.I), "Entschlüsseln und Weiterleiten"),
    (re.compile(r"\bchmod\s+(-\w+\s+)*[0-7]*777", re.I), "chmod 777 (Rechte für alle)"),
    (re.compile(r"\bdd\s+.*\bof=", re.I), "dd (überschreibt roh)"),
    (re.compile(r">\s*/etc/", re.I), "Schreiben nach /etc"),
    (re.compile(r"\bmkfs\b|\bshred\b", re.I), "Formatieren oder Schreddern"),
    (re.compile(r":\(\)\s*\{.*\}\s*;\s*:", re.S), "Fork-Bombe"),
)

# Codeblöcke — nur dort wird gesucht. Fließtext, der „rm" erwähnt, ist kein
# Befehl, und eine Warnung darüber wäre genau das Rauschen, das die Warnung
# entwertet.
# `[BERICHTIGT 31.08., F-10]` Der Zaun verlangte einen Zeilenumbruch **direkt**
# nach den drei Strichen. Damit fielen zwei Formen durch: ein Block mit
# Wagenrücklauf (`\r\n`, so schreibt jedes Windows-Werkzeug) und der
# **einzeilige** Block ```rm -rf /```. Beides sind gültige Codeblöcke, und der
# einzeilige ist die naheliegendste Form für genau einen Befehl.
#
# Der Sprach-Hint zählt nur noch als solcher, **wenn ihm ein Umbruch folgt** —
# sonst hätte ```rm -rf /``` das `rm` als Sprachnamen verschluckt und der
# Inhalt begänne bei `-rf`. Die Warnung wäre ausgeblieben, und zwar leise.
_RE_CODEBLOCK = re.compile(r"```(?:[a-zA-Z]+[ \t]*\r?\n|\r?\n|)(.*?)```", re.S)


def _scharfe_befehle(text: str) -> list[str]:
    """Welche scharfen Verben stehen in den Codeblöcken dieser Antwort?

    Ohne Dubletten und in stabiler Reihenfolge: Zwei gleiche Warnungen unter
    einer Nachricht sind eine zu viel.
    """
    gefunden: list[str] = []
    for block in _RE_CODEBLOCK.findall(text or ""):
        for muster, name in _SCHARFE_MUSTER:
            if name not in gefunden and muster.search(block):
                gefunden.append(name)
    return gefunden


# Auto-Korrektur nur für Daten nahe der Gegenwart: entfernte/historische Angaben
# stammen oft aus Zitaten oder Quellen — da ändern wir keinen fremden Wortlaut.
_AUTOFIX_WINDOW_DAYS = 370

_LOG_PATH = Path(
    os.environ.get("PRESEND_LOG_PATH")
    or str(Path(__file__).parent / "logs" / "presend.jsonl")
)


def _canon_wd(name: str) -> str:
    return _WD_SYNONYM.get(name.lower(), name.capitalize())


def _fix_weekday_dates(text: str, findings: list[dict], today: date | None = None) -> str:
    """Muster A: Wochentag↔Datum-Paarungen prüfen und sicher Falsches korrigieren."""
    today = today or date.today()

    def _handle(m: re.Match, month_from_name: bool) -> str:
        whole = m.group(0)
        try:
            d = int(m.group("d"))
            mo = (_MONTHS_DE[m.group("mon").lower()] if month_from_name
                  else int(m.group("m")))
            y = int(m.group("y"))
            real = date(y, mo, d)
        except (ValueError, KeyError):
            return whole  # unplausibles Datum (z.B. 31.02.) — nicht anfassen
        claimed = _canon_wd(m.group("wd"))
        correct = WEEKDAYS_DE[real.weekday()]
        if claimed == correct:
            return whole
        near = abs((real - today).days) <= _AUTOFIX_WINDOW_DAYS
        findings.append({
            "code": "datum_wochentag",
            "art": "autofix" if near else "log",
            "detail": f"„{claimed}“ → „{correct}“ für {d:02d}.{mo:02d}.{y}"
                      + ("" if near else " (außerhalb Zeitfenster — nur geloggt, "
                                        "könnte Zitat/historisch sein)"),
        })
        if not near:
            return whole
        return whole.replace(m.group("wd"), correct, 1)

    text = _RE_WD_NUM.sub(lambda m: _handle(m, False), text)
    text = _RE_WD_MON.sub(lambda m: _handle(m, True), text)
    return text


def check_and_fix(text: str, *, pending_newer: int = 0,
                  today: date | None = None) -> tuple[str, list[dict]]:
    """Prüft den vollständigen Antworttext. Gibt (ggf. korrigierter Text, Befunde).

    pending_newer: Anzahl NEUERER Nachrichten, die seit Bearbeitungsbeginn eingingen
                   und noch warten (vom Aufrufer ermittelt — Zeitbasis beachten!).
    Fehler hier dürfen den Bot nie stören → alles defensiv.
    """
    findings: list[dict] = []
    if not text:
        return text, findings
    try:
        # (a) Wochentag↔Datum — deterministisch, wird direkt korrigiert
        text = _fix_weekday_dates(text, findings, today=today)

        # (b') relative Zeitaussagen — nur Log (Mitternachts-Drift/Referenzzeit)
        for m in _RE_REL_WD.finditer(text):
            findings.append({
                "code": "datum_relativ",
                "art": "log",
                "detail": f"relative Zeitaussage: „{m.group(0)}“",
            })

        # (c) Vollständigkeit — reiner VERMERK, bewusst KEINE Korrekturrunde.
        # Der Agent kann die neueren Nachrichten gar nicht sehen: sie liegen in der
        # Warteschlange und werden gleich EINZELN beantwortet. Eine Korrekturrunde
        # ist deshalb per Konstruktion vergeblich — sie kostete nur eine zusätzliche
        # Anfrage und verleitete ihn dazu, nach etwas zu fragen, das längst vorliegt
        # („kannst du sie mir zeigen?" — live beobachtet 20.07., zwei Sekunden bevor
        # er dieselben Nachrichten selbst beantwortete).
        if pending_newer > 0:
            findings.append({
                "code": "vollstaendigkeit",
                "art": "vermerk",
                "detail": f"{pending_newer} neuere Nachricht(en) seit Bearbeitungsbeginn "
                          f"eingegangen, von dieser Antwort nicht adressiert",
                "hinweis": (
                    "ℹ️ Eine neuere Nachricht von dir ist inzwischen eingegangen — "
                    "die beantworte ich gleich separat."
                    if pending_newer == 1 else
                    f"ℹ️ {pending_newer} neuere Nachrichten von dir sind inzwischen "
                    "eingegangen — die beantworte ich gleich einzeln."
                ),
            })

        # (d) Tentativ-Sprache — KEIN harter Fehler, nur Kennzahl
        for m in _RE_TENTATIV.finditer(text):
            findings.append({
                "code": "tentativ",
                "art": "log",
                "detail": f"Hedging: „{m.group(0)}“",
            })

        # (e) ⑧ Ausgangs-Wächter für Befehlsblöcke (Adams Einwand 22.08.:
        #     „auch mit Daumen kein Schaden").
        #
        # **Warum hier und nirgends sonst:** Der Bot sieht nicht, was Adam ins
        # Terminal einfügt. Die einzige Stelle, an der ein Schadbefehl noch
        # abzufangen ist, ist der Moment, in dem der Bot ihn **schreibt**.
        # Danach führt der Weg durch einen Menschen, und dort endet jede
        # technische Sicherheit.
        #
        # Das macht aus „kein Schaden ohne deinen Daumen" das ehrlichere
        # **„…und der Daumen sieht, was er drückt"**.
        #
        # **Was das NICHT ist:** eine Erkennung von Absicht. Geprüft wird nur,
        # ob scharfe Verben im Block stehen — ob sie berechtigt sind,
        # entscheidet Adam. Der Wächter macht sichtbar, er verbietet nicht.
        for treffer in _scharfe_befehle(text):
            findings.append({
                "code": "scharfer_befehl",
                "art": "vermerk",
                "detail": f"scharfer Befehl im Ausgang: {treffer}",
                "hinweis": (
                    f"⚠️ Vorsicht: Der Block oben enthält **{treffer}**. "
                    "Lies ihn, bevor du ihn ausführst — ich kann nach dem "
                    "Einfügen nichts mehr prüfen."
                ),
            })
    except Exception:
        log.exception("Pre-Send-Check fehlgeschlagen (nicht-fatal)")
    return text, findings


def needs_correction(findings: list[dict]) -> list[dict]:
    return [f for f in findings if f.get("art") == "korrektur"]


def needs_notice(findings: list[dict]) -> list[dict]:
    """Befunde, die dem Nutzer nur als Vermerk angehängt werden — ohne Korrekturrunde.
    Für alles, was der Agent nicht selbst beheben kann (weil ihm die Information
    gar nicht vorliegt), aber worüber der Nutzer Bescheid wissen soll."""
    return [f for f in findings if f.get("art") == "vermerk"]


def correction_prompt(findings: list[dict]) -> str:
    """Konkreter Befund-Text für die EINE Korrekturrunde an Claude."""
    lines = [
        "[PRE-SEND-PRÜFUNG hat einen Befund an deiner letzten Antwort gefunden. "
        "Korrigiere NUR diesen Punkt und gib die vollständige, korrigierte Antwort "
        "aus — keine Meta-Bemerkung, keine Entschuldigung:",
    ]
    for f in findings:
        lines.append(f"  • {f.get('detail', '')}")
    lines.append("]")
    return "\n".join(lines)


def log_findings(findings: list[dict], meta: dict | None = None) -> None:
    """Alle Befunde protokollieren (Fehlalarm-Quote messbar machen)."""
    if not findings:
        return
    try:
        _LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        entry = {
            "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
            "findings": findings,
        }
        if meta:
            entry["meta"] = meta
        with _LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        log.exception("Pre-Send-Log fehlgeschlagen (nicht-fatal)")


def status() -> dict:
    """Kennzahlen für /presend — wie viele Treffer je Art/Code (Fehlalarm-Quote)."""
    counts: dict[str, int] = {}
    arten: dict[str, int] = {}
    total = 0
    korrektur_erfolg = 0
    korrektur_fehl = 0
    try:
        if _LOG_PATH.is_file():
            for line in _LOG_PATH.read_text(encoding="utf-8").splitlines():
                try:
                    e = json.loads(line)
                except Exception:
                    continue
                total += 1
                for f in e.get("findings", []):
                    counts[f.get("code", "?")] = counts.get(f.get("code", "?"), 0) + 1
                    arten[f.get("art", "?")] = arten.get(f.get("art", "?"), 0) + 1
                m = e.get("meta") or {}
                if m.get("korrektur") == "erfolgreich":
                    korrektur_erfolg += 1
                elif m.get("korrektur") == "fehlgeschlagen":
                    korrektur_fehl += 1
    except Exception:
        log.exception("Pre-Send-Status fehlgeschlagen")
    return {
        "antworten_mit_befund": total,
        "codes": counts,
        "arten": arten,
        "korrektur_erfolgreich": korrektur_erfolg,
        "korrektur_fehlgeschlagen": korrektur_fehl,
        "log_path": str(_LOG_PATH),
    }
