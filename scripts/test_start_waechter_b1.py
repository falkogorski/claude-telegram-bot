#!/usr/bin/env python3
# <!-- ROLLE: test-start-waechter -->
"""Verhaltenstest B1 — Start-Wächter (Conni-Auftrag 25.07.).

Prüft die Logik mit ersetzten Systemaufrufen: Es wird nichts installiert,
nichts beendet, nichts versendet. Der Kern ist der Fall, für den es den
Wächter gibt — der Bot kommt nach einem Neustart NICHT sauber hoch.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="b1test-"))
os.environ["UPDATER_STATE_DIR"] = str(_TMP / "state")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["ALLOWED_USER_IDS"] = "304455165"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import start_waechter as w  # noqa: E402

w.TAKT = 0.01
w.NACHFRIST = 1
fails = []

FREEZE = _TMP / "freeze.txt"
FREEZE.write_text("demo==1.0.0\n", encoding="utf-8")


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:
        # **Auch eine Ausnahme ist ein Befund, kein Abbruchgrund.** Bricht der
        # Laeufer hier ab, laufen die NACHFOLGENDEN Pruefungen nicht mehr - und
        # ihre Befunde gehen still verloren. Dieselbe Klasse wie der Tagescheck,
        # der am 29.07. mitten im Lauf starb und alles Gemessene mitnahm.
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


def _patch(prozess=1234, aktiv=True, check_folge=None, rollback=(True, ""),
           kill="Prozess beendet"):
    """Systemberührende Teile ersetzen; check_folge ist eine Liste von Ergebnissen."""
    w.bot_prozess = lambda: prozess
    w.dienst_aktiv = lambda: aktiv
    folge = iter(check_folge if check_folge is not None else [(True, "")])
    letzte = [(True, "")]

    def _sc(_venv):
        try:
            letzte[0] = next(folge)
        except StopIteration:
            pass
        return letzte[0]
    w.selbstcheck = _sc
    w.zurueckrollen = lambda venv, fr: rollback
    w.neustart_ausloesen = lambda: kill


def _berichte() -> list[str]:
    ordner = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if not ordner.exists():
        return []
    import json
    return [json.loads(p.read_text(encoding="utf-8"))["text"]
            for p in sorted(ordner.glob("*.json"))]


def _leeren():
    ordner = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if ordner.exists():
        for p in ordner.glob("*.json"):
            p.unlink()


# --- Sauberer Hochlauf: nichts anfassen, kurz melden ------------------------
def _sauber():
    _leeren()
    gerollt = []
    _patch()
    w.zurueckrollen = lambda v, f: (gerollt.append(1), (True, ""))[1]
    rc = w.bewachen(Path("/tmp/venv"), FREEZE, frist=2, grund_text="einem Test")
    assert rc == 0, f"Rückgabewert falsch: {rc}"
    assert not gerollt, "es wurde zurückgerollt, obwohl alles sauber war!"
    b = _berichte()
    assert b and "✅" in b[0], f"keine Erfolgsmeldung: {b}"


# --- Kein Prozess → Rettung greift -----------------------------------------
def _kein_prozess_rettet():
    _leeren()
    gerollt, gekillt = [], []
    _patch(prozess=None)
    w.zurueckrollen = lambda v, f: (gerollt.append(f), (True, ""))[1]
    w.neustart_ausloesen = lambda: (gekillt.append(1), "beendet")[1]
    # nach dem Rollback läuft er wieder
    zustand = {"tot": True}

    def _pid():
        return None if zustand["tot"] else 999
    w.bot_prozess = _pid

    def _roll(v, f):
        gerollt.append(f)
        zustand["tot"] = False
        return (True, "")
    w.zurueckrollen = _roll
    rc = w.bewachen(Path("/tmp/venv"), FREEZE, frist=0.2, grund_text="einem Update")
    assert gerollt, "es wurde NICHT zurückgerollt, obwohl der Bot tot war"
    assert Path(gerollt[0]) == FREEZE, "es wurde nicht der eingefrorene Stand genutzt"
    assert gekillt, "kein Neustart ausgelöst"
    assert rc == 1, f"Rückgabewert falsch: {rc}"
    b = _berichte()
    assert b and "🔴" in b[0] and "zurückgesetzt" in b[0], f"Meldung unklar: {b}"


# --- Prozess lebt, aber Selbstcheck rot → trotzdem Rettung -----------------
def _lebt_aber_kaputt():
    _leeren()
    gerollt = []
    _patch(check_folge=[(False, "✗ Medien-Transport (H1)")])
    w.zurueckrollen = lambda v, f: (gerollt.append(1), (True, ""))[1]
    w.bewachen(Path("/tmp/venv"), FREEZE, frist=0.2, grund_text="einem Update")
    assert gerollt, "lebender Prozess mit rotem Selbstcheck galt als sauber!"
    b = _berichte()
    assert b and "Selbstcheck rot" in b[0], f"Grund fehlt in der Meldung: {b}"


# --- Rettung scheitert → doppelt laut melden -------------------------------
def _rettung_scheitert_laut():
    _leeren()
    _patch(prozess=None, rollback=(False, "pip nicht erreichbar"))
    rc = w.bewachen(Path("/tmp/venv"), FREEZE, frist=0.2, grund_text="einem Update")
    assert rc == 2, f"Rückgabewert falsch: {rc}"
    b = _berichte()
    assert b and "🔴🔴" in b[0], f"gescheiterte Rettung nicht laut gemeldet: {b}"
    assert "FEHLGESCHLAGEN" in b[0] and "von Hand" in b[0], \
        "die Meldung sagt nicht, dass ein Eingriff von Hand nötig ist"


# --- Der Bericht landet auch dann, wenn der Bot nichts senden kann ---------
def _bericht_auch_ohne_bot():
    _leeren()
    _patch(prozess=None, rollback=(False, "kaputt"))
    w.bewachen(Path("/tmp/venv"), FREEZE, frist=0.2, grund_text="einem Update")
    assert w.BERICHT.exists(), "keine Zustandsdatei für den 4-Uhr-Check hinterlegt"


# --- Messartefakt: der eigene Prozess zählt nicht als Bot ------------------
def _eigener_prozess_zaehlt_nicht():
    import subprocess as sp
    echt = sp.run
    zeile = f"{os.getpid()} python3 scripts/start_waechter.py --freeze x\n"

    class _R:
        stdout = zeile
    sp.run = lambda *a, **k: _R()
    try:
        import importlib
        importlib.reload(w)
        w.TAKT = 0.01
        assert w.bot_prozess() is None, \
            "der Wächter hält seinen eigenen Prozess für den Bot"
    finally:
        sp.run = echt
        import importlib
        importlib.reload(w)
        w.TAKT = 0.01
        w.NACHFRIST = 1


# --- Stelle 7: der abgekoppelte Start meldet nur, was er belegen kann ------
def _detach_ohne_lebensnachweis_meldet_es():
    """**[RANG A, Stelle 7 — 29.08.] Ausgefuehrt, nicht gelesen.**

    Der `--detach`-Zweig meldete Erfolg, sobald der Kindprozess GESTARTET war.
    Stirbt er sofort — fehlendes venv, unlesbare Freeze-Datei, Tippfehler im
    Pfad —, sieht der Aufrufer [abgekoppelt gestartet] und spielt beruhigt
    sein Update ein. **Es wacht dann niemand**, und weil beide Ausgabekanaele
    nach /dev/null gehen, bleibt auch die Fehlermeldung ungesehen.

    Hier wird ein echter abgekoppelter Start gefahren, mit einem Interpreter,
    der garantiert scheitert. Erwartet: Rueckgabewert ungleich null und eine
    Meldung, die es ausspricht.
    """
    import subprocess as sp
    import sys as _sys
    echt_popen = sp.Popen
    echt_argv = _sys.argv[:]

    class _ToterKindprozess:
        pid = 99999
        def poll(self):
            return 1                      # sofort gestorben

    gedruckt: list[str] = []
    echt_print = __builtins__.print if hasattr(__builtins__, "print") else print
    try:
        w.LEBENSMARKE.unlink(missing_ok=True)
        w.DETACH_NACHWEIS_S = 0.3         # der Test soll nicht warten
        sp.Popen = lambda *a, **k: _ToterKindprozess()
        _sys.argv = ["start_waechter.py", "--freeze", str(FREEZE), "--detach"]
        import io, contextlib
        puffer = io.StringIO()
        with contextlib.redirect_stdout(puffer):
            rc = w.main()
        ausgabe = puffer.getvalue()
    finally:
        sp.Popen = echt_popen
        _sys.argv = echt_argv
        w.DETACH_NACHWEIS_S = 5.0

    assert rc != 0, ("der abgekoppelte Start meldete Erfolg ueber einem toten "
                     f"Waechter (rc={rc}) — genau der Befund von Stelle 7")
    assert "NICHT gestartet" in ausgabe and "wacht niemand" in ausgabe, \
        f"die Meldung sagt nicht, dass niemand wacht: {ausgabe!r}"


def _detach_mit_lebensnachweis_meldet_erfolg():
    """Die Gegenrichtung — sonst waere die Zeile oben mit einem harten
    `return 3` zu erfuellen, und der Wachdienst waere nie startbar."""
    import subprocess as sp
    import sys as _sys
    echt_popen, echt_argv = sp.Popen, _sys.argv[:]

    class _LebendigerKindprozess:
        pid = 12345
        def poll(self):
            # Er lebt — und hat, wie das echte Kind, seine Marke geschrieben.
            w.LEBENSMARKE.parent.mkdir(parents=True, exist_ok=True)
            w.LEBENSMARKE.write_text("12345", encoding="utf-8")
            return None

    try:
        w.LEBENSMARKE.unlink(missing_ok=True)
        w.DETACH_NACHWEIS_S = 1.0
        sp.Popen = lambda *a, **k: _LebendigerKindprozess()
        _sys.argv = ["start_waechter.py", "--freeze", str(FREEZE), "--detach"]
        import io, contextlib
        puffer = io.StringIO()
        with contextlib.redirect_stdout(puffer):
            rc = w.main()
        ausgabe = puffer.getvalue()
    finally:
        sp.Popen = echt_popen
        _sys.argv = echt_argv
        w.DETACH_NACHWEIS_S = 5.0
        w.LEBENSMARKE.unlink(missing_ok=True)

    assert rc == 0, f"ein lebender Waechter wird als Fehlschlag gemeldet (rc={rc})"
    assert "bei der Arbeit" in ausgabe, \
        f"die Erfolgsmeldung nennt den Lebensnachweis nicht: {ausgabe!r}"


def _die_marke_entsteht_waehrend_der_bewachung():
    """**Die Gegenprobe hat gezeigt, dass diese Zeile fehlte.**

    `_detach_mit_lebensnachweis_meldet_erfolg` benutzt eine Attrappe, die die
    Marke SELBST schreibt — sie belegt also nur, dass der Elternprozess auf
    eine vorhandene Marke richtig reagiert. Entfernte man das Schreiben in
    `bewachen()`, blieb der Pruefer gruen: **K2 in Reinform, der Pruefer misst
    seine eigene Nachbildung.**

    Hier wird die Marke MITTEN im echten Lauf beobachtet — sichtbar ist sie
    nur dort, denn am Ende raeumt `bewachen()` sie wieder weg.
    """
    _leeren()
    w.LEBENSMARKE.unlink(missing_ok=True)
    gesehen: list[bool] = []
    _patch()
    echt_warten = w.warte_auf_hochlauf
    try:
        def _beobachten(venv, frist):
            gesehen.append(w.LEBENSMARKE.exists())
            return echt_warten(venv, frist)
        w.warte_auf_hochlauf = _beobachten
        w.zurueckrollen = lambda v, f: (True, "")
        w.bewachen(Path("/tmp/venv"), FREEZE, frist=1, grund_text="einem Test")
    finally:
        w.warte_auf_hochlauf = echt_warten

    assert gesehen, "der Beobachter wurde nie gerufen — Pruefung bedeutungslos"
    assert gesehen[0], ("waehrend der Bewachung liegt KEIN Lebensnachweis vor — "
                        "der abgekoppelte Start koennte ihn nie sehen")


def _die_marke_wird_geraeumt():
    """Eine Marke, die liegen bleibt, behauptet morgen, es wache jemand."""
    _leeren()
    _patch()
    w.zurueckrollen = lambda v, f: (True, "")
    w.bewachen(Path("/tmp/venv"), FREEZE, frist=1, grund_text="einem Test")
    assert not w.LEBENSMARKE.exists(), \
        "der Lebensnachweis liegt nach der Bewachung noch da"


def _die_prozesserkennung_findet_einen_echten_prozess():
    """**[Engywucks Fund ① vom 29.08.] Ausgefuehrt auf DIESER Maschine.**

    Hier stand `pgrep -af` — die GNU-Form. Auf dem Mac gemessen liefert sie
    nackte PIDs ohne Befehlszeile, und `-a` heisst dort *Vorfahren
    einbeziehen*. `bot_prozess()` lieferte damit **immer** `None`; der
    Waechter haette nach Fristablauf ein `pip install` ueber die venv eines
    gesunden Bots gespielt.

    Diese Zeile prueft nicht die Schreibweise des Aufrufs, sondern **ob die
    Erkennung auf der Maschine funktioniert, auf der sie gerade laeuft** —
    mit einem echten Prozess, der `bot.py` im Namen traegt. Genau das haette
    den Fund von Anfang an verhindert, und zwar auf beiden Systemen.
    """
    import subprocess as sp
    import sys as _sys
    import time as _time

    # Ein echter, harmloser Prozess, dessen Befehlszeile `bot.py` enthaelt.
    kind = sp.Popen([_sys.executable, "-c",
                     "import time,sys; sys.argv=['bot.py']; time.sleep(20)",
                     "bot.py"],
                    stdout=sp.DEVNULL, stderr=sp.DEVNULL)
    try:
        _time.sleep(0.6)
        gefunden = w.bot_prozess()
        assert gefunden is not None, (
            "die Prozesserkennung findet einen laufenden bot.py-Prozess NICHT "
            "— auf dieser Maschine liefert sie immer None, und der Waechter "
            "wuerde einen gesunden Bot zurueckrollen")
    finally:
        kind.terminate()
        try:
            kind.wait(timeout=5)
        except Exception:
            kind.kill()

    # Die Gegenrichtung: ohne solchen Prozess darf sie nichts erfinden.
    _time.sleep(0.4)
    # (Auf einer Maschine, auf der der echte Bot laeuft, ist ein Treffer
    #  richtig — deshalb hier nur pruefen, dass der Testprozess weg ist.)
    assert kind.poll() is not None, "der Probe-Prozess laeuft noch"


check("Prozesserkennung findet einen echten Prozess",
      _die_prozesserkennung_findet_einen_echten_prozess)
check("abgekoppelt ohne Lebensnachweis → laut", _detach_ohne_lebensnachweis_meldet_es)
check("abgekoppelt mit Lebensnachweis → Erfolg", _detach_mit_lebensnachweis_meldet_erfolg)
check("der Lebensnachweis entsteht im Lauf", _die_marke_entsteht_waehrend_der_bewachung)
check("der Lebensnachweis wird geräumt", _die_marke_wird_geraeumt)
check("sauberer Hochlauf → nichts anfassen", _sauber)
check("kein Prozess → Rollback auf den eingefrorenen Stand + Neustart", _kein_prozess_rettet)
check("Prozess lebt, Selbstcheck rot → trotzdem Rettung", _lebt_aber_kaputt)
check("gescheiterte Rettung wird doppelt laut", _rettung_scheitert_laut)
check("Bericht liegt auch für den 4-Uhr-Check bereit", _bericht_auch_ohne_bot)
check("eigener Prozess zählt nicht als Bot", _eigener_prozess_zaehlt_nicht)

# --- Kein Rückweg → NICHT eingreifen (Trockenlauf-Lehre 25.07.) ------------
def _ohne_rueckweg_kein_eingriff():
    _leeren()
    gekillt, gerollt = [], []
    _patch(prozess=None)
    w.neustart_ausloesen = lambda: (gekillt.append(1), "beendet")[1]
    w.zurueckrollen = lambda v, f: (gerollt.append(1), (True, ""))[1]
    fehlt = _TMP / "gibtsnicht-freeze.txt"
    rc = w.bewachen(Path("/tmp/venv"), fehlt, frist=0.2, grund_text="einem Test")
    assert not gekillt, "der Bot wurde beendet, obwohl kein Rückweg vorlag!"
    assert not gerollt, "es wurde ein Rückbau versucht, obwohl die Datei fehlt"
    assert rc == 2, f"Rückgabewert falsch: {rc}"
    b = _berichte()
    assert b and "NICHT ein" in b[0], f"Verzicht auf den Eingriff nicht benannt: {b}"


# --- Meldeziel auch ohne Umgebungsvariable (Trockenlauf-Lehre) -------------
def _melde_ziel_aus_einstellungen():
    import json as _j
    alt = os.environ.pop("ALLOWED_USER_IDS", None)
    prefs = Path.home() / ".config" / "claude-telegram-bot" / "prefs.json"
    try:
        assert w._melde_ziel() == "" or w._melde_ziel().isdigit(), \
            "Meldeziel ohne Umgebungsvariable liefert Unsinn"
        if prefs.exists():
            daten = _j.loads(prefs.read_text(encoding="utf-8"))
            if any(str(k).isdigit() for k in daten):
                assert w._melde_ziel().isdigit(), \
                    "Rückfallweg über die Einstellungsdatei greift nicht"
    finally:
        if alt is not None:
            os.environ["ALLOWED_USER_IDS"] = alt


check("kein Rückweg → nicht eingreifen, laut melden", _ohne_rueckweg_kein_eingriff)
check("Meldeziel notfalls aus der Einstellungsdatei", _melde_ziel_aus_einstellungen)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle B1-Start-Wächter-Tests bestanden.")
