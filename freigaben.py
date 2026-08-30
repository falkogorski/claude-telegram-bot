# <!-- ROLLE: freigabe-postfach -->
"""9.4 Phase A — Freigabe-Postfach: der Parkplatz für Entscheidungen.

**Warum es hoch eingeordnet ist:** Es ist nicht bloß ein bequemer Freigabe-Weg,
sondern **die fehlende Leitung** zwischen Bot-Chat und Ablage. Adam entscheidet
häufig per Reaktion oder Sprachnachricht im Bot-Chat — und die Bot-Sitzung darf
nicht ins Repo schreiben (8.7). Also blieb bisher jede dort getroffene
Entscheidung im Bot-Gedächtnis liegen, bis ein Mensch sie übertrug. Genau so ist
der Gesamtdaumen fürs Phasen-Audit verlorengegangen.

**Und es ist die Voraussetzung für Hora:** Ein autonomer Läufer darf keine
Entscheidungen treffen — er muss sie **parken**. Dies ist der Parkplatz.

## Die sieben Leitplanken (unverändert übernommen)

1. **Nur Adams authentifizierte Kennung** darf urteilen.
2. **Konkret vor Label** — die Anfrage zeigt die **wörtliche Aktion**, nicht nur
   ihre Beschriftung. Ein Label ließe sich fälschen, die Aktion nicht verbergen.
3. **Kein Dauer-Knopf für gelb/rot** — Sammelfreigaben gibt es nur für
   reversibles Grün.
4. **Keine Geheimnisse im Kanal** — Anfragen mit Geheimnis-Bezug werden
   abgewiesen, nicht angezeigt.
5. **Fail-safe heißt: die Aktion geschieht nicht.** [KORRIGIERT 2026-07-25]
   Vorher stand hier „Fail-safe = Ablehnen", und der Bot schrieb Adam
   entsprechend „Antwortest du nicht, gilt es als abgelehnt." Das ist zu viel
   behauptet. **Schweigen darf nie bewirken, dass etwas passiert — aber
   Schweigen heißt auch nicht Nein.** Nichtantwort bedeutet übersehen,
   vergessen, nicht da gewesen; keines davon ist ein Urteil. Deshalb:
   * Der Zustand einer unbeantworteten Anfrage ist **offen**, nicht „abgelehnt".
   * **Ins Protokoll kommt nur, was Adam tatsächlich entschieden hat** — eine
     Frist ist kein Urteil und hat im Entscheidungs-Protokoll nichts zu suchen.
   * Die **Frist (24 h) ist eine Auffrischung, kein Verfall**: Die Anfrage wird
     **neu vorgelegt**, nicht beerdigt.
   * Die Unterscheidung, die zählt: **Lag zwischen Zustellung und Frist
     überhaupt eine Regung von Adam vor?** Wenn nein, trägt das Schweigen keine
     Information → schlicht neu vorlegen. Wenn ja → als **„gesehen, offen"**
     markieren; das ist ein Hinweis, dass die Frage unklar gestellt war.
6. **Eine Freigabe erzeugt keine Rechte** — 8.7 bleibt unberührt. Wer eine
   Repo-Schreibung freigibt, gibt sie **nicht** dem Bot frei.
7. **Herkunft kennzeichnen** — jede Anfrage sagt, wer sie gestellt hat.

**Parken kostet kein Kontingent:** Die Anfrage ist eine Datei. Der Fragende legt
sie ab und beendet seinen Zug; er wacht erst beim Urteil wieder auf.
"""
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass, asdict, field
from pathlib import Path

WURZEL = Path(os.environ.get("FREIGABE_DIR")
              or (Path.home() / "postfach" / "freigaben"))
ANFRAGEN = WURZEL / "anfragen"
URTEILE = WURZEL / "urteile"
PROTOKOLL = WURZEL / "protokoll"          # wartet auf die Übertragung ins Drehbuch

# Frist, nach der eine Anfrage ERNEUT VORGELEGT wird (Leitplanke 5).
# 24 h statt 48: Der Zusammenhang einer Frage verschiebt sich schneller, als eine
# Frist von zwei Tagen unterstellt. Die Frist beendet nichts — sie frischt auf.
FRIST_STUNDEN = float(os.environ.get("FREIGABE_FRIST_H") or 24)

