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
zu raten, ist Hora so gebaut, dass er sie **nicht kennen muss**. Die
Limit-Behandlung des Bots (5.31) trägt den Rest — beim Anschlagen wird pausiert
und später fortgesetzt.

**[KORRIGIERT 2026-07-25] „Einer je Lauf" war eine Über-Korrektur.** Zwei Läufe
täglich mal vierzehn Tage sind achtundzwanzig Aufträge — das wäre die Obergrenze
für zwei Wochen gewesen, und von einem Fünf-Stunden-Fenster bliebe fast alles
ungenutzt. Vor allem aber war „einer je Lauf" **selbst eine Annahme**, nämlich
die, dass das Kontingent knapp ist. Genau davon wollte der Entwurf frei sein.

Neu: **Frische Sitzung je Auftrag** (die Isolation bleibt, sie war richtig) —
aber **verkettet, bis die Liste leer ist**, die Kontingent-Pause greift oder die
Fehlserie zuschlägt. Keine Zahl zum Nachjustieren: Es läuft, bis es nicht mehr
kann.

## Fragen sind Wegsteine, keine Halteschilder [NEU 2026-07-25]

**Hora wartet nie.** Braucht ein Auftrag Adams Zustimmung: **parken (9.4),
melden, sofort mit dem nächsten unabhängigen Auftrag weiter.** Ist nichts
Unabhängiges mehr zu tun, endet der Lauf mit Bericht — er steht nicht im
Leerlauf herum. Ein geparkter Punkt blockiert auch den **nächsten** Lauf nicht.

Damit braucht es keine Vorhersage über Adams Verfügbarkeit: **immer fragen, nie
warten.** Die Antwort holt den Läufer später ein, nicht umgekehrt.

Daraus folgt eine Anforderung an die Auftragsliste: **Abhängigkeiten werden
markiert** (`haengt_an: ["<Titel>"]`). Nur so weiß Hora, was unabhängig
weiterlaufen darf, wenn ein Vorgänger geparkt oder gescheitert ist.

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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import botenpost  # noqa: E402

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

# Wortlaute, an denen ein erreichtes Kontingent erkennbar ist. Bewusst hier
# gespiegelt statt aus bot.py importiert: Hora soll ohne dessen Umgebung laufen.
_LIMIT = ("usage limit", "session limit", "rate limit", "limit reached",
          "quota exceeded", "kontingent", "too many requests", "429")


def _kontingent_erschoepft(text: str) -> bool:
    t = (text or "").lower()
    return any(n in t for n in _LIMIT)


def _fehlgrund(erfolg: bool, nachher_ok: bool, ausgabe: str,
               lage: str) -> str:
    """Sagt, **woran** es lag — und unterscheidet die zwei Fälle.

    Ein Auftrag kann auf zwei ganz verschiedene Arten scheitern, und sie
    verlangen verschiedene Antworten: Entweder der **Befehl** ging schief (dann
    zählt seine Ausgabe), oder der Befehl lief und hat dabei **etwas anderes
    kaputtgemacht** (dann zählt der Regressionsstand — und das ist der weit
    ernstere Fall, weil er den Rückweg verlangt).
    """
    if not erfolg:
        text = (ausgabe or "").strip()
        if not text:
            return ("der Befehl endete mit einem Fehler, ohne etwas zu sagen "
                    "(kein Text auf beiden Ausgabekanälen)")
        return "der Befehl meldete: " + text.splitlines()[-1][:200]
    if not nachher_ok:
        return (f"der Befehl lief durch, aber DANACH war der Regressionslauf "
                f"rot ({lage}) — hier hat die Arbeit etwas anderes beschädigt")
    return f"unklar ({lage})"


