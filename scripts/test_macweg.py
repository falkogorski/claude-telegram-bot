#!/usr/bin/env python3
# <!-- ROLLE: test-macweg -->
"""Block 7, erster Schnitt: der Weg VPS → Mac → VPS — **ausgeführt** (26.09.2026).

`[NEU GEFASST 26.09.2026, nach der Widerlegungsprüfung]` Die erste Fassung
bildete rrsync mit einer eigenen Attrappe nach; zwei ihrer Zeilen blieben grün,
obwohl der Schutz entfernt war (P1, P2), und Unterordner, Links und die
Zerlegung von `-e` waren strukturell unsichtbar (P4). Jetzt:

  • Der Rand ist das **echte `rrsync`** (vom Server oder aus Homebrew) hinter
    einer ssh-Attrappe. Die Attrappe sucht den Schlüssel in der
    `authorized_keys`, die das **echte Einrichtungs-Skript** in einen
    Wegwerf-Server geschrieben hat, und startet rrsync mit genau den Angaben
    dieser Zeile. Gemessen wird also die Zeile, die später auf dem Server steht.
  • Die Attrappe weist jeden engen Aufruf ab, der mehr als den eigenen
    Schlüssel anbieten könnte (zweites `-F`, `-i`, Agent).
  • Das Einrichtungs-Skript läuft **wirklich** — mit Abbruchfällen, in denen
    `launchctl` nicht gerufen werden darf.

Fehlt rsync 3 oder rrsync auf dem Rechner, endet der Prüfer mit 77
(übersprungen, nicht bestanden).
"""
import fcntl
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))


def _im_pfad(name: str) -> list[str]:
    """Alle Fundstellen im PATH — ohne feste, maschinengebundene Pfade."""
    return [str(Path(d) / name) for d in os.environ.get("PATH", "").split(os.pathsep)
            if d and (Path(d) / name).is_file()]


def _rsync3() -> str | None:
    # macOS fuehrt openrsync unter demselben Namen; gesucht ist rsync 3.
    for kandidat in _im_pfad("rsync"):
        try:
            v = subprocess.run([kandidat, "--version"], capture_output=True, text=True).stdout
        except OSError:
            continue
        if v.startswith("rsync  version 3"):
            return kandidat
    return None


RSYNC3 = _rsync3()
RRSYNC = (_im_pfad("rrsync") or [None])[0]
if not RSYNC3 or not RRSYNC or not shutil.which("ssh-keygen"):
    print(f"übersprungen: rsync 3 [{RSYNC3}], rrsync [{RRSYNC}] oder ssh-keygen fehlt")
    sys.exit(77)

_TMP = Path(tempfile.mkdtemp(prefix="macweg-"))
SRV = _TMP / "srv"                 # Heimverzeichnis des Wegwerf-Servers
MAC = _TMP / "mac"                 # Heimverzeichnis des Wegwerf-Macs
BIN = _TMP / "bin"
AUFTRAEGE, ERGEBNISSE = SRV / "mac-auftraege", SRV / "mac-ergebnisse"
os.environ["MAC_AUFTRAEGE"] = str(AUFTRAEGE)
os.environ["MAC_ERGEBNISSE"] = str(ERGEBNISSE)
import macauftrag                                               # noqa: E402

fehler: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


# ── Der Rand ────────────────────────────────────────────────────────────────
BIN.mkdir(parents=True)
# Echtes rrsync, nur der rsync-Pfad zeigt auf rsync 3 (Homebrews rrsync ruft
# sonst das macOS-openrsync).
import re as _re                                                # noqa: E402
_rr = _re.sub(r"^RSYNC = .*$", f"RSYNC = {RSYNC3!r}", Path(RRSYNC).read_text(), count=1,
              flags=_re.M)
