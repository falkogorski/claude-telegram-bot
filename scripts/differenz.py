#!/usr/bin/env python3
# <!-- ROLLE: differenzmesser -->
"""Der Differenzmesser — **Mengen statt Aufzählungen.**

**Die Diagnose in einem Satz** (Engywucks Studie, 23.08., 15 Agenten): Die
Ablage ist eine zweite, handgepflegte Kopie von Tatsachen, die im Code schon
stehen — und jede handgepflegte Kopie driftet. Deshalb hilft nicht „besser
pflegen", sondern **weniger Kopien**: ableiten, was ableitbar ist.

Gemessen: 84 Posten, 45 davon Aufzählungen, wo eine Menge hingehört.

**Das Lehrstück steht im Selbstcheck selbst.** `_c_register_vollstaendig` hat
zwei Hälften: Der Skript-Teil bildet eine Menge (alles in `scripts/`, außer
`test_*`) — der ist in Ordnung. Der Modul-Teil war eine fest verdrahtete
Siebenerliste und erfasste sieben von achtzehn. Dass er einmal `ampel.py`
„fand", lag daran, dass `ampel.py` **darin stand**. Genau dieser Satz wurde
jahrelang als Beleg für die Mengen-Regel weitergereicht.

## Die Bauart, und warum sie so ist

Jede Differenzart ist eine Funktion mit der Namensendung `_differenz`. Der
Sammler findet sie über den **eigenen Syntaxbaum** — es gibt keine Stelle, an
der man eine neue eintragen müsste, und keine, an der man sie vergessen kann.
*Ein Modul, das Aufzählungen abschaffen soll, darf nicht selbst mit einer
anfangen.*

Jede Art liefert drei Dinge, **alle drei Pflicht**:

1. die **Differenzmenge** — nie Mitgliedschaft, nie Textsuche nach einem Namen
2. eine **Härte** (`bricht` / `meldet`) — Pflichtfeld, damit Art Nummer sieben
   nicht stillschweigend auf „folgenlos" fällt
3. eine **Gegenprobe**: `<name>_gegenprobe`, die die Lücke künstlich erzeugt.
   **Fehlt sie, weigert sich der Sammler, die Art zu laden.**

Punkt 3 ist die einzige geduldete Prüfung über den Prüfer — und sie ist keine:
eine **Ladebedingung**, kein Lauf.

## Wo das läuft, und warum dort

Gerufen vom Selbstcheck in `bot.py`. Der läuft bei **jedem Bot-Start auf dem
VPS**, im Start-Wächter, im Regressionslauf und über den Tagescheck um vier.
**Die Messung findet damit in der Zielumgebung statt** — am Mac erzeugte
Mengen messen weniger, als sie behaupten (dieselbe Klasse wie der
`$HOME`-Fehler vom 29.07., der einen Wächter einundzwanzig Tage tötete).

**Kein neuer Wächter, kein Zeitgeber, keine neue Ablage, kein Modellaufruf,
kein Netz, keine Kostenquelle.** Ein bestehender Wächter war erweiterbar —
damit ist der Nachweis der Kurs-Regel geführt.
"""
from __future__ import annotations

import ast
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent

# Härtegrade. Ein Pflichtfeld, keine Vorgabe: Wer eine Art hinzufügt, muss sich
# entscheiden.
#
# **Das Kriterium ist kein Geschmacksurteil** (Engywuck, 23.08.):
#
#   BRICHT, wenn etwas WIRKENDES ungeschützt ist.
#   MELDET, wenn etwas UNWIRKSAMES herumliegt.
#
# Am Beispiel derselben zwei Mengen: Ein **Modul ohne Registerzeile** ist
# unsichtbar für 8.1 und 8.2 — es wirkt und niemand prüft es → `bricht`. Eine
# **Registerzeile ohne Modul** führt einen Leser in die Irre, bricht aber nichts
# → `meldet`.
#
# **Der Ausgang für `meldet` muss stehen, BEVOR die erste Art ihn nutzt.** Bis
# zum 23.08. prüfte der Selbstcheck nur `BRICHT`; eine `MELDET`-Differenz wurde
# berechnet und fallen gelassen. Das Feld wäre eine Attrappe gewesen, sobald es
# jemand benutzt hätte — gefunden hat es Engywuck, gefragt hatte ich danach.
BRICHT = "bricht"
MELDET = "meldet"


@dataclass
class Befund:
    """Das Ergebnis einer Differenzart."""
    fehlend: set[str]
    haerte: str
    was: str                       # eine Zeile: was fehlt hier eigentlich
    hinweis: str = ""              # was zu tun ist
    zusatz: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.haerte not in (BRICHT, MELDET):
            raise ValueError(f"Härte fehlt oder ist unbekannt: {self.haerte!r}")


# --------------------------------------------------------------------------
# Differenzart D — kopierbare Kosten-Zuweisungen in der Ablage
# --------------------------------------------------------------------------

_KOSTEN_ZUWEISUNG = re.compile(
    r"ANTHROPIC_API_KEY\s*=\s*\S"          # Zuweisung MIT Wert
    r"|<key>\s*ANTHROPIC_API_KEY\s*</key>"  # plist/XML-Schluessel
)


