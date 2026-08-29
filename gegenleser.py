"""Der Gegenleser — und vor allem: wie man merkt, dass er NICHT gelesen hat.
<!-- ROLLE: gegenleser -->

**Auftrag:** `2026-08-28_bauauftrag-gegenleser-drei-routen.md`, Auftrag 4 —
*„Das ist die Zeile, ohne die die Sache nicht fertig ist."* Engywucks
Übernahme im Arbeitspaket, Rang 8.

## Der Kern in einem Satz

**Ein Gegenleser kann auf drei Arten versagen, und alle drei sehen von außen
wie Erfolg aus:**

| Versagen | Wie es sich anfühlt | Was hier dagegen steht |
|---|---|---|
| Der Dienst ist ausgefallen | „keine Einwände" | Ein eigener Zustand `AUSGEFALLEN`, der sich von `NICHTS_GEFUNDEN` unterscheidet und als **offen** zählt, nicht als grün |
| Das Modell stimmt höflich zu | „gründlich geprüft, alles gut" | `zustimmung_ohne_substanz()` — eine Antwort ohne Bezug auf die Vorlage ist kein Befund |
| Der Befund erreicht niemanden | dasselbe wie kein Befund | `ablegen()` schreibt an einen festen Ort und meldet, wenn das misslingt |

Das ist dieselbe Unterscheidung, die `bot.suchlage()` für die Websuche trifft —
und sie ist dort aus demselben Grund entstanden: **Ein leeres Ergebnis und ein
ausgebliebenes Ergebnis sehen gleich aus und bedeuten das Gegenteil.**

## Was dieses Modul NICHT tut — und das ist Absicht

**Es ruft keinen Anbieter auf.** Kein Schlüssel, keine Netzverbindung, keine
Kosten. Adams Entscheid, von Engywuck im Arbeitspaket festgehalten: *„Kein
Schlüssel wird angelegt, keine Route in Betrieb genommen. Ein Zugang zu einem
Bezahldienst ist Adams Handlung, nicht Micks."*

Der Aufruf wird **hereingereicht** (`ruf`), so wie `bashfreigabe` die
Geheimnis-Schranke hereingereicht bekommt. Damit ist alles hier prüfbar, ohne
dass je ein Cent fließt — und der Tag, an dem ein Schlüssel dazukommt, ändert
an dieser Datei nichts.

## 💰 Vor dem ersten echten Aufruf, in dieser Reihenfolge

1. **Ausgabenlimit beim Anbieter setzen** — nicht im eigenen Code. Das ist die
   einzige Grenze, die auch dann hält, wenn die eigene Zählung versagt.
   Voreinstellung laut Auftrag: 10 € für Route eins und zwei zusammen, 5 € für
   Route drei. Gesamtdeckel 30 € (Adams Entscheid 28.08.).
2. **Zero Data Retention** beantragen (Mistral) bzw. einschalten (xAI).
3. **Rauchtest**, dann erst einhängen.
"""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

__all__ = ["Route", "Befund", "ROUTEN", "GEPRUEFT", "NICHTS_GEFUNDEN",
           "AUSGEFALLEN", "OHNE_SUBSTANZ", "beurteilen",
           "zustimmung_ohne_substanz", "zdr_lage", "ablegen", "sammellage"]

# Die drei Zustände, und der Unterschied zwischen den ersten beiden ist der
# ganze Punkt dieses Moduls.
GEPRUEFT = "geprueft"              # hat gelesen und etwas gefunden
NICHTS_GEFUNDEN = "nichts"         # hat gelesen und nichts gefunden
AUSGEFALLEN = "ausgefallen"        # hat NICHT gelesen — zählt als offen
OHNE_SUBSTANZ = "ohne_substanz"    # hat geantwortet, aber nichts gesagt


@dataclass(frozen=True)
class Route:
    name: str
    anbieter: str
    modell: str
    rechtsraum: str
    auf_abruf: bool = False
    limit_eur: int = 10


# Reihenfolge und Werte aus dem Auftrag, samt der Voreinstellungen aus der
# Entscheidungsvollmacht — **kein Punkt wartet auf eine Antwort Adams.**
ROUTEN = (
    Route("eins", "mistral", "mistral-large-3", "EU", limit_eur=10),
    # Modellwahl beim Einbau zu MESSEN, nicht hier festzulegen: Der
    # OVHcloud-Katalog und die Kostentabelle unseres Verteilers stimmen nicht
    # überein. `gpt-oss-120b` bleibt draußen — die Leitplanke [kein OpenAI im
    # Stapel] ist Adams Wertsetzung, und die enge Auslegung ist die sichere.
    Route("zwei", "ovhcloud", "Meta-Llama-3.3-70B-Instruct", "EU", limit_eur=10),
    Route("drei", "xai", "grok-4.6", "US", auf_abruf=True, limit_eur=5),
)


