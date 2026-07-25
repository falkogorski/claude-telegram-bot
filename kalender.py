# <!-- ROLLE: kalender-caldav -->
"""Kalender und Erinnerungen über CalDAV (iCloud) — vorgezogen am 25.07.2026.

**Warum vorgezogen:** Das Prüfraster der Basisfähigkeiten nannte den Kalender
die einzige Lücke, die Adam **täglich** trifft — Aufgaben aufsprechen,
Erinnerungen, Termine. Phase 7 stand bei null und war spät terminiert. Die
Richtungsentscheidung war längst gefallen (**iCloud, nicht Google**), und
Kalender und Erinnerungen laufen über **dasselbe** CalDAV-Verfahren: ein Bau
statt zwei.

**Verifiziert statt angenommen:** Der Mac-Weg über AppleScript fällt auf Linux
weg — deshalb CalDAV, das Apple offiziell anbietet und das auf jedem System
läuft. Zugang über `caldav.icloud.com` mit einem **anwendungsspezifischen
Kennwort**; das normale Apple-Kennwort funktioniert dort nicht.

**💰 Keine Kosten:** `caldav` ist ein freies Paket, iCloud ist in Adams
Apple-Konto enthalten, der Verkehr läuft direkt zu Apple. Keine Gebühren,
kein Zwischendienst.

**🔐 Geheimnis-Lage:** Zugangsdaten kommen ausschließlich aus der Umgebung
(`ICLOUD_CALDAV_USER`, `ICLOUD_CALDAV_APP_PASSWORT`) — niemals aus einer Datei
im Repo, niemals im Klartext in einer Nachricht. Ohne sie arbeitet das Modul
**nicht halb, sondern gar nicht** und sagt es deutlich; ein halb verbundener
Kalender wäre schlimmer als keiner, weil man ihm glauben würde.
"""
from __future__ import annotations

import datetime as _dt
import os
from dataclasses import dataclass

ICLOUD_URL = os.environ.get("CALDAV_URL") or "https://caldav.icloud.com/"


@dataclass
class Termin:
    """Ein Kalendereintrag in der Form, in der der Bot ihn braucht."""
    beginn: _dt.datetime
    ende: _dt.datetime | None
    titel: str
    ort: str = ""
    notiz: str = ""
    ganztags: bool = False

    def lesbar(self) -> str:
        """Eine Zeile, wie ein Mensch sie sagen würde."""
        tage = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag",
                "Samstag", "Sonntag")
        tag = tage[self.beginn.weekday()]
        datum = self.beginn.strftime("%d.%m.")
        if self.ganztags:
            zeit = "ganztägig"
        elif self.ende is not None:
            zeit = f"{self.beginn:%H:%M} bis {self.ende:%H:%M}"
        else:
            zeit = f"{self.beginn:%H:%M}"
        teile = [f"{tag}, {datum}, {zeit} — {self.titel}"]
        if self.ort:
            teile.append(f"({self.ort})")
        return " ".join(teile)


@dataclass
class Aufgabe:
    """Eine Erinnerung / ein Vorhaben (CalDAV nennt das VTODO)."""
    titel: str
    faellig: _dt.datetime | None = None
    notiz: str = ""
    erledigt: bool = False

    def lesbar(self) -> str:
        if self.faellig is None:
            return self.titel
        return f"{self.titel} — fällig {self.faellig:%d.%m., %H:%M}"


class NichtEingerichtet(RuntimeError):
    """Zugangsdaten fehlen — bewusst ein Fehler, kein stiller Leerlauf."""


def zugang_vorhanden() -> bool:
    return bool(os.environ.get("ICLOUD_CALDAV_USER")
                and os.environ.get("ICLOUD_CALDAV_APP_PASSWORT"))


def _client():
    if not zugang_vorhanden():
        raise NichtEingerichtet(
            "Kalender-Zugang fehlt. Nötig sind ICLOUD_CALDAV_USER (die "
            "Apple-Kennung) und ICLOUD_CALDAV_APP_PASSWORT (ein "
            "anwendungsspezifisches Kennwort von appleid.apple.com — das "
            "normale Apple-Kennwort funktioniert bei CalDAV nicht).")
    import caldav                                     # noqa: PLC0415
    return caldav.DAVClient(
        url=ICLOUD_URL,
        username=os.environ["ICLOUD_CALDAV_USER"],
        password=os.environ["ICLOUD_CALDAV_APP_PASSWORT"])