def _kopierbare_zuweisungen() -> set[str]:
    """Fundstellen, an denen die Ablage einen kostenpflichtigen Schluessel SETZT.

    **Die Menge ist `git ls-files`, nicht `*.md`** — und das ist der Kern.
    Engywucks Befund nannte zehn Doku-Stellen; die schaerfste stand in
    `com.user.claude-telegram-bot.plist.example` und fehlte, **weil seine Menge
    Doku-Dateien war**. Eine Vorlagendatei ist nicht bloss kopierbar, sie ist
    zum Kopieren gemacht. Dieselbe Mengen-Lehre, angewandt auf den Befund, der
    sie formuliert hat.

    **Die trennende Eigenschaft ist Kopierbarkeit, nicht die Zeichenkette.**
    In Markdown zaehlt eine Zuweisung nur **innerhalb eines eingezaeunten
    Codeblocks** — sonst schluege diese Art auf ihrem eigenen Bauauftrag an,
    der die Gefahr im Fliesstext beschreibt, und waere binnen einer Woche
    abgeschaltet. Ausserhalb von Markdown zaehlt sie ueberall: eine `.plist`,
    ein Skript, eine Umgebungsvorlage haben keinen Fliesstext.

    Erwaehnungen ohne Wert (`ANTHROPIC_API_KEY bewusst NICHT gesetzt`) fallen
    heraus, weil das Muster ein Zeichen HINTER dem Gleichheitszeichen verlangt.
    """
    import subprocess
    try:
        aus = subprocess.run(["git", "-C", str(WURZEL), "ls-files"],
                             capture_output=True, text=True, timeout=20)
    except Exception:
        return set()
    treffer: set[str] = set()
    for name in aus.stdout.split("\n"):
        if not name:
            continue
        datei = WURZEL / name
        try:
            text = datei.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue                      # Binaerdatei oder weg — nichts zu lesen
        markdown = name.endswith(".md")
        im_zaun = False
        for nr, zeile in enumerate(text.split("\n"), 1):
            if markdown and zeile.lstrip().startswith("```"):
                im_zaun = not im_zaun
                continue
            if markdown and not im_zaun:
                continue                  # Fliesstext beschreibt, er fuehrt nicht aus
            if _KOSTEN_ZUWEISUNG.search(zeile):
                treffer.add(f"{name}:{nr}")
    return treffer


def kostenzuweisung_differenz(*, ist: set[str] | None = None,
                              soll: set[str] | None = None) -> Befund:
    """Keine versionierte Datei darf einen kostenpflichtigen Schluessel SETZEN.

    **Anlass (24.08.2026):** `MIGRATION-DREHBUCH-ARCHIV.md` trug sechs Zeilen
    ausfuehrbare Shell, die `ANTHROPIC_API_KEY` in zwei `.env`-Dateien
    schrieben, und die Plist-Vorlage setzte ihn als Umgebungsvariable.
    **Ablegen entschaerft keine Befehle** — ungepflegt und unwirksam sind zwei
    verschiedene Dinge, und der Grund, warum niemand hinsah, stand im
    Dateinamen.

    **Ehrlich zur Reichweite** (Engywucks eigene Einschraenkung): Mechanisch
    fassbar ist nur die **Zuweisung**. Die Prosa — [den Key ersetzen],
    [gleicher Key wie lokal] — ist es nicht; dafuer gaebe es keine Regel ohne
    Urteil, und eine Heuristik schluege auf den korrekten Warn-Stellen an. Die
    Prosa wurde am 24.08. von Hand bereinigt und **bleibt der ungeschuetzte
    Rest**. Das gehoert in den Befund geschrieben, nicht weggeheuristikt.

    Anmerkung zum Feldnamen: `fehlend` heisst hier **ueberzaehlig** — gesucht
    wird, was nicht da sein darf. Das Soll ist die leere Menge.
    """
    if ist is None:
        ist = _kopierbare_zuweisungen()
    if soll is None:
        soll = set()
    return Befund(
        fehlend=ist - soll,
        haerte=BRICHT,
        was="ausfuehrbare Stellen, die einen kostenpflichtigen API-Schluessel setzen",
        hinweis=("Auf den Abo-Weg umstellen: `claude setup-token` erzeugt den "
                 "Wert fuer CLAUDE_CODE_OAUTH_TOKEN. Ein ANTHROPIC_API_KEY "
                 "bucht getrennt vom Abo ab und hat im SDK sogar Vorrang. In "
                 "Archiven den Block entschaerfen statt ihn stehenzulassen."),
    )


def kostenzuweisung_differenz_gegenprobe() -> None:
    """Die Luecke kuenstlich erzeugen — die Art MUSS sie finden."""
    b = kostenzuweisung_differenz(ist={"archiv.md:37"}, soll=set())
    assert b.fehlend == {"archiv.md:37"}, f"die Art findet die Luecke nicht: {b.fehlend}"
    leer = kostenzuweisung_differenz(ist=set(), soll=set())
    assert not leer.fehlend, "die Art meldet ohne Luecke"


# --------------------------------------------------------------------------
# Differenzart A — Wurzelmodule gegen Register
# --------------------------------------------------------------------------

