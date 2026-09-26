#!/usr/bin/env python3
# <!-- ROLLE: test-sendeweg -->
"""Der eine Ausgang — **ausgeführt**, nicht gelesen (Block 2b, 26.09.2026).

Claudias Auftrag *Ein Ausgang für alles* (24.09.) in Engywucks Bauform
(Zettel 25.09., Teil 2): eine Unterklasse des Bot-Objekts, durch die jede
Nachricht an Adam läuft. Gemessen wird:

  1. Die Anwendung SENDET über den Ausgang, und es gibt kein zweites
     Bot-Objekt daneben (Mengen-Zeile über den Syntaxbaum).
  2. Je Angabe das richtige Verhalten — sanft auszeichnen, ausdrücklich roh,
     mitgebrachte Auszeichnung, alte Angabe — und der Rückfall.
  3. Kein Inhalt geht verloren (spitze Klammern, Unterstriche, Sterne).
  4. Kein verdeckter Verweis in Bot-eigenem Text.
  5. Auftrag E: der Selbsttext mit allem Heiklen; Stimme ohne Auszeichnung;
     Kopiertext unverändert.
  6. Auftrag G: bei Sprachausgabe wird der Text nach Leseregeln geschnitten.
  7. Die alten Angaben werden weniger, nicht mehr (Sperrklinke).

Echter Code in der Mitte (`AusgangBot`, `auszeichnung`, `send_chunked`,
`send_answer_to_user`); Attrappen nur am Rand: Telegrams Netzaufruf und die
Stimmerzeugung.
"""
import ast
import asyncio
import datetime as _dt
import io
import os
import sys
import tempfile
import types
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="sendeweg-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "1"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["QUESTIONS_FILE"] = str(_TMP / "open_questions.json")
os.environ["PENDING_DIR"] = str(_TMP / "pending")
os.environ["CONVERSATION_LOG_DIR"] = str(_TMP / "conversations")
os.environ["TTS_BACKEND"] = "edge"
os.environ.pop("AZURE_SPEECH_KEY", None)


class _Stimme:
    def __init__(self, text, stimme):
        pass

    async def save(self, pfad):
        Path(pfad).write_bytes(b"ID3")


sys.modules["edge_tts"] = types.SimpleNamespace(Communicate=_Stimme)
WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
from telegram import Chat, Message                              # noqa: E402
from telegram.error import BadRequest                           # noqa: E402
from telegram.ext import ExtBot                                 # noqa: E402
from telegram._utils.defaultvalue import DefaultValue           # noqa: E402
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


# ── Der Rand: Telegrams Netzaufruf, an der Elternklasse ersetzt ─────────────
class _Nachricht:
    def __init__(self, mid):
        self.message_id = mid


class _Rand:
    rufe: list = []
    lehnt: str = ""       # "entities" | "angabe" | "unveraendert" | ""


def _abgelehnt(art: str, kw: dict) -> bool:
    if _Rand.lehnt == "entities":
        return bool(kw.get("entities") or kw.get("caption_entities"))
    if _Rand.lehnt == "angabe":
        pm = kw.get("parse_mode")
        return pm is not None and not isinstance(pm, DefaultValue)
    return _Rand.lehnt == "unveraendert" and art == "edit"


def _rand(art: str):
    async def aufruf(self, *args, **kw):
        for feld in ("voice", "document"):
            if hasattr(kw.get(feld), "read"):
                kw[feld + "_inhalt"] = kw[feld].read()
        _Rand.rufe.append((art, kw))
        if _abgelehnt(art, kw):
            raise BadRequest("Message is not modified" if _Rand.lehnt == "unveraendert"
                             else "Can't parse entities")
        return _Nachricht(len(_Rand.rufe))
    return aufruf


ExtBot.send_message = _rand("send")
ExtBot.edit_message_text = _rand("edit")
ExtBot.send_voice = _rand("voice")
ExtBot.send_document = _rand("document")

AUS = bot.AusgangBot(token="1:test")