(BIN / "rrsync").write_text(_rr)
(BIN / "ssh").write_text(f"""#!{sys.executable}
import os, re, subprocess, sys
from pathlib import Path
SRV = Path({str(SRV)!r}); BIN = Path({str(BIN)!r})
a = sys.argv[1:]
with open(BIN / "ssh.log", "a") as f:
    f.write(repr(a) + "\\n")
if a[:1] == ["-G"]:
    print("user claudebot\\nhostname pruefserver\\nport 22\\n"
          "userknownhostsfile ~/.ssh/known_hosts ~/.ssh/known_hosts2\\nidentityfile ~/.ssh/id_ed25519")
    sys.exit(0)
F, ids, agent, i = [], [], None, 0
while i < len(a) and a[i].startswith("-"):
    if a[i] in ("-F", "-o", "-p", "-i", "-l"):
        wert = a[i + 1]
        if a[i] == "-F": F.append(wert)
        if a[i] == "-i": ids.append(wert)
        if a[i] == "-o":
            k, _, v = wert.partition("=")
            if k.lower() == "identityfile": ids.append(v)
            if k.lower() == "identityagent": agent = v
        i += 2
    else:
        i += 1
host, befehl = a[i], " ".join(a[i + 1:])
umg = dict(os.environ, HOME=str(SRV), MAC_AUFTRAEGE=str(SRV / "mac-auftraege"),
           MAC_ERGEBNISSE=str(SRV / "mac-ergebnisse"))
if host == "claudebot":                  # der volle Zugang — nur die Einrichtung
    if befehl.startswith("test -f"):
        sys.exit(0)
    if "macauftrag.py --probe" in befehl and os.environ.get("SIM_PROBE_ART"):
        k = subprocess.run([sys.executable, "-c", "import macauftrag;print(macauftrag.neue_kennung())"],
                           capture_output=True, text=True, env=umg, cwd={str(WURZEL)!r}).stdout.strip()
        (SRV / "mac-auftraege").mkdir(parents=True, exist_ok=True)
        (SRV / "mac-auftraege" / f"{{k}}.json").write_text(
            '{{"kennung": "%s", "art": "%s"}}' % (k, os.environ["SIM_PROBE_ART"]))
        print(k); sys.exit(0)
    if "macauftrag.py" in befehl:
        sys.exit(subprocess.run([sys.executable, {str(WURZEL / "macauftrag.py")!r},
                                 befehl.split()[-1]], env=umg).returncode)
    sys.exit(subprocess.run(["bash", "-c", befehl], env=umg).returncode)
# Der enge Weg: genau EIN Schluessel, kein Agent, keine fremde Konfiguration.
if F != ["/dev/null"] or len(ids) != 1 or (agent or "").lower() != "none":
    print(f"voller Schluessel angeboten: F={{F}} ids={{ids}} agent={{agent}}", file=sys.stderr)
    sys.exit(99)
key = Path(ids[0])
if not key.is_file() or os.environ.get("SIM_OHNE_EINTRAG"):
    print("Permission denied (publickey).", file=sys.stderr); sys.exit(255)
pub = Path(str(key) + ".pub").read_text().split()[1]
ak = SRV / ".ssh" / "authorized_keys"
for z in (ak.read_text().splitlines() if ak.is_file() else []):
    teile = z.split()
    if len(teile) >= 3 and teile[-2] == pub:
        m = re.match(r'restrict,command="([^"]+)" ', z)
        if not m: break
        cmd = m.group(1).split()
        if os.environ.get("SIM_RICHTUNG_FALSCH"):
            cmd = [{{"-ro": "-wo", "-wo": "-ro"}}.get(x, x) for x in cmd]
        zaehler = BIN / "bringen.zaehler"
        if "-wo" in cmd and os.environ.get("SIM_BRINGEN_FEHLER"):
            n = int(zaehler.read_text() or 0) + 1 if zaehler.exists() else 1
            zaehler.write_text(str(n))
            if str(n) == os.environ["SIM_BRINGEN_FEHLER"]:
                print("Verbindung abgerissen", file=sys.stderr); sys.exit(12)
        os.environ["SSH_ORIGINAL_COMMAND"] = befehl
        os.execv(sys.executable, [sys.executable, str(BIN / "rrsync")] + cmd[1:])
print("Permission denied (publickey).", file=sys.stderr); sys.exit(255)
""")
(BIN / "launchctl").write_text(f"#!/bin/bash\necho \"$@\" >> {BIN}/launchctl.log\n")
for b in ("ssh", "launchctl"):
    (BIN / b).chmod(0o755)
(BIN / "python3").symlink_to(sys.executable)

