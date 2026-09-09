#!/usr/bin/env python3
# <!-- ROLLE: test-zimmer-block1 -->
"""Block 1 des Zimmer-Baus — **der Schluessel trennt wirklich.**

**Adams Bild vom 05.09.:** eine Sitzung je Zimmer. Bis zum 09.09. hingen
Sitzung und Warteschlange an der **Person**; `thread_id` war nur Rueckadresse.

Gemessen wird hier die Trennung selbst — nicht, dass der Code eine `thread_id`
irgendwo hinschreibt, sondern **dass zwei Zimmer zwei Warteschlangen, zwei
Sitzungen und zwei Arbeiter haben** und einander nicht in die Quere kommen.

**Warum ohne laufenden Bot:** Die Trennung ist eine Eigenschaft der
Schluesselbildung. Sie laesst sich an den Traegern messen, ohne Telegram und
ohne Modell — und genau deshalb kann dieser Pruefer im Regressionslauf mit
laufen, statt einmal von Hand gefahren zu werden.
"""
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="zimmer-"))
# **Erzwungen, nicht ergaenzt** — `setdefault` erbte im Zweifel den echten
# Wert und hoebe die Hermetik auf. Der Pruefer der Pruefumgebung hat genau das
# an dieser Datei gefangen, eine Minute nachdem sie entstand.
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot                                                      # noqa: E402

fehler: list[str] = []
zeilen = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global zeilen
    zeilen += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


UID = 4711
print("== Block 1: Sitzung je Zimmer ==")

# ---- Der Schluessel selbst -------------------------------------------------
zeile("derselbe Faden ergibt denselben Schluessel",
      bot.faden(UID, 7) == bot.faden(UID, 7))
zeile("zwei Zimmer sind zwei Schluessel",
      bot.faden(UID, 7) != bot.faden(UID, 8),
      gemessen=f"{bot.faden(UID, 7)} vs {bot.faden(UID, 8)}")
zeile("der Hauptfaden ist ein eigenes Zimmer, nicht dasselbe wie Thema 0",
      bot.faden(UID, None) != bot.faden(UID, 0),
      gemessen=f"{bot.faden(UID, None)} vs {bot.faden(UID, 0)}")
# **Die Kennung als Zeichenkette war die Falle, die im Kopf von `faden()` steht.**
zeile("Kennung als Zeichenkette ergibt KEIN zweites Zimmer",
      bot.faden("4711", 7) == bot.faden(4711, 7),
      gemessen=f"{bot.faden('4711', 7)} vs {bot.faden(4711, 7)}")

# ---- Zwei Warteschlangen ---------------------------------------------------
bot.MAILBOXES.clear()
mb_a = bot._get_mailbox(UID, 7)
mb_b = bot._get_mailbox(UID, 8)
zeile("zwei Zimmer bekommen zwei Warteschlangen", mb_a is not mb_b)
zeile("dasselbe Zimmer bekommt dieselbe zurueck",
      bot._get_mailbox(UID, 7) is mb_a)
mb_a.queue.append("etwas")
zeile("was in einem Zimmer liegt, liegt nicht im anderen",
      len(mb_b.queue) == 0, gemessen=f"B hat {len(mb_b.queue)}")
zeile("der Hauptfaden ist von beiden getrennt",
      bot._get_mailbox(UID) is not mb_a and bot._get_mailbox(UID) is not mb_b)

# ---- Nur-Nachsehen legt kein Zimmer an -------------------------------------
bot.MAILBOXES.clear()
zeile("Nachsehen legt kein Zimmer an (der Waechter zaehlt sonst sein Werk mit)",
      bot._mb_opt(UID, 99) is None and not bot.MAILBOXES,
      gemessen=f"{len(bot.MAILBOXES)} Zimmer nach dem Nachsehen")

