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
import asyncio
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

# Der Chat des Pruefstands (F-22: der Schluessel traegt ihn).
CHAT_PRUEF = 999


def F(person, thema=None, chat=None):
    """Ein Faden fuer den Pruefstand — `chat` faellt auf `CHAT_PRUEF` zurueck.

    **[NEU 11.09.2026, F-22]** Der Schluessel traegt jetzt drei Teile. Ein
    Helfer statt 44 einzelner Aufrufe: Wer den Chat wechseln will, uebergibt
    ihn; wer nur ein Zimmer meint, schreibt weiter zwei Zahlen.
    """
    return bot.faden(person, CHAT_PRUEF if chat is None else chat, thema)


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
# Der Chat des Pruefstands — seit F-22 Teil 1 gehoert er in jeden
# Registerschluessel: `message_id` ist nur JE CHAT eindeutig.
CHAT = 999
print("== Block 1: Sitzung je Zimmer ==")

# ---- Der Schluessel selbst -------------------------------------------------
zeile("derselbe Faden ergibt denselben Schlüssel",
      F(UID, 7) == F(UID, 7))
zeile("zwei Zimmer sind zwei Schlüssel",
      F(UID, 7) != F(UID, 8),
      gemessen=f"{F(UID, 7)} vs {F(UID, 8)}")
zeile("der Hauptfaden ist ein eigenes Zimmer, nicht dasselbe wie Thema 0",
      F(UID, None) != F(UID, 0),
      gemessen=f"{F(UID, None)} vs {F(UID, 0)}")
# **Die Kennung als Zeichenkette war die Falle, die im Kopf von `faden()` steht.**
zeile("Kennung als Zeichenkette ergibt KEIN zweites Zimmer",
      F("4711", 7) == F(4711, 7),
      gemessen=f"{F('4711', 7)} vs {F(4711, 7)}")

# ---- Zwei Warteschlangen ---------------------------------------------------
bot.MAILBOXES.clear()
mb_a = bot._get_mailbox(F(UID, 7))
mb_b = bot._get_mailbox(F(UID, 8))
zeile("zwei Zimmer bekommen zwei Warteschlangen", mb_a is not mb_b)
zeile("dasselbe Zimmer bekommt dieselbe zurück",
      bot._get_mailbox(F(UID, 7)) is mb_a)
mb_a.queue.append("etwas")
zeile("was in einem Zimmer liegt, liegt nicht im anderen",
      len(mb_b.queue) == 0, gemessen=f"B hat {len(mb_b.queue)}")
zeile("der Hauptfaden ist von beiden getrennt",
      bot._get_mailbox(F(UID)) is not mb_a and bot._get_mailbox(F(UID)) is not mb_b)

# ---- Nur-Nachsehen legt kein Zimmer an -------------------------------------
bot.MAILBOXES.clear()
zeile("Nachsehen legt kein Zimmer an (der Wächter zählt sonst sein Werk mit)",
      bot._mb_opt(F(UID, 99)) is None and not bot.MAILBOXES,
      gemessen=f"{len(bot.MAILBOXES)} Zimmer nach dem Nachsehen")

# ---- Zwei Sitzungen --------------------------------------------------------
bot.SESSIONS.clear()
bot.SESSIONS[F(UID, 7)] = "SITZUNG-A"
bot.SESSIONS[F(UID, 8)] = "SITZUNG-B"
zeile("jedes Zimmer findet seine eigene Sitzung",
      bot._sess(F(UID, 7)) == "SITZUNG-A" and bot._sess(F(UID, 8)) == "SITZUNG-B",
      gemessen=f"{bot._sess(F(UID, 7))} / {bot._sess(F(UID, 8))}")
zeile("der Hauptfaden findet KEINE der beiden",
      bot._sess(F(UID)) is None, gemessen=str(bot._sess(F(UID))))