UMG = {**os.environ, "HOME": str(MAC), "PATH": f"{BIN}:{os.environ.get('PATH', '')}",
       "VIDEOARBEITER_RSYNC": RSYNC3, "VIDEOARBEITER_SSH": str(BIN / "ssh"),
       "VIDEOARBEITER_PY": sys.executable,
       "VIDEOARBEITER_PROTOKOLL": str(_TMP / "videoarbeiter.log")}
ORT = MAC / "Library" / "Application Support" / "videoarbeiter" / "videoarbeiter.py"


def neu_aufsetzen() -> None:
    for d in (SRV, MAC):
        shutil.rmtree(d, ignore_errors=True)
        d.mkdir(parents=True)
    for f in ("launchctl.log", "ssh.log", "bringen.zaehler"):
        (BIN / f).unlink(missing_ok=True)


def einrichten(**sim) -> tuple[int, str]:
    r = subprocess.run(["bash", str(WURZEL / "scripts" / "mac" / "videoarbeiter_einrichten.sh")],
                       capture_output=True, text=True, env={**UMG, **sim}, timeout=300)
    return r.returncode, r.stdout + r.stderr


def mac_lauf(**sim) -> tuple[int, str]:
    r = subprocess.run([sys.executable, str(WURZEL / "scripts" / "mac" / "videoarbeiter.py")],
                       capture_output=True, text=True, env={**UMG, **sim}, timeout=120)
    return r.returncode, r.stdout + r.stderr


def scharf() -> bool:
    log = BIN / "launchctl.log"
    return log.exists() and "bootstrap" in log.read_text()


def ak() -> list[str]:
    p = SRV / ".ssh" / "authorized_keys"
    return p.read_text().splitlines() if p.is_file() else []


# ── 1. Die Einrichtung, echt ────────────────────────────────────────────────
print("== 1. Einrichtung (echtes Skript, Wegwerf-Server, echtes rrsync) ==")
neu_aufsetzen()
rc, aus = einrichten()
zeile("Einrichtung laeuft durch und stellt scharf", rc == 0 and scharf(), gemessen=aus[-300:])
eintraege = [z for z in ak() if "rrsync" in z]
zeile("zwei Eintraege: Holen nur lesend, Bringen nur schreibend mit -munge, beide restrict",
      len(eintraege) == 2
      and any(f'restrict,command="/usr/bin/rrsync -ro {AUFTRAEGE}"' in z for z in eintraege)
      and any(f'restrict,command="/usr/bin/rrsync -munge -wo {ERGEBNISSE}"' in z for z in eintraege),
      gemessen=str(eintraege))
zeile("die Gegenproben liefen: ls ~, schreiben und lesen je abgelehnt",
      aus.count("von rrsync abgelehnt") == 2 and "schreiben abgelehnt" in aus
      and "lesen abgelehnt" in aus, gemessen=aus[-300:])
zeile("der Arbeiter liegt am festen Ort, nicht im Arbeitsbaum",
      ORT.is_file() and str(ORT) in (MAC / "Library" / "LaunchAgents" /
                                     "com.jakuna.videoarbeiter.plist").read_text())
rc2, aus2 = einrichten()
zeile("ein zweiter Aufruf legt nichts doppelt an",
      rc2 == 0 and len([z for z in ak() if "rrsync" in z]) == 2, gemessen=aus2[-200:])

# ── 2. Einrichtung: Abbruchfaelle, nie halb scharf ──────────────────────────
print("== 2. Einrichtung bricht ab, statt halb scharf zu werden ==")
for name, sim, erwartet in (
        ("Schluessel nicht eingetragen", {"SIM_OHNE_EINTRAG": "1"}, "scheiterte nicht an rrsync"),
        ("Richtung vertauscht", {"SIM_RICHTUNG_FALSCH": "1"}, "der Holschluessel darf schreiben"),
        ("Probe abgelehnt statt erledigt", {"SIM_PROBE_ART": "shell"}, "kam nicht erledigt zurueck")):
    neu_aufsetzen()
    rc, aus = einrichten(**sim)
    zeile(f"{name}: Abbruch, launchctl nie gerufen",
          rc != 0 and not scharf() and erwartet in aus, gemessen=f"rc={rc} {aus[-200:]!r}")