# Leitplanke 4 — dieselben Marker wie im Bot, bewusst hier gespiegelt: Das
# Postfach muss auch dann schützen, wenn es von einem anderen Prozess befüllt
# wird, der bot.py gar nicht kennt.
_GEHEIM = (".env", "credentials", "token", "secret", "_key", "key.", "keys.",
           "id_ed25519", "id_rsa", "passwor", "/etc/claude-telegram-bot",
           "/etc/telegram-bot-api", "api_hash", "api_id")

AMPELN = ("gruen", "gelb", "rot")

# **[NEU 30.08.] Die ART der Frage — Claudias Auftrag 3 bzw. 5.**
#
# Adam am 28.08. um 19:20 an einer echten Anfrage: *„Ich verstehe nicht, worauf
# der abzielt. Ich verstehe nicht, was ich freigebe oder ablehne."* Die
# Kopfzeile lautete immer „🗝️ Freigabe erbeten", gleich ob ein Systemeingriff
# gemeint war oder eine Protokollzeile. **Das Klemmbrett hat er selbst gewählt**
# (19:41: „Ja, Klemmbrett ist super").
#
# Ohne Angabe bleibt es beim Schlüssel — er gilt weiterhin für alles, was eine
# Handlung auslöst. Weitere Arten kommen später dazu; die Abbildung ist der
# einzige Ort, an dem eine hinzukommt.
ARTEN = {
    "handlung": "🗝️",       # Vorgabe: etwas geschieht auf der Maschine
    "ablage": "📋",         # eine Zeile wird ins Protokoll geschrieben
}

# Wie lange eine begonnene Änderung offen bleiben darf, bevor die
# **ursprüngliche** Anfrage erneut vorgelegt wird. Claudias Setzung, von ihr
# selbst als solche benannt; hier als Umgebungsschlüssel, damit sie sich
# messen lässt, ohne den Code anzufassen.
AENDERUNG_FRIST_S = float(os.environ.get("FREIGABE_AENDERUNG_FRIST_S") or 3600)


@dataclass
class Anfrage:
    kennung: str
    titel: str                 # kurz, für die Liste
    aktion: str                # WÖRTLICH — Leitplanke 2
    ampel: str                 # gruen | gelb | rot
    herkunft: str              # wer fragt (Leitplanke 7)
    gestellt: float = field(default_factory=time.time)
    # `[G5, 25.07.]` Wann die Frage ZUERST gestellt wurde — wird nie
    # überschrieben. `gestellt` wandert bei jeder Auffrischung nach vorn; ohne
    # diesen Anker läse sich eine Frage vom 28.07. nach vierzehn Tagen als
    # frisch gestellt, mit „14× vorgelegt" als einzigem Hinweis. Gerade das
    # Alter sagt Adam bei der Rückkehr, was zuerst dran ist.
    erstmals: float = 0.0
    begruendung: str = ""
    rueckweg: str = ""         # wie ließe es sich rückgängig machen?
    vorgelegt: int = 1         # wie oft schon vorgelegt (1 = erstmals)
    gesehen: bool = False      # Adam war da und hat trotzdem nicht geurteilt
    # `[NEU 30.08.]` Die Art der Frage (Schlüssel aus `ARTEN`) — sie steht in
    # der Kopfzeile, damit Adam sieht, WORÜBER er urteilt, bevor er liest.
    art: str = "handlung"
    # Änderung durch Adam selbst (Claudias dritter Knopf). **Sichtbar, nicht
    # still** (Auflage 3): Wer die Zeile formuliert hat, gehört ins Protokoll.
    geaendert_am: float = 0.0
    geaendert_von: str = ""
    # Eine begonnene, noch unbeantwortete Änderung. `aenderung_nachricht` ist
    # die Kennung der ForceReply-Nachricht — an ihr hängt die Zuordnung, ohne
    # dass jemand raten muss, worauf sich eine Antwort bezieht.
    aenderung_seit: float = 0.0
    aenderung_nachricht: int = 0

    def symbol(self) -> str:
        """Das Zeichen der Art — Unbekanntes bleibt beim Schlüssel."""
        return ARTEN.get(self.art, ARTEN["handlung"])

    def aenderung_haengt(self, jetzt: float | None = None) -> bool:
        """Wartet eine begonnene Änderung zu lange auf Antwort?

        Aus Claudias Bruchtabelle: *Adam antwortet nicht auf die
        Änderungs-Nachricht, sondern schreibt frei — der Bot ordnet die Antwort
        keiner Anfrage zu und verschluckt sie.* Dann wird die **ursprüngliche**
        Anfrage erneut vorgelegt, statt still zu warten.
        """
        if not self.aenderung_seit:
            return False
        return ((jetzt or time.time()) - self.aenderung_seit) > AENDERUNG_FRIST_S

    def __post_init__(self) -> None:
        if not self.erstmals:
            self.erstmals = self.gestellt

    def wartezeit_s(self) -> float:
        """Der Bremsweg: je öfter vorgelegt, desto seltener (G5).

        Starre 24 Stunden hießen bei vierzehn Tagen Abwesenheit **vierzehn
        Nachrichten** je offener Frage — und damit wäre die Wiedervorlage
        wieder ein Halteschild statt eines Wegsteins. Die Bremse ist bei
        viermal gedeckelt: Danach meldet sie sich alle vier Tage, das bleibt
        wahrnehmbar, ohne zu nerven.
        """
        return FRIST_STUNDEN * 3600 * min(max(1, self.vorgelegt), 4)

    def faellig(self, jetzt: float | None = None) -> bool:
        """Ist die Auffrischung fällig? (Früher hieß das `abgelaufen` — der
        Name unterstellte ein Ende, das es nicht gibt.)"""
        return ((jetzt or time.time()) - self.gestellt) > self.wartezeit_s()

    def lesbar(self) -> str:
        sym = {"gruen": "🟢", "gelb": "🟡", "rot": "🔴"}.get(self.ampel, "⬜")
        teile = []
        if self.erstmals:
            teile.append("seit " + time.strftime(
                "%d.%m.", time.localtime(self.erstmals)))
        if self.vorgelegt > 1:
            teile.append(f"{self.vorgelegt}× vorgelegt")
        if self.gesehen:
            teile.append("gesehen, offen")
        zusatz = ("  · " + ", ".join(teile)) if teile else ""
        return f"{sym} {self.titel}  ({self.herkunft}){zusatz}"


