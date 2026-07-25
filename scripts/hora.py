#!/usr/bin/env python3
# <!-- ROLLE: hora -->
"""Hora — der autonome Läufer.

**Wofür:** Adam ist ab Dienstag rund vierzehn Tage nicht erreichbar. Ein
Zeitgeber auf dem **VPS** startet zweimal täglich eine **frische**,
nicht-interaktive Sitzung, die eine **vorab freigegebene** Auftragsliste
abarbeitet, berichtet und endet.

**Warum nicht auf dem Mac:** Ein Rechner, der vierzehn Tage wach bleiben muss,
ist das zerbrechlichste Glied der Kette.

**Warum je Lauf eine frische Sitzung:** Eine Sitzung, die vierzehn Tage lebt,
stirbt sicher. Hora liest seinen Zustand stattdessen aus Drehbuch, Status-Zeilen,
Auftragsliste und `WIEDERANLAUF.md` — also aus dem, was ohnehin die Wahrheit ist.

**Kein Widerspruch zu 8.7:** Die Repo-Schreibsperre gilt der **Bot-Sitzung**,
nicht jedem Prozess auf dem Server. Hora ist eine getrennte Instanz mit eigenem
Auftragsbuch.

## Die fünf Bedingungen — jede im Code, nicht nur im Text

1. **Nur vorab freigegebene Arbeit, keine neuen Entscheidungen.** Was Adams
   Zustimmung bräuchte, wird über **9.4 geparkt**, nicht entschieden.
2. **Die Liste muss voll sein, bevor Adam geht** — ist sie leer, meldet Hora das
   und tut nichts.
3. **Jeder Lauf endet grün oder rollt zurück.** Der Regressionslauf ist das Maß;
   ein roter Stand wird nicht stehen gelassen.
4. **Abbruchkriterium:** Nach drei Fehlläufen in Folge wird **gemeldet statt
   weitergearbeitet**. Ein Läufer, der gegen dieselbe Wand rennt, richtet mehr
   Schaden an als einer, der stehen bleibt.
5. **Tagesbericht ins Postfach** — auch wenn nichts zu tun war.

## Zur Kontingent-Frage — bewusst ohne Annahme gebaut

Die Wochengrenzen des Abos lassen sich von hier aus **nicht** messen. Statt sie
zu raten, ist Hora so gebaut, dass er sie **nicht kennen muss**: Er arbeitet
**einen** Auftrag je Lauf, misst seinen eigenen Verbrauch mit, und die
Limit-Behandlung des Bots (5.31) trägt den Rest — beim Anschlagen wird pausiert
und später fortgesetzt. Ein Plan, der auf einer geratenen Zahl steht, wäre
schlechter als einer, der ohne sie auskommt.

Aufruf: ``python3 scripts/hora.py [--liste …] [--trocken]``
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

import freigaben  # noqa: E402

ZUSTAND = Path(os.environ.get("HORA_DIR") or (Path.home() / ".claude" / "hora"))
LISTE = Path(os.environ.get("HORA_LISTE") or (ZUSTAND / "auftragsliste.json"))
PROTOKOLL = ZUSTAND / "laeufe.jsonl"
POSTFACH = Path(os.environ.get("POSTFACH_DIR")
                or (Path.home() / "postfach")) / "outbox"
FEHLGRENZE = 3
REGRESSION = REPO / "scripts" / "regressionstest.sh"


# ------------------------------------------------------------ Auftragsliste --
def auftraege() -> list[dict]:
    try:
        daten = json.loads(LISTE.read_text(encoding="utf-8"))
    except Exception:
        return []
    return [a for a in daten if isinstance(a, dict) and a.get("titel")
            and not a.get("erledigt")]


def _liste_schreiben(daten: list[dict]) -> None:
    ZUSTAND.mkdir(parents=True, exist_ok=True)
    tmp = LISTE.with_suffix(".tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.replace(LISTE)


def abhaken(titel: str, ergebnis: str) -> None:
    try:
        daten = json.loads(LISTE.read_text(encoding="utf-8"))
    except Exception:
        return
    for a in daten:
        if a.get("titel") == titel:
            a["erledigt"] = True
            a["ergebnis"] = ergebnis[:400]
            a["erledigt_am"] = time.strftime("%Y-%m-%d %H:%M")
    _liste_schreiben(daten)


# ------------------------------------------------------------------ Messen ---
def regression() -> tuple[bool, str]:
    """Bedingung 3: Der Regressionslauf ist das Maß, nicht das Gefühl."""
    try:
        p = subprocess.run(["bash", str(REGRESSION)], cwd=str(REPO),
                           capture_output=True, text=True, timeout=1800)
        letzte = [z for z in (p.stdout or "").splitlines() if "Ergebnis:" in z]
        return p.returncode == 0, (letzte[-1] if letzte else "(keine Ausgabe)")
    except Exception as e:
        return False, f"Testlauf-Fehler: {e}"


def _fehlserie(neu: bool | None = None) -> int:
    """Zählt Fehlläufe in Folge (Bedingung 4)."""
    p = ZUSTAND / "fehlserie.json"
    try:
        n = int(json.loads(p.read_text(encoding="utf-8")).get("n", 0))
    except Exception:
        n = 0
    if neu is not None:
        n = 0 if neu else n + 1
        try:
            ZUSTAND.mkdir(parents=True, exist_ok=True)
            p.write_text(json.dumps({"n": n, "zuletzt": time.strftime("%Y-%m-%d %H:%M")}),
                         encoding="utf-8")
        except Exception:
            pass
    return n


def melden(text: str) -> None:
    ziel = (os.environ.get("ALLOWED_USER_IDS") or "").split(",")[0].strip()
    if not ziel.isdigit():
        try:
            prefs = json.loads((Path.home() / ".config" / "claude-telegram-bot"
                                / "prefs.json").read_text(encoding="utf-8"))
            ziel = next((str(k) for k in prefs if str(k).isdigit()), "")
        except Exception:
            ziel = ""
    if not ziel.isdigit():
        return
    try:
        POSTFACH.mkdir(parents=True, exist_ok=True)
        tmp = POSTFACH / f".hora{time.time_ns()}.tmp"
        tmp.write_text(json.dumps({"target_chat_id": int(ziel), "text": text},
                                  ensure_ascii=False), encoding="utf-8")
        tmp.rename(POSTFACH / f"hora-{time.time_ns()}.json")
    except Exception:
        pass


def _protokollieren(eintrag: dict) -> None:
    try:
        ZUSTAND.mkdir(parents=True, exist_ok=True)
        with PROTOKOLL.open("a", encoding="utf-8") as f:
            f.write(json.dumps(eintrag, ensure_ascii=False) + "\n")
    except Exception:
        pass


# -------------------------------------------------------------------- Lauf ---
def lauf(trocken: bool = False) -> int:
    """Ein Hora-Lauf. Rückgabe 0 = gut, 1 = gemeldet, 2 = angehalten."""
    beginn = time.strftime("%Y-%m-%d %H:%M")

    # Bedingung 4 zuerst: Wer schon dreimal gescheitert ist, fängt nicht wieder an.
    if _fehlserie() >= FEHLGRENZE:
        melden(f"⏸️ Hora hält an ({beginn}): {FEHLGRENZE} Fehlläufe in Folge. "
               "Ich arbeite nicht weiter, bis du hingesehen hast — ein Läufer, "
               "der gegen dieselbe Wand rennt, richtet mehr Schaden an als einer, "
               "der stehen bleibt.\nZum Fortsetzen die Datei "
               f"{ZUSTAND / 'fehlserie.json'} entfernen.")
        return 2

    offen = auftraege()
    if not offen:
        # Bedingung 2 + 5: Auch Leerlauf wird berichtet.
        melden(f"🌾 Hora ({beginn}): Die Auftragsliste ist leer — ich habe "
               "nichts angefasst. Wenn etwas laufen soll, trag es in die Liste "
               "ein; ohne Eintrag entscheide ich nichts von selbst.")
        return 0

    # Bedingung 3, erste Hälfte: Auf rotem Fundament wird nicht gearbeitet
    # (dieselbe Regel wie A5 im Updater).
    vorher_ok, vorher = regression()
    if not vorher_ok:
        _fehlserie(False)
        melden(f"🔴 Hora ({beginn}): Der Regressionslauf war schon **vor** der "
               f"Arbeit rot ({vorher}). Ich habe nichts angefasst — auf einem "
               "roten Fundament zu bauen macht die Ursachensuche unmöglich.")
        return 1

    auftrag = offen[0]                      # einer je Lauf — Kontingent-schonend
    titel = auftrag["titel"]

    # Bedingung 1: Braucht der Auftrag eine Entscheidung, wird er GEPARKT.
    if auftrag.get("braucht_zustimmung"):
        try:
            freigaben.stellen(
                titel=titel,
                aktion=auftrag.get("aktion") or titel,
                ampel=auftrag.get("ampel", "gelb"),
                herkunft="Hora",
                begruendung=auftrag.get("begruendung", ""),
                rueckweg=auftrag.get("rueckweg", ""))
            abhaken(titel, "zur Freigabe geparkt")
            melden(f"🗝️ Hora ({beginn}): „{titel}“ braucht deine Zustimmung — "
                   "ich habe es ins Freigabe-Postfach gelegt statt zu "
                   "entscheiden. Antwortest du nicht, gilt es als abgelehnt.")
            return 0
        except freigaben.Abgewiesen as e:
            abhaken(titel, f"nicht parkbar: {e}")
            melden(f"⚠️ Hora ({beginn}): „{titel}“ lässt sich nicht einmal "
                   f"parken — {e}. Übersprungen.")
            return 1

    if trocken:
        melden(f"🧪 Hora-Probelauf ({beginn}): Ich HÄTTE jetzt „{titel}“ "
               f"bearbeitet. Fundament vorher: {vorher}. Es wurde nichts getan.")
        return 0

    # Die eigentliche Arbeit übernimmt eine frische, nicht-interaktive Sitzung.
    befehl = auftrag.get("befehl")
    if not befehl:
        abhaken(titel, "kein ausführbarer Befehl hinterlegt")
        melden(f"⚠️ Hora ({beginn}): „{titel}“ hat keinen ausführbaren Befehl — "
               "übersprungen. (Hora führt nur aus, was in der Liste steht.)")
        return 1
    try:
        p = subprocess.run(["bash", "-lc", befehl], cwd=str(REPO),
                           capture_output=True, text=True, timeout=7200)
        ausgabe = ((p.stdout or "") + (p.stderr or ""))[-1200:]
        erfolg = p.returncode == 0
    except Exception as e:
        ausgabe, erfolg = str(e), False

    # Bedingung 3, zweite Hälfte: grün oder zurück.
    nachher_ok, nachher = regression()
    if erfolg and nachher_ok:
        _fehlserie(True)
        abhaken(titel, f"erledigt · {nachher}")
        melden(f"✅ Hora ({beginn}): „{titel}“ erledigt.\n{nachher}\n"
               f"Noch offen: {max(0, len(offen) - 1)} Auftrag/Aufträge.")
        _protokollieren({"zeit": beginn, "titel": titel, "ergebnis": "gruen",
                         "regression": nachher})
        return 0

    n = _fehlserie(False)
    _protokollieren({"zeit": beginn, "titel": titel, "ergebnis": "rot",
                     "regression": nachher, "ausgabe": ausgabe[-400:]})
    melden(f"🔴 Hora ({beginn}): „{titel}“ ist nicht sauber durchgelaufen "
           f"({nachher}). Der Auftrag bleibt offen, ich habe nichts abgehakt. "
           f"Fehlläufe in Folge: {n} von {FEHLGRENZE}.\n"
           f"Letzte Ausgabe:\n{ausgabe[-500:]}")
    return 1


def main() -> int:
    ap = argparse.ArgumentParser(description="Hora — autonomer Läufer")
    ap.add_argument("--liste", help="andere Auftragsliste verwenden")
    ap.add_argument("--trocken", action="store_true",
                    help="prüfen und melden, aber nichts ausführen")
    a = ap.parse_args()
    if a.liste:
        globals()["LISTE"] = Path(a.liste)
    return lauf(trocken=a.trocken)


if __name__ == "__main__":
    sys.exit(main())
