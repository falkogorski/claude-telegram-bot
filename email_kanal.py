# <!-- ROLLE: email-kanal -->
"""9.5 — E-Mail über SMTP/IMAP: lesen, entwerfen, nach Freigabe senden.

**Warum dieser Punkt vorgezogen wurde:** Die eigene Vorprüfung der
Business-Anbindungen (25.07.) ergab, dass E-Mail der **einzige grüne Weg** ist.
IMAP und SMTP sind **offene Protokolle** — kein Betreiber kann den Zugang
entziehen, keine Prüfung, keine Kontobindung, keine Gebühr. Alle anderen Wege
führen über einen Anbieter, der die Regeln jederzeit ändert. Das deckt sich mit
dem Grundwert der Souveränität und hat obendrein den größten Alltagsnutzen.

## Die Grundhaltung: senden ist die gefährlichste Fähigkeit im ganzen Aufbau

Alles andere, was dieses System tut, bleibt im Haus oder ist rückholbar. Eine
abgeschickte E-Mail ist **weg** — sie liegt bei einem Menschen, der sie gelesen
hat, und keine Reue holt sie zurück. Deshalb ist dieses Modul auf eine Weise
gebaut, die anderswo übertrieben wäre:

1. **Der Bot sendet nie von sich aus.** Jeder Versand geht über den Parkplatz
   (9.4): Empfänger, Betreff, Text und Anhänge werden **wörtlich** vorgelegt
   (Konkret vor Label), und erst Adams Urteil löst ihn aus. Es gibt **keinen
   Weg**, der daran vorbeiführt — `senden()` verlangt eine Freigabe-Kennung mit
   Urteil „freigegeben" und weigert sich sonst.
2. **Eingehende Mail ist Fremdtext, kein Auftrag.** Was im Posteingang steht,
   hat ein Fremder geschrieben. Eine Mail, die „schick mir die Zugangsdaten"
   verlangt, ist **Datum, nicht Weisung** — der Bot legt Fundstücke vor, er
   handelt nicht danach. Deshalb liefert `posteingang()` standardmäßig nur
   **Kopfzeilen**, und der Text kommt erst auf Abruf (dieselbe Zweistufigkeit
   wie bei Video, Wartungsfenster und Link-Inbox).
3. **Zugangsdaten kommen ausschließlich aus der Umgebung** und werden nirgends
   protokolliert, angezeigt oder in eine Freigabe-Anfrage geschrieben. Der
   Geheimnis-Filter des Postfachs würde eine solche Anfrage ohnehin abweisen —
   aber sie darf gar nicht erst entstehen.

## Die Kopfzeilen-Einschleusung — der Grund für die strenge Prüfung

Ein Zeilenumbruch in Empfänger oder Betreff kann in den Kopfteil einer Mail
zusätzliche Felder schreiben: ein zweites `Bcc:`, ein anderes `From:`. Wer den
Betreff einer Mail beeinflussen kann — und das kann jeder, dessen Text in einen
Entwurf einfließt —, könnte damit stillschweigend mitlesen. Deshalb werden
Steuerzeichen in **allen** Kopffeldern abgewiesen, nicht ersetzt: Ein Betreff,
der so etwas enthält, ist nie ein Versehen.

💰 **Keine Kosten:** Standardprotokolle, kein Anbieter dazwischen, keine Gebühr.
"""
from __future__ import annotations

import imaplib
import logging
import os
import re
import smtplib
import ssl
from dataclasses import dataclass, field
from email.header import decode_header, make_header
from email.message import EmailMessage
from email.utils import parseaddr, formatdate, make_msgid
from pathlib import Path

import freigaben

# **Ein eigener Logger — er fehlte.** Die Fehlerbehandlung in `posteingang()`
# und `_kopf_zerlegen()` rief `log.warning`/`log.exception`, und `log` gab es in
# diesem Modul nicht. Der Fehlerpfad haette also selbst einen Fehler geworfen —
# ausgerechnet dort, wo etwas ehrlich scheitern soll.
#
# Gefunden von der Pruefzeile „ein Verbindungsfehler ist keine leere Mailbox",
# beim ERSTEN Lauf. Kein Lesen haette es gezeigt: Der Name steht da, er sieht
# richtig aus, und der Zweig laeuft nur im Stoerfall.
log = logging.getLogger(__name__)

