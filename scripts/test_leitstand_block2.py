#!/usr/bin/env python3
# <!-- ROLLE: test-leitstand-block2 -->
"""Block 2 des Zimmer-Baus — **die Sicht stimmt mit der Wirklichkeit ueberein.**

Auftrag 6: Protokoll je Zimmer und Leitstand. Engywucks Abnahmezeile lautet
*„`/zimmer` stimmt mit der Wirklichkeit ueberein (zwei Zimmer, eines
schlaeft)"* — genau das wird hier gemessen, und zwar **ausgefuehrt**: Der
Befehl wird mit einer Update-Attrappe gerufen und sein Text geprueft.

**Warum der Leitstand vor der Sekretaerin steht** (Auflage 7): Er ist die
Quelle ihres Kontexts. Eine Sekretaerin ohne eingespeisten Stand erfindet
Auskuenfte — und eine erfundene Auskunft ueber den eigenen Betrieb ist
schlimmer als gar keine.
"""
import asyncio
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="leitstand-"))
# Erzwungen, nicht ergaenzt -- `setdefault` erbte im Zweifel den echten Wert.
os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP / "conversations")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot                                                      # noqa: E402
import channels                                                 # noqa: E402

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
print("== Block 2: Leitstand und Protokoll je Zimmer ==")

# ---- Aufbau: zwei Zimmer, eines arbeitet, eines schlaeft -------------------
job7 = bot.QueuedJob(update=None, text="Rechne die Aufstellung fuer Norderney",
                     user_id=UID, chat_id=999, message_id=7, thread_id=7)
mb7 = bot._get_mailbox(UID, 7)
mb7.current_job = job7
mb7.current_started = time.monotonic() - 180          # laeuft seit drei Minuten
sess7 = bot.UserSession(client=None, chat_id=999)
sess7.last_activity = time.monotonic()
bot.SESSIONS[bot.faden(UID, 7)] = sess7

# Zimmer 8: Warteschlange und eine erledigte Aufgabe, aber KEINE Sitzung.
mb8 = bot._get_mailbox(UID, 8)
mb8.done_log.append((time.time() - 3600, "Angebot geschrieben"))
mb8.queue.append(bot.QueuedJob(update=None, text="warte hier", user_id=UID,
                               chat_id=999, message_id=8, thread_id=8))

stand = {z["thread_id"]: z for z in bot.leitstand(UID)}

zeile("beide Zimmer stehen im Leitstand",
      set(stand) == {7, 8}, gemessen=str(sorted(stand)))
zeile("das arbeitende Zimmer nennt SEINEN Auftrag",
      stand[7]["arbeitet_an"] and "Norderney" in stand[7]["arbeitet_an"],
      gemessen=str(stand[7]["arbeitet_an"]))
zeile("und das andere arbeitet an nichts (Gegenrichtung)",
      stand[8]["arbeitet_an"] is None, gemessen=str(stand[8]["arbeitet_an"]))
zeile("wach ist, wer eine Sitzung hat",
      stand[7]["wach"] and not stand[8]["wach"],
      gemessen=f"7:{stand[7]['wach']} 8:{stand[8]['wach']}")
zeile("die Warteschlange wird je Zimmer gezaehlt",
      stand[7]["warteschlange"] == 0 and stand[8]["warteschlange"] == 1,
      gemessen=f"7:{stand[7]['warteschlange']} 8:{stand[8]['warteschlange']}")
zeile("zuletzt fertig steht beim richtigen Zimmer",
      stand[8]["zuletzt_fertig"] == "Angebot geschrieben"
      and stand[7]["zuletzt_fertig"] is None,
      gemessen=str(stand[8]["zuletzt_fertig"]))

# ---- Die Zeitbasen, und sie sind die eigentliche Falle ---------------------
#
# `current_started` und `last_activity` sind `time.monotonic()`, `done_log`
# traegt `time.time()`. Ein Vergleich ueber die Grenze wirft KEINEN Fehler und
# ist trotzdem immer falsch (Befund 17.07.). Deshalb zwei Zeilen, die messen,
# dass jede Groesse aus ihrer eigenen Basis kommt.
zeile("die laufende Dauer ist eine DAUER (drei Minuten, nicht 56 Jahre)",
      150 < stand[7]["seit_s"] < 250, gemessen=f"{stand[7]['seit_s']:.0f} s")
zeile("der Fertig-Zeitpunkt ist ein ZEITPUNKT der Wanduhr",
      "Stunde" in bot._vor_wie_lange(stand[8]["zuletzt_fertig_ts"]),
      gemessen=bot._vor_wie_lange(stand[8]["zuletzt_fertig_ts"]))

