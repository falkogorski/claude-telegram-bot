"""Positivliste fuer Bash-Befehle — die Wache steht am Ausgang.
<!-- ROLLE: bash-positivliste -->

**Auftrag:** `docs/auftraege/2026-08-29_bauauftrag-bash-freigaben-weniger-druecke.md`
(Claudia 00:45, Engywucks Freigabe mit vier Entscheiden und drei Auflagen im
Nachtpaket 01:20, Adams Abnahme 00:42).

## Warum das ein Sicherheits- und kein Bequemlichkeitsbau ist

Gemessen ueber sieben Tage: **448 Bash-Aufrufe, 352 davon mit Dialog.** Adam
am 29.08. um 00:28: *„Es ist einfach super anstrengend. Man verliert die Lust.
… Ich gucke mir nicht jede Datei vorher an, bevor ich die freigebe."*

**Eine Rueckfrage, die 352 Mal kommt und ungelesen bestaetigt wird, schuetzt
nicht — sie gewoehnt ab.** Der eine gefaehrliche Befehl geht genau deshalb
durch: Er sieht aus wie die 351 davor. Der reale Angriffsweg ist nicht ein
Einbruch auf dem Server, sondern Inhalt, den die Sitzung liest — eine
Webseite, ein weitergeleitetes Bild, eine fremde Ablage. **Eine Positivliste
wirkt auch dann, wenn das Modell hereingelegt wurde; ein weggedrueckter
Dialog wirkt dann nicht.**

## Drei Ausgaenge, nicht zwei

* **frei** — laeuft ohne Rueckfrage (Auftrag 1)
* **abweisen** — wird gar nicht erst vorgelegt (Auftrag 2). Ein Dialog waere
  hier die falsche Antwort: Er verlagert eine Entscheidung auf Adam, die er
  nachts um halb eins nicht pruefen kann.
* **dialog** — alles Uebrige (Auftrag 3), und **alles Unbekannte**. Die
  Vorgabe ist fail-closed: Was diese Datei nicht versteht, geht in den Dialog.

## Was diese Datei NICHT tut

Sie kennt keine Geheimnisse. `_is_sensitive_ref` bleibt in `bot.py` und wird
**hereingereicht** — so bleibt die Geheimnis-Schranke an einer einzigen
Stelle, und ein Pruefer kann eine Attrappe einsetzen und messen, dass ein
Treffer wirklich abweist. Zwei Listen driften; eine gemeinsame kann es nicht
(dieselbe Lehre wie bei der Anmelde-Marke G1).
"""
from __future__ import annotations

import os
import re
import shlex
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["Bereich", "Entscheid", "bereiche_aus_umgebung", "entscheiden",
           "FREI", "ABWEISEN", "DIALOG"]

FREI = "frei"
ABWEISEN = "abweisen"
DIALOG = "dialog"


@dataclass(frozen=True)
class Bereich:
    """Ein Ordner, in dem gearbeitet werden darf.

    **Der Bereichspfad loest sich SELBST auf, und das ist kein Beiwerk.**
    Gefunden beim ersten Prueflauf: Elf Zeilen waren rot, weil die Pruefung
    Wegwerf-Ordner unter `/var/folders/…` anlegte, `resolve()` daraus aber
    `/private/var/folders/…` machte — auf macOS ist `/var` ein symbolischer
    Verweis. Die aufgeloesten Argumente lagen damit nie in den nicht
    aufgeloesten Bereichen.

    Im Pruefstand war das eine rote Zeile. **Im Betrieb waere es eine
    Freigabe, die stillschweigend nie greift** — jeder Befehl fiele weiter in
    den Dialog, und niemand haette einen Grund dafuer. Genau die Fehlerform,
    die dieses Projekt schon dreimal aktenkundig hat: Der Bruch sieht aus wie
    der Normalzustand.

    Die Aufloesung gehoert deshalb hierher und nicht in den Aufrufer: **Was
    jeder Aufrufer selbst tun muss, vergisst irgendwann einer.**
    """
    name: str
    pfad: Path
    schreibbar: bool = False

    def __post_init__(self) -> None:
        try:
            aufgeloest = Path(self.pfad).expanduser().resolve()
        except Exception:
            aufgeloest = Path(self.pfad)
        object.__setattr__(self, "pfad", aufgeloest)

    def enthaelt(self, p: Path) -> bool:
        return p == self.pfad or self.pfad in p.parents


@dataclass(frozen=True)
class Entscheid:
    urteil: str                     # FREI | ABWEISEN | DIALOG
    grund: str = ""
    befehlsart: str = ""            # erstes Wort, fuer das Protokoll (Auftrag 5)
    bereich: str = ""               # Name des Bereichs, fuer das Protokoll
    pfade: tuple[str, ...] = field(default=())


# ---------------------------------------------------------------- die Bereiche
#
# **Abgeleitet, nicht getippt** — dieselbe Lehre wie bei `_REPO_MARKEN`: In
# einem Probelauf-Klon heisst der Ordner anders, und eine feste Zeichenkette
# griffe dort nicht. Ueber die Umgebung ueberschreibbar, damit ein Pruefer
# gegen Wegwerf-Ordner messen kann, statt gegen die echten.

