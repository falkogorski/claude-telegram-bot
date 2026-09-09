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

# **[GEAENDERT 09.09.2026, Block 1b]** Gemessen wird jetzt der ECHTE Weg:
# schreiben mit der Kennung des laufenden Auftrags, lesen durch den Hook.
# Vorher legte der Pruefer eine Datei "001.txt" von Hand ab -- damit war die
# Filterung nach Auftrag nicht messbar, weil es gar keine gab.
def _job(mid: int, wann: int = 1000):
    return bot.QueuedJob(update=None, text=f"Auftrag {mid}", user_id=UID,
                         chat_id=999, message_id=mid, received_at=wann)

_mb7 = bot._get_mailbox(UID, 7)
_j7 = _job(101)
_mb7.current_job = _j7
_k7_kennung = bot._auftrag_kennung(_j7)

_hook = bot._nachsteuer_hook(UID, 7)
zeile("ohne Zettel reicht der Hook nichts hinein",
      _a.run(_hook({}, None, None)) == {},
      gemessen=str(_a.run(_hook({}, None, None)))[:80])

zeile("der Schreiber legt einen Zettel fuer den laufenden Auftrag ab",
      bot.nachsteuer_schreiben(UID, 7, _k7_kennung, 501, "stopp, andere Farbe"),
      gemessen=str(sorted(x.name for x in bot.nachsteuer_ordner(UID, 7).glob("*.txt"))))

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
_mb8 = bot._get_mailbox(UID, 8)
_j8 = _job(108)
_mb8.current_job = _j8
bot.nachsteuer_schreiben(UID, 8, bot._auftrag_kennung(_j8), 508, "fuer Zimmer acht")
_hook7 = bot._nachsteuer_hook(UID, 7)
zeile("ein Zettel fuer Zimmer 8 erreicht Zimmer 7 nicht (Gegenrichtung)",
      _a.run(_hook7({}, None, None)) == {})
_hook8 = bot._nachsteuer_hook(UID, 8)
_k8 = (_a.run(_hook8({}, None, None)).get("hookSpecificOutput") or {}).get("additionalContext", "")
zeile("Zimmer 8 bekommt seinen eigenen",
      "Zimmer acht" in _k8, gemessen=_k8[:60])

# ---- Block 1b: nichts Altes, nichts Doppeltes, nichts Verlorenes ----------
#
# Drei feste Bedingungen aus Engywucks Nachpruefung. Jede einzeln gemessen.

# (a) NICHTS ALTES: ein Zettel, der es nicht mehr in seinen Auftrag geschafft
#     hat, darf den naechsten nicht erreichen -- der bearbeitet etwas anderes.
bot.nachsteuer_schreiben(UID, 7, _k7_kennung, 502, "gehoert zum alten Auftrag")
_mb7.current_job = _job(102, 2000)                       # neuer Auftrag im selben Zimmer
_neu = _a.run(bot._nachsteuer_hook(UID, 7)({}, None, None))
zeile("ein Zettel aus einem fremden Auftrag kommt NICHT an",
      _neu == {}, gemessen=str(_neu)[:60])

# (b) und beim Auftragsende ist der Rest wirklich weg (nicht bloss ungelesen).
bot.nachsteuer_aufraeumen(UID, 7, _k7_kennung, beantwortet=False)
zeile("Auftragsende wirft die Reste weg",
      not list(bot.nachsteuer_ordner(UID, 7).glob(f"{_k7_kennung}__*.txt")),
      gemessen=str(sorted(x.name for x in bot.nachsteuer_ordner(UID, 7).glob("*.txt"))))

# (c) NICHTS DOPPELT: Zettel angekommen UND Auftrag beantwortet -> der
#     eingereihte Zwilling braucht keinen eigenen Lauf.
_mbz = bot._get_mailbox(UID, 11)
_jz = _job(111)
_mbz.current_job = _jz
_kz = bot._auftrag_kennung(_jz)
bot.nachsteuer_schreiben(UID, 11, _kz, 511, "Nachtrag zum laufenden")
_a.run(bot._nachsteuer_hook(UID, 11)({}, None, None))     # der Hook reicht ihn hinein
bot.nachsteuer_aufraeumen(UID, 11, _kz, beantwortet=True)
zeile("angekommen und beantwortet -> der Zwilling wird uebersprungen",
      bot.zettel_erledigt(511), gemessen=str(bot._ZETTEL.get(511)))

