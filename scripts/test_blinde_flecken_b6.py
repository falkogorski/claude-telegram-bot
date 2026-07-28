#!/usr/bin/env python3
# <!-- ROLLE: test-blinde-flecken -->
"""Der kleine Wächter zum Blinde-Flecken-Verfahren (B6).

**Was er kann und was nicht.** Er kann die konkreten Fallen bewachen, die wir
schon kennen — vor allem die Positivliste, die sich als Suche ausgibt. Er kann
das Verfahren nicht ersetzen: Ob ein Kommentar und der Code darunter dasselbe
sagen, beantwortet ein Leser, kein Programm.

Deshalb ist er absichtlich **klein und konkret**. Ein Prüfer, der alles
versprochen hätte, wäre selbst der nächste blinde Fleck.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _zeitgeber_suche_ist_keine_positivliste():
    """**Frage ③ — steht die Vorgabe im Text oder im Code?**

    Über der Zeitgeber-Suche stand „DIE ZEITGEBER WERDEN GESUCHT, NICHT
    AUFGEZÄHLT" — und darunter ein Filter auf die Namensanfänge `claude-`,
    `hora` und `stundenblume`. Eine Positivliste in Verkleidung. Ein neunter
    Zeitgeber mit anderem Namen wäre durchgefallen, und der Kommentar hätte
    behauptet, er sei abgedeckt.

    Das Merkmal muss eine Umbenennung überleben: Was in unser Verzeichnis
    zeigt, ist unseres.
    """
    quelle = (ROOT / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
    suchblock = quelle.split("zeitgeber_still=()")[1].split("if [ \"${#zeitgeber_still")[0]
    assert "ExecStart" in suchblock, \
        "die Zeitgeber werden nicht am Ziel erkannt — womit dann?"
    assert "UNSER_PFAD" in suchblock, "das Suchmerkmal ist nicht der eigene Pfad"
    verdaechtig = re.search(r"\$NF\s*~\s*/\^\((claude-|hora|stundenblume)", suchblock)
    assert not verdaechtig, \
        "die Suche filtert wieder auf Namensanfänge — das ist die Positivliste"


def _jeder_waechter_meldet_seine_blinden_flecken():
    """**Frage ① — weiß der Prüfer, was er nicht prüft?**

    Beide Stellen, die das Komponenten-Register auswerten, hatten denselben
    stillen Übersprung — und der Fix an der einen erreichte die andere nicht.
    """
    vm = (ROOT / "scripts" / "version_monitor.py").read_text(encoding="utf-8")
    assert "blind" in vm and "if updates or blind:" in vm, \
        "der Versions-Monitor meldet blinde Flecken nicht eigenständig"
    up = (ROOT / "scripts" / "updater.py").read_text(encoding="utf-8")
    assert "def blinde_flecken" in up, \
        "der Updater übergeht unerreichbare Quellen wieder stillschweigend"


def _kein_traeger_ohne_wache():
    """**Frage ② — wer prüft den Träger?**

    Der 4-Uhr-Check trägt die Zeitgeber-Wache und läuft selbst über einen
    Zeitgeber. Die Stundenblumen laufen über einen eigenen — nur deshalb kann
    die Verschränkung überhaupt tragen.
    """
    sb = (ROOT / "scripts" / "stundenblume.py").read_text(encoding="utf-8")
    dc = (ROOT / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
    assert "def tagescheck_pruefen" in sb, "die Blumen bewachen den Tagescheck nicht"
    assert re.search(r"stundenblume\.py[\"']?\s+--pruefen", dc), \
        "der Tagescheck bewacht die Belegkette nicht — die Verschränkung ist einseitig"


def _das_verfahren_ist_abgelegt():
    """Ein Verfahren, das nur in einem Commit steht, ist beim nächsten Mal
    vergessen. Der Ablageweg-Grundsatz gilt auch für Verfahren."""
    doku = ROOT / "docs" / "blinde-flecken-verfahren.md"
    assert doku.exists(), "das Verfahren ist nirgends abgelegt"
    t = doku.read_text(encoding="utf-8")
    assert "ROLLE: blinde-flecken-verfahren" in t, "der Rollen-Marker fehlt"
    assert "Stichtag" in t and "überholt durch" in t, \
        "der Gültigkeits-Kopf fehlt — eine alte Fassung läse sich wie der gültige Stand"
    for frage in ("Was prüft er NICHT", "Wer trägt ihn", "im Text oder im Code"):
        assert frage in t, f"die Frage [{frage}] fehlt im Verfahren"


def _kein_gemischtes_anfuehrungspaar_in_zeichenketten():
    """Die Falle, die heute FÜNFMAL zugeschnappt ist — jetzt mit Prüfer.

    **Und beim Bauen dieses Prüfers habe ich zum zweiten Mal denselben Fehler
    gemacht: den Täter zu breit benannt.** Erst hieß es „liegt am Werkzeug",
    dann „liegt am deutschen Anführungszeichen". Beides war zu grob.

    Der Bruch entsteht ausschließlich beim **gemischten Paar**: ein
    typographisches `„` als Öffner und ein gerades `"` als Schließer — Letzteres
    beendet die Zeichenkette, und der Rest der Zeile hängt in der Luft. Ein
    sauber gesetztes Paar (`„…“`) ist völlig unbedenklich; bot.py enthält
    mehrere davon, und keines hat je etwas gebrochen.

    Der Prüfer meldet deshalb genau das Ungleichgewicht: einen Öffner ohne
    seinen typographischen Partner. Wäre er breiter, würde er dreimal am Tag
    grundlos anschlagen und wäre binnen einer Woche abgeschaltet.

    Docstrings sind ausgenommen — dort ist gutes Deutsch erwünscht und
    ungefährlich, weil die dreifachen Anführungszeichen anders schließen.
    """
    import io
    import tokenize
    treffer = []
    for datei in sorted((ROOT / "scripts").glob("*.py")) + [ROOT / "bot.py"]:
        if datei.name == Path(__file__).name:
            # **Selbstbezug, passend zum Thema:** Dieser Prüfer MUSS die
            # Zeichen enthalten, um nach ihnen zu suchen. Er nimmt sich aus —
            # und das ist keine Bequemlichkeit, sondern dieselbe Einsicht wie
            # bei Connis Fund: Was ein Prüfer trägt, kann er nicht prüfen.
            continue
        quelle = datei.read_text(encoding="utf-8")
        try:
            marken = list(tokenize.generate_tokens(io.StringIO(quelle).readline))
        except (tokenize.TokenError, IndentationError, SyntaxError):
            continue                       # zerbrochene Datei: Sache des Syntaxlaufs
        for mark in marken:
            if mark.type != tokenize.STRING:
                continue
            roh = mark.string
            if roh.lstrip("rbfuRBFU").startswith(('"""', "'''")):
                continue                   # Docstring: gutes Deutsch erwünscht
            if roh.count("„") != roh.count("“"):
                treffer.append(f"{datei.name}:{mark.start[0]}")
    assert not treffer, (
        "gemischtes Anfuehrungspaar in einer Zeichenkette - ein typographischer "
        "Oeffner ohne seinen Partner. Sobald der Schliesser ein gerades "
        "Anfuehrungszeichen ist, bricht die Datei. Paarweise setzen oder "
        "eckige Klammern nehmen: " + ", ".join(treffer[:8]))


check("kein gemischtes Anfuehrungspaar in Zeichenketten (5x gebrochen)",
      _kein_gemischtes_anfuehrungspaar_in_zeichenketten)
check("die Zeitgeber-Suche ist keine Positivliste (Frage ③)",
      _zeitgeber_suche_ist_keine_positivliste)
check("beide Register-Auswerter melden ihre blinden Flecken (Frage ①)",
      _jeder_waechter_meldet_seine_blinden_flecken)
check("kein Träger ohne Wache — Verschränkung beidseitig (Frage ②)",
      _kein_traeger_ohne_wache)
check("das Verfahren ist abgelegt und trägt den Gültigkeits-Kopf",
      _das_verfahren_ist_abgelegt)

print()
if fails:
    print(f"❌ {len(fails)} B6-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle B6-Blinde-Flecken-Tests bestanden.")