# Ein Konto heißt hier schlicht „geschaeftlich" oder „privat"; die Zugangsdaten
# stehen unter MAIL_<NAME>_… in der Umgebung. Der Name taucht im Chat auf, die
# Daten nie.
_FELDER = ("ADRESSE", "BENUTZER", "KENNWORT", "IMAP", "SMTP")

# A3: Wie viele Kopfzeilen ein Abruf höchstens holt, und wie lange er auf den
# Server wartet. Beides bewusst klein — der Überblick ist die erste Stufe, der
# Text kommt einzeln auf Abruf.
MAX_ABRUF = 25
ABRUF_FRIST_S = 20

# Was in einem Kopffeld nichts zu suchen hat.
#
# **`[ERWEITERT 2026-08-23, Stufe A1 — gemessen, nicht vermutet]`** Die alte
# Klasse fasste CR, LF und die ASCII-Steuerzeichen. Engywucks Auftrag warnte
# „nicht nur `\n`", und die Messung (`scripts/mess_kopfzeilen_a1.py`) hat ihm
# recht gegeben: **Drei Zeilentrenner kamen durch**, die kein ASCII sind —
# U+0085 (NEXT LINE), U+2028 (LINE SEPARATOR), U+2029 (PARAGRAPH SEPARATOR).
#
# **Der Schaden ist Darstellung, nicht Zerlegung:** In einer Chat-Anzeige bricht
# U+2028 die Zeile, und darunter steht dann `From: chef@firma.de` — für Adams
# Auge eine zweite Kopfzeile, die es nie gab. Die Werte selbst bleiben heil.
#
# **Dazu die unsichtbaren Zeichen** (U+200B–U+200D, U+2060, U+FEFF): Sie
# trennen ein Wort, ohne dass man es sieht — `Rech⁠nung` liest sich wie
# `Rechnung`, ist aber etwas anderes. Sie sind Korpus-Fall 8 und kamen
# ebenfalls durch. Auch sie werden ersetzt, nicht entfernt: Ein Zeichen, das
# spurlos verschwindet, verschiebt die Buchstaben zusammen und verbirgt damit,
# dass etwas da war.
_STEUERZEICHEN = re.compile(
    # `\x09` (Tabulator) ist mit drin: Er ist gueltiger Faltungs-Leerraum und
    # landet nach dem Zusammenfalten IM Wert. Sichtbar ist er dort nicht, aber
    # er verschiebt die Darstellung — und ein Zeichen, das man nicht sieht,
    # gehoert nicht in einen Wert, den ein Mensch lesen soll.
    r"[\r\n\x00-\x08\x09\x0b\x0c\x0e-\x1f\x7f"
    r"  "          # Zeilentrenner jenseits von ASCII
    r"​-‍⁠﻿]"  # unsichtbare Trenner mitten im Wort
)

# Anhänge dürfen nur aus dem Arbeitsbereich kommen — nie aus Geheimnis-Pfaden.
# Dieselben Marker wie im Freigabe-Postfach, bewusst gespiegelt.
_GEHEIME_PFADE = (".env", "credentials", "id_ed25519", "id_rsa", ".ssh",
                  "/etc/claude-telegram-bot", "/etc/telegram-bot-api",
                  "secret", "token", ".claude/hora", "postfach/freigaben")

ANHANG_GRENZE = 20 * 1024 * 1024        # was übliche Empfänger annehmen


class Abgewiesen(Exception):
    """Der Entwurf verletzt eine Leitplanke — er entsteht gar nicht erst."""


