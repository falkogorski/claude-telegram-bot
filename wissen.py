# <!-- ROLLE: wissensablage -->
"""Wissensdatenbank, nach und nach (Block 6, Teil 2 — Fassung 5, 6.4).

`[NEU 24.09.2026]` Adams Vorgabe vom 24.09., 01:19: Zusammenfassungen
bleiben, statt im Chat zu verschwinden. **Dateien und ein Index, kein neues
System** — der Recall-Punkt des Drehbuchs in seiner kleinsten Form.

Ablage `~/workspace/wissen/<jahr>/<quelle>_<datum>_<kurztitel>.md`, je Datei
ein Kopf (Quelle, Adresse, Datum, Grundlage, Herkunftsvermerk), dazu
`wissen/INDEX.md`, den der Bot bei Fragen liest. **Ohne Herkunftsvermerk wird
nicht abgelegt** — eine Zusammenfassung, deren Herkunft niemand mehr kennt,
ist später nicht mehr prüfbar (Adams Entscheid 23.09.: Herkunftsvermerk am
Ende jeder Auswertung Pflicht).

Der Log-Abgleich trägt `wissen/` mit (er nimmt `*.md` aus dem Arbeitsordner).
"""
from __future__ import annotations

import os
import re
import unicodedata
from pathlib import Path


def ordner() -> Path:
    roh = os.environ.get("WISSEN_DIR")
    if roh:
        return Path(roh)
    arbeit = os.environ.get("CLAUDE_ARBEITSORDNER")
    return (Path(arbeit) if arbeit else Path.home() / "workspace") / "wissen"


def _kurz(text: str, grenze: int) -> str:
    t = unicodedata.normalize("NFKD", text or "")
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:grenze] or "ohne-titel"


class Abgewiesen(ValueError):
    pass


def ablegen(*, titel: str, quelle: str, adresse: str, datum: str,
            grundlage: str, herkunft: str, text: str) -> Path:
    """Eine Zusammenfassung ablegen und im Index eintragen. Gibt den Pfad zurück."""
    if not (herkunft or "").strip():
        raise Abgewiesen("ohne Herkunftsvermerk wird nicht abgelegt")
    if not (text or "").strip():
        raise Abgewiesen("leere Zusammenfassung")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", datum or ""):
        raise Abgewiesen("Datum fehlt oder ist nicht JJJJ-MM-TT")
    jahr = datum[:4]
    ziel_ordner = ordner() / jahr
    ziel_ordner.mkdir(parents=True, exist_ok=True)
    ziel = ziel_ordner / f"{_kurz(quelle, 30)}_{datum}_{_kurz(titel, 50)}.md"
    kopf = (f"# {titel.strip()}\n\n"
            f"- **Quelle:** {quelle}\n- **Adresse:** {adresse}\n- **Datum:** {datum}\n"
            f"- **Grundlage:** {grundlage}\n- **Herkunft:** {herkunft.strip()}\n\n---\n\n")
    ziel.write_text(kopf + text.strip() + "\n", encoding="utf-8")
    index = ordner() / "INDEX.md"
    rel = ziel.relative_to(ordner()).as_posix()
    bestand = index.read_text(encoding="utf-8") if index.exists() else (
        "# Wissen — Index\n\nJe Zeile eine Zusammenfassung. Der Bot liest diese Datei bei Fragen.\n\n")
    if f"]({rel})" not in bestand:
        bestand += f"- {datum} · {quelle} · [{titel.strip()}]({rel}) — {grundlage}\n"
        index.write_text(bestand, encoding="utf-8")
    return ziel
