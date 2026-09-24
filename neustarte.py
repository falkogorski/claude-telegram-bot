"""Stille Neustarts — wann einer schweigt, und wer mitzählt.

`[NEU 24.09.2026, Block 3 Teil 2]` Claudias Auftrag 3 vom 19.09. (Adams
Sprachnachricht 14:54): *„Wenn alles gut funktioniert, brauche ich die Info gar
nicht, dass Telegram weggebrochen ist. Das kann hundertmal am Tag sein und
interessiert mich nicht. Das ist nur dann interessant, wenn irgendwas anderes
deswegen ins Stocken gerät."*

Engywucks Ergänzung 2 (Nachtlese 19.09.) und sein Zettel vom 24.09.: Ein
Neustart wird still — aber **der dritte an einem Tag ist ein Befund**, sonst
sieht eine Neustart-Schleife aus wie Ruhe. Zeitraum ein Tag, **gezählt im
Tagescheck**, Rücksetzung um vier.

Deshalb zwei Hälften mit getrennten Besitzern:
- **Der Bot** entscheidet beim Start, ob er schweigt (`still`), und
  VERMERKT jeden stillen Neustart hier (`vermerken`) — mit Grund.
- **Der Tagescheck** zählt um 04:10 nur (`zaehlen`), er schreibt nichts:
  Die Datei gehört claudebot, und der Tagescheck läuft als root — eine
  root-eigene Datei könnte der Bot nie wieder beschreiben (dieselbe Lehre wie
  bei `kanaele.json`). Die „Rücksetzung" ist deshalb ein Zeitfenster, kein
  Löschen.

Nur Standardbibliothek: Der Tagescheck ruft dies mit der Bot-Umgebung, aber
ohne den Bot zu laden.
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path

# Ab dieser Zahl je Tag meldet der Tagescheck laut (Engywuck: „ab dem dritten").
SCHWELLE = 3
# Die Datei wächst nicht unbegrenzt: beim Vermerken auf die letzten N gekürzt.
BEHALTEN = 200
# Die Tagesgrenze: Rücksetzung um vier (Zettel 24.09.).
TAGESGRENZE_STUNDE = 4


LAUT = "[LAUT]"    # Kopf eines Grundes, den Adam selbst ausgelöst hat (/restart)
STILL = "[STILL]"  # Kopf des planmäßigen Hygiene-Neustarts (Timer 04:00)
OHNE_GRUND = "ohne hinterlegten Grund (Dienst neu gestartet)"


def grund_lesen(text: str) -> dict:
    """Den hinterlegten Neustart-Grund zerlegen: wer hat ausgelöst, was wird
    gemeldet, was wird vermerkt. Der [AUTORUN]-Teil bleibt in der Meldung
    (der Bot schneidet ihn danach ab), gehört aber nicht in den Vermerk."""
    t = (text or "").strip()
    planmaessig = adam = False
    if t.startswith(STILL):
        planmaessig = True
        t = t[len(STILL):].strip() or "🌙 Nächtlicher Hygiene-Neustart (4-Uhr-Fenster)."
    elif t.startswith(LAUT):
        adam = True
        t = t[len(LAUT):].strip()
    grund = t.split("[AUTORUN]:", 1)[0].strip() or OHNE_GRUND
    return {"planmaessig": planmaessig, "adam_ausgeloest": adam, "meldung": t, "grund": grund}


def datei() -> Path:
    return Path(os.environ.get("STILLE_NEUSTARTS")
                or Path.home() / ".claude" / "stille-neustarts.jsonl")


def still(*, adam_ausgeloest: bool, nachzuholen: bool, selbstcheck_rot: bool,
          auftraege: bool) -> bool:
    """Schweigt dieser Neustart? Claudias drei Bedingungen, **gleich aus welchem
    Grund er ausgelöst wurde**: (a) Selbstcheck grün, (b) nichts nachzuholen,
    (c) nichts in der Warteschlange.

    Die eine Ausnahme ist **Adams eigener `/restart`**: Der Bot antwortet darauf
    „ich melde mich gleich wieder" — bliebe die Meldung aus, merkte Adam es.
    Claudias Auflage: *„Lautstark bleibt nur, was Adam merken würde."*"""
    return not (adam_ausgeloest or nachzuholen or selbstcheck_rot or auftraege)


def vermerken(grund: str, *, jetzt: float | None = None, pfad: Path | None = None) -> None:
    """Einen stillen Neustart festhalten. Der Aufrufer tut das in einer EIGENEN
    Klammer (Regel vom 10.09.): Ein Fehler hier darf den Start nicht berühren."""
    p = pfad or datei()
    p.parent.mkdir(parents=True, exist_ok=True)
    zeile = json.dumps({"zeit": jetzt if jetzt is not None else time.time(),
                        "grund": (grund or "").strip()[:200]}, ensure_ascii=False)
    alt = p.read_text(encoding="utf-8").splitlines() if p.exists() else []
    neu = (alt + [zeile])[-BEHALTEN:]
    tmp = p.with_suffix(".tmp")
    tmp.write_text("\n".join(neu) + "\n", encoding="utf-8")
    os.replace(tmp, p)


def fenster(jetzt: float | None = None) -> "tuple[float, float]":
    """Der letzte volle Tag bis zur jüngsten Vier-Uhr-Grenze."""
    t = datetime.fromtimestamp(jetzt if jetzt is not None else time.time())
    bis = t.replace(hour=TAGESGRENZE_STUNDE, minute=0, second=0, microsecond=0)
    if t < bis:
        bis -= timedelta(days=1)
    return (bis - timedelta(days=1)).timestamp(), bis.timestamp()


def zaehlen(*, jetzt: float | None = None, pfad: Path | None = None) -> "tuple[int, list[str]]":
    """Anzahl und Gründe der stillen Neustarts im Fenster. Nur lesend.
    Eine unlesbare Zeile wird mitgezählt — ein Neustart, dessen Vermerk
    beschädigt ist, bleibt ein Neustart."""
    p = pfad or datei()
    if not p.exists():
        return 0, []
    von, bis = fenster(jetzt)
    n, gruende = 0, []
    for roh in p.read_text(encoding="utf-8").splitlines():
        if not roh.strip():
            continue
        try:
            e = json.loads(roh)
            z = float(e.get("zeit", 0))
        except (ValueError, TypeError, AttributeError):
            n += 1
            gruende.append("Vermerk unlesbar")
            continue
        if von <= z < bis:
            n += 1
            gruende.append(e.get("grund") or "ohne Grund")
    return n, gruende


def befund(n: int, gruende: "list[str]") -> "tuple[str, str]":
    """(Tür, Satz) für den Tagescheck: `adam` ab der Schwelle, sonst `protokoll`."""
    if n >= SCHWELLE:
        haeufig = sorted(set(gruende), key=gruende.count, reverse=True)[:3]
        return ("adam", f"{n} stille Neustarts gestern (Fenster bis vier Uhr) — das "
                        f"sieht nach einer Schleife aus, nicht nach Zufall. Gründe: "
                        + "; ".join(haeufig))
    if n:
        return ("protokoll", f"Stille Neustarts gestern: {n} ({'; '.join(gruende)})")
    return ("protokoll", "Keine stillen Neustarts gestern")


if __name__ == "__main__":
    # Aufruf aus dem Tagescheck: `TUER<TAB>SATZ` auf einer Zeile.
    tuer, satz = befund(*zaehlen())
    print(f"{tuer}\t{satz}")
