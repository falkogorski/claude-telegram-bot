<!-- ROLLE: entscheidungsvorlage-kanalstruktur -->
# 6.6 Telegram-Kanalstruktur — Entscheidungsvorlage (Daumen-Liste)

**Erstellt:** 23.07.2026, autonomer Lauf. **Noch NICHTS angelegt** — der Bau folgt
gemeinsam nach Phase 3. **Datengrundlage:** Häufigkeits-Analyse der acht
Tagesdateien in `claude-bot-logs/conversations/` (17.–23.07.): Technik/Migration
dominiert (270 Treffer, in allen Dateien), Recherchen/PDFs (102) und Fußball (99)
stark, Business/Blaupause (66) wachsend, Rechnungen (12) und Termine (12)
regelmäßig-klein, rote Themen (Klienten/Human Design) praktisch abwesend (4) —
wie es die Ampel will.

**Prinzipien:** Klein starten (sechs lebende statt fünfzehn verödende Orte),
erweiterbar (6.5 kann später Topics selbst anlegen), **gleiche Terminologie wie
die portable Ordnerstruktur 4.3** („Struktur über Namen") — Klammerwert = 4.3-Ordner.
Der Bot-Chat selbst bleibt die Kommandobrücke (Dialog); die Kanäle sind Ablage.

## Vorschläge — bitte je Zeile 👍/👎

- [ ] **1. 📦 Recherchen & Referenzen** (`recherchen/`) — Zweck: alle
  Recherche-Lieferungen, Referenz-PDFs, Quellen-Berichte. **Automatisch:** jede
  PDF-/Recherche-Ausgabe des Bots (heutiges 6.1-Routing). Manuell: von dir
  geteilte Fundstücke. *Meistgenutzter Ablage-Fall deiner echten Nutzung.*
- [ ] **2. ⚽ Fußball** (`fussball/`) — Zweck: FC-Köln-/Fußball-Recherchen
  (Trainer-/Kapitäns-Chroniken, Spielanalysen); später Andockpunkt für Fanpost.
  **Automatisch:** Recherchen mit Fußball-Erkennung. *Größter Einzel-Themenstrang
  außerhalb der Technik — verdient den eigenen Ort, sonst flutet er Nr. 1.*
- [ ] **3. 🛠️ Technik & Migration** (`technik/`) — Zweck: Statusberichte,
  Weitergabe-Blöcke, Deploy-/Testprotokolle — auch als Lese-Ort der
  Kontrollsitzung. **Automatisch:** auf Zuruf geroutete Statusübersichten.
  Manuell: angepinnte Beschlüsse. *Nach der Migration ruhiger — bleibt als
  Systemgedächtnis.*
- [ ] **4. 💼 Business & Blaupause** (`business/`) — Zweck: Markt-Checks,
  Produkt-/Blaupause-Gedanken, Fairführung-Abstraktes (gelb — Konkretes bleibt
  im sicheren Kanal). Überwiegend manuell + gezielte Recherchen.
- [ ] **5. 🧾 Rechnungen & Papierkram** (`rechnungen/`) — Zweck: Ablage der
  5.19-Ausgaben (Aufstellungen, Rechnungs-PDFs) zur schnellen Kontrolle.
  **Automatisch:** sobald 5.19 gebaut ist. *Klein, aber klar abgegrenzt.*
- [ ] **6. 🗄️ Archiv** (`archiv/`) — Zweck: Abgeschlossenes aus 1–5, manuell
  verschoben, damit die lebenden Orte schlank bleiben. Kein Auto-Routing.

**Bewusst NICHT dabei:** Erinnerungen/Routinen (bekommen mit Phase 7 den eigenen
Erinnerungskanal) · rote Inhalte (Klienten, Human Design konkret — laufen laut
Ampel nie durch Telegram) · ein „Sonstiges" (erzeugt nur einen Müllschlucker).

**Nächster Schritt nach deinem Daumen:** Struktur gemeinsam anlegen (Bau nach
Phase 3), Routing-Regeln je Kanal in 6.1 verdrahten, 4.3-Ordner mit denselben
Namen anlegen.
