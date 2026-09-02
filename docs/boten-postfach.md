<!-- ROLLE: boten-postfach -->
# Boten-Postfach — Nachrichten/Dateien über den Bot versenden (B)

**Zweck:** Andere Instanzen (Bot-Sitzung, Kontrollsitzung, Skripte) sollen etwas
über den Telegram-Bot zustellen können, **ohne den Bot-Token zu kennen**. Der
Bot hält den Token; die Instanz legt nur einen Auftrag in einem Ordner ab.

**Ordner (VPS):** `~/postfach/` (überschreibbar per `POSTFACH_DIR`)
- `outbox/` — hier Aufträge ablegen
- `sent/` — erfolgreich zugestellt (+ ggf. `.note`)
- `failed/` — fehlgeschlagen (+ `.note` mit Grund)

## Auftrags-Format (eine `*.json`-Datei in `outbox/`)

```json
{
  "target_chat_id": 304455165,
  "thread_id": null,
  "text": "Optionaler Nachrichtentext",
  "file": "/absoluter/pfad/zur/datei.pdf",
  "caption": "Optionale Bildunterschrift für die Datei"
}
```
- **`target_chat_id`** (Pflicht): Zielchat. **Allowlist:** nur Adam
  (`ALLOWED_USER_IDS`), der Ausgabekanal oder ein registriertes Haus (Phase 6).
  Andere Ziele → `failed/`.
- **`thread_id`** (optional): Forum-Topic (Zimmer).
- **`text`** und/oder **`file`** (mindestens eins): Text und/oder Datei.
- **`caption`** (optional): nur bei `file`.

## Ablegen — der vorgeschriebene Weg `[GEÄNDERT 02.09.2026, U-3]`

**Benutze das Skript, nicht die Shell-Form:**

```bash
python3 scripts/postfach_ablegen.py --chat 304455165 --text "Hallo aus dem Postfach"
python3 scripts/postfach_ablegen.py --chat 304455165 --datei /pfad/bericht.pdf --beschriftung "Der Bericht"
```

**Warum es das Skript gibt, und es ist kein Komfort-Grund:** Claudia hat am
02.09. gemessen, dass **27 Freigabe-Dialoge** anfielen — praktisch alle davon
Postfach-Aufträge in genau der Shell-Form, die dieses Dokument bis heute
vorschrieb. Die Form trifft **vier** Schranken auf einmal: die Ersetzung
(`$HOME`, `$(date …)`), die **Zuweisung** (`tmp=` — Boden-Bedingung), den
**Zeilenumbruch** (Heredoc) und die Umlenkung.

Eine Positivliste harmloser Ersetzungen hätte nur die erste geöffnet und drei
stehen lassen. Der tragfähige Weg ist der ältere Grundsatz aus
`scripts/bash_dialog_auswertung.py`: **Wiederkehrende gleichartige Dialoge
werden durch benannte, geprüfte Skripte ersetzt, die einzeln in die
Positivliste rücken — nie durch Öffnen einer Klasse.**

Das Skript läuft ohne Rückfrage, weil es in `bashfreigabe.BENANNTE_SKRIPTE`
steht. Es respektiert `POSTFACH_DIR`, ist deterministisch, ruft kein Modell und
geht nicht ins Netz.

### Was das Skript tut (die Shell-Form, zur Erklärung — nicht zum Nachbauen)

Erst unter Temp-Namen schreiben, dann nach `*.json` umbenennen — sonst greift der
Bot eine halb geschriebene Datei:
```bash
tmp="$HOME/postfach/outbox/.$(date +%s%N).tmp"
cat > "$tmp" <<'JSON'
{ "target_chat_id": 304455165, "text": "Hallo aus dem Postfach" }
JSON
mv "$tmp" "$HOME/postfach/outbox/$(date +%s%N).json"
```
**Diese Form ist weiterhin gültig und wird weiterhin dialogpflichtig sein.** Sie
steht hier, damit nachvollziehbar bleibt, was das Skript macht — nicht als
zweiter Weg daneben.

## Sicherheit

- Der Bot versendet **keine Geheimnis-Dateien** (`.env`, credentials,
  token/secret/key …) — solche Aufträge landen in `failed/`.
- Ziel-Allowlist verhindert Versand an fremde Chats.
- Der Bot verarbeitet `outbox/` alle ~15 s (Hintergrund-Task `postfach`).

## Eingangs-Richtung (später)

Die Umkehrung (Repo-Inbox → Zustellung in bestimmte Topics, „Instanzen-Postfach"
/ Jakuna-San-Pins) ist als Phase-6-Merker bei 6.1 notiert und wird dort gebaut.