def bereiche_aus_umgebung(repo: Path | None = None) -> tuple[Bereich, ...]:
    """Die vier Bereiche aus Auftrag 1.

    Bereich 4 (Logs) ist **Engywucks offene Frage 3**, und sie ist gemessen
    beantwortet: Auf dem VPS liegen die Bot-Protokolle unter `logs/` INNERHALB
    des Repos, sind also von Bereich 1 abgedeckt. Er bleibt trotzdem als
    eigener Eintrag stehen, weil `~/logsync/claude-bot-logs` (der Kurier-Klon)
    daneben liegt und nicht zum Repo gehoert. **Redundanz schadet hier nicht;
    eine fehlende Zeile schon.**
    """
    repo = repo or Path(__file__).resolve().parent
    # **Ein EIGENER Schluessel, nicht `HOME`** — der Differenzmesser hat den
    # Grund geliefert: Er verlangt, dass jede Pfadquelle eines Produktivmoduls
    # im Regressionslaeufer riegelbar ist, sonst misst ein Prueflauf gegen
    # Adams echte Ordner. `HOME` global zu verbiegen wuerde venv, Zwischen-
    # speicher und halbe Werkzeugkette mitreissen; ein eigener Schluessel
    # laesst sich gefahrlos umbiegen.
    #
    # Der Rueckfall auf `Path.home()` bleibt **sichtbar** stehen. Ihn zu
    # nehmen, um dem Messer zu entgehen, waere eine Umgehung gewesen: dieselbe
    # Abhaengigkeit, nur unsichtbar — genau die Bauform, die dieses Projekt
    # sich abgewoehnt hat.
    heim = Path(os.environ.get("BASHFREI_HEIM") or Path.home()).expanduser()

    def _p(schluessel: str, vorgabe: Path) -> Path:
        roh = os.environ.get(schluessel)
        return Path(roh).expanduser() if roh else vorgabe

    return (
        Bereich("repo", repo, schreibbar=False),
        Bereich("workspace", _p("BASHFREI_WORKSPACE", heim / "workspace"),
                schreibbar=True),
        Bereich("postfach", _p("BASHFREI_POSTFACH", heim / "postfach"),
                schreibbar=True),
        Bereich("logs", _p("BASHFREI_LOGS", heim / "logsync"), schreibbar=False),
    )


# ---------------------------------------------------------------- die Verben
#
# Nach WIRKUNG geordnet, nicht alphabetisch: Was nur liest, darf in jedem
# Bereich laufen; was schreibt, nur in den schreibbaren.

LESEN = frozenset("""
    ls cat head tail grep rg find wc stat file sort uniq diff du df
    tree nl column less more basename dirname realpath readlink cmp
""".split())

SCHREIBEN = frozenset("sed printf echo cp mv mkdir tee touch".split())

ERZEUGEN = frozenset("pandoc weasyprint typst".split())

# Ohne Wirkung auf Dateien — duerfen ueberall laufen, auch ohne Pfad.
ZUSTAND = frozenset("free uptime date sleep which whoami hostname ps env true echo".split())

# `git` mit einem lesenden Unterbefehl. Alles andere an git ist Dialog —
# `git push` steht ausdruecklich in Auftrag 3.
GIT_LESEND = frozenset("""
    log status diff show branch blame ls-files rev-parse describe
    config remote tag shortlog
""".split())

# `systemctl` NUR mit `status` (Auftrag 1). Jeder andere Unterbefehl greift in
# den Betrieb ein und gehoert nach Auftrag 3 in den Dialog.
SYSTEMCTL_LESEND = frozenset("status list-timers list-units is-active is-enabled show cat".split())

ALLE_ERLAUBTEN = LESEN | SCHREIBEN | ERZEUGEN | ZUSTAND | {"git", "systemctl"}

