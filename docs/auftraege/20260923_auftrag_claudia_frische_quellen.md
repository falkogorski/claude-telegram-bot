**Zweck: WEITERGABE → Claudia** · **Zu tun: unverändert an Claudia.**

# Auftrag an Claudia: Quellenliste für den Frische-Strang, vom Server gemessen

23.09.2026, 17:4x · Engywuck → Claudia · Adams Entscheide von 17:3x: Recherche durch dich über SearxNG; Bewertung später nur auf Adams Wort (`/neues`); Bau als Block 6 bei Mick.

## Worum es geht

Adam will, dass das System am Zahn der Zeit bleibt: Alternativen zu eingebauten Bauteilen regelmäßig sehen, Neues aus der KI-/Digital-Landschaft hereinbekommen, daraus Vorschläge. Der Zufluss wird deterministisch gebaut (Feeds holen, ablegen, kein Modell am Zeitgeber). **Dein Teil jetzt ist die Quellenliste, mit Messung.** Kein Bau, kein Abonnement, kein Konto, keine Kosten.

## Was du lieferst: `quellen.json`-Vorschlag als Papier

Je Quelle eine Zeile: Name · Art (Release-Feed, Blog-Feed, Nachrichten-Feed) · Adresse des Feeds · vom VPS erreichbar (HTTP-Code, gemessen, Datum) · Sprache · Takt (wie oft erscheint etwas) · warum für uns.

**Drei Gruppen:**

1. **Bauteile, die wir einsetzen** (Register `components.json`): Release-Feeds der Projekte, z. B. `https://github.com/<owner>/<repo>/releases.atom` und PyPI-Release-Feeds `https://pypi.org/rss/project/<paket>/releases.xml`. Von meiner Maschine aus war GitHub gesperrt (403) und PyPI offen (200) — bitte vom VPS messen, das zählt.
2. **Anbieter-Meldungen:** Anthropic (Modelle, Claude Code), Telegram Bot-API, die Fremddienste (Transkript). Wo es keinen Feed gibt, ehrlich [kein Feed, nur Seite] notieren — das wird ein `manual`-Eintrag, kein Abruf.
3. **Landschaft:** Adams erste Quelle ist **https://www.kiberatung.de/blog** (deutsch; prüfen, ob es einen RSS-Feed gibt; der WhatsApp-Kanal desselben Anbieters ist für uns nicht maschinell lesbar, das bitte so vermerken). Dazu **internationale** Quellen mit Feed: Newsletter, die per Web-Feed erscheinen, Nachrichtenseiten zu KI und Robotik. Über SearxNG suchen, nicht aus dem Gedächtnis; je Quelle die Feed-Adresse messen. Zielgröße zehn bis fünfzehn Quellen, nicht mehr — die Liste ist der Filter, es gibt kein Stichwortsieb.

## Zwei Grenzen

- **Keine E-Mail-Newsletter.** Kein Postfach vor Ultracode (Kette 29.08.); was nur per Mail kommt, wird als [später, wenn Postfach] vermerkt.
- **Nichts anmelden, nichts abonnieren, nichts bezahlen.** Reine Adressen und Messungen. Zeigt eine Quelle beim Abruf Kosten oder Kontozwang, steht das in der Zeile.

## Form der Lieferung

Ein Papier `ausarbeitungen/2026-09-2x_frische-quellen.md`, dazu die Zeile, wie viele Quellen geprüft und wie viele erreichbar waren (Nenner). Adam bekommt die Datei, Engywuck liest sie im Log-Archiv, Mick baut daraus Block 6.