neu_aufsetzen()
(SRV / ".ssh").mkdir(parents=True)
(SRV / ".ssh" / "authorized_keys").write_text("ssh-ed25519 AAAAALTERSCHLUESSEL adam@mac")
rc, aus = einrichten()
zeile("authorized_keys ohne letzten Zeilenumbruch: alter Eintrag bleibt heil",
      rc == 0 and ak()[0] == "ssh-ed25519 AAAAALTERSCHLUESSEL adam@mac"
      and len([z for z in ak() if z.startswith("restrict,")]) == 2, gemessen=str(ak()))
_pubdatei = MAC / ".ssh" / "videoarbeiter_holen.pub"
pub = _pubdatei.read_text().strip() if _pubdatei.is_file() else "ssh-ed25519 FEHLT test"
(SRV / ".ssh").mkdir(parents=True, exist_ok=True)
(SRV / ".ssh" / "authorized_keys").write_text(f"{pub}\n")          # ohne Einschraenkung!
for f in ("launchctl.log",):
    (BIN / f).unlink(missing_ok=True)
rc, aus = einrichten()
zeile("derselbe Schluessel steht schon uneingeschraenkt: Abbruch, nichts veraendert",
      rc != 0 and not scharf() and ak() == [pub], gemessen=f"rc={rc} {ak()}")

# ── 3. Der Mac-Lauf gegen fremde Eintraege ──────────────────────────────────
print("== 3. Mac-Lauf: fremde und kaputte Einträge ==")
neu_aufsetzen()
rc, aus = einrichten()
k = macauftrag.ablegen("probe")
(AUFTRAEGE / f"{macauftrag.neue_kennung()}.json").mkdir()          # S1: ein Ordner
(AUFTRAEGE / "boese.json").write_text("{}")
(AUFTRAEGE / "notiz.txt").write_text("x")
(AUFTRAEGE / "sub" / "tief").mkdir(parents=True)
(AUFTRAEGE / "sub" / "tief" / "x.bin").write_bytes(b"x")
gross = macauftrag.neue_kennung()
(AUFTRAEGE / f"{gross}.json").write_text('{"x": "' + "a" * 70000 + '"}')
nl = "20260926T000002-cccccc\n"
(AUFTRAEGE / f"{nl}.json").write_text("{}")
(AUFTRAEGE / "20260926T000003-dddddd.json").symlink_to("/etc/hosts")
rc, aus = mac_lauf()
q = ERGEBNISSE / k / "fertig.json"
zeile("trotz Ordner, Link, fremder und kaputter Namen: die Probe kommt erledigt zurueck",
      rc == 0 and q.is_file() and json.loads(q.read_text()).get("art") == "probe",
      gemessen=f"rc={rc} {aus[-300:]!r}")
eingang = MAC / "VPS-Auftraege" / "eingang"
geholt = sorted(p.name for p in eingang.iterdir()) if eingang.is_dir() else []
# Gemessen am Protokoll des Laufs: Der Lauf raeumt Fremdes aus dem Eingang,
# ein Blick hinterher saehe also nie, was geholt wurde.
zeile("Unterordner, fremde Dateien und zu Grosses werden gar nicht erst geholt",
      not any(n in aus for n in ("notiz.txt", "'sub", "boese.json", gross))
      and not any(n in ("notiz.txt", "sub", f"{gross}.json") for n in geholt),
      gemessen=f"{geholt} {aus[-300:]!r}")
try:
    st = macauftrag.stand()
except Exception as e:  # ein Absturz macht die Zeile rot, nicht den Pruefer tot
    st = [("absturz", repr(e))]
arten = [a for a, _ in st]
zeile("der Server-Stand stuerzt nicht ab und meldet fremde Eintraege an die Kontrolle",
      "intern" in arten and any("zurueckgekommen, erledigt" in t for _, t in st)
      and all("\n" not in t for _, t in st), gemessen=str(st)[:400])
zeile("der Link wird nicht verfolgt und nicht geloescht",
      (AUFTRAEGE / "20260926T000003-dddddd.json").is_symlink() and Path("/etc/hosts").exists())
zeile("der zu grosse Auftrag heisst nicht faelschlich [ungeholt]",
      any(gross in t and "64 KB" in t for a, t in st if a == "intern"), gemessen=str(st)[:300])