# ------------------------------------------------------- benannte Skripte (U-3)
#
# **Die einzige Stelle, an der ein Deuter frei laufen darf — und sie ist eng
# gebaut, weil `python3` als Verb die ganze Liste oben aufheben wuerde.**
#
# Engywucks Umbauauftrag 02.09., U-3. Anlass: 27 Ersetzungs-Dialoge, praktisch
# alle Postfach-Auftraege in der Form, die `docs/boten-postfach.md` selbst
# vorschreibt. Die naheliegende Loesung — eine Positivliste harmloser
# Ersetzungen — traegt nicht: Jene Form trifft **vier** Schranken (Ersetzung,
# Zuweisung, Zeilenumbruch, Umlenkung); eine Ersetzungs-Liste oeffnete die
# erste und liesse drei stehen.
#
# Der Grundsatz stammt aus dem Kopf von `scripts/bash_dialog_auswertung.py`
# und ist aelter als dieser Fall: *Wiederkehrende gleichartige Dialoge werden
# durch benannte, geprüfte Skripte ersetzt, die einzeln in die Positivliste
# rücken — nie durch Öffnen einer Klasse.*
#
# **Drei Bedingungen, alle drei notwendig:**
#   1. der aufgeloeste Pfad liegt unter `<repo>/scripts/`,
#   2. der Dateiname steht in dieser Menge,
#   3. das Skript ist versioniert.
#
# **Zu (1): aufgeloest, nicht verglichen.** `_aufloesen` folgt symbolischen
# Verweisen — ein `scripts/x.py`, das nach `/tmp` zeigt, faellt heraus.
#
# **Zu (3), und das ist der Punkt, an dem hier NICHTS gebaut wird:** Es gibt
# keinen `git ls-files`-Aufruf in dieser Funktion. Die Versionierung ist
# bereits garantiert — durch die **Repo-Schreibsperre 8.7**, die dreischichtig
# verhindert, dass die Sitzung eine Datei unter `scripts/` aendert. Ein
# Unterprozess-Aufruf mitten in einer Sicherheitsentscheidung waere langsamer,
# fehleranfaelliger **und schwaecher**: `git ls-files` sagt nur, ob eine Datei
# bekannt ist, nicht ob sie unveraendert ist. Wer 8.7 aufweicht, hebt diese
# Bedingung mit auf — deshalb steht sie hier und nicht nur im Kommentar des
# Auftrags.
#
# **Was ein Eintrag hier bedeutet:** dass dieses Skript **mit beliebigen
# Argumenten** ohne Rueckfrage laeuft. Aufgenommen wird nur, was
# deterministisch ist, kein Modell ruft, nicht ins Netz geht und keine
# Geheimnisse liest. Die Geheimnis-Pruefung ueber den ganzen Befehlstext
# greift ohnehin vorher.
BENANNTE_SKRIPTE = frozenset({
    # Legt einen Zustell-Auftrag im Boten-Postfach ab. Ersetzt die
    # vierfach-dialogpflichtige Shell-Form aus `docs/boten-postfach.md`.
    "postfach_ablegen.py",
    # War fuer genau diesen Weg gebaut (28.08.) und **selbst dialogpflichtig** —
    # ein Handgriff, den der Dialog jedes Mal unterbrach.
    "entscheidung_ablegen.py",
})

# Die Deuter, fuer die (1)-(3) ueberhaupt geprueft werden. Ohne benanntes
# Skript bleibt jeder von ihnen im Dialog.
DEUTER = frozenset({"python3", "python"})

# ---------------------------------------------------------------- was abweist
#
# Auftrag 2. **Diese Faelle werden nicht vorgelegt, sondern abgewiesen.**

# `.claude` ist zu — mit EINER Ausnahme, und die ist Engywucks Auflage A:
# `~/.claude/memory` bleibt LESBAR. Der System-Prompt sagt dem Bot diesen
# Ordner ausdruecklich zu (8.7, Befund G vom 23.08.). Eine Schranke, die dem
# Prompt widerspricht, laesst den Bot an einer Stelle dialogen, die ihm
# zugesagt ist — und niemand versteht warum.
CLAUDE_ORDNER = ".claude"
CLAUDE_AUSNAHME_LESEND = "memory"

# Ausfuehrende Schalter machen aus einem Lese-Verb eine Shell. Uebernommen aus
# `bot._AUSFUEHRENDE_SCHALTER` (H6, Engywucks Probelauf 22.08.): `find -exec`
# ist eine Shell, `find -delete` ein Loeschwerkzeug, und **beides braucht kein
# einziges Verkettungszeichen**, an dem eine Meta-Pruefung greifen wuerde.
AUSFUEHRENDE_SCHALTER = re.compile(
    r"(?<![\w-])-(exec(dir)?|delete|ok(dir)?|fprintf?|fls|printf)(?![\w-])"
    r"|(?<![\w-])--(hide|exclude)=", re.IGNORECASE)

# Ersetzungen: der Inhalt ist zur Pruefzeit unbekannt. Auftrag 4.
ERSETZUNG = re.compile(r"\$\(|`|<\(|\$\{|\$[A-Za-z_]")

# Verkettungen ausser dem einen erlaubten `&&`. Auftrag 4.
WEITERE_VERKETTUNG = re.compile(r"[;|]|\n|\|\|")

# ══════════════════════════════════════════════════════════════════════════
# **ZERLEGEN IST ERLAUBT, SOLANGE KEIN GLIED DEN BODEN VERSCHIEBT.**
#
# In den Dialog faellt jedes Glied, das den Zustand der FOLGENDEN Pruefungen
# aendert: `cd`, `pushd`/`popd`, `export`, `set`, `source` und `.`, sowie
# Zuweisungen der Form `NAME=wert`.
#
# **Warum diese Regel hier steht, obwohl heute nichts durchkommt** — und das
# ist der eigentliche Grund, nicht ein Loch:
#
# Diese Befehle fallen heute in den Dialog, **weil sie in keiner Freiliste
# stehen** — nicht, weil jemand entschieden haette, dass zustandsveraendernde
# Befehle nicht zerlegt werden duerfen. **Der Schutz ist ein Zufall, keine
# Entscheidung.** Wer morgen die Freiliste erweitert — und genau darauf zielt
# die Zerlegung, weniger Rueckfragen — hebt ihn auf, ohne es zu merken.
#
# Der Zusammenhang, an dem es haengt: `_aufloesen` loest relative Pfade gegen
# das Arbeitsverzeichnis des Bot-Prozesses auf. Ein `cd` in einem frueheren
# Glied verschiebt den Boden, auf dem jede folgende Pfadpruefung steht — die
# Pruefung urteilte dann ueber einen anderen Pfad als den, der gelesen wird.
# Dieselbe Fehlerform wie die `..`-Umgehung vom 23.08., nur ueber die
# Verkettung statt ueber den Pfad.
#
# **Und das ist zugleich die Antwort, warum `cd … && …` genau EINMAL erlaubt
# ist:** Die Eins ist keine Zahl, sondern eine Form. `cd` darf den Boden
# verschieben, weil sein Ziel dabei **geprueft** wird — ganz vorn, einmal,
# gegen die erlaubten Bereiche. Ein Maß, zwei Anwendungen.
_BODEN_BEFEHLE = re.compile(
    r"^\s*(?:cd|pushd|popd|export|set|source|\.)(?=\s|$)"
    r"|^\s*[A-Za-z_][A-Za-z_0-9]*=", re.IGNORECASE)

