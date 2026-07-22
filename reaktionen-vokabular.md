# Reaktions-Vokabular (Emoji) — verbindliche Referenz für MIGRATION.md 5.9

## Änderungshistorie

- **2026-07-20** — **v2 (Adam-Entscheid nach der Telegram-Messung).** Telegram
  erlaubt als Reaktion nur einen festen Satz von 73 Emoji (`scripts/tg_reactions.txt`);
  16 der 27 v1-Einträge waren nicht darunter. Adam hat die Zuordnungen neu
  festgelegt — jede Bedeutung der v1-Liste bleibt erhalten, teils mit neuem
  Emoji, teils über einen gleichwertigen Weg (Knopf/Befehl). Neu dazugekommen:
  🍓 und 🍌. Die v1-Fassung (Pin-Liste vom 19.07.) ist über die git-Historie
  dieser Datei einsehbar.
- **2026-07-19** — v1: Telegram-Pin-Liste 1:1 übernommen.

---

**Herkunft:** v1 war die Telegram-Pin-Liste (Adam, 19.07.2026). v2 ist Adams
Neuzuordnung vom 20.07.2026 nach der Messung gegen Telegrams erlaubten
Reaktions-Satz. **Diese Liste gilt vollständig als Teil des Akzeptanzkriteriums
von 5.9** — jede Bedeutung muss erreichbar sein, per Reaktion oder über den
angegebenen gleichwertigen Weg.

Ja/Nein hat immer Vorrang, der Rest ist kontextabhängig.

---

## Als Reaktion (alle gemessen verfügbar)

**Ja/Nein & Bestätigung**
👍 Ja / passt / finde gut / Dank
👌 Ja / OK / alles klar
🫡 Ja — bzw. „erledigt", wenn's eine Aufgabe für mich war `[v2: ersetzt ✅]`
👎 Nein

**Dank & Beziehung**
❤️ Herzlichen Dank / Freude
🙏 Bitte oder Danke *(frag ich im Zweifel kurz nach)*
🤗 Freu mich `[v2: ersetzt 🙌]`
🎉 Lass uns feiern

**Feedback & Genuss**
👏 Stark / Anerkennung
🍓 Lecker, süß, köstlich `[NEU v2]`
🍌 Geil `[NEU v2]`
🤔 🤨 🤷 🤷‍♂ 🤷‍♀ Versteh ich nicht / erklär nochmal
`[v2: fünf gleichwertige Auslöser; ❓ ist als Reaktion nicht verfügbar. Die
v1-Bedeutung von 🤔 („Unsicher / lass mich überlegen") geht hierin auf —
Adam-Zuordnung 20.07.]`

**Steuerung & Tempo**
🔥 ⚡ Los geht's / lass es krachen / kann es kaum erwarten
`[v2: 🔥 umgewidmet von „Mega / richtig gut" (Lob decken 👍 👌 👏 ❤️ ab);
⚡ ersetzt 🚀, das als Reaktion nicht verfügbar ist]`
👀 Genauer anschauen / besser hinsehen `[v2: präzisiert von „Gesehen / schau ich mir an"]`
✍ 👨‍💻 💯 🏆 Wichtig / merk dir das
`[v2: vier gleichwertige Auslöser; ersetzt ⭐. 💯 umgewidmet von „Genau so,
voll richtig" — Adam-Zuordnung 20.07.]`
😴 Später / erinnere mich `[v2: ersetzt 🕐]`

## Über gleichwertigen Weg (als Reaktion nicht möglich)

✋ **Stopp / halt kurz an** → **Knopf bzw. Textbefehl.** Bewusste Entscheidung:
Ein Abbruchsignal muss eindeutig sein; kein sinnverwandtes Ersatz-Emoji trägt
diese Schärfe.

1️⃣–9️⃣ **Wählt Option N** → **Inline-Knöpfe direkt an der nummerierten Liste.**
Telegram bietet keinerlei Ziffern-Emoji als Reaktion an; Knöpfe an den Optionen
sind ohnehin die natürlichere Form.

## Reaktionen außerhalb des Vokabulars

Telegram bietet Adam alle 73 erlaubten Emoji an, nicht nur diese Liste.
Bei einer Reaktion außerhalb des Vokabulars rät der Bot **nicht**, sondern
quittiert freundlich und fragt kurz nach, was gemeint war.

Jederzeit erweiterbar, wenn uns was Neues einfällt.

---

## Technischer Hinweis für den Bau (5.9)

- Telegram führt etliche Emoji **ohne** Variation Selector (VS16): ❤ statt ❤️,
  ✍ statt ✍️, 🤷‍♂ statt 🤷‍♂️. Eingehende Reaktionen und dieses Vokabular beim
  Abgleich **normalisieren** (VS16 entfernen), sonst gehen Treffer verloren.
- Messmethode und Warnung vor der Geister-ID-Sonde: siehe MIGRATION.md 5.9
  („Methoden-Warnung"). Rohliste der 73: `scripts/tg_reactions.txt`.