def _lauf(coro, lehnt: str = ""):
    _Rand.rufe = []
    _Rand.lehnt = lehnt
    try:
        return asyncio.run(coro), None
    except Exception as e:  # ein Bruch macht die Zeile rot, nicht den Prüfer tot
        return None, e


def _arten(kw):
    return {str(e.type) for e in (kw.get("entities") or kw.get("caption_entities") or [])}


# ── 1. Die Anwendung sendet über den Ausgang ────────────────────────────────
print("== 1. Ein Ausgang, kein zweites Bot-Objekt ==")
app = bot.anwendungs_bauplan().build()
zeile("die Anwendung sendet ueber den Ausgang (Bot-Objekt ist AusgangBot)",
      isinstance(app.bot, bot.AusgangBot), gemessen=type(app.bot).__name__)
app2 = (bot.anwendungs_bauplan().base_url("http://127.0.0.1:8081/bot")
        .base_file_url("http://127.0.0.1:8081/file/bot").local_mode(True).build())
zeile("auch mit eigenem Bot-API-Server (5.34) bleibt es der Ausgang",
      isinstance(app2.bot, bot.AusgangBot), gemessen=type(app2.bot).__name__)
zeile("die Link-Vorschau bleibt programmweit aus (Voreinstellung ueberlebt)",
      app.bot.defaults is not None
      and app.bot.defaults.link_preview_options.is_disabled is True)

m = Message(message_id=7, date=_dt.datetime.now(_dt.timezone.utc),
            chat=Chat(id=1, type="private"))
m.set_bot(AUS)
_, err = _lauf(m.reply_text("**Stand** in Ordnung"))
k = _Rand.rufe[0][1] if _Rand.rufe else {}
zeile("reply_text laeuft durch denselben Ausgang (wird ausgezeichnet)",
      err is None and "bold" in _arten(k) and k.get("text") == "Stand in Ordnung",
      gemessen=f"{err!r} {k.get('text')!r} {_arten(k)}")

_ERLAUBT_ANDERSWO = {"scripts/version_monitor.py"}   # siehe Kopf von bot.AusgangBot
_BOT_BAUER = {"Bot", "ExtBot", "ApplicationBuilder"}
fremde_bauer: list[str] = []
fremde_netzwege: list[str] = []
for pfad in sorted(list(WURZEL.glob("*.py")) + list((WURZEL / "scripts").glob("*.py"))):
    rel = str(pfad.relative_to(WURZEL))
    if rel.startswith("scripts/test_"):
        continue
    src = pfad.read_text(encoding="utf-8")
    try:
        baum = ast.parse(src)
    except SyntaxError:
        continue
    for n in ast.walk(baum):
        if isinstance(n, ast.Call):
            f = n.func
            name = f.id if isinstance(f, ast.Name) else (f.attr if isinstance(f, ast.Attribute) else "")
            if name in _BOT_BAUER or (name == "builder" and isinstance(f, ast.Attribute)
                                      and getattr(f.value, "id", "") == "Application"):
                fremde_bauer.append(f"{rel}:{n.lineno} {name}")
        if (isinstance(n, ast.Constant) and isinstance(n.value, str)
                and "api.telegram.org" in n.value and "/send" in n.value
                and rel not in _ERLAUBT_ANDERSWO):
            fremde_netzwege.append(f"{rel}:{n.lineno}")
        if (isinstance(n, ast.JoinedStr) and rel not in _ERLAUBT_ANDERSWO
                and "api.telegram.org" in ast.unparse(n) and "/send" in ast.unparse(n)):
            fremde_netzwege.append(f"{rel}:{n.lineno}")
zeile("kein zweites Bot-Objekt und kein zweiter Bauplan (Syntaxbaum, alle Module)",
      not fremde_bauer, gemessen="; ".join(fremde_bauer))
zeile("kein Python-Modul sendet an Telegram vorbei (ausser benannter Ausnahme)",
      not fremde_netzwege, gemessen="; ".join(fremde_netzwege))

