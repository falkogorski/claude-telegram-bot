#!/usr/bin/env python3
# <!-- ROLLE: auftragsbuch -->
"""B8 Stufe 1 — der Weg, auf dem ein Auftrag ohne Adams Hände ankommt.

**Das Problem, das gelöst wird** (Konzept vom 28.07., Adams Ansage 10:56):
Heute ist Adam die Leitung zwischen den Sitzungen. Ein Bauauftrag entsteht auf
dem Server, er lädt ihn herunter, trägt ihn zur nächsten Sitzung, holt das
Ergebnis ab, bringt es zur Prüfung, trägt den Befund zurück. Vier Wege, jeder
von Hand. **Der Inhalt der Arbeit dauert Minuten, der Transport Stunden** — und
bindet genau die Zeit, um derentwillen das System gebaut wird.

Sein Bild dafür: Wenn die Entwicklung ihn bindet, hat er die grauen Herren
durch die Hintertür hereingelassen.

**Die Gegenrichtung zum Botenpostfach.** Dort legt eine Sitzung etwas ab, das
zu Adam hinaus soll. Hier legt sie etwas ab, das ins System hinein soll. Gleiche
Bauart, gleiche Zurückhaltung: eine Ablagestelle, feste Absenderliste, jede
Nachricht nennt ihren Absender.

**NICHT SCHARFGESTELLT.** Die Verrohrung steht, die Einstufung ist geprüft —
aber `uebernehmen()` verweigert die Übergabe an Horas Auftragsliste, solange
`SCHARF` auf `False` steht. Das ist Connis ausdrückliche Auflage und deckt sich
mit dem Deckel für Adams Abwesenheit: Was wacht, braucht seine Gegenprüfung
vorher; was ruht, darf warten.
"""
from __future__ import annotations

import json
import datetime as _dt
import os
import re
import time
from pathlib import Path

# ---------------------------------------------------------------- Verrohrung
# ---------------------------------------------------------------- Der Riegel --
#
# **Eine DATEI, kein unsichtbarer Schalter** (Adams Entscheid 18.08.2026, Connis
# Auflage 5). Bis heute war der Riegel eine Umgebungsvariable, und an drei
# Stellen stand faelschlich "SCHARF = False": Wer das las, hielt eine Repo-Datei
# fuer den Riegel, waehrend in Wahrheit ein `export` genuegt haette.
#
# Jetzt liegt er dort, wo man ihn suchen wuerde - und er traegt seine eigene
# Frist mit sich. Riegel und Probewochen-Ende sind dasselbe Dokument; ein
# abgelaufener Riegel schliesst sich von selbst. Das ist der Unterschied
# zwischen einem Schalter, den jemand zuruecklegen muss, und einem, der es
# selbst tut.
#
# Die Umgebungsvariable bleibt als zweiter Weg bestehen - fuer einen einzelnen
# Lauf, ohne die Datei anzufassen.
RIEGEL = Path(os.environ.get("AUFTRAGSBUCH_RIEGEL")
              or (Path(__file__).resolve().parent / "auftragsbuch-riegel.md"))