# Wie in bot.py: eine reine FEHLERumleitung schreibt nichts und darf bleiben.
HARMLOSE_UMLEITUNG = re.compile(r"\s*2>\s*(?:&1|/dev/null|/tmp/[\w.\-/]+)")

# Was ein `sleep` hoechstens darf. **Setzung, kein Messwert** — begruendet:
# `sleep` steht in Auftrag 1 unter den wirkungslosen Zustandsabfragen, aber
# `sleep 99999` waere eine blockierte Sitzung ohne jeden Dialog. Fuenf Minuten
# decken jedes Warten ab, das im Alltag vorkommt.
SCHLAF_DECKEL_S = 300


def _ohne_harmlose_umleitung(cmd: str) -> str:
    return HARMLOSE_UMLEITUNG.sub(" ", cmd or "")


def _aufloesen(roh: str, basis: Path | None = None) -> Path | None:
    """Pfad aufloesen — `..` und symbolische Verweise mit.

    **Aufloesen, nicht vergleichen** (Befund D/E, Engywuck 23.08.): Ein `..`
    hebt jede Zusage auf, ohne die Zeichenkette anzutasten. Gemessen liefen
    damals `cat <repo>/../../../etc/passwd` und `cat $X/proc/self/environ`
    ohne Dialog durch.

    **`basis` `[NEU 02.09.2026, A2]`: das `cd`-Ziel, wenn eines vorangeht.**
    Ohne sie loeste ein relativer Pfad im zweiten Glied von `cd X && cat y`
    gegen das **Arbeitsverzeichnis des Bot-Prozesses** auf — also gegen einen
    anderen Boden als den, auf dem die Shell den Befehl ausfuehrt.

    **Heute kam dadurch nichts durch**, weil die Aufloesung in der Praxis
    *hoeher* landet als gemeint und damit aus den Bereichen faellt — die
    sichere Fehlerrichtung. **Aber ein Pruefer, der zufaellig richtig liegt,
    ist kein Pruefer**, und derselbe Zufall koennte mit einer anderen
    Bereichslage kippen. Die Pruefung urteilt jetzt ueber den Pfad, der
    tatsaechlich gelesen wird.
    """
    try:
        p = Path(roh).expanduser()
        if basis is not None and not p.is_absolute():
            p = Path(basis) / p
        return p.resolve()
    except Exception:
        return None


def _bereich_von(p: Path, bereiche) -> Bereich | None:
    # Der ENGSTE passende Bereich gewinnt: Liegt `logs` innerhalb des Repos,
    # soll der Treffer `logs` heissen und nicht `repo` — sonst luegt das
    # Protokoll aus Auftrag 5 ueber den Ort.
    treffer = [b for b in bereiche if b.enthaelt(p)]
    if not treffer:
        return None
    return max(treffer, key=lambda b: len(str(b.pfad)))


def _ist_claude_ordner(p: Path) -> tuple[bool, bool]:
    """(liegt in .claude, liegt im Gedaechtnis-Unterordner)"""
    teile = p.parts
    if CLAUDE_ORDNER not in teile:
        return (False, False)
    i = teile.index(CLAUDE_ORDNER)
    return (True, len(teile) > i + 1 and teile[i + 1] == CLAUDE_AUSNAHME_LESEND)


def _pfad_artig(wort: str) -> bool:
    """Sieht das Argument nach einem Pfad aus?

    Argumente ohne `/` und ohne `~` werden uebersprungen: Suchmuster, Verben,
    Zahlen. **Ein Ausbruch braucht einen Pfad, und ein Pfad hat einen
    Schraegstrich.**

    **`[BERICHTIGT 02.09.2026, A2]` Hier stand als Begruendung: *ein blosser
    Dateiname loest sich gegen das Arbeitsverzeichnis auf, das wir selbst
    setzen.* Nach einem `cd` setzen wir es nicht selbst** — dann loest ein
    blosser Dateiname gegen das cd-Ziel auf.

    **Gemessen ist das keine Luecke**, und der Grund ist die Reihenfolge: Das
    cd-Ziel wird vorher gegen die erlaubten Bereiche geprueft. Ein Dateiname
    ohne Schraegstrich kann diesen Bereich nicht verlassen — dafuer braeuchte
    er ein `..` oder einen Schraegstrich, und beides macht ihn pfad-artig.
    **Die Zusage gilt also weiter; nur ihre Begruendung war ueberholt.**
    """
    return ("/" in wort or wort.startswith("~")) and not wort.startswith("-")


