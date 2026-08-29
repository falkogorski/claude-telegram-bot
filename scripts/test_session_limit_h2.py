#!/usr/bin/env python3
# <!-- ROLLE: test-session-limit -->
"""Verhaltenstest H2 Ebene 1 — Kontingent-Limit (Conni-Auftrag 25.07.).

Belegter Verlust am 24.07.: Adams Nachricht um 20:13 kam nie an, er musste sie
um 22:47 wiederholen. Geprüft wird deshalb die eine Eigenschaft, an der alles
hängt: **die Nachricht darf nicht verloren gehen** — sie wartet vorn in der
Schlange, bis das Kontingent zurück ist.
"""
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="h2test-"))
os.environ["PENDING_DIR"] = str(_TMP / "pending")
os.environ["QUESTIONS_FILE"] = str(_TMP / "q.json")
os.environ["TELEGRAM_BOT_TOKEN"] = ("1:testtoken")
os.environ["ALLOWED_USER_IDS"] = "4242"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import bot  # noqa: E402

fails = []


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


# --- Erkennung: echte Limit-Meldungen ja, Nachbarfehler nein ---------------
def _erkennung():
    treffer = [
        "Claude usage limit reached · resets 8:50pm",
        "You've hit your session limit",
        "429 Too Many Requests",
        "rate limit exceeded",
    ]
    for t in treffer:
        assert bot.is_session_limit(Exception(t)), f"nicht erkannt: {t}"
    daneben = [
        "prompt is too long",
        "JSON message exceeded maximum buffer size of 1048576 bytes",
        "invalid x-api-key",
    ]
    for t in daneben:
        assert not bot.is_session_limit(Exception(t)), f"fälschlich erkannt: {t}"


# --- Reset-Uhrzeit: nur lesen, nie raten -----------------------------------
def _reset_gelesen():
    jetzt = datetime.now().astimezone().replace(hour=14, minute=0, second=0,
                                                microsecond=0).timestamp()
    ts = bot.parse_reset_zeit("Claude usage limit reached · resets 8:50pm", jetzt)
    assert ts is not None, "Uhrzeit nicht gelesen"
    d = datetime.fromtimestamp(ts).astimezone()
    assert (d.hour, d.minute) == (20, 50), f"falsch gelesen: {d}"


def _reset_24h_format():
    jetzt = datetime.now().astimezone().replace(hour=9, minute=0, second=0,
                                                microsecond=0).timestamp()
    ts = bot.parse_reset_zeit("limit reached, resets at 20:15", jetzt)
    d = datetime.fromtimestamp(ts).astimezone()
    assert (d.hour, d.minute) == (20, 15), f"falsch gelesen: {d}"


def _reset_naechster_tag():
    """Liegt die genannte Zeit schon hinter uns, ist der nächste Tag gemeint."""
    jetzt = datetime.now().astimezone().replace(hour=23, minute=30, second=0,
                                                microsecond=0).timestamp()
    ts = bot.parse_reset_zeit("resets 2:00am", jetzt)
    assert ts > jetzt, "Reset-Zeitpunkt liegt in der Vergangenheit"
    assert ts - jetzt < 12 * 3600, "Reset-Zeitpunkt unplausibel weit weg"


def _keine_zeit_kein_raten():
    assert bot.parse_reset_zeit("Claude usage limit reached") is None, \
        "es wurde eine Uhrzeit erfunden, die nicht in der Meldung stand"


# --- Der Kern: die Nachricht bleibt erhalten und behält ihren Platz --------
def _nachricht_bleibt_vorn():
    mb = bot._get_mailbox(4242)
    mb.queue.clear()
    spaeter = bot.QueuedJob(update=None, text="zweite Nachricht", bot=None,
                            chat_id=4242, message_id=2)
    mb.queue.append(spaeter)
    # **[RANG A, Stelle 6 — 29.08.] Hier stand die Nachbildung, nicht die
    # Pruefung.** Der Test legte den Job mit `mb.queue.appendleft(...)` SELBST
    # an den Kopf und setzte die Pause SELBST — und stellte danach fest, dass
    # beides so ist. Er mass seine eigenen zwei Zeilen.
    #
    # Haette `_run_job` das Zuruecklegen eingestellt, waere er gruen geblieben,
    # und Adams Nachricht waere beim naechsten Kontingent-Limit verloren
    # gewesen. Genau der Fall, fuer den A1 ueberhaupt gebaut wurde.
    #
    # Jetzt wird die echte Ruecklage AUFGERUFEN.
    gescheitert = bot.QueuedJob(update=None, text="erste Nachricht", bot=None,
                                chat_id=4242, message_id=1)
    bot.limit_ruecklage(mb, gescheitert,
                        "5-hour limit reached, resets at 9pm")
    assert len(mb.queue) == 2, "eine Nachricht ging verloren"
    assert mb.queue[0].text == "erste Nachricht", \
        "die Reihenfolge stimmt nicht — die ältere Nachricht muss vorn bleiben"
    assert mb.pausiert_bis > 0, "keine Pause gesetzt"
    mb.queue.clear()
    mb.pausiert_bis = 0.0