# ── 4. Abbruch zwischen Ausfuehren und Bringen ──────────────────────────────
print("== 4. Abriss und Wiederholung ==")
neu_aufsetzen()
einrichten()
k = macauftrag.ablegen("probe")
(BIN / "bringen.zaehler").unlink(missing_ok=True)
rc1, aus1 = mac_lauf(SIM_BRINGEN_FEHLER="2")      # das Bringen nach dem Ausfuehren reisst
rc2, aus2 = mac_lauf()
zeile("nach einem Abriss wird nicht noch einmal ausgefuehrt, nur gebracht (S4)",
      rc1 != 0 and aus1.count("erledigt:") == 1 and "erledigt:" not in aus2
      and (ERGEBNISSE / k / "fertig.json").is_file(), gemessen=f"{aus1[-150:]!r} | {aus2[-150:]!r}")
rc3, aus3 = mac_lauf()
zeile("ein schon quittierter Auftrag wird nicht noch einmal ausgefuehrt",
      rc3 == 0 and "erledigt:" not in aus3, gemessen=aus3[-150:])
macauftrag.stand()
zeile("der Server raeumt den quittierten Auftrag weg (der Mac darf nicht)",
      not (AUFTRAEGE / f"{k}.json").exists())

# ── 5. Positivliste und Ablehnung ───────────────────────────────────────────
print("== 5. Positivliste ==")
fremd = macauftrag.neue_kennung()
(AUFTRAEGE / f"{fremd}.json").write_text(json.dumps(
    {"kennung": fremd, "art": "shell", "befehl": "touch " + str(_TMP / "AUSGEFUEHRT")}))
rc, aus = mac_lauf()
q = json.loads((ERGEBNISSE / fremd / "fertig.json").read_text()) \
    if (ERGEBNISSE / fremd / "fertig.json").is_file() else {}
zeile("unbekannte Art: abgelehnt und quittiert, nie ausgefuehrt",
      "Positivliste" in q.get("abgelehnt", "") and "rechner" not in q
      and not (_TMP / "AUSGEFUEHRT").exists(), gemessen=str(q))
st = macauftrag.stand()
zeile("eine Ablehnung kommt am Server als roter Befund an, nicht als Erfolg (S3)",
      any(a == "rot" and fremd in t and "abgelehnt" in t for a, t in st)
      and not any(fremd in t and "erledigt" in t for _, t in st), gemessen=str(st)[:300])

# ── 6. Nur der eigene Schluessel ────────────────────────────────────────────
print("== 6. Nur der eigene Schlüssel ==")
log = (BIN / "ssh.log").read_text()
eng = [z for z in log.splitlines() if "/dev/null" in z]
zeile("jeder enge Aufruf: ein -F /dev/null, genau ein IdentityFile, kein Agent",
      eng and all(z.count("'-F'") == 1 and z.count("IdentityFile=") == 1
                  and "IdentityAgent=none" in z and "'-i'" not in z for z in eng),
      gemessen=eng[-1][:300] if eng else "keine engen Aufrufe")
(MAC / ".ssh" / "videoarbeiter_bringen").rename(MAC / ".ssh" / "weg")
rc, aus = mac_lauf()
(MAC / ".ssh" / "weg").rename(MAC / ".ssh" / "videoarbeiter_bringen")
zeile("fehlt ein Schluessel: ehrlicher Abbruch, kein Aufruf mit anderem Schluessel",
      rc == 78 and "nicht eingerichtet" in aus, gemessen=f"rc={rc} {aus[-120:]!r}")

# ── 7. Ein Lauf zur Zeit ────────────────────────────────────────────────────
print("== 7. Sperre ==")
with open(MAC / "VPS-Auftraege" / ".sperre", "w") as sperre:
    fcntl.flock(sperre, fcntl.LOCK_EX)
    rc, aus = mac_lauf()
zeile("laeuft schon ein Lauf, endet der zweite ohne Eingriff",
      rc == 0 and "anderer Lauf" in aus, gemessen=f"rc={rc} {aus[-120:]!r}")

