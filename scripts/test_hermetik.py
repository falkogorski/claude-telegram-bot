#!/usr/bin/env python3
# <!-- ROLLE: test-hermetik -->
"""Kein Prüflauf darf Betriebszustand anfassen — **die Lehre aus Befund L.**

**Was geschehen ist** (Engywuck, 23.08.): Zwölf Testdateien setzten
`USER_PREFS_FILE` und hielten sich für isoliert. `bot.py` hat die Variable
**nie gelesen** — der Pfad war fest auf `Path.home()` verdrahtet. Jeder
Regressionslauf beschrieb damit die echte `prefs.json`.

Auf dem VPS gemessen: `output_channel_id`, `summary_channel_id` und
`tts_channel_id` standen auf der Test-Attrappe `-1001234567890`, dazu eine
Dauerfreigabe für die Testkennung 4711. Der Bot hätte alle Ausgaben in einen
Kanal gelenkt, den es nicht gibt — **ohne Fehlermeldung**, weil ein unbekannter
Kanal nichts wirft, das jemandem auffällt. Ein Bruch, der wie Ruhe aussieht.

**Warum ein eigener Prüfer und nicht bloß fünf nachgetragene Zeilen:** Der
Regressionsläufer trägt seit dem 20.08. den Satz *„Wer eine neue Zustandsablage
einführt, trägt sie im selben Zug in die Wegwerf-Umgebung ein."* Der Satz stand
da — und die Liste war trotzdem an fünf Stellen unvollständig. Eine Regel ohne
Prüfer ist eine Bitte; das ist in diesem Projekt oft genug gemessen worden.

**Was er misst — und was bewusst nicht:** Er misst eine **Abwesenheit** (eine
Ablage, die im Läufer fehlt), und Abwesenheit lässt sich nicht ausführen. Das
ist der ausdrücklich erlaubte Fall der Regel vom 22.08.; die **Wirkung** — dass
die gesetzten Werte auch wirklich ankommen — misst `test_eingangsschranken.py`
in der Zeile „keine Betriebsablage wird angefasst", und zwar am Zustand der
geladenen Module. Beide zusammen decken den Befund: dieser hier die Lücke, der
andere die tote Variable.
"""
import re
import sys
from pathlib import Path

WURZEL = Path(__file__).resolve().parent.parent
LAEUFER = WURZEL / "scripts" / "regressionstest.sh"

# Ablagen, die absichtlich NICHT umgebogen werden — mit dem Grund daneben.
# Jeder Eintrag hier ist eine Entscheidung, kein Automatismus: Eine lange
# Ausnahmeliste höhlt den Prüfer aus, genau wie bei den Stichwort-Filtern.
GEWOLLT_OFFEN = {
    # Der Läufer setzt es bewusst nur für EINEN Aufruf, nicht global: Ein Test
    # muss das echte Gedächtnis lesen können, ohne hineinzuschreiben.
    "CLAUDE_MEMORY_DIR": "wird gezielt pro Aufruf gesetzt, nicht global",
}

_MUSTER = re.compile(r'os\.environ\.get\(\s*["\']([A-Z][A-Z0-9_]*(?:_DIR|_FILE))["\']')


def eigene_module() -> list[Path]:
    """Nur unsere eigenen Module — keine Abhängigkeiten, kein Prüfstand."""
    return sorted(p for p in WURZEL.glob("*.py") if not p.name.startswith("test_"))


def main() -> int:
    laeufer = LAEUFER.read_text(encoding="utf-8")
    fehlt: dict[str, list[str]] = {}

    for datei in eigene_module():
        for name in _MUSTER.findall(datei.read_text(encoding="utf-8")):
            if name in GEWOLLT_OFFEN:
                continue
            if re.search(rf'^\s*export\s+{re.escape(name)}=', laeufer, re.M):
                continue
            fehlt.setdefault(name, []).append(datei.name)

    print("Hermetik der Prüfläufe")
    print("=" * 40)
    for name, grund in sorted(GEWOLLT_OFFEN.items()):
        print(f"○ {name} — bewusst offen: {grund}")

    if fehlt:
        print()
        for name, dateien in sorted(fehlt.items()):
            print(f"✗ {name} ({', '.join(dateien)}) wird im Regressionsläufer "
                  f"NICHT umgebogen — ein Lauf schreibt in den Betrieb")
        print()
        print(f"❌ {len(fehlt)} Ablage(n) ohne Riegel. Nachtragen in "
              f"scripts/regressionstest.sh, oder mit Begründung in "
              f"GEWOLLT_OFFEN aufnehmen.")
        return 1

    gezaehlt = sum(1 for d in eigene_module()
                   for _ in _MUSTER.findall(d.read_text(encoding="utf-8")))
    print()
    print(f"✓ alle {gezaehlt} umbiegbaren Ablagen sind im Läufer verriegelt")

    fehler = pfade_fest_verdrahtet()
    if fehler:
        print()
        for datei, zeile, text in fehler:
            print(f"✗ {datei}:{zeile} — fest verdrahteter Betriebspfad: {text}")
        print()
        print(f"❌ {len(fehler)} fest verdrahtete(r) Pfad(e). Solche Prüfer sind "
              f"ortsabhängig blind: grün an einem Rechner, wirkungslos am anderen. "
              f"Stattdessen bot._REPO_DIR / bot.WORKDIR verwenden.")
        return 1
    print("✓ kein Prüfer trägt einen fest verdrahteten Betriebspfad")
    print("== Hermetik: bestanden ==")
    return 0