def module_differenz(*, ist: set[str] | None = None,
                     soll: set[str] | None = None) -> Befund:
    """Jedes eigene Wurzelmodul braucht eine **Tabellenzeile** im Register.

    **Ist** kommt aus `git ls-files` statt aus einem Endungsmuster. Das ist
    nicht Geschmack: Es heilt zugleich die Mac/VPS-Divergenz bei ignorierten
    Dateien — was nicht versioniert ist, existiert für die andere Seite nicht.

    **Soll ist eine Tabellenzeile, nicht eine Erwähnung.** Der bisherige Prüfer
    maß `name not in inhalt`; damit genügte ihm eine Nennung in einem
    Warnsatz. Ein Modul, das nur in einer Fußnote vorkommt, hat keinen
    Register-Eintrag — es hat eine Erwähnung.

    Diese Art **findet am Bautag nichts**, und das ist kein Mangel, sondern der
    Normalzustand eines Riegels: Alle achtzehn Module stehen heute im Register,
    durch Disziplin. Sie schützt Modul Nummer neunzehn.
    """
    if ist is None:
        ist = _versionierte_wurzelmodule()
    if soll is None:
        soll = _register_tabellenzeilen()
    return Befund(
        fehlend=ist - soll,
        haerte=BRICHT,
        was="Wurzelmodule ohne Tabellenzeile in ABHAENGIGKEITEN.md",
        hinweis=("Eine Zeile je Modul anlegen: | **Name** (Datei): … | warum | "
                 "Prüfbefehl |. Eine blosse Erwaehnung im Fliesstext genuegt "
                 "nicht — sie traegt weder Grund noch Pruefweg."),
    )


def module_differenz_gegenprobe() -> None:
    """Die Lücke künstlich erzeugen — die Art MUSS sie finden."""
    b = module_differenz(ist={"neu.py", "alt.py"}, soll={"alt.py"})
    assert b.fehlend == {"neu.py"}, f"die Art findet die Luecke nicht: {b.fehlend}"
    # Und die Gegenrichtung: keine Lücke, kein Befund.
    leer = module_differenz(ist={"alt.py"}, soll={"alt.py"})
    assert not leer.fehlend, "die Art meldet ohne Luecke"


def registerleichen_differenz(*, ist: set[str] | None = None,
                              soll: set[str] | None = None) -> Befund:
    """Die **andere Richtung**: eine Registerzeile für ein Modul, das es nicht
    mehr gibt.

    `[NEU 31.08., F-15 — Engywucks eigener Fund]` Differenzart A misst
    `ist - soll`: jedes Modul braucht eine Zeile. Sie kann eine **Karteileiche**
    nicht sehen — eine Zeile, deren Datei längst gelöscht ist. **Das ist genau
    die Richtung, mit der Adam angefangen hat** (Auftrag gegen Karteileichen).

    **Härte `MELDET`, nicht `BRICHT`**, nach dem Kriterium dieses Moduls:
    *bricht, wenn etwas Wirkendes ungeschützt ist; meldet, wenn etwas
    Unwirksames herumliegt.* Eine Registerzeile ohne Datei führt einen Leser in
    die Irre — sie bricht nichts.

    **Die Vorbedingung war zu prüfen und ist erfüllt:** Der `MELDET`-Ausgang
    steht seit dem 23.08. im Selbstcheck. Vorher wurde eine `MELDET`-Differenz
    berechnet und **fallen gelassen**; diese Art wäre als erste ihrer Sorte
    sofort eine Attrappe gewesen.

    **Die Ist-Menge ist hier eine andere als bei Art A** — dort nur die
    Wurzelmodule, hier **jede versionierte `.py`**, denn das Register nennt
    auch Prüfer und Betriebsskripte. Wer beide Mengen gleichsetzt, meldet
    fünfzig Skripte als Leichen.
    """
    if ist is None:
        ist = _alle_versionierten_pythondateien()
    if soll is None:
        soll = _register_tabellenzeilen()
    return Befund(
        fehlend=soll - ist,
        haerte=MELDET,
        was="Registerzeilen für Dateien, die es nicht (mehr) gibt",
        hinweis=("Zeile entfernen oder den Namen berichtigen. Ein Register, das "
                 "Verschwundenes fuehrt, kostet beim Lesen mehr als es nuetzt."),
    )


def registerleichen_differenz_gegenprobe() -> None:
    """Die Leiche kuenstlich erzeugen — die Art MUSS sie finden."""
    b = registerleichen_differenz(ist={"da.py"}, soll={"da.py", "weg.py"})
    assert b.fehlend == {"weg.py"}, f"die Art findet die Leiche nicht: {b.fehlend}"
    assert b.haerte == MELDET, "eine Leiche bricht nichts — sie meldet"
    # Gegenrichtung: keine Leiche, kein Befund. Ohne diese Zeile waere alles
    # oben mit einem [melde immer alles] zu erfuellen.
    leer = registerleichen_differenz(ist={"da.py"}, soll={"da.py"})
    assert not leer.fehlend, "die Art meldet ohne Leiche"
    # Und sie darf NICHT die Richtung von Art A messen: ein Modul ohne Zeile
    # ist ihr Fall nicht.
    andere = registerleichen_differenz(ist={"da.py", "ohne_zeile.py"}, soll={"da.py"})
    assert not andere.fehlend, "die Art misst die Richtung von Art A mit"


def _alle_versionierten_pythondateien() -> set[str]:
    """Jede versionierte `.py` im Repo, nur der Dateiname.

    Bewusst **alle**, nicht nur die Wurzel: Das Register fuehrt auch Pruefer
    und Betriebsskripte in seiner ersten Spalte.
    """
    import subprocess
    try:
        aus = subprocess.run(["git", "-C", str(WURZEL), "ls-files", "*.py"],
                             capture_output=True, text=True, timeout=20)
    except Exception:
        return set()
    return {Path(z).name for z in aus.stdout.split()}


def _versionierte_wurzelmodule() -> set[str]:
    import subprocess
    try:
        aus = subprocess.run(["git", "-C", str(WURZEL), "ls-files", "*.py"],
                             capture_output=True, text=True, timeout=20)
    except Exception:
        return set()
    return {z for z in aus.stdout.split()
            if "/" not in z and not z.startswith("test_") and z != "bot.py"}


