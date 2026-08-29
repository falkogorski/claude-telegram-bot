#!/usr/bin/env python3
# <!-- ROLLE: versions-monitor -->
"""5.21 — Versions-/Update-Monitor (register-basiert, DETERMINISTISCH).

Liest components.json, ermittelt je Komponente die installierte und die
verfügbare Version aus KOSTENFREIEN Quellen (PyPI, npm-Registry, nodejs.org)
und meldet neuere Versionen per Telegram — Major-Sprünge markiert. **KEIN
Modell-/Claude-Aufruf** (AGB-Leitplanke), **keine Installation** (nur Hinweis,
E3). Läuft wöchentlich als systemd-Timer; meldet nur, wenn es etwas gibt.

Aufruf (auf dem VPS, als root, damit alle venvs + der Bot-Token erreichbar sind):
    python3 scripts/version_monitor.py
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "components.json"
# **[BERICHTIGT 29.08., Engywucks Maschinen-Gleichstand, Fund ②]** Der
# Rueckfall war der feste VPS-Pfad — auf dem Mac zeigt er ins Leere. Die
# Bauform (Umgebungsgroesse mit Vorgabe) war richtig, die Vorgabe nicht.
# **Abgeleitet statt getippt**, dieselbe Lehre wie bei `_REPO_MARKEN`: Der
# Ort ergibt sich aus dem Ort dieser Datei und stimmt damit auf jeder
# Maschine.
LOGFILE = Path(os.environ.get("VERSION_MONITOR_LOG")
               or (ROOT / "logs" / "version-monitor.log"))
ENVFILE = os.environ.get("BOT_ENVFILE") or "/etc/claude-telegram-bot.env"
HTTP_TIMEOUT = 15


def _get_json(url: str) -> dict | None:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "momo-version-monitor"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception:
        return None


def _run(cmd: list[str]) -> str:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
    except Exception:
        return ""


def _vtuple(v: str) -> tuple[int, ...]:
    nums = re.findall(r"\d+", v or "")
    return tuple(int(n) for n in nums[:4]) or (0,)


# **Nicht jede Art lässt sich der Größe nach vergleichen.**
# Ein Docker-Fingerabdruck hat keine Reihenfolge — er ist gleich oder anders.
# Und eine Debian-Version wie `7:5.1.6-0+deb12u1` zerfällt beim Zahlenlesen in
# Ziffern, deren Reihenfolge nichts mehr bedeutet (die führende `7` ist eine
# Epoche, keine Hauptversion). Bei beiden ist die Frage ohnehin eine andere:
# nicht „gibt es irgendwo Neueres", sondern „weicht das ab, was diese Maschine
# mir anbietet". Darum wird hier auf UNGLEICHHEIT geprüft, nicht auf Größe —
# ein Zahlenvergleich hätte hier still immer „aktuell" gemeldet.
_VERGLEICH_UNGLEICH = {"docker", "systempaket"}


def _debian_hauptversion(v: str) -> int | None:
    """Erste Zahl NACH der Epoche — `7:5.1.6-0+deb12u1` → 5. (F-3)

    Ohne das konnte ein `systempaket` **nie** MAJOR werden: Die Art liegt in
    `_VERGLEICH_UNGLEICH`, und dort galt `major` pauschal als `False`. Ein
    Debian-Sprung über eine Hauptversion sah damit aus wie ein
    Wartungs-Update — also genau der Fall, den man sich ansehen sollte, im
    Gewand des Falls, den man durchwinkt.
    """
    kern = (v or "").split(":", 1)[-1]
    treffer = re.match(r"\s*(\d+)", kern)
    return int(treffer.group(1)) if treffer else None


def _cmp(cur: str, latest: str, kind: str = "") -> tuple[bool, bool]:
    """(update_verfügbar, ist_major). Major = erste Zahlgruppe unterscheidet sich."""
    if kind in _VERGLEICH_UNGLEICH:
        anders = bool(cur) and bool(latest) and cur != latest
        if not anders or kind != "systempaket":
            # Fingerabdrücke haben keine Hauptversion — dort bleibt es bei False.
            return (anders, False)
        a, b = _debian_hauptversion(cur), _debian_hauptversion(latest)
        return (True, bool(a is not None and b is not None and a != b))
    c, l = _vtuple(cur), _vtuple(latest)
    if not c or not l:
        return (False, False)
    newer = l > c
    major = newer and (l[0] != c[0])
    return (newer, major)


def _rueckwaerts(cur: str, latest: str, kind: str = "") -> bool:
    """Ist das INSTALLIERTE neuer als das angebotene? (F-3)

    **Beide bisherigen Wege waren falsch, jeder auf seine Art.** Bei den
    vergleichbaren Arten fiel dieser Fall stumm in den `else`-Zweig und wurde
    als „aktuell" protokolliert — obwohl er bedeutet, dass die Quelle etwas
    Älteres anbietet als das, was läuft (eine zurückgezogene Fassung, ein
    gewechselter Kanal, ein bevorstehendes Downgrade). Bei den Ungleich-Arten
    wurde er als **Update** gemeldet, mit Pfeil: `1.5 → 1.2`.

    Er ist keins von beidem, sondern eine eigene Auskunft — und eine, die
    jemand sehen sollte.
    """
    if kind in _VERGLEICH_UNGLEICH:
        return False           # Fingerabdrücke haben keine Reihenfolge
    c, l = _vtuple(cur), _vtuple(latest)
    return bool(c and l and c > l)


# --- Versions-Ermittlung je Kind --------------------------------------------
def cur_pip(comp: dict) -> str:
    pip = Path(comp["venv"]) / "bin" / "pip"
    out = _run([str(pip), "show", comp["ref"]])
    m = re.search(r"^Version:\s*(.+)$", out, re.MULTILINE)
    return m.group(1).strip() if m else ""


def latest_pip(comp: dict) -> str:
    d = _get_json(f"https://pypi.org/pypi/{urllib.parse.quote(comp['ref'])}/json")
    return (d or {}).get("info", {}).get("version", "") if d else ""


def cur_npm(comp: dict) -> str:
    out = _run(["npm", "ls", "-g", comp["ref"], "--depth=0"])
    m = re.search(re.escape(comp["ref"]) + r"@([0-9][^\s]*)", out)
    return m.group(1) if m else ""


def latest_npm(comp: dict) -> str:
    quoted = comp["ref"].replace("/", "%2F")
    d = _get_json(f"https://registry.npmjs.org/{quoted}")
    return (d or {}).get("dist-tags", {}).get("latest", "") if d else ""


def cur_node(_comp: dict) -> str:
    return _run(["node", "--version"]).strip()


def latest_node(_comp: dict) -> str:
    d = _get_json("https://nodejs.org/dist/index.json")
    if not isinstance(d, list):
        return ""
    for rel in d:  # neueste zuerst; erste LTS ist die aktuelle LTS-Linie
        if rel.get("lts"):
            return rel.get("version", "")
    return d[0].get("version", "") if d else ""


# --- Systempakete (apt) ------------------------------------------------------
# Beides lokal und kostenfrei. Der Vergleich ist hier NICHT „installiert gegen
# neueste der Welt", sondern „installiert gegen das, was die Paketverwaltung
# anbietet" — die Debian-Antwort ist die einzige, die auf dieser Maschine
# überhaupt erreichbar ist. Eine Meldung „ffmpeg 8.0 ist draußen" wäre nutzlos,
# solange Debian bei 7.1 steht.
def _apt_policy(ref: str, feld: str) -> str:
    # **Beide Werte aus DERSELBEN Auskunft.** Naheliegend wäre `dpkg-query` für
    # das Installierte gewesen — aber dessen Format-Zeichenkette enthält
    # `${Version}`, und beim Messen über eine Fernsitzung hat die Shell genau
    # das zu einer leeren Zeichenkette gemacht. Der Wert sah dann aus wie
    # „nicht installiert". Im Python-Aufruf wäre das nicht passiert (dort geht
    # kein Shell dazwischen), aber eine Quelle, die je nach Aufrufweg etwas
    # anderes sagt, ist eine schlechte Quelle.
    out = _run(["apt-cache", "policy", ref])
    m = re.search(rf"^\s*{feld}:\s*(\S+)", out, re.MULTILINE)
    v = m.group(1).strip() if m else ""
    return "" if v in ("(none)", "") else v


def cur_apt(comp: dict) -> str:
    return _apt_policy(comp["ref"], "Installed")


def latest_apt(comp: dict) -> str:
    return _apt_policy(comp["ref"], "Candidate")


# --- Docker-Abbilder ---------------------------------------------------------
# **Hier wird bewusst NICHT nach Versionsnummern gesucht.** LobeChat läuft auf
# `:latest` — dort ändert sich der Inhalt, ohne dass sich der Name ändert. Ein
# Namensvergleich meldete also nie etwas, während das Abbild monatelang
# veraltet. Verglichen wird der Fingerabdruck: der, den die Registry heute für
# `:latest` ausliefert, gegen den des LOKAL vorhandenen Abbilds. (Nicht gegen
# den laufenden Container — das behauptete diese Zeile bis zum 19.08., siehe
# `cur_docker`.)
_DOCKER_ACCEPT = ",".join([
    "application/vnd.oci.image.index.v1+json",
    "application/vnd.docker.distribution.manifest.list.v2+json",
    "application/vnd.oci.image.manifest.v1+json",
    "application/vnd.docker.distribution.manifest.v2+json",
])


def _docker_teile(ref: str) -> tuple[str, str]:
    name, _, tag = ref.partition(":")
    if "/" not in name:          # „redis" ist in Wahrheit „library/redis"
        name = "library/" + name
    return name, (tag or "latest")


def cur_docker(comp: dict) -> str:
    """Fingerabdruck des lokal vorhandenen **Abbilds**.

    **Bekannter Rand, bewusst offen (F-3, Gegenprüfung 18.08.):** Der Kommentar
    oben behauptete, verglichen werde der Fingerabdruck, „aus dem der laufende
    Container stammt". Das stimmt nicht — hier wird das lokale Abbild
    inspiziert. Ein gezogenes, aber nie gestartetes Abbild meldet damit
    „aktuell", während der Dienst weiter auf dem alten läuft.

    **Warum es trotzdem so bleibt:** Der Weg über den laufenden Container
    braucht Docker-Zugriff, den der Bot nicht hat (`claudebot` ist nicht in der
    Docker-Gruppe, gemessen 28.07.) — die Prüfung liefe also ungetestet in
    einer Umgebung, die ich nicht nachstellen kann. Der einzige betroffene
    Eintrag ist LobeChat, das nicht öffentlich läuft. Der Kommentar ist
    richtiggestellt; die Behauptung war der eigentliche Schaden.
    """
    out = _run(["docker", "image", "inspect", comp["ref"],
                "--format", "{{index .RepoDigests 0}}"])
    _, _, digest = out.strip().partition("@")
    return digest


def latest_docker(comp: dict) -> str:
    name, tag = _docker_teile(comp["ref"])
    # Anonymes Lese-Token — kein Konto, keine Kosten, kein Abbild-Download:
    # geholt wird nur der Kopf des Manifests, nicht das Abbild selbst.
    tok = _get_json("https://auth.docker.io/token?service=registry.docker.io"
                    f"&scope=repository:{name}:pull")
    token = (tok or {}).get("token")
    if not token:
        return ""
    try:
        req = urllib.request.Request(
            f"https://registry-1.docker.io/v2/{name}/manifests/{tag}",
            headers={"Authorization": "Bearer " + token,
                     "Accept": _DOCKER_ACCEPT,
                     "User-Agent": "momo-version-monitor"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as r:
            return r.headers.get("Docker-Content-Digest", "")
    except Exception:
        return ""


# --- GitHub-Veröffentlichungen ----------------------------------------------
# Für Eigenbauten (git-Klon), die keine Paketverwaltung kennt. Anonym: 60
# Anfragen je Stunde — bei einem wöchentlichen Lauf reichlich.
def cur_github(comp: dict) -> str:
    befehl = comp.get("current_cmd")
    if not befehl:
        return ""
    out = _run(["sh", "-c", befehl])
    return out.strip().splitlines()[0].strip() if out.strip() else ""


def latest_github(comp: dict) -> str:
    d = _get_json(f"https://api.github.com/repos/{comp['repo']}/releases/latest")
    return (d or {}).get("tag_name", "") if d else ""


HANDLERS = {
    "pip": (cur_pip, latest_pip),
    "npm_global": (cur_npm, latest_npm),
    "node": (cur_node, latest_node),
    "systempaket": (cur_apt, latest_apt),
    "docker": (cur_docker, latest_docker),
    "github_release": (cur_github, latest_github),
}


def _send_telegram(text: str) -> None:
    env = {}
    try:
        for line in Path(ENVFILE).read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip()
    except Exception:
        return
    token = env.get("TELEGRAM_BOT_TOKEN")
    uids = [u.strip() for u in (env.get("ALLOWED_USER_IDS") or "").split(",") if u.strip()]
    if not token or not uids:
        return
    for uid in uids:
        data = urllib.parse.urlencode({"chat_id": uid, "text": text}).encode()
        try:
            urllib.request.urlopen(
                f"https://api.telegram.org/bot{token}/sendMessage", data=data,
                timeout=HTTP_TIMEOUT)
        except Exception:
            pass


SEENFILE = Path(os.environ.get("VERSION_MONITOR_SEEN")
                or (ROOT / "logs" / "version-monitor-gesehen.json"))
INTERVALL_STD_TAGE = 90


def _kurz(v: str) -> str:
    """Ein Fingerabdruck ist 71 Zeichen lang und in einer Telegram-Meldung
    unlesbar. Wer ihn wirklich braucht, findet ihn im Protokoll — dort steht
    er ungekürzt."""
    return v[:19] + "…" if v.startswith("sha256:") else v


def _gesehen_laden() -> tuple[dict, str | None]:
    """(Sichtungen, Befund-Text oder None).

    **F-3: Fehlt die Datei, ist das der Normalfall — ist sie kaputt, nicht.**
    Vorher fielen beide Fälle in dasselbe stille `{}`, und damit setzte eine
    beschädigte Datei **alle Fristen zurück**, ohne dass es jemand erfuhr. Der
    nächste Lauf begann bei null und meldete monatelang nichts. Genau die
    Signatur, die dieses Projekt am häufigsten trifft: ein Ausbleiben, das wie
    Ruhe aussieht.
    """
    if not SEENFILE.exists():
        return ({}, None)                  # erster Lauf, kein Befund
    try:
        daten = json.loads(SEENFILE.read_text())
        if not isinstance(daten, dict):
            raise ValueError("kein Objekt")
        return (daten, None)
    except Exception as e:
        return ({}, f"⚠️ Sichtungs-Gedächtnis unlesbar ({type(e).__name__}) — "
                    "alle Fälligkeiten beginnen neu. Die Datei wird beim "
                    "nächsten Schreiben ersetzt.")


def _faellig(name: str, comp: dict, gesehen: dict) -> tuple[bool, int]:
    """(ist_faellig, Tage seit der letzten Sichtung).

    Beim ALLERERSTEN Lauf ist nichts faellig - sonst kaeme die ganze Liste auf
    einen Schlag, und eine Meldung, die zwoelf Punkte gleichzeitig nennt, wird
    einmal ueberflogen und nie wieder. Stattdessen wird der Startpunkt gesetzt
    und ab da gezaehlt. (Derselbe Grund, aus dem die Zeitgeber-Wache nicht das
    Alter des letzten Laufs misst: Ein Pruefer, der beim ersten Mal anschlaegt,
    erzieht dazu, ihn zu ueberlesen.)

    **F-3: Ein unlesbarer Zeitstempel galt als „gerade eben gesehen".** Er
    fiel in denselben Rückgabewert wie der erste Lauf — der Eintrag war damit
    **dauerhaft** nicht fällig, und das Protokoll meldete „vor 0 Tagen
    gesehen". Das war keine Lücke, sondern eine aktive Falschauskunft: Sie
    behauptete eine Prüfung, die nie stattgefunden hatte. Jetzt ist er fällig
    und wird als solcher benannt (`seit == -1`).
    """
    tage_soll = int(comp.get("intervall_tage") or INTERVALL_STD_TAGE)
    eintrag = gesehen.get(name)
    if not eintrag:
        return (False, 0)
    try:
        seit = (datetime.now() - datetime.fromisoformat(eintrag)).days
    except Exception:
        return (True, -1)      # unlesbar → fällig, und der Grund wird genannt
    return (seit >= tage_soll, max(seit, 0))


def main() -> int:
    reg = json.loads(REGISTER.read_text())
    updates: list[str] = []   # meldepflichtig
    manual: list[str] = []    # nur Reminder
    blind: list[str] = []     # Befund A/D: was der Monitor NICHT prueft
    loglines: list[str] = []
    gesehen, gedaechtnis_befund = _gesehen_laden()
    if gedaechtnis_befund:
        blind.append(gedaechtnis_befund)
        loglines.append("? Sichtungs-Gedaechtnis unlesbar (GEMELDET)")
    faellig_neu: list[str] = []
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for nr, comp in enumerate(reg.get("components", []), start=1):
        # **F-3: Ein unvollständiger Eintrag tötete den ganzen Lauf.** Fehlte
        # `name` oder `kind`, brach `main()` mit einem KeyError ab — VOR
        # Protokoll und VOR Versand. Ein einziger Tippfehler im Register legte
        # damit den gesamten Monitor still, und zwar lautlos: Wer ihn per
        # Zeitgeber laufen lässt, sieht nur, dass keine Meldung kommt.
        # Jetzt scheitert höchstens der eine Eintrag, und er sagt es.
        name, kind = comp.get("name"), comp.get("kind")
        if not name or not kind:
            blind.append(f"⚠️ Register-Eintrag Nr. {nr} ist unvollständig "
                         f"(name={name or '?'}, kind={kind or '?'}) — er wird "
                         "übersprungen und NICHT geprüft")
            loglines.append(f"? Eintrag {nr}: unvollstaendig (GEMELDET)")
            continue
        if kind == "manual":
            # **Der stille Teil des Registers — und der Grund für diesen Umbau.**
            #
            # Manuelle Einträge hingen bisher als Anhängsel an einer Meldung,
            # die es nur gab, wenn ANDERSWO ein Update gefunden wurde. Läuft
            # alles rund, meldet der Monitor nichts — und dann meldet er auch
            # die manuellen Punkte nicht. Ausgerechnet die, die niemand sonst
            # prüft, waren an die Existenz eines fremden Fundes gekoppelt.
            #
            # Das trifft genau die zwei Einträge, bei denen es am meisten
            # wehtut: `claude-modelle` und `verfahren-medien`. Beide lassen sich
            # nicht automatisch ermitteln (die CLI führt keinen Katalog, und ob
            # es ein besseres Video-Verfahren gibt, ist ein Urteil, keine
            # Abfrage). Statt dafür eine Attrappe zu bauen, bekommen sie eine
            # FÄLLIGKEIT: Nach `intervall_tage` melden sie sich von selbst.
            faellig, seit = _faellig(name, comp, gesehen)
            if faellig:
                # `seit == -1` heißt: der Zeitstempel war unlesbar. Das als
                # „seit -1 Tagen nicht geprüft" zu melden wäre die nächste
                # Falschauskunft — also wird gesagt, was tatsächlich vorliegt.
                wann = ("mit unlesbarem Datum hinterlegt — wann zuletzt "
                        "geprüft wurde, ist unbekannt" if seit < 0
                        else f"seit {seit} Tagen nicht geprüft")
                updates.append(f"🔎 {name}: {wann} — {comp.get('note', '')}")
                loglines.append(f"FAELLIG {name}: "
                                + ("Datum unlesbar" if seit < 0 else f"{seit} Tage"))
                faellig_neu.append(name)
            else:
                manual.append(f"• {name}: manuell prüfen — {comp.get('note', '')}")
                loglines.append(f"~ {name}: manual (vor {seit} Tagen gesehen)")
            continue
        handler = HANDLERS.get(kind)
        if not handler:
            # **Befund A (Vorlage 5.21-E): eine Art, die niemand prüft.**
            #
            # Bis hierher landete das nur im Protokoll — und ein Protokoll, das
            # niemand liest, ist kein Prüfer. Wer eine Komponente mit einer
            # unbekannten Art einträgt, bekam **stille Nichtprüfung**: Der
            # Eintrag stand im Register, sah nach Abdeckung aus, und wurde nie
            # angesehen. Genau die Signatur, die dieses Projekt am häufigsten
            # trifft — ein Ausbleiben, das wie Ruhe aussieht.
            #
            # Das Register selbst nennt heute `github_release`, für das es
            # keinen Handler gibt. Der Fall ist also nicht theoretisch.
            blind.append(f"⚠️ {name}: Art `{kind}` kennt der Monitor nicht — "
                         "dieser Eintrag wird seit jeher NICHT geprüft")
            loglines.append(f"? {name}: unbekannter kind {kind} (GEMELDET)")
            continue
        cur = handler[0](comp)
        latest = handler[1](comp)
        if not cur or not latest:
            # **Befund D, dieselbe Klasse:** Eine weggebrochene Quelle stand
            # bisher stumm im Protokoll. „Es gibt nichts Neues" und „ich komme
            # nicht mehr an die Auskunft" sehen von außen gleich aus — und nur
            # das zweite ist ein Problem.
            blind.append(f"⚠️ {name}: Quelle nicht erreichbar "
                         f"(installiert={cur or '?'}, verfügbar={latest or '?'})")
            loglines.append(f"? {name}: cur={cur or '?'} latest={latest or '?'} (Quelle n/a, GEMELDET)")
            continue
        newer, major = _cmp(cur, latest, kind)
        if _rueckwaerts(cur, latest, kind):
            # F-3: Weder Update noch „aktuell" — eine eigene Auskunft.
            blind.append(f"⚠️ {name}: installiert ist **neuer** als angeboten "
                         f"({_kurz(cur)} vs. {_kurz(latest)}) — die Quelle "
                         "führt etwas Älteres, das ist einen Blick wert")
            loglines.append(f"RUECKWAERTS {name}: {cur} > {latest} (GEMELDET)")
        elif newer:
            tag = "🔴 MAJOR" if major else "🟡"
            pin = " (gepinnt — bewusst, Wartungsfenster)" if comp.get("pinned") else ""
            # Bei den Ungleich-Arten ist der Pfeil eine Behauptung über
            # Reihenfolge, die es dort nicht gibt (F-3) — also „weicht ab".
            wie = (f"{_kurz(cur)} weicht ab von {_kurz(latest)}"
                   if kind in _VERGLEICH_UNGLEICH
                   else f"{_kurz(cur)} → {_kurz(latest)}")
            updates.append(f"{tag} {name}: {wie}{pin}")
            loglines.append(f"UPDATE {name}: {cur} -> {latest}{' MAJOR' if major else ''}")
        else:
            loglines.append(f"ok {name}: {cur} (aktuell)")

    # Sichtungs-Gedächtnis fortschreiben.
    #
    # **Zwei Fälle, absichtlich verschieden behandelt.** Ein Eintrag, der zum
    # ersten Mal gesehen wird, bekommt schlicht sein Startdatum. Ein Eintrag,
    # der gerade als fällig GEMELDET wurde, bekommt das Datum ebenfalls neu —
    # sonst stünde er in jedem folgenden Lauf wieder drin, und aus der
    # Erinnerung würde binnen dreier Wochen ein Dauerton, den niemand mehr
    # liest. Die Meldung ist damit ein Anstoß, keine Mahnung: Sie kommt einmal,
    # und dann erst wieder nach der nächsten Frist.
    #
    # Das ist bewusst schwächer, als es sein könnte — ein „erledigt"-Knopf
    # wäre genauer. Der wäre aber ein zweiter Weg für einen Zustand, und die
    # kosten hier erfahrungsgemäß mehr, als sie einbringen.
    jetzt_iso = datetime.now().isoformat(timespec="seconds")
    for comp in reg.get("components", []):
        # F-3: dieselbe Falle wie oben — die zweite Schleife läuft NACH dem
        # Sammeln, aber VOR Protokoll und Versand. Ein KeyError hier hätte
        # dieselbe Wirkung gehabt: kein Protokoll, keine Meldung.
        if comp.get("kind") != "manual" or not comp.get("name"):
            continue
        if comp["name"] not in gesehen or comp["name"] in faellig_neu:
            gesehen[comp["name"]] = jetzt_iso
    try:
        SEENFILE.parent.mkdir(parents=True, exist_ok=True)
        SEENFILE.write_text(json.dumps(gesehen, indent=2, ensure_ascii=False),
                            encoding="utf-8")
    except Exception:
        pass

    # Protokoll immer
    try:
        LOGFILE.parent.mkdir(parents=True, exist_ok=True)
        with LOGFILE.open("a", encoding="utf-8") as fh:
            fh.write(f"===== Versions-Monitor {stamp} =====\n")
            fh.write("\n".join(loglines) + "\n")
    except Exception:
        pass

    # Meldung nur bei echten Updates (Manual-Reminder hängen wir an, wenn es
    # ohnehin eine Meldung gibt — sonst kein wöchentliches Rauschen).
    if updates or blind:
        teile = []
        if updates:
            teile.append("📦 Update-Monitor (5.21) — verfügbare Versionen:\n"
                         + "\n".join(updates)
                         + "\n\nInstallation bleibt manuell (E3). "
                           "🔴 = Major-Sprung, bewusst prüfen.")
        if blind:
            # **Ein blinder Fleck ist meldepflichtig, auch wenn es sonst nichts
            # gibt.** Andernfalls hätte ich denselben Fehler zweimal gebaut:
            # Ein Befund, der nur ins Protokoll wandert, ist keiner.
            teile.append("🕳️ Blinde Flecken im Register — hier prüft der "
                         "Monitor NICHT:\n" + "\n".join(blind)
                         + "\n\nDas ist kein Update-Hinweis, sondern die "
                           "Auskunft, dass diese Einträge ungeprüft dastehen.")
        if manual:
            teile.append("Manuell im Blick behalten:\n" + "\n".join(manual))
        _send_telegram("\n\n".join(teile))
        print(f"{len(updates)} Update(s), {len(blind)} blinde(r) Fleck(en) gemeldet.")
    else:
        print("Keine Updates, keine blinden Flecken — keine Meldung.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
