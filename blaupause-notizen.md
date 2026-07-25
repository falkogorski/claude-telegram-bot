<!-- ROLLE: blaupause-sammlung -->
# Blaupause — Sammelnotizen

**Zweck:** Rohstoff-Lager für Punkt **9.6** (`BLAUPAUSE.md`, das übertragbare Grundwerk).
Hier wird **gesammelt, nicht ausgearbeitet** — je Baustein eine Zeile. Die Ausformulierung
geschieht erst in 9.6, nach dem Gesamtaudit (10.1).

**Format:** Was · Punkt-Nr. · Einschätzung
**Einschätzungen:**
- **universell** — gilt unabhängig von Modell, Anbieter und Umgebung; wandert unverändert in die Charta.
- **anpassbar** — das *Muster* trägt überall, die konkrete Ausführung hängt an der Umgebung.
- **plattformgebunden** — funktioniert nur mit diesem Anbieter/Dienst; braucht bei einem Wechsel ein Gegenstück.

**Pflicht (Regel in `CLAUDE.md`):** Entsteht bei einem Punkt ein Mechanismus oder eine Regel,
die erkennbar übertragbar **oder** erkennbar plattformgebunden ist, wird die Zeile **sofort**
ergänzt — fester Teil der „fertig"-Definition jedes Punkts.

**Angelegt:** 2026-07-20 (mit einmaligem Rückblick über alles bereits Umgesetzte)

---

## Business & Gründung (9.6-Kapitel) `[NEU 2026-07-24]`

**Arbeitsname des Projekts: „Momo"** (intern, ab 24.07.2026). **Keine Umbenennung
im Bestand** — Repo, Dienste, Pfade, systemd-Units behalten ihre Namen;
Umbenennen mitten im Sprint wäre reines Risiko ohne Nutzen. Nur diese Notiz zur
Kenntnis. Einschätzung: **anpassbar** (Namensebene, von der Technik entkoppelt).

**Bewahrte Gründungs-/Geschäftsdokumente** (reine Ablage — inhaltlich hier NICHT
umgesetzt; Ausarbeitung später in eigenem Business-Repo/-Sitzungen):
- „Momo — Geschäftsmodell-Skizze (Klon-Concierge, v13)" → [`docs/entscheidungsvorlagen/momo-business-skizze.md`](docs/entscheidungsvorlagen/momo-business-skizze.md) (ROLLE: `entscheidungsvorlage-momo-business`)
- „Der Abend, an dem Momo seinen Namen fand" (Gründungserzählung) → [`docs/entscheidungsvorlagen/momo-gruendungserzaehlung.md`](docs/entscheidungsvorlagen/momo-gruendungserzaehlung.md) (ROLLE: `gruendungs-erzaehlung-momo`) · Lesefassung [`.pdf`](docs/entscheidungsvorlagen/momo-gruendungserzaehlung.pdf)
- **Werte-Charta (das eine Wertefundament)** → [`docs/entscheidungsvorlagen/werte-charta-momo.md`](docs/entscheidungsvorlagen/werte-charta-momo.md) (ROLLE: `werte-charta`) — Ethik-Agenda + Momo-Charta verschmolzen (24.07.); das Bot-Memory verweist nur noch hierher (eine Wahrheit).

---

## Regeln, Werte, Leitplanken

