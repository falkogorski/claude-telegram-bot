<!-- ROLLE: fremdflaechen-inventar -->
# Fremdflächen — was das System beeinflusst und in keinem Repo steht

> **Zweck: ABLAGE** · **Zu tun:** nichts — dies ist das Gedächtnis für Orte,
> die kein Prüfer sieht.

**Angelegt 10.09.2026 auf Connis Auftrag**, nach einem Vorfall, der genau
diese Lücke zeigte.

## Was hier hineingehört

Eine **Fremdfläche** ist ein Ort außerhalb beider Repos, an dem eine Änderung
das Verhalten des Systems verändert — **ohne dass ein Regressionslauf, ein
Selbstcheck oder ein Wächter davon erfährt.** Sie ist nicht falsch und nicht
verboten; sie ist unsichtbar, und das ist das Problem.

Der Prüfstein: *Könnte jemand hier etwas ändern, ohne dass irgendein Prüfer
dieses Projekts anschlägt?* Wenn ja, gehört der Ort hier hinein.

---

## 1 · macOS-Anmeldeobjekte und Hintergrundschalter `[10.09.2026]`

**Der Ort:** Systemeinstellungen → „Allgemein" → „Anmeldeobjekte &
Erweiterungen". Dort erscheint **jeder** `LaunchAgent` aus
`~/Library/LaunchAgents` als Schalter. Für Agenten, die `/bin/bash` starten,
zeigt macOS nur **„bash"** an — ohne Angabe, wozu er gehört.

**Der Vorfall:** Adam hat die bash-Einträge deaktiviert, weil sie
undurchsichtig aussahen. Das ist eine vernünftige Vorsichtsreaktion auf eine
Anzeige, die nichts erklärt.

**Was daran gefährlich ist:** Einer dieser Schalter trägt
`com.jakuna.vps-backup` — die tägliche Sicherung des Servers auf den Mac.
Wird er abgeschaltet, **läuft kein Backup mehr, und nichts meldet es.** Der
Bot weiß davon nichts, der Tagescheck läuft auf dem Server, und die Sicherung
schweigt genauso, wenn sie nicht läuft, wie wenn sie erfolgreich ist.

### Gemessen am 10.09.2026, 22:39

**Das Backup ist NICHT ausgefallen** — und das ist eine Berichtigung, keine
Bestätigung:

| Frage | Ergebnis |
|---|---|
| `com.jakuna.vps-backup` geladen? | ja, Status 0 |
| heute gelaufen? | **zweimal** — 12:30:05 und 22:35:38, je 182 MB |
| Lücke in den Tagen davor? | **keine** — 01.09. bis 09.09. je ein Lauf |
| frische Dateien in `latest/`? | 17 vom 10.09. |

Der Ordner `latest/` trägt selbst den 07.09. als Zeitstempel — **das ist kein
Befund:** Der mtime eines Ordners ändert sich nur, wenn Einträge auf seiner
obersten Ebene dazukommen, nicht wenn Dateien darin neu geschrieben werden.
Wer nur darauf sieht, hält ein laufendes Backup für tot.

**Die Gefahr war real, eingetreten ist sie nicht.** Beides gehört in denselben
Satz, sonst wird aus einer Vorsichtsmaßnahme rückwirkend ein Beinahe-Unfall,
den es nicht gab.

### Der zweite bash-Agent — und es war keiner der beiden vermuteten

Gesucht war `icloud-spiegel-bot` (am 29.08. ausgetragen) oder `mirror-ki`
(seit Mai tot). Beide lagen bereits in `_deaktiviert/`. Der Schalter kam von
einem **dritten**: `com.jakuna.mirror-ki-reboot-test` — ein Einmal-Testskript
vom 25.05., das beim Anmelden startet. Beim Austragen von `mirror-ki` am 29.08.
ist es übrig geblieben, weil es einen eigenen Namen trägt.

Seine Logdateien sind seit dem 25.05. **leer und unverändert**: Es lief, tat
nichts (Marker-Datei), und niemand sah hin.

**Ausgetragen am 10.09.2026:** `launchctl bootout` (rc=0), dann nach
`_deaktiviert/com.jakuna.mirror-ki-reboot-test.plist.ausgetragen-2026-09-10`
— dieselbe Form wie am 29.08. **Damit ist `com.jakuna.vps-backup` der einzige
verbliebene bash-Agent**, und der Schalter in Adams Einstellungen hat nur noch
eine Bedeutung.

### Die Lehre, die über den Fall hinausgeht

**Ein Name, der nichts sagt, wird abgeschaltet.** Das ist kein Fehler des
Menschen, sondern eine Eigenschaft der Anzeige. Daraus zwei Griffe:

- **Beim Anlegen eines LaunchAgents mitfragen: Wie heißt er in den
  Einstellungen?** Ein Agent, der dort als nacktes „bash" erscheint, ist ein
  Kandidat fürs Abschalten.
- **Beim Austragen einer Automatik alle Geschwister suchen**, nicht nur den
  Hauptnamen. `mirror-ki` wurde ausgetragen, `mirror-ki-reboot-test` blieb —
  dieselbe Klasse wie die Geschwister-Regel im Code.

### Nebenbefund, nicht beauftragt

`launchctl list` zeigt zwei Agenten mit Fehlerstatus:
`com.jakuna.sort-downloads` (**78**) und `com.jakuna.claude-remote-hub`
(**1**). Beide sind nicht Teil dieses Projekts; der Status sagt nur, dass ihr
letzter Lauf so endete. **Hier notiert, nicht angefasst** — wer fremde
Automatik ohne Auftrag repariert, verändert etwas, das ein anderer gebaut hat.

---

## Noch aufzunehmen

- Das **Gedächtnis** (`~/.claude/memory/`): außerhalb beider Repos, ohne
  Versionierung, ohne Prüfer (siehe `docs/befund-offene-verhaltensregeln.md`).
- **iCloud-Ordner** als Weg für Auftragspapiere: unterliegt dem
  macOS-Datenschutz und war am 28.08. für Werkzeuge gesperrt.
- **`~/.claude/settings.json`**: Seit dem 10.09. lädt der Empfang sie nicht
  mehr (`setting_sources=[]`) — der Hauptstrom aber sehr wohl.
