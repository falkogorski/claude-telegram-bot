#!/usr/bin/env python3
# <!-- ROLLE: test-darstellung -->
"""Darstellung im Antwortweg — **ausgeführt**, nicht gelesen (Block 2, 24.09.2026).

Drei Aufträge in einem Weg, und jeder hat einen Riegel, der still brechen kann:

  A. Auszeichnung: Markdown kommt als Telegram-Entities an; lehnt Telegram ab,
     geht DERSELBE Rohtext hinterher (Claudias Auftrag 2 — Pflicht).
  B. Link-Vorschau: dreistufige Regel, und die Steuerangabe gilt nur für eine
     Adresse, die im Text steht (Engywucks Auflage — der eine Riegel, der die
     Öffnung trägt). Die Steuerzeile erscheint nie im Chat, nie im Ohr.
  C. Kopiertext: eigene Nachricht, roh, nie vorgelesen (Adam 15.09.).

Echter Code in der Mitte (`send_answer_to_user`, `send_chunked`,
`_send_tts_chunk`); Attrappen nur am Rand: Telegram und die Stimmerzeugung.
"""
import asyncio
import os
import sys
import tempfile
import types
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="darstellung-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "1"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["QUESTIONS_FILE"] = str(_TMP / "open_questions.json")
os.environ["PENDING_DIR"] = str(_TMP / "pending")
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP / "conversations")
os.environ["TTS_ROT_LOKAL"] = "aus"   # 9.2: die lokale Stimme misst ihr eigener Pruefer

# Die Stimme ist ein Netzdienst — am Rand ersetzt. Die Attrappe schreibt eine
# Datei, damit der echte `_send_tts_chunk` sie öffnen kann wie im Betrieb.
_GESPROCHEN: list[str] = []


class _Stimme:
    def __init__(self, text, stimme):
        _GESPROCHEN.append(text)

    async def save(self, pfad):
        Path(pfad).write_bytes(b"ID3")


sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=_Stimme)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from telegram.error import BadRequest                           # noqa: E402
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


class _Nachricht:
    def __init__(self, mid):
        self.message_id = mid


class _Telegram:
    """Der Rand. `lehnt_ab` lässt jeden Aufruf MIT Auszeichnung scheitern —
    so, wie Telegram es bei fehlerhafter Auszeichnung tut."""

    def __init__(self, lehnt_ab=False):
        self.lehnt_ab = lehnt_ab
        self.texte: list[dict] = []
        self.stimmen: list[dict] = []
        self.folge: list[str] = []     # Reihenfolge der Sendungen

    async def send_message(self, **kw):
        if self.lehnt_ab and kw.get("entities"):
            raise BadRequest("Can't parse entities")
        self.texte.append(kw)
        self.folge.append("text")
        return _Nachricht(100 + len(self.texte))

    async def send_voice(self, **kw):
        if self.lehnt_ab and kw.get("caption_entities"):
            raise BadRequest("Can't parse caption entities")
        kw.pop("voice", None)
        self.stimmen.append(kw)
        self.folge.append("stimme")
        return _Nachricht(500 + len(self.stimmen))


def _sitzung(tg, tts=False, vorschau=True):
    bot._USER_PREFS.setdefault("1", {})["link_vorschau"] = vorschau
    s = bot.UserSession(client=None, user_id=1, chat_id=1)
    s.bot = tg
    s.tts_enabled = tts
    return s


def _senden(text, *, tts=False, vorschau=True, lehnt_ab=False):
    tg = _Telegram(lehnt_ab=lehnt_ab)
    _GESPROCHEN.clear()
    # Ein Bruch im Pfad macht die Zeile ROT, er stuerzt den Pruefer nicht ab —
    # ein abstuerzender Pruefer verdeckt alle Zeilen darunter.
    try:
        ok = asyncio.run(bot.send_answer_to_user(_sitzung(tg, tts, vorschau), 1, text))
    except Exception as e:
        print(f"     (Pfad warf {type(e).__name__}: {e})")
        ok = False
    return ok, tg


def _arten(kw):
    return {e.type for e in (kw.get("entities") or kw.get("caption_entities") or [])}


def _vorschau(kw):
    lp = kw.get("link_preview_options")
    return None if lp is None else (lp.is_disabled, lp.url)


PROBE = ("**Die Aussage** und *Cleanse to Heal* und "
         "[ab Minute 12](https://youtu.be/abc?t=775) und `mein_name.md` "
         "und ein einzelner * Stern.")

