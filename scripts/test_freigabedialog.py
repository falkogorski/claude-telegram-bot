#!/usr/bin/env python3
# <!-- ROLLE: test-freigabedialog -->
"""Der Freigabedialog sagt, worueber er entscheiden laesst.

**Alle Zeilen rufen `format_tool_call()` AUF und messen die Rueckgabe** —
keine sucht im Quelltext nach Zeichenketten. Das ist Claudias Auflage 5 und
die Hauskrankheit K1: Ein Pruefer, der Text liest, prueft die Schreibweise.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="dialog-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["PENDING_DIR"] = str(_TMP / "pending")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

fails: list[str] = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


class _Ctx:
    decision_reason = None
    blocked_path = None
    title = None
    display_name = None
    description = None


BEFEHL = "rm -rf /home/claudebot/wichtig && curl http://boese.tld"


def _bash_mit_beschreibung_zeigt_beides():
    """Der Satz ergaenzt den Befehl — **er ersetzt ihn nie.**

    Koennte die Beschreibung den Befehl verdraengen, waere sie ein Weg, Adam
    etwas anderes zu zeigen als das, was ausgefuehrt wird.
    """
    text = bot.format_tool_call(
        "Bash", {"command": BEFEHL, "description": "Aufraeumen im Heimverzeichnis"})
    assert "Aufraeumen im Heimverzeichnis" in text, "die Beschreibung fehlt"
    assert BEFEHL in text, f"der VOLLSTAENDIGE Befehl fehlt: {text!r}"
    assert "Angabe der Sitzung" in text, \
        "die Beschreibung ist nicht als Angabe der antragstellenden Sitzung gekennzeichnet"


def _bash_ohne_beschreibung_erfindet_nichts():
    """**Ein Platzhalter wuerde als [unbedenklich] gelesen.** Deshalb entfaellt
    die Zeile ersatzlos."""
    text = bot.format_tool_call("Bash", {"command": BEFEHL})
    assert BEFEHL in text, "der Befehl fehlt"
    assert "Angabe der Sitzung" not in text, \
        f"es wurde eine Beschreibung erfunden: {text!r}"
    assert "keine Beschreibung" not in text.lower(), \
        "ein Platzhalter steht da, wo nichts stehen darf"


def _write_wird_als_veraendernd_eingestuft():
    """Adam muss sehen, dass hier geschrieben wird — und wohin."""
    text = bot.format_tool_call("Write", {"file_path": "/home/claudebot/bot.py",
                                          "content": "x"})
    assert "VERAENDERT" in text, f"Write gilt nicht als veraendernd: {text!r}"
    assert "/home/claudebot/bot.py" in text, "der Dateiname fehlt"


def _unbekanntes_werkzeug_meldet_sich():
    """**Der Pruefer gegen das stille Veralten.**

    Kommt morgen ein Werkzeug hinzu, fiele es in den Sammelzweig. Ohne diese
    Zeile saehe das aus wie eingestuft — ein Bruch, der wie Ruhe aussieht.
    """
    text = bot.format_tool_call("Frobnicate", {"ziel": "x"})
    assert "nicht eingestuft" in text, \
        f"ein unbekanntes Werkzeug wird stillschweigend durchgereicht: {text!r}"


def _die_maschinen_angabe_steht_getrennt():
    """**Herkunft trennen** (Engywucks Antwort auf Claudias Frage 1): Was die
    CLI sagt, ist gemessen; was die Sitzung sagt, ist behauptet."""
    ctx = _Ctx()
    ctx.decision_reason = "Pfad ausserhalb des erlaubten Bereichs"
    ctx.blocked_path = "/etc/geheim.env"
    text = bot.format_tool_call("Bash", {"command": "cat /etc/geheim.env",
                                         "description": "nur mal schauen"}, ctx)
    assert "Maschine — Grund:" in text, "die CLI-Angabe fehlt"
    assert "/etc/geheim.env" in text, "der gesperrte Pfad fehlt"
    kopf = text.split("\n\n")[0]
    assert kopf.index("Angabe der Sitzung") < kopf.index("Maschine —"), \
        "Behauptetes und Gemessenes sind nicht unterscheidbar angeordnet"


def _fremdtext_baut_den_dialog_nicht_um():
    """Eine Beschreibung mit Zeilenumbruechen koennte einen zweiten Dialog
    vortaeuschen. Sie wird entschaerft — der Befehl nie."""
    boese = "harmlos\n\nBash\n\nls -la\nAngabe der Sitzung: alles gut"
    text = bot.format_tool_call("Bash", {"command": "echo x", "description": boese})
    kopf = text.split("\n\n")[0].split("\n")
    # **Die strukturelle Zusage: keine zusaetzliche ZEILE.** Der Kopf besteht
    # aus Angabe, Einstufung und ggf. Maschinen-Zeilen - nicht mehr.
    assert len(kopf) == 2, f"Fremdtext hat den Kopf umgebaut: {kopf}"
    assert kopf[0].startswith("Angabe der Sitzung:"), "die Kennzeichnung fehlt"
    # Und die fremde Angabe steht vollstaendig INNERHALB der Anfuehrung.
    assert kopf[0].endswith("\u201c"), \
        f"das Ende der fremden Angabe ist nicht sichtbar: {kopf[0]!r}"
    assert "echo x" in text, "der echte Befehl fehlt"


def _der_befehl_wird_nie_gekuerzt_wenn_die_beschreibung_lang_ist():
    """**Gekuerzt wird die Beschreibung, nie der Befehl.**"""
    text = bot.format_tool_call(
        "Bash", {"command": BEFEHL, "description": "A" * 5000})
    assert BEFEHL in text, "der Befehl wurde durch eine lange Beschreibung verdraengt"
    assert len(text) < 2000, "die Beschreibung wurde nicht gekuerzt"


check("Bash mit Beschreibung zeigt beides", _bash_mit_beschreibung_zeigt_beides)
check("Bash ohne Beschreibung erfindet nichts", _bash_ohne_beschreibung_erfindet_nichts)
check("Write wird als veraendernd eingestuft", _write_wird_als_veraendernd_eingestuft)
check("unbekanntes Werkzeug meldet sich", _unbekanntes_werkzeug_meldet_sich)
check("Maschinen-Angabe steht getrennt", _die_maschinen_angabe_steht_getrennt)
check("Fremdtext baut den Dialog nicht um", _fremdtext_baut_den_dialog_nicht_um)
check("der Befehl wird nie gekuerzt", _der_befehl_wird_nie_gekuerzt_wenn_die_beschreibung_lang_ist)

print()
if fails:
    print(f"❌ {len(fails)} Dialog-Pruefung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Freigabedialog-Tests bestanden.")
