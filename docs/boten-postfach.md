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

## Atomar ablegen (wichtig)

Erst unter Temp-Namen schreiben, dann nach `*.json` umbenennen — sonst greift der
Bot eine halb geschriebene Datei:
```bash
tmp="$HOME/postfach/outbox/.$(date +%s%N).tmp"
cat > "$tmp" <<'JSON'
{ "target_chat_id": 304455165, "text": "Hallo aus dem Postfach" }
JSON
mv "$tmp" "$HOME/postfach/outbox/$(date +%s%N).json"
```

## Sicherheit

- Der Bot versendet **keine Geheimnis-Dateien** (`.env`, credentials,
  token/secret/key …) — solche Aufträge landen in `failed/`.
- Ziel-Allowlist verhindert Versand an fremde Chats.
- Der Bot verarbeitet `outbox/` alle ~15 s (Hintergrund-Task `postfach`).

## Eingangs-Richtung (später)

Die Umkehrung (Repo-Inbox → Zustellung in bestimmte Topics, „Instanzen-Postfach"
/ Jakuna-San-Pins) ist als Phase-6-Merker bei 6.1 notiert und wird dort gebaut.