# (d) NICHTS VERLOREN: derselbe Weg, aber der Auftrag scheitert -> der
#     Zwilling laeuft ganz normal. Im Zweifel lieber einmal zu viel arbeiten.
_mbf = bot._get_mailbox(UID, 12)
_jf = _job(112)
_mbf.current_job = _jf
_kf = bot._auftrag_kennung(_jf)
bot.nachsteuer_schreiben(UID, 12, _kf, 512, "Nachtrag zum gescheiterten")
_a.run(bot._nachsteuer_hook(UID, 12)({}, None, None))
bot.nachsteuer_aufraeumen(UID, 12, _kf, beantwortet=False)
zeile("angekommen, aber Auftrag gescheitert -> der Zwilling laeuft normal",
      not bot.zettel_erledigt(512), gemessen=str(bot._ZETTEL.get(512)))

# (e) und ein Zettel, den niemand gelesen hat, macht den Zwilling ebenfalls
#     nicht ueberfluessig.
_mbu = bot._get_mailbox(UID, 13)
_ju = _job(113)
_mbu.current_job = _ju
bot.nachsteuer_schreiben(UID, 13, bot._auftrag_kennung(_ju), 513, "nie gelesen")
bot.nachsteuer_aufraeumen(UID, 13, bot._auftrag_kennung(_ju), beantwortet=True)
zeile("nie gelesen -> der Zwilling laeuft normal",
      not bot.zettel_erledigt(513), gemessen=str(bot._ZETTEL.get(513)))

# **Der Hook haengt wirklich an den Optionen** — sonst waere er eine Funktion,
# die niemand ruft. Gemessen am fertigen Optionen-Objekt, nicht am Quelltext.
_opt = bot.hauptsitzungs_optionen(user_id=UID, model_full="x", effort=None,
                                  add_dirs=[], context="", context_via_file=False,
                                  thread_id=7)
zeile("die Sitzung eines Zimmers traegt den Nachsteuer-Hook",
      bool((getattr(_opt, "hooks", None) or {}).get("PreToolUse")),
      gemessen=str(getattr(_opt, "hooks", None))[:80])

# ---- Block 1b: die Wege, nicht nur die Traeger ----------------------------
#
# Engywucks Befund: Die Pruefzeilen von Block 1 massen die TRAEGER (Schluessel,
# Schlangen, Sitzungen) -- und die stimmten. Sie massen nicht die WEGE, die
# ueber die Traeger laufen. Diese zwei Zeilen messen je einen Weg.

# (1) Der Freigabe-Rueckruf gehoert dem Zimmer, das gefragt hat.
#     Vorher war er nur an die Person gebunden: In einem Zimmer OHNE
#     Hauptfaden-Sitzung verweigerte er jedes Werkzeug ("no active session").
bot.SESSIONS.pop(bot.faden(UID), None)                  # kein Hauptfaden offen
_s22 = bot.UserSession(client=None, chat_id=999)
_s22.bot = object()
bot.SESSIONS[bot.faden(UID, 22)] = _s22

_cb_haupt = bot.make_permission_callback(UID)
_erg_haupt = _a.run(_cb_haupt("Read", {}, None))
zeile("ohne Sitzung verweigert der Rueckruf im Hauptfaden (Gegenrichtung)",
      "no active session" in str(getattr(_erg_haupt, "message", "")),
      gemessen=str(getattr(_erg_haupt, "message", ""))[:60])

_cb22 = bot.make_permission_callback(UID, 22)
_erg22 = _a.run(_cb22("Read", {}, None))
zeile("ein Zimmer mit eigener Sitzung bekommt seine Freigabe",
      "no active session" not in str(getattr(_erg22, "message", "")),
      gemessen=type(_erg22).__name__ + ": " + str(getattr(_erg22, "message", ""))[:50])

# (2) Ein nach dem Neustart nachgeholter Auftrag gehoert in SEIN Zimmer.
#     `thread_id` stand im Datensatz und ging beim Einreihen verloren.
import pending                                                   # noqa: E402