def _teile(cmd: str) -> list[str] | None:
    try:
        return shlex.split(cmd)
    except ValueError:
        return None       # unbalancierte Anfuehrungszeichen -> fail-closed


def _unterbefehl(teile: list[str]) -> str:
    """Der erste Nicht-Options-Teil nach dem Verb.

    **Gefunden beim ersten Prueflauf:** `git -C <pfad> log` galt als nicht
    lesend, weil starr `teile[1]` gelesen wurde — und das war `-C`. Genau die
    Form, die in diesem Projekt taeglich vorkommt, waere dauerhaft im Dialog
    gelandet. Optionen und ihre Werte werden deshalb uebersprungen.
    """
    i = 1
    while i < len(teile):
        w = teile[i]
        if w.startswith("-"):
            # Optionen mit eigenem Wert (`-C <pfad>`, `--git-dir <pfad>`):
            # der naechste Teil gehoert dazu, wenn kein `=` im Schalter steht.
            if "=" not in w and i + 1 < len(teile) and not teile[i + 1].startswith("-"):
                i += 2
                continue
            i += 1
            continue
        return w
    return ""


def _schlaf_ok(teile: list[str]) -> bool:
    for w in teile[1:]:
        if w.startswith("-"):
            continue
        try:
            return float(w) <= SCHLAF_DECKEL_S
        except ValueError:
            return False
    return False          # `sleep` ohne Zahl ist keine bekannte Form


def _benanntes_skript(teile: list[str], art: str, bereiche,
                      basis: Path | None) -> Entscheid | None:
    """Darf dieser Deuter-Aufruf durch? `None` heisst ja.

    Drei Bedingungen, alle notwendig (U-3): **direkt** unter `<repo>/scripts/`,
    Name in `BENANNTE_SKRIPTE`, versioniert. Die dritte ist nicht gebaut,
    sondern **geerbt** — die Repo-Schreibsperre 8.7 haelt sie; siehe den
    Kommentar bei `BENANNTE_SKRIPTE`.

    **Streng am ersten Argument, und das ist der Kern:** Steht dort ein
    Schalter, ist Schluss. Sonst faenden `python3 -c "…"` und `python3 -m …`
    einen Weg — bei `-c` waere die Zeichenkette mit dem Code das erste
    Nicht-Schalter-Argument, und eine Pruefung, die *irgendwo* nach einem
    Skriptnamen sucht, haette ihn dort gefunden. **Der Deuter bekommt genau
    eine Form: `python3 <skript> [argumente]`.**
    """
    if len(teile) < 2:
        return Entscheid(DIALOG, f"[{art}] ohne Skript", art)
    erstes = teile[1]
    if erstes.startswith("-"):
        return Entscheid(DIALOG,
                         f"[{art}] mit einem Schalter statt eines Skripts: "
                         f"[{erstes}]", art)
    p = _aufloesen(erstes, basis)
    if p is None:
        return Entscheid(DIALOG, f"Skriptpfad nicht aufloesbar: {erstes}", art)

    repo = next((b.pfad for b in bereiche if b.name == "repo"), None)
    if repo is None:
        # Kein Repo-Bereich bekannt — dann gibt es nichts, wogegen zu pruefen
        # waere. Fail-closed, nicht raten.
        return Entscheid(DIALOG, "kein Repo-Bereich zum Pruefen", art)

    # `p.parent ==` statt „liegt irgendwo darunter": Unterordner sollen NICHT
    # mitkommen. Eine Zusage, die auf einen Baum zeigt, waechst mit ihm.
    if p.parent != (repo / "scripts"):
        return Entscheid(DIALOG,
                         f"[{p.name}] liegt nicht direkt unter scripts/", art,
                         pfade=(str(p),))
    if p.name not in BENANNTE_SKRIPTE:
        return Entscheid(DIALOG,
                         f"[{p.name}] steht nicht unter den benannten "
                         "Skripten", art, pfade=(str(p),))
    return None


