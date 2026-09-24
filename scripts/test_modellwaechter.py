#!/usr/bin/env python3
# <!-- ROLLE: test-modellwaechter -->
"""Modellwächter — **ausgeführt** (Block 4, 24.09.2026).

Adams Entscheid vom 23.09.: umstellen von selbst, mit drei Sicherungen. Jede
hat hier eine Zeile, die nur ihr Riegel fängt:
  (1) Der Wächter schreibt nur `models.json` und meldet mit Rückweg-Knopf.
  (2) Scheitert die erste Nachricht an der NEUEN Kennung, fällt der Bot von
      selbst zurück — und NUR dann.
  (3) Kein Modellaufruf im Wächter.
Dazu: kein Hin und Her (eine zurückgenommene Kennung kommt nicht wieder), und
ein schweigender Feed ist ein Befund, kein „nichts Neues".
"""
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace

_TMP = Path(tempfile.mkdtemp(prefix="modell-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
os.environ["MODELS_FILE"] = str(_TMP / "models.json")
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
WURZEL = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))
sys.path.insert(0, str(WURZEL / "scripts"))
import modellwahl                                               # noqa: E402
import modellwaechter                                           # noqa: E402

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


def _neu():
    Path(os.environ["MODELS_FILE"]).unlink(missing_ok=True)
    out = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    if out.exists():
        for f in out.glob("*.json"):
            f.unlink()


def _post():
    out = Path(os.environ["POSTFACH_DIR"]) / "outbox"
    return [json.loads(f.read_text(encoding="utf-8")) for f in sorted(out.glob("*.json"))] \
        if out.exists() else []


# Nachgebauter Feed in der Form, die am 24.09. gemessen wurde.
FEED = """<rss><channel>
<item><title>September 22</title><pubDate>Tue, 22 Sep 2026 00:00:00 GMT</pubDate>
<description>We've launched Claude Opus 5.5 (claude-opus-5-5). Also claude-opus-5-5-fast.</description></item>
<item><title>September 1</title><pubDate>Tue, 01 Sep 2026 00:00:00 GMT</pubDate>
<description>Claude Fable 5.1 (claude-fable-5-1) and claude-mythos-5-1.</description></item>
<item><title>Aelter</title><pubDate>Mon, 01 Jun 2026 00:00:00 GMT</pubDate>
<description>claude-haiku-4-5, claude-sonnet-5, claude-opus-4-20250514</description></item>
</channel></rss>"""

print("== Modul ==")
_neu()
zeile("ohne Datei gilt die Vorgabe", modellwahl.kennung("opus") == modellwahl.VORGABE["opus"])
zeile("ein Datum ist keine Fassung (claude-opus-4-20250514 ist 4.0)",
      modellwahl.fassung("claude-opus-4-20250514") == (4, 0)
      and modellwahl.fassung("claude-haiku-4-5-20251001") == (4, 5))
zeile("eine Variante mit Anhang ist keine Kennung (…-5-5-fast)",
      "claude-opus-5-5-fast" not in modellwahl.kennungen_im_text(FEED)
      and "claude-opus-5-5" in modellwahl.kennungen_im_text(FEED))

print("== (1) Der Wächter stellt um und meldet mit Knopf ==")
_neu()
rc, aus = modellwaechter.lauf(text=FEED)
d = modellwahl.lesen()
zeile("nur die höhere Fassung wird übernommen: Fable 5 → 5.1, der Rest bleibt",
      rc == 0 and aus.startswith("UMGESTELLT") and "fable claude-fable-5 -> claude-fable-5-1" in aus
      and "opus" not in aus and "haiku" not in aus and "sonnet" not in aus, gemessen=aus)
zeile("models.json trägt neue Kennung, Rückweg und offene Probe",
      d.get("kennungen", {}).get("fable") == "claude-fable-5-1"
      and d.get("vorige", {}).get("fable") == "claude-fable-5"
      and d.get("probe_offen", {}).get("fable") == "claude-fable-5-1", gemessen=str(d))
zeile("der Bot liest ab jetzt die neue Kennung", modellwahl.kennung("fable") == "claude-fable-5-1")
post = _post()
zeile("die Meldung geht über die Botenpost, mit Rückweg-Knopf",
      len(post) == 1 and (post[0].get("knopf") or {}).get("art") == "modell_zurueck"
      and (post[0].get("knopf") or {}).get("kennung") == "fable"
      and "01 Sep 2026" in post[0].get("text", ""), gemessen=str(post)[:200])
rc, aus = modellwaechter.lauf(text=FEED)
zeile("ein zweiter Lauf ändert nichts und meldet nichts", aus.startswith("UNVERAENDERT")
      and len(_post()) == 1, gemessen=aus)

print("== (3) Kein Modellaufruf ==")
zeile("der Wächter hat keine Modell-Bibliothek geladen",
      not any(m.startswith(("claude_agent_sdk", "anthropic")) for m in sys.modules),
      gemessen=str([m for m in sys.modules if "claude" in m or "anthropic" in m]))

print("== Rückweg und kein Hin und Her ==")
res = modellwahl.zuruecknehmen("fable", "Probe")
zeile("der Rückweg stellt die vorige Kennung her",
      res == ("claude-fable-5-1", "claude-fable-5") and modellwahl.kennung("fable") == "claude-fable-5",
      gemessen=str(res))
