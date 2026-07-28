#!/usr/bin/env python3
# <!-- ROLLE: test-stundenblumen -->
"""Verhaltenstest Stundenblumen — die dauerlaufende Belegkette.

Die Eigenschaft, an der alles hängt: **Das Ausbleiben der Übergabe ist der
Alarm.** Dazu die Gegenprobe, die genauso wichtig ist — in Ruhezeiten schweigt
die Kette, sonst glaubt ihr bald niemand mehr.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="blumen-"))
os.environ["BLUMEN_DIR"] = str(_TMP / "blumen")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["ALLOWED_USER_IDS"] = "304455165"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import stundenblume as sb  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _leeren():
    for p in (sb.KETTE, sb.RUHE, sb._GEDAECHTNIS):
        if p.exists():
            p.unlink()
    out = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if out.exists():
        for f in out.glob("*.json"):
            f.unlink()
    sb._befunde = lambda: []


def _meldungen():
    out = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if not out.exists():
        return []
    return [json.loads(f.read_text(encoding="utf-8"))["text"]
            for f in sorted(out.glob("*.json"))]


# Ein Zeitpunkt außerhalb der Ruhestunde, damit die Tageszeit nichts verfälscht.
def _t(versatz=0.0):
    basis = time.mktime(time.struct_time(
        (2026, 7, 25, 14, 0, 0, 4, 206, -1)))
    return basis + versatz


def _kette_waechst_verkettet():
    _leeren()
    a = sb.bluehen(_t(0))
    b = sb.bluehen(_t(60))
    assert a["vorher"] == "—", "die erste Blume zeigt auf etwas"
    assert b["vorher"] == a["abdruck"], "die Kette ist nicht verkettet"
    assert b["abdruck"] != a["abdruck"], "zwei Glieder mit gleichem Abdruck"
    e = sb.kette_pruefen(_t(120))
    assert e["ok"] and e["brueche"] == 0, f"frische Kette gilt als kaputt: {e}"


def _luecke_ist_der_alarm():
    """Der Kern: Nicht der Befund meldet sich, sondern die Lücke."""
    _leeren()
    sb.bluehen(_t(0))
    sb.bluehen(_t(sb.TOLERANZ_S + 600))     # zehn Minuten zu spät
    m = _meldungen()
    assert m, "die Lücke hat keinen Alarm ausgelöst"
    assert "Lücke" in m[0] and "niemand belegt" in m[0], \
        f"die Meldung benennt die Lücke nicht: {m[0]}"


def _kurze_luecke_schweigt():
    _leeren()
    sb.bluehen(_t(0))
    sb.bluehen(_t(sb.TOLERANZ_S - 30))
    assert not _meldungen(), "eine Lücke innerhalb der Toleranz hat gemeldet"


def _ruhe_schweigt():
    """Ein Wächter, dem niemand mehr glaubt, ist schlimmer als keiner."""
    _leeren()
    sb.bluehen(_t(0))
    sb.ruhe_setzen(30)
    e = sb.bluehen(_t(sb.TOLERANZ_S + 900))
    assert e["ruhe"], "die Ruhe wurde nicht erkannt"
    assert not _meldungen(), "in der Ruhezeit wurde Alarm geschlagen"


def _nachtfenster_schweigt():
    _leeren()
    nachts = time.mktime(time.struct_time((2026, 7, 25, 4, 10, 0, 4, 206, -1)))
    sb.bluehen(nachts - 3600)
    e = sb.bluehen(nachts)
    assert e["ruhe"] == "nächtliches Wartungsfenster", \
        f"das Hygiene-Fenster gilt nicht als Ruhe: {e['ruhe']!r}"
    assert not _meldungen(), "im Wartungsfenster wurde Alarm geschlagen"


def _stillstand_faellt_auf():
    """Steht die Kette, sagt die Prüfung es — auch ohne neue Blume."""
    _leeren()
    sb.bluehen(_t(0))
    e = sb.kette_pruefen(_t(sb.TOLERANZ_S + 1200))
    assert not e["ok"], "eine stillstehende Kette gilt als in Ordnung"
    assert "steht still" in e["grund"], f"Grund unklar: {e['grund']}"


def _manipulation_wird_sichtbar():
    """Manipulations-SICHTBAR, nicht -sicher — genau das wird geprüft."""
    _leeren()
    sb.bluehen(_t(0))
    sb.bluehen(_t(60))
    sb.bluehen(_t(120))
    zeilen = sb.KETTE.read_text(encoding="utf-8").splitlines()
    mitte = json.loads(zeilen[1])
    mitte["befunde"] = ["nachträglich hineingeschrieben"]
    zeilen[1] = json.dumps(mitte, ensure_ascii=False)
    sb.KETTE.write_text("\n".join(zeilen) + "\n", encoding="utf-8")
    e = sb.kette_pruefen(_t(130))
    assert not e["ok"] and e["brueche"] >= 1, \
        f"die veränderte Kette gilt als unversehrt: {e}"
    assert "sichtbar gemacht, nicht verhindert" in e["grund"], \
        "die Meldung überzeichnet die Schutzwirkung"


def _befunde_melden_sich():
    _leeren()
    sb._befunde = lambda: [("bot-prozess", "Bot-Prozess nicht vorhanden")]
    sb.bluehen(_t(0))
    m = _meldungen()
    assert m and "Bot-Prozess" in m[0], f"Befund nicht gemeldet: {m}"


def _anmeldung_bruch_wird_gemeldet():
    """C2: Ein Kippen der Anmeldung fällt SOFORT auf, statt in Stille."""
    _leeren()
    sb.shutil.which = lambda n: "/usr/bin/" + n
    ruf = []

    class _P:
        def __init__(self, out): self.stdout, self.stderr, self.returncode = out, "", 0

    def _run(cmd, **kw):
        ruf.append(cmd[0])
        if cmd[0] == "systemctl":
            return _P("4711\n")
        return _P("Jul 25 23:00 bot: anthropic: OAuth token expired\n")
    sb.subprocess.run = _run
    befunde = sb.anmeldung_pruefen()
    assert any("Anmeldung hat versagt" in text for _, text in befunde), \
        f"der Anmelde-Bruch wurde nicht gemeldet: {befunde}"
    assert "journalctl" in ruf, "das Journal wurde gar nicht gelesen"


def _anmeldung_still_wenn_gesund():
    """Und schweigt, wenn nichts ist — sonst glaubt ihr niemand mehr."""
    _leeren()
    sb.shutil.which = lambda n: "/usr/bin/" + n

    class _P:
        def __init__(self, out): self.stdout, self.stderr, self.returncode = out, "", 0
    sb.subprocess.run = lambda cmd, **kw: _P(
        "4711\n" if cmd[0] == "systemctl" else "alles ruhig\n")
    assert not [t for _, t in sb.anmeldung_pruefen() if "versagt" in t], "Fehlalarm bei gesunder Anmeldung"


def _kein_geheimniswert_im_code():
    """Geprüft wird das VORHANDENSEIN der Anmeldung, nie ihr Wert."""
    quelle = Path(sb.__file__).read_text(encoding="utf-8")
    # Der Name darf vorkommen — der Wert darf nirgends gelesen oder gemeldet
    # werden. Ein `split("=", 1)[1]` auf der Prozessumgebung wäre genau das.
    assert 'split("=", 1)[0]' in quelle, \
        "die Umgebung wird nicht nur nach NAMEN durchsucht"
    assert 'split("=", 1)[1]' not in quelle, \
        "der Wert eines Umgebungs-Geheimnisses wird gelesen!"


def _speicher_wache_misst_das_richtige():
    """Der Wächter darf nicht auf `MemFree` schauen — sonst ist er Dauer-Alarm.

    Auf einem gesunden Linux ist `MemFree` fast immer klein, weil der Kernel
    freien Speicher als Zwischenspeicher benutzt und jederzeit wieder hergibt.
    Ein Wächter darauf wäre binnen zwei Tagen abgeschaltet — und damit keiner
    mehr.
    """
    quelle = Path(sb.__file__).read_text(encoding="utf-8")
    block = quelle.split("def speicher_pruefen")[1].split("\ndef ")[0]
    assert "MemAvailable" in block, "die Wache misst nicht MemAvailable"
    assert 'm.get("MemFree")' not in block, \
        "die Wache stützt sich auf MemFree — das wäre ein Dauer-Alarm"

    echt = sb._meminfo
    # Gesund: 3 GiB verfügbar, kein Swap benutzt → Schweigen.
    sb._meminfo = lambda: {"MemTotal": 7940, "MemAvailable": 3000,
                           "SwapTotal": 4096, "SwapFree": 4096}
    assert sb.speicher_pruefen() == [], "Fehlalarm bei gesunder Lage"

    # Knapp, aber nicht kritisch → Hinweis, kein Alarm.
    sb._meminfo = lambda: {"MemTotal": 7940, "MemAvailable": 600,
                           "SwapTotal": 0, "SwapFree": 0}
    b = sb.speicher_pruefen()
    assert len(b) == 1 and b[0][1].startswith("🟡"), f"falsche Stufe: {b}"

    # Kritisch → deutliche Warnung.
    sb._meminfo = lambda: {"MemTotal": 7940, "MemAvailable": 200,
                           "SwapTotal": 0, "SwapFree": 0}
    b = sb.speicher_pruefen()
    assert b and b[0][1].startswith("🔴"), f"die enge Lage wurde nicht erkannt: {b}"

    # Swap in Benutzung → eigene Beobachtung, unabhängig von der Speicherlage.
    sb._meminfo = lambda: {"MemTotal": 7940, "MemAvailable": 3000,
                           "SwapTotal": 4096, "SwapFree": 1000}
    b = sb.speicher_pruefen()
    assert any("Auslagerungsbereich" in t for _, t in b), \
        "benutzter Swap wird nicht bemerkt"

    # Kein Linux (leeres meminfo) → keine Aussage statt Raterei.
    sb._meminfo = lambda: {}
    assert sb.speicher_pruefen() == [], "ohne Messwerte wurde etwas behauptet"
    sb._meminfo = echt


def _echte_befunde_laufen_durch():
    """**Fund vom 26.07., 02:25.** Alle Tests ersetzen `_befunde` durch eine
    Attrappe — und deshalb hat keiner bemerkt, dass ein fehlender Import den
    echten Weg zum Absturz brachte. Der Regressionslauf war grün, die Blume
    wäre bei jedem einzelnen Aufblühen gescheitert.

    Dieselbe Klasse wie Horas drei Funde derselben Nacht: **Die Attrappe prüft
    den Aufruf, nicht den Weg.** Deshalb ruft dieser Test die echte Kette einmal
    ungefiltert — er ist der einzige, der das tut, und genau darin liegt sein
    Wert.
    """
    import ast
    quelle = Path(sb.__file__).read_text(encoding="utf-8")
    baum = ast.parse(quelle)

    # Alles, was das Modul importiert — unter dem Namen, unter dem es danach
    # ansprechbar ist.
    bekannt = set(dir(__builtins__)) | {"__file__", "__name__"}
    for k in ast.walk(baum):
        if isinstance(k, ast.Import):
            bekannt |= {(a.asname or a.name.split(".")[0]) for a in k.names}
        elif isinstance(k, ast.ImportFrom):
            bekannt |= {(a.asname or a.name) for a in k.names}
        elif isinstance(k, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            bekannt.add(k.name)
        elif isinstance(k, ast.Name) and isinstance(k.ctx, ast.Store):
            bekannt.add(k.id)
        elif isinstance(k, ast.arg):
            bekannt.add(k.arg)
        elif isinstance(k, ast.ExceptHandler) and k.name:
            bekannt.add(k.name)

    # Jeder Name, der wie `modul.funktion(...)` benutzt wird, muss bekannt sein.
    fehlend = sorted({
        k.value.id for k in ast.walk(baum)
        if isinstance(k, ast.Attribute) and isinstance(k.value, ast.Name)
        and k.value.id not in bekannt and not k.value.id.startswith("_")
    })
    assert not fehlend, (
        f"benutzt, aber nirgends importiert: {', '.join(fehlend)} — "
        "das wirft erst zur Laufzeit, und zwar bei JEDEM Aufblühen. Kein "
        "anderer Test sieht es, weil alle `_befunde` durch eine Attrappe "
        "ersetzen (belegt am 26.07.: fehlender `zustellmarke`-Import, "
        "Regressionslauf grün, echter Pfad tot).")


def _rollen_zerreisst_die_kette_nicht():
    """Die Falle beim Rollen — und der einzige Grund, es zu bauen statt die
    Datei umzubenennen.

    Ein Rollen, das nur umbenennt, **bricht genau die Verkettung, die den Beleg
    ausmacht**: Das erste Glied der neuen Datei stünde ohne Vorgänger da, und
    der Bruch sähe aus wie eine Manipulation — der Wächter würde sich selbst
    anzeigen. Deshalb zeigt das erste neue Glied auf das letzte alte.
    """
    _leeren()
    for i in range(5):
        sb.bluehen(_t(i * 60))
    letzte_alt = sb._letzte()["abdruck"]

    archiv = sb.rollen(grenze=5, jetzt=_t(300))
    assert archiv and (sb.ZUSTAND / archiv).exists(), "nichts beiseitegelegt"
    assert not sb.KETTE.exists() or sb.KETTE.stat().st_size == 0, \
        "die alte Kette liegt noch am selben Platz"

    neu = sb.bluehen(_t(360))
    assert neu["vorher"] == letzte_alt, (
        "das erste Glied der neuen Datei zeigt NICHT auf das letzte der alten — "
        "die Kette ist am Rollen zerrissen")
    zweites = sb.bluehen(_t(420))
    assert zweites["vorher"] == neu["abdruck"], "danach bricht die Kette"
    e = sb.kette_pruefen(_t(480))
    assert e["ok"] and e["brueche"] == 0, f"die neue Kette gilt als kaputt: {e}"

    # Unter der Grenze wird NICHT gerollt — sonst zerfiele die Kette in Schnipsel.
    assert sb.rollen(grenze=999, jetzt=_t(540)) is None, \
        "es wurde gerollt, obwohl die Grenze nicht erreicht war"


def _lagebericht_nur_zustand():
    """G3: Ein Meldeweg, der ohne den Bot auskommt — aber nichts ausplaudert.

    Was hier landet, wandert in ein Repo und ist sichtbar, sobald jemand es
    einsieht. Deshalb **nur Zustand**: keine Nachrichteninhalte, keine
    Adressaten, keine Geheimnisse.
    """
    _leeren()
    ziel = _TMP / "logsync"
    ziel.mkdir(exist_ok=True)
    echt = sb.LAGEBERICHT
    sb.LAGEBERICHT = ziel / "zustand.json"

    sb._befunde = lambda: [("platte-knapp", "nur noch 2.0 GiB Plattenplatz frei")]
    sb.bluehen(_t(0))
    assert sb.LAGEBERICHT.exists(), "der Lagebericht wurde nicht geschrieben"
    d = json.loads(sb.LAGEBERICHT.read_text(encoding="utf-8"))
    assert set(d) == {"stand", "befunde", "luecke_s", "ruhe", "abdruck"}, \
        f"der Lagebericht führt mehr Felder als vorgesehen: {sorted(d)}"
    assert d["befunde"] == ["nur noch 2.0 GiB Plattenplatz frei"]

    # Auch wenn NICHTS zu melden ist, wird geschrieben — gerade das Ausbleiben
    # der Datei soll später der Alarm sein.
    sb._befunde = lambda: []
    sb.bluehen(_t(60))
    d = json.loads(sb.LAGEBERICHT.read_text(encoding="utf-8"))
    assert d["befunde"] == [], "bei ruhiger Lage wird nicht fortgeschrieben"

    # Ohne Klon wird nichts erfunden.
    sb.LAGEBERICHT = _TMP / "gibtsnicht" / "zustand.json"
    sb.bluehen(_t(120))
    assert not sb.LAGEBERICHT.exists(), "ein fehlender Klon wurde angelegt"
    sb.LAGEBERICHT = echt


def _eine_wortliste_fuer_beide():
    """G1: Zwei Listen driften — deshalb darf es nur eine geben.

    Der Auftrag lautete, einen Test zu bauen, der anschlägt, wenn `bot.py` eine
    Nadel kennt, die die Blume nicht kennt. Stärker ist, den Drift **unmöglich**
    zu machen: eine Quelle, zwei Leser. Also prüft der Test genau das — dass
    keine Seite eine eigene Liste führt.
    """
    import authmarke
    assert "oauth token has expired" in authmarke.NADELN, \
        "der Wortlaut, den wir TATSAECHLICH gesehen haben, fehlt"
    assert authmarke.passt("Error: OAuth token has expired"), \
        "der belegte Wortlaut wird nicht erkannt"

    for datei in (Path(sb.__file__), Path(sb.__file__).parent.parent / "bot.py"):
        quelle = datei.read_text(encoding="utf-8")
        eigene = [z for z in quelle.splitlines()
                  if "invalid x-api-key" in z or "could not resolve authentication" in z]
        assert not eigene, \
            f"{datei.name} führt wieder eine eigene Nadel-Liste: {eigene[:1]}"


def _marke_schlaegt_journal():
    """G1: Der Bot weiß es im Augenblick des Bruchs — das ist der bessere Weg."""
    import authmarke
    _leeren()
    authmarke.setzen("Error: OAuth token has expired")
    sb.shutil.which = lambda n: None          # weder systemctl noch journalctl
    befunde = sb.anmeldung_pruefen()
    assert any("Anmeldung hat versagt" in text for _, text in befunde), \
        "die Marke allein genügt nicht — der Wächter hängt am Journal"
    authmarke.loeschen()
    assert not [b for b in sb.anmeldung_pruefen() if "versagt" in b], \
        "nach der Entwarnung meldet er weiter"


def _kein_geheimniswert_in_der_marke():
    import authmarke
    authmarke.setzen("401 for key sk-ant-oat01-ABCDEFGHIJKLMNOPQRSTUVWXYZ012345")
    inhalt = json.dumps(authmarke.gesetzt() or {})
    assert "sk-ant-oat01-ABCDEFGHIJKLMNOPQRSTUVWXYZ012345" not in inhalt, \
        "ein Schlüssel steht im Klartext in der Marke!"
    authmarke.loeschen()


def _daempfer_wiederholt_nicht_minuetlich():
    """G4: 60 Meldungen je Stunde wären das Ende der Glaubwürdigkeit."""
    _leeren()
    sb._befunde = lambda: [("bot-prozess", "Bot-Prozess nicht vorhanden")]
    for i in range(5):
        sb.bluehen(_t(i * 60))
    m = _meldungen()
    assert len(m) == 1, f"derselbe Befund wurde {len(m)}× gemeldet"
    # Nach der Wiedervorlage-Frist darf er sich erinnern.
    sb.bluehen(_t(sb.WIEDERVORLAGE_S + 120))
    assert len(_meldungen()) == 2, "nach einer Stunde meldet er sich nicht wieder"


def _daempfer_entwarnt():
    """Was wegfällt, wird gesagt — sonst weiß niemand, ob es behoben ist."""
    _leeren()
    sb._befunde = lambda: [("platte-knapp", "nur noch 2.0 GiB Plattenplatz frei")]
    sb.bluehen(_t(0))
    sb._befunde = lambda: []
    sb.bluehen(_t(60))
    m = _meldungen()
    assert len(m) == 2 and "erledigt" in m[1], f"keine Entwarnung: {m}"


def _kein_modellaufruf_im_modul():
    quelle = Path(sb.__file__).read_text(encoding="utf-8")
    for verdacht in ("claude_agent_sdk", "anthropic", "ClaudeSDKClient",
                     "requests", "urlopen"):
        assert verdacht not in quelle, \
            f"eine Blume darf nichts Teures tun, fand aber: {verdacht}"


def _fortlaufende_zahl_meldet_nur_einmal():
    """**Der Sturm vom 28.07., 10:02 — als Prüfung.**

    Der Befund lautete „Zustellung gestört (seit 9 Min)", eine Minute später
    „(seit 10 Min)". Ein Dämpfer, der Texte vergleicht, hält das für einen
    **neuen** Befund und den alten für **weggefallen**: zwei Nachrichten pro
    Minute, Alarm und Entwarnung im selben Atemzug.

    Mit Kennung ist es dreimal derselbe Befund — eine Meldung, keine Entwarnung.
    """
    _leeren()
    for i, minuten in enumerate((9, 10, 11)):
        sb._befunde = lambda m=minuten: [
            ("zustellung-gestoert", f"📵 Zustellung gestört (seit {m} Min)")]
        sb.bluehen(_t(i * 60))
    m = _meldungen()
    assert len(m) == 1, (
        f"{len(m)} Meldungen statt einer — die wandernde Zahl gilt wieder als "
        f"neuer Befund: {[x[:50] for x in m]}")
    assert "erledigt" not in m[0], "es wurde zugleich entwarnt"


def _zwei_kennungen_kommen_beide_durch():
    """Die Gegenprobe: Der Dämpfer darf nicht zusammenfassen, was verschieden ist.

    Wichtig gerade bei den zwei Speicherschwellen — **die rote Warnung darf
    nicht von der gelben verschluckt werden.** Eine Zahlen-Bereinigung hätte
    sie nur zufällig getrennt (weil die Wortlaute sich unterscheiden), die
    Kennung trennt sie absichtlich.
    """
    _leeren()
    sb._befunde = lambda: [
        ("speicher-eng", "🔴 Nur noch 200 MiB verfügbar"),
        ("platte-knapp", "nur noch 2.0 GiB Plattenplatz frei")]
    sb.bluehen(_t(0))
    m = _meldungen()
    assert len(m) == 1, "die Befunde kamen nicht in EINER Meldung"
    assert "200 MiB" in m[0] and "2.0 GiB" in m[0], \
        f"ein Befund wurde verschluckt: {m[0]}"

    quelle = Path(sb.__file__).read_text(encoding="utf-8")
    for k in ("speicher-eng", "speicher-hinweis"):
        assert f'"{k}"' in quelle, \
            f"die Kennung {k} fehlt — die zwei Schwellen hängen wieder zusammen"


check("Kette wächst und ist verkettet", _kette_waechst_verkettet)
check("die Lücke ist der Alarm", _luecke_ist_der_alarm)
check("kurze Lücke schweigt", _kurze_luecke_schweigt)
check("angeordnete Ruhe schweigt", _ruhe_schweigt)
check("nächtliches Wartungsfenster schweigt", _nachtfenster_schweigt)
check("Stillstand fällt bei der Prüfung auf", _stillstand_faellt_auf)
check("Veränderung wird sichtbar (nicht verhindert)", _manipulation_wird_sichtbar)
check("echte Befunde melden sich", _befunde_melden_sich)
check("Anmelde-Bruch wird sofort gemeldet (C2)", _anmeldung_bruch_wird_gemeldet)
check("gesunde Anmeldung schweigt (C2)", _anmeldung_still_wenn_gesund)
check("nie der Wert eines Geheimnisses (C2)", _kein_geheimniswert_im_code)
check("Speicher-Wache misst MemAvailable, nicht MemFree",
      _speicher_wache_misst_das_richtige)
check("kein benutzter Name ohne Import (Attrappen-Luecke)",
      _echte_befunde_laufen_durch)
check("Rollen zerreisst die Kette nicht (Naht)", _rollen_zerreisst_die_kette_nicht)
check("Lagebericht führt nur Zustand (G3)", _lagebericht_nur_zustand)
check("EINE Wortliste für Bot und Blume (G1)", _eine_wortliste_fuer_beide)
check("die Marke schlägt das Journal (G1)", _marke_schlaegt_journal)
check("kein Geheimniswert in der Marke (G1)", _kein_geheimniswert_in_der_marke)
check("Dämpfer: kein minütliches Wiederholen (G4)",
      _daempfer_wiederholt_nicht_minuetlich)
check("Dämpfer entwarnt, wenn ein Befund wegfällt (G4)", _daempfer_entwarnt)
check("kein Modell- und kein Netzaufruf im Modul", _kein_modellaufruf_im_modul)
check("fortlaufende Zahl meldet nur EINMAL (Sturm 28.07.)",
      _fortlaufende_zahl_meldet_nur_einmal)
check("zwei Kennungen kommen beide durch (rot verschluckt gelb nicht)",
      _zwei_kennungen_kommen_beide_durch)


def _entwarnung_nennt_den_text_nicht_die_kennung():
    """**Live-Fund vom 28.07., 13:02 — im ersten echten Lauf nach dem Umbau.**

    Adam bekam wörtlich „erledigt — kette-luecke". Technisch richtig, für einen
    Menschen unbrauchbar: Die Kennung ist das Werkzeug des Dämpfers, nicht
    seine Sprache. Deshalb legt das Gedächtnis den zuletzt gemeldeten Wortlaut
    mit ab — sonst ist er beim Entwarnen nicht mehr da.
    """
    _leeren()
    sb._befunde = lambda: [("kette-luecke", "Die Kette hatte eine Lücke von 179 Minuten")]
    sb.bluehen(_t(0))
    sb._befunde = lambda: []
    sb.bluehen(_t(60))
    m = _meldungen()
    entwarnung = [x for x in m if "erledigt" in x]
    assert entwarnung, "es wurde nicht entwarnt"
    assert "Lücke von 179 Minuten" in entwarnung[0], (
        "die Entwarnung nennt die Kennung statt des Wortlauts: "
        f"{entwarnung[0][:120]}")
    assert "kette-luecke" not in entwarnung[0], \
        "die interne Kennung steht in Adams Nachricht"


check("Entwarnung nennt den Text, nicht die Kennung (Live-Fund)",
      _entwarnung_nennt_den_text_nicht_die_kennung)


def _statuszeile_meldet_stillstand():
    """Adams Wunsch vom 28.07.: sehen koennen, dass es laeuft — auf Abruf.

    **Warum keine stuendliche Meldung:** Ein Waechter, der regelmaessig „alles
    gut" sagt, wird nach zwei Tagen ueberlesen — und dann auch die eine
    Meldung, die zaehlt. Der Meldungssturm desselben Tages hat vorgefuehrt,
    wohin das fuehrt. Also Ueberblick auf Abruf, Alarm bei Anlass.

    Die Zeile muss vor allem EINES koennen: den Stillstand benennen. Eine
    Statuszeile, die bei stehender Kette „alles gut" sagt, waere schlimmer als
    keine.
    """
    import os as _os
    _os.environ.setdefault("TELEGRAM_BOT_TOKEN", "1:test")
    _os.environ.setdefault("ALLOWED_USER_IDS", "1")
    sys.path.insert(0, str(Path(sb.__file__).resolve().parent.parent))
    import bot

    echt = bot.Path.home
    heim = Path(_TMP / "heim")
    (heim / ".claude" / "stundenblumen").mkdir(parents=True, exist_ok=True)
    bot.Path.home = staticmethod(lambda: heim)
    kette = heim / ".claude" / "stundenblumen" / "kette.jsonl"
    try:
        # (1) Keine Kette → ehrlich gesagt, nicht beschoenigt.
        assert "noch keine Glieder" in bot._blumen_zeile()

        # (2) Frische Kette ohne Befund → lueckenlos, nichts zu melden.
        kette.write_text(json.dumps(
            {"zeit": time.time(), "befunde": []}) + "\n", encoding="utf-8")
        z = bot._blumen_zeile()
        assert "lückenlos" in z and "nichts zu melden" in z, z

        # (3) STILLSTAND — der Fall, für den die Zeile da ist.
        kette.write_text(json.dumps(
            {"zeit": time.time() - 3600, "befunde": []}) + "\n", encoding="utf-8")
        z = bot._blumen_zeile()
        assert "steht still" in z, (
            f"eine stehende Kette wird als in Ordnung gemeldet: {z}")

        # (4) Befunde werden genannt, nicht verschwiegen.
        kette.write_text(json.dumps(
            {"zeit": time.time(), "befunde": ["nur noch 2.0 GiB frei"]}) + "\n",
            encoding="utf-8")
        assert "2.0 GiB" in bot._blumen_zeile()
    finally:
        bot.Path.home = echt


check("Statuszeile benennt den Stillstand (Ueberblick auf Abruf)",
      _statuszeile_meldet_stillstand)



# ---------- Connis Fund 28.07.: der blinde Fleck auf den eigenen Träger ------
def _tagescheck_wird_mitbewacht():
    """**Was ein Prüfer trägt, kann er nicht prüfen.**

    Die Zeitgeber-Wache kann jeden Zeitgeber prüfen — außer den, der sie selbst
    startet. Sie lebt in `daily_check.sh`, und der läuft über einen Zeitgeber.
    Stirbt ausgerechnet dieser, stirbt die Wache mit ihm, und niemand meldet
    es. Das ist kein Konstruktionsfehler, sondern die übliche Grenze jeder
    Selbstprüfung — und deshalb ist die Lösung auch keine bessere
    Selbstprüfung, sondern eine zweite, unabhängige Instanz.
    """
    log = _TMP / "daily-check.log"
    sb.TAGESCHECK_LOG = log

    # Frisch gelaufen -> Ruhe.
    log.write_text("x", encoding="utf-8")
    assert sb.tagescheck_pruefen() == [], "ein frischer Lauf wird gemeldet"

    # Seit 30 Stunden nichts -> Befund, und zwar mit der vereinbarten Kennung.
    alt = time.time() - 30 * 3600
    os.utime(log, (alt, alt))
    befunde = sb.tagescheck_pruefen()
    assert len(befunde) == 1, f"der Ausfall wird nicht gemeldet: {befunde}"
    assert befunde[0][0] == "tagescheck-still", \
        f"falsche Kennung — der Dämpfer greift sonst nicht: {befunde[0][0]}"
    assert "Zeitgeber-Wache" in befunde[0][1], \
        "die Meldung sagt nicht, WAS mit dem Tagescheck ausfällt"

    # 25 Stunden sind noch kein Ausfall — ein verspäteter Lauf (Neustart,
    # Wartungsfenster, Zeitumstellung) darf nicht alarmieren.
    knapp = time.time() - 25 * 3600
    os.utime(log, (knapp, knapp))
    assert sb.tagescheck_pruefen() == [], \
        "ein bloß verspäteter Lauf schlägt Alarm — das schaltet den Wächter ab"

    # Gar kein Protokoll ist ein echter Befund, kein Grund zu schweigen.
    log.unlink()
    assert sb.tagescheck_pruefen()[0][0] == "tagescheck-still"


def _verschraenkung_greift_in_BEIDE_richtungen():
    """Eine Kreuzverschränkung, die nur in eine Richtung wirkt, ist keine —
    sie ist bloß ein zweiter Wächter mit demselben blinden Fleck."""
    import re
    daily = (Path(__file__).resolve().parent / "daily_check.sh").read_text(encoding="utf-8")
    assert re.search(r"stundenblume\.py[\"']?\s+--pruefen", daily), \
        "der Tagescheck prüft die Belegkette NICHT — die Verschränkung ist einseitig"
    quelle = Path(sb.__file__).read_text(encoding="utf-8")
    assert "def tagescheck_pruefen" in quelle and "tagescheck_pruefen()" in \
        quelle.split("def tagescheck_pruefen")[0], \
        "die Blumen prüfen den Tagescheck nicht — oder rufen es nicht auf"


check("Tagescheck wird von den Blumen mitbewacht (Connis Fund)",
      _tagescheck_wird_mitbewacht)
check("die Verschränkung greift in BEIDE Richtungen",
      _verschraenkung_greift_in_BEIDE_richtungen)

if fails:
    print(f"\n❌ {len(fails)} Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("\nAlle Stundenblumen-Tests bestanden.")