# Eine Tabellenzeile beginnt mit `|` und trägt den Dateinamen in der ERSTEN
# Spalte. Eine Erwähnung im Fließtext tut das nicht.
_TABELLENZEILE = re.compile(r"^\s*\|([^|]*)\|", re.M)


def _register_tabellenzeilen() -> set[str]:
    register = WURZEL / "ABHAENGIGKEITEN.md"
    if not register.exists():
        return set()                       # anderswo ausgecheckt — kein Befund
    inhalt = register.read_text(encoding="utf-8")
    gefunden = set()
    for erste_spalte in _TABELLENZEILE.findall(inhalt):
        gefunden |= set(re.findall(r"[\w./-]+\.py", erste_spalte))
    return {Path(g).name for g in gefunden}


# --------------------------------------------------------------------------
# Differenzart B — Zustandsablagen gegen die Wegwerf-Umgebung des Läufers
# --------------------------------------------------------------------------

def ablagen_differenz(*, ist: set[str] | None = None,
                      soll: set[str] | None = None) -> Befund:
    """Jede umbiegbare Zustandsablage muss im Regressionsläufer verriegelt sein.

    **Der einzige Punkt mit Schaden nach aussen** — Prüfläufe schreiben sonst
    in Adams echte Ablagen. Belegt: am 26.07. eine Testmeldung als echte
    Nachricht, am 20.08. ein Prüf-Eintrag im echten Auftragsbuch, am 23.08.
    drei falsche Kanal-Kennungen in der echten `prefs.json`.

    **Die Ist-Menge wird NICHT über die Endung gebildet**, und das ist die
    Korrektur an meiner eigenen Fassung vom selben Tag: `scripts/test_hermetik.py`
    suchte Schlüssel mit Endung `_DIR` oder `_FILE`. Das ist eine Aufzählung
    mit Regex-Anstrich — sie verfehlte `AMPEL_RULES_PATH`, `AMPEL_STATE_PATH`,
    `AMPEL_CUSTOM_PATH`, `AMPEL_LOG_PATH` und `PRESEND_LOG_PATH`.

    **Ausgerechnet die Ampel**, die laut `CLAUDE.md` das Heikelste im Projekt
    führt (Klienten-Namen, ausdrücklich cloud-frei zu pflegen). Ein Prüflauf
    hätte ihre Regeldatei überschreiben können, und niemand hätte es gemessen.

    Ist ist deshalb: **jeder Umgebungsschlüssel, aus dem ein Produktivmodul
    einen Pfad bildet** — erkannt daran, dass der gelesene Wert in einem
    `Path(...)`-Ausdruck landet oder der Rückfall ein Pfad ist.
    """
    if ist is None:
        ist = _zustandsschluessel()
    if soll is None:
        soll = _laeufer_verriegelt()
    return Befund(
        fehlend=ist - soll - set(GEWOLLT_OFFEN),
        haerte=BRICHT,
        was="Zustandsablagen ohne Riegel in scripts/regressionstest.sh",
        hinweis=("Als `export NAME=\"$PRUEFHEIM/...\"` eintragen — oder mit "
                 "Begruendung in GEWOLLT_OFFEN. Ein Lauf schreibt sonst in den "
                 "Betrieb, und zwar lautlos."),
    )


def ablagen_differenz_gegenprobe() -> None:
    b = ablagen_differenz(ist={"AMPEL_RULES_PATH", "POSTFACH_DIR"},
                          soll={"POSTFACH_DIR"})
    assert b.fehlend == {"AMPEL_RULES_PATH"}, \
        f"die Art findet die Luecke nicht: {b.fehlend}"
    leer = ablagen_differenz(ist={"POSTFACH_DIR"}, soll={"POSTFACH_DIR"})
    assert not leer.fehlend, "die Art meldet ohne Luecke"


# Ablagen, die absichtlich NICHT umgebogen werden — mit dem Grund daneben.
# Jeder Eintrag ist eine Entscheidung, kein Automatismus: Eine lange
# Ausnahmeliste höhlt den Riegel aus, genau wie bei den Stichwort-Filtern.
GEWOLLT_OFFEN = {
    "CLAUDE_MEMORY_DIR": "wird gezielt pro Aufruf gesetzt, nicht global — ein "
                         "Test muss das echte Gedaechtnis LESEN koennen",
    # Die drei folgenden sind LESEPFADE. Engywucks Kriterium für Schritt 2
    # lautet: „schreibt das Skript wirklich, oder liest es nur?" — was ein
    # Prüflauf nicht schreibt, kann er nicht beschädigen.
    "BOT_ENVFILE": "die geschuetzte Umgebungsdatei — wird nur GELESEN, und sie "
                   "gehoert root: ein Lauf als claudebot kommt gar nicht heran",
    "WHISPER_MODEL_PATH": "zeigt auf eine Modelldatei, die nur gelesen wird — "
                          "umgebogen fuende die Transkription ihr Modell nicht",
    "AUFTRAGSBUCH_RIEGEL": "ein KONFIGURATIONSDOKUMENT, das nur gelesen wird — "
                           "es traegt die Frist der Probewoche und wird von der "
                           "Kontrolle gesetzt, nie vom Code geschrieben. "
                           "Umgebogen zeigt es ins Leere, und ein Riegel, der "
                           "ins Leere zeigt, sperrt nichts (der Regressionslauf "
                           "hat genau das sofort gemeldet)",
    "CLAUDE_WORKDIR": "Adams Arbeitsverzeichnis. Im Pruflauf laeuft kein Agent, "
                      "der dort schriebe; umgebogen wuerden dagegen Pruefer "
                      "blind, die Pfade GEGEN das Arbeitsverzeichnis vergleichen "
                      "— genau der Fehler vom 23.08. (Befund F, meine eigene "
                      "Zeile blieb bei entferntem Schutz gruen)",
}