# ── 8. Wer merkt es (24 Stunden) ────────────────────────────────────────────
print("== 8. Wer merkt es (24 Stunden) ==")
neu_aufsetzen()
st = macauftrag.stand()
zeile("ohne Auftragsordner: nur eine Protokollzeile, kein Alarm",
      all(a == "ok" for a, _ in st) and "nicht eingerichtet" in st[0][1], gemessen=str(st))
alt = macauftrag.ablegen("probe")
jetzt = time.time()
os.utime(AUFTRAEGE / f"{alt}.json", (jetzt - 25 * 3600, jetzt - 25 * 3600))
rot = [t for a, t in macauftrag.stand(jetzt) if a == "rot"]
zeile("25 Stunden ungeholt: an Adam, mit dem letzten Lebenszeichen",
      len(rot) == 1 and "ungeholt" in rot[0] and "noch nie" in rot[0], gemessen=str(rot))
(ERGEBNISSE / alt).mkdir(parents=True)
(ERGEBNISSE / alt / "geholt.json").write_text("{}")
rot = [t for a, t in macauftrag.stand(jetzt) if a == "rot"]
zeile("geholt, aber 25 Stunden ohne Quittung: an Adam",
      len(rot) == 1 and "nicht zurueckgekommen" in rot[0], gemessen=str(rot))
zeile("Zeitform: Einzahl als Wort, Mehrzahl als Ziffer",
      macauftrag.menschlich(50) == "vor einer Minute" and macauftrag.menschlich(600) == "vor 10 Minuten",
      gemessen=f"{macauftrag.menschlich(50)!r} / {macauftrag.menschlich(600)!r}")
try:
    macauftrag.ablegen("shell")
    zeile("unbekannte Art wird gar nicht erst abgelegt", False)
except ValueError:
    zeile("unbekannte Art wird gar nicht erst abgelegt", True)

# ── 9. Tagescheck 9r ────────────────────────────────────────────────────────
print("== 9. Tagescheck 9r ==")
import re                                                       # noqa: E402
_dc = (WURZEL / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
_m = re.search(r"# >>> MACWEG\n(.*?)# <<< MACWEG", _dc, re.S)
_abschnitt = _m.group(1) if _m else ""


def _tagescheck(venvpy: str = sys.executable) -> str:
    vorspann = ('set -uo pipefail\n'
                'add() { echo "ADD:$1"; }\nintern() { echo "INTERN:$1"; }\n'
                'red() { echo "RED:$1"; }\nsudo() { shift 2; "$@"; }\n'
                f'BOTDIR="{WURZEL}"\nVENVPY="{venvpy}"\nBOTHOME="{SRV}"\n')
    return subprocess.run(["bash", "-c", vorspann + _abschnitt], capture_output=True,
                          text=True, env=dict(os.environ)).stdout


_a = _tagescheck()
zeile("Tagescheck 9r: haengender Auftrag geht rot an Adam",
      "RED:Mac-Auftrag" in _a and "nicht zurueckgekommen" in _a, gemessen=_a[-200:])
zeile("Tagescheck 9r: dazu die Protokollzeile mit dem Stand", "ADD:🖥️ Mac-Weg:" in _a)
(AUFTRAEGE / "fremd.txt").write_text("x")
_a = _tagescheck()
zeile("Tagescheck 9r: ein fremder Eintrag geht an die Kontrolle",
      "INTERN:fremder Eintrag" in _a, gemessen=_a[-200:])
(BIN / "kaputt").write_text("#!/bin/bash\necho Traceback >&2\nexit 1\n")
(BIN / "kaputt").chmod(0o755)
_a = _tagescheck(str(BIN / "kaputt"))
zeile("Tagescheck 9r: stuerzt die Pruefung ab, erfaehrt es die Kontrolle",
      "INTERN:Pruefung des Mac-Wegs lief nicht" in _a, gemessen=_a[-200:])
shutil.rmtree(AUFTRAEGE)
_a = _tagescheck()
zeile("Tagescheck 9r: nicht eingerichtet ist kein Alarm",
      "RED:" not in _a and "INTERN:" not in _a and "nicht eingerichtet" in _a, gemessen=_a)

shutil.rmtree(_TMP, ignore_errors=True)
print(f"== Ergebnis: {zeilen - len(fehler)}/{zeilen} ==")
sys.exit(1 if fehler else 0)
