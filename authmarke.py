# <!-- ROLLE: anmelde-marke -->
"""Die Anmelde-Marke — eine Quelle für zwei Leser.

**Warum es dieses winzige Modul gibt (G1, 25.07.2026):** Die Stundenblumen
suchten im Journal nach Wortlauten, die ich für den Bruch der Anmeldung hielt.
`bot.py` kannte längst eine eigene, **aus echten Vorfällen gewachsene** Liste.
Von sieben Marken war genau **eine** in beiden Listen — und der wichtigste Fall
ging knapp daneben: Ich suchte `oauth token expired`, gesehen hatten wir
`oauth token **has** expired`. Ein Wort dazwischen, und der Wächter wäre an dem
einen Fall vorbeigelaufen, für den er gebaut wurde.

**Zwei Lehren, und die zweite ist die wichtigere:**

1. **Zwei Listen driften.** Deshalb steht die Liste jetzt **hier**, und beide
   Seiten importieren sie. Das ist stärker als ein Test, der die Listen
   vergleicht: Ein Test hätte den Drift gemeldet, diese Struktur lässt ihn
   nicht entstehen.
2. **Auf einen fremden Wortlaut zu horchen, ist ohnehin der schwächere Weg.**
   Der Bot **weiß** im Augenblick des Bruchs Bescheid — er behandelt ihn ja.
   Also schreibt er eine **Marke**, und der Wächter liest sie: deterministisch,
   im eigenen Format, ohne Journal-Rechte, und vollkommen gleichgültig
   dagegen, wie der Anbieter seine Fehlermeldung morgen formuliert.

Die Journal-Suche bleibt als **zweites Netz** — für den Fall, dass der Bot so
früh oder so hart scheitert, dass er zum Schreiben nicht mehr kommt.

**Kein Geheimnis in der Marke.** Sie enthält Zeitpunkt und eine kurze,
gesäuberte Ursache — nie den Wortlaut einer Fehlermeldung im Ganzen, weil dort
Zugangsdaten mitlaufen könnten.
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path

# Aus echten Vorfällen gewachsen (vormals `is_auth_error` in bot.py). Wer hier
# etwas ergänzt, versorgt damit automatisch beide Leser.
NADELN = (
    "401",
    "invalid authentication",
    "invalid x-api-key",
    "authentication_error",
    "failed to authenticate",
    "could not resolve authentication",
    "oauth token has expired",
    # Ergänzungen 25.07. — plausible Schreibweisen desselben Falls. Bewusst
    # großzügig: Ein übersehener Anmelde-Bruch kostet vierzehn Tage Stille,
    # ein Fehlalarm eine Nachricht.
    "oauth token expired",
    "invalid api key",
    "invalid_api_key",
    "please run /login",
    "credentials are no longer valid",
)

MARKE = Path(os.environ.get("AUTH_MARKE")
             or (Path.home() / ".claude" / "anmeldung-gekippt"))

# Was aus einer Ursache herausfliegt, bevor sie abgelegt wird: alles, was nach
# einem Schlüssel aussieht. Die Marke soll erklären, nicht ausplaudern.
_SCHLUESSEL = re.compile(r"(sk-[A-Za-z0-9_\-]{6,}|[A-Za-z0-9_\-]{40,})")


def passt(text: str) -> bool:
    """Sieht dieser Text nach einem Anmelde-Bruch aus?"""
    t = (text or "").lower()
    return any(n in t for n in NADELN)


def setzen(ursache: str = "") -> None:
    """Der Bot ruft das im Augenblick des Bruchs — er weiß es dann bereits."""
    try:
        MARKE.parent.mkdir(parents=True, exist_ok=True)
        kurz = _SCHLUESSEL.sub("«…»", str(ursache or "")[:300])
        tmp = MARKE.with_suffix(".tmp")
        tmp.write_text(json.dumps(
            {"zeit": time.time(),
             "menschlich": time.strftime("%Y-%m-%d %H:%M:%S"),
             "ursache": kurz}, ensure_ascii=False), encoding="utf-8")
        tmp.replace(MARKE)
    except Exception:
        pass                       # eine Marke, die nicht geht, darf nichts brechen


def loeschen() -> None:
    """Nach einem gelungenen Lauf — die Anmeldung trägt wieder."""
    try:
        MARKE.unlink()
    except OSError:
        pass


def gesetzt() -> dict | None:
    """Für den Wächter: liegt eine Marke, und seit wann?"""
    try:
        return json.loads(MARKE.read_text(encoding="utf-8"))
    except Exception:
        return None
