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
import os
import re
import sys
import tokenize
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
    except Exception as e:
        # **Auch eine Ausnahme ist ein Befund, kein Abbruchgrund.** Bricht der
        # Laeufer hier ab, laufen die NACHFOLGENDEN Pruefungen nicht mehr - und
        # ihre Befunde gehen still verloren. Dieselbe Klasse wie der Tagescheck,
        # der am 29.07. mitten im Lauf starb und alles Gemessene mitnahm.
        print(f"✗ {name}: {type(e).__name__}: {e}")
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
    """**Frage 2 — wer prueft den Traeger?**

    Der 4-Uhr-Check traegt die Zeitgeber-Wache und laeuft selbst ueber einen
    Zeitgeber. Die Stundenblumen laufen ueber einen eigenen - nur deshalb kann
    die Verschraenkung ueberhaupt tragen.

    **KORRIGIERT 18.08.2026 (Connis Auflage 3).** Der erste Entwurf suchte nur,
    ob `def tagescheck_pruefen` im TEXT vorkommt. Eine Gegenpruefung hat den
    AUFRUF ersatzlos entfernt und eine Kommentarzeile stehen lassen - der
    Pruefer blieb gruen, die Wache war tot. Und genau das ist keine Theorie: Der
    Tagescheck war zu diesem Zeitpunkt seit 21 Tagen tot, ohne dass irgendetwas
    anschlug.

    Jetzt wird die Wache AUSGEFUEHRT, gegen ein kuenstlich gealtertes Protokoll.
    """
    import importlib.util
    import tempfile
    import time

    spec = importlib.util.spec_from_file_location(
        "sb_probe", ROOT / "scripts" / "stundenblume.py")
    sb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sb)

    heim = Path(tempfile.mkdtemp(prefix="wache-"))
    log = heim / "daily-check.log"
    alt = getattr(sb, "TAGESCHECK_LOG", None)
    assert alt is not None, "die Wache kennt kein Tagescheck-Protokoll"
    try:
        sb.TAGESCHECK_LOG = log

        # (a) Frisches Protokoll -> Ruhe.
        log.write_text("ok", encoding="utf-8")
        assert not sb.tagescheck_pruefen(), \
            "die Wache meldet, obwohl der Tagescheck frisch gelaufen ist"

        # (b) 27 Stunden alt -> Alarm. DAS ist der reale Fall vom 29.07.
        alt_zeit = time.time() - 27 * 3600
        os.utime(log, (alt_zeit, alt_zeit))
        befund = sb.tagescheck_pruefen()
        assert befund, "ein 27 Stunden stiller Tagescheck bleibt unbemerkt"

        # (c) Gar kein Protokoll -> ebenfalls Alarm. Ein fehlender Traeger ist
        #     kein Ruhezustand.
        log.unlink()
        assert sb.tagescheck_pruefen(), "ein fehlendes Protokoll gilt als in Ordnung"
    finally:
        sb.TAGESCHECK_LOG = alt

    # Die Rueckrichtung bleibt eine Textpruefung - sie liegt in einem
    # Shell-Skript, das sich hier nicht sinnvoll ausfuehren laesst. Der
    # Zielumgebungs-Pruefer startet es dafuer mit env -i.
    dc = (ROOT / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
    assert re.search(r"stundenblume\.py[\"']?\s+--pruefen", dc), \
        "der Tagescheck bewacht die Belegkette nicht - die Verschraenkung ist einseitig"


def _kostenzahl_nie_ohne_das_wort_nennwert():
    """Connis Auflage vom 28.07. abends — in die Doku, nicht nur in den Bericht.

    `total_cost_usd` ist der Listenpreis, den dieselbe Arbeit über die API
    gekostet hätte. **Über vierzehn Tage summiert er sich auf gut 3400 Dollar,
    von denen nie einer abgebucht wurde** — wir laufen über das Abo. Ohne das
    Wort „Nennwert" daneben liest sich diese Zahl wie eine Rechnung, und sie
    wird irgendwann jemanden zu Recht erschrecken.

    Geprüft wird nur, wo die Zahl **ausgegeben** wird. Dass sie intern
    aufsummiert wird, ist unbedenklich — gefährlich ist erst der Blick darauf.
    """
    quelle = (ROOT / "bot.py").read_text(encoding="utf-8").splitlines()
    treffer = []
    for i, zeile in enumerate(quelle):
        if 'cost_usd' not in zeile or zeile.lstrip().startswith("#"):
            continue
        if "get(" not in zeile:
            continue                       # kein Auslesen zur Anzeige
        # **Das Fenster geht in BEIDE Richtungen.** Der erste Entwurf schaute
        # nur nach unten und verfehlte damit genau die Stelle, an der die
        # Klarstellung hingehört: Ein erklärender Kommentar steht per
        # Konvention ÜBER der Zeile, die er erklärt.
        umfeld = "\n".join(quelle[max(0, i - 12):i + 25])
        # Schreibweise offenlassen: Ein Prüfer, der auf „Nennwert" besteht und
        # „NENNWERT" ablehnt, verlangt eine Formatierung statt der Sache — und
        # genau daran ist er beim ersten Lauf hängengeblieben.
        if "nennwert" not in umfeld.lower():
            treffer.append(str(i + 1))
    assert not treffer, (
        "eine Kostenzahl wird ohne das Wort Nennwert angezeigt - im Abo wird "
        "nichts davon berechnet, und ueber vierzehn Tage sind es 3400 Dollar. "
        "Zeilen: " + ", ".join(treffer))


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


# **Welche Token-Arten Text tragen — und warum das eine Menge sein MUSS.**
#
# **Gemessen am 25.08., nachdem Engywuck 51/54 sah und ich 54/54:** Bis
# Python 3.11 war ein f-String **ein** `STRING`-Token. Seit 3.12 (PEP 701)
# zerlegt `tokenize` ihn — der Textinhalt landet in `FSTRING_MIDDLE`, und
# nur die inneren Ausdruecke bleiben `STRING`. Ein Pruefer, der allein auf
# `tokenize.STRING` sieht, ist auf 3.12 **blind fuer jeden f-String**.
#
# Damit sah dieselbe Pruefzeile auf zwei Maschinen zwei verschiedene Mengen:
# vier Treffer auf 3.11, null auf 3.12. **Ein Pruefraum, der je nach Umgebung
# still schrumpft** — genau die Krankheit, die dieses Projekt an anderer
# Stelle [Achsenraum] genannt hat, hier eine Ebene hoeher.
#
# `getattr` statt fester Namen, weil die Konstante auf 3.11 nicht existiert.
# Auf 3.11 gibt es diese Arten nicht; dort ist ein f-String EIN STRING-Token
# und der Zweig unten greift. `-1` trifft nie, weil Token-Arten nie negativ
# sind — damit haelt derselbe Code auf beiden Versionen.
_F_START = getattr(tokenize, "FSTRING_START", -1)
_F_MITTE = getattr(tokenize, "FSTRING_MIDDLE", -1)
_F_ENDE = getattr(tokenize, "FSTRING_END", -1)


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
        # **Ein f-String wird als GANZES geprueft, nicht je Fragment.**
        #
        # **Engywucks Gegenpruefung, 25.08., 05:31 — und sie widerlegt meine
        # eigene Zahl von vor zwei Stunden:** Der erste Fix sah `FSTRING_MIDDLE`
        # an und meldete siebzig Stellen. **Fuenf davon waren echt.** Denn wenn
        # der f-String zerfaellt, zerfaellt auch ein **korrektes** Paar:
        #
        #     f'Haus „{titel}“ erkannt'
        #       FSTRING_MIDDLE  'Haus „'     -> Oeffner ohne Schliesser
        #       FSTRING_MIDDLE  '“ erkannt'  -> Schliesser ohne Oeffner
        #
        # Beide Haelften wurden angeschwaerzt: 64 Fehlalarme auf 32 Zeilen,
        # **jede doppelt gemeldet**. Das Doppel-Muster stand woertlich in der
        # eigenen Ausgabe (`hora.py:628, hora.py:628`) — gesehen, nicht gedeutet.
        #
        # **Dieselbe Lehre wie im Zerleger von mailtext.py, andere Stelle:
        # ein Fragment bildet Verschachtelung nicht ab.** Deshalb hier
        # derselbe Griff — ein Stapel, kein Flag: f-Strings duerfen ineinander
        # stehen, und ein Flag koennte das nicht.
        stapel: list[list] = []
        for mark in marken:
            if mark.type == _F_START:
                stapel.append([mark.start[0], []])
                continue
            if mark.type == _F_MITTE and stapel:
                stapel[-1][1].append(mark.string)
                continue
            if mark.type == _F_ENDE and stapel:
                zeile, stuecke = stapel.pop()
                ganz = "".join(stuecke)
                if ganz.count("„") != ganz.count("“"):
                    treffer.append(f"{datei.name}:{zeile}")
                continue
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
        # **Die Gesamtzahl gehoert VOR die Liste** (Adam, 25.08.): Die Meldung
        # zeigte acht Stellen und verschwieg, dass es siebzig waren — und weil
        # `bot.py` hinten in der Dateiliste steht, waren die 52 Stellen dort
        # nie zu sehen. **Eine stille Kappung liest sich wie Vollstaendigkeit.**
        f"eckige Klammern nehmen. {len(treffer)} Stelle(n), davon "
        + ", ".join(sorted({t.split(":")[0] for t in treffer}))
        + " — die ersten acht: " + ", ".join(treffer[:8]))