rc, aus = modellwaechter.lauf(text=FEED)
zeile("eine zurückgenommene Kennung trägt der Wächter nicht wieder ein",
      aus.startswith("UNVERAENDERT") and modellwahl.kennung("fable") == "claude-fable-5", gemessen=aus)

print("== Schweigen ist ein Befund ==")
rc, aus = modellwaechter.lauf(text="<rss><channel>nichts</channel></rss>")
zeile("ein Feed ohne jede Kennung ist FEHLER, nicht „unverändert“",
      rc == 3 and aus.startswith("FEHLER"), gemessen=aus)
_alt = modellwaechter.abrufen
modellwaechter.abrufen = lambda url=None: (_ for _ in ()).throw(OSError("keine Verbindung"))
try:
    rc, aus = modellwaechter.lauf()
finally:
    modellwaechter.abrufen = _alt
zeile("ein gescheiterter Abruf ist FEHLER", rc == 3 and "keine Verbindung" in aus, gemessen=aus)
_neu()
rc, aus = modellwaechter.lauf(trocken=True, text=FEED)
zeile("im Trockenlauf wird nichts geschrieben und nichts gemeldet",
      "trocken" in aus and not Path(os.environ["MODELS_FILE"]).exists() and not _post(), gemessen=aus)

print("== (2) Der Rückfall im Bot ==")
import bot                                                      # noqa: E402


class _Tg:
    def __init__(self):
        self.texte = []

    async def send_message(self, **kw):
        self.texte.append(kw)


def _sitzung(voll):
    s = bot.UserSession(client=None, user_id=4711, chat_id=4711,
                        current_model="fable", modell_voll=voll)
    s.bot = _Tg()
    return s


_neu()
modellwaechter.lauf(text=FEED)          # Fable umgestellt, Probe offen
s = _sitzung("claude-fable-5-1")
ok = asyncio.run(bot._modellprobe_zurueck(s, "Connection reset by peer"))
zeile("ein fremder Fehler nimmt nichts zurück",
      ok is False and modellwahl.kennung("fable") == "claude-fable-5-1")
ok = asyncio.run(bot._modellprobe_zurueck(
    s, 'API Error: 404 {"type":"not_found_error","message":"model: claude-fable-5-1"}'))
zeile("scheitert die Probe an der neuen Kennung, geht der Bot von selbst zurück",
      ok is True and modellwahl.kennung("fable") == "claude-fable-5", gemessen=str(modellwahl.lesen()))
zeile("und sagt es Adam", s.bot.texte and "zurückgegangen" in s.bot.texte[0]["text"],
      gemessen=str(s.bot.texte)[:120])

_neu()
modellwaechter.lauf(text=FEED)
alt = _sitzung("claude-fable-5")        # eine Sitzung, die noch mit der ALTEN läuft
ok = asyncio.run(bot._modellprobe_zurueck(alt, "model not_found: claude-fable-5"))
zeile("eine Sitzung mit der alten Kennung nimmt nichts zurück",
      ok is False and modellwahl.kennung("fable") == "claude-fable-5-1")
zeile("die bestandene Probe wird vermerkt",
      modellwahl.probe_bestanden("fable", "claude-fable-5-1") and modellwahl.probe_offen("fable") is None)
ok = asyncio.run(bot._modellprobe_zurueck(_sitzung("claude-fable-5-1"),
                                           "model not_found: claude-fable-5-1"))
zeile("nach bestandener Probe fällt ein späterer Fehler nicht mehr zurück",
      ok is False and modellwahl.kennung("fable") == "claude-fable-5-1")

print("== (1) Der Rückweg-Knopf ==")
_neu()
modellwaechter.lauf(text=FEED)
bearbeitet = []


async def _antwort(*a, **k):
    return None


async def _edit(text=None, **kw):
    # Wie Telegram: Der Text darf positional kommen — der Handler tut das.
    bearbeitet.append({"text": text, **kw})

q = SimpleNamespace(data="pfk:modell_zurueck:fable", answer=_antwort,
                    message=SimpleNamespace(text="🔄 Neues Modell übernommen"),
                    edit_message_text=_edit)
upd = SimpleNamespace(callback_query=q, effective_user=SimpleNamespace(id=4711))
asyncio.run(bot.on_postfach_knopf(upd, None))
zeile("der Knopf stellt zurück — ohne Modellstart",
      modellwahl.kennung("fable") == "claude-fable-5" and bearbeitet
      and "Zurückgestellt" in bearbeitet[-1]["text"], gemessen=str(bearbeitet)[:150])
zeile("die Knopfart steht in der geschlossenen Liste der Botenpost",
      "modell_zurueck" in __import__("botenpost").KNOPF_ARTEN)

import shutil                                                   # noqa: E402
shutil.rmtree(_TMP, ignore_errors=True)
print()
if fehler:
    print(f"❌ {len(fehler)} von {zeilen} Zeilen rot: {', '.join(fehler)}")
    sys.exit(1)
print(f"✅ Alle {zeilen} Zeilen des Modellwächters bestanden.")
