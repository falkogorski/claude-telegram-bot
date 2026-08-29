#!/usr/bin/env python3
"""Der Gegenleser-Prüfer — ausgeführt, ohne einen einzigen Anbieter-Aufruf.

**Rang 8, Auftrag 4.** Geprüft werden die drei Versagensarten, die von außen
wie Erfolg aussehen. Kein Schlüssel, kein Netz, keine Kosten — das Modul ruft
grundsätzlich nichts auf, deshalb ist das hier vollständig messbar.
"""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import gegenleser as g                                          # noqa: E402

fehler: list[str] = []
n = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global n
    n += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


VORLAGE = ("Bauauftrag: Die Postfach-Grenze soll je Absender gelten. "
           "Claudia darf hundert Sendungen je Stunde, alle anderen fuenf. "
           "Eingetragen wird, wer mehr darf, nie wer weniger darf.")

print("== Versagen 1: der Dienst ist ausgefallen ==")
b = g.beurteilen("eins", None, fehler="Zeitueberschreitung")
zeile("Ausfall ist NICHT [nichts gefunden]", b.lage == g.AUSGEFALLEN,
      gemessen=b.lage)
zeile("Ausfall zaehlt als offen, nicht als geprueft", not b.zaehlt_als_geprueft)
zeile("der Hinweis sagt es in Klartext",
      "nicht gebilligt" in b.hinweis.lower(), gemessen=b.hinweis)
b = g.beurteilen("eins", None)
zeile("keine Antwort ist ebenfalls ein Ausfall", b.lage == g.AUSGEFALLEN)

print("-- und die Gegenrichtung: ein echter Befund gilt --")
b = g.beurteilen("eins", "Zeile 12: die Grenze wird nie geprueft.\n"
                         "Zeile 40: der Absender kommt aus dem Auftrag selbst.",
                 vorlage=VORLAGE)
zeile("echter Befund ist geprueft", b.lage == g.GEPRUEFT, gemessen=b.lage)
zeile("die Punkte werden gezaehlt", len(b.punkte) == 2, gemessen=str(b.punkte))

print()
print("== Versagen 2: das Modell stimmt hoeflich zu ==")
for antwort, was in [
    ("Sieht gut aus.", "knapp"),
    ("Alles in Ordnung, keine Einwaende.", "zwei Floskeln"),
    ("LGTM", "englisch"),
    ("", "leer"),
    ("   ", "nur Leerzeichen"),
]:
    zeile(f"[{was}] gilt als ohne Substanz",
          g.zustimmung_ohne_substanz(antwort, VORLAGE),
          gemessen=repr(antwort))

print("-- die Gegenrichtung, und sie ist die wichtigere --")
for antwort, was in [
    ("Sieht gut aus, aber die Postfach-Grenze wird nie gemessen.",
     "Zustimmung MIT Bezug"),
    ("Der Absender stammt aus dem Auftrag selbst — das faengt keinen Fehllauf.",
     "kurzer, konkreter Einwand"),
    ("Keine Einwaende. " + "Die Begruendung dafuer ist ausfuehrlich: " * 4,
     "lang, auch wenn floskelhaft"),
]:
    zeile(f"[{was}] gilt NICHT als leer",
          not g.zustimmung_ohne_substanz(antwort, VORLAGE), gemessen=antwort[:50])

b = g.beurteilen("zwei", "Sieht gut aus.", vorlage=VORLAGE)
zeile("substanzlose Zustimmung zaehlt als UNGEPRUEFT",
      b.lage == g.OHNE_SUBSTANZ and not b.zaehlt_als_geprueft, gemessen=b.lage)

print()
print("== Versagen 3: der Befund erreicht niemanden ==")
# `resolve()` statt eines festen `/private/tmp` — den Pfad gibt es nur auf
# macOS, und dieser Pruefer starb auf dem VPS beim Import (Engywucks
# Gegenpruefung 29.08.). Was auf einer Maschine gemessen wurde, gilt auf
# der anderen nicht.
d = Path(tempfile.mkdtemp(prefix="gegenleser-")).resolve()
os.environ["GEGENLESER_DIR"] = str(d)
ok, wo = g.ablegen([g.beurteilen("eins", "Zeile 12: Grenze ungeprueft.",
                                 vorlage=VORLAGE)], "probe-1")
