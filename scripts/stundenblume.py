#!/usr/bin/env python3
# <!-- ROLLE: stundenblumen -->
"""Stundenblumen — die dauerlaufende Belegkette.

**Das Problem, das sie lösen:** Alle bisherigen Prüfungen sind
**Zeitpunkt**-Prüfungen — der 4-Uhr-Check, der Selbstcheck beim Start, der
Regressionslauf. Steht der Prüfer selbst still, merkt es niemand. Ein Wächter,
der schweigt, ist von einem Wächter, der nichts zu melden hat, nicht zu
unterscheiden.

**Die Umkehrung:** Kurze, billige Prüfläufe in dichter Folge, die einander
anstoßen. **Das Ausbleiben der Übergabe ist selbst der Alarm.** Nicht der Befund
meldet sich, sondern die Lücke.

**Warum das minütlich geht:** Eine Blume ruft **kein Modell** auf. Sie kostet
nichts und darf deshalb laufen, so oft sie will.

**`[RICHTIGGESTELLT 2026-08-20]` Hier stand: „Sieht sie etwas Auffälliges,
weckt sie ein Modell — billig immer, teuer nur bei Anlass."** Das war nie
gebaut. Im Quelltext steht kein einziger Modellaufruf; sie führt ausschließlich
Systembefehle aus. Claudia hat es am 20.08. beim Suchen nach einem Weckruf
gefunden — **sie hätte auf einen Mechanismus gewartet, den es nie gab.**

Dieselbe Klasse wie der Dämpfer-Docstring und wie „das Archiv, auf das
Engywuck ohnehin zugreift": **Eine Beschreibung, die mehr verspricht als der
Bau, ist gefährlicher als eine fehlende** — denn niemand prüft nach, was schon
dasteht. Wer die Blume um einen Weckruf erweitern will, baut ihn; bis dahin
sagt dieser Text, was sie wirklich tut.

**Die Kette ist git-artig, keine Blockchain.** Jede Blume trägt den Fingerabdruck
der vorigen; eine nachträglich veränderte Blume bricht die Kette sichtbar.
**Ehrlich dazu:** Das ist manipulations-**sichtbar**, nicht manipulations-**sicher**
— wer die ganze Kette neu rechnet, hinterlässt keine Spur. Für unser Problem
genügt das: Wir sichern gegen **Ausfall und Versehen**, nicht gegen einen
Fälscher im eigenen Haus. Blockchain löst Misstrauen zwischen Fremden; dieses
Problem haben wir nicht. Die Stufe darüber wären signierte Commits — vorgemerkt,
nicht jetzt.

**Ruhezeiten von Anfang an.** Neustart, Wartung, Netzhänger dürfen **keinen**
Alarm auslösen. Ein Wächter, dem niemand mehr glaubt, ist schlimmer als keiner —
deshalb sind die Ruhefenster Teil des ersten Entwurfs, nicht ein späterer Aufsatz.

**Die Rollen bleiben getrennt:** Hora **arbeitet** · die Stundenblumen **belegen,
dass das System lebt** · Kassiopeia **prüft Inhalte**.

Aufruf: ``python3 scripts/stundenblume.py`` (je Lauf eine Blume)
        ``python3 scripts/stundenblume.py --pruefen`` (Kette bewerten, für 8.1)
        ``python3 scripts/stundenblume.py --ruhe 20`` (20 Minuten Ruhe)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import botenpost  # noqa: E402

ZUSTAND = Path(os.environ.get("BLUMEN_DIR")
               or (Path.home() / ".claude" / "stundenblumen"))
KETTE = ZUSTAND / "kette.jsonl"
RUHE = ZUSTAND / "ruhe_bis"
POSTFACH = Path(os.environ.get("POSTFACH_DIR")
                or (Path.home() / "postfach")) / "outbox"

# Takt und Toleranz. Die Toleranz ist bewusst großzügig: Lieber eine Lücke
# übersehen als jede Woche ein Fehlalarm — Vertrauen ist die knappere Ressource.
TAKT_S = int(os.environ.get("BLUMEN_TAKT") or 60)
TOLERANZ_S = int(os.environ.get("BLUMEN_TOLERANZ") or 300)
# Das nächtliche Hygiene-Fenster (04:00) ist ein bekannter Unterbruch.
RUHE_STUNDEN = {4}


def _in_ruhe(jetzt: float | None = None) -> str:
    """Warum gerade keine Meldung fällig ist — leerer Text heißt: keine Ruhe."""
    jetzt = jetzt or time.time()
    try:
        bis = float(RUHE.read_text(encoding="utf-8").strip())
        if jetzt < bis:
            rest = int((bis - jetzt) / 60)
            return f"angeordnete Ruhe (noch {rest} min)"
    except Exception:
        pass
    if time.localtime(jetzt).tm_hour in RUHE_STUNDEN:
        return "nächtliches Wartungsfenster"
    return ""


def ruhe_setzen(minuten: int) -> None:
    ZUSTAND.mkdir(parents=True, exist_ok=True)
    RUHE.write_text(str(time.time() + minuten * 60), encoding="utf-8")


def _letzte() -> dict | None:
    try:
        with KETTE.open("rb") as f:
            f.seek(0, 2)
            groesse = f.tell()
            f.seek(max(0, groesse - 4096))
            zeilen = f.read().decode("utf-8", "replace").splitlines()
        for z in reversed(zeilen):
            if z.strip():
                return json.loads(z)
    except Exception:
        return None
    return None


def _fingerabdruck(eintrag: dict) -> str:
    roh = json.dumps({k: eintrag[k] for k in sorted(eintrag) if k != "abdruck"},
                     ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(roh.encode("utf-8")).hexdigest()[:16]


# ------------------------------------------------------------- die Prüfungen --
def _befunde() -> list[tuple[str, str]]:
    """Billige, deterministische Prüfungen — kein Modell, kein Netz.

    **Jeder Befund trägt eine KENNUNG neben seinem Text** — die Kennung geht
    ins Gedächtnis des Dämpfers, der Text an Adam.

    **Warum eine Kennung und nicht ein bereinigter Text** (Conni, 28.07.): Eine
    Bereinigung wäre eine Heuristik, die im Hintergrund rät; die Kennung ist
    eine Zusage, die die Signatur **erzwingt**. Wer künftig einen Prüfer ohne
    Kennung anhängt, kann es gar nicht erst — statt unbemerkt auf den Lärm-Weg
    zurückzufallen. *Wo Struktur und Prüfer beide möglich sind, gewinnt die
    Struktur.*

    Bewusst klein gehalten: Eine Blume, die eine Minute rechnet, ist keine
    Blume mehr. Was teuer zu prüfen ist, gehört in den 4-Uhr-Check.
    """
    raus: list[tuple[str, str]] = []
    # 1. Lebt der Bot? (die verlässliche Auskunft, nicht die selbstzählende)
    if shutil.which("systemctl"):
        try:
            p = subprocess.run(["systemctl", "show", "claude-telegram-bot",
                                "-p", "MainPID", "--value"],
                               capture_output=True, text=True, timeout=10)
            pid = (p.stdout or "").strip()
            if not pid or pid == "0":
                raus.append(("bot-prozess", "Bot-Prozess nicht vorhanden"))
        except Exception as e:
            raus.append(("dienst-unabfragbar", f"Dienst nicht abfragbar: {e}"))
    # 2. Läuft die Platte voll?
    try:
        s = os.statvfs("/")
        frei = s.f_bavail * s.f_frsize / (1024 ** 3)
        if frei < 5:
            raus.append(("platte-knapp",
                         f"nur noch {frei:.1f} GiB Plattenplatz frei"))
    except Exception:
        pass
    # 2b. Wird der Arbeitsspeicher knapp? `[NEU 26.07.]`
    raus.extend(speicher_pruefen())
    # 3. Staut sich das Boten-Postfach? (ein Zeichen, dass der Bot nicht arbeitet)
    try:
        wartend = len(list(POSTFACH.glob("*.json")))
        if wartend > 20:
            raus.append(("postfach-stau",
                         f"{wartend} unzugestellte Postfach-Aufträge"))
    except Exception:
        pass
    # 4. Ist die Anmeldung gekippt? (C2)
    raus.extend(anmeldung_pruefen())
    # 5. Erreicht Telegram uns noch? Dieselbe Bauart wie bei der Anmeldung: Der
    # Bot hat den Schlüssel ohnehin und fragt selbst nach; die Blume liest nur
    # seine Marke. So gibt es keinen ZWEITEN Ort für ein Geheimnis.
    raus.extend(zustellung_pruefen())
    # 6. Lebt der 4-Uhr-Check noch? (Connis Fund, 28.07.)
    raus.extend(tagescheck_pruefen())
    return raus


# Der Tagescheck läuft täglich um 04:10. 26 Stunden lassen einen verspäteten
# Lauf (Neustart, Wartungsfenster, Zeitumstellung) durch und schlagen erst an,
# wenn wirklich einer ausgefallen ist.
#
# **Hier ist die feste Schwelle ausnahmsweise richtig** — anders als bei der
# Zeitgeber-Wache, die bewusst `NextElapseUSecRealtime` misst, statt einen Takt
# zu raten. Der Unterschied: Dort war der Takt unbekannt (der Versions-Monitor
# läuft wöchentlich, ein 26-Stunden-Maß hätte beim ersten Lauf angeschlagen).
# Hier ist er bekannt und fest. Eine Regel ist nicht deshalb schlecht, weil sie
# eine Zahl enthält, sondern wenn die Zahl geraten ist.
TAGESCHECK_STILL_S = 26 * 3600
TAGESCHECK_LOG = Path(os.environ.get("TAGESCHECK_LOG")
                      or "/home/claudebot/claude-telegram-bot/logs/daily-check.log")


def tagescheck_pruefen() -> list[tuple[str, str]]:
    """Schließt den blinden Fleck der Zeitgeber-Wache auf ihren eigenen Träger.

    **Der Fund (Conni, 28.07.):** Die Zeitgeber-Wache kann jeden Zeitgeber
    prüfen — außer den, der sie selbst startet. Sie lebt in `daily_check.sh`,
    und der läuft über einen Zeitgeber. Stirbt ausgerechnet dieser, stirbt die
    Wache mit ihm, und niemand meldet es.

    Das ist kein Konstruktionsfehler, sondern die übliche Grenze jeder
    Selbstprüfung: **Was ein Prüfer trägt, kann er nicht prüfen.** Die Lösung
    ist deshalb auch keine bessere Selbstprüfung, sondern eine zweite,
    unabhängige Instanz — die Stundenblumen laufen über einen eigenen
    Zeitgeber. Danach bewachen sich beide gegenseitig: die Blumen den
    Tagescheck über diese Zeile, der Tagescheck die Blumen über seine
    bestehende Ketten-Prüfung. **Kreuzverschränkung statt Selbstbezug.**

    Gemessen wird die Änderungszeit des Protokolls — es wird am Ende jedes
    Laufs geschrieben, unabhängig davon, ob der Lauf Probleme fand. Gefragt ist
    „ist er gelaufen", nicht „war er grün"; ein grüner Tag ist kein Ausfall.
    """
    try:
        alter = time.time() - TAGESCHECK_LOG.stat().st_mtime
    except FileNotFoundError:
        # Kein Protokoll heißt: noch nie gelaufen. Das ist ein echter Befund
        # und kein Grund zu schweigen — der Dämpfer sorgt dafür, dass er nicht
        # stündlich wiederkommt.
        return [("tagescheck-still",
                 "🔴 Vom 4-Uhr-Check gibt es überhaupt kein Protokoll — er "
                 "scheint noch nie gelaufen zu sein. Damit läuft auch die "
                 "Zeitgeber-Wache nicht, die in ihm wohnt.")]
    except OSError:
        return []                          # nicht lesbar: keine Aussage, kein Raten
    if alter < TAGESCHECK_STILL_S:
        return []
    stunden = int(alter // 3600)
    return [("tagescheck-still",
             f"🔴 Der 4-Uhr-Check hat sich seit etwa {stunden} Stunden nicht "
             "gemeldet. Mit ihm schweigt die Zeitgeber-Wache, der "
             "Regressionslauf und die Token-Alterung — also ausgerechnet die "
             "Prüfungen, die sonst alles andere melden.")]


def rollen(grenze: int | None = None, jetzt: float | None = None) -> str | None:
    """Legt die Kette beiseite und beginnt eine neue — **ohne sie zu zerreißen.**

    **Die Falle, um die es hier geht:** Ein Rollen, das einfach die Datei
    umbenennt, **bricht genau die Verkettung, die den Beleg ausmacht.** Das
    erste Glied der neuen Datei stünde ohne Vorgänger da, und die Prüfung
    könnte von da an nichts mehr über die Zeit davor sagen. Der Bruch sähe
    obendrein aus wie eine Manipulation — der Wächter würde sich selbst
    anzeigen.

    Deshalb: Das erste Glied der neuen Datei **zeigt auf das letzte der alten**.
    Die Kette läuft über die Dateigrenze hinweg weiter; nur das Lesen wird
    wieder billig.

    **Gemessen am 26.07., bevor das hier gebaut wurde:** 20 160 Glieder (also
    vierzehn Tage minütlich) sind **3,2 MiB**, und `--pruefen` braucht dafür
    **0,15 Sekunden**. Das Rollen ist also **keine Not, sondern Vorsorge** — bei
    einem Jahr Dauerbetrieb wären es rund 84 MiB, die jede Prüfung vollständig
    liest. Die Zahl steht hier, damit niemand später eine Dringlichkeit
    hineinliest, die nie gemessen wurde.
    """
    grenze = grenze or ROLL_GRENZE
    if not KETTE.exists():
        return None
    try:
        with KETTE.open("r", encoding="utf-8") as f:
            zeilen = sum(1 for _ in f)
    except OSError:
        return None
    if zeilen < grenze:
        return None

    letzte = _letzte()
    stempel = time.strftime("%Y%m%d-%H%M",
                            time.localtime(jetzt or time.time()))
    archiv = KETTE.with_name(f"{KETTE.name}.{stempel}")
    try:
        KETTE.rename(archiv)
    except OSError:
        return None
    # Der Anschluss: Das erste Glied der neuen Datei trägt den Abdruck des
    # letzten alten als `vorher` — genau wie jedes andere Glied auch. Damit ist
    # die Naht von einer gewöhnlichen Fortsetzung nicht zu unterscheiden.
    if letzte:
        _NAHT.write_text(json.dumps(
            {"vorher": letzte.get("abdruck", "—"),
             "quelle": archiv.name}, ensure_ascii=False), encoding="utf-8")
    return archiv.name


def zustellung_pruefen() -> list[str]:
    """Liest die Zustell-Marke — mehr nicht, und genau das ist der Punkt.

    Der gefährlichste Ausfall ist der, bei dem alle Anzeigen auf Grün stehen:
    Der Bot läuft, der Selbstcheck ist grün, die Kette wächst — und trotzdem
    kommt seit Stunden nichts mehr an. Die Marke ist das einzige Zeichen.
    """
    m = zustellmarke.gesetzt()
    if not m:
        return []
    seit = int((time.time() - float(m.get("zeit", 0))) / 60)
    zusatz = ("" if m.get("adresse_unveraendert", True)
              else " Die eingetragene Adresse weicht zudem von der erwarteten ab.")
    return [("zustellung-gestoert",
             f"📵 Zustellung gestört (seit {seit} Min): "
             f"{m.get('grund', 'ohne Angabe')}{zusatz} "
             "Der Bot läuft — aber es erreicht ihn womöglich nichts mehr.")]


# ------------------------------------------------------------ Speicher-Wache --
# **Warum das hier steht und nicht in Adams Aufmerksamkeit** (Werte-Charta 7a):
# *Was vorhersehbar knapp wird, wird beobachtet, bevor es knapp ist.* Der
# Arbeitsspeicher ist der Musterfall — er läuft nicht langsam voll wie eine
# Platte, sondern kippt: Der OOM-Killer schlägt ohne Vorwarnung zu und reißt
# mit, was gerade am meisten braucht. Am 25.07. gemessen: 7,53 GiB Spitzen bei
# 7,75 GiB vorhanden, und **kein Swap**.
#
# **Zwei Schwellen, weil sie zwei verschiedene Dinge bedeuten:** Unter 800 MiB
# ist es ein Hinweis, unter 400 MiB ist es die letzte Warnung vor dem Kippen.
# Bewusst nicht in Prozent — bei einer kleinen Maschine sind zehn Prozent von
# fast nichts immer noch fast nichts.
SPEICHER_HINWEIS_MIB = int(os.environ.get("BLUMEN_SPEICHER_HINWEIS") or 800)
# **Eine Setzung, kein Messwert** — und das steht hier, damit es niemand fuer
# eine Messung haelt. Belegt ist nur, dass sie im Normalbetrieb dieser Maschine
# nicht anschlaegt: Der gemessene Mittelwert lag rund dreihundertfach darunter
# (drei Seiten je Minute gegen tausend). Als Umgebungsgroesse, damit sie ohne
# Codeaenderung nachgezogen werden kann.
SWAP_SEITEN_SCHWELLE = int(os.environ.get("BLUMEN_SWAP_SEITEN") or 1000)
# Schreibfehler werden gesammelt statt verschluckt: Eine Blume, die ihren
# Vorwert nie ablegen kann, schwiege fuer immer — ein Ausbleiben, das wie Ruhe
# aussieht.
_SCHREIBFEHLER: list[str] = []
SPEICHER_ENG_MIB = int(os.environ.get("BLUMEN_SPEICHER_ENG") or 400)


def _meminfo() -> dict[str, int]:
    """Liest /proc/meminfo — Werte in MiB. Leer, wenn es die Datei nicht gibt."""
    raus: dict[str, int] = {}
    try:
        for zeile in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            name, _, rest = zeile.partition(":")
            teile = rest.split()
            if teile and teile[0].isdigit():
                raus[name.strip()] = int(teile[0]) // 1024
    except Exception:
        pass
    return raus


def speicher_pruefen() -> list[str]:
    """Meldet knappen Arbeitsspeicher, bevor der OOM-Killer entscheidet.

    **Gemessen wird `MemAvailable`, nicht `MemFree`** — und das ist der ganze
    Trick: `MemFree` sieht auf einem gesunden Linux immer bedrohlich klein aus,
    weil der Kernel freien Speicher als Zwischenspeicher benutzt und ihn
    jederzeit wieder hergibt. Ein Wächter auf `MemFree` wäre ein Dauer-Alarm und
    damit binnen zwei Tagen abgeschaltet. `MemAvailable` ist die Schätzung des
    Kernels selbst, wie viel wirklich zu holen wäre.

    **Der Swap wird mitgemeldet, wenn er benutzt wird** — nicht als Alarm,
    sondern als Beobachtung: Er soll das Netz für den Notfall sein, keine
    Ausweichfläche im Alltag (deshalb `vm.swappiness=10`). Wird er im Alltag
    angefasst, ist das der Hinweis, dass die Auslegung nicht mehr passt.
    """
    m = _meminfo()
    if not m:
        return []                         # kein Linux: keine Aussage, kein Raten
    verfuegbar = m.get("MemAvailable")
    if verfuegbar is None:
        return []
    raus: list[str] = []
    gesamt = m.get("MemTotal", 0)
    if verfuegbar < SPEICHER_ENG_MIB:
        raus.append((
            "speicher-eng",
            f"🔴 Nur noch {verfuegbar} MiB Arbeitsspeicher verfügbar von "
            f"{gesamt} MiB — das ist der Bereich, in dem der Kernel anfängt, "
            "Prozesse zu beenden. Wenn es den Bot trifft, merkt es niemand "
            "außer diesem Hinweis."))
    elif verfuegbar < SPEICHER_HINWEIS_MIB:
        raus.append((
            "speicher-hinweis",
            f"🟡 Der Arbeitsspeicher wird knapp: {verfuegbar} MiB verfügbar von "
            f"{gesamt} MiB. Noch kein Grund zur Eile, aber der Zeitpunkt, "
            "hinzusehen — bevor es einer werden muss."))
    # **Gemessen wird die AKTIVITAET, nicht der Bestand** (Auftrag 1 vom
    # 27.08., Adam freigegeben 18:04).
    #
    # Der alte Befund schlug an, sobald mehr als 256 MiB im
    # Auslagerungsbereich **lagen**. Der eigene Kommentar nannte die richtige
    # Absicht und das falsche Mass im selben Satz: *[Wird er im Alltag
    # ANGEFASST…]* — angefasst ist eine Handlung, gemessen wurde ein Bestand.
    #
    # **Gemessen am 27.08. auf dem VPS:** 594 MiB lagen drin, `pswpin` stand
    # bei **null** — in sechs Wochen wurde **nichts zurueckgeholt**. Das ist
    # kein Notfall, sondern Hausarbeit des Kernels. Der Bereich leert sich ohne
    # Neustart nicht, also haette dieser Befund **vierundzwanzigmal am Tag bis
    # in alle Ewigkeit** gemeldet, ohne dass je etwas zu tun ist. **Ein
    # Waechter, der taeglich meldet und nie etwas zu tun gibt, ist binnen zwei
    # Tagen abgeschaltet.**
    #
    # Der Befund entsteht jetzt nur, wenn **beides zugleich** zutrifft:
    # Auslagerung laeuft UND der Speicher ist knapp. Auslagerung bei reichlich
    # Speicher ist Hausarbeit; Auslagerung bei Enge ist das Vorzeichen des
    # Kippens. **Nur der zweite Fall verdient einen Waechter.**
    seiten = _swap_seiten_je_minute()
    if seiten is not None and seiten > SWAP_SEITEN_SCHWELLE \
            and verfuegbar < SPEICHER_HINWEIS_MIB:
        raus.append((
            NUR_PROTOKOLL + "swap-aktiv",
            f"↔️ Der Kernel lagert gerade aus: rund {int(seiten)} Seiten je "
            f"Minute, bei nur {verfuegbar} MiB verfügbarem Arbeitsspeicher. "
            "Auslagerung bei reichlich Speicher wäre Hausarbeit — bei Enge "
            "ist sie das Vorzeichen des Kippens."))
    return raus


def _swap_seiten_je_minute(jetzt: float | None = None) -> float | None:
    """Wie viele Seiten je Minute gerade ausgelagert werden — oder `None`.

    `/proc/vmstat` fuehrt `pswpout` als **kumulativen** Zaehler. Die Blume legt
    den zuletzt gesehenen Stand ab und bildet beim naechsten Lauf die
    Differenz; der minuetliche Takt ist das Fenster, es muss nichts gewartet
    werden.

    **Drei Faelle schweigen ausdruecklich** — keine Aussage ist besser als
    Raterei:

    * **Erster Lauf** (kein Vorwert): merken, nichts melden.
    * **Zaehlerruecksprung** (kleiner als zuletzt): Die Maschine wurde neu
      gestartet. Merken, nichts melden.
    * **`/proc/vmstat` nicht lesbar** (kein Linux, kein Recht): `None`.

    **Ein Schreibfehler wird NICHT verschluckt.** Liesse sich der Vorwert nie
    ablegen, schwiege die Blume fuer immer — ein Ausbleiben, das wie Ruhe
    aussieht. Deshalb wird er als eigener Befund gemeldet.
    """
    jetzt = time.time() if jetzt is None else jetzt
    try:
        roh = Path("/proc/vmstat").read_text(encoding="utf-8")
    except Exception:
        return None
    aktuell = None
    for zeile in roh.splitlines():
        if zeile.startswith("pswpout "):
            try:
                aktuell = int(zeile.split()[1])
            except (IndexError, ValueError):
                return None
            break
    if aktuell is None:
        return None

    merker = ZUSTAND / "swap-zaehler.json"
    vorher = {}
    try:
        vorher = json.loads(merker.read_text(encoding="utf-8"))
    except Exception:
        pass
    try:
        ZUSTAND.mkdir(parents=True, exist_ok=True)
        merker.write_text(json.dumps({"pswpout": aktuell, "zeit": jetzt}),
                          encoding="utf-8")
    except Exception:
        _SCHREIBFEHLER.append("swap-zaehler.json nicht schreibbar")

    alt_wert = vorher.get("pswpout")
    alt_zeit = float(vorher.get("zeit") or 0)
    if alt_wert is None or alt_zeit <= 0:
        return None                       # erster Lauf
    if aktuell < alt_wert:
        return None                       # Neustart: Zaehler zurueckgesprungen
    minuten = (jetzt - alt_zeit) / 60.0
    if minuten <= 0:
        return None
    return (aktuell - alt_wert) / minuten


# --------------------------------------------------------------- C2 Anmeldung --
# **[G1, 25.07.] Die Wortliste kommt aus `authmarke.py`, nicht von hier.**
# Vorher stand hier eine eigene — von sieben Marken war genau eine auch in der
# des Bots, und der wichtigste Fall ging um ein Wort daneben (`oauth token
# expired` gegen `oauth token has expired`). Zwei Listen driften; eine
# gemeinsame kann es nicht. Das ist stärker als ein Test, der den Drift meldet.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import authmarke  # noqa: E402
import zustellmarke  # noqa: E402


def anmelde_befunde(namen: set) -> list:
    """Aus der Menge der Umgebungs-NAMEN die Kosten-Befunde ableiten.

    **Herausgezogen, damit ein Pruefer sie erreicht** (Engywuck 24.08.). Vorher
    sass die Entscheidung mitten in `anmeldung_pruefen()` hinter einem
    `/proc`-Zugriff — nicht ausfuehrbar pruefbar, und genau deshalb ungeprueft.

    **Der Fehler, den das behebt:** Die API-Schluessel-Warnung sass INNERHALB
    von `if "CLAUDE_CODE_OAUTH_TOKEN" not in namen`. **Waren BEIDE gesetzt,
    schwieg der Waechter** — und `.env.example` benennt genau diesen Fall als
    die Gefahr: liegen beide, bevorzugt das SDK den Schluessel, das Abo bleibt
    ungenutzt, und es wird abgebucht. Der Waechter prueft seither den Fall, der
    dokumentiert ist, nicht den, den sich jemand vorgestellt hat.

    Es wird ausschliesslich mit NAMEN gearbeitet, nie mit Werten.
    """
    raus = []
    hat_abo = "CLAUDE_CODE_OAUTH_TOKEN" in namen
    if "ANTHROPIC_API_KEY" in namen:
        # Zwei verschiedene Lagen, zwei verschiedene Saetze. Die gefaehrlichere
        # ist die zweite, weil sie wie Ordnung aussieht: das Abo-Token liegt ja.
        zusatz = ("— und er liegt NEBEN dem Abo-Token: das SDK bevorzugt den "
                  "Schlüssel, das Abo bleibt ungenutzt."
                  if hat_abo else
                  "statt über das Abo-Token.")
        raus.append(("api-schluessel",
                     f"⚠️ Der Bot läuft über einen API-Schlüssel {zusatz} "
                     "Das bucht Geld ab — getrennt vom Abo!"))
    if not hat_abo:
        raus.append(("keine-abo-anmeldung", "Keine Abo-Anmeldung in der Dienst-Umgebung"))
    return raus


def anmeldung_pruefen(seit_s: int = 900) -> list[str]:
    """Meldet, wenn die Anmeldung gekippt ist — statt vorherzusagen, wann.

    **Was gemessen wurde, bevor das hier so gebaut wurde** (25.07.): Auf dem VPS
    gibt es **keine** `~/.claude/.credentials.json`. Die Anmeldung ist ein
    Abo-Token in der Dienst-Umgebung, Form `sk-ant-oat…`, 108 Zeichen, **ohne
    Punkte** — also **kein JWT**. Damit steckt **kein Ablaufdatum im Token**, und
    jede Restlaufzeit-Anzeige wäre erfunden. (Das ist genau die Klasse Aussage,
    die der Beleg-Grundsatz verbietet: ein Merkmal behaupten, das im Material
    nicht enthalten ist.)

    Also die ehrliche Umkehrung — **drei** deterministische Prüfungen, kein
    Modell-Aufruf, kein Netz, und der Wert des Geheimnisses wird nie gelesen:

    0. **Liegt eine Marke?** `[NEU G1]` Der **Bot selbst** schreibt sie im
       Augenblick des Bruchs — er behandelt den Fall ja gerade und weiß es
       genauer als jeder Horcher. Das ist der **vorrangige** Weg: eigenes
       Format, keine Journal-Rechte nötig, und gleichgültig dagegen, wie der
       Anbieter seine Fehlermeldung morgen formuliert.
    1. **Ist überhaupt eine Anmeldung da?** Nur Vorhandensein, nie der Wert.
    2. **Hat sie zuletzt versagt?** Auth-Wortlaute im Journal — als **zweites
       Netz** für den Fall, dass der Bot zum Schreiben der Marke nicht mehr kam.

    **`[G2, 25.07.]` „Konnte nicht nachsehen" ist ein eigener Zustand.** Vorher
    endeten beide Prüfungen bei `except: pass` mit dem Vermerk „nicht lesbar ist
    kein Befund" — das ist genau die Krankheit, gegen die die Stundenblumen
    erfunden wurden, diesmal **im Wächter selbst**: Ein Prüfer, der nicht
    hinsehen kann, ist von einem, der nichts findet, nicht zu unterscheiden.
    **Gemessen (25.07., auf dem VPS):** Der Dienst läuft als `claudebot`, der
    Prüfer ebenso — Journal und Prozess-Umgebung sind **beide lesbar**. Es ist
    also heute kein blinder Fleck; aber sobald sich der Dienstnutzer oder die
    Härtung ändert, wird er einer, und dann soll es auffallen.
    """
    raus: list[tuple[str, str]] = []

    # (0) Die Marke — der vorrangige Weg.
    marke = authmarke.gesetzt()
    if marke:
        raus.append(("anmeldung-gekippt", "🔑 Die Anmeldung hat versagt (" + marke.get("menschlich", "?")
                    + "): " + str(marke.get("ursache", ""))[:120]
                    + " — das Abo-Token muss neu erzeugt werden. Bis dahin "
                      "arbeitet nichts, was ein Modell braucht."))

    pid = ""
    if shutil.which("systemctl"):
        try:
            p = subprocess.run(["systemctl", "show", "claude-telegram-bot",
                                "-p", "MainPID", "--value"],
                               capture_output=True, text=True, timeout=10)
            pid = (p.stdout or "").strip()
        except Exception:
            raus.append(("blind-dienst",
                         "👁️ Ich konnte den Dienst nicht abfragen — ab hier "
                         "sehe ich die Anmeldung nicht mehr."))
            return raus
    if not pid or pid == "0":
        return raus                       # kein Prozess — meldet Prüfung 1 schon

    # (1) Vorhandensein — es wird nur der NAME gesucht, nie der Wert gelesen.
    try:
        roh = Path(f"/proc/{pid}/environ").read_bytes().decode("utf-8", "replace")
        namen = {z.split("=", 1)[0] for z in roh.split("\0") if "=" in z}
        raus.extend(anmelde_befunde(namen))
    except Exception as e:
        raus.append(("blind-umgebung",
                     "👁️ Ich darf die Umgebung des Bot-Prozesses nicht lesen "
                     f"({type(e).__name__}) — diese Prüfung ist blind. Das ist "
                     "kein Entwarnungs-, sondern ein Rechte-Befund."))

    # (2) Zweites Netz: Wortlaute im Journal. Nur die letzten Minuten, damit ein
    # alter Fehler nicht ewig nachhallt — und nur, wenn keine Marke liegt.
    if shutil.which("journalctl") and not marke:
        try:
            p = subprocess.run(
                ["journalctl", "-u", "claude-telegram-bot", "--since",
                 f"{max(60, seit_s)} seconds ago", "--no-pager", "-q"],
                capture_output=True, text=True, timeout=20)
            if p.returncode != 0:
                raus.append(("blind-journal",
                             "👁️ Ich darf das Journal des Dienstes nicht lesen — "
                             "das zweite Netz für Anmelde-Brüche ist blind."))
            else:
                text = (p.stdout or "").lower()
                treffer = [m for m in authmarke.NADELN if m in text]
                if treffer:
                    raus.append((
                        "anmeldung-gekippt",
                        "🔑 Die Anmeldung hat versagt (" + treffer[0]
                        + ") — das Abo-Token muss neu erzeugt werden."))
        except Exception:
            raus.append((
                "journal-unabfragbar",
                "👁️ Das Journal war nicht abfragbar — das zweite Netz "
                "für Anmelde-Brüche ist blind."))
    return raus


def bluehen(jetzt: float | None = None) -> dict:
    """Eine Blume: Lücke bewerten, prüfen, Glied anhängen, ggf. melden."""
    jetzt = jetzt or time.time()
    ZUSTAND.mkdir(parents=True, exist_ok=True)
    vorige = _letzte()
    ruhegrund = _in_ruhe(jetzt)
    befunde = _befunde()          # (Kennung, Text) je Befund

    luecke = None
    if vorige is not None:
        luecke = jetzt - float(vorige.get("zeit", jetzt))

    # Ist die Kette frisch gerollt, steht der Vorgaenger in der Naht — sonst
    # begaenne die neue Datei ohne Anschluss und der Beleg waere zerrissen.
    naht = None
    if vorige is None:
        try:
            naht = json.loads(_NAHT.read_text(encoding="utf-8"))
        except Exception:
            naht = None

    eintrag = {
        "zeit": round(jetzt, 3),
        "menschlich": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(jetzt)),
        "vorher": ((vorige or {}).get("abdruck")
                   or (naht or {}).get("vorher") or "—"),
        "luecke_s": round(luecke, 1) if luecke is not None else None,
        "ruhe": ruhegrund,
        # In der Kette stehen nur die TEXTE — sie ist ein Beleg für Menschen.
        # Die Kennungen begleiten den Lauf und gehen an den Dämpfer.
        "befunde": [t for _, t in befunde],
    }
    eintrag["abdruck"] = _fingerabdruck(eintrag)
    if naht:                       # Naht verbraucht — sie gilt genau einmal
        try:
            _NAHT.unlink()
        except OSError:
            pass
    try:
        with KETTE.open("a", encoding="utf-8") as f:
            f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    except Exception:
        pass

    # G3: Der Zustand wandert IMMER in den Log-Abgleich — auch wenn nichts zu
    # melden ist. Gerade das Ausbleiben dieser Datei wäre der Alarm.
    lagebericht_schreiben(eintrag)

    # Melden: nur bei echtem Anlass, nie in der Ruhe — und nicht minütlich
    # dasselbe (G4).
    if not ruhegrund:
        gruende = [(k, t) for k, t in befunde]
        if luecke is not None and luecke > TOLERANZ_S:
            # **Ein Ereignis, kein Zustand** — deshalb ohne Entprellung.
            gruende.insert(0, (SOFORT + "kette-luecke",
                               f"Die Kette hatte eine Lücke von "
                               f"{luecke / 60:.0f} Minuten — in dieser Zeit hat "
                               "niemand belegt, dass das System lebt."))
        # **Der Filter greift VOR dem Daempfer, nicht danach** (Auftrag 2 vom
        # 27.08.). Filterte man nur die Meldungen, kaeme die Warnung nicht an,
        # die **Entwarnung aber schon** — Adam bekaeme ein [erledigt], ohne je
        # die Warnung gesehen zu haben. Das ist derselbe Fehler wie am 28.07.,
        # nur seitenverkehrt. Vor dem Daempfer getrennt, kann keine Entwarnung
        # entstehen, die es nicht geben darf.
        #
        # **Die Kette schreibt weiter alles mit** — `p:`-Befunde stehen
        # vollstaendig im Protokoll und in `kette.jsonl`. Nur der Weg zu Adam
        # entfaellt. **Der Nachweis geht nicht verloren, er wird still.**
        still = [(k, tx) for k, tx in gruende if k.startswith(NUR_PROTOKOLL)]
        gruende = [(k, tx) for k, tx in gruende if not k.startswith(NUR_PROTOKOLL)]
        # Ins Protokoll, nicht in den Chat. Die Blume hat keinen Logger —
        # sie schreibt ihren Nachweis in die Kette; `eintrag` traegt die
        # Befunde ohnehin vollstaendig, `p:`-Kennungen eingeschlossen.
        # **Kein zweiter Ort, keine zweite Wahrheit.**
        neu, entwarnt = _daempfen(gruende, jetzt)
        # 🪷 Lotus für den neuen Befund, 🌺 Hibiskus für die Entwarnung
        # (Adams Festlegung, 28.07.): die beginnende gegen die vollendete Blüte.
        # Die Signatur sagt **wer**, die Zustandszeichen im Text sagen **was**.
        if neu:
            melden("🪷 Stundenblume " + eintrag["menschlich"] + ":\n• "
                   + "\n• ".join(neu))
        if entwarnt:
            melden("🌺 Stundenblume " + eintrag["menschlich"]
                   + ": erledigt —\n• " + "\n• ".join(entwarnt))
    return eintrag


# ------------------------------------------------------------------ Dämpfer --
# Wie lange ein bereits gemeldeter Befund schweigt, bevor er sich wiederholt.
# **Kennungen mit diesem Praefix werden geschrieben, aber nicht gesendet.**
#
# Nach der Meldungs-Einteilung vom 21.08. gibt es drei Klassen: was Adam
# betrifft, was technisch ist und ohnehin bearbeitet wird, und was reiner
# Nachweis ist. Die zweite Klasse gehoert ins Protokoll und an die
# Kontrollsitzung — **nicht in Adams Chat.**
#
# **Warum ein Praefix und kein drittes Feld:** Die Befundlisten sind heute
# uneinheitlich getippt (als `list[str]` deklariert, Tupel zurueckgegeben). Ein
# drittes Feld zwaenge jede entpackende Stelle zur Aenderung und braeche
# stillschweigend jede, die uebersehen wird.
#
# **Warum keine zentrale Ausschlussliste:** Eine Liste an anderer Stelle waechst
# nicht mit. Wer kuenftig einen Befund anlegt, sieht sie nicht und meldet an
# Adam, ohne es zu wollen. **Die Einstufung gehoert an den Befund selbst** —
# das Praefix steht dort, wo der Befund entsteht, und laesst sich nicht
# vergessen.
NUR_PROTOKOLL = "p:"

# **Kennungen mit diesem Praefix werden SOFORT gemeldet, ohne Entprellung.**
#
# **Beim Bauen der Entprellung gefunden (28.08.):** Der Auftrag verlangt, dass
# ein Befund erst nach drei Laeufen in Folge als aufgetreten gilt. Das trifft
# **Zustands**-Befunde richtig (Speicher knapp, Bot weg) — aber eine
# **Kettenluecke ist ein Ereignis**: Sie tritt genau einmal auf und ist danach
# vergangen. Mit Entprellung waere sie **nie wieder gemeldet worden**, und sie
# ist der Kern-Alarm dieser Wache: *[in dieser Zeit hat niemand belegt, dass
# das System lebt.]*
#
# Dieselbe Bauform wie beim Protokoll-Praefix, aus demselben Grund: **Die
# Einstufung gehoert an den Befund selbst.** Eine Liste an anderer Stelle
# waechst nicht mit — wer kuenftig ein Ereignis anlegt, sieht sie nicht.
SOFORT = "!"

# **Der Melde-Ausloeser ist die AENDERUNG, nicht die Zeit** (Auftrag 3 vom
# 28.08.). Bis dahin schwieg der Daempfer eine Stunde und wertete den Befund
# danach wieder als neu. Das galt im Juli als Fortschritt — davor meldete die
# Blume minuetlich —, war aber an einem **Dauerzustand** zu Ende gedacht: Er
# endet nie von selbst. Gemessen: zwanzig wortgleiche Meldungen in zwanzig
# Stunden, dreizehn davon voellig unveraendert.
#
# `WIEDERVORLAGE_S` bleibt als Groesse erhalten, hat aber die neue Bedeutung
# einer **Sperrfrist nach Entwarnung** und heisst danach.
ERNEUT_SPERRE_S = int(os.environ.get("BLUMEN_ERNEUT_SPERRE") or 1800)

# **Entprellung — die Begriffe sind Handwerk, nicht Erfindung.** Prometheus
# kennt beides seit Jahren: `for` wartet ab, ob eine Bedingung anhaelt, bevor
# ein Alarm zaehlt; `keep_firing_for` haelt ihn nach dem Wegfall noch eine
# Weile, ausdruecklich gegen flatternde Alarme. **Wir uebernehmen das
# Verfahren, nicht das Werkzeug.**
#
# **Als Zaehler, nicht als Zeitstempel** — dann traegt die Regel auch, wenn der
# Takt einmal geaendert wird.
MELDE_LAEUFE = int(os.environ.get("BLUMEN_MELDE_LAEUFE") or 3)
ENTWARN_LAEUFE = int(os.environ.get("BLUMEN_ENTWARN_LAEUFE") or 5)

# **Eine Erinnerung nach zwoelf Stunden, nur bei Rot** (Adams Entscheidung 2,
# Engywucks Empfehlung A). Rot heisst *Warten auf Adams Daumen*; ein rotes
# Ereignis um 05:00 Uhr, das bis zum naechsten Morgen schweigt, ist der stille
# Bruch. Bei Gelb und Beobachtung gilt das nicht.
ERINNERUNG_S = int(os.environ.get("BLUMEN_ERINNERUNG") or 12 * 3600)

# Entwarnte Kennungen bleiben im Gedaechtnis, damit die Sperrfrist greift —
# aber nicht ewig. Die Zahl der Kennungen ist zweistellig; die Grenze ist
# Vorsorge, keine Not.
VERFALL_S = 7 * 24 * 3600

WIEDERVORLAGE_S = int(os.environ.get("BLUMEN_WIEDERVORLAGE") or 3600)
_GEDAECHTNIS = ZUSTAND / "gemeldet.json"
# Naht-Speicher fuer das Rollen: haelt den Abdruck des letzten Glieds der
# beiseitegelegten Datei fest, damit die neue Kette daran anschliesst.
_NAHT = ZUSTAND / "naht.json"
# Ab wie vielen Zeilen gerollt wird. 20160 = vierzehn Tage minuetlich.
ROLL_GRENZE = int(os.environ.get("BLUMEN_ROLL_GRENZE") or 20160)


def _daempfen(gruende: list[tuple[str, str]],
              jetzt: float) -> tuple[list[str], list[str]]:
    """Erste Meldung sofort, Wiederholung frühestens nach einer Stunde.

    **Warum das kein Feinschliff ist (G4):** Ohne Dämpfer meldet ein
    anhaltender Befund **minütlich** — eine Stunde sind sechzig Nachrichten,
    vierzehn Tage wären es theoretisch zwanzigtausend. Das widerspricht dem
    eigenen Satz im Dateikopf: *Ein Wächter, dem niemand mehr glaubt, ist
    schlimmer als keiner.*

    **Verglichen wird die KENNUNG, nie der Wortlaut.** `[ERSETZT 28.07.]`

    Belegt am selben Tag um 10:02: Der Befund lautete „Zustellung gestört (seit
    9 Min)", eine Minute später „(seit 10 Min)". Ein Dämpfer, der Texte
    vergleicht, hält das für einen **neuen** Befund — und den Text der
    Vorminute für **weggefallen**. Ergebnis: zwei Nachrichten pro Minute,
    Alarm und Entwarnung im selben Atemzug. Der Dämpfer, der den Lärm
    verhindern sollte, hat ihn verdoppelt.

    Mein erster Fix bereinigte die Zahlen aus dem Text. Das hätte funktioniert
    und war trotzdem der schwächere Weg: **eine Heuristik, die im Hintergrund
    rät.** Die Kennung ist eine Zusage, die die Signatur erzwingt — wer künftig
    einen Prüfer anhängt, *kann* die Kennung nicht vergessen, statt unbemerkt
    auf den Lärm-Weg zurückzufallen. *Wo Struktur und Prüfer beide möglich
    sind, gewinnt die Struktur.*

    **Die Kette schreibt weiter minütlich; nur der Mund wird leiser, nicht das
    Auge.** Und was wegfällt, wird ausdrücklich **entwarnt** — sonst weiß
    niemand, ob es behoben ist oder der Wächter nur müde wurde.
    """
    try:
        bekannt = json.loads(_GEDAECHTNIS.read_text(encoding="utf-8"))
    except Exception:
        bekannt = {}
    if not isinstance(bekannt, dict):
        bekannt = {}

    def _eintrag(k: str) -> dict:
        e = bekannt.get(k)
        if isinstance(e, dict):
            return dict(e)
        # Alte Form (Zeitstempel oder {zeit,text}) vertraeglich einlesen:
        # nach dem Einspielen steht das Gedaechtnis noch in der Vorform.
        return {"text": k, "gesehen": 0, "gefehlt": 0,
                "gemeldet_seit": None, "entwarnt_um": None}

    aktuell = {k: tx for k, tx in gruende}
    stand: dict[str, dict] = {}
    neu: list[str] = []
    entwarnt: list[str] = []

    for kennung, text in gruende:
        e = _eintrag(kennung)
        e["text"] = text
        e["gesehen"] = int(e.get("gesehen") or 0) + 1
        e["gefehlt"] = 0
        if not e.get("gemeldet_seit"):
            # **Verzoegerte Meldung:** Erst nach MELDE_LAEUFE Laeufen in Folge
            # gilt ein Befund als aufgetreten. Kurze Zuckungen bleiben still,
            # ein echter Ausfall meldet drei Minuten spaeter.
            if e["gesehen"] >= MELDE_LAEUFE or kennung.startswith(SOFORT):
                seit_entwarnung = jetzt - float(e.get("entwarnt_um") or 0)
                if e.get("entwarnt_um") and seit_entwarnung < ERNEUT_SPERRE_S:
                    pass          # **Sperrfrist** — kommt wieder, schweigt noch
                else:
                    neu.append(text)
                    e["gemeldet_seit"] = jetzt
                    e["entwarnt_um"] = None
        elif text.startswith("🔴") and \
                jetzt - float(e["gemeldet_seit"]) >= ERINNERUNG_S:
            # Erinnerung, nur bei Rot.
            neu.append(text)
            e["gemeldet_seit"] = jetzt
        stand[kennung] = e

    for kennung, roh in bekannt.items():
        if kennung in aktuell:
            continue
        e = _eintrag(kennung)
        e["gefehlt"] = int(e.get("gefehlt") or 0) + 1
        e["gesehen"] = 0
        if e.get("gemeldet_seit") and e["gefehlt"] >= ENTWARN_LAEUFE:
            # **Verzoegerte Entwarnung:** Ein kurzes Aussetzen erzeugt kein
            # [erledigt]. Und entwarnt wird mit dem TEXT, nicht mit der
            # Kennung — der Live-Fund vom 28.07.: [erledigt — kette-luecke]
            # war technisch richtig und fuer einen Menschen unbrauchbar.
            entwarnt.append(e.get("text") or kennung)
            e["gemeldet_seit"] = None
            e["entwarnt_um"] = jetzt
        # **Entwarnte bleiben im Gedaechtnis** — sonst greift die Sperrfrist
        # nicht. Genau das war der Fehler bis zum 28.08.: Der Stand wurde nur
        # aus den AKTUELLEN Gruenden gebaut, eine entwarnte Kennung fiel heraus
        # und war beim naechsten Auftreten unbekannt. `jetzt − 0 >= 3600` traf
        # dann immer zu. Belegt am 16.08.: sechsundzwanzig Wechsel in fuenfzig
        # Minuten, dreizehn Alarme und dreizehn Entwarnungen — der Daempfer war
        # wirkungslos, weil jede Entwarnung sein Gedaechtnis leerte.
        if e.get("entwarnt_um") and jetzt - float(e["entwarnt_um"]) > VERFALL_S:
            continue              # verfallen, nicht uebernehmen
        stand[kennung] = e

    try:
        ZUSTAND.mkdir(parents=True, exist_ok=True)
        tmp = _GEDAECHTNIS.with_suffix(".tmp")
        tmp.write_text(json.dumps(stand, ensure_ascii=False), encoding="utf-8")
        tmp.replace(_GEDAECHTNIS)
    except Exception:
        pass
    return neu, entwarnt


def kette_pruefen(jetzt: float | None = None) -> dict:
    """Bewertet die Kette — für den 4-Uhr-Check (8.1).

    Prüft zweierlei: **Ist sie frisch?** (blüht überhaupt noch etwas) und **ist
    sie unversehrt?** (passen die Fingerabdrücke aneinander).
    """
    jetzt = jetzt or time.time()
    if not KETTE.exists():
        return {"ok": False, "grund": "Es gibt noch keine Kette."}
    letzte = _letzte()
    if letzte is None:
        return {"ok": False, "grund": "Die Kette ist leer."}
    alter = jetzt - float(letzte.get("zeit", 0))
    frisch = alter <= TOLERANZ_S or bool(_in_ruhe(jetzt))

    # Unversehrtheit — zwei Prüfungen, und die zweite ist die eigentliche:
    #   (a) zeigt jedes Glied auf das vorige?
    #   (b) passt der gespeicherte Abdruck noch zum INHALT des Glieds?
    # Ohne (b) wäre die Kette Zierde: Wer ein Glied verändert, ohne seinen
    # Abdruck anzufassen, bliebe unsichtbar — genau das hat der erste Testlauf
    # am 25.07. aufgedeckt. Ein Fingerabdruck, der nie nachgerechnet wird,
    # belegt nichts.
    brueche, vorher = 0, None
    try:
        with KETTE.open(encoding="utf-8") as f:
            for z in f:
                if not z.strip():
                    continue
                e = json.loads(z)
                if _fingerabdruck(e) != e.get("abdruck"):
                    brueche += 1                      # (b) Inhalt verändert
                elif vorher is not None and e.get("vorher") != vorher:
                    brueche += 1                      # (a) Glied ausgetauscht
                vorher = e.get("abdruck")
    except Exception as e:
        return {"ok": False, "grund": f"Kette nicht lesbar: {e}"}

    ok = frisch and brueche == 0
    grund = ""
    if not frisch:
        grund = (f"Die jüngste Blume ist {alter / 60:.0f} Minuten alt — "
                 "die Kette steht still.")
    elif brueche:
        grund = (f"{brueche} Bruchstelle(n) in der Kette — ein Glied zeigt nicht "
                 "auf das vorige. Das ist sichtbar gemacht, nicht verhindert.")
    return {"ok": ok, "grund": grund, "alter_s": round(alter),
            "brueche": brueche}


# ------------------------------------------------- G3: der Weg ohne den Bot --
# Alle Meldewege dieses Systems — Blumen, Hora, Start-Wächter — legen ins
# Boten-Postfach, und **zugestellt wird vom Bot**. Mit `Restart=always` deckt
# das den Normalfall. Der Restfall bleibt: ein Bot, der dauerhaft nicht
# hochkommt. Dann sammeln sich die Meldungen im Ausgang, und Adam hört
# vierzehn Tage nichts — der Befund „Bot-Prozess nicht vorhanden" müsste vom
# nicht vorhandenen Bot zugestellt werden.
#
# **Die Umkehrung, eine Ebene höher:** Der Log-Abgleich läuft (ab Schritt 1
# stündlich) über einen eigenen Bereitstellungs-Schlüssel in ein eigenes Repo —
# **unabhängig von Bot und Telegram**. Legt die Blume ihren Zustand dort ab,
# kann Adam vom Telefon über GitHub nachsehen, auch wenn der Bot stumm ist. Und
# **bleiben die Commits aus, ist das Ausbleiben selbst der Alarm** — dieselbe
# Idee wie bei der Kette, nur außerhalb der Maschine.
#
# ⚠️ **Nur Zustand, nie Inhalte, nie Geheimnisse.** Was hier landet, wird
# öffentlich sichtbar, sobald jemand das Repo einsieht.
LAGEBERICHT = Path(os.environ.get("LOG_SYNC_REPO")
                   or (Path.home() / "logsync" / "claude-bot-logs")) / "zustand.json"


def lagebericht_schreiben(eintrag: dict) -> None:
    """Legt den Zustand in den Log-Abgleich — Adams zweiter Meldeweg."""
    try:
        if not LAGEBERICHT.parent.is_dir():
            return                        # kein Klon vorhanden: nichts erfinden
        knapp = {
            "stand": eintrag.get("menschlich"),
            "befunde": eintrag.get("befunde", []),
            "luecke_s": eintrag.get("luecke_s"),
            "ruhe": eintrag.get("ruhe", ""),
            "abdruck": eintrag.get("abdruck"),
        }
        tmp = LAGEBERICHT.with_suffix(".tmp")
        tmp.write_text(json.dumps(knapp, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        tmp.replace(LAGEBERICHT)
    except Exception:
        pass


def _lage_ausgeben() -> int:
    """Was derzeit ansteht — je Befund eine Zeile, mit dem ersten Auftreten.

    **Auftrag 5 vom 28.08.** Seit der Umstellung meldet ein Befund genau
    einmal und schweigt danach. Ohne diese Ausgabe wuesste Adam am naechsten
    Tag nicht mehr, **was noch offen ist** — die Meldung ist vergangen, der
    Zustand nicht.

    **Damit hat jede Klasse einen Weg:** Ein Befund, der auftritt oder
    wegfaellt, geht sofort und einmal nach Telegram. Einer, der unveraendert
    ansteht, erscheint hier — einmal taeglich. Und `p:`-Befunde bleiben in
    Kette und Protokoll.

    **Gelesen wird DIESELBE Datei, die der Daempfer schreibt.** Kein zweiter
    Zustand, keine zweite Wahrheit — sonst koennte die Lage etwas anderes
    sagen als gemeldet wurde.
    """
    try:
        bekannt = json.loads(_GEDAECHTNIS.read_text(encoding="utf-8"))
    except Exception:
        bekannt = {}
    offen = [(k, e) for k, e in (bekannt or {}).items()
             if isinstance(e, dict) and e.get("gemeldet_seit")]
    if not offen:
        # **Still an ruhigen Tagen** (Adams Entscheidung 1, Empfehlung A):
        # [nichts zu tun] ist genau das Rauschen, das weg soll. Der Nachweis
        # bleibt in Kette und Protokoll lesbar.
        return 0
    for kennung, e in sorted(offen, key=lambda x: float(x[1]["gemeldet_seit"])):
        seit = time.strftime("%d.%m. %H:%M",
                             time.localtime(float(e["gemeldet_seit"])))
        print(f"↳ steht an seit {seit}: {e.get('text') or kennung}")
    return 0


def melden(text: str) -> None:
    """Meldet über die gemeinsame Botenpost — mit Absender.

    Vorher legte jeder Schreiber seine Datei selbst ab, mit vier fast
    gleichen Codeblöcken und OHNE Absender. Als am 26.07. nachts eine
    Meldung bei Adam ankam, kostete die Suche nach ihrem Urheber über
    eine Stunde — die Nachricht hätte es selbst sagen können.
    """
    botenpost.legen(text, "blume")


def main() -> int:
    ap = argparse.ArgumentParser(description="Stundenblumen — Belegkette")
    ap.add_argument("--pruefen", action="store_true", help="Kette bewerten")
    ap.add_argument("--lage", action="store_true",
                    help="was derzeit ansteht, je Befund eine Zeile")
    ap.add_argument("--rollen", action="store_true",
                    help="Kette beiseitelegen, wenn sie zu lang ist")
    ap.add_argument("--ruhe", type=int, metavar="MINUTEN",
                    help="Ruhefenster setzen (kein Alarm)")
    a = ap.parse_args()
    if a.lage:
        return _lage_ausgeben()
    if a.ruhe:
        ruhe_setzen(a.ruhe)
        print(f"Ruhe für {a.ruhe} Minuten gesetzt.")
        return 0
    if a.rollen:
        name = rollen()
        if name:
            print(name)
        return 0
    if a.pruefen:
        e = kette_pruefen()
        print(("✅ Kette lebt" if e["ok"] else f"❌ {e['grund']}")
              + f" (jüngste Blume vor {e.get('alter_s', '?')} s, "
                f"{e.get('brueche', 0)} Bruchstelle(n))")
        return 0 if e["ok"] else 1
    e = bluehen()
    print(f"🪷 {e['menschlich']} · {e['abdruck']} · "
          + (", ".join(e["befunde"]) if e["befunde"] else "nichts Auffälliges")
          + (f" · {e['ruhe']}" if e["ruhe"] else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