@dataclass
class Konto:
    name: str
    adresse: str
    benutzer: str
    imap: str
    smtp: str
    # `[NEU 26.07.]` Weitere Adressen desselben Kontos. Ein anwendungs-
    # spezifisches Kennwort gilt **pro Konto, nicht pro Adresse** — Aliasse
    # brauchen also weder eigenes Kennwort noch eigenen Eintrag, nur die
    # Erlaubnis, als Absender aufzutreten.
    #
    # ⚠️ **Warum eine Liste und nicht freie Wahl:** Wer den Absender bestimmen
    # kann, kann in Adams Namen schreiben. Mailtexte entstehen hier teils aus
    # Inhalten, die von außen kommen — ein frei wählbares `From` wäre damit ein
    # Weg, fremden Text unter Adams Adresse zu setzen. Was nicht in dieser
    # Liste steht, kann kein Absender werden.
    aliasse: tuple[str, ...] = ()

    def darf_senden_als(self, adresse: str) -> bool:
        ziel = (adresse or "").strip().lower()
        return ziel == self.adresse.lower() or ziel in (
            a.lower() for a in self.aliasse)
    # Das Kennwort steht bewusst NICHT im Datensatz: Ein Datensatz wandert in
    # Protokolle, Fehlermeldungen und Fehlersuchen. Es wird bei Bedarf frisch
    # aus der Umgebung geholt und sofort wieder vergessen.

    def _kennwort(self) -> str:
        wert = os.environ.get(f"MAIL_{self.name.upper()}_KENNWORT") or ""
        if not wert:
            raise Abgewiesen(
                f"Für „{self.name}“ ist kein Kennwort hinterlegt. Es gehört in "
                "die geschützte Umgebungsdatei — nie in den Chat, nie ins Repo.")
        return wert


def konten() -> dict[str, Konto]:
    """Liest die eingerichteten Konten aus der Umgebung.

    Ein unvollständig eingerichtetes Konto wird **weggelassen, nicht geraten** —
    ein halb konfigurierter Versandweg ist gefährlicher als gar keiner.
    """
    raus: dict[str, Konto] = {}
    namen = {s.split("_")[1] for s in os.environ
             if s.startswith("MAIL_") and len(s.split("_")) > 2}
    for n in sorted(namen):
        werte = {f: os.environ.get(f"MAIL_{n}_{f}", "").strip() for f in _FELDER}
        if not all(werte[f] for f in ("ADRESSE", "BENUTZER", "KENNWORT",
                                      "IMAP", "SMTP")):
            continue
        roh = os.environ.get(f"MAIL_{n}_ALIASSE", "")
        aliasse = tuple(a.strip() for a in re.split(r"[,\s]+", roh)
                        if a.strip() and "@" in a)
        raus[n.lower()] = Konto(name=n.lower(), adresse=werte["ADRESSE"],
                                benutzer=werte["BENUTZER"], imap=werte["IMAP"],
                                smtp=werte["SMTP"], aliasse=aliasse)
    return raus


def eingerichtet() -> bool:
    return bool(konten())


# ------------------------------------------------------------------ Entwurf --
@dataclass
class Entwurf:
    konto: str
    an: list[str]
    betreff: str
    text: str
    anhaenge: list[str] = field(default_factory=list)
    kennung: str = ""          # Freigabe-Kennung, sobald vorgelegt
    absender: str = ""         # leer = die Hauptadresse des Kontos

    def lesbar(self) -> str:
        """Die wörtliche Vorlage — Konkret vor Label.

        Bewusst vollständig: Empfänger, Betreff, Text und jeder Anhang mit Namen
        und Größe. Wer eine Mail freigibt, muss sehen, was hinausgeht, nicht
        eine Beschreibung davon.
        """
        zeilen = [f"Von:     {self.absender or self.konto}",
                  f"An:      {', '.join(self.an)}",
                  f"Betreff: {self.betreff}", "", self.text.strip()]
        for p in self.anhaenge:
            groesse = Path(p).stat().st_size / 1024
            zeilen.append(f"[Anhang: {Path(p).name} · {groesse:.0f} KiB]")
        return "\n".join(zeilen)


def _kopffeld(wert: str, feld: str) -> str:
    """Weist ab, statt zu säubern — ein solcher Wert ist nie ein Versehen."""
    if _STEUERZEICHEN.search(wert or ""):
        raise Abgewiesen(
            f"Das Feld „{feld}“ enthält Steuerzeichen. Damit ließen sich "
            "zusätzliche Kopfzeilen einschleusen (etwa ein stilles Bcc) — "
            "solche Entwürfe entstehen hier nicht.")
    return (wert or "").strip()


def _adresse_pruefen(roh: str) -> str:
    name, adr = parseaddr(_kopffeld(roh, "An"))
    if not adr or "@" not in adr or adr.startswith("@") or adr.endswith("@"):
        raise Abgewiesen(f"Keine brauchbare Empfängeradresse: {roh!r}")
    return adr


