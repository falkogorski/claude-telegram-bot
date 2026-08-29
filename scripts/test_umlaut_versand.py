#!/usr/bin/env python3
"""Der Umlaut-Prüfer am Versandpfad — ausgeführt, nicht gelesen.

**Engywucks Auflage C (29.08.):** Adam hat diesen Prüfer viermal verlangt
(28.07., 26.08., 27.08., 28.08. 20:45). Er stand in einer Auftragsfassung, die
noch am selben Abend überholt wurde — ohne die Auflage wäre er still
weggefallen.

Geprüft wird über `postfach_darf_senden`, also über **die Schranke selbst**,
nicht über die Wortliste. Eine Prüfung der Liste allein bliebe grün, wenn
jemand den Aufruf entfernt.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# **Hermetik (Lehre aus dem Abhaengigkeits-Register, Punkt 4).** Die Umgebung
# wird ERZWUNGEN, nicht ergaenzt. Ohne diese Zeilen laeuft der Pruefer nur
# dort, wo zufaellig eine `.env` liegt — im Probelauf-Klon vom 29.08. ist er
# genau daran gescheitert, waehrend er im Hauptbaum gruen war. Ein Pruefer,
# der von einer nicht versionierten Datei abhaengt, misst die Maschine und
# nicht den Code.
import os as _os
_os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
_os.environ["ALLOWED_USER_IDS"] = "4711"

import bot                                                     # noqa: E402

fehler: list[str] = []


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


ZIEL = next(iter(bot.ALLOWED_USER_IDS), 4711) if getattr(bot, "ALLOWED_USER_IDS", None) else 4711


def darf(text: str):
    return bot.postfach_darf_senden({"target_chat_id": ZIEL, "text": text})


print("== Umlaut-Ersatz am Versandpfad ==")

# Die drei Fälle aus dem Befund vom 27.08., wörtlich.
for wort, satz in [
    ("Vorraete", "Die Vorraete sind knapp."),
    ("verfuegbar", "Der Dienst ist wieder verfuegbar."),
    ("Stoerung", "Eine Stoerung wurde behoben."),
]:
    ok, grund = darf(satz)
    zeile(f"[{wort}] wird am Versand gestoppt", not ok, gemessen=f"ok={ok} grund={grund}")
    zeile(f"[{wort}] — die Meldung nennt das Wort", wort.lower() in grund.lower(),
          gemessen=grund)

# **Deutsche Zusammensetzung** — der Fall, den eine Wortgrenze verfehlt hätte.
ok, _ = darf("Die Speichervorraete reichen noch.")
zeile("Zusammensetzung [Speichervorraete] wird gestoppt", not ok)
ok, _ = darf("Eine Systemstoerung liegt vor.")
zeile("Zusammensetzung [Systemstoerung] wird gestoppt", not ok)

# **Die Gegenrichtung, und sie ist die wichtigere.** Ein Prüfer, der zu oft
# anschlägt, wird abgeschaltet — dann ist er schlechter als keiner.
for satz, was in [
    ("Die Vorräte sind knapp.", "richtige Umlaute"),
    ("Der Dienst ist wieder verfügbar.", "richtige Umlaute"),
    ("Die queue ist leer, der value true.", "englische ue-Woerter"),
    ("Ein Status-Update von der Pipeline.", "englischer Fachbegriff"),
    ("Alles in Ordnung, nichts zu melden.", "harmloser Satz"),
    ("Der Commit 8170b3a ist gepusht.", "technischer Satz"),
]:
    ok, grund = darf(satz)
    zeile(f"kein Fehlalarm bei [{was}]", ok, gemessen=grund)

# Die Schranke muss WIRKLICH gerufen werden — Abwesenheit über echte
# Aufrufknoten, nicht über Zeilen mit dem Namen.
import ast as _ast                                             # noqa: E402
_baum = _ast.parse(Path(bot.__file__).read_text(encoding="utf-8"))
_darf = next((k for k in _ast.walk(_baum)
              if isinstance(k, _ast.FunctionDef) and k.name == "postfach_darf_senden"), None)
zeile("postfach_darf_senden existiert", _darf is not None)
_rufe = [k for k in _ast.walk(_darf)
         if isinstance(k, _ast.Call) and isinstance(k.func, _ast.Name)
         and k.func.id == "umlaut_ersatz_gefunden"] if _darf else []
zeile("die Schranke ruft den Umlaut-Pruefer auf", len(_rufe) >= 1,
      gemessen=f"{len(_rufe)} Aufrufknoten")

# Und die Geheimnis-Schranke daneben darf davon nicht berührt sein.
ok, grund = bot.postfach_darf_senden(
    {"target_chat_id": ZIEL, "file": "/home/claudebot/.env", "text": "hier"})
zeile("die Geheimnis-Schranke haelt weiterhin", not ok, gemessen=grund)

print()
if fehler:
    print(f"❌ {len(fehler)} Zeilen rot")
    for f in fehler:
        print(f"   · {f}")
    sys.exit(1)
print("✅ Alle Zeilen des Umlaut-Versandpruefers bestanden")