# ── 2. Je Angabe das richtige Verhalten, und der Rückfall ───────────────────
print("== 2. Angaben und Rückfall ==")
_lauf(AUS.send_message(chat_id=1, text="**fett** und `code_x`"))
k = _Rand.rufe[0][1]
zeile("keine Angabe: sanft ausgezeichnet (Fett, Code), ohne parse_mode",
      {"bold", "code"} <= _arten(k) and "parse_mode" not in k and k["text"] == "fett und code_x",
      gemessen=f"{k.get('text')!r} {_arten(k)}")

ROH_STATUS = "Stand:\n  • eins_a\n  • zwei - b\n\n\nEnde"
_lauf(AUS.send_message(chat_id=1, text=ROH_STATUS))
k = _Rand.rufe[0][1]
zeile("Text ohne Auszeichnung behaelt sein Bild (Einzug, Leerzeilen, Unterstrich)",
      k.get("text") == ROH_STATUS and not k.get("entities"), gemessen=repr(k.get("text")))

_lauf(AUS.send_message(chat_id=1, text="**x** und _y_", parse_mode=None))
k = _Rand.rufe[0][1]
zeile("parse_mode=None heisst ausdruecklich roh",
      k.get("text") == "**x** und _y_" and not k.get("entities"), gemessen=repr(k))

_ents = bot.auszeichnung("**a**")[1]
_lauf(AUS.send_message(chat_id=1, text="a", entities=_ents))
k = _Rand.rufe[0][1]
zeile("mitgebrachte Auszeichnung geht unveraendert durch",
      k.get("entities") == _ents and k.get("text") == "a")

_, err = _lauf(AUS.send_message(chat_id=1, text="**fett** hier"), lehnt="entities")
zeile("lehnt Telegram die Auszeichnung ab, geht derselbe Text roh hinterher",
      err is None and len(_Rand.rufe) == 2 and _Rand.rufe[1][1].get("text") == "**fett** hier"
      and _Rand.rufe[1][1].get("parse_mode") is None,
      gemessen=f"{err!r} {[r[1].get('text') for r in _Rand.rufe]}")

_, err = _lauf(AUS.send_message(chat_id=1, text="<b>A &amp; B</b>", parse_mode="HTML"),
               lehnt="angabe")
zeile("alte HTML-Angabe abgelehnt: Rohtext ohne Marken, Zeichen entschluesselt",
      err is None and len(_Rand.rufe) == 2 and _Rand.rufe[1][1].get("text") == "A & B",
      gemessen=f"{err!r} {[r[1].get('text') for r in _Rand.rufe]}")

_, err = _lauf(AUS.send_message(chat_id=1, text="*alt* fett", parse_mode="Markdown"))
zeile("alte Markdown-Angabe geht so, wie der Aufrufer sie schrieb",
      err is None and _Rand.rufe[0][1].get("parse_mode") == "Markdown"
      and _Rand.rufe[0][1].get("text") == "*alt* fett")

_, err = _lauf(AUS.edit_message_text(text="**gleich**", chat_id=1, message_id=5),
               lehnt="unveraendert")
zeile("[not modified] beim Bearbeiten: kein roher zweiter Versuch",
      isinstance(err, BadRequest) and len(_Rand.rufe) == 1,
      gemessen=f"{err!r}, {len(_Rand.rufe)} Aufrufe")

_lauf(AUS.edit_message_text(text="**neu**", chat_id=1, message_id=5))
k = _Rand.rufe[0][1]
zeile("Bearbeiten laeuft ebenfalls durch den Ausgang",
      "bold" in _arten(k) and k.get("text") == "neu", gemessen=repr(k.get("text")))

_, err = _lauf(AUS.send_voice(chat_id=1, voice=io.BytesIO(b"ID3"), caption="**Titel**"),
               lehnt="entities")
zeile("Bildunterschrift: ausgezeichnet, bei Ablehnung roh — die Stimme kommt trotzdem",
      err is None and len(_Rand.rufe) == 2 and "bold" in _arten(_Rand.rufe[0][1])
      and _Rand.rufe[1][1].get("caption") == "**Titel**"
      and _Rand.rufe[1][1].get("voice_inhalt") == b"ID3",
      gemessen=f"{err!r} {[(r[1].get('caption'), r[1].get('voice_inhalt')) for r in _Rand.rufe]}")