def _anhang_pruefen(pfad: str) -> str:
    p = Path(pfad).expanduser()
    try:
        p = p.resolve(strict=True)
    except OSError:
        raise Abgewiesen(f"Anhang nicht gefunden: {pfad}")
    if not p.is_file():
        raise Abgewiesen(f"Anhang ist keine Datei: {pfad}")
    niedrig = str(p).lower()
    if any(m in niedrig for m in _GEHEIME_PFADE):
        raise Abgewiesen(
            f"„{p.name}“ liegt in einem Geheimnis-Pfad. Eine solche Datei "
            "verlässt das Haus nicht — auch nicht auf ausdrücklichen Wunsch.")
    if p.stat().st_size > ANHANG_GRENZE:
        raise Abgewiesen(f"„{p.name}“ ist größer als "
                         f"{ANHANG_GRENZE // 1024 // 1024} MiB.")
    return str(p)


def entwerfen(konto: str, an, betreff: str, text: str,
              anhaenge=None, absender: str = "") -> Entwurf:
    """Baut einen Entwurf und prüft ihn — **sendet nichts.**"""
    verfuegbar = konten()
    if konto not in verfuegbar:
        raise Abgewiesen(
            f"Kein Konto „{konto}“ eingerichtet. Vorhanden: "
            + (", ".join(verfuegbar) or "keines"))
    k = verfuegbar[konto]
    if absender and not k.darf_senden_als(absender):
        erlaubt = ", ".join((k.adresse,) + k.aliasse)
        raise Abgewiesen(
            f"„{absender}“ ist für dieses Konto nicht als Absender hinterlegt. "
            f"Erlaubt sind: {erlaubt}. Ein frei wählbarer Absender käme einer "
            "Vollmacht gleich — die Liste steht bewusst in der geschützten "
            "Umgebungsdatei und nicht im Gespräch.")
    ziele = [an] if isinstance(an, str) else list(an or [])
    if not ziele:
        raise Abgewiesen("Ohne Empfänger kein Entwurf.")
    if not (betreff or "").strip():
        raise Abgewiesen("Ohne Betreff kein Entwurf — ein leerer Betreff "
                         "landet beim Empfänger im Spam.")
    if not (text or "").strip():
        raise Abgewiesen("Ohne Text kein Entwurf.")
    return Entwurf(konto=konto,
                   an=[_adresse_pruefen(z) for z in ziele],
                   betreff=_kopffeld(betreff, "Betreff")[:200],
                   text=text,
                   anhaenge=[_anhang_pruefen(p) for p in (anhaenge or [])],
                   absender=_kopffeld(absender, "Absender") or k.adresse)


def zur_freigabe(e: Entwurf, herkunft: str = "E-Mail") -> str:
    """Legt den Entwurf auf den Parkplatz (9.4). Rückgabe: die Kennung.

    **Ampel gelb, nicht grün** — auch wenn der Inhalt harmlos ist: Ein Versand
    ist unwiderruflich, und Leitplanke 3 verbietet Sammelfreigaben für alles,
    was nicht reversibles Grün ist. Es soll bewusst **keinen Dauer-Knopf für
    E-Mail** geben.

    Der **Rückweg bleibt leer**, und das ist kein Versäumnis: Für eine
    abgeschickte Mail gibt es keinen. Das Feld ehrlich leer zu lassen ist
    richtiger, als einen zu erfinden — und es hält den Entwurf zugleich aus der
    Bündelung heraus.
    """
    a = freigaben.stellen(
        titel=f"E-Mail an {', '.join(e.an)}: {e.betreff}"[:120],
        aktion=e.lesbar(),
        ampel="gelb",
        herkunft=herkunft,
        begruendung="Versand ist unwiderruflich — bitte Empfänger und Anhänge "
                    "prüfen.",
        rueckweg="")
    e.kennung = a.kennung
    return a.kennung


def _freigabe_pruefen(e: Entwurf) -> None:
    """Der Riegel: ohne Adams Urteil geht nichts hinaus."""
    if not e.kennung:
        raise Abgewiesen("Dieser Entwurf wurde nie vorgelegt. Versand ohne "
                         "Freigabe gibt es nicht.")
    urteil = freigaben.urteil_lesen(e.kennung)
    if not urteil:
        raise Abgewiesen("Für diesen Entwurf liegt noch kein Urteil vor. "
                         "Solange nichts entschieden ist, geschieht nichts — "
                         "das ist kein Nein, nur ein Noch-nicht.")
    if urteil.get("urteil") != "freigegeben":
        raise Abgewiesen("Dieser Entwurf wurde abgelehnt.")