def _ein_befehl(teile: list[str], roh: str, bereiche,
                ist_geheimnis, umgelenkt_nach: str = "",
                basis: Path | None = None) -> Entscheid:
    """Ein einzelner Befehl, bereits zerlegt und ohne Verkettung.

    `basis` ist das geprüfte `cd`-Ziel, falls eines vorangeht (A2) — relative
    Pfade werden dagegen aufgeloest statt gegen das Arbeitsverzeichnis.
    """
    verb = teile[0]
    art = Path(verb).name          # `/bin/ls` protokolliert als `ls`

    if ist_geheimnis(roh):
        return Entscheid(ABWEISEN, "Geheimnis-Pfad — auch lesend zu", art)

    if art in DEUTER:
        # **Die eine Ausnahme von „kein Deuter" — und sie oeffnet keine
        # Klasse, sondern nennt zwei Dateien.** Faellt die Pruefung durch,
        # laeuft der Befehl unten durch dieselbe Pfad-Pruefung wie jeder
        # andere: `--datei` und Konsorten werden gegen die Bereiche gehalten.
        _e = _benanntes_skript(teile, art, bereiche, basis)
        if _e is not None:
            return _e
    elif art not in ALLE_ERLAUBTEN:
        # Auftrag 3, und dieser Punkt traegt die ganze Konstruktion: Ein
        # Skript kann jede Grenze dieser Liste umgehen. Waere `python3` frei,
        # waeren die Auftraege 1 und 2 wirkungslos.
        return Entscheid(DIALOG, f"[{art}] steht nicht auf der Positivliste", art)

    if AUSFUEHRENDE_SCHALTER.search(roh):
        return Entscheid(DIALOG, "ein ausfuehrender Schalter (-exec/-delete)", art)

    if art == "git":
        unter = _unterbefehl(teile)
        if unter not in GIT_LESEND:
            return Entscheid(DIALOG, f"git {unter or '—'} ist nicht lesend", art)

    if art == "systemctl":
        unter = _unterbefehl(teile)
        if unter not in SYSTEMCTL_LESEND:
            return Entscheid(DIALOG,
                             f"systemctl {unter or '—'} greift in den Betrieb ein", art)

    if art == "sleep" and not _schlaf_ok(teile):
        return Entscheid(DIALOG, f"sleep ueber {SCHLAF_DECKEL_S} s", art)

    schreibt = art in SCHREIBEN
    # `sed` liest, solange es nicht in-place schreibt.
    if art == "sed" and not re.search(r"(?<![\w-])-\w*i", " ".join(teile[1:])):
        schreibt = False

    # **Erzeuger lesen und schreiben zugleich — und das ist kein Sonderfall,
    # sondern der Normalfall.** Auftrag 1 sagt es genau: *„Dokumentenerzeugung:
    # pandoc, weasyprint — AUSGABE in Bereich 2."* Die Quelle darf also im Repo
    # liegen; nur das Ziel muss schreibbar sein.
    #
    # Erkannt wird das Ziel am ausdruecklichen `-o`, **nicht an der Position**.
    # Eine Positions-Regel („das letzte Argument ist das Ziel") waere geraten,
    # und geratene Regeln sind in einer Sicherheitsschranke genau das, was
    # dieses Projekt sich abgewoehnt hat.
    erzeugt_nach: set[str] = set()
    if art in ERZEUGEN:
        for i, w in enumerate(teile):
            if w in ("-o", "--output") and i + 1 < len(teile):
                erzeugt_nach.add(teile[i + 1])
            elif w.startswith("--output="):
                erzeugt_nach.add(w.split("=", 1)[1])

    # ---- die Pfade
    gefunden: list[str] = []
    bereich_name = ""
    for wort in teile[1:]:
        if not _pfad_artig(wort):
            continue
        p = _aufloesen(wort, basis)
        if p is None:
            return Entscheid(DIALOG, f"Pfad nicht aufloesbar: {wort}", art)
        gefunden.append(str(p))

        in_claude, ist_gedaechtnis = _ist_claude_ordner(p)
        if in_claude:
            # Auflage A: Gedaechtnis lesend frei, alles andere unter `.claude` zu.
            if ist_gedaechtnis and not schreibt:
                bereich_name = bereich_name or "gedaechtnis"
                continue
            return Entscheid(ABWEISEN,
                             "unter .claude — nur der Gedaechtnis-Ordner ist "
                             "lesend frei", art)

        b = _bereich_von(p, bereiche)
        if b is None:
            return Entscheid(DIALOG, f"liegt ausserhalb der Bereiche: {p}", art)
        muss_schreibbar = schreibt or (wort in erzeugt_nach)
        if muss_schreibbar and not b.schreibbar:
            return Entscheid(DIALOG, f"Bereich [{b.name}] ist nur lesbar", art)
        bereich_name = bereich_name or b.name

    if schreibt and not gefunden and not umgelenkt_nach:
        # Ein Schreibbefehl ohne erkennbaren Pfad schreibt irgendwohin —
        # in den Dialog damit.
        #
        # **`umgelenkt_nach` gehoert in diese Bedingung**, und der Prueflauf hat
        # gezeigt warum: `printf x > <postfach>/auftrag.json` ist der haeufigste
        # Schreibweg ueberhaupt. Das Ziel steht dort in der Umlenkung, die eine
        # Ebene hoeher bereits gegen die schreibbaren Bereiche geprueft und
        # danach aus der Zeile entfernt wurde — hier unten war also kein Pfad
        # mehr zu sehen. Der Befehl waere dauerhaft im Dialog gelandet, und der
        # Grund haette gelautet „ohne erkennbaren Pfad", obwohl der Pfad
        # dastand.
        return Entscheid(DIALOG, "Schreibbefehl ohne erkennbaren Pfad", art)

    if not gefunden and art not in ZUSTAND:
        # `ls` ohne Argument trifft das Arbeitsverzeichnis, das wir setzen —
        # das ist einer der Bereiche. Aber es ausdruecklich benennen, statt es
        # stillschweigend als frei zu behandeln.
        bereich_name = "arbeitsverzeichnis"

    return Entscheid(FREI, "", art, bereich_name or "—", tuple(gefunden))


