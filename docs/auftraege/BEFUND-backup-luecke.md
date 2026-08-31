<!-- ROLLE: befund-backup-luecke -->
# Befund: Die Backup-Pfadliste ist eine Aufzählung — 25 Ablagen fallen heraus

**Kopf:** 31.08.2026, 09:58 (Systemuhr abgelesen) · Kontroll-Sitzung · gemessen an `717b059`
**Anlass:** Micks Fund, dass die vier Hora-Zahlen nicht rekonstruierbar sind
**Rang: A** — Datenverlust bei Serverausfall, und er sähe wie Ruhe aus

---

## Micks Befund trägt — und über den zweiten Weg ist er größer

Er hat gemessen, dass `log_sync.sh` nur Gespräche und Ausarbeitungen sichert.
**Richtig, aber das ist der Log-Abgleich, nicht das Backup.** Nach der Regel
*„ein gescheiterter Weg beweist keine Unmöglichkeit"* habe ich den zweiten Weg
geprüft: `scripts/vps_backup.sh`, Zeilen 50–57.

**Die Liste sichert unter `~` genau vier Dinge:**

```
/home/claudebot/.claude/memory/
/home/claudebot/.claude/ampel_rules.toml
/home/claudebot/.claude/ampel_custom.json
/home/claudebot/claude-telegram-bot/logs/
```

(dazu `/etc/claude-telegram-bot.env`, die Token-Marke, searxng- und
litellm-Konfiguration — die sind nicht das Thema.)

**Gemessen über alle Produktivmodule: 25 von 27 beschriebenen Ablagen unter `~`
liegen außerhalb.**

| ❌ nicht gesichert | wessen Zustand |
|---|---|
| `~/.claude/auftragsbuch` · `~/.claude/hora` | **Das Auftragsbuch und Horas Protokoll** — Micks Anlass |
| `~/postfach` · `~/postfach/freigaben` | **Boten-Postfach und Freigaben** (9.4) |
| `~/notes/telegram-notes.md` | **Adams persönliche Notizen** |
| `~/.config/claude-telegram-bot` | **Adams Voreinstellungen** (`prefs.json`, `usage.json`) |
| `~/.claude/gegenleser` · `~/.claude/erinnerungen` · `~/.claude/link-inbox` · `~/.claude/stundenblumen` · `~/.claude/updater` · `~/.claude/wachposten` · `~/.claude/kontingent-sitzung` | sieben Module, gebaut seit dem 25.07. |
| `~/.claude/limit-stand.json` · `limit-gemeldet.json` · `bot-heartbeat.txt` · `zustellung-gestoert` · `anmeldung-gekippt` · `websuche-verlauf.json` | Zustandsdateien der Wächter |

---

## Die Ursache ist die Mengen-Regel, wieder

**Die Liste ist eine Aufzählung, kein Satz mit Zugehörigkeitsregel.** Sie war am
Tag ihrer Entstehung vollständig. **Jedes Modul, das seither gebaut wurde,
schreibt nach `~/.claude/<name>/` und fällt heraus** — ohne dass irgendwo etwas
rot wird.

Das ist exakt das Muster, das dieses Projekt inzwischen fünfmal gefunden hat:
die Sieben-Modul-Liste im Register-Prüfer, `glob("test_*.py")` im
Umgebungs-Prüfer, `scripts/*.sh` im Zielumgebungs-Prüfer, die Idiom-Menge im
Differenzmesser. **Hier ist es dieselbe Krankheit an der Stelle, die den
Rückweg tragen soll.**

**Und sie sieht wie Ruhe aus:** Das Backup läuft täglich, meldet Erfolg, und der
Erfolg ist wahr — für das, was in der Liste steht.

---

## Was zu tun ist — und was ausdrücklich nicht

**Der Fix ist eine Menge statt einer Aufzählung:** `/home/claudebot/.claude/`
und `/home/claudebot/postfach/` als Ganzes, plus `~/.config/claude-telegram-bot`
und `~/notes/`. **Mit ausdrücklichen Ausschlüssen statt Einschlüssen** — und die
Reihenfolge der rsync-Regeln ist dabei die Funktion, nicht die Form; das steht
seit dem 25.07. im Register, als 146 KB Sitzungskontext ins Log-Repo wanderten,
weil Ausschlüsse hinter Einschlüssen standen.

**Vor dem Bau zu klären, und deshalb geht es an Adam, nicht an Mick:**

1. **Wie groß wird das Backup?** `~/.claude/projects/` kann Sitzungsprotokolle
   in Gigabyte-Größe enthalten. 💰 **Speicher- und Traffic-Kosten sind eine
   Kostenquelle** — die Warnpflicht gilt, und „unklar" gilt als ja. **Erst
   messen, was die Ordner wiegen, dann entscheiden.**
2. **Geheimnisse.** Unter `~/.claude/` und `~/postfach/` können Token, Kennwörter
   und fremde Daten liegen. Ein Backup, das alles einsammelt, sammelt auch das
   ein — **wohin geht es, und wer kann es lesen?**
3. **Adams Notizen und Gesprächsprotokolle** sind das Privateste im System. Ob
   sie ins Backup gehören, ist seine Entscheidung, nicht unsere.

**Was NICHT getan wird:** kein Blind-Erweitern der Liste um die 25 Namen. Das
wäre dieselbe Aufzählung, nur länger — und in vier Wochen fehlte Nummer 26.

**Und ein Wächter gehört diesmal wirklich dazu**, aber ein vorhandener: Die
Selbstcheck-Zeile „Register-Vollständigkeit" prüft bereits Module gegen das
Register. **Die Frage, die niemand stellt, ist: schreibt dieses Modul Zustand,
und liegt der im Backup?** Das ist eine Erweiterung einer bestehenden Prüfung,
kein dritter Orden — aber erst nach dem Fix und erst nach Adams Entscheid zu 1–3.

---

## Einordnung

**Rang A.** Nicht weil heute etwas kaputt ist — das Backup läuft und tut, was in
seiner Liste steht. Sondern weil **der Rückweg schmaler ist, als jeder glaubt,
der die Zeile „tägliches Backup verifiziert" liest.** Punkt 4.1 steht im
Drehbuch auf VERIFIZIERT; verifiziert wurde die Liste, nicht ihre
Vollständigkeit.

**Das ist keine Kritik an der Verifizierung von damals.** Sie war richtig. Der
Fehler ist, dass eine Aufzählung altert und niemand es bemerkt.
