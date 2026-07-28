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
nichts und darf deshalb laufen, so oft sie will. Sieht sie etwas Auffälliges,
weckt sie ein Modell — billig immer, teuer nur bei Anlass.

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
    return raus


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
    swap_gesamt = m.get("SwapTotal", 0)
    swap_frei = m.get("SwapFree", 0)
    if swap_gesamt and (swap_gesamt - swap_frei) > 256:
        raus.append((
            "swap-benutzt",
            f"↔️ Es liegen {swap_gesamt - swap_frei} MiB im Auslagerungsbereich. "
            "Der soll das Netz für den Notfall sein, keine Ausweichfläche im "
            "Alltag — wird er regelmäßig angefasst, passt die Auslegung nicht "
            "mehr."))
    return raus


# --------------------------------------------------------------- C2 Anmeldung --
# **[G1, 25.07.] Die Wortliste kommt aus `authmarke.py`, nicht von hier.**
# Vorher stand hier eine eigene — von sieben Marken war genau eine auch in der
# des Bots, und der wichtigste Fall ging um ein Wort daneben (`oauth token
# expired` gegen `oauth token has expired`). Zwei Listen driften; eine
# gemeinsame kann es nicht. Das ist stärker als ein Test, der den Drift meldet.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import authmarke  # noqa: E402
import zustellmarke  # noqa: E402


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
        if "CLAUDE_CODE_OAUTH_TOKEN" not in namen:
            if "ANTHROPIC_API_KEY" in namen:
                raus.append(("api-schluessel",
                             "⚠️ Der Bot läuft über einen API-Schlüssel statt "
                             "über das Abo-Token — das bucht Geld ab!"))
            else:
                raus.append(("keine-abo-anmeldung", "Keine Abo-Anmeldung in der Dienst-Umgebung"))
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
            gruende.insert(0, ("kette-luecke",
                               f"Die Kette hatte eine Lücke von "
                               f"{luecke / 60:.0f} Minuten — in dieser Zeit hat "
                               "niemand belegt, dass das System lebt."))
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

    def _zeit(e) -> float:
        return float((e or {}).get("zeit", e or 0) or 0) if isinstance(e, dict) \
            else float(e or 0)

    def _text(k: str) -> str:
        e = bekannt.get(k)
        return (e or {}).get("text", k) if isinstance(e, dict) else k

    neu = [text for kennung, text in gruende
           if jetzt - _zeit(bekannt.get(kennung)) >= WIEDERVORLAGE_S]
    aktuell = {kennung for kennung, _ in gruende}
    # **Entwarnt wird mit dem TEXT, nicht mit der Kennung.** `[LIVE-FUND 28.07.]`
    # Der erste echte Lauf nach dem Umbau meldete Adam wörtlich „erledigt —
    # kette-luecke". Technisch richtig, für einen Menschen unbrauchbar: Die
    # Kennung ist das Werkzeug des Dämpfers, nicht seine Sprache. Deshalb legt
    # das Gedächtnis neben dem Zeitpunkt auch den zuletzt gemeldeten Wortlaut
    # ab — sonst wäre er beim Entwarnen nicht mehr da.
    entwarnt = [_text(k) for k in bekannt if k not in aktuell]

    stand = {kennung: {"zeit": (jetzt if text in neu
                               else _zeit(bekannt.get(kennung)) or jetzt),
                       "text": text}
             for kennung, text in gruende}
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
    ap.add_argument("--rollen", action="store_true",
                    help="Kette beiseitelegen, wenn sie zu lang ist")
    ap.add_argument("--ruhe", type=int, metavar="MINUTEN",
                    help="Ruhefenster setzen (kein Alarm)")
    a = ap.parse_args()
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