# ---- Der Name: aufgeloest, aber nie geraten -------------------------------
zeile("ohne Zuordnung steht die nackte Kennung da, kein erfundener Name",
      stand[7]["name"] == "Zimmer 7", gemessen=stand[7]["name"])

channels.register_house(bot._USER_PREFS, "werkstatt", 999, "🔧 Werkstatt", True)
channels.record_topic(bot._USER_PREFS, "werkstatt", "Migration & Technik", 7)
stand2 = {z["thread_id"]: z for z in bot.leitstand(UID)}
zeile("mit Zuordnung steht der Klarname da",
      "Migration & Technik" in stand2[7]["name"], gemessen=stand2[7]["name"])
zeile("ein anderer Chat mit derselben Themen-Kennung bekommt den Namen NICHT",
      channels.zimmer_name_fuer(bot._USER_PREFS, 12345, 7) is None,
      gemessen=str(channels.zimmer_name_fuer(bot._USER_PREFS, 12345, 7)))

# ---- Der Befehl selbst, ausgefuehrt ---------------------------------------
GESENDET: list[str] = []


class _Nachricht:
    message_id = 1
    message_thread_id = None

    async def reply_text(self, text, **kw):
        GESENDET.append(text)
        return None


class _Update:
    class _User:
        id = UID
        is_bot = False

    effective_user = _User()
    effective_message = _Nachricht()
    message = effective_message
    effective_chat = None


asyncio.run(bot.cmd_zimmer(_Update(), None))
text = GESENDET[0] if GESENDET else ""

zeile("/zimmer antwortet ueberhaupt", bool(text), gemessen=text[:60])
zeile("und nennt das arbeitende Zimmer mit seinem Auftrag",
      "Norderney" in text and "arbeitet an" in text, gemessen=text[:120])
zeile("das schlafende Zimmer steht als schlafend da",
      "schläft" in text, gemessen=text[:200])
# Erste Fassung dieser Zeile mass die falsche Sache: `" s" not in text` traf
# auf „— schlaeft". Jetzt gesucht wird eine nackte Sekundenzahl -- das ist,
# was hier nicht stehen soll (Adams Zeitform-Regel).
import re as _re                                                # noqa: E402

zeile("die Dauer steht in Worten, keine nackte Sekundenzahl",
      "Minuten" in text and not _re.search(r"\b\d+\s*(?:s|Sek|Sekunden)\b", text),
      gemessen=text[:160])
# **Adams Regel vom 20.08.:** keine Frage, deren Antwort nirgends ankommt.
zeile("keine Frage ohne Wirkung",
      not text.rstrip().endswith("?"), gemessen=text.rstrip()[-60:])
zeile("die Meldung nennt ihren Antwortweg",
      "Antwortweg" in text, gemessen=text[-120:])

# ---- Protokoll je Zimmer ---------------------------------------------------
#
# Der HAUPTFADEN behaelt `<datum>.md`. Das ist keine Bequemlichkeit: Wachposten,
# Log-Abgleich und die Mac-Sitzung lesen diesen Namen seit Wochen.
tag = time.strftime("%Y-%m-%d")
bot.ConversationLogger(UID).log_user("aus dem Hauptchat")
bot.ConversationLogger(UID, 7).log_user("aus Zimmer sieben")
haupt = bot.LOG_DIR / f"{tag}.md"
zimmer = bot.LOG_DIR / f"{tag}_zimmer-7.md"

zeile("der Hauptfaden behaelt seinen Dateinamen",
      haupt.exists(), gemessen=str(sorted(p.name for p in bot.LOG_DIR.glob("*.md"))))
zeile("das Zimmer bekommt eine eigene Datei",
      zimmer.exists(), gemessen=str(sorted(p.name for p in bot.LOG_DIR.glob("*.md"))))
# **Lesen, das nicht wirft.** Faellt die Trennung weg, gibt es die Zimmer-Datei
# gar nicht -- ein `read_text()` risse den Pruefer an dieser Stelle ab und
# verdeckte alle Zeilen darunter. In der Gegenprobe gemessen und behoben.
def _inhalt(pfad: Path) -> str:
    return pfad.read_text(encoding="utf-8") if pfad.exists() else ""


zeile("und die Eintraege landen nicht im falschen Protokoll",
      "Zimmer sieben" in _inhalt(zimmer)
      and "Zimmer sieben" not in _inhalt(haupt),
      gemessen=_inhalt(haupt)[:80].replace("\n", " "))
zeile("die Kopfzeile des Zimmer-Protokolls nennt das Zimmer",
      "Zimmer 7" in _inhalt(zimmer),
      gemessen=_inhalt(zimmer)[:60].replace("\n", " "))

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen von Block 2 bestanden.")