zeile("der Befund wird abgelegt", ok, gemessen=wo)
zeile("und liegt wirklich da", Path(wo).is_file() if ok else False)

os.environ["GEGENLESER_DIR"] = "/dev/null/unmoeglich"
ok2, meldung = g.ablegen([g.beurteilen("eins", "x", vorlage=VORLAGE)], "probe-2")
zeile("ein misslungenes Ablegen wird GEMELDET, nicht verschluckt",
      (not ok2) and "NICHT abgelegt" in meldung, gemessen=meldung)
os.environ["GEGENLESER_DIR"] = str(d)

print()
print("== die Gesamtlage ueber alle Routen ==")
lage, satz = g.sammellage([
    g.beurteilen("eins", None, fehler="down"),
    g.beurteilen("zwei", None, fehler="down"),
])
zeile("alle stumm → ausgefallen", lage == g.AUSGEFALLEN, gemessen=satz)
zeile("und der Satz sagt [nicht gebilligt]", "nicht gebilligt" in satz.lower(),
      gemessen=satz)

lage, satz = g.sammellage([
    g.beurteilen("eins", "Zeile 12: Grenze ungeprueft.", vorlage=VORLAGE),
    g.beurteilen("zwei", None, fehler="down"),
])
zeile("einer prueft, einer faellt aus → der Satz nennt beides",
      lage == g.GEPRUEFT and "ausgefallen: zwei" in satz, gemessen=satz)
zeile("die Zahl der echten Pruefer steht darin", "1 von 2" in satz,
      gemessen=satz)
zeile("leere Liste → ausgefallen", g.sammellage([])[0] == g.AUSGEFALLEN)

print()
print("== Zero Data Retention: beantragt ist nicht bewilligt ==")
ok, satz = g.zdr_lage({"beantragt_am": "2026-08-29"})
zeile("beantragt allein genuegt NICHT", not ok, gemessen=satz)
zeile("der Satz nennt die Folge",
      "eingeschraenkt" in satz.lower() and "liegen" in satz.lower(), gemessen=satz)
ok, satz = g.zdr_lage({"beantragt_am": "2026-08-29", "bewilligt_am": "2026-09-02"})
zeile("erst bewilligt zaehlt", ok, gemessen=satz)
zeile("gar nichts → eingeschraenkt", not g.zdr_lage({})[0])

print()
print("== die Routen selbst ==")
zeile("drei Routen", len(g.ROUTEN) == 3)
zeile("Grok laeuft NUR auf Abruf",
      [r.auf_abruf for r in g.ROUTEN] == [False, False, True])
zeile("Grok hat das engere Limit",
      g.ROUTEN[2].limit_eur == 5 and g.ROUTEN[0].limit_eur == 10)
zeile("die Limits zusammen bleiben unter Adams Deckel von 30 EUR",
      sum(r.limit_eur for r in g.ROUTEN) <= 30,
      gemessen=str(sum(r.limit_eur for r in g.ROUTEN)))
zeile("gpt-oss-120b ist NICHT eingetragen (Adams Leitplanke)",
      not any("gpt-oss" in r.modell for r in g.ROUTEN),
      gemessen=str([r.modell for r in g.ROUTEN]))

print()
print("== und das Wichtigste: nichts ruft an ==")
quelle = (Path(__file__).resolve().parent.parent / "gegenleser.py").read_text(
    encoding="utf-8")
for verboten in ("requests.", "httpx.", "urlopen", "litellm.completion",
                 "openai.", "anthropic."):
    zeile(f"kein Aufruf ueber [{verboten}]", verboten not in quelle)
zeile("kein Schluessel aus der Umgebung gelesen",
      "API_KEY" not in quelle and "api_key" not in quelle)

print()
if fehler:
    print(f"❌ {len(fehler)} von {n} Zeilen rot:")
    for f in fehler:
        print(f"   · {f}")
    sys.exit(1)
print(f"✅ Alle {n} Zeilen des Gegenleser-Pruefers bestanden")
