#!/usr/bin/env python3
"""Die Fehlererkennung liest auch die Nutzlast — nicht nur die Meldung.

**Gemessen im Probelauf-Klon fuer den SDK-Sprung (29.08.).** Ab
`claude-agent-sdk` 0.2.140 wirft das SDK `ResultError` mit strukturierter
Nutzlast, ausdruecklich damit Aufrufer *ohne String-Matching* verzweigen
koennen. Wir verzweigen aber ueber genau das — und ein Zugangsfehler, dessen
Text nur in `data` steht, waere unerkannt geblieben.

**Im Regressionslauf waere das nie rot geworden**, weil dort keine echte
SDK-Ausnahme entsteht. Deshalb dieser Pruefer: Er baut die Ausnahmeformen
selbst nach — mit dem echten `ResultError`, wenn das SDK ihn kennt, sonst mit
einer gleich geformten Attrappe. So laeuft er mit alter UND neuer Fassung.
"""
import os
import sys
from pathlib import Path

os.environ["TELEGRAM_BOT_TOKEN"] = "0:pruefstand"
os.environ["ALLOWED_USER_IDS"] = "4711"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot                                                     # noqa: E402

fehler: list[str] = []


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


class _NutzlastFehler(Exception):
    """Gleiche Form wie `ResultError`, unabhaengig von der SDK-Fassung."""
    def __init__(self, meldung: str, data: dict | None = None):
        super().__init__(f"{meldung} (exit code: 1)")
        self.data = data or {}


def bauen(meldung: str, data: dict | None = None):
    """Nimmt den echten `ResultError`, wenn er da ist — sonst die Attrappe."""
    try:
        from claude_agent_sdk import ResultError
        return ResultError(meldung, data or {}, 1)
    except ImportError:
        return _NutzlastFehler(meldung, data)


print("== Fehlererkennung mit strukturierter Nutzlast ==")

# ---- Der Fall, der den Bot blind gemacht haette.
e = bauen("Command failed", {"subtype": "error",
                             "errors": ["authentication_error: invalid bearer token"]})
zeile("Zugangsfehler NUR in der Nutzlast wird erkannt", bot.is_auth_error(e),
      gemessen=f"str(e)={str(e)!r}")
zeile("…und die Meldung allein traegt ihn wirklich nicht",
      "authentication" not in str(e).lower(),
      gemessen=f"sonst waere die Zeile darueber bedeutungslos: {str(e)!r}")

# ---- Der wortlautunabhaengige Beleg — der eigentliche Gewinn.
e = bauen("Command failed", {"api_error_status": 401})
zeile("Status 401 gilt als Zugangsfehler, ohne jedes Stichwort",
      bot.is_auth_error(e))
e = bauen("Command failed", {"api_error_status": 403})
zeile("Status 403 ebenso", bot.is_auth_error(e))

# ---- Die Gegenrichtung: ein Wächter, der immer anschlägt, ist keiner.
e = bauen("Command failed", {"api_error_status": 500,
                             "errors": ["internal server error"]})
zeile("Status 500 ist KEIN Zugangsfehler", not bot.is_auth_error(e))
e = bauen("Der Nutzer schrieb: mein Passwort ist abgelaufen", {})
zeile("Nutzertext ueber abgelaufene Zugaenge loest nichts aus",
      not bot.is_auth_error(e), gemessen=str(e))

# ---- Der alte Weg muss weiter tragen (Rueckwaertsvertraeglichkeit).
zeile("nackte Ausnahme wie bisher erkannt",
      bot.is_auth_error(Exception("OAuth token expired")))
zeile("Meldung im message-Feld weiterhin erkannt",
      bot.is_auth_error(bauen("OAuth token expired", {})))
zeile("harmlose Ausnahme bleibt harmlos",
      not bot.is_auth_error(Exception("connection reset by peer")))

# ---- Kontext-Ueberlauf und Puffergrenze: dieselbe Bauform, dieselbe Luecke.
e = bauen("Command failed", {"errors": ["prompt is too long: 250000 tokens"]})
zeile("Kontext-Ueberlauf in der Nutzlast wird erkannt", bot.is_context_overflow(e))
zeile("Kontext-Ueberlauf im message-Feld weiterhin",
      bot.is_context_overflow(Exception("prompt is too long")))
zeile("harmlose Ausnahme ist kein Ueberlauf",
      not bot.is_context_overflow(Exception("timeout")))

e = bauen("Command failed", {"errors": ["exceeded maximum buffer size"]})
zeile("Puffergrenze in der Nutzlast wird erkannt", bot.is_transport_overflow(e))

# ---- Kein Geheimnis in den Suchtext, und das ist keine Formsache:
#      der Text wandert ueber `authmarke.setzen` in eine Datei.
e = bauen("Command failed", {"session_id": "sitzung-4711",
                             "result": "ok", "errors": ["nichts"],
                             "geheim": "sk-ant-oat01-SEHRGEHEIM"})
text = bot.fehlertext_vollstaendig(e)
zeile("unbekannte Nutzlast-Felder landen NICHT im Suchtext",
      "SEHRGEHEIM" not in text and "sitzung-4711" not in text,
      gemessen=text)

# ---- Ohne Nutzlast verhaelt sich alles wie zuvor.
zeile("ohne data-Feld bleibt der Text die Meldung",
      bot.fehlertext_vollstaendig(Exception("schlicht")) == "schlicht")

print()
if fehler:
    print(f"❌ {len(fehler)} Zeilen rot")
    for f in fehler:
        print(f"   · {f}")
    sys.exit(1)
print("✅ Alle Zeilen der SDK-Fehlererkennung bestanden")