def senden(e: Entwurf) -> str:
    """Sendet — **nur** mit vorliegender Freigabe. Rückgabe: die Message-ID."""
    _freigabe_pruefen(e)
    k = konten()[e.konto]

    # Zweite Prüfung kurz vor dem Absenden: Die Liste kann sich seit dem
    # Entwurf geändert haben, und dies ist die letzte Stelle, an der es noch
    # jemand merken kann.
    if not k.darf_senden_als(e.absender or k.adresse):
        raise Abgewiesen(f"„{e.absender}“ ist kein erlaubter Absender.")

    m = EmailMessage()
    m["From"] = e.absender or k.adresse
    m["To"] = ", ".join(e.an)
    m["Subject"] = e.betreff
    m["Date"] = formatdate(localtime=True)
    m["Message-ID"] = make_msgid()
    m.set_content(e.text)
    for p in e.anhaenge:
        pfad = Path(p)
        m.add_attachment(pfad.read_bytes(), maintype="application",
                         subtype="octet-stream", filename=pfad.name)

    wirt, _, port = k.smtp.partition(":")
    with smtplib.SMTP_SSL(wirt, int(port or 465),
                          context=ssl.create_default_context()) as s:
        s.login(k.benutzer, k._kennwort())
        s.send_message(m)
    return m["Message-ID"]


# -------------------------------------------------------------- Posteingang --
def _entziffern(roh: str) -> str:
    """Kopfzeilen kommen kodiert; Steuerzeichen fliegen dabei raus."""
    try:
        text = str(make_header(decode_header(roh or "")))
    except Exception:
        text = roh or ""
    return _STEUERZEICHEN.sub(" ", text).strip()


def posteingang(konto: str, anzahl: int = 10) -> list[dict]:
    """Die jüngsten Nachrichten — **nur Kopfzeilen**.

    Zweistufig wie überall sonst: Erst der Überblick, der Text auf Abruf. Das
    spart nicht nur Aufwand, es hält auch Fremdtext aus dem Zusammenhang
    heraus, solange ihn niemand angefordert hat.
    """
    verfuegbar = konten()
    if konto not in verfuegbar:
        raise Abgewiesen(
            f"Kein Konto „{konto}“ eingerichtet."
            + (f" Vorhanden: {', '.join(sorted(verfuegbar))}." if verfuegbar
               else " Es ist überhaupt keines hinterlegt."))
    k = verfuegbar[konto]
    # **A3 — Grenzen und ehrliche Fehlschläge.**
    #
    # Der Deckel ist **hart**, nicht nur eine Vorgabe: Ein Aufrufer, der sich
    # vertippt, holt sonst tausend Kopfzeilen in den Kontext. Fremdtext ist
    # genau das, wovon so wenig wie möglich hereinkommen soll — der Deckel ist
    # hier keine Bequemlichkeit, sondern Teil der Absicherung.
    anzahl = max(1, min(int(anzahl or 10), MAX_ABRUF))
    wirt, _, port = k.imap.partition(":")
    raus: list[dict] = []
    try:
        return _abrufen(k, wirt, port, anzahl, raus)
    except Abgewiesen:
        raise
    except imaplib.IMAP4.error as e:
        # **Der häufigste echte Fall, und er hat einen eigenen Text**: falsche
        # Zugangsdaten. Ein „Abruf fehlgeschlagen" ließe Adam raten, ob der
        # Server weg ist oder das Kennwort falsch — und bei mailbox.org ist es
        # fast immer Letzteres (App-Passwort statt Kontokennwort).
        log.warning("IMAP-Anmeldung/Abruf abgelehnt für %s", konto)
        raise Abgewiesen(
            f"Das Postfach „{konto}“ hat den Zugriff abgelehnt. Meist ist das "
            "das Kennwort — manche Anbieter verlangen ein eigenes "
            "App-Passwort statt des Kontokennworts.") from None
    except (OSError, ssl.SSLError) as e:
        # Netz, Name, Zeitüberschreitung. Der Grund wird BENANNT, nie
        # stillschweigend eine leere Liste zurückgegeben — eine leere Liste
        # heißt „keine Post", und das wäre eine Falschauskunft.
        log.warning("IMAP-Verbindung zu %s fehlgeschlagen: %s", wirt, e)
        raise Abgewiesen(
            f"Ich habe „{konto}“ nicht erreicht ({wirt}): {e}. "
            "Das ist ein Verbindungsproblem, keine leere Mailbox.") from None