# Ein Schlüssel gilt als Zustandsablage, wenn der gelesene Wert in einem
# Pfad-Ausdruck landet. Gesucht wird im Syntaxbaum nach `os.environ.get(NAME)`
# innerhalb eines `Path(...)`-Aufrufs oder mit einem Pfad-artigen Rückfall.
_PFAD_MERKMAL = re.compile(r"[/\\]|\.json$|\.txt$|\.log$|\.md$")


def _zustandsschluessel() -> set[str]:
    raus: set[str] = set()
    for datei in _produktivmodule():
        try:
            baum = ast.parse(datei.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call):
                continue
            name = _environ_get_name(knoten)
            if name:
                raus.add(name) if _im_pfad_zusammenhang(baum, knoten) else None
    return raus


def _environ_get_name(knoten: ast.Call) -> str | None:
    """`os.environ.get("NAME")` → `"NAME"`, sonst None."""
    f = knoten.func
    if not (isinstance(f, ast.Attribute) and f.attr == "get"):
        return None
    ziel = f.value
    if not (isinstance(ziel, ast.Attribute) and ziel.attr == "environ"):
        return None
    if not knoten.args:
        return None
    erst = knoten.args[0]
    if isinstance(erst, ast.Constant) and isinstance(erst.value, str):
        return erst.value
    return None


def _im_pfad_zusammenhang(baum: ast.AST, ziel: ast.Call) -> bool:
    """Landet dieser Wert in einem Pfad? — am Baum, nicht am Text.

    Zwei Merkmale, beide genügen: Der Aufruf steckt in einem `Path(...)`, oder
    sein Rückfall (`or "..."`) sieht wie ein Pfad aus. Das zweite fängt die
    Ampel-Schlüssel, deren `Path(...)` eine Zeile weiter steht.
    """
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Call) and _ist_path_aufruf(knoten):
            if any(k is ziel for k in ast.walk(knoten)):
                return True
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.BoolOp) and isinstance(knoten.op, ast.Or):
            if not any(k is ziel for k in ast.walk(knoten.values[0])):
                continue
            for rest in knoten.values[1:]:
                if isinstance(rest, ast.Constant) and isinstance(rest.value, str):
                    # **Eine Adresse ist keine Ablage.** `CALDAV_URL` fiel im
                    # ersten Lauf hier herein, weil `https://…` Schrägstriche
                    # trägt. Ein Prüflauf kann eine URL nicht beschädigen.
                    if rest.value.startswith(("http://", "https://")):
                        return False
                    if _PFAD_MERKMAL.search(rest.value):
                        return True
                if isinstance(rest, ast.Call) and _ist_path_aufruf(rest):
                    return True
                if isinstance(rest, ast.JoinedStr):
                    return True
                # **Arithmetik ist keine Pfad-Verkettung.** `int(os.environ.get(
                # "ZUSTELL_TAKT_S") or 3 * 3600)` ist eine Zeitspanne. Der erste
                # Entwurf zählte jedes `BinOp` als Pfad und meldete drei
                # Zahlenwerte als Zustandsablagen — ein Prüfer, der grundlos
                # anschlägt, wird binnen einer Woche abgeschaltet.
                if isinstance(rest, ast.BinOp) and isinstance(rest.op, ast.Add):
                    linke = rest.left
                    if isinstance(linke, ast.Constant) and isinstance(linke.value, str):
                        return True
    return False


def _ist_path_aufruf(knoten: ast.Call) -> bool:
    f = knoten.func
    return ((isinstance(f, ast.Name) and f.id in ("Path", "str"))
            or (isinstance(f, ast.Attribute) and f.attr in ("Path", "joinpath")))


def _produktivmodule() -> list[Path]:
    """Eigene Module und Betriebsskripte — keine Prüfstände."""
    raus = [p for p in sorted(WURZEL.glob("*.py"))
            if not p.name.startswith("test_")]
    raus += [p for p in sorted((WURZEL / "scripts").glob("*.py"))
             if not p.name.startswith("test_") and p.name != "differenz.py"]
    return raus


_EXPORT = re.compile(r"^\s*export\s+([A-Z][A-Z0-9_]*)=", re.M)


def _laeufer_verriegelt() -> set[str]:
    laeufer = WURZEL / "scripts" / "regressionstest.sh"
    if not laeufer.exists():
        return set()
    return set(_EXPORT.findall(laeufer.read_text(encoding="utf-8")))


# --------------------------------------------------------------------------
# Differenzart C — Prüfer mit fest verdrahtetem Betriebspfad
# --------------------------------------------------------------------------