# ── 3. Kein Inhalt geht verloren ────────────────────────────────────────────
print("== 3. Verlustwächter ==")
for roh in ("Ordner <neu> und x<y", "__init__.py und _privat_", "<div>\nBlock\n</div>",
            "A &amp; B", "Dateien: a_b_c.md, d__e.py"):
    for sanft in (False, True):
        au = bot.auszeichnung(roh, sanft=sanft)
        klar = roh if au is None else au[0]
        zeile(f"nichts verschluckt ({'sanft' if sanft else 'Antwort'}): {roh[:28]!r}",
              not bot._inhalt_verloren(roh.replace("&amp;", "&amp;"), klar, [] if au is None else au[1])
              and all(t in klar for t in ("<neu>", "__init__", "<div>", "&amp;", "d__e")
                      if t in roh),
              gemessen=repr(klar))

_alt = bot._tgm.convert
bot._tgm.convert = lambda s, **_: (s.replace("wichtig", ""), [])
try:
    au = bot.auszeichnung("ein wichtiger **Satz**")
finally:
    bot._tgm.convert = _alt
zeile("verschluckt die Umwandlung Buchstaben, geht der Rohtext (Waechter greift)",
      au is None, gemessen=repr(au))

# ── 4. Kein verdeckter Verweis in Bot-eigenem Text ──────────────────────────
print("== 4. Sanfter Modus ==")
_lauf(AUS.send_message(chat_id=1, text="Neue Mail: [Rechnung](https://fremd.example/x)"))
k = _Rand.rufe[0][1]
zeile("Bot-eigener Text: kein Verweis mit verdeckter Adresse (Betreffzeile bleibt roh)",
      "https://fremd.example/x" in k.get("text", "") and "text_link" not in _arten(k),
      gemessen=repr(k))
_lauf(AUS.send_message(chat_id=1, text="**Befehl:** rm -rf a*b*c"))
k = _Rand.rufe[0][1]
zeile("einzelne Sterne bleiben stehen (Befehl a*b*c unverfaelscht)",
      "a*b*c" in k.get("text", "") and "bold" in _arten(k), gemessen=repr(k.get("text")))
au = bot.auszeichnung("<https://beispiel.de/a_b>", sanft=True)
zeile("ein Verweis, der seine Adresse zeigt, ist erlaubt",
      au is not None and au[0] == "https://beispiel.de/a_b", gemessen=repr(au))

# ── 5. Auftrag E: der Selbsttext ────────────────────────────────────────────
print("== 5. Selbsttext (Auftrag E) ==")
SELBST = ("## Stand der Dinge\n\n"
          "**Fett** und *kursiv* und ein [Beleg am Wort](https://beispiel.de/q?a=1&b=2).\n\n"
          "| Datei | Ort |\n|---|---|\n| mein_datei_name.md | Kunden & <Archiv> |\n\n"
          "Ein einzelner * Stern bleibt.")
au = bot.auszeichnung(SELBST)
arten = {str(e.type) for e in au[1]} if au else set()
zeile("Selbsttext wird ausgezeichnet: fett, kursiv, Verweis am Wort, Ueberschrift, Tabelle",
      au is not None and {"bold", "italic", "text_link", "pre"} <= arten, gemessen=str(arten))
zeile("Selbsttext: Unterstrich im Dateinamen, & und < im Ordner, einzelner Stern stehen",
      au is not None and all(t in au[0] for t in ("mein_datei_name.md", "Kunden & <Archiv>", " * ")),
      gemessen=repr(au[0] if au else None))
gesprochen = bot._strip_markdown_for_tts(SELBST)
zeile("die Stimme hoert keine Auszeichnungszeichen",
      not any(z in gesprochen for z in ("**", "##", "](", "|---")), gemessen=repr(gesprochen[:120]))


