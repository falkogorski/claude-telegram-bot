> **An Adam, zur Weitergabe an Mick** · Engywuck · 09.09.2026, 19:52 · geprüft: `2206efe`, `23d01d6:bot.py` (`_nachsteuer_hook`), SDK 0.2.127 `_internal/query.py`

# Deploy 23d01d6: abgenommen. Schritt 3 beweist weniger, als der Bericht sagt.

**Schritt 0 bis 2: abgenommen.** Der Stand vorher ist aus dem merge-Kopf abgelesen (`0270fd7`, Micks Angabe war richtig, meine `e335c23` falsch). Der Regressionslauf ist grün mit der erwarteten Übersprungenen. `2206efe` setzt den Rückweg-Grundsatz vollständig und richtig um, Prüfzeile am Rückgabewert inklusive.

**Schritt 3: die Aussage „das SDK schluckt die leere Hook-Antwort" ist nicht gemessen.** Zwei Gründe, beide am Code:

- Der Hook **schreibt auf dem leeren Pfad keine Zeile** (`_nachsteuer_hook`: `if not text: return {}`, die Log-Zeile kommt erst danach). „Keine Hook-Zeile im Protokoll" ist also der Normalfall, ob der Hook lief oder nicht.
- Wirft der Hook eine Ausnahme, **loggt das SDK nichts**: `query.py:534` fängt sie und schickt eine Fehlerantwort an die CLI, ohne Python-seitige Protokollzeile. Auch dann stünde in bot.err.log nichts. Und die CLI führt nach einem Hook-Fehler das Werkzeug trotzdem aus; die Antwort des Bots beweist daher ebenfalls nichts über den Hook.

Was der Deploy tatsächlich bewiesen hat: Der Bau der Optionen mit `hooks=` bricht die Sitzung nicht, und ein Werkzeuglauf kommt durch. Das ist das Wichtigste und es reicht für heute. Aber das benannte Risiko ist **offen, nicht erledigt**.

**Der Beweis kommt mit Block 1b von selbst, und gehört als Prüfzeile in dessen Deploy-Block:** Adam schickt eine Nachricht, während ein Auftrag mit Werkzeuglauf läuft. Dann muss im Protokoll stehen:

```
Nachsteuern: N Zeichen an den laufenden Auftrag gereicht (Zimmer haupt)
```

und die Antwort muss den Nachtrag erkennbar berücksichtigen. Erst diese Zeile misst den Hook durch das SDK, in beide Richtungen. Bis dahin steht das Risiko als Risiko in Micks Bericht, nicht als erledigt.

**Nebenbefund, bestätigt:** `Kontingent-Ereignis: art=five_hour status=allowed reset=1788990600` ist die neue Zeile aus `86be8f0`; der Reset-Wert ist 23:50 heute. M-7 ist damit messbar, die Signatur bleibt `status=rejected`.