def _kalender_waehlen(principal, name: str | None, aufgabenliste: bool = False):
    """Sucht eine Sammlung nach Namen; sonst die erste passende.

    Bewusst tolerant beim Namen (Groß-/Kleinschreibung, Teiltreffer): Adam sagt
    „privat", die Sammlung heißt vielleicht „Privat" oder „Zuhause". Wird
    nichts Passendes gefunden, wird das **gesagt** und nicht stillschweigend
    eine beliebige Sammlung genommen — in den falschen Kalender zu schreiben
    ist schlimmer als nicht zu schreiben.
    """
    sammlungen = principal.calendars()
    if not sammlungen:
        raise NichtEingerichtet("Es ist keine Kalender-Sammlung erreichbar.")
    if name:
        gesucht = name.strip().lower()
        for k in sammlungen:
            if gesucht in (k.name or "").strip().lower():
                return k
        vorhandene = ", ".join((k.name or "?") for k in sammlungen)
        raise LookupError(
            f"Keine Sammlung namens „{name}“ gefunden. Vorhanden: {vorhandene}")
    return sammlungen[0]


def sammlungen_auflisten() -> list[str]:
    """Welche Kalender und Aufgabenlisten gibt es? — der erste Handgriff."""
    c = _client()
    return [(k.name or "(ohne Namen)") for k in c.principal().calendars()]


def termine_lesen(von: _dt.datetime | None = None, tage: int = 7,
                  kalender: str | None = None) -> list[Termin]:
    """Termine eines Zeitraums, chronologisch."""
    von = von or _dt.datetime.now().astimezone().replace(
        hour=0, minute=0, second=0, microsecond=0)
    bis = von + _dt.timedelta(days=tage)
    k = _kalender_waehlen(_client().principal(), kalender)
    ergebnis: list[Termin] = []
    for e in k.search(start=von, end=bis, event=True, expand=True):
        v = getattr(e, "vobject_instance", None)
        if v is None or not hasattr(v, "vevent"):
            continue
        ev = v.vevent
        beginn = getattr(ev, "dtstart", None)
        if beginn is None:
            continue
        b = beginn.value
        ganztags = not isinstance(b, _dt.datetime)
        if ganztags:
            b = _dt.datetime.combine(b, _dt.time.min).astimezone()
        ende_feld = getattr(ev, "dtend", None)
        e_wert = ende_feld.value if ende_feld is not None else None
        if e_wert is not None and not isinstance(e_wert, _dt.datetime):
            e_wert = _dt.datetime.combine(e_wert, _dt.time.min).astimezone()
        ergebnis.append(Termin(
            beginn=b, ende=e_wert,
            titel=str(getattr(ev, "summary", None).value
                      if hasattr(ev, "summary") else "(ohne Titel)"),
            ort=str(ev.location.value) if hasattr(ev, "location") else "",
            ganztags=ganztags))
    ergebnis.sort(key=lambda t: t.beginn)
    return ergebnis


def termin_anlegen(t: Termin, kalender: str | None = None) -> str:
    """Legt einen Termin an. Rückgabe: eine lesbare Bestätigung.

    **Bewusst ohne eigene Rückfrage:** Ob Adam vorher bestätigt, entscheidet der
    Bot an der Oberfläche — dieses Modul ist das Werkzeug, nicht das Gatter.
    Doppelte Gatter an verschiedenen Stellen führen dazu, dass sich jede Stelle
    auf die andere verlässt.
    """
    k = _kalender_waehlen(_client().principal(), kalender)
    ende = t.ende or (t.beginn + _dt.timedelta(hours=1))
    k.save_event(dtstart=t.beginn, dtend=ende, summary=t.titel,
                 location=t.ort or None, description=t.notiz or None)
    return f"Termin angelegt: {t.lesbar()}"


def aufgaben_lesen(liste: str | None = None,
                   auch_erledigte: bool = False) -> list[Aufgabe]:
    """Offene Erinnerungen/Vorhaben."""
    k = _kalender_waehlen(_client().principal(), liste, aufgabenliste=True)
    ergebnis: list[Aufgabe] = []
    for t in k.todos(include_completed=auch_erledigte):
        v = getattr(t, "vobject_instance", None)
        if v is None or not hasattr(v, "vtodo"):
            continue
        vt = v.vtodo
        faellig = None
        if hasattr(vt, "due"):
            d = vt.due.value
            faellig = d if isinstance(d, _dt.datetime) else \
                _dt.datetime.combine(d, _dt.time.min).astimezone()
        ergebnis.append(Aufgabe(
            titel=str(vt.summary.value) if hasattr(vt, "summary") else "(ohne Titel)",
            faellig=faellig,
            erledigt=bool(hasattr(vt, "completed"))))
    ergebnis.sort(key=lambda a: (a.faellig is None, a.faellig or _dt.datetime.max))
    return ergebnis


def aufgabe_anlegen(a: Aufgabe, liste: str | None = None) -> str:
    """Legt eine Erinnerung an."""
    k = _kalender_waehlen(_client().principal(), liste, aufgabenliste=True)
    k.save_todo(summary=a.titel,
                due=a.faellig if a.faellig else None,
                description=a.notiz or None)
    return f"Erinnerung angelegt: {a.lesbar()}"