# ---------------------------------------------------------------- Auftrag 5
#
# **Adams Nachtrag vom 29.08., 01:2x, macht die Messung zur Bringschuld statt
# zur Rueckfallebene** — sein Wortlaut: *„Sie werden ueber kurz oder lang
# nerven. Messdaten proaktiv hinzuziehen bitte!"* Ein Protokoll, das niemand
# liest, ist keine Messung; deshalb wird hier abgelegt und nach sieben Tagen
# von `scripts/bash_dialog_auswertung.py` von selbst vorgelegt.
#
# **Was abgelegt wird: Zeitpunkt, Urteil, Befehlsart, Bereich. Sonst nichts.**
# Ausdruecklich KEIN Grund und KEINE Pfade — der Grund traegt Pfade
# („liegt ausserhalb der Bereiche: /…"), und eine Zaehldatei ist der falsche
# Ort dafuer. Auftrag 5 sagt es genau: *„Kein Geheimnis kann darin stehen,
# weil nur das erste Wort und der Bereichsname abgelegt werden."*

def _zaehldatei() -> Path:
    roh = os.environ.get("BASHFREI_PROTOKOLL")
    if roh:
        return Path(roh).expanduser()
    heim = Path(os.environ.get("BASHFREI_HEIM") or Path.home()).expanduser()
    return heim / ".claude" / "bash-freigaben.jsonl"


def protokollieren(erg: Entscheid, *, zeit: str) -> None:
    """Eine Zeile je Aufruf — und ein Fehlschlag darf den Bot nicht aufhalten.

    Der Zeitpunkt wird **hereingereicht**, nicht hier gebildet: So bleibt die
    Funktion rein und ein Pruefer kann sie ohne Uhr messen.
    """
    try:
        datei = _zaehldatei()
        datei.parent.mkdir(parents=True, exist_ok=True)
        import json
        with datei.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"zeit": zeit, "urteil": erg.urteil,
                                "art": erg.befehlsart, "bereich": erg.bereich},
                               ensure_ascii=False) + "\n")
    except Exception:
        # **Bewusst stumm.** Eine volle Platte oder ein fehlendes Recht darf
        # keinen Bash-Aufruf scheitern lassen — die Messung ist wichtig, aber
        # nicht wichtiger als die Arbeit. Dass sie ausbleibt, faellt bei der
        # Auswertung auf: eine Datei ohne frische Zeilen ist selbst ein Befund.
        pass


def _zerlegt(glieder: list[str], roh: str, ist_geheimnis, bereiche) -> Entscheid:
    """Mehrere Glieder einzeln pruefen — frei nur, wenn jedes frei ist.

    **Ein Ort fuer `;`, `|`, `||` und `&&`.** Sie stand zuerst nur bei
    `;`/`|`; als `&&` dazukam (U-3b), waere die Boden-Bedingung an zwei
    Stellen gestanden — und die naechste Aenderung haette eine davon
    angefasst. Ein Mass, ein Ort.

    **Die Boden-Bedingung ist der Kern:** Zustandsveraendernde Befehle
    (`cd`, `export`, `source`, `NAME=wert`) fielen vor der Zerlegung in den
    Dialog, **weil sie auf keiner Freiliste standen** — nicht weil jemand
    entschieden haette, dass sie nicht zerlegt werden duerfen. Wer sie
    zerlegte, pruefte die folgenden Glieder gegen einen Boden, den das erste
    gerade verschoben hat. Deshalb steht die Regel jetzt geschrieben da.

    Ein einziges ABWEISEN entscheidet sofort; ein DIALOG merkt sich den
    **ersten** Grund, damit die Meldung auf das Glied zeigt, an dem es lag.
    """
    # Das Geheimnis einmal ueber den GANZEN Befehl, bevor zerlegt wird: Ein
    # Marker, der ueber eine Gliedgrenze reicht, waere sonst in keinem
    # einzelnen Glied vollstaendig.
    if ist_geheimnis(roh):
        return Entscheid(DIALOG, "ein Geheimnis-Marker im Befehl")
    strengste = None
    for g in glieder:
        if _BODEN_BEFEHLE.search(g):
            return Entscheid(DIALOG,
                             f"ein Glied verschiebt den Boden fuer die "
                             f"folgenden Pruefungen: [{g.strip()[:40]}]")
        e = entscheiden(g, ist_geheimnis=ist_geheimnis, bereiche=bereiche)
        if e.urteil == ABWEISEN:
            return e
        if e.urteil == DIALOG and strengste is None:
            strengste = e
    return strengste or Entscheid(
        FREI, "", befehlsart=(glieder[0].split() or [""])[0],
        bereich="mehrgliedrig")