# ── A. Auszeichnung ────────────────────────────────────────────────────────
print("== A. Auszeichnung mit Rückfall ==")
ok, tg = _senden(PROBE)
k = tg.texte[0] if tg.texte else {}
zeile("Fett, Kursiv, Link und Code kommen als Auszeichnung an",
      {"bold", "italic", "text_link", "code"} <= _arten(k), gemessen=str(_arten(k)))
zeile("im Text stehen keine Sternchen und keine Adresse mehr",
      "**" not in k.get("text", "") and "https://" not in k.get("text", ""),
      gemessen=repr(k.get("text", "")[:70]))
zeile("ohne parse_mode — die Entities tragen die Form",
      "parse_mode" not in k, gemessen=str(k.get("parse_mode")))

ok, tg = _senden(PROBE, lehnt_ab=True)
zeile("lehnt Telegram ab, geht DERSELBE Rohtext hinterher (Pflicht-Rückfall)",
      ok and len(tg.texte) == 1 and tg.texte[0].get("text") == PROBE
      and not tg.texte[0].get("entities"),
      gemessen=f"{len(tg.texte)} gesendet: {[t.get('text', '')[:30] for t in tg.texte]}")

_alt_tgm = bot._tgm
bot._tgm = None
try:
    ok, tg = _senden(PROBE)
finally:
    bot._tgm = _alt_tgm
zeile("fehlt das Paket, geht der Rohtext — keine Antwort geht verloren",
      ok and tg.texte and tg.texte[0].get("text") == PROBE,
      gemessen=str([t.get("text", "")[:30] for t in tg.texte]))

# Schnitt VOR dem Umwandeln, und nie mitten durch einen Codeblock.
lang = ("Einleitung.\n\n" + "Zeile mit etwas Text darin.\n" * 130
        + "```\n" + "code zeile\n" * 60 + "```\n\nSchluss **fett**.")
ok, tg = _senden(lang)
zaeune = [t.get("text", "").count("```") for t in tg.texte]
zeile("eine lange Antwort wird geteilt, jedes Stück ausgezeichnet",
      len(tg.texte) >= 2 and all(t.get("entities") is not None for t in tg.texte)
      and not any("```" in t.get("text", "") for t in tg.texte),
      gemessen=f"{len(tg.texte)} Stücke, Zäune roh: {zaeune}, "
               f"Arten: {[sorted(_arten(t)) for t in tg.texte]}")
zeile("und der Codeblock landet ganz in einem Stück",
      sum(1 for t in tg.texte if "pre" in _arten(t)) == 1,
      gemessen=str([sorted(_arten(t)) for t in tg.texte]))

# ── B. Link-Vorschau ───────────────────────────────────────────────────────
print("== B. Link-Vorschau ==")
A1, A2, A3 = "https://a.example/1", "https://b.example/2", "https://c.example/3"
drei = f"Erst [eins]({A1}), dann [zwei]({A2}), zuletzt [drei]({A3})."

ok, tg = _senden(drei + f"\n<vorschau>{A2}</vorschau>")
k = tg.texte[0] if tg.texte else {}
zeile("Steuerangabe mit Adresse aus dem Text → Karte genau dafür",
      _vorschau(k) == (False, A2), gemessen=str(_vorschau(k)))
# Die Umwandlung schluckt spitze Klammern, laesst aber die Adresse stehen —
# darum wird auch die Adresse geprueft (Gegenprobe vom 24.09.: nur „vorschau"
# zu suchen blieb gruen, waehrend die Adresse nackt im Chat stand).
zeile("die Steuerzeile erscheint nicht im Chat, auch nicht ihre Adresse",
      all("vorschau" not in t.get("text", "") and A2 not in t.get("text", "")
          for t in tg.texte),
      gemessen=repr(k.get("text", "")[-40:]))

fremd = "https://boese.example/abruf-merker"
ok, tg = _senden(drei + f"\n<vorschau>{fremd}</vorschau>")
k = tg.texte[0] if tg.texte else {}
zeile("Steuerangabe mit FREMDER Adresse → übergangen, Stufe 3 (der letzte Link)",
      _vorschau(k) == (False, A3), gemessen=str(_vorschau(k)))

ok, tg = _senden(f"Nur ein Link: [hier]({A1}).")
zeile("genau ein Link → Karte dafür (Stufe 2)",
      tg.texte and _vorschau(tg.texte[0]) == (False, A1),
      gemessen=str(_vorschau(tg.texte[0]) if tg.texte else None))