# ---- Zwei Sitzungen --------------------------------------------------------
bot.SESSIONS.clear()
bot.SESSIONS[bot.faden(UID, 7)] = "SITZUNG-A"
bot.SESSIONS[bot.faden(UID, 8)] = "SITZUNG-B"
zeile("jedes Zimmer findet seine eigene Sitzung",
      bot._sess(UID, 7) == "SITZUNG-A" and bot._sess(UID, 8) == "SITZUNG-B",
      gemessen=f"{bot._sess(UID, 7)} / {bot._sess(UID, 8)}")
zeile("der Hauptfaden findet KEINE der beiden",
      bot._sess(UID) is None, gemessen=str(bot._sess(UID)))

# ---- Die Gegenrichtung: ein Zimmer schliessen laesst das andere leben ------
bot.SESSIONS.clear()
bot.SESSIONS[bot.faden(UID, 7)] = "A"
bot.SESSIONS[bot.faden(UID, 8)] = "B"
bot.SESSIONS.pop(bot.faden(UID, 7), None)
zeile("ein Zimmer schliessen laesst das andere stehen (Gegenrichtung)",
      bot._sess(UID, 7) is None and bot._sess(UID, 8) == "B")

# ---- Der Job traegt den Faden bis zur Sitzung ------------------------------
# **Die Stelle, an der der Umbau haette scheitern koennen:** Der Job kannte
# `thread_id` laengst — sie kam nur nie beim Schluessel an.
import inspect                                                  # noqa: E402
_quelle = inspect.getsource(bot._run_job)
zeile("der Auftrag holt die Sitzung SEINES Zimmers",
      "ensure_session(user_id, thread_id=job.thread_id)" in _quelle,
      gemessen=[z.strip() for z in _quelle.splitlines()
                if "ensure_session" in z][:1])

# ---- Das Kontingent-Limit gilt der PERSON, nicht dem Zimmer ---------------
# **Ein Regress, den der Schluesselwechsel selbst erzeugt hat** (Engywucks
# Auflage 3): Solange es eine Warteschlange je Person gab, war `pausiert_bis`
# auf ihr richtig. Seit dem 09.09. gibt es eine je Zimmer — vier Zimmer
# haetten dasselbe kontoweite Limit viermal entdeckt.
import time as _t                                               # noqa: E402
bot._LIMIT_PAUSE_BIS.clear()
_bis = _t.time() + 600
bot.limit_pause_setzen(UID, _bis)
zeile("die Pause einer Person gilt fuer JEDES ihrer Zimmer",
      bot.limit_pause_bis(UID) > _t.time(),
      gemessen=f"{bot.limit_pause_bis(UID) - _t.time():.0f}s")
zeile("eine andere Person ist davon nicht betroffen (Gegenrichtung)",
      bot.limit_pause_bis(UID + 1) == 0.0)
# Der spaetere Zeitpunkt gewinnt: Ein zweites Zimmer darf die Pause nicht
# verkuerzen, nur verlaengern.
bot.limit_pause_setzen(UID, _bis - 300)
zeile("ein zweites Zimmer verkuerzt die Pause nicht",
      abs(bot.limit_pause_bis(UID) - _bis) < 1.0,
      gemessen=f"{bot.limit_pause_bis(UID) - _bis:+.0f}s")
bot.limit_pause_setzen(UID, _bis + 300)
zeile("eine spaetere Freigabe verlaengert sie sehr wohl",
      bot.limit_pause_bis(UID) > _bis)
bot.limit_pause_loeschen(UID)
zeile("aufgehoben wird sie fuer alle Zimmer zugleich",
      bot.limit_pause_bis(UID) == 0.0)
# **Und die Entscheidung wird AUSGEFUEHRT, nicht gelesen.**
# Die erste Fassung dieser Zeile suchte einen Namen im Quelltext des Workers —
# und blieb bei der Gegenprobe gruen, weil derselbe Name eine Zeile tiefer
# stehen blieb. Jetzt wird `pause_rest_s` gerufen.
class _MbOhnePause:
    pausiert_bis = 0.0