def festpfade_differenz(*, ist: set[str] | None = None,
                        soll: set[str] | None = None) -> Befund:
    """Kein Prüfer trägt einen Betriebspfad fest ein. **Soll ist leer.**

    Am 23.08. sind **vier** Prüfer aufgefallen, die den VPS-Pfad fest
    eingetragen hatten — darunter eine Zeile, die ich am selben Tag selbst
    geschrieben hatte. Solange die geprüfte Logik nur Zeichenketten verglich,
    waren sie pfadunabhängig grün; **die Blindheit entstand erst durch die
    Verbesserung** (Befund D/E: Pfade werden jetzt aufgelöst).

    **Die gefährliche Richtung ist nicht „rot am falschen Rechner", sondern
    „grün aus dem falschen Grund".** Meine F-Zeile blieb bei entferntem Schutz
    grün, weil `/home/claudebot` am Mac nicht das Arbeitsverzeichnis ist — auf
    dem VPS ist es genau das, dort wäre das Loch offen gewesen und der Prüfer
    still.

    Diese Art zog aus `scripts/test_hermetik.py` hierher um, damit es **eine**
    Quelle gibt statt zweier Stellen für dieselbe Frage.
    """
    if ist is None:
        ist = _feste_betriebspfade()
    return Befund(
        fehlend=ist - (soll or set()),
        haerte=BRICHT,
        was="Pruefer mit fest verdrahtetem Betriebspfad",
        hinweis=("bot._REPO_DIR bzw. bot.WORKDIR verwenden. Ein fester Pfad "
                 "macht den Pruefer ortsabhaengig — schlimmstenfalls gruen aus "
                 "dem falschen Grund."),
    )


def festpfade_differenz_gegenprobe() -> None:
    b = festpfade_differenz(ist={"test_x.py:12 /home/claudebot"})
    assert b.fehlend, "die Art findet den festen Pfad nicht"
    leer = festpfade_differenz(ist=set())
    assert not leer.fehlend, "die Art meldet ohne Fund"


def _ist_ortsabhaengig(wert: str) -> bool:
    """Nur die zwei Formen, die tatsächlich gebrochen sind — nicht jeder Pfad.

    **Warum so eng:** Der erste Entwurf schlug bei sieben Stellen an, davon
    **sechs berechtigt** — Textmuster-Werte für `_is_sensitive_ref`, wo ein
    fester Pfad genau der Testgegenstand ist. Eine davon war sogar ein
    **Docstring**: Der Prüfer stolperte über die Beschreibung seines eigenen
    Gegenstands, exakt der Fehler, den die Regel vom 22.08. benennt.

    Übrig bleiben die Repo-Wurzel (wird gegen `_REPO_DIR` aufgelöst) und das
    nackte Heimverzeichnis (dient als Stellvertreter für `WORKDIR`).
    """
    w = wert.rstrip("/")
    if w == "/home/claudebot":
        return True
    return "claude-telegram-bot" in w and (
        w.startswith("/home/claudebot") or w.startswith("~/"))


# Dateien, in denen ein fester Pfad der **Gegenstand** ist, nicht ein Fehler.
#
# **[BERICHTIGT 29.08., Engywucks Gegenprüfung (b)]** Hier stand
# `name.endswith(("test_hermetik.py", "differenz.py"))` — eine Endungsprüfung
# auf den **ganzen Pfad**. Sie trifft heute genau die zwei gewollten Dateien,
# aber `scripts/test_differenz.py` — der naheliegendste Name für einen Prüfer
# von `differenz.py` — fiele damit **still mit heraus**: *Der Prüfer seines
# eigenen Gegenstands wäre der erste, der verschwindet.*
#
# Verglichen wird deshalb der **Dateiname** gegen eine benannte Menge.
_EIGENER_GEGENSTAND = frozenset({"test_hermetik.py", "differenz.py"})


def _alle_python_dateien() -> list[Path]:
    """Alle versionierten `.py`-Dateien — als MENGE über eine Eigenschaft.

    **[BERICHTIGT 29.08., Engywucks Maschinen-Gleichstand, Fund ②]** Hier
    stand:

        sorted((WURZEL / "scripts").glob("test_*.py")) + [WURZEL / "bot.py"]

    Das erfasst 45 Prüfer und `bot.py` — **alle Betriebsskripte lagen
    außerhalb.** Gemessen ergab die Prüfart deshalb die **leere Menge**,
    während im Bestand drei echte Festpfade standen (`stundenblume.py:193`,
    `version_monitor.py:29` und `:299`). **Der Prüfer, der ortsabhängige
    Festpfade finden soll, konnte die einzigen echten nicht sehen.**

    Das ist die Mengen-Regel zum fünften Mal — und diesmal ausgerechnet in
    `differenz.py`, dem Werkzeug, das eigens gegen Aufzählungen gebaut wurde.
    *Jede Prüfung läuft über eine Menge, und es ist immer die, die dem
    Erbauer am Bautag einfiel.*

    `test_hermetik.py` bleibt ausgenommen: Dort **ist** ein fester Pfad der
    Testgegenstand.
    """
    import subprocess
    try:
        aus = subprocess.run(["git", "-C", str(WURZEL), "ls-files", "*.py"],
                             capture_output=True, text=True, timeout=20)
    except Exception as e:
        # **[BERICHTIGT 29.08., Engywucks Gegenprüfung (a)]** Hier stand
        # `return []`. Eine leere Dateimenge ergibt dieselbe Ausgabe wie ein
        # sauberer Bestand — **zwei identische Meldungen, zwei
        # entgegengesetzte Bedeutungen.** Genau die Form des Fehlers, gegen
        # den diese Datei gebaut ist: Der Prüfer misst nichts und meldet grün.
        #
        # Heute greift es nicht, weil Mac und VPS Git-Checkouts sind. Es
        # greift an dem Tag, an dem jemand aus einem Tarball ausrollt, in
        # einem Worktree misst oder `git` im Dienstpfad fehlt — und dann still.
        raise RuntimeError(
            f"Die Dateimenge konnte nicht gebildet werden ({e!r}). Das ist "
            "KEIN leeres Ergebnis: Es wurde nichts geprueft. Ein Bestand ohne "
            "Git-Verwaltung ist ein Befund, kein Bestehen.") from e
    dateien = []
    for name in aus.stdout.split("\n"):
        # `test_hermetik.py` und `differenz.py` bleiben draußen: Dort **ist**
        # ein fester Pfad der Testgegenstand. Beim ersten geweiteten Lauf
        # schlug die Prüfart sofort auf ihre eigenen Vergleichszeichenketten
        # an (`differenz.py:503` und `:506`) — **ein Prüfer, der über die
        # Beschreibung seines eigenen Gegenstands stolpert, wird binnen einer
        # Woche abgeschaltet.** Das ist wörtlich eine der beiden Regeln, die
        # `CLAUDE.md` für Prüfer aufstellt.
        if not name or Path(name).name in _EIGENER_GEGENSTAND:
            continue
        pfad = WURZEL / name
        if pfad.is_file():
            dateien.append(pfad)
    if not dateien:
        # Auch der zweite Weg in die leere Menge: `git` lief, lieferte aber
        # nichts (kein Checkout, leeres Verzeichnis, falsche Wurzel).
        raise RuntimeError(
            "Die Dateimenge ist leer — es gibt keine versionierte .py-Datei "
            "unter der Wurzel. Das ist ein Befund, kein Bestehen: Ein Pruefer "
            "ueber der leeren Menge besteht immer.")
    return sorted(dateien)