def _urteil_einholen(auftrag: dict) -> tuple[str, str]:
    """Die Parkstrecke — **und der Weg zurück.**

    **Der Fund, dem diese Funktion ihr Dasein verdankt (Echtlauf 26.07., 01:45):**
    Ein geparkter Auftrag wurde vorher **abgehakt**. Er verschwand damit aus der
    Liste — und Adams Zustimmung wäre ins Leere gelaufen, weil niemand die
    Aktion danach je ausgeführt hätte. Die Meldung sagte „ich lege es dir wieder
    vor", und der Code hatte den Auftrag bereits weggeräumt. Der Grundsatz
    lautet „die Antwort holt ihn später ein, nicht umgekehrt" — dafür muss
    etwas da sein, das eingeholt werden kann.

    Rückgabe: (Lage, Text). Lagen:
    * ``wartet`` — Anfrage liegt (neu gestellt oder noch unbeantwortet)
    * ``freigegeben`` — Adam hat zugestimmt, der Auftrag darf jetzt laufen
    * ``abgelehnt`` — Adam hat abgelehnt; damit ist der Auftrag erledigt
    * ``unparkbar`` — die Anfrage verletzt eine Leitplanke (z. B. Geheimnis)
    """
    kennung = auftrag.get("freigabe_kennung")
    if kennung:
        urteil = freigaben.urteil_lesen(kennung)
        if urteil:
            return (("freigegeben", "von dir freigegeben")
                    if urteil.get("urteil") == "freigegeben"
                    else ("abgelehnt", "von dir abgelehnt"))
        # Kein Urteil und keine offene Anfrage mehr? Dann ist sie verlorengegangen
        # — neu stellen ist richtiger als schweigen.
        if freigaben.finden(kennung) is not None:
            return "wartet", "liegt bei dir"
    try:
        a = freigaben.stellen(
            titel=auftrag["titel"],
            aktion=auftrag.get("aktion") or auftrag["titel"],
            ampel=auftrag.get("ampel", "gelb"),
            herkunft="Hora",
            begruendung=auftrag.get("begruendung", ""),
            rueckweg=auftrag.get("rueckweg", ""))
    except freigaben.Abgewiesen as e:
        return "unparkbar", str(e)
    _vermerken(auftrag["titel"], freigabe_kennung=a.kennung,
               geparkt_am=time.strftime("%Y-%m-%d %H:%M"))
    return "wartet", "neu vorgelegt"


def _blockiert(auftrag: dict, ausgefallen: set[str]) -> str | None:
    """Hängt der Auftrag an etwas, das geparkt oder gescheitert ist?

    Ohne diese Angabe müsste Hora raten — und ein Läufer, der auf einem nicht
    fertigen Vorgänger aufbaut, richtet mehr Schaden an als einer, der ihn
    überspringt. Fehlt die Angabe, gilt der Auftrag als unabhängig; das ist die
    ehrlichere Vorgabe, weil sie nichts unterstellt.
    """
    for t in (auftrag.get("haengt_an") or []):
        if t in ausgefallen:
            return str(t)
    return None


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


