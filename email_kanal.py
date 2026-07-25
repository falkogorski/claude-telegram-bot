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

# Ein Konto heißt hier schlicht „geschaeftlich" oder „privat"; die Zugangsdaten
# stehen unter MAIL_<NAME>_… in der Umgebung. Der Name taucht im Chat auf, die
# Daten nie.
_FELDER = ("ADRESSE", "BENUTZER", "KENNWORT", "IMAP", "SMTP")

# Was in einem Kopffeld nichts zu suchen hat. Steuerzeichen ermöglichen die
# Einschleusung zusätzlicher Kopfzeilen (siehe Modulkopf).
_STEUERZEICHEN = re.compile(r"[\r\n\x00-\x08\x0b\x0c\x0e-\x1f]")

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
        raus[n.lower()] = Konto(name=n.lower(), adresse=werte["ADRESSE"],
                                benutzer=werte["BENUTZER"], imap=werte["IMAP"],
                                smtp=werte["SMTP"])
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

    def lesbar(self) -> str:
        """Die wörtliche Vorlage — Konkret vor Label.

        Bewusst vollständig: Empfänger, Betreff, Text und jeder Anhang mit Namen
        und Größe. Wer eine Mail freigibt, muss sehen, was hinausgeht, nicht
        eine Beschreibung davon.
        """
        zeilen = [f"Von:     {self.konto}",
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
              anhaenge=None) -> Entwurf:
    """Baut einen Entwurf und prüft ihn — **sendet nichts.**"""
    verfuegbar = konten()
    if konto not in verfuegbar:
        raise Abgewiesen(
            f"Kein Konto „{konto}“ eingerichtet. Vorhanden: "
            + (", ".join(verfuegbar) or "keines"))
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
                   anhaenge=[_anhang_pruefen(p) for p in (anhaenge or [])])


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

    m = EmailMessage()
    m["From"] = k.adresse
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
        raise Abgewiesen(f"Kein Konto „{konto}“ eingerichtet.")
    k = verfuegbar[konto]
    wirt, _, port = k.imap.partition(":")
    raus: list[dict] = []
    with imaplib.IMAP4_SSL(wirt, int(port or 993),
                           ssl_context=ssl.create_default_context()) as v:
        v.login(k.benutzer, k._kennwort())
        v.select("INBOX", readonly=True)          # readonly: nichts verändern
        _, daten = v.search(None, "ALL")
        kennungen = (daten[0].split() if daten and daten[0] else [])
        for kid in reversed(kennungen[-max(1, anzahl):]):
            _, teil = v.fetch(kid, "(BODY.PEEK[HEADER.FIELDS "
                                   "(FROM SUBJECT DATE)])")
            kopf = b"".join(t[1] for t in teil if isinstance(t, tuple))
            felder = {}
            for zeile in kopf.decode("utf-8", "replace").splitlines():
                if ":" in zeile:
                    name, _, wert = zeile.partition(":")
                    felder[name.strip().lower()] = _entziffern(wert)
            raus.append({"kennung": kid.decode(),
                         "von": felder.get("from", "—"),
                         "betreff": felder.get("subject", "(ohne Betreff)"),
                         "datum": felder.get("date", "")})
    return raus


def uebersicht() -> str:
    """Für `/mail` — deterministisch, ohne Modell-Aufruf."""
    k = konten()
    if not k:
        return ("📮 Noch kein E-Mail-Konto eingerichtet.\n"
                "Je Konto gehören Adresse, Benutzer, Kennwort sowie IMAP- und "
                "SMTP-Adresse in die geschützte Umgebungsdatei auf dem Server — "
                "**nie in den Chat.** Sag Bescheid, dann nenne ich dir den Weg.")
    zeilen = [f"• {n} — {c.adresse}" for n, c in k.items()]
    return ("📮 Eingerichtete Konten:\n" + "\n".join(zeilen)
            + "\n\nVersand geht immer über den Freigabe-Knopf: Ich lege dir "
              "Empfänger, Betreff und Anhänge wörtlich vor, und erst dein "
              "Urteil schickt sie los.")