_mb0 = _MbOhnePause()
bot._LIMIT_PAUSE_BIS.clear()
zeile("ohne Pause wartet niemand",
      bot.pause_rest_s(_mb0, UID) == 0.0)
bot.limit_pause_setzen(UID, _t.time() + 120)
zeile("die Pause der PERSON haelt ein Zimmer an, das selbst keine hat",
      bot.pause_rest_s(_mb0, UID) > 60,
      gemessen=f"{bot.pause_rest_s(_mb0, UID):.0f}s")
zeile("ein Zimmer einer ANDEREN Person laeuft weiter (Gegenrichtung)",
      bot.pause_rest_s(_mb0, UID + 1) == 0.0)
bot.limit_pause_loeschen(UID)

# ---- Nachsteuern ohne Stoppen (Auftrag 8) ---------------------------------
# **Adam am 05.09.:** *optimieren, ergaenzen, zuruecknehmen, ohne zu stoppen.*
# Das Stoppen gibt es laengst; der sanfte Weg fehlte. Gemessen wird der HOOK
# selbst — aufgerufen, nicht im Quelltext gesucht.
import asyncio as _a                                            # noqa: E402

_hook = bot._nachsteuer_hook(UID, 7)
zeile("ohne Zettel reicht der Hook nichts hinein",
      _a.run(_hook({}, None, None)) == {},
      gemessen=str(_a.run(_hook({}, None, None)))[:80])

_ord = bot.nachsteuer_ordner(UID, 7)
_ord.mkdir(parents=True, exist_ok=True)
(_ord / "001.txt").write_text("stopp, andere Farbe", encoding="utf-8")
_erg = _a.run(_hook({}, None, None))
_kontext = (_erg.get("hookSpecificOutput") or {}).get("additionalContext", "")
zeile("ein Zettel kommt an der naechsten Werkzeuggrenze an",
      "andere Farbe" in _kontext, gemessen=_kontext[:80])
zeile("und er ist als Adams Nachsteuerung kenntlich",
      "nachgesteuert" in _kontext.lower(), gemessen=_kontext[:60])

# **Verbraucht, nicht nur gelesen** — sonst haette das Modell denselben
# Nachtrag nach zehn Werkzeugaufrufen zehnmal im Kontext.
zeile("derselbe Zettel kommt kein zweites Mal",
      _a.run(_hook({}, None, None)) == {})

# **Und er landet im richtigen Zimmer.**
(bot.nachsteuer_ordner(UID, 8)).mkdir(parents=True, exist_ok=True)
(bot.nachsteuer_ordner(UID, 8) / "001.txt").write_text("fuer Zimmer acht", encoding="utf-8")
_hook7 = bot._nachsteuer_hook(UID, 7)
zeile("ein Zettel fuer Zimmer 8 erreicht Zimmer 7 nicht (Gegenrichtung)",
      _a.run(_hook7({}, None, None)) == {})
_hook8 = bot._nachsteuer_hook(UID, 8)
_k8 = (_a.run(_hook8({}, None, None)).get("hookSpecificOutput") or {}).get("additionalContext", "")
zeile("Zimmer 8 bekommt seinen eigenen",
      "Zimmer acht" in _k8, gemessen=_k8[:60])

# **Der Hook haengt wirklich an den Optionen** — sonst waere er eine Funktion,
# die niemand ruft. Gemessen am fertigen Optionen-Objekt, nicht am Quelltext.
_opt = bot.hauptsitzungs_optionen(user_id=UID, model_full="x", effort=None,
                                  add_dirs=[], context="", context_via_file=False,
                                  thread_id=7)
zeile("die Sitzung eines Zimmers traegt den Nachsteuer-Hook",
      bool((getattr(_opt, "hooks", None) or {}).get("PreToolUse")),
      gemessen=str(getattr(_opt, "hooks", None))[:80])

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen von Block 1 bestanden.")