def _feste_betriebspfade() -> set[str]:
    """Über den **Syntaxbaum**, damit Kommentare und Docstrings draußen sind."""
    raus = set()
    dateien = _alle_python_dateien()
    for datei in dateien:
        try:
            baum = ast.parse(datei.read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            continue
        docstrings = set()
        for knoten in ast.walk(baum):
            if isinstance(knoten, (ast.Module, ast.FunctionDef,
                                   ast.AsyncFunctionDef, ast.ClassDef)):
                erste = (knoten.body or [None])[0]
                if (isinstance(erste, ast.Expr)
                        and isinstance(erste.value, ast.Constant)
                        and isinstance(erste.value.value, str)):
                    docstrings.add(id(erste.value))
        for knoten in ast.walk(baum):
            if (isinstance(knoten, ast.Constant)
                    and isinstance(knoten.value, str)
                    and id(knoten) not in docstrings
                    and _ist_ortsabhaengig(knoten.value)):
                raus.add(f"{datei.name}:{knoten.lineno} {knoten.value}")

    # **[GEWEITET 29.08., Engywucks Gegenprüfung (c)]** Der Fund lautete
    # „die Dateimenge ist zu eng" — `git ls-files "*.py"` weitet sie nur
    # **innerhalb einer Sprache.** Gemessen standen die festen Pfade auch in
    # Skripten und im Komponenten-Register.
    #
    # **Je Dateityp eine eigene Ableseart, weil der Syntaxbaum nur bei Python
    # trägt.** Das ist der Preis dafür, dass die Menge über eine Eigenschaft
    # entsteht statt über eine Sprache — und er ist niedriger, als die Lücke
    # es war.
    raus |= _feste_pfade_in_skripten()
    raus |= _feste_pfade_in_json()
    return raus


def _versionierte(muster: str) -> list[Path]:
    """Versionierte Dateien eines Musters — dieselbe Mengenbildung wie oben."""
    import subprocess
    try:
        aus = subprocess.run(["git", "-C", str(WURZEL), "ls-files", muster],
                             capture_output=True, text=True, timeout=20)
    except Exception as e:
        raise RuntimeError(
            f"Die Dateimenge fuer [{muster}] konnte nicht gebildet werden "
            f"({e!r}) — das ist ein Befund, kein leeres Ergebnis.") from e
    return [WURZEL / n for n in aus.stdout.split("\n")
            if n and (WURZEL / n).is_file()]


# Dateien, in denen ein VPS-Pfad **richtig** ist — je Eintrag eine Begründung.
#
# **Das ist eine Aufzählung, und hier ist sie die richtige Form.** Ob ein
# fester Pfad ein Fehler oder eine Absicht ist, kann kein Muster entscheiden:
# Es ist jedes Mal ein Urteil. Dieselbe Bauart wie die Ausnahmeliste der roten
# Worte — *jede Zeile darin ist eine Entscheidung, kein Automatismus.*
#
# **Sie bleibt kurz, sonst höhlt sie die Prüfart aus.** Wer hier etwas
# einträgt, schreibt den Grund dazu; ohne Grund gehört der Pfad begradigt.
_VPS_GEBUNDEN = {
    "daily_check.sh":
        "Läuft als systemd-Dienst auf dem VPS, als root — `$HOME` wäre dort "
        "`/root`, deshalb steht `BOTHOME` ausdrücklich fest (der Kommentar in "
        "der Datei begründet es). Auf dem Mac wird er nie aufgerufen.",
    "vps_backup.sh":
        "Läuft VOM Mac AUS gegen den VPS. Die Pfade sind die des ENTFERNTEN "
        "Rechners — ableiten hieße hier, auf den falschen zu zeigen.",
    "test_zielumgebung.sh":
        "Der Pfad ist ein ERKENNUNGSMERKMAL, kein Ablageort: `if [ -d … ]` "
        "prüft, ob wir überhaupt auf dem VPS stehen.",
    "components.json":
        "Register des Versions-Wächters, der ausschließlich auf dem VPS läuft "
        "(kein Zeitgeber auf dem Mac). Und er meldet einen toten Pfad LAUT "
        "(`Quelle nicht erreichbar`, Befund D) — der Fall ist nicht still.",
    "api_cache_pflege.sh":
        "VPS-Wartungsskript; die Vorgabe steht hinter einer Umgebungsgröße "
        "und ist damit umbiegbar.",
}


def _ist_bewusst_vps_gebunden(datei: Path) -> bool:
    return datei.name in _VPS_GEBUNDEN


def _feste_pfade_in_skripten() -> set[str]:
    """Shell-Skripte: zeilenweise, ohne Kommentare.

    Kein Syntaxbaum — es gibt keinen für `sh`. Kommentarzeilen fallen heraus,
    sonst stolperte die Prüfung über die **Erklärungen**, die in diesem
    Projekt genau diese Pfade besprechen.
    """
    raus = set()
    for datei in _versionierte("*.sh"):
        # `scripts/mac/` ist ausdruecklich maschinengebunden.
        if "/mac/" in str(datei) or _ist_bewusst_vps_gebunden(datei):
            continue
        try:
            zeilen = datei.read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for nr, zeile in enumerate(zeilen, 1):
            if zeile.lstrip().startswith("#"):
                continue
            for treffer in re.findall(r"[\"'\s=:(]((?:/home/claudebot|~/)[\w./-]*)",
                                      zeile):
                if _ist_ortsabhaengig(treffer):
                    raus.add(f"{datei.name}:{nr} {treffer}")
    return raus


def _feste_pfade_in_json() -> set[str]:
    """Register-Dateien: rekursiv ueber alle Zeichenketten-Werte.

    `components.json` ist der Fall, der das noetig macht — der
    Versions-Waechter liest es, und dort stehen acht venv-Pfade.
    """
    import json as _json
    raus = set()
    for datei in _versionierte("*.json"):
        if _ist_bewusst_vps_gebunden(datei):
            continue
        try:
            daten = _json.loads(datei.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue

        def geh(o, pfad="") -> None:
            if isinstance(o, dict):
                for k, v in o.items():
                    geh(v, f"{pfad}.{k}" if pfad else str(k))
            elif isinstance(o, list):
                for i, v in enumerate(o):
                    geh(v, f"{pfad}[{i}]")
            elif isinstance(o, str) and _ist_ortsabhaengig(o):
                raus.add(f"{datei.name}:{pfad} {o}")

        geh(daten)
    return raus


# --------------------------------------------------------------------------
# Der Sammler — findet die Arten über den EIGENEN Syntaxbaum
# --------------------------------------------------------------------------

def arten() -> list[tuple[str, callable]]:
    """Alle Differenzarten dieses Moduls, mit erzwungener Gegenprobe.

    **Warum über den Syntaxbaum und nicht über eine Liste:** Ein Modul, das
    Aufzählungen abschaffen soll, darf nicht mit einer anfangen. Es gibt keine
    Stelle, an der man eine neue Art eintragen müsste — und deshalb keine, an
    der man sie vergessen kann.

    **Die Gegenprobe ist Ladebedingung, kein Lauf.** Wer eine Art ohne
    `<name>_gegenprobe` hinzufügt, bekommt hier einen Fehler statt einer stillen
    Aufnahme. Das ist die einzige geduldete Prüfung über einen Prüfer, und sie
    ist keine: Sie verlangt nur, dass es sie gibt.
    """
    quelle = Path(__file__).read_text(encoding="utf-8")
    baum = ast.parse(quelle)
    # **`globals()`, nicht `sys.modules[__name__]`.** Beim Einhängen in den
    # Selbstcheck wird dieses Modul über `importlib` von Hand geladen und steht
    # dann NICHT in `sys.modules` — der Zugriff lieferte `None` und die ganze
    # Prüfzeile brach mit `'NoneType' object has no attribute '__dict__'`.
    # Gefunden beim Ausführen der Einhängung, nicht beim Lesen.
    hier = globals()
    namen = [k.name for k in baum.body
             if isinstance(k, ast.FunctionDef) and k.name.endswith("_differenz")]
    raus = []
    for name in sorted(namen):
        if f"{name}_gegenprobe" not in hier:
            raise RuntimeError(
                f"Differenzart {name!r} hat keine Gegenprobe. Ohne sie ist "
                f"nicht belegt, dass sie eine Luecke ueberhaupt findet — "
                f"eine Art, die nie etwas meldet, sieht genauso aus.")
        raus.append((name, hier[name]))
    return raus


def messen() -> list[Befund]:
    """Alle Arten fahren. Gibt nur die Arten zurück, die etwas gefunden haben."""
    raus = []
    for _name, art in arten():
        b = art()
        if b.fehlend:
            raus.append(b)
    return raus


def gegenproben_fahren() -> None:
    """Jede Gegenprobe einmal — für den Prüfstand."""
    hier = globals()
    for name, _ in arten():
        hier[f"{name}_gegenprobe"]()


def main() -> int:
    print("Differenzmesser")
    print("=" * 40)
    for name, _ in arten():
        print(f"○ {name}")
    print()
    befunde = messen()
    if not befunde:
        print("✓ keine Differenz — alle Mengen decken sich")
        return 0
    schlimm = False
    for b in befunde:
        zeichen = "✗" if b.haerte == BRICHT else "⚠"
        schlimm = schlimm or b.haerte == BRICHT
        print(f"{zeichen} {b.was}: {', '.join(sorted(b.fehlend))}")
        if b.hinweis:
            print(f"   {b.hinweis}")
    return 1 if schlimm else 0


if __name__ == "__main__":
    sys.exit(main())
