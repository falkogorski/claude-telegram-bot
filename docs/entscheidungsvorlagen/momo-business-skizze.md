<!-- ROLLE: entscheidungsvorlage-momo-business -->

# MOMO — Geschäftsmodell-Skizze „Klon-Concierge"

**Konsolidierter Stand v13 · Brainstorming Adam + Kontrollsitzung, 23./24.07.2026**
Bestimmung: Gründungsdokument Nr. 2 des künftigen Business-Repos (Nr. 1 ist die
Gründungserzählung „Der Abend, an dem Momo seinen Namen fand"). Nach dem
Migrations-Sprint zusätzlich als `docs/entscheidungsvorlagen/` ins Repo übernehmen
und im 9.6-Business-Kapitel der Blaupause verankern. Keine Entscheidung ist final —
alles Adams Vorlage zum Weiterentwickeln.

---

## 1. Nordstern & Leitmotiv

Menschen zu einem befreiteren, leichteren, reicheren Leben verhelfen — durch einen
ethisch sauberen, individuell konfigurierten KI-Assistenten, der zugleich **Butler**
(nimmt Lästiges ab), **Coach** (bringt bei), **Werkzeug**, **Multiplikator** (bringt
in die Umsetzung) und **Ideengeber** ist. Jeder Mensch soll sich frei entwickeln und
aufbauen dürfen. Das Geschäft finanziert die Vision — nicht umgekehrt.

**Das Leitmotiv ist die Zeit** (ausführlich: Gründungserzählung): Die grauen Herren
stehlen Zeit, indem sie Menschen das Sparen einreden — **Momo gibt gestohlene Zeit
zurück** und schützt den Augenblick. Der Assistent trägt die Uhr, damit der Mensch
den Moment leben kann.

**Der Nordstern hat zwei Hälften (v13):**
1. **Butler zuerst:** Zeit zurückgeben — Fristen, Kleinkram, Verwalten, Erinnern
   übernehmen.
2. **Coach danach — Produktbaustein „In den Ausdruck kommen":** Momo hilft Menschen
   (freiwillig, auf Wunsch, niemals aufgedrängt), ihre Lebensthemen, Hobbys,
   Interessen und Freuden herauszufiltern, zu vereinen und in Einklang zu bringen
   mit möglichen Geschäftsmodellen, Berufen, Berufungen — Ziel: in die eigene Kraft,
   Mitte und den Ausdruck kommen, dann in Erfolg und Fülle. Auf Wunsch begleitete
   Arbeit an den Lebensthemen selbst. Tiefgründig, vor allem hilfreich.
   Ohne diese zweite Hälfte wäre zurückgegebene Zeit nur Leere — mit ihr wird sie
   Fülle. **Adams eigener Weg vom 23.07. (Zeitthema → Momo) ist der dokumentierte
   Prototyp dieses Prozesses; die Gründungserzählung ist die erste Fallstudie.**

**Referenz-Fall Nr. 0 ist Adam selbst:** Das Vier-Stunden-Prinzip (siehe Abschnitt 9)
ist zugleich Betriebsmodell und gelebter Produktbeweis.

## 2. Name, Wesen, Stimmen

- **Projektname intern ab sofort: „Momo"** (Arbeitstitel). OM-Signatur: dreimal OM
  im Namen (zweimal gespiegelt, einmal lesbar); im Wort **Moment** steht das OM
  vollständig sichtbar in der Mitte, flankiert von zwei gespiegelten Mo — die drei
  Brüder des Meister Hora, eingeschrieben ins Wort des Augenblicks.
- **Wesenskern des Assistenten** (gehört als Charakter-Definition in den
  System-Prompt jedes Klons, Charta-Kapitel „Wesen"): **liebevoll, geduldig,
  präsent, achtsam, ein ewiger Zuhörer, gibt nie auf — versucht es noch einmal
  anders.**
- **Stimmen zur Wahl (v12):** **Momo** (weiblich — die Zuhörerin) und **Beppo**
  (männlich — der Ein-Schritt-nach-dem-anderen-Weise; deckt sich wörtlich mit der
  Queue-/Nacht-Philosophie des Systems). Kunde wählt seine Assistenten-Stimme —
  Stimme ist Individualisierungs-Feature, kein Support-Detail. Keine
  Adam-Klon-Stimme, kein Avatar; die KI kennzeichnet sich stets als KI
  (EU-Transparenzpflicht + Vertrauensschutz).
- **Namensfamilie für Marke/Produkte (v12):** Stundenblume · Kassiopeia (die
  vorausblickende Assistenz!) · Wortspiel „im MoMOMent".
- **Marken-/Titelschutz:** Momo/Figurennamen sind Michael Endes geschütztes Werk —
  vor jedem öffentlichen Launch saubere Marken- und Titelprüfung (das Motiv ist
  frei, die geschützten Namen nicht automatisch). Intern gilt der Name ab sofort.

## 3. Werte-Architektur & Ethik-Charta

**Der Ursprung ist Adams, der Ausdruck ist universal (v11):**
- **Ursprung (privat, non-dogmatisch):** gnostische Lehren, hermetische Tradition,
  Schöpfungsgesetze — Adams persönliches Fundament, in seinen anderen Projekten
  (u. a. Fair-Führung) bereits definiert; von dort übernehmen. Kreise schließen
  sich bewusst: ein Werteursprung, viele Ausdrucksformen — die Blaupause ist
  mehrprojektfähig angelegt.
- **Ausdruck (im Produkt, für jeden verständlich):** liebevoll sein, wirklich
  zuhören, dem Menschen und seiner Schöpferkraft dienen, niemals Zeit stehlen,
  keinen Unfug unterstützen, nicht reglementieren. Kein Kunde bekommt Kosmologie —
  jeder Kunde bekommt ihre Frucht.
- **Eingebauter Werteboden:** Jeder Klon läuft auf Claude — Anthropics Ethik-Boden
  ist technisch mitgeliefert und nicht wegkonfigurierbar. Die Charta legt darüber
  Zweck und Ton fest; die Untergrenze muss niemand selbst durchsetzen.

## 4. Kern-Architektur

- **Klon-pro-Kunde, nie Multi-Tenant** (Rotes-Team-Urteil): Jeder Kunde erhält eine
  vollständige eigene Kopie — eigener Bot, eigener Server, eigenes Gedächtnis.
- **Kunde besitzt alles:** eigener VPS, eigenes Claude-Abo **oder** API-Key mit
  Ausgabenlimit, eigene Ablage. Verkauft werden **Einrichtung + Individualisierung
  + Care-Abo** — nie KI-Zugang. Dreifach sauber: AGB (Einzelnutzer-Eigenbetrieb je
  Kunde, kein Dritt-Routing), Kosten (keine laufenden KI-Kosten bei Adam), DSGVO
  (Adam wartet remote, hostet nicht — „Dein Assistent gehört wirklich Dir" als
  Datenschutz-USP in Produktform).
- **System-Schicht vs. Lebens-Schicht:** Der Klon trennt Blaupausen-Code (Maschine)
  strikt von persönlichen Daten (Memory, Logs, Regeln). Care-Updates fassen nur die
  System-Schicht an — ein Update berührt nie ein persönliches Wort. (Gleiches
  Deploy-Muster wie im Ur-System.)
- **Kunden-Governance nach 8.7-Muster:** **Spielwiese** frei (bedienen,
  konfigurieren, lernen, eigene Inhalte) — **Maschinenraum** schreibgeschützt;
  Änderungen nur über den Care-Kanal. Kunden lernen am System, ohne es zerlegen zu
  können.
- **Zugangs-VPN als fester Einrichtungs-Bestandteil (v8):** Kein Panel je
  öffentlich (Lehre aus dem OpenClaw-Vorfall; eigene 3.1-Auflage). Standard:
  Tailscale auf Kunden-Account (kostenlos, App, null Konfiguration); Option:
  WireGuard self-hosted für Anbieter-Unabhängigkeit. Consumer-VPNs für
  Kunden-Traffic: bewusst außerhalb des Produkts.
- **Quelloffen für Kunden ab Kunde Nr. 1 (v6):** Jeder Kunde darf den Code seines
  eigenen Klons vollständig einsehen — Transparenz + kein Lock-in („Du könntest
  jederzeit ohne mich weitermachen"). Schützt wird dadurch nichts Geheimes,
  sondern Adams Aufmerksamkeit: Kunde = Vertrag + Care-Kanal; Öffentlichkeit =
  Verpflichtungs-Tresen. Leichte Weitergabe-Klausel im Vertrag als Norm, nicht als
  Festung — Kunden schützen ihre Klone ohnehin selbst (ihre Lebensdaten stecken
  darin).
- **Pro Kunde ein eigenes WIEDERANLAUF.md** (Bus-Faktor: kein Kunde strandet).

## 5. Support-Architektur

**Der Support für KI-Assistenten ist selbst einer (v3/v6):** KI-Betreuung als
24/7-Fläche (Betreuungs-Klon, Hilfe zur Selbsthilfe, gewählte Stimme, kennzeichnet
sich als KI, Eskalationspfad zum Menschen) — der Mensch als seltene, wertvolle
Spitze. Skalierungs-Prinzip: Grenzkosten pro Kunde gegen null; menschliche Zeit nur
in bedeutsamen Momenten. **Pionier-Kunden-Status** für technisch versierte
Frühkunden: Einblick + direkter Draht + kuratierte Beiträge über den Care-Kanal =
wachsende Expertise ohne Maschinenraum-Bastelei.

## 6. Stufenleiter

1. **Concierge (jetzt → ~5 Kunden):** Handarbeit nach Blaupause. Pilotkunde Nr. 1
   vorhanden (Freund; Preisanker ~1.000 €). Jeder Case wird dokumentiert und füllt
   die Übertragbarkeits-Matrix (Geräte-/OS-Vielfalt: Linux/Windows/Android/…) —
   die Matrix wird später zur Preistabelle (Standard / Anpassung / Exot).
2. **Werkzeuggestützt (ab ~5 Kunden):** REBUILD wird Setup-Skript; Einrichtung
   ~1 Tag. **KI-geführtes Intake-Interview** statt Formular-App: erhebt Ziele,
   Arbeitsweise, Lebens-/Gerätelandschaft; generiert Konfiguration + Preis; ist
   zugleich Live-Demo des Produkts. (App/Webseite später als Hülle darum.)
3. **Produktisiert:** Webseite, Demo-Bot (Drehbuch 9.3), Konfigurator, Warteliste.
4. **Open-Core:** „Code frei, Können bezahlt" (Nextcloud-Muster). Öffentliches
   Repo erst als **bewusster Stufe-4-Meilenstein**: bereinigte Blaupausen-Fassung
   (neues Repo — nie das persönliche, dessen Historie Adams Leben enthält), mit
   eingeplanter Community-Pflege. Kein Monopol-Ziel — Nachbauen ausdrücklich okay.

## 7. Vertrieb

- **Kanal 1 — Empfehlung durch das Produkt selbst:** „Der Assistent stellt sich
  selbst vor" — der Bot des Kunden verlinkt den Interessenten-Kontakt
  (Telegram-nativ) und führt ein kurzes, charmantes Kennenlern-Gespräch
  (Mini-Intake): Kostprobe statt Landingpage. **Plus:** Hinter jeder Empfehlung
  steht ein echter Mensch mit echter Erfahrung als Ansprechpartner — Network
  Marketings Kernstärke (persönliches Vertrauen), verheiratet mit einer Demo, die
  das Produkt *ist*. Diese Kombination ist der Vertriebs-USP.
- **Empfehlungs-/Affiliate-Programm (v7/v9):**
  - **Margen von Anfang an einpreisen:** Vertriebsanteil (~40–60 %, branchenüblich
    Dienstleistung/Beratung; reine Online-Produkte bis ~80 %) wird ab dem ersten
    **Normalpreis** einkalkuliert — der Programm-Start ist später ein
    **Freischalten, nie eine Preiserhöhung.**
  - **Pilotphase: ausdrücklich provisionsfrei** (Pilotpreis liegt ohnehin unter
    Normal; Margen noch nicht vorhanden; Testphase).
  - **Phase 2: eine Empfehlungsebene** — Einmalzahlung → Einmalprovision;
    Monatsbeitrag → laufender Anteil (üblich, fair, Ansporn).
  - **Mehrebenen später:** in DE etabliert (Berufsverband existiert), machbar,
    aber wasserdicht geprüft (Abgrenzung Schneeballsystem) — kein Blocker, nur
    Sorgfalt.
  - **Start-Gate (v9, präzisiert — zweiteilig, messbar):** (1) **Vollautomatische
    Kette** Intake → Einrichtung → Onboarding → Betreuung → Abrechnung ohne
    Pflicht-Mensch (Mensch als Kür-Moment, nie Flaschenhals) — Multiplikation ist
    exponentiell; der Engpass-Test ist nicht „ein Schub", sondern „skaliert ohne
    menschliches Mitwachsen". (2) **Empfehlbare Produktreife** — Multiplikation
    ist ein Verstärker ohne Meinung. Einordnung: natürlicher Übergang Stufe 3→4.
- **Weitere Kanäle:** Adams paralleles Affiliate-Projekt als Übungsfeld/Grundlage;
  Social Media als eigener späterer Posten mit eigener Tragweite.

## 8. Pricing-Skelett

- **Einrichtung:** Pilot ~990 € (inkl. Nacharbeit, als Pilotpreis deklariert,
  gegen Feedback + Referenz) → später gestaffelt ~1.500 / 2.500+ je Umfang, vom
  Intake generiert. Normalpreis von Tag eins mit Vertriebsmarge kalkuliert (s. o.).
- **Care-Abo als Kerngeschäft:** ~49–99 €/Monat — Updates, Monitoring, kleine
  Anpassungen, Fragen; **klare Umfangsgrenze** (z. B. 2 Std./Monat, darüber
  Stundensatz) gegen Support-Kriechen. Zehn Care-Abos = Grundeinkommen.
- **Kunden-Nebenkosten transparent direkt beim Kunden:** VPS ~5–10 €/Monat,
  eigenes Claude-Abo oder API-Budget mit Spend-Limit.
- **Betreuungs-Feinjustierung** ergibt sich aus realem Umfang der ersten Cases.

## 9. Betriebs-Vorgaben

- **Design-Vorgabe: Adams Regelbetrieb ≤ 4 Std./Woche.** Keine Einschränkung,
  sondern die Produktisierungs-Zwangskraft: Jeder Prozess wird so gebaut, dass die
  Maschine ihn trägt. Adams Zeit fließt in **menschliche Momente** (Intake-Gespräch,
  Übergabe-Moment, Quartals-Check-in, echte Blockaden) — Bindung entsteht durch
  bedeutsame Momente, nicht durch Erreichbarkeit.
- **Aufbauphase (~1.–3. Jahr) bewusst hands-on** — Lernen am echten Kunden; danach
  übernehmen Mitarbeiter die Momente, nie die Technik (die macht die Maschine).
- **Rechtliches Minimalpaket vor Kunde Nr. 1:** Dienstleistungsvertrag
  (Leistungsumfang, Haftungsgrenze, „KI kann irren"-Klausel, leichte
  Weitergabe-Klausel), Gewerbe/Rechnung (5.19 hilft), AV-Vertrag nur falls doch
  gehostet wird.
- **Klienten-Setups laufen NIE über Adams Abo** (AGB-rote Linie aus dem
  Strategie-Bericht): eigene Zugänge oder API mit Kostenrechnung.
- **Kontingent-/Nacht-Prinzip gilt auch geschäftlich:** Autonome Läufe takten sich
  nach der Ressource, die zuerst ausgeht; Eskalation gezielt statt pauschal.

## 10. Nächste Schritte (nach dem Migrations-Sprint)

1. Business-Repo anlegen — Gründungsdokumente: (1) Gründungserzählung,
   (2) diese Skizze.
2. Diese Skizze zusätzlich ins Bot-Repo (`docs/entscheidungsvorlagen/`) +
   Verankerung im 9.6-Business-Kapitel der Blaupause.
3. Markenrecherche-Auftrag vorbereiten (Momo/Beppo/Kassiopeia/Stundenblume).
4. Rechtliches Minimalpaket klären.
5. Pilotkunde Nr. 1 (der Freund): Intake-Gespräch als ersten echten Case führen —
   dokumentiert als Fallstudie Nr. 1 (nach Nr. 0: Adam).

---

*Konsolidiert aus den Merk-Zeilen v1–v13 des Abends vom 23./24.07.2026.
Schwesterdokument: „Der Abend, an dem Momo seinen Namen fand"
(ROLLE: gruendungs-erzaehlung-momo).*