class Abgewiesen(Exception):
    """Die Anfrage verletzt eine Leitplanke — sie wird nicht einmal angezeigt."""


def _ordner() -> None:
    for p in (ANFRAGEN, URTEILE, PROTOKOLL):
        p.mkdir(parents=True, exist_ok=True)


def _hat_geheimnis(text: str) -> bool:
    t = (text or "").lower()
    return any(m in t for m in _GEHEIM)


def stellen(titel: str, aktion: str, ampel: str, herkunft: str,
            begruendung: str = "", rueckweg: str = "",
            art: str = "handlung") -> Anfrage:
    """Legt eine Anfrage ab. Prüft die Leitplanken, BEVOR etwas sichtbar wird."""
    if ampel not in AMPELN:
        raise Abgewiesen(f"unbekannte Ampelfarbe: {ampel!r}")
    if art not in ARTEN:
        # Abgewiesen statt stillschweigend auf die Vorgabe zurückfallen: Eine
        # falsch geschriebene Art wäre sonst unsichtbar und Adam läse das
        # Schlüssel-Zeichen über einer Ablage-Frage.
        raise Abgewiesen(f"unbekannte Art: {art!r} (bekannt: {', '.join(ARTEN)})")
    if not (titel or "").strip() or not (aktion or "").strip():
        raise Abgewiesen("Titel und wörtliche Aktion sind Pflicht (Konkret vor Label)")
    # Leitplanke 4: Geheimnisse erreichen den Kanal gar nicht erst.
    for feld, wert in (("Titel", titel), ("Aktion", aktion),
                       ("Begründung", begruendung), ("Rückweg", rueckweg)):
        if _hat_geheimnis(wert):
            raise Abgewiesen(
                f"{feld} enthält einen Geheimnis-Bezug — eine solche Anfrage "
                "geht nicht durch den Chat. Bitte den Weg wählen, der ohne "
                "Geheimnis auskommt.")
    _ordner()
    kennung = f"{int(time.time())}-{abs(hash((titel, aktion))) % 100000:05d}"
    a = Anfrage(kennung=kennung, titel=titel.strip()[:120],
                aktion=aktion.strip()[:2000], ampel=ampel,
                herkunft=(herkunft or "unbekannt").strip()[:60],
                begruendung=begruendung.strip()[:600],
                rueckweg=rueckweg.strip()[:600], art=art)
    tmp = ANFRAGEN / f".{kennung}.tmp"
    tmp.write_text(json.dumps(asdict(a), ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.rename(ANFRAGEN / f"{kennung}.json")
    return a


def offene(jetzt: float | None = None) -> list[Anfrage]:
    """Alle noch unbeantworteten Anfragen, älteste zuerst."""
    _ordner()
    raus: list[Anfrage] = []
    for p in sorted(ANFRAGEN.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            raus.append(Anfrage(**{k: v for k, v in d.items()
                                   if k in Anfrage.__annotations__}))
        except Exception:
            continue
    return raus


def finden(kennung: str) -> Anfrage | None:
    for a in offene():
        if a.kennung == kennung:
            return a
    return None


def _anfrage_speichern(a: Anfrage) -> None:
    """Schreibt eine bestehende Anfrage atomar zurück."""
    _ordner()
    tmp = ANFRAGEN / f".{a.kennung}.tmp"
    tmp.write_text(json.dumps(asdict(a), ensure_ascii=False, indent=2),
                   encoding="utf-8")
    tmp.rename(ANFRAGEN / f"{a.kennung}.json")


def auffrischen(letzte_regung: float | None = None,
                jetzt: float | None = None) -> list[Anfrage]:
    """Legt fällige Anfragen ERNEUT vor, statt sie verfallen zu lassen.

    ``letzte_regung`` ist der Zeitpunkt, zu dem Adam zuletzt irgendetwas getan
    hat (Nachricht, Reaktion, Befehl). Der Bot kennt ihn ohnehin.

    * **Keine Regung im Fenster** → das Schweigen trägt keine Information.
      Die Anfrage wird schlicht neu vorgelegt, der Zähler steigt.
    * **Regung im Fenster** → Adam war da und hat trotzdem nicht geurteilt.
      Das wird als „gesehen, offen" vermerkt — ein Hinweis, dass die Frage
      unklar gestellt war, nicht ein Nein.

    Rückgabe: die Anfragen, die neu vorzulegen sind.
    """
    now = jetzt or time.time()
    raus: list[Anfrage] = []
    for a in offene(now):
        # **`[NEU 30.08.]` Eine hängende Änderung wird aufgelöst, nicht
        # ausgesessen.** Aus Claudias Bruchtabelle: Adam antwortet nicht auf
        # die Änderungs-Nachricht, sondern schreibt frei — dann ordnet der Bot
        # die Antwort keiner Anfrage zu, und *„wer merkt es? Adam, wenn nichts
        # geschieht — oder niemand"*. Die Anfrage kommt dann mit dem
        # URSPRÜNGLICHEN Text zurück, samt Hinweis, dass die Änderung offen
        # blieb. Ohne diesen Zweig bliebe sie für immer gesperrt: Der Merker
        # weist jede weitere Änderung ab.
        if a.aenderung_haengt(now):
            a.aenderung_seit = 0.0
            a.aenderung_nachricht = 0
            a.vorgelegt += 1
            a.gestellt = now
            _anfrage_speichern(a)
            raus.append(a)
            continue
        if not a.faellig(now):
            continue
        a.gesehen = bool(letzte_regung and letzte_regung >= a.gestellt)
        a.vorgelegt += 1
        a.gestellt = now          # die Frist frischt auf, sie läuft nicht ab
        _anfrage_speichern(a)
        raus.append(a)
    return raus


def unbeantwortet(jetzt: float | None = None) -> list[Anfrage]:
    """Die eigene Liste: mehr als einmal vorgelegt und noch immer ohne Urteil.

    Bewusst **getrennt vom Entscheidungs-Protokoll** — dort steht nur, was Adam
    tatsächlich entschieden hat.
    """
    return [a for a in offene(jetzt) if a.vorgelegt > 1 or a.gesehen]


def urteilen(kennung: str, ja: bool, von: str, grund: str = "",
             jetzt: float | None = None) -> dict:
    """Trägt ein Urteil ein. Rückgabe: der Protokoll-Eintrag.

    **Nur ein tatsächliches Urteil landet hier** — eine verstrichene Frist ist
    keines und erzeugt deshalb keinen Eintrag (siehe `auffrischen`). Ein Ja
    bleibt ein Ja, auch wenn die Anfrage schon mehrfach vorgelegt wurde; die
    Auffrischung sorgt dafür, dass der Zusammenhang frisch ist.
    """
    a = finden(kennung)
    if a is None:
        raise Abgewiesen("Diese Anfrage gibt es nicht (mehr).")
    entschieden = bool(ja)
    eintrag = {
        "kennung": a.kennung,
        "titel": a.titel,
        "aktion": a.aktion,
        "ampel": a.ampel,
        "herkunft": a.herkunft,
        "urteil": "freigegeben" if entschieden else "abgelehnt",
        "grund": (grund or "").strip()[:400],
        "vorgelegt": a.vorgelegt,
        "beantwortet_von": von,
        "beantwortet_am": time.strftime("%Y-%m-%d %H:%M",
                                        time.localtime(jetzt or time.time())),
        "art": a.art,
    }
    # **Auflage 3 — die Änderung ist sichtbar, auch im Protokoll.** Nicht nur
    # DASS geändert wurde, sondern von wem: *Eine von Adam selbst formulierte
    # Protokollzeile ist stärker als meine* — sie ist dann kein Verständnis von
    # mir mehr, sondern sein Wortlaut. Das gehört an die Zeile, nicht in eine
    # Fußnote.
    if a.geaendert_am:
        eintrag["formuliert_von"] = a.geaendert_von
        eintrag["geaendert_am"] = time.strftime(
            "%Y-%m-%d %H:%M", time.localtime(a.geaendert_am))
    _ordner()
    for ordner, name in ((URTEILE, "u"), (PROTOKOLL, "p")):
        tmp = ordner / f".{a.kennung}.tmp"
        tmp.write_text(json.dumps(eintrag, ensure_ascii=False, indent=2),
                       encoding="utf-8")
        tmp.rename(ordner / f"{a.kennung}.json")
    try:
        (ANFRAGEN / f"{a.kennung}.json").unlink()
    except OSError:
        pass
    return eintrag


def aenderung_beginnen(kennung: str, nachricht_id: int,
                       jetzt: float | None = None) -> Anfrage:
    """Merkt vor, dass Adam diese Anfrage gerade ändert.

    **Auflage 5 — nur an OFFENEN Anfragen.** Eine bereits beurteilte Anfrage
    ist abgeschlossen; nachträgliches Ändern erzeugte ein Urteil zu einem Text,
    den niemand so beurteilt hat. `finden()` liefert nur Offene, das ist die
    Prüfung.

    **Und nur EINE Änderung je Anfrage.** Zwei gleichzeitig laufende hätten
    zwei Antwortwege auf denselben Text — wer zuletzt schreibt, gewänne, und
    niemand sähe es. Eine hängende Änderung wird nach `AENDERUNG_FRIST_S`
    freigegeben, damit ein unbeantworteter Versuch die Anfrage nicht für immer
    sperrt.
    """
    a = finden(kennung)
    if a is None:
        raise Abgewiesen("Diese Anfrage gibt es nicht mehr — sie ist "
                         "beantwortet oder zurückgezogen. Geändert wird nur, "
                         "was noch offen ist.")
    if a.aenderung_seit and not a.aenderung_haengt(jetzt):
        raise Abgewiesen("An dieser Anfrage läuft bereits eine Änderung. "
                         "Antworte auf die Änderungs-Nachricht oder warte, "
                         "bis sie verfällt.")
    a.aenderung_seit = jetzt or time.time()
    a.aenderung_nachricht = int(nachricht_id)
    _anfrage_speichern(a)
    return a


def aenderung_zu_nachricht(nachricht_id: int) -> Anfrage | None:
    """Welche Anfrage hängt an dieser Änderungs-Nachricht?

    **Die Zuordnung ist technisch, nicht geraten** — das ist der Grund, warum
    Variante B (erzwungene Antwort) Adams eigenem Ausweichvorschlag vorgezogen
    wurde: Er hatte erwogen, den Text von Hand zu kopieren, mit der Sorge, der
    Bot müsse dann erraten, worauf er sich bezieht.
    """
    for a in offene():
        if a.aenderung_nachricht and a.aenderung_nachricht == int(nachricht_id):
            return a
    return None


def aendern(kennung: str, neuer_text: str, von: str,
            jetzt: float | None = None) -> Anfrage:
    """Übernimmt Adams eigene Fassung des Aktionstexts.

    ## Die fünf Auflagen, und sie sind der eigentliche Bau

    Der Änderungsknopf verändert den Text, über den anschließend entschieden
    wird. Das ist ein Angriffsweg, wenn er unbedacht gebaut wird.

    **1. Nur Adams Kennung darf ändern** — geprüft im Aufrufer gegen dieselbe
    Allowlist wie das Urteil, nicht gegen den Chat.
    **2. Nach jeder Änderung wird erneut vorgelegt** — hier dadurch gesichert,
    dass die Anfrage offen bleibt und `vorgelegt` weiterzählt; ein geänderter
    Text kann nie ohne neue Vorlage freigegeben werden.
    **3. Die Änderung ist sichtbar** — `geaendert_am`/`geaendert_von` wandern
    in die Anzeige und ins Protokoll.
    **4. Die Geheimnisprüfung läuft erneut.** Sie griff bisher nur beim
    Anlegen; ein Text, der nachträglich ein Geheimnis bekommt, wäre ungeprüft
    durchgegangen — die Leitplanke wäre an der Stelle offen gewesen, an der sie
    am leichtesten zu übersehen ist.
    **5. Nur an offenen Anfragen** — siehe `aenderung_beginnen`.

    **Zu lang wird gemeldet, nicht abgeschnitten.** Stilles Kürzen erzeugte ein
    Urteil über einen halben Satz.
    """
    a = finden(kennung)
    if a is None:
        raise Abgewiesen("Diese Anfrage gibt es nicht mehr — geändert wird "
                         "nur, was noch offen ist.")
    text = (neuer_text or "").strip()
    if not text:
        raise Abgewiesen("Der geänderte Text ist leer. Ohne wörtliche Aktion "
                         "gibt es nichts zu beurteilen (Konkret vor Label).")
    if len(text) > 2000:
        raise Abgewiesen(
            f"Der geänderte Text ist {len(text)} Zeichen lang, erlaubt sind "
            "2000. Ich kürze ihn NICHT von selbst — ein Urteil über einen "
            "halben Satz wäre schlimmer als diese Meldung.")
    if _hat_geheimnis(text):
        raise Abgewiesen(
            "Der geänderte Text enthält einen Geheimnis-Bezug. Auch eine "
            "Änderung geht durch dieselbe Prüfung wie das Anlegen — sonst "
            "wäre die Leitplanke genau dort offen, wo sie niemand vermutet.")
    a.aktion = text
    a.geaendert_am = jetzt or time.time()
    a.geaendert_von = (von or "unbekannt").strip()[:60]
    a.aenderung_seit = 0.0
    a.aenderung_nachricht = 0
    a.vorgelegt += 1
    a.gestellt = jetzt or time.time()
    _anfrage_speichern(a)
    return a


def urteil_lesen(kennung: str) -> dict | None:
    """Für den Fragenden: Liegt schon ein Urteil vor?"""
    p = URTEILE / f"{kennung}.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def buendelbar(anfragen: list[Anfrage]) -> list[Anfrage]:
    """Leitplanke 3: Nur reversibles Grün darf gesammelt freigegeben werden."""
    return [a for a in anfragen if a.ampel == "gruen" and a.rueckweg.strip()]


def uebersicht(jetzt: float | None = None) -> str:
    """Für `/freigaben` — deterministisch, ohne Modell-Aufruf."""
    liste = offene(jetzt)
    if not liste:
        return "✅ Keine offenen Freigabe-Anfragen."
    zeilen = []
    for a in liste:
        rest = (a.wartezeit_s() - ((jetzt or time.time()) - a.gestellt)) / 3600
        frist = ("⌛ lege ich dir gleich erneut vor" if rest <= 0
                 else f"lege ich in {rest:.0f} h erneut vor")
        zeilen.append(f"{a.lesbar()}\n   {frist}")
    return (f"🗝️ Offene Freigabe-Anfragen ({len(liste)}):\n"
            + "\n".join(zeilen)
            + "\n\nOhne Antwort geschieht nichts — und nichts gilt als "
              "abgelehnt. Ich lege sie dir einfach wieder vor.")


def protokoll_offen() -> list[dict]:
    """Urteile, die noch nicht ins Drehbuch übertragen wurden."""
    _ordner()
    raus = []
    for p in sorted(PROTOKOLL.glob("*.json")):
        try:
            raus.append(json.loads(p.read_text(encoding="utf-8")))
        except Exception:
            continue
    return raus


def protokoll_erledigt(kennung: str) -> None:
    try:
        (PROTOKOLL / f"{kennung}.json").unlink()
    except OSError:
        pass
