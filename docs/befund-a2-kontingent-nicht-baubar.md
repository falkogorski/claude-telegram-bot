<!-- ROLLE: befund-a2-kontingent -->
# Befund A2: Die Kontingent-Frühwarnung ist mit dem Abo-Token nicht baubar

**Stichtag:** 2026-08-20 · **überholt durch:** — · **maßgeblich ist diese
Datei** · **Auftrag:** Claudia, 20.08. („Schritt 1 ist der Probeaufruf;
scheitert er, endet der Auftrag als *nicht baubar*")

## Das Ergebnis

**Der Probeaufruf ist gescheitert — und zwar sauber und wiederholbar.** Damit
tritt genau der Ausgang ein, den der Auftrag vorgesehen hat. Das ist ein
gültiges Ergebnis, kein Fehlschlag.

## Was probiert wurde und woran es scheitert

Der undokumentierte Endpunkt `GET https://api.anthropic.com/api/oauth/usage`,
aufgerufen **in der echten Bot-Umgebung** auf dem VPS (via `systemd-run` mit
der geschützten `EnvironmentFile`, damit das Token nie über eine Kommandozeile
läuft), in drei Kopfzeilen-Varianten:

| Variante | Ergebnis |
|---|---|
| nur `Authorization: Bearer …` | **HTTP 403** |
| Bearer + `anthropic-beta: oauth-2025-04-20` | **HTTP 403** |
| Bearer + `anthropic-version: 2023-06-01` | **HTTP 403** |

**Die Zahl ist die Diagnose.** Nicht 404 — der Endpunkt existiert. Nicht 401 —
das Token wird erkannt. **403 heißt: erkannt und nicht berechtigt.**

**Warum, und das ist die eigentliche Erkenntnis:** Der Bot läuft mit einem
**Setup-Token** (`sk-ant-oat…`, aus `claude setup-token`), wie es die
Kostenregel verlangt. Der Endpunkt ist offenbar für das **Sitzungs-Token**
gedacht, das `claude login` im interaktiven Gebrauch erzeugt. Beide sind
Abo-Zugänge, aber nicht derselbe Zugang. Gegengeprüft: Auf dem VPS liegt keine
`~/.claude/.credentials.json`, und `ANTHROPIC_API_KEY` ist **nicht** gesetzt —
die Kostenregel hält unverändert.

## Welche Wege noch offen sind

**Weil ein gescheiterter Weg keine Unmöglichkeit beweist** — die Regel verlangt
den dritten Teil der Diagnose:

1. **Ein Sitzungs-Token per `claude login` auf dem VPS hinterlegen.** Technisch
   der naheliegende Weg. **Ich empfehle ihn nicht:** Er schafft eine **zweite
   Stelle mit einem Kontozugang**, die gepflegt, erneuert und geschützt werden
   muss — genau das, was Claudias Messung beim Wecker ausdrücklich vermeiden
   wollte. Der Gewinn wäre eine Warnung bei 80 statt 97 Prozent; der Preis eine
   dauerhaft größere Angriffsfläche. **Das ist Adams Entscheidung, nicht meine**
   — sie gehört ins Freigabe-Postfach, nicht in einen Bau.
2. **Ein lokaler Zähler im Bot.** Von Adam am 20.08. um 09:57 abgelehnt, und
   die Begründung trägt: Er sieht nicht, was am Desktop oder im Browser
   verbraucht wird.
3. **Die bestehende Anbieter-Warnung.** Bleibt unangetastet und ist damit
   weiterhin die einzige Quelle — mit ihrer bekannten Schwäche: **ein**
   Warnzustand, dessen Zeitpunkt der Anbieter bestimmt.

## Was trotzdem im Repo bleibt

[`scripts/kontingent.py`](../scripts/kontingent.py) — **gebaut, aber nirgends
eingebunden.** Kein Zeitgeber, kein Aufruf aus dem Bot, keine Schwellenlogik.

**Warum nicht gelöscht:** Sollte der Zugang je verfügbar sein (Adams Entscheid
zu Weg 1, oder ein offizieller Endpunkt), ist der Abrufer samt Token-Schutz,
Formprüfung und Ausfall-Schwelle fertig. Der Aufwand, ihn zu behalten, ist
null; ihn zu wiederholen wäre eine Stunde.

**Damit er keine Falsch-Wahrheit wird**, trägt sein Kopf den Vermerk, und diese
Datei ist die maßgebliche Auskunft: **A2 ist nicht in Betrieb.**

## Die Lehre

**Die Sollbruchstelle hat sich gezeigt, bevor sie eingebaut war.** Der Auftrag
nannte den versionierten Beta-Header als Risiko — „ändert Anthropic die
Schnittstelle, verstummt der Abrufer". Eingetreten ist die Vorstufe davon: Sie
gibt uns von vornherein nichts. **Ein undokumentierter Endpunkt ist kein Weg,
sondern eine Wette**, und diese hier ist verloren, bevor Aufwand hineingeflossen
ist — das ist der günstigste Zeitpunkt.