def _abrufen(k, wirt: str, port: str, anzahl: int, raus: list) -> list[dict]:
    """Der eigentliche Abruf — herausgezogen, damit die Fehlerbehandlung oben
    lesbar bleibt und jeder Fall seinen eigenen Text bekommt."""
    with imaplib.IMAP4_SSL(wirt, int(port or 993),
                           ssl_context=ssl.create_default_context(),
                           # Ohne Frist hängt der Abruf am toten Server, bis
                           # jemand den Bot neu startet — und Adam sieht nur,
                           # dass nichts kommt.
                           timeout=ABRUF_FRIST_S) as v:
        v.login(k.benutzer, k._kennwort())
        v.select("INBOX", readonly=True)          # readonly: nichts verändern
        _, daten = v.search(None, "ALL")
        kennungen = (daten[0].split() if daten and daten[0] else [])
        for kid in reversed(kennungen[-max(1, anzahl):]):
            _, teil = v.fetch(kid, "(BODY.PEEK[HEADER.FIELDS "
                                   "(FROM SUBJECT DATE)])")
            kopf = b"".join(t[1] for t in teil if isinstance(t, tuple))
            felder = _kopf_zerlegen(kopf)
            raus.append({"kennung": kid.decode(),
                         "von": felder.get("from", "—"),
                         "betreff": felder.get("subject", "(ohne Betreff)"),
                         "datum": felder.get("date", "")})
    return raus


def _kopf_zerlegen(roh: bytes) -> dict[str, str]:
    """Kopfzeilen → Felder, über den **Standard-Parser**. (Stufe A1)

    **Warum nicht mehr selbst zerlegen.** Hier stand eine eigene Schleife:
    `splitlines()`, dann an `:` teilen. Die kennt **keine gefalteten
    Kopfzeilen** — im Mail-Format darf ein langer Wert über mehrere Zeilen
    laufen, wenn die Fortsetzung mit Leerraum beginnt. Eine Zeile ohne
    Doppelpunkt fiel damit unter den Tisch, und eine Fortsetzung **mit**
    Doppelpunkt wurde als **eigenes Feld** gelesen.

    Genau das ist der Kern von Engywucks A1 — **aber eine Stufe früher als er
    beschrieb.** Sein Weg („der entzifferte Wert erzeugt eine Zeile, die die
    nächste Runde als Kopffeld liest") greift nicht: Die Schleife lief über den
    **rohen** Kopf, entzifferte Werte kamen nie in sie zurück. Gemessen in
    `scripts/mess_kopfzeilen_a1.py`, elf Varianten.

    Der Weg, der greift, ist der **unkodierte**: ein echtes CRLF im rohen Kopf.
    Dann sieht `splitlines()` zwei Zeilen, und `From: chef@firma.de` wird zum
    Absender. Ob ein IMAP-Server so etwas ausliefert, habe ich **nicht** gegen
    einen echten Server gemessen — die Lücke wird geschlossen, ohne dass ich
    behaupte, sie sei praktisch erreichbar.

    **`email.parser` macht diesen Fehler nicht.** Er kennt die Faltung, er
    kennt die Wiederholung desselben Feldnamens, und er ist seit Jahrzehnten
    gegen echte Post gelaufen. *Fremdes nehmen, wo es nicht ans Herz geht* —
    hier geht es nicht ans Herz: Es ist Formatarbeit, keine Schrankenlogik.

    **Bei Wiederholung gewinnt die ERSTE.** Ein zweites `From:` ist der
    klassische Fälschungsversuch; die erste Nennung ist die, die der Server
    gesetzt hat.
    """
    from email import policy
    from email.parser import Parser
    try:
        # **Erst dekodieren, dann zerlegen** — nicht `BytesParser`. Der liest
        # Kopfzeilen byteweise (formal richtig: dort ist nur ASCII erlaubt),
        # und ein Mehrbyte-Zeichen zerfaellt dabei in Ersatzzeichen. Gemessen:
        # ein rohes U+0085 im Betreff ergab `Rechnung\ufffd\ufffdFrom: …`.
        #
        # Sicherheitsrelevant ist das nicht — der Absender bleibt echt. Aber
        # Adam bekaeme Kauderwelsch zu lesen, und das faellt ihm zu Recht auf.
        nachricht = Parser(policy=policy.compat32).parsestr(
            roh.decode("utf-8", "replace"), headersonly=True)
    except Exception:
        log.exception("Kopfzeilen nicht zerlegbar")
        return {}
    felder: dict[str, str] = {}
    for name, wert in nachricht.items():
        schluessel = name.strip().lower()
        if schluessel in felder:
            continue                      # die erste Nennung gewinnt
        felder[schluessel] = _entziffern(wert)
    return felder


