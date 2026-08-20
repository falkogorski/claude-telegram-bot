<!-- ROLLE: befund-a2-kontingent -->
# Befund A2: Die Kontingent-Anzeige — vier Wege zu, der fünfte stand offen

> **⚠️ BERICHTIGT AM 20.08.2026, 18:5x — der Titel dieser Datei war falsch.**
>
> Sie hieß „nicht baubar“. **Sie ist gebaut.** Der Abruf `/kontingent`
> läuft, der Prüfer `scripts/test_kontingent_a2.py` hält ihn fest.
>
> **Was ich übersehen hatte:** Die Zahl muss gar nicht abgefragt werden. Sie
> steht in den **Kopfzeilen jeder API-Antwort** und fließt ohnehin durch den
> Nachrichtenstrom, den der Bot verarbeitet:
>
> ```
> anthropic-ratelimit-unified-<fenster>-utilization
> anthropic-ratelimit-unified-<fenster>-reset
> ```
>
> Das SDK reicht sie als `RateLimitEvent` durch (`utilization`, `status`,
> `resets_at`, `rate_limit_type`) — und `bot.py` verarbeitete dieses Ereignis
> **seit F-5 bereits**. Nur lag das Merken **unter** der Statusbewertung, und
> die lässt nur Warnung und Ablehnung durch. **Jeder grüne Stand fiel
> heraus** — der Wert war die ganze Zeit im Haus und wurde weggeworfen.
>
> **Kosten: keine.** Kein Aufruf, kein zweites Token, keine neue
> Angriffsfläche — genau die Bedenken, die unten gegen den zweiten Weg
> sprechen, entfallen damit ersatzlos.
>
> **Wie der Fehler entstand, und das ist die Lehre:** Ich habe vier Wege
> geprüft, alle vier führten zu einer verschlossenen Tür, und daraus
> „nicht baubar“ gemacht. Der V-Grundsatz in `CLAUDE.md` sagt seit dem
> 25.07., dass ein gescheiterter Weg keine Unmöglichkeit beweist und dass
> ein „geht nicht“ den dritten Teil schuldet: **welche Wege noch offen
> sind.** Den hatte ich nicht geprüft. **Adam hat nicht lockergelassen** —
> „der Bot ist doch selber eine laufende Sitzung, warum kann der nicht
> fragen?“ — und genau diese Frage führte zur richtigen: **woher nimmt
> die CLI ihre Zahl?** Nicht: welchen Endpunkt rufe ich an.
>
> **Der Rest dieser Datei bleibt unverändert stehen**, weil er weiterhin
> gilt: Die vier beschriebenen Wege sind tatsächlich zu. Sie waren nur nicht
> alle.

# Befund A2: Die Kontingent-Frühwarnung ist mit dem Abo-Token nicht baubar

**Stichtag:** 2026-08-20 · **überholt durch:** die Berichtigung im Kasten oben (20.08.) · **maßgeblich ist diese
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
3. **Ein CLI-Unterbefehl** — `[GEPRÜFT 2026-08-20 abends, ebenfalls zu]`
   Naheliegend, weil die Claude-CLI den Stand in der Sitzung selbst anzeigt.
   `claude --help` kennt aber **keinen** Kontingent-Befehl: `agents`, `auth`,
   `auto-mode`, `doctor`, `gateway`, `install`, `mcp`, `plugin`, `project`,
   `setup-token` — mehr nicht. `/usage` existiert nur **innerhalb** einer
   laufenden Sitzung und ist damit nicht skriptbar.

4. **Die bestehende Anbieter-Warnung.** Bleibt unangetastet und ist damit
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