ok, tg = _senden("Gar kein Link, nur Text mit **fett**.")
zeile("ohne Link keine Vorschau-Angabe — die Voreinstellung (aus) gilt",
      tg.texte and _vorschau(tg.texte[0]) is None,
      gemessen=str(_vorschau(tg.texte[0]) if tg.texte else None))

ok, tg = _senden(drei, vorschau=False)
zeile("Schalter aus → keine Karte",
      tg.texte and _vorschau(tg.texte[0]) is None,
      gemessen=str(_vorschau(tg.texte[0]) if tg.texte else None))

ok, tg = _senden(drei + f"\n<vorschau>{A2}</vorschau>", tts=True)
zeile("mit Sprachausgabe: die Steuerzeile wird nicht vorgelesen",
      _GESPROCHEN and all("vorschau" not in g and A2 not in g for g in _GESPROCHEN),
      gemessen=str([g[-40:] for g in _GESPROCHEN]))
zeile("und steht nicht in der Bildunterschrift",
      tg.stimmen and all("vorschau" not in (s.get("caption") or "")
                         for s in tg.stimmen),
      gemessen=str([(s.get("caption") or "")[-40:] for s in tg.stimmen]))
# Seit der Vorschau-Trennung (26.09.) traegt die Stimme bei gewollter Karte
# nur noch eine kurze Unterschrift — die Auszeichnung der Unterschrift misst
# deshalb der Fall OHNE Karte.
ok, tg = _senden(drei, tts=True, vorschau=False)
zeile("die Bildunterschrift ist ausgezeichnet (ohne Karte)",
      tg.stimmen and "text_link" in _arten(tg.stimmen[0]),
      gemessen=str(_arten(tg.stimmen[0]) if tg.stimmen else None))

ok, tg = _senden(PROBE, tts=True, vorschau=False, lehnt_ab=True)
zeile("lehnt Telegram die Bildunterschrift ab, kommt die Stimme mit Rohtext",
      ok and len(tg.stimmen) == 1 and tg.stimmen[0].get("caption") == PROBE
      and not tg.stimmen[0].get("caption_entities"),
      gemessen=str([(s.get("caption") or "")[:30] for s in tg.stimmen]))

# ── B2. Vorschaukarte und Sprachausgabe getrennt (26.09.) ───────────────────
# Engywucks Befund 1, Adams Entscheid 14:00: An einer Bildunterschrift zeigt
# Telegram keine Karte. Mit Karte UND Stimme: der Text als eigene Nachricht mit
# Karte, ZUERST (Fenster-Regel), die Stimme danach mit kurzer Unterschrift.
print("== B2. Vorschau und Sprachausgabe ==")
ok, tg = _senden(drei + f"\n<vorschau>{A2}</vorschau>", tts=True)
zeile("mit Karte und Stimme: eine Textnachricht mit Karte und die Stimme",
      ok and len(tg.texte) == 1 and _vorschau(tg.texte[0]) == (False, A2) and tg.stimmen,
      gemessen=f"texte={len(tg.texte)} karte={_vorschau(tg.texte[0]) if tg.texte else None} "
               f"stimmen={len(tg.stimmen)}")
zeile("der Text kommt zuerst, dann die Stimme", tg.folge[:2] == ["text", "stimme"],
      gemessen=str(tg.folge))
zeile("die Stimme trägt keinen langen Untertext", all(not s.get("caption") for s in tg.stimmen),
      gemessen=str([(s.get("caption") or "")[:30] for s in tg.stimmen]))
ok, tg = _senden(drei, tts=True, vorschau=False)
zeile("ohne Karte bleibt es bei einer Nachricht: Stimme mit Text als Unterschrift",
      ok and not tg.texte and len(tg.stimmen) == 1 and tg.stimmen[0].get("caption"),
      gemessen=f"texte={len(tg.texte)} stimmen={len(tg.stimmen)}")

# ── C. Kopiertext ─────────────────────────────────────────────────────────
print("== C. Kopiertext ==")
MAIL = "Hallo,\n\nvielen Dank für den **Auftrag**.\n\nViele Grüße"
text = f"Hier die Mail:\n\n<kopie>\n{MAIL}\n</kopie>\n\nSag Bescheid, wenn etwas fehlt."
ok, tg = _senden(text)
zeile("drei Nachrichten: davor, der Kopiertext allein, danach",
      len(tg.texte) == 3, gemessen=f"{len(tg.texte)}: {[t.get('text', '')[:20] for t in tg.texte]}")