def nachricht_text(konto: str, kennung: str) -> tuple[dict, str, list[str]]:
    """**Genau eine** Nachricht holen — Kopf, sichtbarer Text, Verborgenes.

    **Stufe B, und die Zweistufigkeit ist der Punkt.** Der Überblick kostet
    nichts und holt nur Kopfzeilen; der Text kommt erst, wenn Adam ihn
    ausdrücklich anfordert. So bleibt Fremdtext aus dem Zusammenhang heraus,
    solange ihn niemand braucht — dieselbe Zweistufigkeit wie bei Video,
    Dokument und Link-Ablage.

    **Weiterhin `readonly` und `BODY.PEEK`.** Ein fremdes Postfach wird gelesen,
    nie verändert: Ein gesetztes Flag wanderte auf jedes andere Gerät, und Adam
    hielte eine Mail für gelesen, die er nie gesehen hat.

    **Anhänge werden nicht berührt** — auch nicht „nur zum Anzeigen". Sie sind
    eine eigene Risikoklasse und ein eigener Auftrag; hier wird ausschließlich
    der Textteil gelesen.
    """
    verfuegbar = konten()
    if konto not in verfuegbar:
        raise Abgewiesen(f"Kein Konto [{konto}] eingerichtet.")
    if not re.fullmatch(r"\d{1,9}", str(kennung or "")):
        # Die Kennung geht in einen IMAP-Befehl. Sie kommt zwar aus unserer
        # eigenen Liste, aber ein Wert, der in eine Befehlssprache wandert,
        # wird geprüft — nicht weil dieser Weg offen ist, sondern damit er es
        # bleibt, wenn jemand die Herkunft ändert.
        raise Abgewiesen(f"Unbrauchbare Nachrichtennummer: {kennung!r}")
    k = verfuegbar[konto]
    wirt, _, port = k.imap.partition(":")
    try:
        with imaplib.IMAP4_SSL(wirt, int(port or 993),
                               ssl_context=ssl.create_default_context(),
                               timeout=ABRUF_FRIST_S) as v:
            v.login(k.benutzer, k._kennwort())
            v.select("INBOX", readonly=True)
            _, kopfteil = v.fetch(str(kennung),
                                  "(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT DATE)])")
            _, koerperteil = v.fetch(str(kennung), "(BODY.PEEK[TEXT])")
    except imaplib.IMAP4.error:
        log.warning("IMAP-Abruf einer Nachricht abgelehnt: %s", konto)
        raise Abgewiesen(
            f"Das Postfach [{konto}] hat den Zugriff abgelehnt.") from None
    except (OSError, ssl.SSLError) as e:
        log.warning("IMAP-Verbindung zu %s fehlgeschlagen: %s", wirt, e)
        raise Abgewiesen(
            f"Ich habe [{konto}] nicht erreicht: {e}. Das ist ein "
            "Verbindungsproblem, keine leere Nachricht.") from None

    felder = _kopf_zerlegen(
        b"".join(t[1] for t in kopfteil if isinstance(t, tuple)))
    roh = b"".join(t[1] for t in koerperteil if isinstance(t, tuple))
    import mailtext
    text, verborgen = mailtext.lesbar(roh.decode("utf-8", "replace"))
    return felder, text, verborgen