def _riegel_offen() -> tuple[bool, str]:
    """(offen, Begruendung) — liest die Riegel-Datei und ihre Frist.

    Faellt irgendetwas aus - Datei fehlt, unlesbar, Datum unverstaendlich -,
    ist der Riegel ZU. Ein Riegel, der sich im Zweifel oeffnet, ist keiner.
    """
    if os.environ.get("AUFTRAGSBUCH_SCHARF") == "ja":
        return (True, "durch Umgebungsvariable fuer diesen Lauf")
    try:
        text = RIEGEL.read_text(encoding="utf-8")
    except Exception:
        return (False, "keine Riegel-Datei")
    if not re.search(r"^\s*SCHARF:\s*ja\s*$", text, re.MULTILINE | re.IGNORECASE):
        return (False, "die Riegel-Datei sagt nicht SCHARF: ja")
    m = re.search(r"^\s*GILT-BIS:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.MULTILINE)
    if not m:
        return (False, "die Riegel-Datei nennt kein Fristdatum (GILT-BIS)")
    try:
        bis = _dt.date.fromisoformat(m.group(1))
    except ValueError:
        return (False, f"unverstaendliches Fristdatum: {m.group(1)}")
    if _dt.date.today() > bis:
        return (False, f"die Frist ist am {bis.isoformat()} abgelaufen")
    return (True, f"Riegel offen bis {bis.isoformat()}")


SCHARF, SCHARF_GRUND = _riegel_offen()

BUCH = Path(os.environ.get("AUFTRAGSBUCH_DIR")
            or (Path.home() / ".claude" / "auftragsbuch"))
EINGANG = BUCH / "eingang"
ABGELEGT = BUCH / "abgelegt"

# Feste Absenderliste — ein Absender, den sich jeder ausdenken kann, belegt
# nichts. Dieselbe Überlegung wie beim Botenpostfach.
ABSENDER = ("claudia", "conni", "mick", "hora", "stundenblume")


# ------------------------------------------------------------------- Ampel --
#
# **Hier liegt die eigentliche Sicherheitsfrage dieser Stufe, nicht in der
# Technik.** Das Konzept benennt den gefährlichsten Fall selbst: „Ich stufe
# einen Auftrag falsch als grün ein — etwas wird gebaut, das Adam so nicht
# wollte, und NIEMAND merkt es, bis es auffällt."
#
# Das Gegenmittel steht ebenfalls dort und wird hier wörtlich umgesetzt:
# **Grün gilt nur für eine benannte, geschlossene Liste von Auftragsarten —
# nicht nach dem Urteil im Einzelfall.** Ein Auftrag mit unbekannter Art ist
# NICHT grün; er ist gelb. Wer eine neue grüne Art will, trägt sie hier ein,
# und der Eintrag trägt sein Prüfdatum.
#
# Die Liste ist absichtlich kurz. Jede Erweiterung ist eine Entscheidung, die
# Adam gehört.
# **Adams Entscheid vom 18.08.2026: genau diese vier, keine fünfte.**
# Jede Art traegt ihr Pruefdatum - sie ist an dem Tag als gruen-tauglich
# befunden worden, nicht fuer immer. Wer eine Art aufnimmt, setzt das Datum neu.
GRUENE_ARTEN: dict[str, str] = {
    # Ein belegter Defekt wird behoben - UND ein Test dafuer existiert bereits.
    # Die Praezisierung ist Adams: Ohne vorhandenen Test ist eine
    # "Fehlerbehebung" eine Behauptung, keine Reparatur.
    "fehlerbehebung": "2026-08-18",
    # Beschriftungen, Emojis, Wortlaut.
    "zeichenwechsel": "2026-08-18",
    # Tote Pfade, Doppelungen, Formatarbeit.
    "aufraeumen": "2026-08-18",
    # Eine Pruefung wird ergaenzt oder geschaerft.
    "test": "2026-08-18",
}
# GESTRICHEN 18.08.2026: "doku" (Register, Blaupause, Drehbuch-Stand). Adams
# Entscheid nennt vier Arten, und diese ist nicht darunter. Bewusst NICHT
# stillschweigend beibehalten - bei einer geschlossenen Liste ist jede stille
# Ergaenzung genau der Fehler, den die Liste verhindern soll.
#
# **BESTAETIGT am selben Abend (Adam mit Conni): bleibt draussen, jetzt nicht.**
# Der natuerliche Moment fuer eine Erweiterung ist die Auswertung am 25.08. -
# "Liste erweitern" steht dort ohnehin als eine der Optionen. Eine Woche
# Betrieb zeigt besser als jede Vorueberlegung, ob doku-Auftraege dazugehoeren.
# Bis dahin sind sie gelb und brauchen Adams Daumen.

# Worte, bei denen die Ampel unabhängig von der Art auf Rot springt. Sie sind
# eine ZUSÄTZLICHE Bremse, kein Ersatz für die geschlossene Liste: Eine
# Wortsuche kann man umgehen, ohne es zu wollen.
#
# **KEINE schließende Wortgrenze — und das ist der ganze Punkt.** Der erste
# Entwurf hatte `\b…\b`, und die eigene Prüfung fiel sofort darüber: „Klient"
# schlug an, „Klientendaten" nicht. Ausgerechnet beim heikelsten Wort. Deutsche
# Zusammensetzungen hängen ihr Bestimmungswort vorn an, und eine Wortgrenze
# dahinter macht die Suche für genau die Fälle blind, für die sie da ist —
# Kundenliste, Passwortdatei, Löschauftrag, Kostenstelle.
#
# Der Preis ist ein gelegentlicher Fehlalarm („Absender" enthält kein Muster,
# aber „Abospur" träfe auf `abo`). Bei einer Bremse ist das die richtige
# Richtung: **Lieber einmal zu oft rot als einmal zu wenig.**
# **KORRIGIERT 18.08.2026 (Gegenpruefung): auf BEIDEN Seiten keine Wortgrenze.**
#
# Der erste Entwurf hatte `\b…\b` und verfehlte [Klientendaten]. Die Korrektur
# strich nur die HINTERE Grenze - und verallgemeinerte damit einen Einzelfall.
# Denn [Klient] steht in [Klientendaten] zufaellig VORN; im Deutschen steht das
# Grundwort aber HINTEN. Gemessen mit der halben Korrektur, alle ohne Treffer:
#
#   Serverpasswort · Zugangsschluessel · Zugriffstoken · Systemschluessel ·
#   Bestandskunden · Datenbankpasswort
#
# Das waren die Faelle, fuer die die Bremse gebaut wurde. Ohne beide Grenzen
# treffen sie.
#
# Der Preis sind mehr Fehlalarme: [above] enthaelt [abo], [Abort] enthaelt
# [abo], [kostenlos] enthaelt [kosten]. Bei einer BREMSE ist das die richtige
# Fehlerrichtung - aber nicht gratis: Rot heisst Warten auf Adams Daumen. Die
# haeufigsten harmlosen Traeger stehen deshalb als Ausnahmen darunter.
ROTE_WORTE = re.compile(
    r"(root|sudo|schlüssel|schluessel|token|secret|passwort|kennwort|"
    r"firewall|webhook|öffentlich|oeffentlich|kosten|bezahl|abo|api[_-]?key|"
    r"lösch|loesch|klient|kunde)", re.IGNORECASE)

# Woerter, die ein rotes Stichwort nur ZUFAELLIG enthalten. Bewusst kurz und
# ausdruecklich benannt: Eine lange Ausnahmeliste hoehlt die Bremse aus, und
# jede Zeile hier ist eine Entscheidung, kein Automatismus.
# Auch hier KEINE schliessende Wortgrenze - und das war beim ersten Anlauf
# prompt falsch: [kostenlose] mit Beugungsendung fiel durch `\b` und wurde rot.
# Dieselbe Lehre wie eine Ebene darueber, im selben Zug erneut gemacht.
ROT_AUSNAHMEN = re.compile(
    r"\b(above|abort|abonnement|abordnung|kostenlos|kostenfrei|kostenguenstig|"
    r"kostengünstig|unentgeltlich)", re.IGNORECASE)


def einstufen(auftrag: dict) -> tuple[str, str]:
    """(ampel, begründung) — deterministisch, ohne Modell, ohne Urteil.

    Die Reihenfolge ist Absicht: **Rot schlägt Grün.** Ein Aufräum-Auftrag, der
    das Wort „Token" enthält, ist kein Aufräum-Auftrag mehr.
    """
    text = " ".join(str(auftrag.get(f, "")) for f in
                    ("titel", "aktion", "begruendung", "befehl"))
    # Die Ausnahmen werden VOR der Suche entfernt, nicht danach geprueft: Sonst
    # verdeckte ein einziges [kostenlos] einen echten Treffer im selben Satz.
    text_ohne = ROT_AUSNAHMEN.sub(" ", text)
    treffer = ROTE_WORTE.search(text_ohne)
    if treffer:
        return ("rot", f"enthält [{treffer.group(0)}] — Sicherheit, Geld oder "
                       "fremde Daten berührt")
    art = str(auftrag.get("art") or "").strip().lower()
    if art in GRUENE_ARTEN:
        return ("gruen", f"Art [{art}] steht seit {GRUENE_ARTEN[art]} auf der "
                         "geschlossenen Grün-Liste")
    if not art:
        return ("gelb", "keine Art angegeben — ohne Art kein Grün")
    return ("gelb", f"Art [{art}] steht nicht auf der Grün-Liste")


# ------------------------------------------------------------------ Ablegen --
def _sicher(name: str) -> str:
    return re.sub(r"[^a-z0-9_-]+", "-", name.lower()).strip("-") or "ohne-namen"


def legen(auftrag: dict, absender: str) -> Path:
    """Legt einen Auftrag in den Eingang. Gibt den Pfad zurück.

    Der Absender steht **zweimal** darin, im Dateinamen und im Inhalt — der
    Dateiname ist das, was man in einem vollen Ordner sieht, ohne eine Datei zu
    öffnen. Gelernt aus der anonymen Meldung vom 26.07., deren Urheber über eine
    Stunde Suche gekostet hat.
    """
    if absender not in ABSENDER:
        raise ValueError(f"unbekannter Absender: {absender}")
    if not auftrag.get("titel"):
        raise ValueError("ein Auftrag ohne Titel ist keiner")
    ampel, grund = einstufen(auftrag)
    satz = dict(auftrag)
    satz.update({
        "herkunft": absender,
        "ampel": ampel,
        "ampel_grund": grund,
        # Die Einstufung wird MITGESCHRIEBEN, nicht bei jedem Lesen neu
        # gerechnet: Ändert sich die Grün-Liste später, soll nachvollziehbar
        # bleiben, unter welcher Regel dieser Auftrag hereinkam.
        "eingang_am": time.strftime("%Y-%m-%d %H:%M:%S"),
        "braucht_zustimmung": ampel != "gruen",
    })
    EINGANG.mkdir(parents=True, exist_ok=True)
    ziel = EINGANG / f"{time.strftime('%Y%m%d-%H%M%S')}-{absender}-{_sicher(satz['titel'])[:40]}.json"
    ziel.write_text(json.dumps(satz, ensure_ascii=False, indent=2), encoding="utf-8")
    return ziel


def eingang() -> list[dict]:
    """Alles, was wartet — nach Eingangszeit, ältestes zuerst."""
    if not EINGANG.is_dir():
        return []
    raus = []
    for datei in sorted(EINGANG.glob("*.json")):
        try:
            satz = json.loads(datei.read_text(encoding="utf-8"))
        except Exception:
            continue                       # unlesbar: liegen lassen, nicht raten
        satz["_datei"] = str(datei)
        raus.append(satz)
    return raus


def uebersicht() -> str:
    """Eine Zeile je Auftrag — das, was Adam im Chat sehen soll.

    Das Konzept verspricht ihm **eine Zeile** statt eines Dokuments: worum es
    geht, Ampelfarbe, ein Knopf. Mehr wäre wieder Transport.
    """
    wartend = eingang()
    if not wartend:
        return "📋 Auftragsbuch: nichts offen."
    zeichen = {"gruen": "🟢", "gelb": "🟡", "rot": "🔴"}
    zeilen = [f"📋 Auftragsbuch — {len(wartend)} offen:"]
    for a in wartend:
        zeilen.append(f"{zeichen.get(a.get('ampel'), '🟡')} {a['titel']} "
                      f"· von {a.get('herkunft', '?')}")
    # **Der Zustand des Riegels gehoert in jede Uebersicht** - in BEIDE
    # Richtungen. Ein Uebergang, der leise nichts tut, sieht aus wie einer, der
    # leise alles tut; seit dem 18.08. gilt auch das Umgekehrte.
    if not SCHARF:
        zeilen.append(f"\n⏸️ Die Übergabe an Hora ist NICHT scharfgestellt "
                      f"({SCHARF_GRUND}) — hier bewegt sich nichts von allein.")
    else:
        zeilen.append(f"\n▶️ Die Übergabe an Hora ist SCHARF ({SCHARF_GRUND}). "
                      f"Grüne Aufträge laufen ohne weitere Rückfrage an und "
                      f"melden sich einzeln.")
    return "\n".join(zeilen)


# --------------------------------------------------------------- Übergeben --
def erledigen(marke_oder_titel: str, ergebnis: str,
              wer: str = "unbekannt") -> tuple[bool, str]:
    """Die fehlende Tuer: einen Auftrag als erledigt ablegen. `(ok, Meldung)`

    **Der zweite Befund vom 26.08., und ohne ihn waere Adams Weg C nur halb:**
    Das Auftragsbuch kannte **keinen Weg, einen gelben Auftrag zu erledigen.**
    `uebernehmen` verschiebt ausschliesslich **gruene** Auftraege; fuer einen
    gelben gab es keine Tuer nach draussen. Er lag, bis ihn jemand von Hand
    wegraeumte — acht Stueck waren es.

    **Die Tagesmarke sorgte dafuer, dass taeglich einer dazukam; die fehlende
    Tuer dafuer, dass keiner je ging.** Ohne diese Funktion laege auch nach der
    Marken-Aenderung derselbe eine Eintrag bis in alle Ewigkeit — nur eben
    still.

    **Mit der Tuer wird der Eintrag zum echten Faelligkeitszeichen:** Liegt
    eine Sichtung im Eingang, ist sie offen. Ist keine da, ist sie erledigt,
    und der Tagescheck legt am naechsten Morgen eine neue an. Das ist besser
    als der Zustand vor allen Aenderungen — ein Stapel sagt weder etwas ueber
    Faelligkeit noch ueber Erledigung.

    **Gebaut wie `uebernehmen`: erst schreiben, dann wegraeumen.** Der Befund
    der Gegenpruefung vom 18.08. gilt hier genauso — braeche das Schreiben ab,
    laege der Auftrag im Abgelegten und der Vermerk waere nirgends.

    **Findet sie nichts, sagt sie das.** Eine Funktion, die still tut, als sei
    etwas geschehen, ist schlimmer als eine, die scheitert.
    """
    treffer = [a for a in eingang()
               if a.get("marke") == marke_oder_titel
               or a.get("titel") == marke_oder_titel]
    if not treffer:
        return (False, f"nichts im Eingang unter [{marke_oder_titel}] — "
                       "nichts erledigt")

    ABGELEGT.mkdir(parents=True, exist_ok=True)
    geraeumt = 0
    for a in treffer:
        quelle = Path(a["_datei"])
        satz = {k: v for k, v in a.items() if not k.startswith("_")}
        satz["erledigt_am"] = _dt.datetime.now().isoformat(timespec="seconds")
        satz["erledigt_von"] = wer
        satz["ergebnis"] = ergebnis
        ziel = ABGELEGT / quelle.name
        # Erst der vollstaendige Vermerk am Zielort, dann die Quelle weg.
        tmp = ziel.with_suffix(".tmp")
        tmp.write_text(json.dumps(satz, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        tmp.replace(ziel)
        if quelle.exists():
            quelle.unlink()
        geraeumt += 1
    return (True, f"{geraeumt} Auftrag/Auftraege unter [{marke_oder_titel}] "
                  f"abgelegt: {ergebnis}")


def uebernehmen(hora_liste: Path | None = None) -> tuple[int, str]:
    """Reicht **grüne** Aufträge an Horas Liste weiter. (Anzahl, Meldung)

    **Der Riegel.** Solange `SCHARF` nicht gesetzt ist, geschieht hier nichts —
    und zwar mit Meldung, nicht stillschweigend. Ein Übergang, der leise
    nichts tut, sähe aus wie ein Übergang, der leise alles tut; von außen ist
    beides dieselbe Ruhe.

    Gelb und Rot werden **nie** hier übergeben. Sie warten auf Adams Daumen
    über die Freigabe-Leitung (9.4) — der Knopf ist ein Vorgang, kein Vortrag.
    """
    # **KORRIGIERT 18.08.2026 (Gegenpruefung, Connis Auflage 5).**
    #
    # Hier stand `a.get("ampel") == "gruen"` — die Ampel wurde also aus der
    # DATEI gelesen. `einstufen()` lief nur beim Ablegen. Wer eine Datei von
    # Hand in den Eingang legte, konnte sich damit sein eigenes Gruen
    # ausstellen: Die Gegenpruefung hat einen Auftrag mit unbekannter Art,
    # unbekanntem Absender und dem Rot-Wort [Root-Zugang] im Titel als gruen an
    # Hora durchgereicht, nur weil "ampel": "gruen" darin stand.
    #
    # **Die Ampel im Eintrag ist ein Vorschlag, nie eine Wahrheit.** Massgeblich
    # ist die Einstufung gegen die geschlossene Liste im MOMENT der Uebergabe.
    # Das faengt zugleich den zweiten Fall: Wird eine Gruen-Art spaeter
    # entfernt, weil sie sich als gefaehrlich erwies, bleiben bereits liegende
    # Auftraege sonst gruen.
    wartend = []
    for a in eingang():
        jetzt, grund = einstufen(a)
        if jetzt != "gruen":
            continue
        if a.get("ampel") != "gruen":
            # Nur vermerken, nicht uebergeben — eine Abweichung in DIESE
            # Richtung ist harmlos, aber sie gehoert gesehen.
            continue
        a["_ampel_geprueft"] = grund
        wartend.append(a)
    if not SCHARF:
        return (0, f"nicht scharfgestellt — {len(wartend)} grüne Aufträge "
                   "warten, es wurde nichts übergeben")
    if not wartend:
        return (0, "nichts Grünes im Eingang")

    ziel = hora_liste or Path(os.environ.get("HORA_LISTE")
                              or (Path.home() / ".claude" / "hora" / "auftragsliste.json"))
    try:
        daten = json.loads(ziel.read_text(encoding="utf-8"))
        if not isinstance(daten, list):
            daten = []
    except Exception:
        daten = []
    vorhanden = {a.get("titel") for a in daten if isinstance(a, dict)}

    uebernommen = 0
    gemeldet: list[str] = []
    for a in wartend:
        if a["titel"] in vorhanden:
            continue                       # schon in der Liste: nicht doppeln
        satz = {k: v for k, v in a.items() if not k.startswith("_")}
        daten.append(satz)
        uebernommen += 1
        vorhanden.add(a["titel"])          # sonst rutschen Namensgleiche doppelt durch
        gemeldet.append(
            f"🟢 [{a['titel']}] von {a.get('absender', 'unbekannt')} — "
            f"grün, weil Art [{a.get('art', '?')}] auf der geschlossenen Liste "
            f"steht (geprüft {GRUENE_ARTEN.get(a.get('art', ''), '?')})")

    # **Erst schreiben, dann wegräumen** (Gegenprüfungs-Befund 18.08.).
    # Vorher verschob die Schleife jede Eingangsdatei ins Archiv, BEVOR die
    # Zielliste geschrieben war. Brach das Schreiben ab — Rechte, Platte,
    # Absturz —, lag der Auftrag im Archiv und stand in keiner Liste. Verloren,
    # ohne Meldung.
    ziel.parent.mkdir(parents=True, exist_ok=True)
    tmp = ziel.with_suffix(".tmp")
    tmp.write_text(json.dumps(daten, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(ziel)

    ABGELEGT.mkdir(parents=True, exist_ok=True)
    for a in wartend:
        quelle = Path(a["_datei"])
        if quelle.exists():
            quelle.replace(ABGELEGT / quelle.name)

    # **Probewoche: jede Grün-Ausführung meldet sich, und zwar ungedämpft.**
    # Connis Auflage vom 18.08. — die Sichtbarkeit IST der Zweck der Woche.
    # Wer sie dämpft, prüft nicht die Automatik, sondern die Dämpfung.
    if gemeldet:
        try:
            import botenpost
            botenpost.legen(
                "🟢 Grün-Automatik hat übergeben (Probewoche):\n"
                + "\n".join(gemeldet)
                + "\n\nHora arbeitet sie im nächsten Lauf ab und meldet je "
                  "Auftrag den Regressionsstand.",
                absender="auftragsbuch")
        except Exception:
            # Eine misslungene Meldung darf die Übergabe nicht zurücknehmen —
            # aber sie darf auch nicht so aussehen, als hätte es sie gegeben.
            print("WARNUNG: Übergabe erfolgt, Meldung an Adam fehlgeschlagen")

    return (uebernommen, f"{uebernommen} grüne Aufträge an Hora übergeben")


if __name__ == "__main__":
    print(uebersicht())
