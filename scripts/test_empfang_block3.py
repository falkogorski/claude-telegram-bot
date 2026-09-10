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

print(f"\n{zeilen - len(fehler)}/{zeilen} Zeilen grün")
sys.exit(1 if fehler else 0)