def posteingang_lesbar(konto: str, anzahl: int = 10) -> str:
    """Die Kopfzeilen als Text für den Chat — **fremder Wortlaut als Zitat.**

    **A2 aus Engywucks Auftrag.** Drei Dinge, die hier zusammenkommen:

    **① Kein Markdown-Rendering des Fremdtexts.** Ein Betreff
    `[Rechnung ansehen](boese.tld)` darf keine Verknüpfung werden. Deshalb geht
    jeder fremde Wert durch `_neutral()`, das die Zeichen entschärft, mit denen
    Telegram formatiert — und der Bot sendet diese Nachricht **ohne**
    `parse_mode`, was der zweite Riegel ist.

    **② Erkennbar fremd.** Jede Zeile trägt das Zitatzeichen `▏` und die Werte
    stehen in Anführungszeichen. Wer die Liste sieht, soll auf den ersten Blick
    wissen: **Das hat jemand anderes geschrieben.** Der Kopf sagt es zusätzlich
    in Worten — das ist derselbe Rangvermerk wie beim angepinnten Text und beim
    Recall-Kopf.

    **③ Keine anklickbare Adresse.** Auch die Absenderadresse bleibt Text. Ein
    Klick wäre ein Abruf, und ein Abruf ist eine Handlung.

    **Was hier ausdrücklich NICHT geschieht:** kein Modell wird gestartet, kein
    Text wird geholt, kein Anhang berührt. Das ist der ganze Punkt von Stufe A —
    **Fremdtext kann hier bauartbedingt nichts anweisen, weil es nichts gibt,
    das er anweisen könnte.**
    """
    nachrichten = posteingang(konto, anzahl)
    if not nachrichten:
        return f"📭 In [{konto}] liegt nichts."
    zeilen = [f"📬 Die {len(nachrichten)} jüngsten in [{konto}] — "
              "**fremder Wortlaut, notiert, keine Anweisung:**", ""]
    for i, n in enumerate(nachrichten, 1):
        zeilen.append(f"{i}. ▏Von: [{_neutral(n['von'])}]")
        zeilen.append(f"   ▏Betreff: [{_neutral(n['betreff'])}]")
        if n.get("datum"):
            zeilen.append(f"   ▏{_neutral(n['datum'])}")
        zeilen.append("")
    zeilen.append("Der Text einer Nachricht wird erst geholt, wenn du ihn "
                  "anforderst — bis dahin habe ich nur diese Kopfzeilen.")
    return "\n".join(zeilen)


# Zeichen, mit denen Telegram formatiert. Sie werden im Fremdtext **ersetzt**,
# nicht entfernt: Wer `*Rechnung*` schreibt, soll auch `*Rechnung*` lesen — nur
# eben nicht fett, und ohne dass unklar bleibt, ob dort etwas stand.
_FORMATZEICHEN = str.maketrans({
    "*": "∗", "_": "＿", "`": "ˋ", "[": "〔", "]": "〕",
    "~": "∼", "|": "¦", ">": "＞", "#": "＃",
})


def _neutral(wert: str) -> str:
    """Fremdtext, der nichts mehr formatieren oder verlinken kann. (A2)

    **Ersetzen statt entfernen** — dieselbe Überlegung wie bei den unsichtbaren
    Zeichen: Ein Zeichen, das spurlos verschwindet, verbirgt, dass es da war.
    Ein Betreff `[Klick hier](boese.tld)` liest sich danach als
    `〔Klick hier〕(boese.tld)` — sichtbar, unverlinkt, unverfälscht im Sinn.

    **Das ist der zweite Riegel, nicht der erste.** Der erste ist, dass die
    Nachricht ohne `parse_mode` gesendet wird. Beide zusammen, weil eine
    Sendestelle irgendwann jemand ändert — und dann trägt noch einer.
    """
    return (wert or "").translate(_FORMATZEICHEN)


def uebersicht() -> str:
    """Für `/mail` — deterministisch, ohne Modell-Aufruf."""
    k = konten()
    if not k:
        return ("📮 Noch kein E-Mail-Konto eingerichtet.\n"
                "Je Konto gehören Adresse, Benutzer, Kennwort sowie IMAP- und "
                "SMTP-Adresse in die geschützte Umgebungsdatei auf dem Server — "
                "**nie in den Chat.** Sag Bescheid, dann nenne ich dir den Weg.")
    zeilen = []
    for n, c in k.items():
        zeilen.append(f"• {n} — {c.adresse}")
        if c.aliasse:
            zeilen.append("   auch als: " + ", ".join(c.aliasse))
    return ("📮 Eingerichtete Konten:\n" + "\n".join(zeilen)
            + "\n\nVersand geht immer über den Freigabe-Knopf: Ich lege dir "
              "Empfänger, Betreff und Anhänge wörtlich vor, und erst dein "
              "Urteil schickt sie los.")