def _sitzung(tts=False):
    bot._USER_PREFS.setdefault("1", {})["link_vorschau"] = False
    s = bot.UserSession(client=None, user_id=1, chat_id=1)
    s.bot = AUS
    s.tts_enabled = tts
    return s


KOPIE = "cp a_b*.md /ziel/**x**/ && echo <fertig>"
ok, err = _lauf(bot.send_answer_to_user(_sitzung(), 1, f"Hier der Befehl:\n<kopie>{KOPIE}</kopie>"))
kopien = [r[1] for r in _Rand.rufe if r[1].get("text") == KOPIE]
zeile("Kopiertext geht Zeichen fuer Zeichen unveraendert, ausdruecklich roh",
      err is None and len(kopien) == 1 and kopien[0].get("parse_mode") is None
      and not kopien[0].get("entities"),
      gemessen=f"{err!r} {[r[1].get('text') for r in _Rand.rufe]}")

# Der Freigabedialog zeigt Befehle — jedes Senden und Nachziehen seiner Texte
# ist ausdruecklich roh. Mengen-Zeile: jede Funktion, die die Ansicht baut.
_baum = ast.parse((WURZEL / "bot.py").read_text(encoding="utf-8"))
ohne_roh: list[str] = []
for fn in ast.walk(_baum):
    if not isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)):
        continue
    # Die Namen, die einen Text aus der Dialogansicht tragen (`text, zeilen =
    # sammel_ansicht(...)`, `protokoll = sammel_protokoll(...) if ... else ""`).
    dialogtexte: set[str] = set()
    for a in ast.walk(fn):
        if isinstance(a, ast.Assign) and any(
                isinstance(c, ast.Call) and getattr(c.func, "id", "") in
                ("sammel_ansicht", "sammel_protokoll") for c in ast.walk(a.value)):
            for ziel in a.targets:
                erstes = ziel.elts[0] if isinstance(ziel, ast.Tuple) else ziel
                if isinstance(erstes, ast.Name):
                    dialogtexte.add(erstes.id)
    for c in ast.walk(fn):
        textarg = [k.value for k in getattr(c, "keywords", []) if k.arg == "text"]
        if (isinstance(c, ast.Call) and isinstance(c.func, ast.Attribute)
                and c.func.attr in ("send_message", "edit_message_text")
                and textarg and isinstance(textarg[0], ast.Name)
                and textarg[0].id in dialogtexte):
            pm = [k for k in c.keywords if k.arg == "parse_mode"]
            if not (pm and isinstance(pm[0].value, ast.Constant) and pm[0].value.value is None):
                ohne_roh.append(f"{fn.name}:{c.lineno}")
zeile("Freigabedialog: jedes Senden und Nachziehen ist ausdruecklich roh",
      not ohne_roh, gemessen="; ".join(ohne_roh))

# ── 6. Auftrag G: Leseregeln bei Sprachausgabe ──────────────────────────────
print("== 6. Sprachausgabe (Auftrag G) ==")
ABSATZ = ("Dies ist ein ruhiger Absatz mit etwas Inhalt, der sich gut lesen laesst. " * 6).strip()
LANG = f"## Erster Teil\n\n{ABSATZ}\n\n## Zweiter Teil\n\n{ABSATZ}\n\n**Schluss:** {ABSATZ}"
ok, err = _lauf(bot.send_answer_to_user(_sitzung(tts=True), 1, LANG))
arten_folge = [r[0] for r in _Rand.rufe]
texte = [r[1] for r in _Rand.rufe if r[0] == "send"]
stimmen = [r[1] for r in _Rand.rufe if r[0] == "voice"]
zeile("lange Antwort bei Sprachausgabe: Text zuerst als eigene Nachricht",
      err is None and arten_folge[:1] == ["send"] and len(texte) == 1
      and "Zweiter Teil" in texte[0].get("text", ""),
      gemessen=f"{err!r} {arten_folge}")
zeile("die Stimmen folgen ohne Bildunterschrift (keine Textschnipsel nach Sprechtakt)",
      len(stimmen) >= 2 and all(not s.get("caption") for s in stimmen),
      gemessen=f"{len(stimmen)} Stimmen, Unterschriften {[bool(s.get('caption')) for s in stimmen]}")

