**Zweck: WEITERGABE → Mick** · **Zu tun: nur lesen. Fassung 2 nach Claudias Messung (24.09., 01:00): Reihenfolge geändert, W4 zurückgestuft.**

# Vormerkung für Mick: WhatsApp-Kanäle als Zufluss (Block 6b)

24.09.2026, 00:3x · Engywuck · Adams Entscheide 00:2x: alle Wege durchprobieren; W4 mit eigener Nummer freigegeben (💰 SIM/eSIM einmalig); W3 als Rückfall.

**Claudias Messung (`2026-09-24_whatsapp-messung.md`):** W1 tot (Kanalseite liefert nur die Visitenkarte). W2 Blog ohne Feed, Kanal kein Spiegel; neu M6 Newsletter-Archiv kibubble.news. M3: Kanal-Unterstützung in beiden Hauptzweigen unvollständig; **npm-Kampagne mit bösartigen Baileys-Abspaltungen (SafeDep)** → W4 nur aus dem Ursprungs-Repo, gepinnt, mit Prüfsumme, nie eine Abspaltung. M4/M5 unbelegt.

**Reihenfolge, neu:** (1) M6 Newsletter-Feed → nur Quelle in `quellen.json`. (2) W3 Zweitgerät, Adams Hand, Bot-Seite ein Eingang. (3) W4 zuletzt.

**Alte Reihenfolge, zur Ablage** (`20260924_auftrag_claudia_whatsapp_messung.md`):
1. **W1/W2** (Kanalseite oder Blog-Feed): falls tragfähig, nur eine Quelle in `quellen.json` von Block 6, ggf. ein kleiner Seiten-Parser in `zufluss.py`. Kein eigener Block.
2. **W3 Zweitgerät, offizielle App:** Adams Hand (Mac oder Android mit seiner Geschäftsnummer), Bot-Seite nur ein Eingang: Nachricht vom Gerät → Zufluss-Datei. Deterministisch, kein Modell.
3. **W4 Bibliothek als verknüpftes Gerät auf dem VPS** (Baileys, gemessen: `newsletterFollow`, `newsletterFetchMessages`, `newsletterMetadata` in `src/Socket/newsletter.ts`; Alternative whatsapp-web.js, [Channels ✅]): **nur mit eigener Nummer, nie mit Adams Haupt- oder Geschäftsnummer.** Eigener Dienst unter eigenem Nutzer, Sitzungsdaten als Geheimnispfad (Register, `_is_sensitive_ref`), nur Lesen von Kanälen, kein Senden, Inhalt als Mitschrift in die Zufluss-Datei. Neue Schrankenlogik → Ultracode-Prüfstelle vor dem Scharfstellen (CLAUDE.md, [vor jeder Anbindung fremder Datenquellen]). Klon-Probe (R4).

**Gut genug wenn:** Ein Kanalbeitrag landet innerhalb eines Tages als Zeile in der Zufluss-Datei, ohne Modellaufruf, ohne dass eine Nummer von Adam beteiligt ist.

Jetzt nichts tun außer lesen: die zwei Bibliotheken kennen, Baileys-Newsletter-Datei einmal durchgehen.