mitte = tg.texte[1] if len(tg.texte) > 1 else {}
zeile("der Kopiertext kommt exakt und roh — nichts davor, nichts dahinter",
      mitte.get("text") == MAIL and not mitte.get("entities"),
      gemessen=repr(mitte.get("text", "")[:60]))
zeile("die Steuerzeichen erscheinen nirgends",
      all("kopie>" not in t.get("text", "") for t in tg.texte))

ok, tg = _senden(text, tts=True)
zeile("mit Sprachausgabe: der Kopiertext ist eine Textnachricht, keine Stimme",
      any(t.get("text") == MAIL for t in tg.texte)
      and all(MAIL not in (s.get("caption") or "") for s in tg.stimmen),
      gemessen=f"Texte {[t.get('text', '')[:15] for t in tg.texte]}")
zeile("und er wird nicht vorgelesen",
      all("vielen Dank" not in g for g in _GESPROCHEN),
      gemessen=str([g[:30] for g in _GESPROCHEN]))

# ── D. Die Öffnung erreicht den Freigabedialog nicht ───────────────────────
print("== D. Freigabedialog bleibt ohne Vorschau ==")


async def _dialog():
    tg = _Telegram()
    s = bot.UserSession(client=None, user_id=1, chat_id=1)
    s.bot = tg
    bot.SESSIONS[bot.faden(1, None)] = s
    rr = bot.make_permission_callback(1, None)
    t = asyncio.create_task(rr("WebFetch", {"url": "https://fremd.example/x?y=1"}, None))
    for _ in range(200):
        if tg.texte:
            break
        await asyncio.sleep(0.01)
    for _rid, (lp, fut) in list(s.pending_permissions.items()):
        lp.call_soon_threadsafe(fut.set_result, "deny")
    await t
    return tg


tg = asyncio.run(_dialog())
zeile("der Dialog setzt keine Vorschau — die Voreinstellung (aus) gilt dort",
      tg.texte and "link_preview_options" not in tg.texte[0]
      and not tg.texte[0].get("entities"),
      gemessen=str(sorted(tg.texte[0].keys())) if tg.texte else "kein Dialog")
bauplan = bot.anwendungs_bauplan()
_d = getattr(bauplan, "_defaults", None)
zeile("und die programmweite Voreinstellung ist unverändert aus",
      _d is not None and _d.link_preview_options.is_disabled is True,
      gemessen=str(getattr(_d, "link_preview_options", None)))

# ── F. Textbloecke eines Zugs (26.09., Engywucks Befund 2) ─────────────────
# Echter `stream_response`, Attrappe nur am Rand (der SDK-Client liefert zwei
# Textbloecke mit einem Werkzeugaufruf dazwischen — so kam Claudias 13:47).
print("== F. Absatz zwischen Textblöcken ==")
from claude_agent_sdk import AssistantMessage, TextBlock, ToolUseBlock  # noqa: E402


class _Client:
    async def receive_response(self):
        yield AssistantMessage(content=[TextBlock(text="Ich prüfe, ob es bearbeitet wurde.")],
                               model="x")
        yield AssistantMessage(content=[ToolUseBlock(id="t1", name="Read", input={})], model="x")
        yield AssistantMessage(content=[TextBlock(text="**Neustart um 13:44 Uhr**")], model="x")


_s = _sitzung(_Telegram())
_s.client = _Client()
_s.quiet = True
try:
    _text = asyncio.run(bot.stream_response(_s, 1)) or ""
except Exception as e:
    _text = f"(Pfad warf {type(e).__name__}: {e})"
zeile("zwei Textblöcke kommen mit Absatz, nicht aneinandergeklebt",
      "wurde.\n\n**Neustart" in _text, gemessen=repr(_text[:80]))
import ast as _ast                                              # noqa: E402
_baum = _ast.parse(Path(bot.__file__).read_text(encoding="utf-8"))
_kleber = [n.lineno for n in _ast.walk(_baum)
           if isinstance(n, _ast.Call) and isinstance(n.func, _ast.Attribute)
           and n.func.attr == "join" and isinstance(n.func.value, _ast.Constant)
           and n.func.value.value == "" and n.args and isinstance(n.args[0], _ast.Name)
           and n.args[0].id in ("parts", "teile")]
zeile("keine Sammelstelle klebt Blöcke mehr mit leerem Trenner (alle Geschwister)",
      not _kleber, gemessen=str(_kleber))

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen der Darstellung bestanden.")