def entscheiden(cmd: str, *, ist_geheimnis, bereiche=None) -> Entscheid:
    """Darf dieser Bash-Befehl ohne Rueckfrage laufen?

    `ist_geheimnis` ist die Geheimnis-Schranke aus `bot.py`
    (`_is_sensitive_ref` mit `schreibend=False`), hereingereicht statt
    nachgebaut.
    """
    roh = cmd or ""
    if not roh.strip():
        return Entscheid(DIALOG, "leerer Befehl")

    bereiche = bereiche if bereiche is not None else bereiche_aus_umgebung()
    ohne = _ohne_harmlose_umleitung(roh)
    umgelenkt_nach = ""

    # ---- Auftrag 4: das Fliesstext-Problem, VOR jeder Verb-Pruefung
    if ERSETZUNG.search(ohne):
        return Entscheid(DIALOG,
                         "eine Ersetzung ($(…), Rueckwaertsanfuehrung, "
                         "Variable) — ihr Inhalt ist hier nicht bekannt")

    # Umlenkung: `>` und `>>` schreiben tatsaechlich. Erlaubt nur, wenn das
    # Ziel in einem schreibbaren Bereich liegt.
    for treffer in re.finditer(r">>?\s*(\S+)", ohne):
        ziel = _aufloesen(treffer.group(1))
        if ziel is None:
            return Entscheid(DIALOG, "Umlenkungsziel nicht aufloesbar")
        b = _bereich_von(ziel, bereiche)
        if b is None or not b.schreibbar:
            return Entscheid(DIALOG,
                             f"Umlenkung nach [{ziel}] — ausserhalb der "
                             "schreibbaren Bereiche")
        umgelenkt_nach = str(ziel)
        ohne = ohne.replace(treffer.group(0), " ")

    # ---- Zerlegung an `;`, `|` und `||` (Adams Freigabe 01.09.)
    #
    # **Jedes Glied einzeln durch dieselbe Pruefung; frei nur, wenn jedes Glied
    # frei ist.** Ein einziges Dialog- oder Abweis-Urteil entscheidet fuer den
    # ganzen Befehl, mit dem Grund des betroffenen Glieds. Das erspart die
    # Rueckfrage bei `grep … | head` und aehnlichem Alltag.
    #
    # **Zeilenumbruch bleibt Dialog** — er stand in derselben Menge, ist aber
    # nicht beauftragt. Die konservative Richtung, wo nichts entschieden wurde.
    if "\n" in ohne:
        return Entscheid(DIALOG,
                         "ein Zeilenumbruch im Befehl — bitte in einzelne "
                         "Befehle teilen")
    _glieder = [s.strip() for s in re.split(r"\|\||[;|]", ohne) if s.strip()]
    if len(_glieder) > 1:
        return _zerlegt(_glieder, roh, ist_geheimnis, bereiche)

    if WEITERE_VERKETTUNG.search(ohne):
        return Entscheid(DIALOG,
                         "eine Verkettung ausser dem einen erlaubten "
                         "[cd … && …] — bitte in einzelne Befehle teilen")

    stuecke = [s.strip() for s in re.split(r"&&", ohne) if s.strip()]

    # ---- `&&`: zerlegen wie `;` — mit EINER benannten Ausnahme (U-3b)
    #
    # Claudia hat gemessen, dass `a && b` ohne `cd` ein spuerbarer Teil der
    # taeglichen Dialoge ist; `ls && echo fertig` fiel bis hierher durch.
    #
    # **Warum `&&` nicht einfach mit in die obere Zerlegung kann:** `cd` ist
    # ein Boden-Befehl. `cd x && ls` wuerde dort als Glied `cd x` erkannt und
    # in den Dialog geschickt — **die eine Form, die heute ausdruecklich
    # erlaubt ist, waere weg.** Deshalb steht sie hier als Ausnahme davor,
    # ausdruecklich benannt, und gilt nur bei **genau einem** `&&`:
    # `cd x && ls && wc` faellt in die Zerlegung und dort ueber den Boden.
    #
    # **Ein Mass, eine benannte Ausnahme** — nicht zwei Masse nebeneinander.
    _kopf_ist_cd = False
    if len(stuecke) == 2:
        _k = _teile(stuecke[0])
        if _k is None:
            return Entscheid(DIALOG, "unbalancierte Anfuehrungszeichen")
        _kopf_ist_cd = bool(_k) and _k[0] == "cd"

    if len(stuecke) > 1 and not _kopf_ist_cd:
        return _zerlegt(stuecke, roh, ist_geheimnis, bereiche)

    # ---- die eine erlaubte Verkettungsform: `cd <erlaubter Pfad> && <Befehl>`
    if len(stuecke) == 2:
        kopf = _teile(stuecke[0])
        if kopf is None:
            return Entscheid(DIALOG, "unbalancierte Anfuehrungszeichen")
        if len(kopf) != 2:
            return Entscheid(DIALOG, "[cd] ohne genau ein Ziel")
        ziel = _aufloesen(kopf[1])
        if ziel is None:
            return Entscheid(DIALOG, "cd-Ziel nicht aufloesbar")
        in_claude, ist_gedaechtnis = _ist_claude_ordner(ziel)
        if in_claude and not ist_gedaechtnis:
            return Entscheid(ABWEISEN, "cd unter .claude")
        if _bereich_von(ziel, bereiche) is None and not in_claude:
            return Entscheid(DIALOG, f"cd-Ziel ausserhalb der Bereiche: {ziel}")
        rest = stuecke[1]
        # **A2:** Das cd-Ziel ist hier bereits gegen die Bereiche geprueft.
        # Genau deshalb darf es als Aufloesungsbasis dienen — ein ungeprueftes
        # Ziel waere die Umkehrung des Schutzes.
        _cd_ziel = ziel
    else:
        rest = stuecke[0]
        _cd_ziel = None

    teile = _teile(rest)
    if not teile:
        return Entscheid(DIALOG, "Befehl nicht zerlegbar")

    # `ziel` ist das **bereits geprueffte** cd-Ziel (oder None ohne `cd`).
    return _ein_befehl(teile, roh, bereiche, ist_geheimnis, umgelenkt_nach,
                       basis=_cd_ziel)