# ---- Die Gegenrichtung: ein Zimmer schliessen laesst das andere leben ------
bot.SESSIONS.clear()
bot.SESSIONS[F(UID, 7)] = "A"
bot.SESSIONS[F(UID, 8)] = "B"
bot.SESSIONS.pop(F(UID, 7), None)
zeile("ein Zimmer schließen lässt das andere stehen (Gegenrichtung)",
      bot._sess(F(UID, 7)) is None and bot._sess(F(UID, 8)) == "B")

# ---- Der Job traegt den Faden bis zur Sitzung ------------------------------
# **Die Stelle, an der der Umbau haette scheitern koennen:** Der Job kannte
# `thread_id` laengst — sie kam nur nie beim Schluessel an.
import inspect                                                  # noqa: E402
_quelle = inspect.getsource(bot._run_job)
zeile("der Auftrag holt die Sitzung SEINES Zimmers",
      "ensure_session(faden_von_job(job))" in _quelle,
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
zeile("die Pause einer Person gilt für JEDES ihrer Zimmer",
      bot.limit_pause_bis(UID) > _t.time(),
      gemessen=f"{bot.limit_pause_bis(UID) - _t.time():.0f}s")
zeile("eine andere Person ist davon nicht betroffen (Gegenrichtung)",
      bot.limit_pause_bis(UID + 1) == 0.0)
# Der spaetere Zeitpunkt gewinnt: Ein zweites Zimmer darf die Pause nicht
# verkuerzen, nur verlaengern.
bot.limit_pause_setzen(UID, _bis - 300)
zeile("ein zweites Zimmer verkürzt die Pause nicht",
      abs(bot.limit_pause_bis(UID) - _bis) < 1.0,
      gemessen=f"{bot.limit_pause_bis(UID) - _bis:+.0f}s")
bot.limit_pause_setzen(UID, _bis + 300)
zeile("eine spätere Freigabe verlängert sie sehr wohl",
      bot.limit_pause_bis(UID) > _bis)
bot.limit_pause_loeschen(UID)
zeile("aufgehoben wird sie für alle Zimmer zugleich",
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
zeile("die Pause der PERSON hält ein Zimmer an, das selbst keine hat",
      bot.pause_rest_s(_mb0, UID) > 60,
      gemessen=f"{bot.pause_rest_s(_mb0, UID):.0f}s")
zeile("ein Zimmer einer ANDEREN Person läuft weiter (Gegenrichtung)",
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

_mb7 = bot._get_mailbox(F(UID, 7))
_j7 = _job(101)
_mb7.current_job = _j7
_k7_kennung = bot._auftrag_kennung(_j7)

_hook = bot._nachsteuer_hook(F(UID, 7))
zeile("ohne Zettel reicht der Hook nichts hinein",
      _a.run(_hook({}, None, None)) == {},
      gemessen=str(_a.run(_hook({}, None, None)))[:80])

zeile("der Schreiber legt einen Zettel für den laufenden Auftrag ab",
      bot.nachsteuer_schreiben(F(UID, 7), _k7_kennung, (CHAT, 501), "stopp, andere Farbe"),
      gemessen=str(sorted(x.name for x in bot.nachsteuer_ordner(F(UID, 7)).glob("*.txt"))))

_erg = _a.run(_hook({}, None, None))
_kontext = (_erg.get("hookSpecificOutput") or {}).get("additionalContext", "")
zeile("ein Zettel kommt an der nächsten Werkzeuggrenze an",
      "andere Farbe" in _kontext, gemessen=_kontext[:80])
zeile("und er ist als Adams Nachsteuerung kenntlich",
      "nachgesteuert" in _kontext.lower(), gemessen=_kontext[:60])

# **Verbraucht, nicht nur gelesen** — sonst haette das Modell denselben
# Nachtrag nach zehn Werkzeugaufrufen zehnmal im Kontext.
zeile("derselbe Zettel kommt kein zweites Mal",
      _a.run(_hook({}, None, None)) == {})

# **Und er landet im richtigen Zimmer.**
_mb8 = bot._get_mailbox(F(UID, 8))
_j8 = _job(108)
_mb8.current_job = _j8
bot.nachsteuer_schreiben(F(UID, 8), bot._auftrag_kennung(_j8), (CHAT, 508), "fuer Zimmer acht")
_hook7 = bot._nachsteuer_hook(F(UID, 7))
zeile("ein Zettel für Zimmer 8 erreicht Zimmer 7 nicht (Gegenrichtung)",
      _a.run(_hook7({}, None, None)) == {})
_hook8 = bot._nachsteuer_hook(F(UID, 8))
_k8 = (_a.run(_hook8({}, None, None)).get("hookSpecificOutput") or {}).get("additionalContext", "")
zeile("Zimmer 8 bekommt seinen eigenen",
      "Zimmer acht" in _k8, gemessen=_k8[:60])

# ---- Block 1b: nichts Altes, nichts Doppeltes, nichts Verlorenes ----------
#
# Drei feste Bedingungen aus Engywucks Nachpruefung. Jede einzeln gemessen.

# (a) NICHTS ALTES: ein Zettel, der es nicht mehr in seinen Auftrag geschafft
#     hat, darf den naechsten nicht erreichen -- der bearbeitet etwas anderes.
bot.nachsteuer_schreiben(F(UID, 7), _k7_kennung, (CHAT, 502), "gehoert zum alten Auftrag")
_mb7.current_job = _job(102, 2000)                       # neuer Auftrag im selben Zimmer
_neu = _a.run(bot._nachsteuer_hook(F(UID, 7))({}, None, None))
zeile("ein Zettel aus einem fremden Auftrag kommt NICHT an",
      _neu == {}, gemessen=str(_neu)[:60])

# (b) und beim Auftragsende ist der Rest wirklich weg (nicht bloss ungelesen).
bot.nachsteuer_aufraeumen(F(UID, 7), _k7_kennung, beantwortet=False)
zeile("Auftragsende wirft die Reste weg",
      not list(bot.nachsteuer_ordner(F(UID, 7)).glob(f"{_k7_kennung}__*.txt")),
      gemessen=str(sorted(x.name for x in bot.nachsteuer_ordner(F(UID, 7)).glob("*.txt"))))

# (c) NICHTS DOPPELT: Zettel angekommen UND Auftrag beantwortet -> der
#     eingereihte Zwilling braucht keinen eigenen Lauf.
_mbz = bot._get_mailbox(F(UID, 11))
_jz = _job(111)
_mbz.current_job = _jz
_kz = bot._auftrag_kennung(_jz)
bot.nachsteuer_schreiben(F(UID, 11), _kz, (CHAT, 511), "Nachtrag zum laufenden")
_a.run(bot._nachsteuer_hook(F(UID, 11))({}, None, None))     # der Hook reicht ihn hinein
bot.nachsteuer_aufraeumen(F(UID, 11), _kz, beantwortet=True)
zeile("angekommen und beantwortet -> der Zwilling wird übersprungen",
      bot.zettel_erledigt((CHAT, 511)), gemessen=str(bot._ZETTEL.get((CHAT, 511))))

# (d) NICHTS VERLOREN: derselbe Weg, aber der Auftrag scheitert -> der
#     Zwilling laeuft ganz normal. Im Zweifel lieber einmal zu viel arbeiten.
_mbf = bot._get_mailbox(F(UID, 12))
_jf = _job(112)
_mbf.current_job = _jf
_kf = bot._auftrag_kennung(_jf)
bot.nachsteuer_schreiben(F(UID, 12), _kf, (CHAT, 512), "Nachtrag zum gescheiterten")
_a.run(bot._nachsteuer_hook(F(UID, 12))({}, None, None))
bot.nachsteuer_aufraeumen(F(UID, 12), _kf, beantwortet=False)
zeile("angekommen, aber Auftrag gescheitert -> der Zwilling läuft normal",
      not bot.zettel_erledigt(512), gemessen=str(bot._ZETTEL.get(512)))

# (e) und ein Zettel, den niemand gelesen hat, macht den Zwilling ebenfalls
#     nicht ueberfluessig.
_mbu = bot._get_mailbox(F(UID, 13))
_ju = _job(113)
_mbu.current_job = _ju
bot.nachsteuer_schreiben(F(UID, 13), bot._auftrag_kennung(_ju), (CHAT, 513), "nie gelesen")
bot.nachsteuer_aufraeumen(F(UID, 13), bot._auftrag_kennung(_ju), beantwortet=True)
zeile("nie gelesen -> der Zwilling läuft normal",
      not bot.zettel_erledigt(513), gemessen=str(bot._ZETTEL.get(513)))

# **Der Hook haengt wirklich an den Optionen** — sonst waere er eine Funktion,
# die niemand ruft. Gemessen am fertigen Optionen-Objekt, nicht am Quelltext.
_opt = bot.hauptsitzungs_optionen(fd=F(UID, 7), model_full="x", effort=None,
                                  add_dirs=[], context="", context_via_file=False,
                                  )
# **[VERSCHÄRFT 10.09.2026, Ultracode-Befund E2] `bool(...)` misst, dass
# IRGENDEIN Hook dasteht.** Im Probelauf wurde der Nachsteuer-Hook durch eine
# Attrappe ersetzt — die Zeile blieb grün, und die halbe Zusage von Auftrag 8
# war unbewacht.
#
# Jetzt wird der Hook **ausgeführt**: Ein Zettel wird abgelegt, der Hook
# gerufen, und gemessen, dass genau dieser Text im Kontext ankommt. Eine
# Attrappe an seiner Stelle liefert das nicht.
_hooks = (getattr(_opt, "hooks", None) or {}).get("PreToolUse") or []
zeile("die Sitzung eines Zimmers trägt einen PreToolUse-Hook",
      bool(_hooks), gemessen=str(getattr(_opt, "hooks", None))[:80])

_haken = None
for _m in _hooks:
    for _h in (getattr(_m, "hooks", None) or []):
        _haken = _h
        break
# **Die Kennung kommt aus dem laufenden Auftrag, nicht aus der Luft:** Der
# Hook liest nur Zettel SEINES Auftrags -- das ist der Sinn der Kennung
# (ein Nachtrag aus fremdem Zusammenhang ist schlimmer als keiner).
_mb_e2 = bot._get_mailbox(F(UID, 7))
_mb_e2.current_job = bot.QueuedJob(update=None, text="laeuft", user_id=UID,
                                   message_id=4241, received_at=1000)
bot.nachsteuer_schreiben(F(UID, 7), bot._auftrag_kennung(_mb_e2.current_job),
                         4242, "Nachtrag aus E2")
# **Ein Bruch macht diese Zeile rot, er stuerzt den Pruefer nicht ab** --
# eine Attrappe an der Hook-Stelle kann jede Form haben, auch eine, die
# `asyncio.run` gar nicht annimmt. Ein abstuerzender Pruefer verdeckt alles
# darunter (Lehre vom Block-2-Pruefer am 09.09.).
try:
    _erg_e2 = asyncio.run(_haken({}, None, None)) if _haken else {}
except Exception as _ex_e2:
    _erg_e2 = {"_fehler": str(_ex_e2)}
_kontext_e2 = str(((_erg_e2 or {}).get("hookSpecificOutput") or {})
                  .get("additionalContext", "")) or str(_erg_e2.get("_fehler", ""))
zeile("und es ist WIRKLICH der Nachsteuer-Hook, keine Attrappe",
      "Nachtrag aus E2" in _kontext_e2, gemessen=_kontext_e2[:120] or "leer")
_mb_e2.current_job = None

# ---- Block 1b: die Wege, nicht nur die Traeger ----------------------------
#
# Engywucks Befund: Die Pruefzeilen von Block 1 massen die TRAEGER (Schluessel,
# Schlangen, Sitzungen) -- und die stimmten. Sie massen nicht die WEGE, die
# ueber die Traeger laufen. Diese zwei Zeilen messen je einen Weg.

# (1) Der Freigabe-Rueckruf gehoert dem Zimmer, das gefragt hat.
#     Vorher war er nur an die Person gebunden: In einem Zimmer OHNE
#     Hauptfaden-Sitzung verweigerte er jedes Werkzeug ("no active session").
bot.SESSIONS.pop(F(UID), None)                  # kein Hauptfaden offen
_s22 = bot.UserSession(client=None, chat_id=999)
_s22.bot = object()
bot.SESSIONS[F(UID, 22)] = _s22

_cb_haupt = bot.make_permission_callback(F(UID))
_erg_haupt = _a.run(_cb_haupt("Read", {}, None))
zeile("ohne Sitzung verweigert der Rückruf im Hauptfaden (Gegenrichtung)",
      "no active session" in str(getattr(_erg_haupt, "message", "")),
      gemessen=str(getattr(_erg_haupt, "message", ""))[:60])

_cb22 = bot.make_permission_callback(F(UID, 22))
_erg22 = _a.run(_cb22("Read", {}, None))
# **[VERSCHAERFT 10.09.2026, Claudias Befund]** Hier stand
# `"no active session" not in message` -- zu schwach, denn das misst **eine
# bestimmte Ablehnung**, nicht die Erlaubnis. Jetzt wird auf ERLAUBT geprueft.
#
# **Ihre Begruendung trifft allerdings nicht, und das ist nachgemessen:** Sie
# vermutete, ein `NameError` im Sendepfad haette diese Zeile gruen gelassen.
# Der Zustand von gestern Nacht wurde nachgestellt (Import weg, Buchfuehrung
# zurueck in die Sende-Klammer) -- die Zeile blieb **auch mit der
# Verschaerfung** gruen. Der Grund liegt tiefer: `Read` ist ein Lesewerkzeug
# und wird ohne Dialog erlaubt, der defekte Sendepfad wird hier also gar nicht
# betreten. **Eine schaerfere Bedingung macht aus einer Zeile, die den Pfad
# nicht beruehrt, keine, die ihn prueft.**
#
# Den Fall faengt `scripts/test_freigabeweg.py` -- dort wird ein `Write`
# gefragt, und das geht wirklich durch den Dialog.
zeile("ein Zimmer mit eigener Sitzung bekommt seine Freigabe",
      type(_erg22).__name__ == "PermissionResultAllow",
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
      any(j.thread_id == 21 for j in bot._get_mailbox(F(UID, 21)).queue),
      gemessen=str([(j.thread_id, j.text[:20]) for j in bot._get_mailbox(F(UID, 21)).queue]))
zeile("und nicht im Hauptfaden (Gegenrichtung)",
      not any(j.text.startswith("Frage aus Zimmer 21")
              for j in bot._get_mailbox(F(UID)).queue),
      gemessen=str([j.text[:20] for j in bot._get_mailbox(F(UID)).queue]))

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
           "close_session", "ensure_session", "make_permission_callback",
           "nachsteuer_ordner", "_session_worker"}
_quelle = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
_baum = _ast.parse(_quelle)

# ── F-22 voll: derselbe Faden-Wert aus ZWEI Chats ───────────────────────────
#
# **Die Zusage des Zimmer-Baus, jetzt vollständig.** Bis zum 11.09. fielen
# Privatchat, der General-Bereich einer Forum-Gruppe und jede normale Gruppe
# auf **denselben** Schlüssel: eine Sitzung, ein Protokoll, eine
# Warteschlange für drei verschiedene Orte.
zeile("zwei Chats derselben Person sind ZWEI Zimmer",
      F(UID, None, chat=111) != F(UID, None, chat=222),
      gemessen=f"{F(UID, None, chat=111)} vs {F(UID, None, chat=222)}")
zeile("dasselbe Thema in zwei Chats ist NICHT dasselbe Zimmer",
      F(UID, 7, chat=111) != F(UID, 7, chat=222))
zeile("und derselbe Ort bleibt dasselbe Zimmer (Gegenrichtung)",
      F(UID, 7, chat=111) == F(UID, 7, chat=111))

# Die Teile heißen, statt gezählt zu werden — ein viertes Feld würde sonst
# jede Index-Stelle still verschieben.
_f22 = F(UID, 7, chat=111)
zeile("der Faden nennt seine Teile beim Namen",
      (_f22.person, _f22.chat, _f22.thema) == (UID, 111, 7),
      gemessen=str(_f22))

# Und die Wirkung: getrennte Warteschlangen.
bot.MAILBOXES.clear()
bot._get_mailbox(F(UID, None, chat=111)).queue.append("A")
bot._get_mailbox(F(UID, None, chat=222)).queue.append("B")
zeile("was im einen Chat liegt, liegt nicht im anderen",
      list(bot._get_mailbox(F(UID, None, chat=111)).queue) == ["A"]
      and list(bot._get_mailbox(F(UID, None, chat=222)).queue) == ["B"])
bot.MAILBOXES.clear()

# Auch der Nachsteuer-Ordner trennt die Chats.
zeile("der Zettel-Ordner trennt die Chats",
      bot.nachsteuer_ordner(F(UID, None, chat=111))
      != bot.nachsteuer_ordner(F(UID, None, chat=222)),
      gemessen=bot.nachsteuer_ordner(F(UID, None, chat=111)).name)

# **[UMGESTELLT 11.09.2026, F-22] Die Zusage hat sich geändert, also misst die
# Zeile etwas anderes.**
#
# Bis gestern hieß sie „kein Ein-Argument-Aufruf" — damals waren Person und
# Thema zwei Zahlen, und ein fehlendes zweites Argument bedeutete: Faden
# vergessen. **Jetzt ist ein Argument die richtige Form**, denn der Faden ist
# ein Wert. Die alte Zeile hätte ab hier jeden Aufruf angeschwärzt.
#
# Gemessen wird deshalb die **Bauform selbst**: Keine dieser Türen darf noch
# einen `thread_id`- oder `user_id`-Parameter tragen. Solange das gilt, kann
# keine Aufrufstelle den Chat vergessen — nicht weil jemand daran denkt,
# sondern weil es keinen Weg gibt, ihn wegzulassen.
_mit_alten_teilen = []
for _fn in _ast.walk(_baum):
    if not isinstance(_fn, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
        continue
    if _fn.name not in _TUEREN:
        continue
    _namen = {a.arg for a in _fn.args.args} | {a.arg for a in _fn.args.kwonlyargs}
    if {"thread_id", "user_id"} & _namen:
        _mit_alten_teilen.append(f"{_fn.name}({', '.join(sorted(_namen))})")
zeile("keine Tür nimmt Person und Thema einzeln — der Faden ist EIN Wert",
      not _mit_alten_teilen, gemessen="; ".join(_mit_alten_teilen))

# Und die Gegenprobe der Bauform: Der Faden trägt wirklich drei Teile, und der
# Chat ist einer davon.
zeile("der Faden trägt Person, Chat und Thema",
      bot.Faden._fields == ("person", "chat", "thema"),
      gemessen=str(bot.Faden._fields))

# Die Gegenrichtung: Der Zähler läuft über eine nicht-leere Menge. Eine
# Prüfzeile über null Funktionen ist immer grün und misst nichts.
_gefunden = sum(1 for _fn in _ast.walk(_baum)
                if isinstance(_fn, (_ast.FunctionDef, _ast.AsyncFunctionDef))
                and _fn.name in _TUEREN)
zeile("der Zähler sieht die Türen überhaupt",
      _gefunden >= 8, gemessen=f"{_gefunden} von {len(_TUEREN)} Türen gefunden")

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen von Block 1 bestanden.")