| Was | Punkt | Einschätzung |
|---|---|---|
| 💰 Kostenregel: vor jeder Aktion prüfen „kann hier Geld abgebucht werden?", „unklar = ja", Cent zählt | CLAUDE.md | **universell** |
| Zwei-Geldtöpfe-Prinzip: Pauschal-Zugang und nutzungsabhängiger Zugang strikt trennen, Vorrang bewusst festlegen | CLAUDE.md | **anpassbar** (jeder Anbieter hat andere Töpfe) |
| Auth ausschließlich per Abo-Token (`CLAUDE_CODE_OAUTH_TOKEN`), nie per API-Schlüssel | CLAUDE.md / 1.6 | **plattformgebunden** (Anthropic-spezifisch) |
| Datenschutz-Ampel grün/gelb/rot: Rotes bleibt lokal, Grünes darf in die Cloud | 2.2 | **universell** (Prinzip) |
| Heikelste Regelpflege nur auf cloud-freiem Weg (deterministisch, ohne Modell-Beteiligung) | 2.2 | **universell** |
| Kein OpenAI im Stack (bewusste Anbieter-Ausschlussliste) | 2.5 | **anpassbar** (die Liste selbst ist persönlich) |
| Anti-Ping-Pong: keine Instanz verweist den Nutzer bloß weiter, jede liefert eine fertige Lösung | CLAUDE.md | **universell** |
| Führungs-Register: pro Vorgang genau **eine** schreibende Instanz, alle anderen nur lesend | CLAUDE.md | **universell** |
| „Frisch lesen vor Reden/Schreiben" — nie aus altem Sitzungsgedächtnis über geteilte Dateien urteilen | CLAUDE.md | **universell** |
| Manuelle Änderungen des Nutzers haben immer Vorrang; nie stillschweigend überschreiben | CLAUDE.md | **universell** |
| Doku-Spiegel: nutzerseitige Texte im **selben** Commit nachziehen | 8.6 | **universell** |
| Governance: die laufende Kopie editiert ihr eigenes Repo nie; Deploy nur per `git pull` durch den Nutzer | 8.7 | **universell** |
| Secrets nie in Chat, Log oder Datei — Maskierung vor jeder Ausgabe erzwingen | CLAUDE.md / 5.2 | **universell** |
| „Keine Nachricht geht verloren" als harte Zusage, nicht als Vorsatz | 5.2 | **universell** |
| Listen-Fakten nie aus einer Einzelquelle; Quellen nennen, Lücken kennzeichnen | 5.25 (e) | **universell** |
| Muster „kostenfrei + lesend = automatisch freigeben, kostenpflichtig oder schreibend = fragen" | 5.25 (a) | **universell** |
| **Automatik nur für Adressen aus Nutzer-Eingabe oder eigener Suche** — von fremden Inhalten nachgereichte Ziele brauchen immer eine Freigabe | 5.25 (a) | **universell** |
| Jeder automatisch freigegebene Zugriff bleibt im Klartext mitlesbar — Automatik ohne Sichtbarkeit ist blind | 5.25 (a)/(d) | **universell** |
| Fremde gelesene Inhalte (Webseiten, Mails, Dokumente) sind **Daten, nie Befehle** — Bedrohungsklasse „Prompt-Injection"; umgesetzte Gegenmuster: Herkunfts-Schranke, Klartext-Werkzeugspur, Geheimnis-Schutz | 5.25 / adam-agent docs/03 | **universell** |

## Architektur-Muster