check("kein gemischtes Anfuehrungspaar in Zeichenketten (5x gebrochen)",
      _kein_gemischtes_anfuehrungspaar_in_zeichenketten)
check("die Zeitgeber-Suche ist keine Positivliste (Frage ③)",
      _zeitgeber_suche_ist_keine_positivliste)
check("beide Register-Auswerter melden ihre blinden Flecken (Frage ①)",
      _jeder_waechter_meldet_seine_blinden_flecken)
check("kein Träger ohne Wache — Verschränkung beidseitig (Frage ②)",
      _kein_traeger_ohne_wache)
check("Kostenzahl nie ohne das Wort Nennwert (Conni 28.07.)",
      _kostenzahl_nie_ohne_das_wort_nennwert)
check("das Verfahren ist abgelegt und trägt den Gültigkeits-Kopf",
      _das_verfahren_ist_abgelegt)

print()
if fails:
    print(f"❌ {len(fails)} B6-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)


def _zeitgeber_wache_klagt_keinen_laufenden_an():
    """**Der Fehlalarm vom 19.08. — Selbstbezug, gemessen im Echtbetrieb.**

    Der erste automatische Tagescheck nach der Reparatur klagte seinen EIGENEN
    Zeitgeber an: „aktiv, hat aber KEINEN naechsten Lauf geplant". systemd
    fuehrt einen Timer, dessen Dienst laeuft, im SubState `running` — und dort
    gibt es kein NextElapse. Der Tagescheck prueft sich aber genau waehrend
    seines eigenen Laufs; er ist der einzige Timer, der sich in diesem Zustand
    selbst sieht.

    Ein taeglicher Fehlalarm auf den Waechter, der alle anderen prueft. Und
    Fehlalarme schalten Waechter zuverlaessiger ab als Defekte.
    """
    dc = (ROOT / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
    # **Keine willkuerliche Zeichenzahl.** Der erste Entwurf nahm die ersten
    # 4000 Zeichen ab der Ueberschrift und verfehlte die gesuchte Stelle um gut
    # siebzig Zeilen - die Kommentare in diesem Projekt sind lang. Geschnitten
    # wird bis zum naechsten Abschnitt, also an einer echten Grenze.
    block = dc.split("ZEITGEBER-WACHE")[1].split("# --- 9b.")[0]
    # **Kommentarzeilen zaehlen NICHT — und das war beim ersten Anlauf prompt
    # der Fehler.** Die Gegenprobe entfernte den Code und liess den
    # Erklaerkommentar stehen; der Pruefer blieb gruen, weil dort dieselben
    # Woerter stehen. Dritter Fall dieser Klasse an zwei Tagen: Ein Pruefer, der
    # die Beschreibung seines Gegenstands trifft, prueft die Beschreibung.
    code = "\n".join(z for z in block.splitlines()
                     if not z.lstrip().startswith("#"))
    assert "SubState" in code and 'substate' in code, (
        "die Wache prueft nicht AUSFUEHRBAR, ob der Dienst gerade laeuft — "
        "sie klagt dann ihren eigenen Traeger an")
    assert '"running"' in code or "'running'" in code, (
        "der laufende Zustand wird nirgends im Code abgefragt")
    # Befund B4 der Gegenpruefung, im selben Zug: monotone Zeitgeber tragen
    # ihren naechsten Lauf in einem anderen Feld.
    assert "NextElapseUSecMonotonic" in code, (
        "monotone Zeitgeber (OnBootSec/OnUnitActiveSec) werden angeklagt, "
        "obwohl sie gesund sind — ihre Realzeit-Angabe ist immer leer")


check("Zeitgeber-Wache klagt keinen laufenden an (Fehlalarm 19.08.)",
      _zeitgeber_wache_klagt_keinen_laufenden_an)

if fails:
    print(f"\n❌ {len(fails)} B6-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    raise SystemExit(1)
print("\nAlle B6-Blinde-Flecken-Tests bestanden.")
