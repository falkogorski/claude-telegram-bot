#!/usr/bin/env python3
# <!-- ROLLE: test-empfang-block3 -->
"""Der Empfang (Block 3): Werkzeugsatz, Weitergabe, Signatur, Knopf.

**Was hier ausgeführt und was gemessen wird**, denn der Unterschied ist der
ganze Wert dieses Prüfers:

* Die **Sicherheitsentscheidung** wird an der fertigen Befehlszeile gemessen —
  dieselbe Zeichenkette, die die CLI wirklich bekommt (`_build_command`). Ein
  Textscan über `bot.py` ließe sich durch Aufteilen der Zeichenkette umgehen.
* Das **Werkzeug** wird ausgeführt. Attrappen sitzen nur an den Rändern; was
  in der Mitte läuft, ist der Code, der im Betrieb läuft.

**Was hier NICHT gemessen werden kann:** ob die CLI bei `--tools ""` das
in-Prozess-Werkzeug tatsächlich anbietet. Das braucht einen echten Modelllauf;
am Mac war die Anmeldung am 10.09. abgelaufen. Die CLI-Hilfe sagt zu `--tools`
ausdrücklich *„from the built-in set"* — das ist **gelesen, nicht gemessen**,
und steht deshalb als Prüfzeile für den Betrieb im Bericht, nicht als grüne
Zeile hier.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="empfang-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP / "conversations")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot                                                      # noqa: E402
import channels                                                 # noqa: E402
import empfang                                              # noqa: E402
from claude_agent_sdk._internal.transport.subprocess_cli import (  # noqa: E402
    SubprocessCLITransport)

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
print("== Empfang (Block 3) ==")

# ── 1. Der Werkzeugsatz, an der fertigen Befehlszeile ────────────────────────
opts = bot.sekretaerin_optionen(UID)
_transport = SubprocessCLITransport(prompt="x", options=opts)
_transport._cli_path = "/bin/echo"        # Pfad setzen, ohne zu starten
cmd = _transport._build_command()
befehl = " ".join(cmd)

zeile("alle eingebauten Werkzeuge sind abgeschaltet",
      "--tools" in cmd and cmd[cmd.index("--tools") + 1] == "",
      gemessen=befehl[:200])
zeile("die Positivliste trägt genau einen Eintrag: den VOLLEN Werkzeugnamen",
      "--allowedTools" in cmd
      and cmd[cmd.index("--allowedTools") + 1] == empfang.WERKZEUG_NAME,
      gemessen=str(opts.allowed_tools))
zeile("der Modus ist dontAsk, nicht bypassPermissions",
      opts.permission_mode == "dontAsk", gemessen=str(opts.permission_mode))
zeile("die Verbotsliste sperrt Bash, Read, Write und WebFetch ausdrücklich",
      all(w in (opts.disallowed_tools or []) for w in
          ("Bash", "Read", "Write", "WebFetch")))
zeile("der Werkzeug-Server ist mitgegeben",
      empfang.WERKZEUG_SERVER in (opts.mcp_servers or {}))
zeile("die Websuche ist NICHT dabei",
      "suche" not in (opts.mcp_servers or {}))
zeile("kein Ordner ist mitgegeben (add_dirs leer)",
      not (opts.add_dirs or []), gemessen=str(opts.add_dirs))
zeile("kein Freigabe-Rückruf — sie soll nicht fragen dürfen",
      getattr(opts, "can_use_tool", None) is None)
zeile("sie läuft auf Sonnet, nicht auf dem höchsten Modell",
      "sonnet" in (opts.model or ""), gemessen=str(opts.model))

# **Die Gegenprobe zur Positivliste**, ohne die die Zeile nur eine Schreibweise
# prüft: Ein leerer Eintrag träfe genau den Fehler aus `bot.py:4744` — und
# `dontAsk` mit leerer Liste verweigert dann auch das eigene Werkzeug.
leer = bot.werkzeugfreie_optionen("x")
zeile("ohne Positivliste bleibt die Fabrik bei null Einträgen",
      list(leer.allowed_tools or []) == [] and leer.permission_mode == "dontAsk")

# ── 2. Das Werkzeug, ausgeführt ──────────────────────────────────────────────
# Der Handler steckt in einer Closure und wird vom SDK im Server gekapselt.
# Statt in dessen Innereien zu greifen, wird er **beim Bauen** mitgenommen —
# so misst der Prüfer denselben Code, den der Server registriert.
_HANDLER: list = []
_orig_tool_server = bot.create_sdk_mcp_server


def _fang(name, version="1.0.0", tools=None):
    if tools:
        _HANDLER.clear()
        _HANDLER.append(tools[0].handler)
    return _orig_tool_server(name=name, version=version, tools=tools)


bot.create_sdk_mcp_server = _fang
bot._empfang_mcp(UID)
bot.create_sdk_mcp_server = _orig_tool_server
werkzeug = _HANDLER[0]


def lauf(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


asyncio.set_event_loop(asyncio.new_event_loop())

# **Attrappe am Rand: der Arbeiter.** Ohne sie holt der echte Worker den Job
# im selben Atemzug wieder aus der Warteschlange und startet einen Modelllauf
# — gemessen würde dann die Abarbeitung, nicht die Einreihung. Dass der
# Arbeiter angestoßen wird, prüft die Zeile darunter eigens.
_GEWECKT: list = []
bot._ensure_worker = lambda uid, tid=None: _GEWECKT.append((uid, tid))

# Ein Zimmer, das es wirklich gibt: über die laufenden Fäden (ohne Häuser).
mb_haupt = bot._get_mailbox(UID, None)
erg = lauf(werkzeug({"zimmer": "Hauptchat", "text": "MIGRATION.md lesen"}))
zeile("ein Auftrag an ein bekanntes Zimmer landet in dessen Warteschlange",
      len(mb_haupt.queue) == 1
      and mb_haupt.queue[0].text == "MIGRATION.md lesen"
      and not erg.get("is_error"),
      gemessen=str(erg))
zeile("der abgelegte Auftrag trägt KEINE Telegram-Nummer",
      mb_haupt.queue and mb_haupt.queue[0].message_id is None,
      gemessen=str(mb_haupt.queue[0].message_id if mb_haupt.queue else "leer"))
zeile("der Arbeiter des Zimmers wird angestoßen",
      (UID, None) in _GEWECKT, gemessen=str(_GEWECKT))

vorher = len(mb_haupt.queue)
erg = lauf(werkzeug({"zimmer": "Rumpelkammer", "text": "irgendwas"}))
zeile("ein unbekanntes Zimmer wird benannt abgelehnt, nichts wird eingereiht",
      erg.get("is_error") and len(mb_haupt.queue) == vorher
      and "Rumpelkammer" in erg["content"][0]["text"],
      gemessen=str(erg))
zeile("die Absage nennt die bekannten Zimmer",
      "Hauptchat" in erg["content"][0]["text"])

# Der Riegel gegen den doppelten Auftrag — **Code, nicht Prompt.**
bot._EMPFANG.setdefault(UID, {})["nur_antworten"] = True
vorher = len(mb_haupt.queue)
erg = lauf(werkzeug({"zimmer": "Hauptchat", "text": "doppelt"}))
zeile("bei einer Zwischenantwort reicht sie nichts weiter",
      erg.get("is_error") and len(mb_haupt.queue) == vorher,
      gemessen=str(erg))
bot._EMPFANG[UID]["nur_antworten"] = False

# ── 3. Zettel und Registerschlüssel ─────────────────────────────────────────
mb_haupt.current_job = bot.QueuedJob(update=None, text="laeuft gerade",
                                     user_id=UID, message_id=77)
erg = bot.auftrag_einreihen(UID, None, "waehrend gearbeitet wird", chat_id=UID)
zwilling = mb_haupt.queue[-1]
zeile("in ein arbeitendes Zimmer geht der Auftrag ein UND als Zettel hinein",
      erg["lief"] and erg["gereicht"], gemessen=str(erg))
zeile("der Zwilling trägt seine Kennung in zettel_id, nicht in message_id",
      zwilling.zettel_id is not None and zwilling.zettel_id < 0
      and zwilling.message_id is None,
      gemessen=f"zettel_id={zwilling.zettel_id}, message_id={zwilling.message_id}")
zeile("der Registerschlüssel folgt zettel_id, wo es eine gibt",
      bot.zettel_schluessel(zwilling) == zwilling.zettel_id
      and bot.zettel_schluessel(bot.QueuedJob(update=None, text="x",
                                              message_id=42)) == 42)
mb_haupt.current_job = None

# **Die Null-Falle**, latent seit Block 1b: Ein Zettel ohne Kennung stünde
# unter der Null — und übersprungen würde dann JEDER Auftrag ohne
# Telegram-Nummer, weil `int(None or 0)` dieselbe Null ergibt.
bot._ZETTEL.clear()
geschrieben = bot.nachsteuer_schreiben(UID, None, "auftrag-x", None, "text")
zeile("ein Zettel ohne Kennung wird abgelehnt und registriert nichts",
      geschrieben is False and 0 not in bot._ZETTEL)

# ── 4. Signatur (Auflage 5) ─────────────────────────────────────────────────
zeile("jede Antwort des Empfangs trägt sein Zeichen",
      empfang.mit_signatur("Guten Tag").startswith(empfang.SIGNATUR))
zeile("das Zeichen wird nicht doppelt gesetzt",
      empfang.mit_signatur(f"{empfang.SIGNATUR} da")
      .count(empfang.SIGNATUR) == 1)
zeile("das Zeichen ist das von Adam gewählte Personenzeichen",
      empfang.SIGNATUR == "👩‍💼", gemessen=repr(empfang.SIGNATUR))

# ── 5. Der eingespeiste Stand (Claudias Bruchstelle Nummer eins) ────────────
stand = empfang.kontext_text([{
    "name": "Werkstatt · Migration & Technik", "wach": True,
    "arbeitet_an": "Protokoll je Zimmer", "seit_s": 185, "warteschlange": 2,
    "zuletzt_fertig": "Leitstand gebaut", "pausiert_rest_s": 0,
}])
zeile("der Stand nennt Zimmer, Auftrag und Warteschlange",
      "Migration & Technik" in stand and "Protokoll je Zimmer" in stand
      and "2 in der Warteschlange" in stand, gemessen=stand)
zeile("die Dauer steht in Worten, nicht in Sekunden",
      "3 Minuten" in stand and "185" not in stand, gemessen=stand)
leer_stand = empfang.kontext_text([])
zeile("ohne wache Zimmer sagt der Stand das ausdrücklich",
      "kein Zimmer wach" in leer_stand, gemessen=leer_stand)

# ── 6. Der Knopf (Auftrag 4) ────────────────────────────────────────────────
bot._USER_PREFS.pop(str(UID), None)
zeile("der Empfang ist aus, solange niemand ihn einschaltet",
      bot.empfang_an(UID) is False)
bot.empfang_setzen(UID, True)
zeile("eingeschaltet gilt er — und liegt in den Vorlieben, nicht im Speicher",
      bot.empfang_an(UID)
      and bot._USER_PREFS[str(UID)].get("empfang") is True)
bot.empfang_setzen(UID, False)
zeile("er schaltet auch wieder aus", bot.empfang_an(UID) is False)

# ── 7. Die Weiche (Regel 1) — ausgeführt, nicht gelesen ─────────────────────
bot.empfang_setzen(UID, True)
zeile("bei eingeschaltetem Empfang beantwortet die Sekretärin den Hauptchat",
      bot.geht_an_empfang(UID, None, None) is True)
zeile("in einem Zimmer arbeitet das Zimmer, nicht der Empfang",
      bot.geht_an_empfang(UID, 47, None) is False)
zeile("eine Nachricht mit Anhang geht am Empfang vorbei",
      bot.geht_an_empfang(UID, None, "📎 Datei: b.pdf") is False)
bot.empfang_setzen(UID, False)
zeile("bei ausgeschaltetem Knopf wird der Empfang NIE gefragt",
      bot.geht_an_empfang(UID, None, None) is False)

# ── 8. Anhänge gehen am Empfang vorbei ──────────────────────────────────────
zeile("Foto, Datei und Video gehen nicht an den Empfang",
      all(bot._hat_anhang(n) for n in
          ("📷 Foto: a.jpg", "📎 Datei: b.pdf", "🎬 Video: c.mp4")))
zeile("die abgeschriebene Sprachnachricht geht an den Empfang",
      bot._hat_anhang("🎙️ Sprachnachricht (0:42)") is False)

# ── 9. Zimmer-Auflösung: nie geraten ────────────────────────────────────────
zeile("Hauptchat löst auf den Faden ohne Thema auf",
      (bot.zimmer_ziel(UID, "Hauptchat") or {}).get("thread_id") is None)
zeile("ein unbekannter Name löst NICHT auf",
      bot.zimmer_ziel(UID, "Gibt es nicht") is None)

prefs = {}
channels.register_house(prefs, "werkstatt", -100, "Werkstatt", True)
channels.record_topic(prefs, "werkstatt", "Migration & Technik", 47)
zeile("die Schreibweise darf abweichen, die Bedeutung nicht",
      channels.zimmer_aufloesen(prefs, "migration-technik") == (-100, 47,
                                "Werkstatt · Migration & Technik"),
      gemessen=str(channels.zimmer_aufloesen(prefs, "migration-technik")))
channels.register_house(prefs, "nirgendhaus", -200, "Nirgendhaus", True)
channels.record_topic(prefs, "nirgendhaus", "Migration & Technik", 3)
zeile("ein doppelt vergebener Name wird NICHT geraten",
      channels.zimmer_aufloesen(prefs, "Migration & Technik") is None)

# ── 10. Haushalt: Obergrenze und Einschlafen (Auftrag 5) ────────────────────
for fd in list(bot.MAILBOXES):
    bot.MAILBOXES.pop(fd)
zeile("ohne arbeitende Zimmer darf jedes starten",
      bot.darf_starten(UID, None) is True)

for tid in (1, 2, 3):
    m = bot._get_mailbox(UID, tid)
    m.current_job = bot.QueuedJob(update=None, text=f"job {tid}", user_id=UID)
zeile("die Obergrenze zählt die arbeitenden Zimmer der PERSON",
      bot.arbeitende_zimmer(UID) == 3, gemessen=str(bot.arbeitende_zimmer(UID)))
zeile("bei erreichter Grenze darf ein weiteres Zimmer NICHT starten",
      bot.darf_starten(UID, 9) is False)
zeile("ein Zimmer zählt sich selbst nicht mit",
      bot.arbeitende_zimmer(UID, ausser=1) == 2)
zeile("eine fremde Person ist von der Grenze nicht betroffen",
      bot.darf_starten(9999, None) is True)
bot.MAILBOXES[bot.faden(UID, 1)].current_job = None
zeile("wird ein Zimmer fertig, darf das wartende starten",
      bot.darf_starten(UID, 9) is True)

# Das Einschlafen — **ausgeführt**, nicht über die Konstante gelesen.
import time as _t                                                # noqa: E402
_jetzt = _t.monotonic()


class _Sitzung:
    def __init__(self, still_s, freigaben=None):
        self.last_activity = _jetzt - still_s
        self.pending_permissions = freigaben or {}


_leer = bot.Mailbox()
zeile("eine lange stille Sitzung ohne Arbeit schläft ein",
      bot.darf_einschlafen(_Sitzung(31 * 60), _leer, _jetzt, thread_id=47) is True)
zeile("eine eben noch tätige Sitzung schläft NICHT ein",
      bot.darf_einschlafen(_Sitzung(60), _leer, _jetzt, thread_id=47) is False)
_voll = bot.Mailbox()
_voll.current_job = bot.QueuedJob(update=None, text="laeuft", user_id=UID)
zeile("ein arbeitendes Zimmer schläft nicht ein, egal wie still es ist",
      bot.darf_einschlafen(_Sitzung(99 * 60), _voll, _jetzt, thread_id=47) is False)
zeile("eine offene Freigabe verhindert das Einschlafen — sie wartet auf Adam",
      bot.darf_einschlafen(_Sitzung(99 * 60, {"r1": "x"}), _leer, _jetzt,
                           thread_id=47) is False)
zeile("eine frisch geöffnete Sitzung ohne jede Regung schläft nicht ein",
      bot.darf_einschlafen(_Sitzung(0), _leer, _jetzt, thread_id=47) is False
      and bot.darf_einschlafen(type("S", (), {"last_activity": 0,
                                              "pending_permissions": {}})(),
                               _leer, _jetzt, thread_id=47) is False)
# **Der Empfang schläft nicht** (Claudias Auftrag 5) — und zwar bauartbedingt:
# Er liegt in einem eigenen Register, nicht in `SESSIONS`. Der Wächter, der
# einschlafen lässt, läuft über `SESSIONS` und kann ihn deshalb nie erreichen.
bot._EMPFANG[UID] = {"client": None, "bot": None, "chat_id": UID}
zeile("der Empfang liegt in einem eigenen Register, nicht bei den Zimmern",
      UID in bot._EMPFANG
      and not any(fd for fd in bot.SESSIONS if fd == bot.faden(UID, None)),
      gemessen=f"SESSIONS={list(bot.SESSIONS)}")
zeile("der Empfang taucht im Leitstand nicht auf — er ist kein Zimmer",
      all("mpfang" not in (z.get("name") or "") for z in bot.leitstand(UID)),
      gemessen=str([z.get("name") for z in bot.leitstand(UID)]))

# ── A-4 (Ultracode 10.09.): was OHNE den Knopf wirkt ────────────────────────
#
# **Diese vier Zeilen sind die dringendsten des ganzen Blocks:** Der Haushalt
# läuft unabhängig vom Empfangs-Knopf, also seit dem Deploy im Betrieb.
zeile("A-4: der HAUPTFADEN schläft nicht ein (Adams Entscheid)",
      bot.darf_einschlafen(_Sitzung(99 * 60), _leer, _jetzt, thread_id=None) is False)
zeile("A-4: ein Zimmer schläft weiterhin ein (Gegenrichtung)",
      bot.darf_einschlafen(_Sitzung(99 * 60), _leer, _jetzt, thread_id=47) is True)
# **[UMGESTELLT 10.09.2026, Engywucks Befund] Diese Zeile schrieb den
# Vorgabewert fest.** Sie verlangte, dass ein Aufruf OHNE Faden schlafen darf
# — also genau die Lücke, die Block 1b so teuer gemacht hat. Jetzt misst sie
# das Gegenteil: **Wer den Faden vergisst, kommt gar nicht durch.**
try:
    bot.darf_einschlafen(_Sitzung(99 * 60), _leer, _jetzt)
    _ohne_faden_ging = True
except TypeError:
    _ohne_faden_ging = False
zeile("A-4: ohne Faden ist der Aufruf gar nicht möglich (pflichtig)",
      _ohne_faden_ging is False)

# `0` heißt AUS, nicht „sofort" — bei `ZIMMER_GLEICHZEITIG` heißt es dasselbe.
# Zwei Schalter mit derselben Null und entgegengesetzter Wirkung sind eine
# Falle, die genau einmal zuschlägt.
_alt = bot.ZIMMER_SCHLAF_NACH_S
bot.ZIMMER_SCHLAF_NACH_S = 0
zeile("A-4: die Null schaltet das Einschlafen AUS, nicht scharf",
      bot.darf_einschlafen(_Sitzung(99 * 60), _leer, _jetzt, thread_id=47) is False)
bot.ZIMMER_SCHLAF_NACH_S = _alt

# Ein Zimmer, das auf Adams Freigabe wartet, rechnet nicht — sonst blockierten
# drei offene Dialoge jedes weitere Zimmer bis zu einer Stunde.
for fd in list(bot.MAILBOXES):
    bot.MAILBOXES.pop(fd)
for fd in list(bot.SESSIONS):
    bot.SESSIONS.pop(fd)
for tid in (1, 2, 3):
    m = bot._get_mailbox(UID, tid)
    m.current_job = bot.QueuedJob(update=None, text=f"job {tid}", user_id=UID)
zeile("A-4: drei rechnende Zimmer füllen die Grenze",
      bot.darf_starten(UID, 9) is False)
_wartend = bot.UserSession(client=None)
_wartend.pending_permissions = {"r1": "wartet auf Adam"}
bot.SESSIONS[bot.faden(UID, 2)] = _wartend
zeile("A-4: ein Zimmer, das auf eine Freigabe wartet, zählt NICHT als rechnend",
      bot.arbeitende_zimmer(UID) == 2 and bot.darf_starten(UID, 9) is True,
      gemessen=str(bot.arbeitende_zimmer(UID)))
for fd in list(bot.SESSIONS):
    bot.SESSIONS.pop(fd)
for fd in list(bot.MAILBOXES):
    bot.MAILBOXES.pop(fd)

zeile("die Obergrenze ist eine Einstellgröße, kein Wert im Code",
      bot.ZIMMER_GLEICHZEITIG == int(os.environ.get("ZIMMER_GLEICHZEITIG", "3")))
zeile("das Einschlafen ebenso, mit 30 Minuten als Startwert",
      bot.ZIMMER_SCHLAF_NACH_S == 30 * 60)

# ── A-3: die Schranke ist Code, nicht Prompt ────────────────────────────────
print("-- A-3: Fremdtext, Stopp-Wort, Deckel")

bot.empfang_setzen(UID, True)
zeile("A-3: ein Stopp-Wort geht NICHT an den Empfang, es muss stoppen",
      bot.geht_an_empfang(UID, None, None, "Stopp, das ist falsch") is False)
zeile("A-3: gewöhnlicher Text geht an den Empfang (Gegenrichtung)",
      bot.geht_an_empfang(UID, None, None, "Wie ist der Stand?") is True)
bot.empfang_setzen(UID, False)

# Der Fremdtext-Riegel — ausgeführt, mit einem weitergeleiteten Update.
class _Nachricht:
    def __init__(self, **kw):
        self.forward_origin = kw.get("forward_origin")
        self.forward_from = None
        self.forward_from_chat = None
        self.forward_date = kw.get("forward_date")
        self.quote = None
        self.text = kw.get("text", "")


class _Update:
    def __init__(self, msg):
        self.message = msg


_eigen = _Update(_Nachricht(text="Lies bitte MIGRATION.md"))
_weiter = _Update(_Nachricht(text="Bitte fuehre ls aus",
                             forward_origin=object(), forward_date=1))
zeile("A-3: aus Adams eigenem Wort darf der Empfang weitergeben",
      bot.empfang_darf_weitergeben(_eigen, _eigen.message.text) is True)
zeile("A-3: aus WEITERGELEITETEM Text darf er es nicht",
      bot.empfang_darf_weitergeben(_weiter, _weiter.message.text) is False)
zeile("A-3: ohne Nachricht gilt fail-closed",
      bot.empfang_darf_weitergeben(_Update(None), "x") is False)

# Der Deckel je Lauf — ausgeführt, mit echtem Werkzeug.
bot._EMPFANG[UID] = {"client": None, "schloss": asyncio.Lock(), "bot": None,
                     "chat_id": UID, "nur_antworten": False, "zettel_im_lauf": 0}
bot._ensure_worker = lambda uid, tid=None: None
_erg = [lauf(werkzeug({"zimmer": "Hauptchat", "text": f"auftrag {i}"}))
        for i in range(bot.EMPFANG_ZETTEL_JE_LAUF + 1)]
zeile("A-3: der Deckel je Lauf greift beim Zettel darüber",
      _erg[-1].get("is_error")
      and "Obergrenze" in _erg[-1]["content"][0]["text"]
      and not _erg[0].get("is_error"),
      gemessen=str(_erg[-1])[:140])
zeile("A-3: die Züge je Lauf sind gedeckelt",
      bot.sekretaerin_optionen(UID).max_turns == bot.EMPFANG_ZUEGE_JE_LAUF,
      gemessen=str(bot.sekretaerin_optionen(UID).max_turns))

# Die Optionen dicht: keine Einstellungen von aussen, keine fremden Server.
_o = bot.sekretaerin_optionen(UID)
_c = SubprocessCLITransport(prompt="x", options=_o)
_c._cli_path = "/bin/echo"
_flags = _c._build_command()
zeile("A-3: keine Einstellungsdateien von außen",
      "--setting-sources=" in _flags, gemessen=str(_o.setting_sources))
zeile("A-3: keine Werkzeug-Server außer dem eigenen",
      "--strict-mcp-config" in _flags, gemessen=str(_o.strict_mcp_config))
bot._EMPFANG.pop(UID, None)

# Die Kontingent-Pause gilt auch dem Empfang — er läuft aus demselben Topf.
bot._EMPFANG.pop(UID, None)
bot.limit_pause_setzen(UID, _t.time() + 600)
zeile("A-3: bei laufender Kontingent-Pause fragt der Empfang gar nicht erst",
      lauf(bot.sekretaerin_fragen(UID, "Wie ist der Stand?")) is None
      and UID not in bot._EMPFANG,
      gemessen=str(list(bot._EMPFANG)))
bot.limit_pause_loeschen(UID)

# Der Selbstcheck fängt einen Eintrag, der am Schloss vorbei entsteht.
# **`client` ist absichtlich da:** So misst die Zeile das SCHLOSS allein.
# Mit einem leeren Eintrag hätte die zweite Bedingung mitgefangen, und die
# Gegenprobe hätte grün gezeigt, obwohl der Schloss-Schutz entfernt war —
# genau die falsche Gegenprobe, vor der die eigenen Regeln warnen.
bot._EMPFANG[UID] = {"client": None}
_ok, _zeilen = bot.run_self_check()
zeile("A-1: ein Eintrag ohne Schloss fällt im Selbstcheck auf",
      any("Empfang wohlgeformt" in z and z.startswith("✗") for z in _zeilen),
      gemessen=str([z for z in _zeilen if "Empfang" in z]))
bot._EMPFANG.pop(UID, None)
_ok2, _zeilen2 = bot.run_self_check()
zeile("A-1: ohne solchen Eintrag ist die Zeile grün (Gegenrichtung)",
      any("Empfang wohlgeformt" in z and z.startswith("✓") for z in _zeilen2))

# ── A-2: die Wege eines weitergereichten Auftrags ───────────────────────────
print("-- A-2: Rückadresse, Kennung, Zwilling")

for fd in list(bot.MAILBOXES):
    bot.MAILBOXES.pop(fd)
bot._ensure_worker = lambda uid, tid=None: None
bot.auftrag_einreihen(UID, 47, "etwas tun", chat_id=-100)
_j = bot._get_mailbox(UID, 47).queue[-1]
zeile("A-2: der Auftrag trägt seine Rückadresse ins ZIMMER, nicht ins General",
      _j.output_thread_id == 47,
      gemessen=f"output_thread_id={_j.output_thread_id}")
zeile("A-2: eine ausdrücklich genannte Rückadresse gewinnt (Gegenrichtung)",
      bot.auftrag_einreihen(UID, 47, "x", chat_id=-100,
                            output_thread_id=9) is not None
      and bot._get_mailbox(UID, 47).queue[-1].output_thread_id == 9)

# Zwei Aufträge aus dem Empfang in derselben Sekunde: verschiedene Kennungen.
_a = bot.QueuedJob(update=None, text="a", user_id=UID, zettel_id=-1,
                   received_at=1000.0)
_b = bot.QueuedJob(update=None, text="b", user_id=UID, zettel_id=-2,
                   received_at=1000.0)
zeile("A-2: zwei Aufträge aus dem Empfang haben verschiedene Kennungen",
      bot._auftrag_kennung(_a) != bot._auftrag_kennung(_b),
      gemessen=f"{bot._auftrag_kennung(_a)} vs {bot._auftrag_kennung(_b)}")

# Der Zwilling eines Empfangs-Auftrags gilt als eingearbeitet.
bot._ZETTEL.clear()
_lauf_job = bot.QueuedJob(update=None, text="laeuft", user_id=UID,
                          received_at=500.0, message_id=3)
_mbz = bot._get_mailbox(UID, None)
_mbz.queue.clear()
_mbz.current_job = _lauf_job
_zw = bot.QueuedJob(update=None, text="zwilling", user_id=UID,
                    zettel_id=-77, received_at=900.0)
_mbz.queue.append(_zw)
bot._ZETTEL[-77] = {"auftrag": "x", "gelesen": True, "erledigt": False}
_offen, _eingearbeitet = bot._neuere_wartende(UID, _lauf_job)
zeile("A-2: ein eingearbeiteter Zwilling aus dem Empfang zählt als erledigt",
      (_offen, _eingearbeitet) == (0, 1),
      gemessen=f"offen={_offen}, eingearbeitet={_eingearbeitet}")
_mbz.current_job = None
_mbz.queue.clear()
bot._ZETTEL.clear()

# ── A-5: Meldungen bleiben im Zimmer ────────────────────────────────────────
#
# **Auch das wirkt ohne den Knopf.** Ein Kontingent-Stopp in Zimmer 47 meldete
# sich im General — und im Zimmer sah es aus wie ein Hänger, also wie Ruhe.
print("-- A-5: Meldungen bleiben im Zimmer")

_GESENDET: list = []


class _MeldeBot:
    async def send_message(self, *a, **kw):
        _GESENDET.append(kw if kw else {"stellung": a})
        return type("M", (), {"message_id": 1})()


# Ausgeführt: die Fehler-Sofortmeldung.
_GESENDET.clear()
_job = bot.QueuedJob(update=None, text="etwas aus Zimmer 47", user_id=UID,
                     chat_id=-100, thread_id=47, message_id=5,
                     bot=_MeldeBot())
lauf(bot._notify_job_failed(_job))
zeile("A-5: die Fehlermeldung geht in das Zimmer, aus dem der Auftrag kam",
      _GESENDET and _GESENDET[0].get("message_thread_id") == 47,
      gemessen=str(_GESENDET))

# Ausgeführt: die Stall-Meldung.
_GESENDET.clear()
_mb = bot.Mailbox()
_mb.current_job = bot.QueuedJob(update=None, text="haengt", user_id=UID,
                                chat_id=-100, thread_id=47, bot=_MeldeBot())
_mb.current_started = _t.monotonic() - 999
lauf(bot._handle_stalled_session(UID, _mb, None, 999.0, thread_id=47))
zeile("A-5: die Stall-Meldung nennt das Zimmer, das hängt",
      any(g.get("message_thread_id") == 47 for g in _GESENDET),
      gemessen=str(_GESENDET)[:200])

# Und die Menge: Kein Sendeaufruf in diesen drei Funktionen ohne Faden.
# **Abwesenheit über echte Aufrufknoten gemessen**, nicht über Textsuche —
# ein Name im Baum sagt nichts, ein fehlendes Schlüsselwort schon.
import ast as _ast                                                # noqa: E402
_quelle = (Path(bot.__file__).read_text(encoding="utf-8"))
_baum = _ast.parse(_quelle)
_ohne_faden: list[str] = []
for _fn in _ast.walk(_baum):
    if not isinstance(_fn, (_ast.FunctionDef, _ast.AsyncFunctionDef)):
        continue
    if _fn.name not in ("_run_job", "_notify_job_failed",
                        "_handle_stalled_session"):
        continue
    for _k in _ast.walk(_fn):
        if not isinstance(_k, _ast.Call):
            continue
        _name = getattr(_k.func, "attr", None) or getattr(_k.func, "id", None)
        if _name not in ("send_chunked", "send_message"):
            continue
        _kw = {a.arg for a in _k.keywords}
        if not ({"thread_id", "message_thread_id"} & _kw):
            _ohne_faden.append(f"{_fn.name}:{_k.lineno}")
zeile("A-5: kein Sendeaufruf in Auftrag, Fehlermeldung und Wächter ohne Faden",
      not _ohne_faden, gemessen=", ".join(_ohne_faden))

print(f"\n{zeilen - len(fehler)}/{zeilen} Zeilen grün")
sys.exit(1 if fehler else 0)