def _ist_ortsabhaengig(wert: str) -> bool:
    """Nur die zwei Formen, die tatsächlich gebrochen sind — nicht jeder Pfad.

    **Warum so eng:** Der erste Entwurf dieses Prüfers schlug bei sieben
    Stellen an, von denen **sechs berechtigt** waren: Textmuster-Werte für
    `_is_sensitive_ref`, wo ein fester Pfad genau der Testgegenstand ist. Eine
    davon war sogar ein **Docstring** — der Prüfer stolperte über die
    Beschreibung seines eigenen Gegenstands, exakt der Fehler, den die Regel
    vom 22.08. benennt. Ein Prüfer, der sechsmal grundlos anschlägt, wird
    binnen einer Woche abgeschaltet und prüft dann gar nichts mehr.

    Übrig bleiben die zwei Formen, bei denen der Pfad gegen **ortsabhängige**
    Logik läuft:

    * **Die Repo-Wurzel** (`…/claude-telegram-bot`, `~/claude-telegram-bot`) —
      sie wird seit Befund D/E aufgelöst und mit `_REPO_DIR` verglichen.
    * **Das nackte Heimverzeichnis** (`/home/claudebot` exakt) — es dient als
      Stellvertreter für `WORKDIR`. Genau daran blieb meine eigene F-Zeile bei
      entferntem Schutz grün: Am Mac ist es nicht das Arbeitsverzeichnis, auf
      dem VPS ist es genau das.

    Unterpfade wie `/home/claudebot/.bash_history` sind Textmuster und bleiben
    zu Recht draußen.
    """
    w = wert.rstrip("/")
    # `"~"` allein war im ersten Entwurf mit drin — und traf sofort drei
    # harmlose Stellen. Ein Prüfer, der bei einer Tilde anschlägt, ist Lärm.
    if w == "/home/claudebot":
        return True
    return "claude-telegram-bot" in w and (
        w.startswith("/home/claudebot") or w.startswith("~/"))


def pfade_fest_verdrahtet() -> list[tuple[str, int, str]]:
    """Trägt ein Prüfer einen Betriebspfad fest ein? — **viermal an einem Tag.**

    Am 23.08. sind bei der Abarbeitung von Engywucks Befund **vier** Prüfer
    aufgefallen, die `/home/claudebot/claude-telegram-bot` oder
    `~/claude-telegram-bot` fest eingetragen hatten: die Eingangsschranken, der
    Selbstcheck, der E4-Prüfer — und eine Zeile, die ich am selben Tag **selbst
    neu geschrieben** hatte.

    **Warum das lange unsichtbar blieb:** Solange die geprüfte Logik nur
    Zeichenketten verglich, war der Pfad gleichgültig; die Prüfer waren
    pfadunabhängig grün. Seit Befund D/E löst die Logik Pfade auf — und
    plötzlich misst ein fester Pfad am Bau-Ort etwas anderes als im Betrieb.

    Die schlimmere Richtung ist nicht „rot am Mac", sondern **„grün aus dem
    falschen Grund"**: Meine eigene F-Zeile blieb bei entferntem Schutz grün,
    weil `/home/claudebot` am Mac nicht das Arbeitsverzeichnis ist. Auf dem VPS
    ist es genau das — dort wäre das Loch offen gewesen und der Prüfer still.

    Dieselbe Klasse wie der 29.07., als ein `$HOME` in einem root-Dienst einen
    täglichen Wächter einundzwanzig Tage lang tötete. **Am Mac lief alles.**

    Gemessen wird über den **Syntaxbaum**, nicht über den Text: Kommentare gibt
    es dort nicht, und Docstrings lassen sich gezielt ausnehmen. Genau daran
    ist der erste Entwurf gescheitert — er las Zeilen und schlug in der eigenen
    Erklärung an.
    """
    import ast
    raus = []
    # Die eigene Datei ausgenommen: Sie TRÄGT die Muster als Gegenstand. Ein
    # Prüfer, der über die Beschreibung seines eigenen Gegenstands stolpert,
    # wird binnen einer Woche abgeschaltet (Regel vom 22.08.) — beim ersten
    # Lauf hat er genau das getan.
    dateien = [d for d in sorted(WURZEL.glob("scripts/test_*.py"))
               if d.name != "test_hermetik.py"] + [WURZEL / "bot.py"]
    for datei in dateien:
        try:
            baum = ast.parse(datei.read_text(encoding="utf-8"))
        except SyntaxError:
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
                raus.append((datei.name, knoten.lineno, knoten.value))
    return raus


if __name__ == "__main__":
    sys.exit(main())