@dataclass
class Befund:
    route: str
    lage: str
    text: str = ""
    hinweis: str = ""
    punkte: tuple[str, ...] = field(default=())

    @property
    def zaehlt_als_geprueft(self) -> bool:
        """**Nur zwei der vier Zustände sind eine Prüfung.**

        Ein Ausfall und eine substanzlose Zustimmung zählen als OFFEN — sonst
        wäre der Gegenleser eine Beruhigung statt einer Prüfung.
        """
        return self.lage in (GEPRUEFT, NICHTS_GEFUNDEN)


# --------------------------------------------------------------- Versagen (2)
#
# Die höfliche Zustimmung. Sie ist die heimtückischste der drei Arten, weil sie
# wie die gründlichste Arbeit aussieht.

_ZUSTIMMUNG = re.compile(
    r"^\W*(sieht gut aus|alles (gut|in ordnung|klar)|keine (einwände|einwaende|"
    r"anmerkungen|bedenken|probleme)|nichts (zu beanstanden|gefunden|auffällig)|"
    r"passt( so)?|einverstanden|zustimmung|looks good|lgtm|no (issues|concerns))",
    re.IGNORECASE)


def zustimmung_ohne_substanz(antwort: str, vorlage: str = "",
                             mindestzeichen: int = 120) -> bool:
    """Eine Antwort, die zustimmt, ohne die Vorlage anzufassen.

    **Zwei Merkmale zusammen, nie eines allein:** Sie ist kurz UND sie nimmt
    keinen Bezug auf den Inhalt. Nur auf die Länge zu prüfen wäre falsch — ein
    knapper, aber konkreter Einwand ist wertvoll. Nur auf den Wortlaut zu
    prüfen ebenfalls: [Sieht gut aus, aber Zeile 40 …] ist eine echte Prüfung.

    Der Bezug wird an **seltenen Wörtern der Vorlage** gemessen, nicht an
    häufigen — [der], [und], [nicht] stehen in jeder Antwort und belegen
    nichts.
    """
    text = (antwort or "").strip()
    if not text:
        return True
    if len(text) >= mindestzeichen:
        return False
    if not _ZUSTIMMUNG.search(text):
        return False
    if not vorlage:
        return True
    # Bezug: teilt die Antwort ein seltenes Wort mit der Vorlage?
    selten = {w.lower() for w in re.findall(r"\b\w{7,}\b", vorlage)}
    in_antwort = {w.lower() for w in re.findall(r"\b\w{7,}\b", text)}
    return not (selten & in_antwort)


# --------------------------------------------------------------- Versagen (1)

def beurteilen(route: str, antwort: str | None, fehler: str | None = None,
               vorlage: str = "") -> Befund:
    """Was ist wirklich passiert? — die reine Funktion, die alles trägt.

    Sie ruft nichts auf und schreibt nichts. Damit lässt sie sich vollständig
    ausführen — dieselbe Bauform wie `beurteilen()` im Websuche-Wächter und
    `entscheiden()` in der Bash-Positivliste.
    """
    if fehler:
        return Befund(route, AUSGEFALLEN, hinweis=(
            f"Die Route [{route}] konnte nicht pruefen: {fehler}. "
            "Das ist KEIN [nichts gefunden] — es liegt gar kein Urteil vor. "
            "Die Vorlage bleibt ungeprueft, nicht gebilligt."))
    if antwort is None:
        return Befund(route, AUSGEFALLEN, hinweis=(
            f"Die Route [{route}] hat nicht geantwortet. Ungeprueft, "
            "nicht gebilligt."))
    if zustimmung_ohne_substanz(antwort, vorlage):
        return Befund(route, OHNE_SUBSTANZ, text=antwort, hinweis=(
            f"Die Route [{route}] hat zugestimmt, ohne auf die Vorlage "
            "einzugehen. Das zaehlt als ungeprueft — eine hoefliche Zustimmung "
            "ist kein Befund."))
    punkte = tuple(z.strip(" -*•\t") for z in (antwort or "").splitlines()
                   if z.strip(" -*•\t"))
    if not punkte:
        return Befund(route, NICHTS_GEFUNDEN, text=antwort)
    return Befund(route, GEPRUEFT, text=antwort, punkte=punkte)