ok, err = _lauf(bot.send_answer_to_user(_sitzung(tts=True), 1, "**Kurz** gesagt: passt."))
stimmen = [r[1] for r in _Rand.rufe if r[0] == "voice"]
zeile("kurze Antwort bleibt eine Einheit: Stimme mit ausgezeichneter Unterschrift",
      err is None and [r[0] for r in _Rand.rufe] == ["voice"]
      and "bold" in _arten(stimmen[0]),
      gemessen=f"{err!r} {[r[0] for r in _Rand.rufe]}")

# ── 7. Sperrklinke: die alten Angaben werden weniger ────────────────────────
print("== 7. Sperrklinke ==")
zaehl = {"markdown": 0, "html": 0}
for c in ast.walk(_baum):
    if isinstance(c, ast.Call):
        for kw in c.keywords:
            if kw.arg == "parse_mode":
                w = ast.unparse(kw.value)
                if w in ("ParseMode.MARKDOWN", "'Markdown'"):
                    zaehl["markdown"] += 1
                elif w in ("ParseMode.HTML", "'HTML'"):
                    zaehl["html"] += 1
# Bestand am 26.09.2026. Wer eine Stelle umstellt, senkt die Zahl hier mit;
# wer eine neue alte Angabe schreibt, wird rot.
zeile("alte Markdown-Angaben: hoechstens 16 (Bestand 26.09.)",
      zaehl["markdown"] <= 16, gemessen=str(zaehl["markdown"]))
zeile("HTML-Angaben: hoechstens 7 (Bestand 26.09.)",
      zaehl["html"] <= 7, gemessen=str(zaehl["html"]))

# ── 8. Tagescheck 9q: der Abschnitt selbst (echter Abschnitt, Rand ersetzt) ──
print("== 8. Tagescheck 9q ==")
import re as _re                                                  # noqa: E402
import subprocess                                                 # noqa: E402
_dc = (WURZEL / "scripts" / "daily_check.sh").read_text(encoding="utf-8")
_m = _re.search(r"# >>> AUSGANG\n(.*?)# <<< AUSGANG", _dc, _re.S)
_abschnitt = _m.group(1) if _m else ""
zeile("Tagescheck 9q ist markiert und ruft diesen Pruefer",
      "test_sendeweg.py" in _abschnitt)


def _tagescheck(rc: int) -> str:
    # Der Rand ist der Pruefer-Aufruf: eine Attrappe statt dieses Skripts,
    # sonst riefe der Pruefer sich selbst.
    attrappe = _TMP / f"py_{rc}"
    attrappe.write_text("#!/bin/bash\n"
                        + ("echo '  ❌ Selbsttext wird ausgezeichnet'\n" if rc else "")
                        + "echo '== Ergebnis: 39/40 =='\n" + f"exit {rc}\n")
    attrappe.chmod(0o755)
    vorspann = ('set -uo pipefail\n'
                'add() { echo "ADD:$1"; }\nintern() { echo "INTERN:$1"; }\n'
                'sudo() { shift 2; "$@"; }\n'
                f'BOTDIR="{WURZEL}"\nVENVPY="{attrappe}"\nBOTHOME="$HOME"\n')
    return subprocess.run(["bash", "-c", vorspann + _abschnitt],
                          capture_output=True, text=True).stdout


_a = _tagescheck(0)
zeile("Tagescheck 9q: gruener Pruefer gibt eine gruene Zeile", "ADD:✅ Ausgang" in _a,
      gemessen=_a[-200:])
_a = _tagescheck(1)
zeile("Tagescheck 9q: roter Pruefer geht mit der roten Zeile an die Kontrolle",
      "INTERN:Ausgang: Selbsttest rot" in _a and "Selbsttext" in _a, gemessen=_a[-200:])

import shutil                                                     # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print(f"== Ergebnis: {zeilen - len(fehler)}/{zeilen} ==")
sys.exit(1 if fehler else 0)