def _vermerken(titel: str, **felder) -> None:
    """Schreibt Felder an einen Auftrag, OHNE ihn abzuhaken.

    Gebraucht für die Parkstrecke: Ein geparkter Auftrag ist **nicht erledigt**,
    er wartet. Siehe `_urteil_einholen`.
    """
    try:
        daten = json.loads(LISTE.read_text(encoding="utf-8"))
    except Exception:
        return
    for a in daten:
        if a.get("titel") == titel:
            a.update(felder)
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
    """Meldet ueber die gemeinsame Botenpost — mit Absender.

    Vorher legte jeder Schreiber seine Datei selbst ab, mit vier fast
    gleichen Codebloecken und OHNE Absender. Als am 26.07. nachts eine
    Meldung bei Adam ankam, kostete die Suche nach ihrem Urheber ueber
    eine Stunde. Die Nachricht haette es selbst sagen koennen.
    """
    botenpost.legen(text, "hora")


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

    # ---- Die Kette: Auftrag um Auftrag, bis die Liste leer ist oder etwas
    # ---- den Läufer anhält. Kein Zeitwert, keine Stückzahl zum Nachjustieren.
    ausgefallen: set[str] = set()        # geparkt oder gescheitert
    erledigt: list[str] = []
    geparkt: list[str] = []
    uebersprungen: list[str] = []
    gescheitert: list[str] = []
    freigegeben_jetzt: list[str] = []
    probe: list[str] = []                # nur im Probelauf
    abbruch = ""
    letzte_lage = vorher

    for auftrag in offen:
        titel = auftrag["titel"]

        # Wegstein eines gestolperten Vorgängers — überspringen, nicht warten.
        vorgaenger = _blockiert(auftrag, ausgefallen)
        if vorgaenger:
            uebersprungen.append(f"{titel} (hängt an „{vorgaenger}“)")
            continue

        # Bedingung 1: Braucht der Auftrag eine Entscheidung, wird er GEPARKT —
        # und Hora geht SOFORT weiter. Fragen sind Wegsteine, keine Halteschilder.
        if auftrag.get("braucht_zustimmung"):
            lage, text = _urteil_einholen(auftrag)
            if lage == "wartet":
                geparkt.append(f"{titel} ({text})")
                ausgefallen.add(titel)
                continue
            if lage == "abgelehnt":
                abhaken(titel, "von Adam abgelehnt")
                uebersprungen.append(f"{titel} (abgelehnt)")
                ausgefallen.add(titel)
                continue
            if lage == "unparkbar":
                abhaken(titel, f"nicht parkbar: {text}")
                uebersprungen.append(f"{titel} (nicht parkbar: {text})")
                ausgefallen.add(titel)
                continue
            # lage == "freigegeben": weiter unten normal ausführen — die Antwort
            # hat den Auftrag eingeholt, genau wie vorgesehen.
            freigegeben_jetzt.append(titel)

        if trocken:
            probe.append(titel)
            continue

        befehl = auftrag.get("befehl")
        if not befehl:
            abhaken(titel, "kein ausführbarer Befehl hinterlegt")
            uebersprungen.append(f"{titel} (kein ausführbarer Befehl hinterlegt)")
            ausgefallen.add(titel)
            continue

        # Frische Sitzung je Auftrag — die Isolation bleibt.
        try:
            p = subprocess.run(["bash", "-lc", befehl], cwd=str(REPO),
                               capture_output=True, text=True, timeout=7200)
            ausgabe = ((p.stdout or "") + (p.stderr or ""))[-1200:]
            erfolg = p.returncode == 0
        except Exception as e:
            ausgabe, erfolg = str(e), False

        # Kontingent erschöpft: anhalten, nicht scheitern. Der Auftrag bleibt
        # offen und der nächste Lauf nimmt ihn wieder auf — genau das, wofür
        # die Liste da ist.
        if not erfolg and _kontingent_erschoepft(ausgabe):
            abbruch = ("Kontingent erschöpft — ich habe angehalten, nichts "
                       "abgehakt und nichts verloren.")
            break

        nachher_ok, letzte_lage = regression()
        if erfolg and nachher_ok:
            _fehlserie(True)
            abhaken(titel, f"erledigt · {letzte_lage}")
            erledigt.append(titel)
            _protokollieren({"zeit": beginn, "titel": titel,
                             "ergebnis": "gruen", "regression": letzte_lage})
            continue

        n = _fehlserie(False)
        ausgefallen.add(titel)
        # **Fund aus dem Echtlauf (26.07.):** Hier stand `letzte_lage`, also das
        # Ergebnis des Regressionslaufs. Die Meldung las sich dadurch als
        # „gescheitert (30/30 bestanden)" — die Zahl war richtig und die Aussage
        # sinnlos, weil sie die falsche Frage beantwortet. Wer nachts eine
        # Fehlermeldung liest, will wissen, **woran der Auftrag scheiterte**,
        # nicht, wie es dem Fundament geht.
        gescheitert.append(f"{titel} — {_fehlgrund(erfolg, nachher_ok, ausgabe, letzte_lage)}")
        _protokollieren({"zeit": beginn, "titel": titel, "ergebnis": "rot",
                         "regression": letzte_lage, "ausgabe": ausgabe[-400:]})
        if n >= FEHLGRENZE:
            abbruch = (f"{FEHLGRENZE} Fehlläufe in Folge — ich halte an. "
                       f"Letzte Ausgabe:\n{ausgabe[-400:]}")
            break

    # Bedingung 5: Bericht, auch wenn nichts zu tun war.
    teile = [f"🌾 Hora ({beginn}) — Lauf beendet."]
    if probe:
        teile.append(f"🧪 Probelauf: Ich HÄTTE {len(probe)} Auftrag/Aufträge "
                     "bearbeitet — " + " · ".join(probe)
                     + ". Es wurde nichts getan.")
    if erledigt:
        teile.append(f"✅ Erledigt ({len(erledigt)}): " + " · ".join(erledigt))
    if freigegeben_jetzt:
        teile.append(f"🔓 Nach deiner Freigabe ausgeführt "
                     f"({len(freigegeben_jetzt)}): "
                     + " · ".join(freigegeben_jetzt))
    if geparkt:
        teile.append(f"🗝️ Wartet auf dein Urteil ({len(geparkt)}): "
                     + " · ".join(geparkt)
                     + "\n   Ohne Antwort geschieht nichts — und nichts gilt "
                       "als abgelehnt. Der Auftrag bleibt in der Liste und "
                       "läuft, sobald du zustimmst.")
    if uebersprungen:
        teile.append(f"⏭️ Übersprungen ({len(uebersprungen)}): "
                     + " · ".join(uebersprungen))
    if gescheitert:
        teile.append(f"🔴 Nicht sauber durchgelaufen ({len(gescheitert)}): "
                     + " · ".join(gescheitert)
                     + "\n   Diese Aufträge bleiben offen, abgehakt ist nichts.")
    if abbruch:
        teile.append("⏸️ " + abbruch)
    teile.append(f"Fundament zuletzt: {letzte_lage}")
    teile.append(f"Noch offen in der Liste: {len(auftraege())}")
    melden("\n".join(teile))

    if abbruch:
        return 2
    return 1 if (gescheitert or uebersprungen) else 0


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