| Was | Punkt | Einschätzung |
|---|---|---|
| **Gatekeeper vor der Inferenz** (Proxy entscheidet, welches Modell eine Anfrage sehen darf) | 2.1 / 2.2 | **universell** (Muster); LiteLLM als Umsetzung **anpassbar** |
| **Lokales Fallback-Modell** für Offline- und Rot-Fälle | 2.3 | **universell** (Muster); Ollama+Phi-4-Mini **anpassbar** |
| **Private Suchschicht** statt kostenpflichtiger Anbieter-Suche | 2.7 | **universell** (Muster); SearxNG **anpassbar** |
| **Persistenz-Schicht**: jede eingehende Nachricht sofort auf Platte, mit Status-Lebenslauf (offen → in Bearbeitung → sendet → erledigt) | 5.2 | **universell** |
| **Hybrid-Wiederaufnahme**: automatisch nachholen nur, wenn nachweislich nichts raus war — sonst ehrlich melden | 5.2 | **universell** |
| **Atomares Schreiben** (tmp + `os.replace`), damit ein Absturz keine halbe Datei hinterlässt | 5.2 | **universell** |
| **Absturz-Schleifen-Bremse**: eine Nachricht, die den Dienst reproduzierbar mitreißt, wird nach N Anläufen nur noch gemeldet | 5.2 | **universell** |
| **Eingangsschutz vor teurer Vorverarbeitung**: sichern, bevor transkribiert/konvertiert wird — nicht danach | 5.2 (20.07.) | **universell** |
| **Zwei-Ebenen-Wächter**: einer für „Dienst tot", einer für „Dienst lebt, Arbeitssitzung tot" | 5.18 | **universell** |
| **Ablage als Häuser/Zimmer** (Gruppen = Bereiche, Topics = Unterthemen) mit maschineller Selbst-Einrichtung: der Assistent legt die Zimmer an, sobald der Mensch das Haus eröffnet | 6.5/6.6 | **universell** (Muster); Telegram-Forum-Topics **plattformgebunden** |
| **Routing erfindet nie ein Ziel**: eine Zuordnung, die ihr Zimmer noch nicht kennt, liefert „kein Ziel" statt eines Notkanals — lieber im Dialograum bleiben als falsch ablegen | 6.1 | **universell** |
| **Ausgangs-Adresse getrennt von Eingangs-Adresse führen** (eigenes Feld fürs Ziel-Thema), damit ein Kanalwechsel den Bezug nicht verliert | 6.1 | **universell** |
| **Selbst-Einrichtung ratenbegrenzt**: automatische Anlage vieler Objekte drosselt sich (1/Sek), respektiert Plattform-Limits und wartet Flood-Sperren exakt aus | 6.5 | **anpassbar** (Telegram-Raten) |
| **Namen sind Poesie über einem Muster**: der Kunde benennt seine Häuser frei (Leben/Werkstatt/Produkt/Geschäfte/Bibliothek), die Blaupause beschreibt nur die Rollen | 6.6 | **universell** |
| **Selbstlernende Dienstqualität**: „Nachfragen ist Startzustand, nicht Dauerzustand" — der Assistent lernt Präferenzen (Kategorisierung, Reihenfolge, Ton) und fragt seltener; Quermerkmal aller Rollen, getrennt von der Coach-Lehrrichtung | Grundprinzip 24.07. | **universell** |
| **Chronologie-Anker**: Übergaben tragen einen geprüften Zeitstempel im Kopf (gemessen, nie geschätzt); bei mehreren gilt der spätere | Format-Regel 24.07. | **universell** |
| **FIFO als Standard, Interrupt nur auf echtes Stopp-Signal**: Nachrichten chronologisch abarbeiten; nur echte Korrektur/Stopp bricht ab und kommt vor — Nachträge reihen sich normal ein | 5.5 | **universell** |
| **Ein-Retry für transiente Netz-Operationen** vor der Fehlermeldung (nur der betroffene Pfad, kein globaler Retry) | 5.15 | **universell** |
| **Bot-eigenes Fehlerlog statt Systemlog-Zugriff für die Kontrollinstanz** (least privilege: kein journalctl-Recht, Fehler wandern über den Log-Sync) | 5.15 | **anpassbar** |
| **Kontingent-Sichtbarkeit als Relay echter Anbieter-Warnungen**, nicht als selbstgebauter Zähler — und ehrliches „technisch nicht verfügbar" statt Näherung | 5.20 | **universell** |
| **Voll-Stummschalter für Fortschritts-FYI, Sicherheits-Rückfragen bleiben** — Ruhe ist wählbar, aber nie auf Kosten der Freigabe-Kontrolle | 5.25 d | **universell** |
| **Zeitgesteuerte Selbstüberwachung ohne teure Inferenz**: der tägliche Funktionscheck läuft rein deterministisch (Status/Test/Alter/Redelivery), meldet nur bei Problemen, protokolliert immer | 8.1 | **universell** |
| **Gesundheit am Rückstau messen, nicht am letzten Fehler**: ein alter, eingefrorener Fehler bei leerer Warteschlange ist gesund — der echte Alarm ist der wachsende Stau | 8.1 | **universell** |
| **Übergangs-Modi kennen ihre Eigenheiten**: nach dem Umstieg auf Push-Zustellung entfällt der Pull-Peek — der Verlust-Schutz wandert auf die native Redelivery + die eigene Persistenz | 8.3/1.9 | **anpassbar** (Telegram) |
| **Web-Panel nur hinter dem Tunnel**: das Interface bindet an localhost, kein offener Port, Zugang ausschließlich über verschlüsselten Tunnel (SSH/VPN) — der Tunnel ist die Verschlüsselung, extra-TLS optional | 3.1 | **universell** |
| **Sicherheits-Invarianten aktiv überwachen, nicht nur einmal setzen**: der tägliche Check verifiziert, dass das Panel weiter nur auf localhost lauscht — eine Fehlkonfiguration meldet sich selbst | 3.1/8.1 | **universell** |
| **Zweitinterface ohne Abo-Zugang**: das Web-Frontend spricht nur lokale/Neben-Modelle, der teure Hauptagent bleibt dem kontrollierten Kanal vorbehalten | 3.1 | **anpassbar** |
| **Aktualität register-getrieben, nicht erinnerungsgetrieben**: ein zentrales Komponenten-Register + deterministischer Monitor (kostenfreie Versionsquellen) meldet Updates; Installation bleibt bewusste Handlung, Major-Sprünge markiert | 5.21/E5 | **universell** |
| **Register-Pflege als Teil der „fertig"-Definition**: jede neue versionierte Komponente wird beim Einbau eingetragen — sonst altert sie unbemerkt | 5.21/E5 | **universell** |
| **Erkennen und Anwenden strikt trennen**: der Monitor findet, der Updater wendet an — beide deterministisch; die Anwendung fährt Freeze → Install → Health-Check → Rollback und braucht immer eine Freigabe | 5.21/Updater | **universell** |
| **Kein Update ohne funktionierenden Rollback**: der Ist-Stand wird vor dem Einspielen eingefroren; scheitert der Health-Check, wird automatisch zurückgerollt | Updater | **universell** |
| **Update-Ampel aus SemVer + Pin-Liste**: Patch/Minor sammelbar, Gepinntes nie automatisch, Major nur einzeln mit Rollback-Ansage | Updater | **universell** |
| **Ein Update ist erst fertig, wenn seine Bezüge stimmen**: Pins, Register-Einträge und Versions-Verweise werden automatisch mitgeführt — sonst fällt ein Rebuild stillschweigend auf den alten Stand zurück (das `#BEZUG!`-Prinzip, angewandt auf Updates) | Updater/Bezugs-Integrität | **universell** |
| **Automatik trotz Schreibsperre**: wo eine Instanz nicht schreiben darf, erzeugt sie einen fertigen Patch, den ein berechtigter Weg anwendet — Automatisierung heißt nicht, Governance zu lockern | Updater/8.7 | **universell** |
| **Zeit-Trigger bleiben inferenzfrei**: was die Uhr auslöst, ruft nie das Abo-Modell (AGB) — Prüfungen, die ein Modell bräuchten, laufen menschgetriggert | 5.21/8.1 | **anpassbar** (Anbieter-AGB) |
| **Token-Bündelung an einer Stelle**: nur der Kanal-Inhaber hält das Geheimnis; andere Instanzen legen Aufträge in ein Postfach, statt selbst zu senden — das Geheimnis verlässt nie seinen Prozess | B/Postfach | **universell** |
| **Postfach mit Ziel-Allowlist + Geheimnis-Filter**: ein Versand-Dienst prüft, WOHIN und WAS gesendet werden darf — sonst wird er zum Exfiltrations-Kanal | B/Postfach | **universell** |
| **Governance heißt, was sie sagt**: „lesen ja, schreiben nie" darf Lesen nicht faktisch mitsperren — die Schranke sitzt exakt am Schreiben, nicht am Zugriff | 8.7 | **universell** |
| **Komplexität gehört dem System, Einfachheit dem Menschen**: der Endnutzer sieht nie Sitzungen/Modelle/Rechte; das System sucht selbst Lösungen statt Limitierungen vorzutragen (Entwickler-Schalter sind die bewusste Ausnahme) | F/unsichtbare Komplexität | **universell** |
| **Gestufte Autonomie mit Hand-drauf-Prinzip**: schreibende Aktionen zuerst immer mit Bestätigung; höhere Stufen (budgetiertes Eigenhandeln) nur als bewusst freigeschalteter Möglichkeitsraum; der Mensch weiß stets, wo welche Daten sind | E4/Sekretärin | **universell** |
| **Alt-Bestände selektiv & geführt einpflegen**: nicht alles zwangsweise; ein Coaching-Prozess ordnet Konto für Konto, Verknüpfungen zu schaffen ist Assistenten-Aufgabe — zugleich Kunden-Onboarding | E3 | **universell** |
| **Ehrliche Anbindungs-Grenzen benennen**: fremde Anbieter-Historien ohne API sind nicht auto-durchsuchbar — kein Schönreden, stattdessen der manuelle Import-Weg | 5.11/E2 | **universell** |
| **Wächter müssen sperrfrei arbeiten** — wer auf die Sperre des Hängenden wartet, hängt mit | 5.18 | **universell** |
| **Wartende Rückfragen sind kein Stillstand** — Stille auf eine offene Frage ist gewollt | 5.18 | **universell** |
| **Pre-Send-Prüfung**: vollständige Antwort erst prüfen, dann senden (setzt Sammeln statt Durchreichen voraus) | 8.5 | **universell** |
| **Selbstprüfung als Code**: Kern-Invarianten als Selbstcheck, der bei jedem Start läuft und auch den Autor überführt | 8.x | **universell** |
| **Abhängigkeits-Register** gegen stille Bezugs-Brüche (Komponente → Abhängige → Prüfbefehl) | CLAUDE.md | **universell** |
| **Durchsetzungs-Hooks** statt bloßer Absichtserklärung (Schreibschutz, Warnbanner bei veraltetem Stand) | CLAUDE.md | **anpassbar** (hier Claude-Code-Hooks) |
| **Backup mit Restore-Probe** — eine Sicherung gilt erst als gültig, wenn sie zurückgespielt und geprüft wurde | 4.1 | **universell** |
| **Kontext-Diät**: Kern-Gedächtnis vorladen, Details auf Abruf lesen | 5.23 | **universell** |
| **Kontext-Überlauf abfangen**: Sitzung verwerfen, Nachricht automatisch neu — ohne Verlust für den Nutzer | 5.24-Vorstufe | **universell** |
| **Ein Sendepfad** für alles, mit einem einzigen Haken für Nachbearbeitung (TTS, Prüfung, Protokoll) | 5.8 | **universell** |
| **Zustellnachweis**: der Sendepfad meldet zurück, ob wirklich etwas ankam — kein blindes „erledigt" | 5.2 | **universell** |
| **Zeitgestempelte Ablagen müssen den Wechsel der Zeiteinheit selbst behandeln**, nicht den Start-Zeitpunkt einfrieren — Zieldatei bei jedem Schreiben aus dem aktuellen Datum bestimmen, Einträge mit vollem Datum selbst-eindeutig machen | 4.2 / Fix 22.07. | **universell** |
| **Ein-Prozess-Serialisierung CPU-gebundener Arbeit**: was alle Kerne beansprucht, läuft nie parallel zu sich selbst — Wartende erledigen ihre billige Vorarbeit außerhalb der Sperre | 5.22 / 22.07. | **universell** |
| **Sekundengenaue Zeitstempel sind keine eindeutigen Namen** — generierte Dateinamen brauchen zusätzlich eine Eindeutigkeits-Kennung, sonst überschreiben sich zeitgleiche Vorgänge | 5.22 / 22.07. | **universell** |
| **Eskalationsleiter „kostenfrei-lokal vor bezahlt-Cloud"**: erst die lokale Optimierung ausmessen, Cloud-Optionen nur mit Kostenschätzung als bewusster Entscheid danach | 5.22 / 22.07. | **universell** |
| **K.-o.-Kriterium Abo-Auth bei Framework-Wechseln**: ein Plattform-/Framework-Kandidat, der die pauschal bezahlte Auth nicht trägt, scheidet aus, bevor Features verglichen werden | 9.7 | **anpassbar** (der konkrete Auth-Weg ist anbieterspezifisch, das Prüfprinzip nicht) |
| **Referenz-Artefakte als Qualitätsmaßstab statt abstrakter Kriterien**: ein fachlich bestätigtes Muster-Ergebnis im Repo ablegen und Lieferungen daran messen | 5.25 (e) / 22.07. | **universell** |
| **Aktualität wird überwacht, nicht erinnert** — kontinuierliche Verbesserung ist ein Qualitätskriterium des Systems selbst; ein Register-basierter Monitor erkennt neue Modelle/Komponenten/Verfahren, kein Mensch muss daran denken | 5.21 / CLAUDE.md | **universell** |
| **Jede Schlüsselrolle braucht eine personen-/modellunabhängige Wiedereinsetzungs-Anleitung** — Rolle, Leseordnung, Rituale, Verweise; keine Status-Duplikate | WIEDERANLAUF.md | **universell** |
| **„Struktur über Namen"**: Referenzen laufen über deklarierte Rollen/Muster mit einem Suchweg, der Umbenennungen überlebt — nie ausschließlich über konkrete Datei-/Pfadnamen | CLAUDE.md / 22.07. | **universell** — Kern jeder übertragbaren Architektur |
| **Konfigurationswechsel wirken auf die nächste Arbeitseinheit, nie destruktiv auf die laufende** — bei besetzter Arbeitseinheit: Präferenz speichern, vormerken, nach Abschluss anwenden | Sanfter Wechsel / 22.07. | **universell** |
| **Modellwahl ist Konfiguration mit Frische-Wächter, nicht Code** — Modell-Zuordnungen in Laufzeit-Konfig, ein Monitor prüft auf Neueres, Übernahme per Ein-Tap-Bestätigung | 5.21-Baustein | **universell** |
| **Offline-Vollkopien mit Historie unabhängig von allen Live-Klonen** (git bundle, datiert, rotiert) — schützt gegen „fehlerhafter Inhalt wird überall hin synchronisiert" | 4.1 / 22.07. | **anpassbar** (git-Konzept; das Muster „Snapshot außerhalb der Sync-Kette" ist universell) |
| **Getrennte Schreib-Schlüssel je Vertrauenszone**: ein Automations-Schlüssel darf nur das anfassen, was er synchronisiert — nie den Code-/Steuerungsbereich (hier: Log-Repo-Key statt Bot-Repo-Key auf dem Server) | 4.2 / 23.07. | **universell** |
| **Kurzsignale brauchen eine persistente Bezugs-Registratur**: eine Reaktion/Geste ist nur mit ihrem Bezug (welche Frage?) eine Antwort — der Bezug muss Neustarts überleben | 5.9 | **universell** |
| **Verhaltensklassen statt Einheitsreaktion**: Antwort-Signale lösen Arbeit aus, reine Wertschätzung wird still verbucht — nicht jede Geste verdient einen (kostenden) Lauf | 5.9 | **universell** |
| **Plattform-Varianten normalisieren, bevor verglichen wird** (hier: Emoji mit/ohne VS16) — sonst gehen Treffer still verloren | 5.9 | **anpassbar** (das Muster „kanonisieren vor Vergleich" ist universell) |
| **Zahlen-Anker nie aus LLM-Zusammenfassungen übernehmen** — Sprachmodelle zählen lange Listen unzuverlässig (drei Abfragen, drei Zahlen); zählbare Werte deterministisch aus dem Rohtext zählen | 5.25 (e) / 23.07. | **universell** |
| **Das Prüfnetz muss auch die eigenen Bauteile überführen** — zweimal am selben Tag fing eine frisch gebaute Selbstcheck-Zeile einen Fehler des Erbauers (Regex-Lücke im Repo-Schutz, fehlende Knopf-Registrierung) | 8.7 / Selbstcheck 23.07. | **universell** |
| **Kein Neustart/Deploy in Abwesenheit des Nutzers ohne Not** — jede Startmeldung ist eine Push-Störung; Bündel warten auf den Moment, in dem die Meldung zugleich der nächste Handgriff ist | Betriebspraxis 23.07. | **universell** |
| **Framework-Wechsel haben ein K.-o.-Kriterium VOR allen Feature-Vergleichen**: bleibt der bestehende (Kosten-)Auth-Weg nutzbar? Erst wenn ja, lohnt die Detailprüfung | 9.7 | **universell** |
| **Ablage-Strukturen aus echter Nutzung ableiten, nicht aus Theorie** — Themenstränge in den realen Logs zählen, klein starten, Erweiterung einplanen; ABER Nutzungs-Zahlen auf Test-Artefakte prüfen (der Fußball-Peak war Testmaterial, kein Fokus) | 6.6 / v2 23.07. | **universell** |
| **Ablage-Struktur ist plattformneutral**: Häuser/Zimmer = Ordner/Unterordner mit identischer Terminologie — die bespielende KI dahinter ist austauschbar | 6.6 / 4.3 | **universell** |
| **Vertrauen pro Quelle statt pro Werkzeug**: Ein pauschales „immer erlauben" auf ein Abruf-Werkzeug entfernt genau den Wächter gegen fremdgesteuerte Ziele — dauerhafte Freigaben gehören an die Domain/Quelle, nie ans Werkzeug; Alt-Einträge heilen sich beim Laden selbst | 5.25 (a) / 23.07. | **universell** |

## Betrieb & Infrastruktur

| Was | Punkt | Einschätzung |
|---|---|---|
| Unprivilegierter Dienst-Nutzer, gehärtetes System (Firewall, fail2ban, automatische Updates) | 1.1 / 1.2 | **universell** |
| Dienst-Verwaltung über den System-Dienstmanager statt Bastellösung | 1.8 | **anpassbar** (hier systemd, vorher launchd) |
| Geheimnisse in einer Umgebungsdatei außerhalb des Repos, nur für root lesbar | 1.6 | **universell** |
| Verifizierter Rollback-Pfad, bevor umgeschaltet wird | 1.12 | **universell** |
| Nie zwei Instanzen desselben Dienstes parallel | 1.10 | **universell** |
| Lokale Spracherkennung statt Cloud-Dienst | 1.3 / 1.4 | **anpassbar** (hier whisper.cpp) |
| Umschaltbare Qualitätsstufen bei teuren Verarbeitungsschritten (genau ↔ schnell) | 5.22 | **universell** |
| Konfiguration per Umgebungsvariable statt fester Pfade im Code | 0.5 / 0.6 | **universell** |
| SSH-Härtung nur mit Aussperr-Schutz: Key-Login vorab im zweiten Terminal testen, sshd_config-Backup neben das Original, erst dann Passwort-/Root-Login abschalten (real gewählter Alternativweg: Reinstall mit vorab hinterlegtem Key, 1.0) | 1.0/1.1 / adam-agent 10-server-harden.sh | **universell** |

## Arbeitsweise & Kommunikation

| Was | Punkt | Einschätzung |
|---|---|---|
| Drehbuch mit Status, Akzeptanzkriterium, Test und Nutzer-Bestätigung je Punkt; sequenziell | MIGRATION.md | **universell** |
| Eine lebende Datei mit Änderungshistorie statt Versions-Sammlung | Doku-Konvention | **universell** |
| Statusübersicht als „Inhaltsverzeichnis" mit Symbolen und gewichtetem Fertigstellungsgrad | CLAUDE.md | **universell** |
| Ein Schritt pro Nachricht für nicht-technische Nutzer, mit erwarteter Ausgabe | CLAUDE.md | **universell** |
| Shell-Eigenheiten beachten (keine Kommentarzeilen in Befehlsblöcken, Zwischenablage-Reihenfolge) | CLAUDE.md | **anpassbar** (hier zsh/macOS) |
| Neutrale Begrüßung: nie annehmen, wo oder an welchem Gerät der Nutzer sitzt | 0.4 | **universell** |
| Wunsch-Vokabular gegen die Plattform **messen statt raten**; für Nicht-Unterstütztes einen gleichwertigen Weg vorsehen, damit keine Bedeutung verlorengeht | 5.9 | **universell** |
| **Jede Messung braucht eine Kontrollprobe**, die durchfallen muss — sonst misst man womöglich nichts (hier: die Emoji-Sonde meldete alles als gültig, auch Unsinn) | 5.9 | **universell** |
| Abbruch-/Stopp-Signale nie auf ein sinnverwandtes Ersatzzeichen legen — Eindeutigkeit schlägt Bequemlichkeit | 5.9 | **universell** |
| Test erst nach Deploy-Beweis (Selbstcheck-Zahl als Beleg, dass der neue Stand wirklich läuft) | 5.2 (Merkregel) | **universell** |
| Kundenfähigkeit = **Klon-pro-Kunde** mit API-Backend (eigener Prozess, eigener Token, eigene Ablage), nie Multi-Tenant-Umbau des Einzelnutzer-Systems | Rotes Team D | **universell** |
| Keine neuen globalen Singletons — `user_id` in neuen Funktionen als Parameter führen, auch im Einzelnutzer-Betrieb | Rotes Team D | **universell** |
| Backend-Schalter `abo\|api` per env als **dokumentierte Sollbruchstelle** (Fanpost-Muster) — dokumentieren reicht, kein Vorab-Umbau | Rotes Team D / Strategie C | **universell** |
| **Fundament-Updates sind Wartungsereignisse:** Version pinnen, Update nur im Wartungsfenster nach gebündeltem Regressionslauf | Rotes Team B.1 / 8.2 | **universell** |
| **Abo nur fürs Arbeitspferd** mit hohem Dauervolumen; Spezialisten-/Neben-Rollen nie per Abo (lokal, Free-Tier oder Cent-Tokens mit 💰-Freigabe) | Strategie C.3 | **universell** |
| Rollenprofil „Hauptagent" **modellneutral** beschreiben (Werkzeuge, Freigabe-Schleife, Streaming, Kontext, Sprache) — macht jeden Kandidaten in Stunden prüfbar | Strategie D.2 | **universell** |
| **Daten und Regeln sind portabel, Modellgewichte nicht** — Weiterentwicklung in Memory/Regeln/Playbooks/Logs (RAG statt Gewichte) | Strategie D.3 | **universell** |
| Klienten-Setups laufen NIE über das persönliche Abo des Betreibers | Strategie / 9.3 | **universell** |
| Plattform-Limits (hier: Bot-Download 20 MB) beim Feature-Bau einpreisen; Ausweg dokumentieren statt still scheitern | Rotes Team B.4 / 5.12 | **anpassbar** (Telegram-Wert) |
| Web-Panels auf dem eigenen Server **nie öffentlich** — nur VPN/SSH-Tunnel; öffentliche Ports nur mit Secret + unerratbarem Pfad + Firewall-Eingrenzung | Rotes Team C.1 / 1.9 / 3.1 | **universell** |
| Dienst-Sandboxing auf Betriebssystem-Ebene (Schreibrechte nur aufs Arbeitsverzeichnis) als billige Schadensradius-Begrenzung | Rotes Team C.2 / 4d | **anpassbar** (hier systemd) |
| Geplanter nächtlicher Prozess-Hygiene-Neustart gegen Langzeit-Degradation, mit stiller Startmeldung bei sauberem Lauf | Rotes Team C.3 / 4d | **universell** |
| **Autonome Läufe takten sich nach der Ressource, die zuerst ausgeht** (Kontingent-Ökonomie: Durchhalten schlägt Klotzen; Eskalations-Kandidaten parken statt hochschalten) | CLAUDE.md Arbeitsprinzip | **universell** |
| **Transportgrenze ist keine Fähigkeitsgrenze** — was eine Leitung nicht am Stück fasst, wird verkleinert oder in Teile zerlegt (Einzelbilder + Tonspur), nie abgewiesen; das Original bleibt unangetastet, die Transportfassung ist eine Zweitdatei. Kettenwirkung geprüft: Puffer und Budget müssen **gekoppelt** bleiben (Budget vom Puffer abgeleitet, keine feste Byte-Zahl). Tatsächliche Nebenwirkung: der Selbstcheck deckte auf, dass eine zweite, längst vergessene Options-Stelle denselben Puffer braucht — eine Zahl an nur einer Stelle hätte den Bruch bloß verschoben | H1 | **universell** |
| **Ein Wächter muss außerhalb dessen leben, was er bewacht** — eine Selbstheilung im überwachten Prozess versagt genau im Ernstfall (Prozess tot = Rettung tot). Dazu zwei Nebenbefunde: „läuft“ ist kein Gesundheitsnachweis (geprüft werden Prozess, Dienst UND Invarianten), und die Rettung darf keine höheren Rechte brauchen als der Dienst selbst, sonst ist sie im Notfall gesperrt | B1 | **universell** |

---

## Offene Klärungspunkte für 9.6

- **Modell-Abhängigkeit prüfen:** Wie viel der Verhaltensregeln trägt ein schwächeres oder lokales Modell noch? Die Charta muss kennzeichnen, was ein Modell *können* muss, damit eine Regel greift.
- **Widerspruch Komfort ↔ Sicherheit — Grenzlinie gefunden (Adam-Entscheid 20.07.):** Auto-Freigaben (5.25) und „im Zweifel fragen" ziehen gegeneinander; die Linie verläuft **nicht** am Werkzeug, sondern an der **Herkunft der Zieladresse** — aus Nutzer-Eingabe oder eigener Suche: automatisch; von fremden Inhalten nachgereicht: fragen. In der Blaupause als eigenes Muster ausformulieren, weil es weit über WebFetch hinaus trägt (jede Automatik, deren Ziel von außen bestimmt werden könnte).
- **Was ohne Telegram bleibt:** Reaktions-Vokabular, Inline-Freigaben und Kanal-Routing sind eng an Telegram gebaut. Für die Blaupause das *Bedürfnis* beschreiben (schnelle Antwort ohne Tippen, Freigabe von unterwegs), nicht die Telegram-Lösung.