_key21 = pending.make_key(999, 21)
pending.record(_key21, {"text": "Frage aus Zimmer 21", "status": pending.STATUS_OPEN,
                        "user_id": UID, "chat_id": 999, "message_id": 21,
                        "thread_id": 21})


class _AppAttrappe:
    bot = None


bot._reconcile_pending(_AppAttrappe())
zeile("ein nachgeholter Auftrag landet in SEINEM Zimmer",
      any(j.thread_id == 21 for j in bot._get_mailbox(UID, 21).queue),
      gemessen=str([(j.thread_id, j.text[:20]) for j in bot._get_mailbox(UID, 21).queue]))
zeile("und nicht im Hauptfaden (Gegenrichtung)",
      not any(j.text.startswith("Frage aus Zimmer 21")
              for j in bot._get_mailbox(UID).queue),
      gemessen=str([j.text[:20] for j in bot._get_mailbox(UID).queue]))

# ---- Block 1b: die MENGE, nicht die Liste ---------------------------------
#
# **Engywucks Auflage nach der Nachpruefung von Block 1.** Er fand sechs
# Stellen, an denen der Faden im Umfeld bereitlag und nicht uebergeben wurde --
# und benannte den Grund: Die Ersetzung von `SESSIONS.get(user_id)` war
# mechanisch, `_sess(user_id)` OHNE zweites Argument ist der Hauptfaden. Das
# faellt nicht auf, weil es niemand meldet.
#
# Diese Zeile zaehlt darum ALLE Aufrufe der Tueren mit nur einem Argument und
# verlangt an jeder ein `# Hauptfaden:` mit Grund. Dann ist jede verbleibende
# Stelle eine ENTSCHEIDUNG statt einer Vergessenheit -- und Stelle Nummer
# sieben faellt beim Bauen auf, nicht erst in einer Nachpruefung.
#
# **Warum das hier Quelltext liest und trotzdem taugt:** Gemessen wird die
# ABWESENHEIT eines Arguments ueber echte Aufrufknoten (`ast.Call`), nicht das
# Vorkommen eines Namens im Text. Das ist die zweite der beiden Formen, die
# Engywuck am 22.08. als tragfaehig benannt hat.
import ast as _ast                                              # noqa: E402

_TUEREN = {"_sess", "_mb_opt", "_get_mailbox", "_ensure_worker",
           "close_session", "ensure_session", "make_permission_callback"}
_quelle = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
_zeilen = _quelle.split(chr(10))     # NICHT splitlines(): bot.py enthaelt
                                     # U+2028/U+2029, die dort mitteilen wuerden
                                     # und alle Zeilennummern verschoeben.
_ohne_grund = []
for _kn in _ast.walk(_ast.parse(_quelle)):
    if not (isinstance(_kn, _ast.Call) and isinstance(_kn.func, _ast.Name)
            and _kn.func.id in _TUEREN):
        continue
    if len(_kn.args) + len(_kn.keywords) > 1:
        continue
    _umfeld = chr(10).join(_zeilen[max(0, _kn.lineno - 4):_kn.lineno])
    if "# Hauptfaden:" not in _umfeld:
        _ohne_grund.append(f"{_kn.func.id}:{_kn.lineno}")

zeile("jede Ein-Argument-Tuer ist als Hauptfaden BEGRUENDET",
      not _ohne_grund,
      gemessen=(", ".join(_ohne_grund) if _ohne_grund
                else "alle begruendet"))

# Und die Gegenrichtung: Der Zaehler findet ueberhaupt etwas. Eine Pruefzeile,
# die ueber einer leeren Menge laeuft, ist immer gruen und misst nichts.
_alle_tueren = sum(1 for _kn in _ast.walk(_ast.parse(_quelle))
                   if isinstance(_kn, _ast.Call) and isinstance(_kn.func, _ast.Name)
                   and _kn.func.id in _TUEREN)
zeile("der Zaehler sieht die Tueren ueberhaupt",
      _alle_tueren >= 40, gemessen=f"{_alle_tueren} Aufrufe")

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen von Block 1 bestanden.")