def sammellage(befunde) -> tuple[str, str]:
    """Die Gesamtlage über alle Routen — `(lage, Satz)`.

    **Ein einzelner tauglicher Gegenleser genügt nicht**, wenn die anderen
    stumm blieben: Dann ist die Vorlage von einem gelesen worden, und das war
    vor diesem Bau schon der Zustand. Der Satz sagt ausdrücklich, wie viele
    wirklich gelesen haben.
    """
    befunde = list(befunde)
    if not befunde:
        return (AUSGEFALLEN, "Keine Route hat geantwortet — nichts geprueft.")
    echt = [b for b in befunde if b.zaehlt_als_geprueft]
    stumm = [b for b in befunde if not b.zaehlt_als_geprueft]
    if not echt:
        return (AUSGEFALLEN,
                f"KEINE der {len(befunde)} Routen hat geprueft "
                f"({', '.join(b.route for b in stumm)}). Die Vorlage ist "
                "ungeprueft — nicht gebilligt.")
    satz = f"{len(echt)} von {len(befunde)} Routen haben geprueft"
    if stumm:
        satz += (f"; ausgefallen: {', '.join(b.route for b in stumm)}. "
                 "Das ist beim Gewichten der Befunde zu beachten")
    return (GEPRUEFT if any(b.lage == GEPRUEFT for b in echt)
            else NICHTS_GEFUNDEN, satz + ".")


# --------------------------------------------------------------- Versagen (3)

def _ablage() -> Path:
    """Wohin die Befunde gehen.

    **Eine Umgebungsgroesse, nicht zwei.** Die erste Fassung hatte zusaetzlich
    `GEGENLESER_HEIM` als Rueckfall — der Differenzmesser hat sie sofort als
    ungeriegelte Pfadquelle gemeldet, und er hatte recht: Zwei Wege zu einem
    Ort heissen, dass ein Prueflauf den einen riegelt und ueber den anderen
    doch in Adams echte Ablage schreibt. Der Rueckfall war ueberdies
    ueberfluessig, weil `GEGENLESER_DIR` denselben Dienst vollstaendig tut.
    """
    roh = os.environ.get("GEGENLESER_DIR")
    if roh:
        return Path(roh).expanduser()
    return Path.home() / ".claude" / "gegenleser"


def ablegen(befunde, marke: str) -> tuple[bool, str]:
    """Der feste Weg in die Ablage, die die Kontrollsitzung liest.

    **[Kein Befund ohne Empfaenger]** — der dritte Versagensweg. Und wenn das
    Ablegen misslingt, wird das GEMELDET statt verschluckt: Ein Befund, der
    still verschwindet, ist genau dasselbe wie kein Befund.
    """
    try:
        ordner = _ablage()
        ordner.mkdir(parents=True, exist_ok=True)
        lage, satz = sammellage(befunde)
        datei = ordner / f"{marke}.json"
        datei.write_text(json.dumps({
            "marke": marke,
            "lage": lage,
            "zusammenfassung": satz,
            "routen": [{"route": b.route, "lage": b.lage,
                        "punkte": list(b.punkte), "hinweis": b.hinweis}
                       for b in befunde],
        }, ensure_ascii=False, indent=2), encoding="utf-8")
        return (True, str(datei))
    except Exception as e:
        return (False, f"Befund konnte NICHT abgelegt werden: {e}")


# ------------------------------------------------------- Zero Data Retention

def zdr_lage(zustand: dict) -> tuple[bool, str]:
    """Ist die Datenlöschung wirklich zugesagt — oder nur beantragt?

    **Aus [was kann brechen]:** *„Zero Data Retention wird beantragt, aber nie
    bewilligt — und niemand merkt, dass die Vorlagen weiter liegen bleiben.
    Wer merkt es: niemand."*

    Deshalb zwei Felder statt eines Hakens. **Solange `bewilligt_am` leer ist,
    gilt die Route als eingeschraenkt** — und der Satz sagt es in Klartext,
    statt einen Haken zu zeigen, den niemand hinterfragt.
    """
    beantragt = (zustand or {}).get("beantragt_am")
    bewilligt = (zustand or {}).get("bewilligt_am")
    if bewilligt:
        return (True, f"Datenloeschung bewilligt am {bewilligt}.")
    if beantragt:
        return (False, f"Datenloeschung beantragt am {beantragt}, NICHT "
                       "bewilligt — die Vorlagen liegen weiterhin beim "
                       "Anbieter. Die Route gilt als eingeschraenkt.")
    return (False, "Datenloeschung weder beantragt noch bewilligt — die "
                   "Vorlagen liegen beim Anbieter. Route eingeschraenkt.")