# --- Der Zweig existiert im Code und schließt sauber ab --------------------
def _zweig_verhaelt_sich_richtig():
    """**[RANG A, Stelle 6] Textsuche ersetzt — dreimal.**

    Hier stand `src.index(...)` mit Suchfenstern von 900 und 2500 Zeichen. Das
    ist doppelt zerbrechlich: Es misst Schreibweise statt Wirkung, UND das
    Fenster verschiebt sich, sobald jemand einen Kommentar einfuegt. Ein
    umformulierter Zweig waere rot geworden, ohne dass sich etwas geaendert
    haette — und ein entkernter waere gruen geblieben.
    """
    import ast as _ast
    import inspect

    # (a) Die Ruecklage TUT, was sie soll — ausgefuehrt, mit leerer Schlange.
    mb = bot.Mailbox()
    job = bot.QueuedJob(update=None, text="x", bot=None, chat_id=1, message_id=1)
    bis = bot.limit_ruecklage(mb, job, "5-hour limit reached, resets at 9pm")
    assert list(mb.queue) == [job], "die Ruecklage legt den Auftrag nicht zurueck"
    assert mb.pausiert_bis > 0, "die Ruecklage setzt keine Pause"
    assert bis, "die Reset-Zeit aus der Meldung wurde nicht gelesen"

    # (b) Ohne Zeitangabe wird keine erfunden — aber pausiert wird trotzdem.
    mb2 = bot.Mailbox()
    job2 = bot.QueuedJob(update=None, text="y", bot=None, chat_id=1, message_id=2)
    bis2 = bot.limit_ruecklage(mb2, job2, "usage limit reached")
    assert bis2 is None, "es wurde eine Zeit erfunden, die nicht dastand"
    assert mb2.pausiert_bis > 0, "ohne Zeitangabe wird gar nicht pausiert"

    # (c) Der Limit-Zweig RUFT sie — echte Aufrufknoten, keine Zeichenkette.
    _baum = _ast.parse(inspect.getsource(bot._run_job).lstrip())
    _rufe = [k for k in _ast.walk(_baum)
             if isinstance(k, _ast.Call) and isinstance(k.func, _ast.Name)
             and k.func.id == "limit_ruecklage"]
    assert _rufe, "_run_job ruft die Ruecklage nicht auf — der Limit-Fall " \
                  "verliert die Nachricht wieder"

    # (d) Und er endet als OFFEN, nicht als gescheitert. Gemessen ueber den
    #     Rueckgabewert im Syntaxbaum statt ueber ein Textfenster.
    _rueck = {k.value.value for k in _ast.walk(_baum)
              if isinstance(k, _ast.Return) and isinstance(k.value, _ast.Constant)
              and isinstance(k.value.value, str)}
    assert "offen" in _rueck, \
        "der Limit-Fall wird nicht als offen (= nicht gescheitert) beendet"

    w = inspect.getsource(bot._session_worker)
    assert "pausiert_bis" in w, "der Worker kennt die Kontingent-Pause nicht"


check("Limit-Meldungen erkannt, Nachbarfehler nicht", _erkennung)
check("Reset-Uhrzeit aus der Meldung gelesen (12h)", _reset_gelesen)
check("Reset-Uhrzeit gelesen (24h)", _reset_24h_format)
check("vergangene Uhrzeit meint den nächsten Tag", _reset_naechster_tag)
check("ohne Angabe wird keine Uhrzeit erfunden", _keine_zeit_kein_raten)
check("Nachricht bleibt erhalten und behält ihren Platz", _nachricht_bleibt_vorn)
check("Limit-Zweig legt zurück, pausiert und gilt als offen", _zweig_verhaelt_sich_richtig)

if fails:
    print(f"\n{len(fails)} Test(s) fehlgeschlagen: {fails}")
    sys.exit(1)
print("\nAlle H2-Kontingent-Tests bestanden.")


def _a1_zugangsfehler_legt_zurueck():
    """A1 — die eine Luecke, die nicht vierzehn Tage warten durfte.

    Beim Kontingent-Limit war seit dem 25.07. alles geregelt: Die Nachricht
    geht an den Kopf der Schlange zurueck. Beim ZUGANGSFEHLER galt sie als
    „aufgegeben" — und war damit fort, nicht verzoegert. Ausgerechnet im Fall,
    fuer den die ganze Abwesenheits-Vorsorge gebaut wurde: Kippt das Token,
    waehrend niemand da ist, verlaere Adams Nachricht.

    Geprueft wird am Code, weil der Zweig nur im echten Fehlerpfad laeuft.
    """
    quelle = Path(bot.__file__).read_text(encoding="utf-8")
    zweig = quelle.split("if is_auth_error(e):")[1].split("if is_session_limit(e):")[0]

    assert "mb.queue.appendleft(job)" in zweig, \
        "der Auftrag wird beim Zugangsfehler NICHT zurueckgelegt — er ist fort"
    assert "STATUS_OPEN" in zweig, \
        "der Auftrag bleibt nicht offen; er stuende als gescheitert im Register"
    assert 'return "aufgegeben"' not in zweig, \
        "der Zweig gilt weiterhin als aufgegeben"
    assert 'return "zurueckgelegt"' in zweig, "kein eigener Ausgang"

    # KEINE Pause: Ein Zugangsfehler heilt nicht nach einer Frist.
    assert "pausiert_bis" not in zweig, (
        "beim Zugangsfehler wird eine Pause gesetzt — das verspricht eine "
        "Rueckkehr, die niemand geben kann; nur ein neues Token hilft")

    # Und der Ausgang muss in der Persistenz-Pflege ankommen, sonst stuende der
    # Auftrag als gescheitert da, obwohl er gleich wieder gezogen wird.
    assert '("offen", "zurueckgelegt")' in quelle, \
        "der neue Ausgang wird in der Persistenz nicht als OFFEN gefuehrt"

    # Adam erfaehrt, dass nichts verloren ist.
    assert "nicht verloren" in zweig, \
        "die Meldung sagt Adam nicht, dass seine Nachricht erhalten bleibt"


check("A1: Zugangsfehler legt den Auftrag zurueck, statt ihn aufzugeben",
      _a1_zugangsfehler_legt_zurueck)
