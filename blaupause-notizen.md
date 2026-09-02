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
| **Wer fremden Text verarbeitet, bekommt keinen Schreibweg — er bekommt ein Formular.** Statt dem exponierten Prozess eine Schreibrechts-Ausnahme zu geben, erzeugt er einen strukturierten Auftrag ohne Fließtext; ein separates, deterministisches Werkzeug prüft ihn gegen Weißlisten (welche Dateien, welche Werte) und führt aus. Nebenwirkung, die den Ausschlag gab: Die Weißlisten sind nicht Beiwerk, sondern die Sicherheit selbst — neun der elf Prüfungen sind Ablehnungen | C1 | **universell** |
| **Eine Regel ohne Prüfer ist eine Bitte** — jede Disziplin-Regel bekommt eine maschinelle Entsprechung, sonst verfällt sie still. Beleg: Der Prüfer fand beim allerersten Lauf eine Lücke und beim zweiten das eigene, Minuten alte Skript | R2 | **universell** |
| **Einen Zielkonflikt auflösen statt ihn zu verwalten:** Feine Abtastung und schlanker Kontext widersprechen sich nur, solange jedes Einzelstück einzeln übergeben wird. Ein Übersichtsbild plus Verzeichnis kehrt das um — Überblick sofort, Details auf Abruf. Gilt über Video hinaus für jede dichte Datenmenge (Logzeilen, Messreihen, Seiten) | 5.28 | **universell** |
| **Aktualität gilt dem VERFAHREN, nicht nur der Versionsnummer** — regelmäßig prüfen, ob es einen besseren Weg gibt, aber Solides nicht wegwerfen, nur weil Neues existiert. Wo sich Neuheit nicht maschinell feststellen lässt, im Register ehrlich als „manuell prüfen“ führen statt eine Attrappe zu bauen | CLAUDE.md | **universell** |
| **Kein Eingriff ohne gesicherten Rueckweg — auch nicht durch das Sicherheitsnetz selbst.** Spiegelbild der Regel "kein Einspielen ohne Rollback-Stand": Wer eingreifen will, ohne zurueck zu koennen, richtet Schaden ohne Aussicht auf Besserung an. Im Trockenlauf haette der Waechter genau so einen gesunden Dienst beendet. Merkmal: Rettungslogik braucht dieselbe Vorpruefung wie die Aenderungslogik, die sie bewacht | B1 | **universell** |
| **Jede Vorgabe braucht drei Antworten: Wer prueft sie, wo wird sie sichtbar, auf welchem Weg kommt sie in die Ablage?** Fehlt eine, verfaellt sie still. Belegt durch drei Faelle derselben Klasse binnen 24 Stunden: fehlender Pruefer (R2), fehlender Gueltigkeits-Vermerk (11), fehlender Ablageweg (9.4). Die Nebenwirkung war jedes Mal dieselbe: nicht ein Fehler, sondern ein stiller Vertrauensverlust in die eigene Statusauskunft | R2 / 11 / 9.4 | **universell** |
| **Ein Messwerkzeug, das Teil des gemessenen Feldes ist, braucht einen Nachweis, dass es sich selbst herausrechnet.** Im Notbetriebs-Drill meldete die Prozess-Suche zwei Instanzen, obwohl eine lief — sie fand die eigene Befehlszeile. Gegenmittel: die Auskunft dort holen, wo der Beobachter nicht Teil der Menge ist (hier die Prozess-Kennung des Dienstverwalters). Nebenwirkung, die den Wert ausmacht: derselbe Trugschluss hatte einen Tag zuvor eine Phantom-Zweitinstanz vorgetaeuscht | Notbetriebs-Drill / B1 | **universell** |
| **Echtzeit-Faktor und Beschleunigung sind zwei Groessen — eine Kennzahl braucht ihre Einheit, sonst wird sie falsch gelesen.** Aus "6,3x" (Audiodauer je Rechenzeit) wurde in mehreren Bloecken "6,3x schneller"; die tatsaechliche Beschleunigung war 1,8x. Gegenmittel: Kennzahlen nie nackt weitergeben, sondern mit Bezugsgroesse — und vor der Uebernahme einmal selbst nachrechnen | 5.35 | **universell** |
| **Was deterministisch beantwortet werden kann, geht nicht durchs Modell.** Kalenderabfrage, Update-Pruefung, Versions-Abgleich, Nachzieher: alle lesen, formatieren und antworten ohne Modellaufruf. Zwei Gewinne in einem — es kostet kein Kontingent UND haelt Daten vom Anbieter fern. Erkennungsmerkmal: Wenn die Antwort aus einer Quelle ableitbar ist, braucht sie kein Urteil | 7.4 / 5.21 / C1 / C2 | **universell** |
| **Ueberblick verkleinert, Details in Originalauflaesung nachreichen** — dieselbe Zweistufigkeit fuer Bilder wie fuer Videos. Anlass: Beim Verkleinern geht zuerst genau das verloren, was Detailerkennung braucht (Kleingedrucktes, Zahlen). Zweiter Teil, der oft fehlt: Eine unsichere Erkennung muss sich VON SELBST als unsicher zeigen, nicht erst auf Nachfrage | 5.28 / Nachtrag V | **universell** |
| **Eine Aufzaehlung von Belegen ist keine Beweisfuehrung, solange nicht geprueft ist, ob die Belege im Material ueberhaupt vorhanden sein KOENNEN.** Konkret bei Bildern: Aufloesungs-Budget vor der Behauptung — Merkmale unter der Aufloesungsgrenze existieren nicht. Nebenwirkung, die den Wert ausmacht: Neun stimmige Merkmale ergaben eine falsche Bestimmung, weil keines davon physikalisch sichtbar war | Bild-Regel CLAUDE.md | **universell** |
| **Nach jeder Filter-/Sync-Aenderung das ERGEBNIS pruefen, nicht die Absicht** — was im Ziel liegt, nicht was die Konfiguration sagt. Anlass: Die Ausschluss-Regel existierte, wurde aber nie nachgemessen; rsync nimmt die erste zutreffende Regel und zog 146 KB Kontext mit. Vierter Fall derselben Klasse in zwei Tagen: Vorgabe da, Pruefung fehlt | Wirkungs-Regel CLAUDE.md | **universell** |
| **Ein Versprechen, das nicht ganz traegt, ist schlechter als ein kleineres, das haelt.** „Auf eigenem Server" heisst nicht „nur wir koennen es lesen" — gemessen: blankes Dateisystem ohne Verschluesselung. Der Gewinn bleibt gross (keine Auswertung, kein Profil, kein Handel), aber die Formulierung muss die Grenze nennen | Werte-Charta §3 | **universell** |
| **Zweistufigkeit als Grundmuster: erst ablegen, dann auf Abruf verarbeiten.** Dritte Anwendung derselben Idee — Video (Uebersicht/Details), Wartungsfenster (vormerken/ausfuehren), Link-Inbox (ablegen/verarbeiten). Gewinn jedes Mal derselbe: kein Aufwand fuer etwas, das nur geparkt werden sollte. Nebenwirkung, die den Ausschlag gab: Die WEICHE zwischen beiden Stufen ist die eigentliche Arbeit — hier kippte ein vorangestellter Pfeil den ersten Testlauf | 5.14 / 5.28 / 5.36 | **universell** |
| **Wer nicht schreiben darf, legt ab — und ein getrenntes Werkzeug traegt ein.** Dritte Anwendung (Boten-Postfach, Nachzieher, Freigabe-Protokoll): Der einspritzungsexponierte Prozess erzeugt strukturierte Dateien, ein deterministisches Werkzeug ausserhalb wendet sie an. Nebenwirkung, die den Wert ausmacht: Beim Protokoll faellt dadurch die Angriffsflaeche auf EINE Tabellenzeile zusammen — Umbrueche und Trennzeichen werden gesaeubert, mehr als eine Zeile kann ein untergeschobenes Urteil nicht bewirken | 9.4 / C1 / B | **universell** |
| **Eine Regel greift dort, wo sie GELESEN wird — der Fehler passiert aber dort, wo gehandelt wird.** Die Durchlauf-Regel stand in der Startlektuere, der Fehler geschah am Zugende: drei Wiederholungen trotz korrekter Regel. Gegenmittel: den Pruefer an die STELLE DES HANDELNS haengen (hier ein Stop-Hook), nicht die Ermahnung wiederholen. Nebenwirkung, die dazugehoert: Jeder solche Waechter braucht eine Notbremse, sonst wird er selbst zum Hindernis | Durchlauf-Wache | **universell** |

| **Schweigen darf nie bewirken, dass etwas geschieht — aber Schweigen ist auch kein Nein.** Der Fail-safe war als „gilt als abgelehnt" gebaut; das ist eine Ueberdehnung: Nichtantwort heisst uebersehen, vergessen, nicht da gewesen. Richtig ist: die Aktion unterbleibt, der Zustand bleibt **offen**, und die Frist **frischt auf** statt zu verfallen. Nebenwirkung, die den Wert ausmacht: Erst dadurch faellt auf, dass eine Frist sonst **erfundene Urteile ins Entscheidungs-Protokoll** geschrieben haette — ein Protokoll voller Neins, die nie jemand gesagt hat | 9.4 / B1 | **universell** |
| **Die Unterscheidung, die eine Nichtantwort erst lesbar macht: war der Mensch ueberhaupt da?** Keine Regung im Fenster → das Schweigen traegt keine Information, schlicht neu vorlegen. Regung im Fenster, aber kein Urteil → „gesehen, offen", und das ist ein Hinweis, dass die FRAGE unklar gestellt war. Nebenwirkung: Die Spur dafuer gehoert an EINE Stelle (ein Handler ganz vorn), nicht in dreissig Einstiegspunkte — eine Spur, die dreissigfach gepflegt werden muss, ist an der einunddreissigsten vergessen | 9.4 / B1 | **universell** |
| **Ein automatisierter Ablauf darf nie an einer menschlichen Antwort haengen bleiben — er parkt, meldet und geht weiter; die Antwort holt ihn spaeter ein.** Nebenwirkung, die den Ausschlag gab: Damit das traegt, muss die Auftragsliste **Abhaengigkeiten benennen** (`haengt_an`) — sonst weiss der Laeufer nicht, was nach einem geparkten Punkt noch unabhaengig ist, und muesste raten. Fehlende Angabe gilt als „unabhaengig", weil das die einzige Vorgabe ist, die nichts unterstellt | 9.8 / B2 | **universell** |
| **Eine Ueber-Korrektur ist auch eine Annahme.** „Ein Auftrag je Lauf" sollte das Kontingent schonen — und unterstellte damit genau das, wovon der Entwurf frei sein wollte: dass es knapp ist. Richtig ist, ohne die Zahl auszukommen: verkettet arbeiten, bis es nicht mehr geht. Nebenwirkung: Der Halt bei erschoepftem Kontingent musste ausdruecklich vom Fehlschlag getrennt werden — sonst haette der Laeufer sich selbst als kaputt gemeldet, obwohl nur die Zeit um war | 9.8 / A1 | **universell** |
| **Ein Ablaufdatum, das im Material nicht steht, darf nicht angezeigt werden.** Vor dem Bau der Anmelde-Wache gemessen: Das Abo-Token ist opak (108 Zeichen, kein JWT) — es enthaelt kein Ablaufdatum. Jede Restlaufzeit waere erfunden gewesen. Ehrliche Umkehrung: nicht vorhersagen, wann sie kippt, sondern sofort melden, DASS sie gekippt ist. Nebenwirkung, die dazugehoert: Die Pruefung darf nur den NAMEN des Geheimnisses lesen, nie den Wert — dafuer ein eigener Test, der den Wertzugriff im Quelltext verbietet | 9.9 / C2 | **anpassbar** |
| **Der Spitzenwert ist die Kennzahl, der Momentanwert die Falle.** Ollama sah mit 42 MiB harmlos aus und hatte 5,10 GiB Spitze — es laedt sein Modell erst bei der ersten Anfrage. Zweite Lehre: Der Lasttest war unnoetig, weil das Betriebssystem die Spitzen ohnehin mitfuehrt; ein abgelesener Wert aus dem echten Betrieb schlaegt einen simulierten und gefaehrdet nichts. Nebenwirkung, die den eigentlichen Befund lieferte: Beim Messen fiel auf, dass **kein Swap** existiert — und das, nicht Ollama, ist der Grund, warum Knappheit hier toedlich statt langsam waere | C1 | **universell** |

| **Zwei Listen driften — eine gemeinsame kann es nicht.** Der Waechter suchte nach Wortlauten fuer den Anmelde-Bruch, der Bot kannte laengst eine eigene, aus echten Vorfaellen gewachsene Liste: von sieben Marken war genau EINE in beiden, und der wichtigste Fall ging um ein Wort daneben ("oauth token expired" gegen "oauth token HAS expired"). Der Auftrag lautete, einen Test gegen den Drift zu bauen; staerker ist, ihn strukturell unmoeglich zu machen. Nebenwirkung, die den eigentlichen Gewinn brachte: Beim Umbau fiel auf, dass Horchen ohnehin der schwaechere Weg ist — der Bot WEISS es im Augenblick des Bruchs und kann eine Marke im eigenen Format schreiben, unabhaengig davon, wie der Anbieter morgen formuliert | G1 | **universell** |
| **Ein Pruefer, der nicht hinsehen kann, ist von einem, der nichts findet, nicht zu unterscheiden.** Beide Anmelde-Pruefungen endeten bei "nicht lesbar ist kein Befund" — genau die Krankheit, gegen die die Waechter erfunden wurden, diesmal IM Waechter. "Konnte nicht nachsehen" ist ein eigener Zustand. Nebenwirkung: Die Tests bewiesen nichts dagegen, weil sie den Systemaufruf durch eine Attrappe ersetzten — gruen heisst dort nicht "laeuft dort". Erst die Messung in der Zielumgebung klaert es | G2 | **universell** |
| **Ein Waechter ohne Daempfer schaltet sich selbst ab.** Ein anhaltender Befund haette sich minuetlich gemeldet: 60 Nachrichten je Stunde, ueber vierzehn Tage theoretisch zwanzigtausend. Ein Waechter, der zuschuettet, wird stummgeschaltet — und ist dann gar keiner mehr. Loesung: erste Meldung sofort, Wiederholung fruehestens nach einer Stunde, Entwarnung wenn der Befund wegfaellt. Nebenwirkung, die dazugehoert: Ohne ausdrueckliche Entwarnung weiss niemand, ob es behoben ist oder der Waechter nur muede wurde. Die Kette schreibt weiter minuetlich; nur der Mund wird leiser, nicht das Auge | G4 | **universell** |
| **Eine Wiedervorlage ohne Bremsweg wird selbst zum Halteschild.** Starre 24 Stunden haetten bei vierzehn Tagen Abwesenheit vierzehn Nachrichten je offener Frage ergeben. Loesung: Wartezeit waechst mit der Zahl der Vorlagen, gedeckelt bei viermal. Nebenwirkung, die den Wert ausmacht: Beim Bauen fiel auf, dass die Auffrischung den Zeitstempel ueberschrieb — nach vierzehn Tagen haette sich eine alte Frage als frisch gestellt gelesen, und gerade das ALTER sagt bei der Rueckkehr, was zuerst dran ist | G5 | **universell** |
| **Ein Fehlerfang an der falschen Stelle sieht aus wie ein Riegel, ohne einer zu sein.** Beim Beheben des Link-Abhak-Fehlers wollte ich try/except um den Aufruf legen — der reiht aber nur in die Warteschlange ein und kehrt sofort zurueck; der Lauf findet spaeter statt. Der Fang haette nur das Einreihen abgesichert und den Fehler VERDECKT, weil er ueberzeugend aussieht. Nachbedingungen gehoeren an das Objekt, das den Ausgang erlebt (hier: den Auftrag), nicht an die Stelle, die ihn ausloest | S1 / G6 | **universell** |
| **Eine Kennzahl, die von Hand nachgepflegt werden muss, wird irgendwann nicht nachgepflegt.** Der Regressionslauf hatte seine Gesamtzahl fest eingetippt: 30 gruene Zeilen, gemeldet "29/29" — und bei einem Fehlschlag haette er ebenso falsch gerechnet. Gefunden nur, weil ich die gruenen Zeilen einmal gegengezaehlt habe. Nebenwirkung: Der Fehler war in der Zaehlung selbst, also in genau dem Werkzeug, das alle anderen Fehler finden soll | 8.2 | **universell** |

---

## Offene Klärungspunkte für 9.6

- **Modell-Abhängigkeit prüfen:** Wie viel der Verhaltensregeln trägt ein schwächeres oder lokales Modell noch? Die Charta muss kennzeichnen, was ein Modell *können* muss, damit eine Regel greift.
- **Widerspruch Komfort ↔ Sicherheit — Grenzlinie gefunden (Adam-Entscheid 20.07.):** Auto-Freigaben (5.25) und „im Zweifel fragen" ziehen gegeneinander; die Linie verläuft **nicht** am Werkzeug, sondern an der **Herkunft der Zieladresse** — aus Nutzer-Eingabe oder eigener Suche: automatisch; von fremden Inhalten nachgereicht: fragen. In der Blaupause als eigenes Muster ausformulieren, weil es weit über WebFetch hinaus trägt (jede Automatik, deren Ziel von außen bestimmt werden könnte).
- **Was ohne Telegram bleibt:** Reaktions-Vokabular, Inline-Freigaben und Kanal-Routing sind eng an Telegram gebaut. Für die Blaupause das *Bedürfnis* beschreiben (schnelle Antwort ohne Tippen, Freigabe von unterwegs), nicht die Telegram-Lösung.

- **Zustell-Wächter** · ② · **universell** — Jedes System, das über einen fremden
  Dienst erreichbar sein muss, braucht einen Wächter für die **Gegenrichtung**.
  Alle unsere Wächter prüften, ob *wir* leben; keiner, ob man uns noch erreicht.
  Der Ausfall, bei dem jede Anzeige auf Grün steht, ist der teuerste.
  **Nebenwirkung, die niemand erwartet hatte:** Der Schlüssel steht bei Telegram
  im Aufruf-Pfad, also in jeder Fehlermeldung mit Adresse — der Wächter musste
  gegen das Ausplaudern gebaut werden, bevor er gegen den Ausfall wachen durfte.

- **Ein vorhandenes Bauteil ist kein erreichbares Bauteil** · ⑥ · **universell**
  — „Der Knopf existiert" wurde zu „der Knopf erscheint"; tatsächlich hing er an
  einer Bedingung, die bei Instagram nie zutraf. Vorhandensein prüfen heißt: den
  **Weg dorthin** prüfen, nicht die Zeile im Code.

- **Wo Struktur und Prüfer beide möglich sind, gewinnt die Struktur** · ⑥ ·
  **universell** — Ein Test meldet Drift; eine gemeinsame Quelle lässt ihn nicht
  entstehen (`authmarke.py`). Der Prüfer ist die Notlösung für das, was sich
  nicht zusammenlegen lässt. **In derselben Nacht zweimal angewandt:** die
  Wegwerf-Umgebung im Regressionslauf statt vierzehn einzelner Test-Korrekturen.

- **Prüfläufe brauchen eine Wegwerf-Umgebung** · ① · **universell** — Ein
  Testszenario hat Adam nachts um 01:44 eine echte Nachricht geschickt („Update
  von demo"). **Nebenwirkung, die die eigentliche Lehre ist:** Der Schaden ist
  nicht die Menge sinnloser Meldungen, sondern die **Gewöhnung** — wer gelernt
  hat, einen Absender zu überlesen, überliest auch dessen echte Meldung.

- **Attrappen belegen die Verkettung nicht** · ① · **anpassbar** — Hora bestand
  elf Tests und hatte drei Fehler, die erst der erste echte Lauf zeigte. Der
  schwerste: Ein geparkter Auftrag wurde abgehakt, Adams Zustimmung wäre ins
  Leere gelaufen. **Kein Test prüfte den Rückweg**, weil alle den Hinweg prüften.

- **Wer vom Ziel aus zieht, sichert nur, solange das Ziel wach ist** · ⑤ · **universell** — Eine Sicherung, die der Empfaenger anstoesst, faellt genau dann aus, wenn der Empfaenger laenger fehlt. **Nebenwirkung beim Bauen:** Der Ersatz-Schnappschuss liegt auf derselben Maschine und ist damit KEIN Backup, sondern ein Rueckweg — das musste in den Kopf des Skripts, sonst haelt ihn spaeter jemand fuer mehr.

- **Ein Riegel an einer Stelle ist eine Momentaufnahme** · ① · **universell** —
  Drei Riegel, weil jeder allein zu wenig deckt: die Wegwerf-Umgebung des
  Läufers (hilft nur, wenn über ihn gestartet wird), die Ersetzung im Test
  (hilft nur für *diesen* Test), der Prüfsatz (gilt auch für das, was noch
  niemand geschrieben hat). **Nebenwirkung:** Der Prüfsatz fand beim ersten Lauf
  nichts — und genau das war der Beleg, dass die ersten beiden schon saßen.

- **Eine anonyme Nachricht darf es im eigenen Haus nicht geben** · ① ·
  **universell** — Leitplanke 7 galt fürs Freigabe-Postfach, nicht fürs
  Boten-Postfach. **Nebenwirkung beim Suchen, die die eigentliche Lehre ist:**
  Ein abgekoppelter Prozess überlebt das Testende; eine Momentaufnahme direkt
  danach spricht den Täter frei. Wer nach einem Verursacher sucht, muss zuerst
  wissen, ob er überhaupt schon fertig ist.

- **Eine Kennzahl ohne Definition ist keine Messung** · ② · **universell** —
  5,10 GiB und 3017 MiB waren **beide** korrekt abgelesen und meinten
  Verschiedenes: `MemoryPeak` zählt den Datei-Zwischenspeicher mit,
  `MemAvailable` rechnet ihn heraus. **Nebenwirkung, die den Beleg lieferte:**
  Die Summe aller Spitzenwerte ergab 23 005 MiB auf einer 7940-MiB-Maschine —
  eine Zahl, die das Dreifache des Vorhandenen ergibt, kann keine Belegung sein.
  Die unangenehmere Sorte Fehler: Sie besteht jede Prüfung, die nur das Ablesen
  prüft.

- **Eine erfundene Zusammenfassung ist schlechter als keine** · ③ ·
  **universell** — „Schnell Rechnen Üben" für „wie man eine Rechnung schreibt":
  Die Form stimmt, der Inhalt ist erdacht, und **nichts an der Ausgabe verrät
  es**. Dieselbe Klasse wie die neun Merkmale bei vier Bildpunkten. **Der
  deterministische Gegenentwurf ist sprachlich schwächer und kann nicht lügen** —
  jedes Wort stand vorher im Text, Wort für Wort nachprüfbar. Das ist der Preis
  und der Gewinn in einem Satz.

- **Ein Wächter kann selbst zur Störquelle werden** · ④ · **universell** — Zwei
  fehlerhafte Wächter schickten zusammen 26 Nachrichten in dreizehn Minuten.
  Beide Fehler waren behebbar; **dass es keinen Riegel gab, der so etwas
  überhaupt begrenzt, war der eigentliche Mangel.** Die Obergrenze sitzt am
  **Ausgang**, nicht an der Quelle — eine Grenze an der Quelle hilft nur der
  bekannten Quelle, eine am Ausgang hilft allen, auch den ungeschriebenen.
  **Nebenwirkung, die die Bauart bestimmt hat:** Zurückgehaltenes darf nicht
  verschwinden. Es wird gezählt und in der nächsten durchgelassenen Nachricht
  genannt — sonst wäre die Meldung darüber selbst wieder eine Nachricht.

- **Ein Dämpfer, der Texte vergleicht, wird von einem Zeitstempel ausgehebelt**
  · ① · **universell** — „(seit 9 Min)" und „(seit 10 Min)" gelten als zwei
  Befunde: der eine neu, der andere weggefallen. **Der Dämpfer verdoppelt den
  Lärm, statt ihn zu dämpfen.** Meine erste Lösung bereinigte die Zahlen — eine
  Heuristik, die im Hintergrund rät. Die **Kennung** ist eine Zusage, die die
  Signatur erzwingt: Wer einen Prüfer anhängt, *kann* sie nicht vergessen.

- **Ein vergangener Fehler ist kein Zustand** · ② · **universell** — Der
  Zustell-Wächter hielt einen elf Minuten alten „Connection refused" für eine
  Störung, obwohl direkt daneben stand, dass alles läuft (null wartende
  Updates). Was zählt, ist nicht **ob** etwas schiefging, sondern **ob jetzt
  etwas hängt** — und dafür gab es einen direkten Messwert, den ich nicht
  ausgewertet hatte.

- **Eine Kette, die entscheidet, ist keine Entlastung, sondern ein zweiter
  Herr** · Entwicklungskette · **universell** — der Satz, an dem sich jede
  Automatisierungsstufe messen lassen muss.

- **Der Maßstab der Automatisierung: Wie oft muss Adam etwas tun, das keine
  Entscheidung ist?** · Entwicklungskette · **universell** — die messbare Form
  des Momo-Nordsterns. Alles andere (Zeitersparnis, Durchsatz) ist Nebenwirkung.

- **Der Kurier ersetzt den Transport, nie die Prüfung** · A3 · **universell** —
  Ein Weg, auf dem Arbeit ohne Gegenlesung ankommt, ist keine Leitung, sondern
  eine zweite Bauleitung. **Nebenwirkung beim Bauen:** Der Weg existierte
  bereits (`~/workspace` im Log-Abgleich) und war nur nicht benannt — gebaut
  wurde am Ende nichts, vereinbart alles. Das ist der billigste Fall.

- **Überblick auf Abruf schlägt Dauerfunk** · Statuszeile · **universell** —
  Adam wollte sehen, dass es läuft. Die naheliegende Antwort wäre eine
  stündliche Meldung gewesen; die richtige war eine Zeile in `/status`.
  **Ein Wächter, der regelmäßig „alles gut" sagt, wird überlesen — und dann
  auch die eine Meldung, die zählt.**

- **Eine geratene Schwelle kann den Takt nicht kennen — systemd kennt ihn** ·
  B2/Befund E · **universell** — Die Zeitgeber-Wache hatte zuerst eine feste
  Grenze von 26 Stunden und hätte beim **ersten** Lauf einen Fehlalarm erzeugt:
  Der Versions-Monitor läuft wöchentlich, sein letzter Lauf lag zu Recht 33
  Stunden zurück. **Nebenwirkung, die den Umbau erzwang:** Der richtige Maßstab
  stand die ganze Zeit daneben — `NextElapseUSecRealtime`. Ein überfälliger
  *nächster* Lauf ist taktunabhängig; ein altes *letztes* Datum ist es nie.

- **Kein Prüfweg darf voraussetzen, was ein Wächter als Fehler wertet** · K3 ·
  **universell** — Der Modell-Abgleich sollte einen API-Schlüssel nutzen; die
  Anmelde-Prüfung meldet genau dessen Anwesenheit als Alarm. Zwei Teile des
  Systems hätten gegeneinander gearbeitet, **und beide hätten recht gehabt**.

- **Ein Register, das mehr Arten kennt als sein Prüfer, erzeugt stille
  Nichtprüfung** · B2/Befund A · **universell** — `components.json` nannte
  `github_release`, der Monitor hatte keinen Handler dafür. Der Eintrag stand
  da, sah nach Abdeckung aus und wurde nie angesehen. **Nebenwirkung beim
  Bauen:** Beim Melden wäre mir fast derselbe Fehler ein zweites Mal
  unterlaufen — die Fundliste wurde zunächst nur ausgegeben, wenn es *auch*
  Updates gab. **Ein blinder Fleck ist meldepflichtig, gerade wenn es sonst
  nichts gibt.**
- **Umschalter mit ehrlichem Haken** · B3 · **universell** — gebaut: ein Modus-Knopf wurde von der Einmal-Aktion zum gespeicherten Zustand. Geprueft: dass beide Beschriftungen bedienbar sind und die Tiefe an der Sitzungserzeugung haengt. **Tatsaechlich aufgetreten:** Die sichtbare Beschwerde („er geht nicht mehr aus“) war die harmlosere Haelfte — die stille war ein `close_session` je Anfrage, das den Gespraechsfaden zerschnitten haette, ohne dass es je als Fehler aufgefallen waere. **Lehre: Wer eine Beschwerde behebt, muss pruefen, was am selben Schalter haengt, worueber sich niemand beschweren KANN.**
- **Erinnerung mit eigener Frist statt Anhängsel** · B2-Rest · **universell** — gebaut: `manual`-Registereinträge bekamen eine Fälligkeit. Geprüft: dass der erste Lauf schweigt und die Meldung sich nicht wiederholt. **Tatsächlich aufgetreten:** Beim Ausbau fiel eine eigene Prüfung um, weil sie an `github_release` als Beispiel für „unbekannte Art“ geheftet war — genau die Art, die dieser Ausbau ergänzt hat. **Lehre: Ein Prüfer darf sein Beispiel nicht aus dem Bestand nehmen, den er absichern soll — er muss einen Fall wählen, den es nie geben wird.**
- **Rechtegrenze benennen statt überspringen** · B2-Rest · **universell** — gebaut: `/updates` zeigt jetzt, was es nicht beantworten konnte. Geprüft: dass eine stumme Quelle nicht als „aktuell“ durchgeht. **Tatsächlich aufgetreten:** Der Befund war gar nicht gesucht — er fiel beim Bau des Knopfes auf, weil dieselbe Lücke, die im Monitor geschlossen war, im Updater noch offenstand. **Lehre: Wo zwei Stellen dieselbe Frage beantworten, wandert ein Fix nicht von allein mit.** Und: „braucht Root“ und „Quelle kaputt“ müssen verschieden klingen, sonst wird die dauerhafte Rechtegrenze als Dauerstörung gelesen und abgeschaltet.
- **Warnung weiterreichen statt selbst rechnen** · B4/5.20 · **universell** — gebaut: die Limit-Vorwarnung des Anbieters wird durchgereicht, mit Dämpfer je Kontingent-Art. Geprüft: dass sie genau einmal je Zustand kommt und keine Prozentzahl erfindet. **Tatsächlich aufgetreten:** Beim Nachmessen des vorhandenen Verbrauchszählers kam heraus, dass er 63 Eingabe-Token je Antwort auswies — der Zwischenspeicher fehlte ganz, und der ausgewiesene Betrag war ein Nennwert, der sich über vierzehn Tage auf 3400 Dollar summierte, ohne je abgebucht zu werden. **Lehre: Eine Kennzahl, die niemand je nachgerechnet hat, ist keine Messung, sondern eine Behauptung mit Nachkommastellen** — und eine Geldzahl ohne den Zusatz „wird nicht berechnet“ erschrickt zu Recht.
- **Die Reihenfolge ist der Mechanismus** · B5 · **universell** — gebaut: vier Vorlese-Regeln für Datum, Kennnummern, Jahre und den Bezugs-Vermerk. Geprüft: dass jede Regel greift **und** dass sie nicht zu weit greift. **Tatsächlich aufgetreten:** Die eigentliche Arbeit steckte nicht in den Regeln, sondern in ihrer Abfolge — Datum muss vor der Versionsregel laufen, Kennnummern vor der Jahresregel, sonst zerstört die eine, was die andere braucht. **Lehre: Wo mehrere Umschreibungen auf denselben Text wirken, ist die Reihenfolge Teil der Logik und gehört geprüft wie Code** — sie bricht lautlos, kein Syntaxfehler meldet sie. Zweite Lehre: **Bei Umschreibungen ist die Gegenprobe wichtiger als die Probe.** Eine Regel, die zu viel greift, erzeugt falsche Auskünfte; eine, die fehlt, nur nüchterne.
- **Was ein Prüfer trägt, kann er nicht prüfen** · Connis Fund 28.07. · **universell** — gebaut: die Stundenblumen bewachen den 4-Uhr-Check mit, der Check bewacht über die Ketten-Prüfung die Blumen. Geprüft: beide Richtungen, und dass ein bloß verspäteter Lauf nicht alarmiert. **Tatsächlich aufgetreten:** Die Zeitgeber-Wache konnte jeden Zeitgeber prüfen außer dem, der sie selbst startet — der Fund kam von außen, nicht aus der Selbstprüfung, und das ist genau der Punkt. **Lehre: Gegen den blinden Fleck auf den eigenen Träger hilft keine bessere Selbstprüfung, sondern nur eine zweite Instanz mit eigenem Antrieb. Kreuzverschränkung statt Selbstbezug.** Nebenbefund: Beim Anhängen der Prüfungen stand die Meldung „Alle Tests bestanden“ plötzlich mitten in der Datei — sie hätte Erfolg gemeldet, bevor die letzten zwei Prüfungen liefen. **Wer an ein Prüfskript hinten anbaut, muss dessen Abschlussblock mitnehmen.**
- **Die Positivliste in Verkleidung** · B6 · **universell** — gebaut: das Blinde-Flecken-Verfahren mit drei Fragen und ein kleiner Wächter dazu. Geprüft: mit nachgestelltem Rückfall, dass der Wächter wirklich anschlägt. **Tatsächlich aufgetreten:** Die allererste Anwendung von Frage ③ fand einen Fall im eigenen Bestand — über der Zeitgeber-Suche stand „gesucht, nicht aufgezählt“, und darunter filterte sie auf drei Namensanfänge. **Lehre: Ein Kommentar, der eine Vorgabe formuliert, ist kein Beleg, dass der Code darunter sie einhält — er ist eher ein Hinweis darauf, dass jemand sie für schwer einzuhalten hielt.** Zweite Lehre: **Ein Suchmerkmal muss eine Umbenennung überleben.** Bei Zeitgebern ist das nicht der Name, sondern das Ziel — was in unser Verzeichnis zeigt, ist unseres.
- **Der falsch benannte Täter** · Anführungszeichen-Falle · **universell** — die Regel lautete „solche Dateien nur über Edit/Write ändern“, und dann sprengte ein **frisch geschriebenes** Write genau daran. **Lehre: Wenn eine Regel wiederholt bricht, ist zuerst zu prüfen, ob sie die richtige Ursache benennt.** Nicht das Werkzeug war es, sondern das deutsche Anführungszeichen in einem doppelt gequoteten String — unabhängig davon, wie der String entsteht. Vier Wiederholungen an einem Tag waren nötig, um das zu sehen. **Nachtrag am selben Abend: Auch die zweite Fassung war zu breit.** Der Bruch entsteht nur beim gemischten Paar — typographischer Öffner, gerader Schließer; sauber gesetzte Paare sind harmlos, und `bot.py` enthält mehrere. **Lehre zweiter Ordnung: Wer eine Regel nachschärft, macht sie gern strenger statt genauer — und eine zu breite Regel schlägt grundlos an, bis jemand sie abschaltet.** Der Prüfer meldet deshalb genau das Ungleichgewicht, nichts sonst.
- **Sparmodus gebaut und ruhend** · B7 · **universell** — gebaut: die Reaktion auf die Limit-Warnung (Tiefe senken), Schalter vorhanden, **standardmäßig aus**. Geprüft: dass er ohne Zutun nicht greift und die Umstellung nie stillschweigend geschieht. **Tatsächlich aufgetreten:** Beim Anbauen der Prüfungen stand die Meldung „Alle Tests bestanden“ zum **zweiten Mal an diesem Tag** mitten in der Datei — beim zweiten Mal war sie in Sekunden erkannt. **Lehre: Eine Verhaltensänderung, die der Mensch nicht angestoßen hat, gehört ihm — der Mechanismus darf gebaut sein, das Scharfstellen ist seine Entscheidung.** Und: Ein Bot, der seine Arbeitstiefe unbemerkt senkt, sieht von außen aus wie ein schlechter gewordener Assistent; deshalb wird die Umstellung immer genannt.
- **Deutsche Zusammensetzungen unterlaufen die Wortgrenze** · B8 · **universell** — gebaut: das Auftragsbuch mit Ampel-Einstufung, ruhend. Geprüft: dass Grün nur aus der geschlossenen Liste kommt und Rot sie schlägt. **Tatsächlich aufgetreten:** Die eigene Prüfung fiel beim ersten Lauf über `\bklient\b` — „Klient“ schlug an, **„Klientendaten“ nicht**, ausgerechnet beim heikelsten Wort. Deutsche Zusammensetzungen hängen ihr Bestimmungswort vorn an; eine schließende Wortgrenze macht jede Stichwort-Bremse für genau die Fälle blind, für die sie gebaut wurde — Kundenliste, Passwortdatei, Löschauftrag. **Lehre: Bei einer Bremse ist ein Fehlalarm die richtige Fehlerrichtung — lieber einmal zu oft rot als einmal zu wenig.** Zweite Lehre: **Grün darf nie aus einem Urteil im Einzelfall kommen, nur aus einer benannten Liste** — eine Fehleinstufung ist der einzige Fehler dieses Konzepts, den niemand bemerkt.
- **Die letzte Zeile ist eine Positionsannahme** · Hora-Halt 28.07. · **universell** — gebaut: der Fehlgrund sucht die auffälligen Zeilen statt der letzten. Geprüft: an genau der Ausgabe, an der es scheiterte. **Tatsächlich aufgetreten:** Der Halt selbst war richtig (Notbremse nach drei Fehlläufen), aber die Meldung lautete „der Befehl meldete: ✓ Medien-Eingangsschutz“ — die letzte von 29 Zeilen, und eine grüne. Die rote stand mittendrin. **Lehre: Wo eine Ausgabe Zeile für Zeile berichtet, ist die Position kein Hinweis auf den Inhalt** — man muss nach dem Merkmal suchen, nicht nach dem Ort. Und: **Eine Fehlermeldung, die eine Hand zur Diagnose braucht, ist in einer Abwesenheit keine Meldung.**
- **Ein Prüfer darf keine Formatierung verlangen** · Nennwert-Riegel · **universell** — gebaut: die Auflage, dass Kostenzahlen nie ohne das Wort „Nennwert“ auftauchen. **Tatsächlich aufgetreten: zwei Fehlschläge nacheinander, beide meine.** Erst schaute das Umfeld-Fenster nur nach unten — ein erklärender Kommentar steht per Konvention aber **darüber**. Dann bestand der Prüfer auf „Nennwert“ und lehnte „NENNWERT“ ab. **Lehre: Wer auf ein Wort prüft, muss die Schreibweise offenlassen und in beide Richtungen sehen — sonst verlangt er eine Formatierung statt der Sache.** Nebenbei: Beim ersten Treffer war die Versuchung groß, den Prüfer weichzuspülen; richtig war, die Sache am Ursprung klarzustellen.
- **Ein unvollständig übernommener Befehl** · Hora-Halt 28.07. · **universell** — der gescheiterte Auftrag war eine Kopie des Selbstcheck-Aufrufs aus `daily_check.sh`, hatte aber dessen **Umgebungs-Vorbereitung** nicht mitgenommen (`CLAUDE_MEMORY_DIR`). Kein Defekt am System. **Lehre: Wer einen Befehl aus einem Skript in eine Auftragsliste kopiert, kopiert nur die sichtbare Zeile — die Vorbereitung darüber ist Teil des Befehls.** Dieselbe Familie wie der geerbte-Umgebungsvariablen-Fehlalarm vom 25.07.
- **Eine Pruefung, die die Pruefende verschont, ist keine** · Gegenpruefung 18.08. · **universell** — gebaut: sechs frische Sitzungen ueber zehn ruhende Punkte, mit dem Auftrag [finde, was nicht traegt] statt [pruefe, ob es stimmt]. Geprueft: rund vierzig Befunde, drei davon schwer, zwei deploy-blockierend. **Tatsaechlich aufgetreten:** Die Gegenpruefung hat nicht nur die Bau-Sitzung widerlegt, sondern auch die Abnahmen der KONTROLLE - die Wortgrenzen-Regel und die Text-Pruefer-Klasse waren beide abgenommen worden. Das war kein Betriebsunfall der Auflage, sondern ihr Beweis. **Lehre: Wer eine Gegenpruefung anordnet, muss sie auf die eigenen Urteile mit anwenden - sonst prueft sie nur nach unten.** Und der Satz, an dem der ganze Tag haengt: **[gruen] ist nicht [wahr].** In allen drei schweren Faellen war der zustaendige Selbstpruefer gruen.
- **Die Quelle bestimmt die Schwelle** · Log-Wachposten · **universell** — gebaut: ein deterministischer Posten, der neue Log-Zeilen gegen Muster prüft. Geprüft: elf Zeilen, ausführend, Attrappe nur am Postfach-Rand. **Tatsächlich aufgetreten:** Der erste Entwurf ließ eine ECHTE Zeile aus der Fehlerdatei durchfallen (`TimedOut: Timed out`) — kein Muster traf. Das war kein Musterfehler, sondern ein Denkfehler: **In einer Fehlerdatei ist jede neue Zeile bereits der Befund.** Dort nach Fehlermerkmalen zu suchen heißt zu prüfen, ob ein Fehler auch wirklich einer ist. **Lehre: Bevor man Muster schärft, fragt man, ob die Quelle sie überhaupt braucht** — und man misst an echten Daten, nicht an erfundenen.
- **Wer „disable" gesagt hat, hat es gewollt** · Zeitgeber-Wache · **universell** — gebaut: die Suche findet jetzt auch Timer von der Platte, nicht nur geladene. **Tatsächlich aufgetreten:** Sie fand im selben Moment einen achten Zeitgeber, eine bewusst abgeschaltete Altlast — und hätte ihn ab sofort täglich als still gemeldet. **Lehre: Wer die Erfassung erweitert, muss im selben Zug den Ausweg für bewusst Ruhendes bauen**, sonst tauscht man einen blinden Fleck gegen einen Dauer-Alarm, und der ist schlimmer: Ein stiller Wächter wird vergessen, ein lauter wird abgeschaltet. Die Absicht stand dabei schon in systemd selbst (`UnitFileState`) — es brauchte keine zweite Liste.
- **Ein stiller Fang macht aus einem Tippfehler eine Falschauskunft** · F-5 Limit-Marke · **universell** — gebaut: Persistenz des Warn-Zustands über einen Neustart. Geprüft: ausführend, Marke geschrieben und wieder eingelesen. **Tatsächlich aufgetreten:** Die Sicherung schrieb `json.dumps`, während das Modul in dieser Datei `_json` heißt. Ein `NameError` — und `except Exception: pass` hat ihn verschluckt. Die Funktion tat lautlos nichts, der Zustand wurde nie gesichert, und ein Prüfer, der den Code nur gelesen hätte, wäre grün geblieben. **Lehre: Ein stiller Fang verwandelt jeden Fehler in seiner Reichweite zu einem Ausbleiben — auch einen Tippfehler, den ein Absturz sofort gezeigt hätte.** Wo er nötig ist (eine Marke darf den Betrieb nicht aufhalten), gehört ein Protokoll-Eintrag hinein: verschluckt ja, unsichtbar nein. Zweite Lehre, härter: **Nur das Ausführen hat es gezeigt.**
- **Adams Arbeitsliste** · Arbeitsmodus „Geteilt" 19.08. · **anpassbar** — gebaut: eine Repo-Datei, in der jeder Bau seinen hinterlassenen Menschen-Schritt im selben Commit einträgt, mit Minutenschätzung und „was es freischaltet". **Warum überhaupt:** Handgriffe lagen verstreut über Chats und Berichte; wer sie finden wollte, musste wissen, wo er sucht. **Lehre: Ein Handgriff, den niemand findet, ist kein wartender Punkt, sondern ein verlorener** — und die Minutenschätzung ist kein Schmuck, sondern das, was ein knappes Zeitfenster überhaupt füllbar macht. Übertragbar auf jedes System, in dem Automatik und Mensch sich abwechseln; die Startbestände sind projektspezifisch.
- **Eine Regel ohne Zeitgeber ist eine Bitte an den Menschen** · Nachtbetrieb 19.08. · **universell** — „Nächte arbeiten, Tage entscheiden" galt seit Juli und trug praktisch nicht. **Gemessen statt vermutet:** Nachtarbeit fand statt (26.07. 02:40–03:40, 19.08. 01:27), aber ausschließlich nach einem ausdrücklichen Abend-Anstoß. Die Ursache ist strukturell: Die Bau-Sitzung hat **keinen eigenen Zeitgeber**, und die Durchlauf-Wache greift nur innerhalb eines laufenden Zuges. **Lehre: Bevor man eine Arbeitsregel wiederholt, prüft man, ob sie überhaupt einen Auslöser hat** — sonst ermahnt man jemanden für etwas, das er gar nicht auslösen kann. Der autonome Läufer auf dem Server hatte diesen Auslöser von Anfang an; die Sitzung am Rechner nie.
- **Eine Frage ohne Wirkung ist schlimmer als keine** · Wachposten-Schlusszeile · **universell** — gebaut: Die Zeile „Engywuck wecken?" ist durch eine Stand-Ansage ersetzt. **Tatsächlich aufgetreten:** Adam hat mit einem Daumen geantwortet, und nichts geschah — der Postfach-Versand registriert keine offene Frage, also griff die stille Quittung (ein Häkchen, kein Lauf). Beide Hälften fehlten: kein Weg für die Antwort, und nichts zu wecken. **Lehre: Wer eine Frage stellt, muss vorher wissen, wo die Antwort ankommt** — sonst verlässt sich der Mensch darauf, entschieden zu haben, und niemand merkt, dass nichts geschah. Der Rang folgt daraus: erst die Wirkung bauen, bis dahin die Frage weglassen.
- **Protokollieren ist nicht Melden** · ASCII-Befund 20.08. · **universell** — gemessen: Ein `JSONDecodeError` stand vierundzwanzig Tage in `bot-errors.log`, mit ihm die Spur zu einer Ansage an Adam, die nie ankam. Die Fehlerbehandlung hat sauber gearbeitet und trotzdem versagt. **Lehre: Ein Protokoll ist ein Ablageort, kein Meldeweg** — wer Fehler nur protokolliert, hat sie aufgehoben, nicht gemeldet. Der Log-Wachposten ist die Antwort darauf, und dieser Fund war sein erster Beleg.
- **Wer den Weg umgeht, umgeht die Prüfung darin** · ASCII-Befund 20.08. · **universell** — gemessen: Die zerbrochene Auftragsdatei war nicht ASCII-verdorben (der Code schreibt durchweg `ensure_ascii=False`, Gegenprobe mit Umlauten und gemischtem Anführungspaar geht heil durch), sondern **von Hand geschrieben** und dabei mitten in einer Zeichenkette gesplittet. **Lehre: Eine Schreibfunktion ist zugleich die einzige Stelle, die für Wohlgeformtheit einsteht** — wer die Datei direkt schreibt, verliert diese Garantie, ohne es zu merken. Dieselbe Familie wie die Heredoc-Regel. Und: **Zwei Vermutungen können gleichzeitig plausibel und beide falsch sein** — hier hielten weder „der Umweg existiert" noch „der Umweg war die Ursache" der Messung stand.
- **Die Messform ist Teil der Messung** · Instanz-Zählung 20.08. · **universell** — gemessen: `pgrep -cf "python.*bot.py"` meldete zwei Instanzen, `pgrep -af` zeigte eine. Der zweite Treffer war **die eigene SSH-Kommandozeile**, weil sie den Musterstring trug. **Tatsächlich aufgetreten, und das ist die eigentliche Lehre:** Ich habe daraufhin den Tagescheck verdächtigt, seinen Ausdruck per Heredoc nachgestellt — und wieder zwei bekommen, weil **auch die Nachstellung** den Musterstring in ihrer Aufrufzeile trug. Beinahe hätte ich einen Prüfer „repariert", der nie kaputt war. **Lehre: Wer ein Messartefakt nachstellt, muss prüfen, ob die Nachstellung dasselbe Artefakt erzeugt** — sonst bestätigt sie sich selbst. Der Vorbehalt stand seit dem 25.07. im Drehbuch und die richtige Lösung seit dem 24.07. in `start_waechter.py`; verlässlich ist `systemctl show -p MainPID`.
- **Eine falsche Begründung ist auch bei richtigem Ergebnis ein Fehler** · Entwarnung 01:23 · **universell** — die nächtliche Entwarnung „zwei Prozesse, aber der alte fuhr noch herunter" war im Ergebnis richtig (es lief genau einer) und in der Ursache falsch (es war die Messform). **Lehre: Eine plausible Erzählung, die zum richtigen Ergebnis führt, verdeckt den echten Mechanismus** — und beim nächsten Auftreten sucht man an der falschen Stelle. Wer entwarnt, muss die Entwarnung belegen, nicht erklären.
- **Ein Angebot kommt an, eine Frage nicht** · Wachposten-Knopf · **universell** — gebaut: eine Schaltfläche an der Postfach-Meldung, die den Befund deterministisch ins Auftragsbuch legt. **Der Unterschied ist nicht sprachlich:** Vorher endete die Meldung mit einer Frage, die niemand beantworten konnte; jetzt trägt sie einen Weg. **Tatsächlich aufgetreten beim Bauen:** Die Attrappe des Prüfers hatte die alte Arität und hätte den neuen Parameter verschluckt — dieselbe Klasse wie am 18.08., wo eine Attrappe genau die falsche Signatur trug, die der Fehler hatte. **Lehre: Eine Prüf-Attrappe spiegelt die echte Signatur, niemals `**kwargs`** — ein nachsichtiger Rand macht jeden Tippfehler im Aufruf unsichtbar. Zweite Lehre: **Der zugestimmte Auftrag bleibt gelb.** Adam stimmt dem Hinterlegen zu, nicht dem Bauen; wer daraus grün macht, dehnt eine Zustimmung aus, die so nie erteilt wurde.
- **Ein Prüfer, der ohne die Sache läuft, belegt nicht die Sache** · Phase-7-Messung · **universell** — gemessen: Der CalDAV-Prüfer ist grün und läuft **ausdrücklich ohne Netz und ohne Zugangsdaten**; er belegt Formatierung und Fehlerverhalten, nicht dass die Verbindung trägt. Vorbildlich ist, dass er das selbst sagt. **Lehre: Wo ein Prüfer den Kern der Sache nicht erreichen kann, muss er die Lücke benennen** — sonst liest ein grüner Lauf sich wie eine funktionierende Anbindung. Verwandt mit „grün ist nicht wahr", aber die andere Richtung: Hier ist grün ehrlich und trotzdem kein Beleg.
- **Ein Fund macht noch keine Regel** · Phase-7-Messung · **universell** — der Verdacht „die Status-Zeilen sind zu pessimistisch" traf bei **einer von vier** zu; die anderen drei waren korrekt offen. **Lehre: Wer aus einem berichtigten Status auf den Rest schließt, ersetzt eine Falschaussage durch eine größere.** Die Prüfregel heißt „Status ist ein Befund", nicht „Status ist meist zu pessimistisch" — jede Zeile wird einzeln gemessen.
- **Ein Ordner, der lügt, ist schlimmer als ein leerer** · A1 Drossel-Fix · **universell** — gemessen: Zurückgehaltene Nachrichten lagen in `sent/`, weil die Drosselung „kein Fehler, sondern eine bewusste Entscheidung" sei. Der Satz stimmt und die Ablage trotzdem nicht: Adam vermisste am 20.08. eine angeforderte Datei, die dort als zugestellt geführt wurde. **Lehre: Ein Ablageort ist eine Aussage über den Zustand, keine Begründung für ihn** — wo etwas liegt, muss stimmen, auch wenn der Grund es dorthin gebracht hat. Zweite Lehre: Drosselung ist der einzige vorübergehende Zustand mit **bekanntem Ende** — man muss den Abstand nicht raten, man kann ihn rechnen.
- **Die geschlossene Liste zeigt in die sichere Richtung** · A1 Fehlerklassen · **universell** — vorübergehende Fehler werden aufgezählt, alles andere gilt als dauerhaft. Andersherum (alles Unbekannte wiederholen) wäre die bequemere Bauweise und die falsche: Ein dauerhafter Fehler liefe fünfmal ins Leere, und Adam wartete fünfmal. **Lehre: Bei einer geschlossenen Liste entscheidet nicht ihr Inhalt über die Sicherheit, sondern welche Seite den Zweifelsfall bekommt.**
- **Wer Inhalte umleitet, muss den neuen Weg mitbauen** · A4 Wachposten-Archiv · **universell** — gebaut: zwei Fassungen, ein deutscher Satz an Adam, die Einzelheiten ins Archiv. **Tatsächlich aufgetreten:** Der Auftrag sagte „ins Archiv, auf das Engywuck ohnehin zugreift" — er griff nicht darauf zu, weil der Kurier die neue Datei nicht kannte. Die Details wären auf dem Server verblieben, und niemand hätte es bemerkt: **eine Stille, die wie Ordnung aussieht.** Gefunden erst beim Nachmessen des Kuriers, nicht beim Bauen der Trennung. **Lehre: Eine Umleitung ist erst fertig, wenn der neue Zielort nachweislich erreicht wird** — „liegt im Archiv" ist eine Aussage über den Schreibort, keine über den Leser.
- **Ein Prüfer, der seine Erwartung aus dem Geprüften bezieht, kann nie rot werden** · Menü-Sortierung · **universell** — die Sortier-Prüfung verglich die Reihenfolge gegen `bot._BEFEHL_ZUERST`, also gegen dieselbe Konstante, die sie absichern sollte. **Gemessen:** Die Gegenprobe (Konstante auf „hilfe" geändert) blieb grün. Erst mit der Erwartung **im Prüfer selbst** schlug sie an. **Lehre: Der Sollwert gehört auf die Prüfseite, nie auf die geprüfte.** Dieselbe Klasse wie die pgrep-Nachstellung desselben Vormittags, die das Artefakt erzeugte, das sie nachweisen sollte — beide Male sah die Messung richtig aus und maß sich selbst.
- **Nach einem Rücksetzen den Bytecode wegräumen** · Gegenprobe Menü · **universell** — nach `cp bak bot.py` meldete der Prüfer weiter den geänderten Zustand: Python las `__pycache__`. Eine Minute Verwirrung, aber die Klasse ist dieselbe wie oben — **die Messform ist Teil der Messung**. Bei jeder Gegenprobe, die Dateien zurückspielt, gehört der Cache mit weg.
- **Eine Text-Prüfung, die beim Umbau rot wird, hat recht gehabt** · Doku-Spiegel & E4 · **universell** — zwei Prüfer wurden rot, als Menü und Hilfetext aus dem Quelltext in eine Laufzeit-Liste wanderten. Beide suchten Schreibweisen (`BotCommand("update_ja"`, `"/name — "`). **Der Reflex wäre, sie anzupassen; richtig war, sie umzubauen** — jetzt messen sie die Liste selbst. **Lehre: Wenn ein Umbau einen Prüfer rot macht, ohne die Sache zu ändern, prüfte er die Form.** Das ist der billigste Zeitpunkt, das zu merken.
- **Eine Quittung, die sich selbst mitzählt, wird nie ruhig** · Quittungs-Fix · **universell** — der Riegel „nur schreiben, wenn sich etwas geändert hat" griff eine Runde lang nicht: Die Quittung listete sich selbst unter ihrer Fracht, also änderte sie sich beim zweiten Lauf zwangsläufig. **Gefunden vom Prüfer, nicht beim Bauen** — mein Fix war fertig und plausibel. **Lehre: Eine Aussage über einen Vorgang gehört nicht in die Menge, über die sie aussagt.** Verwandt mit der Prozess-Zählung, die sich selbst mitzählte, und dem Prüfer, der seinen eigenen Erklärkommentar traf — dieselbe Familie: Der Beobachter steht im Bild.
- **Ein Verlauf, in dem jeder Eintrag dasselbe sagt, ist keiner** · 155 Commits an einem halben Tag · **universell** — jeder Fünf-Minuten-Lauf schrieb einen Commit, allein wegen der Uhrzeit in der Kopfzeile. **Lehre: Ein Zeitstempel ist keine Änderung.** Wo eine Datei regelmäßig neu erzeugt wird, wird sie **jenseits ihres Zeitstempels** verglichen, bevor sie ersetzt wird — sonst verdeckt der Lärm genau die Änderungen, für die man den Verlauf führt.
- **Ein undokumentierter Endpunkt ist keine Schnittstelle, sondern eine Wette** · A2 · **universell** — gemessen: HTTP 403 in drei Kopfzeilen-Varianten, in der echten Bot-Umgebung. Nicht 404 (er existiert), nicht 401 (das Token wird erkannt) — **erkannt und nicht berechtigt**, weil der Bot ein Setup-Token trägt und der Endpunkt das Sitzungs-Token erwartet. **Die im Auftrag benannte Sollbruchstelle trat ein, bevor Aufwand hineinfloss** — das ist der günstigste Zeitpunkt. **Lehre: „Nicht baubar" ist ein Ergebnis, kein Fehlschlag**, wenn die Diagnose ihre drei Teile trägt: welcher Weg, woran er scheiterte, welche Wege offen bleiben. Und der offene Weg (zweites Token auf dem VPS) wird **benannt und nicht gegangen** — er kostet eine dauerhafte Angriffsfläche für eine frühere Warnung, und diese Abwägung gehört dem Menschen.
- **Ein Zähler bewacht eine Sache, nicht zwei** · Drossel-Runden · **universell** — der Versuchszähler sollte Fehlschläge begrenzen, zählte aber auch Drossel-Runden mit; bei längerem Rückstau wären Nachrichten im Endlager gelandet, **die nie gescheitert sind**. **Lehre: Wer zwei verschiedene Ereignisse in einem Feld zählt, kann keine Grenze mehr sinnvoll setzen** — dieselbe Verwechslung wie beim Dämpfer, der „habe ich das gemeldet" und „wie viele zeige ich" in einer Frage beantwortete. Gefunden von der Kontrolle, nicht vom Bauenden.
- **Ein Bericht über einen Filter muss denselben Filter spiegeln** · Quittung, zweiter Durchgang · **universell** — nach dem ersten Fix schrumpfte die Ausschluss-Liste von 5.207 auf 120 Zeilen und war damit **immer noch falsch**: Der Bericht prüfte den DATEINAMEN, rsync schließt über `--exclude='.*'` aber ganze VERZEICHNISSE aus. Übrig blieben Pip-Metadaten aus `.pdfenv/`, jede mit „bitte melden, das sollte mitkommen". **Aus zu viel Länge war eine aktive Falschauskunft geworden** — schlimmer als vorher, weil sie zum Handeln auffordert. **Lehre: Wer beschreibt, was ein Mechanismus tut, muss dieselbe Bedingung prüfen wie der Mechanismus** — nicht eine ähnliche. Und: **Ein erster Fix, der eine Zahl stark verbessert, ist deshalb noch nicht richtig** — 120 statt 5.207 sah nach Erfolg aus und war der Moment, in dem man aufhört zu messen.
- **Eine übernommene Pflicht ist noch kein Mechanismus** · A6.1 · **universell** — Engywuck hatte die tägliche Sichtung am 20.08. als stehende Disziplin übernommen; das war ehrlich gemeint und trug trotzdem nur, solange die Aufmerksamkeit reicht. Der Tagescheck legt den Vermerk jetzt ins Auftragsbuch, wo die Kontrolle ihn beim nächsten Start **vorfindet**. **Lehre: Zwischen „ich mache das ab jetzt" und „es liegt beim nächsten Start da" liegt derselbe Unterschied wie zwischen Regel und Prüfer** — und beide Zustände fühlen sich beim Vereinbaren gleich an. Wer eine Pflicht übernimmt, sollte im selben Zug fragen, woran sie hängen wird, wenn niemand daran denkt.
- **Nach dem Verhalten fragen, nicht nach dem Ding** · A3 · **universell** — der Auftrag suchte einen „Selbstanstoß" im Quelltext, fand keinen und schloss auf eine Lücke. Tatsächlich **endet der Worker beim Limit gar nicht**: Er wartet in Häppchen und arbeitet danach weiter. Es gibt keinen Weckruf, weil niemand einschläft. **Lehre: „Gibt es X?" ist eine schwächere Frage als „was geschieht in Fall Y?"** — die erste findet nur, was einen Namen hat. Und der zweite Teil, der genauso zählt: **Ein Beleg, der eine Vermutung bestätigt, ist keine verlorene Arbeit.** Die Zusage trug, aber bis heute nahmen es alle an, statt es zu wissen.
- **Eine Beschreibung, die mehr verspricht als der Bau, ist gefährlicher als eine fehlende** · Stundenblumen-Kopftext · **universell** — dort stand seit Wochen, die Blume „wecke bei Auffälligem ein Modell". Im Quelltext gibt es keinen einzigen Modellaufruf. **Niemand prüft nach, was schon dasteht.** Dritter Fall dieser Klasse (Dämpfer-Docstring, „das Archiv, auf das Engywuck ohnehin zugreift") — und jedes Mal hätte sich jemand auf etwas verlassen, das es nie gab.
- **Ein Vorfall ohne Commit sieht aus wie kein Vorfall** · scp in den VPS-Klon · **universell** — ich habe ein Prüfskript per `scp` direkt ins Repo-Verzeichnis des Servers gelegt statt nach `/tmp`; der nächste `git pull` brach daran ab. **Weil nichts committet war, fühlte es sich wie eine Lappalie an** — es war die Governance-Klasse 8.7 in ihrer unauffälligsten Form: Repo-Stand und laufender Code laufen auseinander, und es zeigt sich erst beim Deploy. **Lehre: Die Schwere eines Vorfalls bemisst sich an dem, was er hätte anrichten können, nicht an dem, was sichtbar wurde.** Der Fix ist eine Zeile im bestehenden Tagescheck — **melden, nie aufräumen**: Eine automatische Löschung könnte Handarbeit vernichten, die jemand mit gutem Grund dort abgelegt hat.
- **Wer eine neue Zustandsablage einführt, trägt sie im selben Zug in die Wegwerf-Umgebung ein** · A6.1 im Prüflauf · **universell** — der Regressionslauf setzt seit dem 26.07. Wegwerf-Pfade für Postfach, Freigaben, Hora und Blumen. Das **Auftragsbuch fehlte** — und am Tag, an dem A6.1 dort hineinschrieb, stand prompt ein Prüf-Eintrag im echten Buch (20.08., 13:58). Der Weg dorthin war indirekt: Der Zielumgebungs-Prüfer startet den **echten** Tagescheck. **Lehre: Die Liste der Riegel wächst langsamer als die Liste der Orte, an denen ein Test schreiben kann** — deshalb gehört der Riegel zum Bau der Ablage, nicht zur späteren Aufräumrunde. Und der Nachweis am Ende muss **jede** dieser Ablagen messen, nicht nur die erste, für die man ihn gebaut hat.
- **Ein für harmlos gehaltener Befund war die Spur zum schweren** · F-6 · **universell** — die `NOT in sudoers`-Zeile im Journal habe ich als Lärm eingeordnet und in die F-Liste geschoben. Beim Nachmessen des **Landeorts** (Engywucks Präzisierung: der Wachposten liest `bot-errors.log`, nicht das Journal) stellte sich heraus: Sie stammt aus meinen eigenen Prüfläufen — und über dieselbe Kette schrieb ein Prüflauf ins echte Auftragsbuch. **Lehre: „Harmlos" ist eine Einordnung, keine Messung.** Wer den Lärm zurückverfolgt, statt ihn wegzuräumen, findet manchmal das, was ihn erzeugt.
- **Was gefiltert wird, gehört ans Ende** · 7.4 Terminlinks · **anpassbar** — der Zugangslink steht bewusst **hinter** dem lesbaren Teil der Terminzeile, nicht mittendrin. Grund: Der Vorlese-Filter nimmt Adressen heraus, und was er aus der Mitte reißt, hinterlässt einen zerbrochenen Satz. **Lehre: Wer weiß, dass ein Teil seiner Ausgabe später weggefiltert wird, ordnet sie so, dass das Wegfallen nichts zerstört.** Gilt für jede Ausgabe mit zwei Empfängern — hier Auge und Ohr.
- **Die Zahl war nie das Kriterium** · 7.2 Ausfall-Hinweis · **universell** — ich hatte den Ausfall-Hinweis an `len(zeilen) > 1` gehängt, um eine Doppelung zu vermeiden. Der Prüfer fand sofort den Fall, in dem genau **eine** Aufgabe überlebte: Der Hinweis fiel weg, und der Teilausfall wurde still. **Lehre: Wenn eine Bedingung eine Zahl prüft, obwohl die eigentliche Frage ein Zustand ist, trifft sie irgendwann den falschen Fall.** Die Frage war nie „wie viele Zeilen", sondern „steht der Hinweis schon da".
- **Der zweite Ort wird vergessen** · Status-Zeilen-Messung 20.08. · **universell** — drei von vier stichprobenartig geprüften OFFEN-Zeilen waren Falsch-Wahrheiten, eine davon über einen Monat lang: Der Punkt war **vollständig erfüllt**. Das Muster ist nicht Nachlässigkeit, sondern **fehlende Rückkopplung**: Wer baut, schreibt den Commit; die Status-Zeile ist ein zweiter Ort, und der zweite Ort wird vergessen. Dieselbe Klasse wie der Doku-Spiegel, eine Ebene höher. **Lehre: Wo ein Zustand an zwei Stellen geführt wird, driften sie** — entweder man verbindet sie mechanisch, oder man misst regelmäßig. Ein Prüfer scheitert hier daran, dass „gebaut" nur gegen ein Akzeptanzkriterium in Prosa entscheidbar ist; also bleibt die Messung, angewandt **vor** jeder Vorlage.
- **Gebaut wurde anders als skizziert — das ist kein Fehler, aber es macht blind** · dieselbe Messung · **universell** — 5.20 sollte einen eigenen Zeitgeber bekommen und wurde eine Zeile im vorhandenen Tagescheck (besser: ein Wächter weniger). 9.4 sollte ein HTTP-Endpunkt werden und wurde erst ein Postfach. **Beide Male war der Bau gut und die Zeile falsch.** Lehre: Wer von der Skizze abweicht, muss die Skizze nachziehen — sonst sucht der Nächste nach etwas, das unter anderem Namen längst dasteht.
- **Kontingent-Stand aus den Antwort-Kopfzeilen** - A2 - **universell.** Was gebaut: Merker fuer jeden vorbeikommenden Rate-Limit-Stand plus Abruf `/kontingent` mit Altersangabe. Kettenwirkung geprueft: Warnpfad (F-5) unveraendert, Postfach unberuehrt, kein zusaetzlicher Aufruf. **Tatsaechlich eingetretene Nebenwirkung:** Der Bau war winzig - die Arbeit lag im **Widerlegen des eigenen „geht nicht“**. Vier geprueften Wegen lang galt A2 als nicht baubar; der fuenfte stand die ganze Zeit offen, weil die Zahl gar nicht abgefragt werden muss - sie kommt mit jeder Antwort mit. Gefunden nicht durch Nachdenken, sondern weil **Adam nicht lockerliess** und ich daraufhin im CLI-Buendel nachsah, woher die Zahl ueberhaupt stammt. Lehre: Bei „geht nicht“ zuerst fragen, **woher die vorhandene Loesung ihre Daten nimmt** - nicht, welchen Endpunkt man selbst anrufen koennte.
- **Eine Quelle fuer eine Linkart** - 6.2/6.4 - **universell.** Was gebaut: fuenf handverteilte Kanal-Verweise auf eine zentrale Funktion zusammengefuehrt. Kettenwirkung geprueft: Inline-Knoepfe bewusst unangetastet, Regressionslauf 50/50. **Tatsaechlich eingetretene Nebenwirkung:** Der frisch geschriebene Pruefer wurde rot und hat **nicht den Code, sondern meine Lesart widerlegt** — ich hatte einen Kommentar („Buttons loesen KEINEN Dialog aus, anders als tg://-Textlinks“) als Vorschrift fuer den Knopf gelesen; er war die **Begruendung**, warum der Knopf den Deep-Link nutzen darf. Damit drehte sich der ganze Befund um: nicht der Knopf ist der Zweifelsfall, sondern der Textlink. Lehre: **Einen Kommentar, der ein Verhalten begruendet, nicht als Regel fuer dieses Verhalten lesen** - und einen Pruefer schreiben, der die eigene Annahme angreifen kann.
- **Rueckweg nur, wo er existiert** - 5.13 - **universell.** Was gebaut: Zitat-Bezug im Pin-Merker. Kettenwirkung geprueft: Geschwister-Zweig (persoenliche Notiz) mitgenommen, Dateihandle-Nebenbefund gleich mit, 51/51. **Tatsaechlich eingetretene Nebenwirkung:** Die interessante Entscheidung war nicht, **wie** man verlinkt, sondern **wo man es laesst** — im Privatchat vergibt Telegram keine adressierbare Nachricht, also steht dort die blosse Nummer. Die Versuchung war, trotzdem irgendeinen Link zu bauen, damit es einheitlich aussieht. **Ein Link, der ins Leere fuehrt, ist schlechter als keiner: er sieht aus wie ein Rueckweg und ist keiner.** Die Pruefzeile sichert ausdruecklich die Abwesenheit des Links, nicht seine Anwesenheit.
- **Eine Invariante brechen, ohne zu luegen** - A2.2 - **universell.** Was gebaut: `/kontingent` misst bei leerem Stand einmal frisch. Kettenwirkung geprueft: Befehlsbeschreibung, Anzeigetext und Register mitgewandert; Aufrufstellen auf zwei begrenzt und gemessen. **Tatsaechlich eingetretene Nebenwirkung:** Der Pruefer der Auflage „kein anderer Pfad ruft die Messung“ zaehlte die **Definitionszeile** als dritten Aufruf mit — der Beobachter im Bild, zum wiederholten Mal in diesem Projekt (Prozess-Zaehlung, Quittungsliste, Erklaerkommentar). Lehre: **Wer Vorkommen zaehlt, muss sich aus der Zaehlung herausrechnen** — und die gefaehrlichste Stelle dafuer ist die Definition dessen, was man zaehlt. Zweite Lehre: Wird eine Invariante bewusst gebrochen, ist die **Beschreibung Teil des Bruchs** — sonst entsteht die umgekehrte Falsch-Wahrheit, bei der der Bau mehr tut, als der Text zugibt.
- **Wenn die Schnittstelle schweigt, die Oberflaeche fragen** - A2.2 - **universell.** Was gebaut: Kontingent-Prozentwerte ueber eine echte Sitzung am Pseudo-Terminal. Kettenwirkung geprueft: Ereignisweg unveraendert (Zustand/Ruecksetzzeit kommen weiter gratis mit), Werte werden **zusammengefuehrt statt ersetzt**, 51/51. **Tatsaechlich eingetretene Nebenwirkung:** Der Bau war das Kleinste; die Arbeit lag im **Ausschliessen von fuenf Wegen** — und der entscheidende Hinweis kam aus Adams **Screenshot seiner eigenen Oberflaeche**, nicht aus dem Code. Zweitens: `/usage` ist lokal, also **kostet der Abruf nichts** — damit fiel die gesamte Kosten- und AGB-Abwaegung weg, die ich vorher um den Modell-Lauf herum gebaut hatte. Lehre: **Wenn eine Anwendung etwas anzeigt, existiert der Wert** — die Frage ist nie ob, sondern ueber welchen Kanal. Und: Zwei Anlaeufe scheiterten daran, dass ein **Einstiegsdialog die Eingabe verbrauchte**; bei Oberflaechen-Automatisierung ist der halbfertige Zustand der Normalfall, nicht die Ausnahme.
- **Der Schalter gehoert an den Ausgang, nicht an die Stelle** - Pruefumgebung - **universell.** Was gebaut: Trockenlauf-Weiche in den drei Wirkungs-Ausgaengen des Tagescheck plus Umleitung der Ablage. Kettenwirkung geprueft: Normalfall in der Gegenrichtung gemessen, 51/51 und 20/20. **Tatsaechlich eingetretene Nebenwirkung:** Die erste Messung zeigte, dass **heute schon nichts passiert** — aber nur, weil dem inneren Lauf die **Dateirechte** fehlten. Beinahe haette ich daraus „kein Handlungsbedarf“ gemacht. Lehre: **Ein Leck, das zufaellig nicht leckt, ist ein Leck** — die Frage ist nicht, ob es heute passiert, sondern was es unter anderen Rechten taete. Zweitens, unangenehm: Beim Pruefen habe ich selbst per `cp` ins VPS-Repo geschrieben (Governance 8.7) und es erst durch `git status` gemerkt — zum zweiten Mal in zwei Tagen. Der Weg ueber Commit und `git pull` ist keine Foermlichkeit, sondern der einzige, der den Klon sauber laesst.
- **Wer eine Meldung bekommt, muss etwas damit tun koennen** - Ebene B, 9.6-Stoff - **universell, Grundsatz statt Bau** (Engywuck-Entscheid 21.08.). Meldungen eines Systems zerfallen in drei Klassen, und jede braucht einen anderen Empfaenger: **(1) Adam muss entscheiden** — geht an ihn, mit einem Weg, auf dem seine Antwort ankommt (sonst gilt „keine Frage ohne Wirkung“). **(2) technisch, wird bearbeitet** — geht ins Auftragsbuch; die mechanisierte taegliche Sichtung ist die Quittung, nicht ein Versprechen. **(3) reines Protokoll** — bleibt im Log. Der Fehler, den das verhindert: Alles an Adam zu schicken, weil es sicherer wirkt. **Eine Meldung, mit der der Empfaenger nichts anfangen kann, ist Laerm** — und Laerm trainiert das Wegsehen, bis die eine wichtige Meldung mit untergeht. Zur Unsichtbaren Komplexitaet gehoert deshalb nicht nur, dem Endnutzer Technik zu ersparen, sondern **jeder Instanz nur das zu zeigen, was sie beantworten kann.** Im Zweifel bleibt Adam der Rueckfall.
- **Von aussen kommen nie Anweisungen** - Sicherheits-Grundsatz - **universell, hoechster Rang** (Adam 21.08.). Jeder Eingang - Mail, Webseite, PDF, Dateiname, Kalendereintrag, Messenger - liefert **Information, nie Befehl**; auch dann nicht, wenn dort Befehlszeilen stehen. **Warum das hier gratis ist:** Adam gibt niemals per Mail Anweisungen, also zerstoert das harte Verbot keinen Anwendungsfall. **Wo kein legitimer Fall existiert, kostet das Verbot nichts** — und genau solche Stellen sollte man kategorisch schliessen statt heuristisch. Zweite Richtung mitdenken: Sensibles verlaesst das System nicht ueber unverschluesselte Kanaele. **Der Messenger ist der heiklere Weg, nicht der harmlosere** — eine uebernommene Kennung spricht aus der Rolle des Berechtigten, und die Herkunfts-Schranke prueft die Kennung, nicht den Menschen. **Reihenfolge ist Teil des Kriteriums:** erst bauen und pruefen, dann mit fremden Daten arbeiten. Fuer ein Produkt gilt: Ohne diese Trennung ist es nicht fertig, egal wie gut es sonst ist.
- **Schranken fragen nicht nach Absicht, sondern nach Reichweite** - Eingangs-Absicherung 1-10 - **universell, hoechster Rang.** Was gebaut: neun Riegel gegen Anweisungen aus Fremdinhalten. Kettenwirkung geprueft: 52/52 und 21/21 in der ZIELUMGEBUNG, drei Gegenproben. **Tatsaechlich eingetretene Nebenwirkung, und sie ist die eigentliche Lehre:** Zwei der neun Befunde betrafen Code, den ich SELBST geschrieben hatte — und einer davon war eine Fehlannahme ueber die Bedeutung einer leeren Liste (`allowed_tools=[]` liest sich wie „keine Werkzeuge“ und bedeutet das Gegenteil; es steht woertlich in der Anbieter-Doku). **Wer eine Sicherheitsoption setzt, muss ihre Semantik NACHLESEN, nicht erschliessen** — sie sieht oft aus wie das, was man erwartet. Zweitens: Bei drei der neun Punkte sagte ein KOMMENTAR das Richtige und der Code etwas anderes (Suchtreffer, harmlose Dateinamen, Absenderpruefung). **Ein Kommentar ist eine Absichtserklaerung; nur ein Pruefer, der ausfuehrt, ist eine Zusage.** Drittens: Jede Schranke braucht eine **Gegenrichtung** in der Pruefung - eine, die alles abweist, besteht jede Sicherheitspruefung und macht das Werkzeug kaputt.
- **Der Pruefer misst die Funktion, nicht die Verdrahtung** - Engywucks Probelauf 22.08. - **universell, die teuerste Lehre des Projekts.** Was gebaut: acht schwere Befunde an frischem, am selben Tag gebautem Sicherheitscode. Kettenwirkung geprueft: 52/52 und 21/21 in der Zielumgebung, sieben Gegenproben. **Tatsaechlich eingetretene Nebenwirkung:** Von neun Pruefzeilen, die ich fuer ausfuehrend hielt, waren fuenf **umgehbar** - und in allen fuenf Faellen aus demselben Grund: Sie riefen die Funktion auf, aber niemand pruefte, ob sie noch AUFGERUFEN wird. Fabrik ja, Aufrufer nein. Bereinigung ja, Aufruf nein. Kopf-Zeichenkette ja, Kontext nein. **Der Kopfbefund des eigenen Berichts hatte gar keinen Pruefer** - der Commit trug seinen Namen, die Schutzzeilen liessen sich entfernen, alles blieb gruen. Die Faustregel daraus, hart: **Jede Zeile, die Quelltext LIEST - `getsource`, `read_text`, `find`, Zeilenzaehlung -, ist umgehbar.** Acht von acht gemessenen Faellen. Wo eine Abwesenheit zu messen ist, hilft der Syntaxbaum (echte Aufrufe statt Zeilen mit dem Namen); wo Verhalten zu messen ist, muss der Pfad AUSGEFUEHRT werden, notfalls durch Herausziehen der Entscheidung in eine eigene Funktion. Zweite Lehre: **Ein Fix, der eine Handlung in einen Dialog verlagert, ist erst fertig, wenn der Dialog zeigt, worueber er entscheiden laesst** (H4: die Adresse stand nirgends).

## Ultracode-Nachlese Eingangs-Absicherung (23.08.2026, Engywucks Befund A–L)

- **Prüfstand-Hermetik über Umgebungsvariablen · Befund L · universell** —
  geprüft: ob die zwölf Testdateien wirklich isoliert sind. *Nebenwirkung, die
  keiner erwartet hat:* Sie waren es nie. `bot.py` hat `USER_PREFS_FILE`
  niemals gelesen; jeder Lauf beschrieb die echte Ablage, und auf dem VPS
  standen danach alle drei Kanal-Kennungen auf einer Test-Attrappe. **Eine
  gesetzte Variable, die niemand liest, sieht genauso aus wie eine, die wirkt** —
  das ist der Kern, und er gilt für jedes System mit Prüfumgebung.

- **Ein fester Betriebspfad macht Prüfer ortsabhängig blind · D/E/F · universell**
  — geprüft: die Pfad-Auflösung gegen die Repo-Wurzel. *Nebenwirkung:* **Vier**
  Prüfer trugen den VPS-Pfad fest ein, darunter einer, den ich am selben Tag
  selbst geschrieben hatte. Solange die geprüfte Logik nur Zeichenketten
  verglich, waren sie pfadunabhängig grün — die Blindheit entstand erst durch
  die Verbesserung. **Die gefährliche Richtung ist nicht „rot am falschen
  Rechner", sondern „grün aus dem falschen Grund".**

- **Ein Ausweichpfad bei Unsicherheit ist die Umkehrung von fail-closed ·
  Befund C · universell** — geprüft: der Leseweg für Fremddokumente.
  *Nebenwirkung:* Der `else`-Zweig fing nicht nur die unbekannten Formate,
  sondern auch **jeden Fehlschlag der Erkennung** — ein PDF mit Füllbytes vor
  der Kennung und jeder `open()`-Fehler. Wer die Prüfung zum Scheitern brachte,
  bekam den weniger geschützten Weg. Für ein paar Bytes.

- **Ein Geltungsbereich, der an einem Nebeneffekt hängt, ist keiner ·
  Governance-Ortstest · universell** — geprüft: nichts, es fiel beim Beheben
  von D/E an. *Nebenwirkung:* Der Test „Klon hat keine lokalen Änderungen" galt
  nur auf dem VPS — nicht durch eine Bedingung, sondern weil der fest
  eingetragene Pfad am Bau-Ort nicht existierte. Mit dem echten Pfad existierte
  er immer, und der Test schlug dort an, wo ein unsauberer Baum normal ist.

- **Zwei Gefahren in einer Liste ergeben in beide Richtungen Fehler · Befund G ·
  universell** — geprüft: die Marker der Geheimnis-Erkennung. *Nebenwirkung:*
  Weil Lesen und Schreiben denselben Topf teilten, war der Gedächtnis-Ordner
  beim bloßen Lesen dialogpflichtig — **gegen die eigene Zusage im
  System-Prompt** — und gleichzeitig fehlten die Ziele, die tatsächlich
  Geheimnisse ausgeben. Der Doku-Spiegel war gebrochen, ohne dass etwas kaputt
  aussah.

- **Ein zu scharfer Riegel ist kein sicherer Riegel · H und I · universell** —
  geprüft: wie oft die Schranke im Alltag anspringt. *Nebenwirkung:* Fünf
  harmlose Recherchefragen waren dialogpflichtig, und elf von sechzehn normalen
  Adressen ebenso. Der Kommentar im Code **benannte diese Erosion bereits** —
  nur maß sie niemand. Eine Warnung ohne Messung altert zur Dekoration.

- **Der Prüfer für „fester Pfad" musste dreimal enger gefasst werden · anpassbar**
  — *Nebenwirkung:* Sein erster Entwurf schlug bei sieben Stellen an, von denen
  **sechs berechtigt** waren — eine davon war seine eigene Erklärung. Genau der
  Fehler, den die Regel vom 22.08. beschreibt, begangen beim Bau des Prüfers
  für eine andere Regel. **Ein Prüfer wird nicht dadurch besser, dass er mehr
  findet.**

- **Zustand bereinigen, während der Besitzer läuft, ist wirkungslos · Befund L,
  Nachlese · universell** — geprüft: dass die gesäuberte `prefs.json` auf dem
  VPS sauber bleibt. *Nebenwirkung, die tatsächlich eintrat:* Sie war es nach
  dem Neustart wieder **voll mit Testwerten**. Der laufende Bot hatte die alten
  Werte beim Start in den Speicher geladen und beim nächsten Speichern
  zurückgeschrieben — meine Bereinigung lief an ihm vorbei. **Die richtige
  Reihenfolge ist: anhalten, sichern, bereinigen, starten.** Ich hatte das
  Risiko sogar im Laufplan notiert und trotzdem am laufenden Dienst gearbeitet;
  eine notierte Gefahr ist keine abgewendete.

## Differenzmesser (23.08.2026, Engywucks Bauauftrag)

- **Die Gegenprobe als LADEBEDINGUNG statt als Prüfung · Schritt 1 · universell**
  — geprüft: dass jede Differenzart eine Gegenprobe hat. *Nebenwirkung, die den
  Entwurf trägt:* Sie ist damit **kein Prüfer über einen Prüfer** (Wächter
  dritter Ordnung, verboten), sondern eine Bedingung beim Laden. Wer eine Art
  ohne `<name>_gegenprobe` hinzufügt, bekommt einen Fehler statt einer stillen
  Aufnahme. **Eine Art, die nie etwas meldet, sieht sonst aus wie eine, die
  passt.**

- **Die Ist-Menge über die Endung zu bilden ist eine Aufzählung mit
  Regex-Anstrich · Differenzart B · universell** — geprüft: welche
  Zustandsablagen der Regressionsläufer verriegelt. *Nebenwirkung:* Meine eigene
  Fassung vom selben Vormittag suchte `_DIR` und `_FILE` und verfehlte damit
  **die Ampel** — vier Schlüssel, die laut `CLAUDE.md` das Heikelste im Projekt
  führen. Ein Prüflauf hätte ihre Regeldatei überschreiben können, und der
  Prüfer, der genau das verhindern sollte, hätte geschwiegen. **Ein Muster ist
  keine Menge, auch wenn es wie eine aussieht.**

- **Der Regressionslauf entscheidet die Einzelfälle besser als Nachdenken ·
  Schritt 2 · anpassbar** — *Nebenwirkung:* Ich habe `AUFTRAGSBUCH_RIEGEL`
  umgebogen, weil er wie eine Zustandsablage aussah. Der Lauf meldete sofort:
  Er ist ein **Konfigurationsdokument**, das die Frist der Probewoche trägt und
  nur gelesen wird — umgebogen zeigt er ins Leere, und ein Riegel, der ins Leere
  zeigt, sperrt nichts. Engywucks Anweisung „einzeln entscheiden" ließ sich so
  billiger befolgen als durch Lesen.

- **Eine geschätzte Größenordnung vor dem Bauen nachmessen · F-12 · universell**
  — der Auftrag nannte „`Path.home()` in 16 Produktivmodulen". Gemessen: 39
  Stellen, davon **30 bereits durch einen Umgebungsschalter abgedeckt**. Übrig
  neun. *Die Nebenwirkung ist die Entscheidung:* Für neun Stellen eine
  Dauermeldung zu bauen, hätte genau die Erosion neu erzeugt, die am selben Tag
  bei zwei anderen Filtern behoben wurde. **Gebaut wurde deshalb nichts — die
  Zahl ging in die F-Liste.**

- **Wer eine Menge bildet, muss auch die Menge der SCHREIBWEISEN bilden ·
  Engywucks Gegenprüfung 23.08. · universell** — geprüft: dass die Ist-Menge
  der Zustandsablagen nicht über die Endung gebildet wird. *Nebenwirkung, die
  erst seine Gegenprüfung fand:* Ich habe die **Dateimenge** korrekt gebildet
  (`git ls-files` statt Endungsmuster) und dabei die **Idiom-Menge
  eingefroren** — `_environ_get_name` kennt genau eine Schreibweise von sechs.

  **Das ist die tückischere Ebene**, weil der Fehler *nach* der befolgten Regel
  auftritt und deshalb wie Sorgfalt aussieht. Man hat die Aufzählung an der
  einen Stelle abgeschafft und an der nächsten neu angelegt, ohne es zu merken.

  Gemessen ist er heute folgenlos (kein `os.getenv` im Produktivcode, kein
  Subscript auf eine Ablage) — **er ist morgen blind, nicht heute.** Genau
  deshalb gehört er in die F-Liste und nicht in eine Sofortrunde.

- **Ein dynamisch geladenes Modul braucht seinen Eintrag in `sys.modules`,
  bevor es läuft · Einhängung · anpassbar** — *Nebenwirkung:* `@dataclass`
  schlägt beim Aufbau `sys.modules.get(cls.__module__)` nach; fehlt der Eintrag,
  stirbt der Import mit `'NoneType' object has no attribute '__dict__'`. **Ich
  habe die Meldung zuerst der falschen Stelle zugeschrieben** und dort
  umgestellt — die Umstellung war für sich richtig, aber nicht die Ursache.
  Gefunden erst, als ich den Ladevorgang einzeln ausführte und den vollen
  Stapel las statt der letzten Zeile.

- **Die Schreibweisen-Regel gilt auch für den Prüfer des Prüfers · Engywuck über
  sich selbst, 23.08. · universell** — *Nebenwirkung, und sie ist die
  eindrücklichste des Tages:* Seine Prüfsonde für die Einhängung suchte
  `ast.Call`-Knoten mit „differenz" im Aufruf und fand **null** — weil der
  Aufruf über ein dynamisch geladenes Modul geht. **Er hat damit genau die
  Regel gebrochen, die er mir eine Stunde vorher geschrieben hatte**, und es
  war das zweite Mal am selben Tag, dass seine eigene Messung zu eng war.

  Die Lehre ist nicht „auch Kontrolleure irren", sondern präziser: **Eine Regel
  über Mengenbildung gilt für jede Ebene, auf der jemand eine Menge bildet** —
  auch für die Sonde, mit der man die Befolgung der Regel misst. Wer sie nur
  auf den geprüften Code anwendet, hat sie halb verstanden.

- **Vor der Gegenprobe hinschreiben, WELCHE Zeile rot werden soll · Engywucks
  Handgriff · universell** — *Anlass:* Ich hatte an einem Tag zweimal eine
  Gegenprobe gefahren, bei der die falsche Zeile rot wurde, und es beide Male
  fast als Beleg genommen. Der Handgriff kostet einen Satz und verwandelt
  „die falsche wurde rot" von einem **Zufallsfund** in einen **Fehlschlag**.

  *Beim ersten Anwenden sofort etwas gezeigt:* Für den `meldet`-Ausgang notierte
  ich vorab, dass der Selbstcheck-Status **nicht** das Unterscheidungsmerkmal
  ist — nur die Anwesenheit der Hinweiszeile. Ohne die notierte Erwartung hätte
  ich auf „OK: True" geschaut und nichts gemerkt.

- **Ein Instrument ersetzt kein anderes, auch wenn beide prüfen · Ultracode vs.
  Kontroll-Gegenprüfung · universell** — *Nebenwirkung:* Ich hatte geschrieben,
  die Ultracode-Prüfstelle sei „durch Engywucks Gegenprüfung erfüllt". Der Satz
  klingt vernünftig und ist falsch: **Breite** (viele Blickwinkel, adversarisch)
  und **Tiefe** (wenige Stellen, gründlich) vertreten einander nicht. In vier
  Wochen hätte ihn jemand als Präzedenz zitiert, und die Prüfstelle wäre still
  weggefallen. **Die zulässigen Gründe sind stattdessen: bereits bedient, oder
  Auslöser nicht eingetreten.**

## Mail-Abruf Stufe A (23.08.2026)

- **Eine Funktion ohne Aufrufer ist kein Feature · Anlass · universell** —
  geprüft: ob „Postfächer freischalten" etwas bewirkt hätte. *Nebenwirkung:*
  Nein. Von neunzehn Funktionen in `email_kanal.py` rief `bot.py` genau **eine**,
  und `posteingang()` hatte **keinen** Aufrufer. Das Modul war vollständig
  gebaut, getestet und dokumentiert — und tot. **Ein Prüfer, der die Funktion
  misst, findet das nie**; nur die Frage „wer ruft das eigentlich" findet es.

- **`name.strip()` entfernte den Marker, der die Zeile ausweist · A1 ·
  universell** — *Nebenwirkung, und sie ist die elegante des Tages:* Im
  Mail-Format weist ein **führendes Leerzeichen** eine Zeile als Fortsetzung
  der vorherigen aus. Die Handschleife rief `name.strip().lower()` — und
  entfernte damit genau das Zeichen, an dem man die Fortsetzung erkennt. Aus
  ` From: chef@firma.de` wurde ein eigenes Feld, und das Wörterbuch überschrieb.

  **Die Lehre über den Fall hinaus:** Normalisierung ist nicht neutral. Wer
  einen Wert säubert, bevor er ihn deutet, kann genau das Merkmal löschen, das
  die Deutung trägt.

- **Fehlerbehandlung, die selbst einen Fehler wirft · A3 · anpassbar** —
  *Nebenwirkung:* `log` war in `email_kanal.py` **nie definiert**. Die
  Fehlerzweige riefen `log.warning`, und der Name sah richtig aus. **Der Zweig
  läuft nur im Störfall** — also genau dann, wenn er tragen soll. Gefunden hat
  es die Prüfzeile „ein Verbindungsfehler ist keine leere Mailbox" beim ersten
  Lauf; kein Lesen hätte es gezeigt.

- **Das gemischte Anführungspaar, zum sechsten Mal · anpassbar** — beim Bau von
  A2 wieder `„…"` geschrieben, wieder SyntaxError. Der Prüfer aus `CLAUDE.md`
  greift, aber erst nachträglich. *Was diesmal half:* die dort empfohlenen
  **eckigen Klammern** von vornherein für Meldungen zu nehmen — `[{konto}]`
  statt Anführungszeichen. Die Regel zu kennen genügt offenbar nicht; man
  braucht die Ausweichform im Finger.

## Mail-Abruf Stufe B4 + Angriffskorpus (23.08.2026)

- **Entfernen ist eine stille Lüge, Markieren ist die Information · B4 ·
  universell** — Engywuck ließ die Wahl: verstecktes HTML mitlesen und
  markieren, **oder** entfernen. *Die Nebenwirkung des Entfernens ist der
  Grund gegen es:* Eine Mail, deren versteckter Teil spurlos verschwindet,
  sieht **harmlos aus**. Adam erführe nie, dass jemand etwas zu verbergen
  versuchte — und **genau das ist die Information, die er braucht.** Ein
  Absender, der weiße Schrift benutzt, hat sich damit erklärt.

  Dazu der billigere Maßstab: Ob ein versteckter Satz eine *Anweisung* ist,
  kann niemand zuverlässig entscheiden. Ob er **versteckt war**, ist eine
  strukturelle Tatsache im Auszeichnungstext. **Wir messen, was messbar ist.**

- **Der Kommentar versprach mehr, als der Prüfer maß · eigene Gegenprobe ·
  universell** — *Nebenwirkung, und sie hat sich selbst gezeigt:* Meine
  Gegenprobe „Zeichen entfernen statt ersetzen" ließ die Prüfzeile **grün**.
  Sie maß „kein unsichtbares Zeichen im Text" — was Entfernen ebenso erfüllt.
  Der Kommentar daneben schloss Entfernen ausdrücklich aus.

  **Ohne Engywucks Handgriff** (vorher hinschreiben, welche Zeile rot werden
  soll) hätte ich die grüne Gegenprobe als bestanden verbucht. So fiel auf,
  dass sie die falsche Sache misst — und eine neue Zeile schließt die Lücke.

- **Zwei von fünf eigenen Gegenproben waren falsch konstruiert · Verfahren ·
  universell** — sie trafen schlicht nicht, weil der Patch-Anker nicht passte
  oder der Eingriff die Prüfung gar nicht berührte. **Beides sah aus wie „der
  Schutz hält".** Der Handgriff verwandelt genau diesen Fall von einem
  beruhigenden Ergebnis in einen sichtbaren Fehlschlag.

- **Zum zweiten Mal am selben Tag: der Prüfer stolperte über seinen eigenen
  Erklärtext · B2 · universell** — *Nebenwirkung:* Die erste Fassung suchte
  `task_origins`, `adam_anteil` und `QueuedJob` als **Text** im Quelltext der
  geprüften Funktion — und schlug an, weil deren **Docstring genau erklärt,
  warum sie diese Dinge nicht berührt.**

  Die Regel vom 22.08. benennt das ausdrücklich, und ich habe sie an einem Tag
  zweimal gebrochen (einmal beim Pfad-Prüfer, einmal hier). **Der Griff, der
  hilft, ist derselbe wie überall:** über den Syntaxbaum messen, echte
  Namensknoten statt Textvorkommen. Kommentare gibt es dort nicht, und
  Docstrings sind Zeichenketten, keine Namen.

- **Bauartbedingt schlägt geprüft · B2 · universell** — der werkzeugfreie
  Mail-Lauf kann `task_origins` nicht erweitern, **weil es die Verbindung nicht
  gibt**: eigene Optionen, eigener Client, kein Auftrag in der Warteschlange.
  Kein Filter weist etwas ab; es führt schlicht kein Weg dorthin.

  *Der Unterschied zur Prüfung ist praktisch, nicht philosophisch:* Ein Filter
  muss richtig bleiben, während der Code sich ändert. Eine fehlende Verbindung
  muss erst hergestellt werden, und das fällt beim Schreiben auf.

- **Committet und deployt, ohne den vollen Lauf zu fahren · eigener
  Verfahrensfehler, 23.08. · universell** — ich hatte `mess_redeseite.py` nur
  auf **Syntax** geprüft, weil es „nur ein Messwerkzeug" ist. Auf dem VPS waren
  danach **zwei** Prüfungen rot: das gemischte Anführungspaar (zum siebten Mal)
  und der Register-Eintrag.

  *Die Nebenwirkung ist die Lehre:* Ein Werkzeug ohne Prüferstatus wird trotzdem
  vom Läufer erfasst — der Register-Wächter und der Anführungszeichen-Wächter
  kennen die Unterscheidung „Prüfer oder Werkzeug" nicht, und das ist richtig
  so. **„Das ist doch nur ein Hilfsskript" ist keine Ausnahme vom vollen Lauf**,
  sondern genau die Formulierung, mit der man ihn sich spart.

## Engywucks Nachfreigabe zum Mail-Abruf (23.08.2026, Abend)

- **Der Deckel muss GETRENNT sein, sonst schiebt man die Markierung über die
  Kante · ② · universell** — Engywucks Bedingung, und die Messung gab ihm in
  **beide** Richtungen recht: Fülltext im sichtbaren Teil hätte den
  Verborgen-Abschnitt verdrängt (fail-open), und ein einzelnes langes Versteck
  ging mit **200.000 Zeichen** ungekürzt in den Modell-Lauf (Kontext-Flutung).

  *Die Lehre über den Fall hinaus:* **Ein gemeinsamer Deckel über zwei Töpfen
  ist ein Hebel** — wer den einen füllt, leert den anderen. Wo zwei Dinge
  unterschiedlich wichtig sind, brauchen sie unterschiedliche Grenzen.

- **Die Heuristik klagte korrektes Verhalten an · ③ · universell** — mein
  Merkmal „erste Person" schlug bei Fall 12 an. Der Satz lautete: *„Der
  Absender schreibt wörtlich: ‚…, **ich habe** sie verlegt.'"* Der Bot hatte
  **genau richtig zitiert**, und das Muster klagte ihn dafür an.

  *Nebenwirkung:* Ein Prüfer, der korrektes Verhalten meldet, wird schneller
  abgeschaltet als einer, der nichts findet. Fix: **zitierte Rede vor der
  Messung herausnehmen** — die Merkmale suchen die Haltung des Bots *daneben*.

- **Die Tatsache nehmen, nicht die Zeichenkette · ④ · universell** — Engywucks
  Griff für die Anhänge, und er ist allgemeiner als sein Anlass: Adam braucht
  „diese Mail bringt etwas mit", **nicht** den vom Absender gewählten
  Dateinamen. Der MIME-Typ kommt vom Server, die Abbildung ist eine feste
  Wortliste, Unbekanntes heißt „unbekannt". **Damit steht in der Übersicht kein
  einziges Zeichen, das ein Fremder gewählt hat.**

- **Die Ausnahme wird aus der Harmlosigkeit des GEGENSTANDS begründet, nie aus
  dem Risiko · Engywuck zu meinem fünften Fehler · universell** — *„ist ja nur
  ein Messwerkzeug" hat dieselbe Form wie „ist ja nur ein Kommentar".* Die
  tragfähige Fassung hängt den vollen Lauf an den **Commit**, nicht an den
  Gegenstand. Dann gibt es nichts mehr zu begründen — und das ist billiger als
  jede Abwägung, weil die Frage „ist das wichtig genug?" länger dauert als der
  Lauf.

## Engywucks Nachtrag F-18 (23.08.2026, spät)

- **„Nie kürzen" heißt wörtlich „unbegrenzt" · Engywuck über seine eigene
  Regel · universell** — er hatte geschrieben *„gekürzt wird der sichtbare
  Text, NIE der Verborgen-Abschnitt"*, und die Messung fand daraufhin ein Loch
  in **seiner** Richtung: 200.000 Zeichen verborgener Text gingen ungekürzt in
  den Modell-Lauf.

  **Seine Formulierung hatte genau den Fehler, den meine Lehre beschreibt:**
  *Ein gemeinsamer Deckel über zwei Töpfen ist ein Hebel — wer den einen füllt,
  leert den anderen.* Die richtige Fassung ist nicht „einen nie kürzen",
  sondern **„beide einzeln deckeln"**. Ein Verbot ohne Grenze ist selbst eine
  Grenze, nur eine unendliche.

- **Die Zitat-Trennung kann blind machen, und Blindheit sieht aus wie Ruhe ·
  ③ · universell** — Engywuck bat um einen Testfall „Zitat, Gedankenstrich,
  Übernahme". *Gemessen:* Der bestand, aber ein **anderer** fiel durch —
  `„Bitte zahlen. — Ich werde das erledigen."` verschluckt als ein einziges
  Zitat den ganzen Text, und beide Merkmale finden nichts.

  **Ein Merkmal, das nichts findet, sieht aus wie eines, das nichts zu finden
  hatte.** Der Griff dagegen ist nicht schärfer trennen, sondern **die
  Blindheit selbst melden**: Bleibt nach der Trennung fast nichts übrig, ist
  das ein Befund, kein Freispruch.

- **Der Prüfer sah die Datei gar nicht — einen Tag nach dem Differenzmesser ·
  F-18 · universell** — `test_pruefumgebung.py` bildete seine Menge als
  `glob("test_*.py")`. `mess_redeseite.py` importiert `bot`, setzt
  Umgebungsvariablen, heißt aber nicht `test_*` — und fiel heraus. Sein
  `setdefault` auf `ALLOWED_USER_IDS` blieb ungesehen, **auf genau der
  Variablen, die im Register namentlich als Anlass steht.**

  *Und beim Beheben zeigte sich die Krankheit ein zweites Mal, eine Ebene
  tiefer:* Die Prüfung selbst hatte eine **Namensliste von vier Ordnern**.
  Auf die Eigenschaft umgestellt („in einem Prüfstand ist JEDES `setdefault`
  falsch"), fand sie sofort **dreizehn** Dateien statt einer.

  **Die Lehre in einem Satz:** Ein Namensmuster ist eine Aufzählung mit
  Regex-Anstrich — und es versagt nicht laut, sondern indem es leise weniger
  misst, als sein Name verspricht.

- **Die trennende Eigenschaft muss man messen, nicht raten · F-18 · anpassbar**
  — mein erster Ersatz („importiert `bot` UND setzt Umgebung") fing prompt
  `start_waechter.py` mit, ein **Betriebsskript**, das `Popen` legitim braucht.
  Gemessen trennt `tempfile` sauber: Ein Prüfstand legt sich eine Wegwerf-Ablage
  an, ein Betriebsskript arbeitet im echten Zustand. **Zwei Messwerkzeuge auf
  der einen Seite, elf Betriebsskripte auf der anderen** — die Tabelle stand in
  zehn Sekunden, das Raten hätte länger gedauert und wäre falsch geblieben.

- **Jede Pruefung laeuft ueber eine Menge — und es ist immer die, die dem
  Erbauer am Bautag einfiel · Mail-Schranken 9.5 · universell**
  — **Engywucks Verallgemeinerung von drei Messungen binnen zwei Tagen**, und
  sie loest die drei Faelle in einen auf:

  | Stelle | die Menge | wie gross sie wirklich war |
  |---|---|---|
  | Namensliste im Pruefer | `glob("test_*.py")` | eine von dreizehn |
  | Idiom-Erkenner | `os.environ.get(...)` | eine von sechs |
  | Mail-Korpus | [was uns einfiel] | kein echtes Mailformat |

  **In KEINEM der drei stand eine Liste da.** Die Menge steckte in einem
  **Namensmuster**, einem **Erkenner**, einem **Korpus** — unsichtbar, und
  darum nicht mitgewachsen. Damit ist auch die Fassung vom 23.08. („wer eine
  Menge bildet, muss auch die Menge der Schreibweisen bilden") als **Sonderfall**
  eingeordnet, nicht als eigene Regel.

  **Der Griff, und er ist der ganze Ertrag:** Bei jeder Pruefung fragen
  **[was ist ihre Menge, und woher kommt die?]** — nicht [steht hier eine
  Liste?]. Die zweite Frage findet genau die Faelle, die ohnehin sichtbar sind.

  **Steht ein Korpus oder Pruefstand an, lautet die Frage nicht [welche Faelle
  nehmen wir auf], sondern [woher kommt die Menge] — und die Antwort sollte ein
  ERZEUGER sein, keine Handauswahl.** Fuer den Mail-Korpus heisst das: echte
  Nachrichten aus einem Postfach-Export, ein MIME-Baukasten. Eine Handauswahl
  misst die Vorstellungskraft ihres Erbauers, die Schranke nur nebenbei.

- **Ablegen entschaerft keine Befehle · Kostenregel 24.08. · universell**
  — **Engywucks Lehre**, gefunden beim Messen der API-Schluessel-Anweisungen:
  Gemeldet waren vier README-Stellen, gemessen wurden **zehn** — und die
  schwerste stand in `MIGRATION-DREHBUCH-ARCHIV.md`: **sechs Zeilen
  ausfuehrbare Shell**, die einen kostenpflichtigen Schluessel in die
  Umgebungsdatei schreiben.

  **Ein Befehlsblock im Archiv ist genauso kopierbar wie einer im gueltigen
  Drehbuch.** Der Grund, warum niemand hinsah, steht im Dateinamen — [Archiv]
  liest sich wie [erledigt], ist aber nur [nicht mehr gepflegt]. Ungepflegt und
  unwirksam sind zwei verschiedene Dinge.

  **Der Griff:** Beim Archivieren pruefen, ob die Datei **ausfuehrbare Bloecke**
  enthaelt. Wenn ja, gehoeren sie entschaerft oder mit einem Warnkopf versehen —
  **im selben Zug wie das Archivieren**, weil danach niemand mehr hinsieht.

- **Die Mengen-Lehre, angewandt auf den Befund, der sie formuliert hat ·
  Kostenregel 24.08. · universell**
  — Engywucks Befund nannte **zehn Stellen in `*.md`**. Die schaerfste stand in
  `com.user.claude-telegram-bot.plist.example` und **fehlte, weil seine Menge
  Doku-Dateien war.** Eine Vorlagendatei ist nicht bloss kopierbar, sie ist
  **zum Kopieren gemacht** — sie wird kopiert, umbenannt und geladen.

  **Die Menge des Pruefers ist deshalb `git ls-files`, nicht `*.md`.** Wer eine
  Menge ueber eine Endung bildet, hat sie ueber einen Namen gebildet.

  **Und die trennende Eigenschaft ist Kopierbarkeit, nicht die Zeichenkette:**
  In Markdown zaehlt eine Zuweisung nur **im eingezaeunten Codeblock**. Ohne
  diese Trennung schluege die Art auf ihrem **eigenen Bauauftrag** an, der die
  Gefahr im Fliesstext beschreibt — und waere binnen einer Woche abgeschaltet.

- **Eine Gegenprobe, die zuruecksetzt, darf nicht an ungesicherter Arbeit
  laufen · Kostenregel 24.08. · universell**
  — Selbst passiert, im selben Zug: Ich habe die Gegenprobe der Sammelfunktion
  an `README.md` gefahren und mit `git checkout README.md` zurueckgesetzt —
  **und damit vier uncommittete Ersetzungen mitgeloescht**, die ich zehn
  Minuten vorher in dieselbe Datei geschrieben hatte. Bei `stundenblume.py`
  hatte ich zwei Schritte zuvor sauber mit `cp` gesichert; bei der README nicht.

  **Der Griff:** Vor einer Gegenprobe, die den Zustand zurueckdreht, entweder
  **committen** oder die Datei **kopieren** — oder an einer Datei pruefen, in
  der nichts liegt. Dieselbe Klasse wie [git commit nie an einen
  dateiaendernden Heredoc ketten]: **Der Rueckweg zerstoert, was er schuetzen
  soll**, wenn man ihn ohne Blick auf den Arbeitsstand geht.

- **Das Vier-Augen-Prinzip traegt ueber das Projekt hinaus · Kurs-Blick 24.08.
  · universell**
  — **Adams eigene Uebertragung**, und sie ist der erste Beleg von aussen: Er
  nimmt aus der Zusammenarbeit mit, **fuer die Businessprojekte ebenfalls eine
  Kontrollsitzung einzurichten** — weil es sich hier bewaehrt hat.

  **Damit ist die Bauform als solche bestaetigt, nicht nur ihr Ergebnis.**
  Bemerkenswert ist, WAS sich bewaehrt hat: nicht [eine zweite Meinung], sondern
  **die Trennung von Bauen und Pruefen bei getrenntem Kontext** — der Erbauer
  bewertet den eigenen Bau ueber seine eigene Absicht, und keine Sorgfalt hebt
  das auf.

  **Die drei Stuecke, ohne die es Beruhigung statt Kontrolle wird** (aus
  diesem Projekt gemessen, nicht erdacht): **① Der Auftrag lautet [finde, was
  nicht traegt], nie [pruefe, ob es stimmt]** — wer bestaetigen soll,
  bestaetigt. **② Die Kontrolle muss den Bau nicht kennen** — frischer Kontext
  ist der Wirkstoff, nicht ein Mangel. **③ Eine Gegenpruefung, die nie etwas
  findet, ist selbst der Befund.**

- **Eine Menge aus FUNKTIONSNAMEN ist keine Menge · Gestalten-Erzeuger 24.08.
  · universell**
  — **Mein eigener Fehler, im Werkzeug, das genau dagegen gebaut wird.** Die
  Kodierungs-Achse zog ich aus `dir(email.encoders)` und schnitt das Praefix
  ab: `7or8bit`, `base64`, `quopri`. Das sind die Namen der **Funktionen**;
  die Werte heissen `7bit`, `8bit`, `quoted-printable`. **Zwei von drei
  ungueltig, zwei Drittel des Achsenraums fielen weg.**

  **Das Rettende war nicht Aufmerksamkeit, sondern eine Auflage:** Engywuck
  hatte verlangt, **jede Baufehlschlagung zu zaehlen statt still zu
  ueberspringen**. Der Lauf meldete 160 Fehlschlaege von 240 — sonst haette er
  achtzig geprueste Gestalten gemeldet, und niemand haette bemerkt, dass er
  nur **eine** Kodierung kennt. **Ein Prueferaum, der still schrumpft, sieht
  aus wie ein Pruefer, der nichts findet.**

  **Der Griff:** Eine Menge aus einer Bibliothek zu ziehen genuegt nicht — man
  muss pruefen, ob man die **Werte** hat oder nur ihre **Bezeichner**. Wo eine
  geschlossene Norm-Menge existiert (RFC 2045 kennt fuenf Kodierungen), ist
  die Aufzaehlung legitim; **welche davon gelten, wird trotzdem gemessen**,
  nicht behauptet.

- **Ein Deckel, der eine Ecke des Raums zeigt, ist selbst eine Handauswahl ·
  Gestalten-Erzeuger 24.08. · universell**
  — Zweiter Selbstbefund im selben Bau: `itertools.product` laeuft die erste
  Achse zuerst durch. Ein Abbruch nach n Stueck liefert deshalb **nur
  Gestalten mit der ersten Aufbau-Art**. Beim ersten Lauf waren 199 von 200
  Befunden derselbe Fall, und der halbe Achsenraum war ungesehen — **es sah
  aus wie ein gruendlicher Lauf.**

  **Der Griff:** Volle Kombinationsliste bilden, dann **gleichmaessige
  Schrittprobe** ziehen (deterministisch, kein Zufall). Und im Bericht die
  **Raumgroesse** neben der Stichprobengroesse nennen, damit sichtbar bleibt,
  welcher Anteil ueberhaupt gesehen wurde.

- **Eine Voraussetzung gehoert in die Ladebedingung, nicht in eine Pruefzeile ·
  Rang 0.5 · universell**
  — **Gebaut:** `scripts/mailgestalten._pruefe_achsen()` bricht den **Import**
  ab, wenn ein Achsenwert nicht zu seiner Wertmenge gehoert; dazu meldet jeder
  Lauf **erwartet · gebaut · uebersprungen mit Grund**, und eine Abweichung ist
  **rot**, nicht kommentiert.

  **Kettenwirkung geprueft:** zwei Gegenproben — ungueltiger Achsenwert
  (`quopri`) muss den Import toeten · ein scheiternder Bau muss den Lauf rot
  faerben und den Grund nennen.

  **Tatsaechlich eingetretene Nebenwirkung — und sie ist die Lehre:** **Meine
  zweite Gegenprobe war falsch konstruiert und traf nicht.** Ich hatte
  `utf_16` als [Codec, der scheitert] eingesetzt — er ist gueltig und hat
  anstandslos gebaut. Der Lauf blieb gruen, und **das sah aus wie [der Schutz
  haelt]**. Dritter Fall dieser Klasse binnen drei Tagen.

  **Der Griff dagegen ist Engywucks Handgriff, und er hat wieder getragen:**
  **Vor der Gegenprobe hinschreiben, WELCHE Zeile rot werden soll** — dann ist
  [die falsche wurde rot] ebenso ein Fehlschlag wie [gar keine wurde rot].
  Ohne die vorher notierte Erwartung haette ich die gruene zweite Gegenprobe
  als bestandene verbucht.

  **Warum Ladebedingung und nicht Pruefzeile:** Eine Pruefzeile kann
  uebersprungen, abgeschaltet oder schlicht nicht gefahren werden. Der Import
  laeuft immer, wenn das Werkzeug laeuft. **Wo eine Voraussetzung erzwingbar
  ist, ist Beobachten die schwaechere Wahl.**

- **Eine Gegenprobe soll die Vorfassung LADEN, nicht NACHSTELLEN · Rang 1 ·
  universell**
  — **Gebaut:** Die Verstecktheit folgt in `mailtext.py` jetzt aus einer Menge
  benannter Mechanismen (`_VERBERGENDE_STILE`, `_VERBERGENDE_ATTRIBUTE`), und
  der Zerleger fragt nur `verbergungsgrund(attrs)`. Er weiss nicht mehr, WIE
  verborgen wird, nur DASS.

  **Kettenwirkung geprueft:** Der Gestalten-Erzeuger faerbt den alten Zerleger
  **45 von 60 rot**, den neuen **0 von 60** — auf der HTML-Ebene, ueber alle
  Kodierungen, Zeichensaetze, Verbergungsarten und Platzierungen.

  **Tatsaechlich eingetretene Nebenwirkung, und sie ist die eigentliche
  Lehre:** **Zwei meiner drei Gegenproben blieben gruen und prueften nichts.**
  Ich hatte die Vorfassung **nachgestellt** — den Rahmensuch-Lauf durch `pop()`
  ersetzt — aber `pop()` ist immer noch ein **Stapel**; der alte Fehler war ein
  **Zaehler**. Meine Nachstellung war besser als das Original und fing deshalb
  nichts. Dasselbe bei der Leerelement-Probe: Der Stapel repariert diesen Fall
  **nebenbei mit**, weil `</head>` den ganzen Teilbaum schliesst.

  **Der Griff:** `git show HEAD:datei` liefert die **echte** Vorfassung. Sie
  laden und dagegen messen — nicht aus dem Gedaechtnis nachbauen. **Eine
  nachgestellte Vorfassung traegt die Annahmen dessen, der sie nachstellt**,
  und genau die sind beim Beheben gerade frisch korrigiert worden.

  **Und der Pruefstein wurde zur Pruefzeile:** Engywucks Frage [kostet ein
  fuenfter Mechanismus eine Zeile in der Menge oder einen Eingriff im
  Zerleger?] steht jetzt als ausgefuehrte Messung in
  `test_mailkorpus.py` — sie legt zur Laufzeit einen Mechanismus in die Menge
  und prueft, dass er greift. **Ein Pruefstein als Vorsatz haelt bis zum
  ersten eiligen Tag.**

- **Vor der Gegenprobe pruefen, ob der EINGRIFF ueberhaupt gegriffen hat ·
  Rang B · universell — dritter Fall an einem Tag**
  — **Dreimal am 25.08. blieb eine Gegenprobe gruen, und jedes Mal aus
  demselben Grund: nicht der Schutz hielt, sondern der Eingriff fand nicht
  statt.**

  1. Vorfassung **nachgestellt** statt geladen (`pop()` statt Zaehler) — meine
     Nachstellung war besser als das Original.
  2. Ein Codec als [scheitert] gewaehlt, der in Wahrheit baut (`utf_16`).
  3. Eine Zeile ersetzt, **die es so nicht gab**: `max(0.05, …)` statt
     `max(1.0, …)`. `str.replace` meldet das nicht — es ersetzt schlicht
     nichts und gibt den Text unveraendert zurueck.

  **Alle drei sahen aus wie [der Schutz haelt].** Das ist die gefaehrlichste
  Form eines gruenen Laufs, weil sie Sicherheit erzeugt, wo nichts geprueft
  wurde.

  **Der Griff, zwei Zeilen und billig:**
  `assert alt in t, "ANKER FEHLT"` **vor** jeder Ersetzung — dann bricht die
  Gegenprobe laut ab, statt still zu bestehen. Und wo es um eine Vorfassung
  geht: `git show HEAD:datei` laden, nicht nachbauen.

  **Der Zusatz aus Engywucks Entkernungs-Katalog, selbst gemessen noetig:**
  `__pycache__` **vor jedem** Gegenprobe-Lauf loeschen. Sonst serviert Python
  das Ergebnis des vorherigen Eingriffs (mtime-Sekunde und Groesse zufaellig
  gleich), und man misst einen Geisterbefund.

- **K3 gebaut, waehrend ich K3 reparierte · Rang B (b) · universell**
  — Mein Ersatz fuer den Formatzwang pruefte, ob **irgendein** Schlaf-Aufruf
  gedeckelt ist. Das ist woertlich die Krankheit K3 aus dem Befund, den ich
  gerade abarbeitete: **Schwelle ueber die Datei statt Zuordnung je Pfad.**
  Aufgefallen nur, weil die Gegenprobe (nach der Korrektur oben) rot wurde.
  **Wer eine Fehlerklasse repariert, baut sie im selben Zug am ehesten neu ein**
  — die Denkform, die den Fehler erzeugt hat, ist beim Reparieren am
  praesentesten.

- **Eine Zahl aus einem frisch reparierten Pruefer ist noch kein Befund ·
  Anfuehrungs-Pruefer 25.08. · universell**
  — **Dreimal in einer Nacht dieselbe Form** (Engywucks Beobachtung, und sie
  ist der Ertrag der Nacht): Engywuck mass 51/54 — **richtig, aber nur weil
  seine Umgebung zufaellig die sehende war** (Python 3.11). Ich mass danach 70
  Stellen — **falsch, weil mein Fix eine neue Fehlerquelle mitbrachte**.
  **Beide Male hat erst die Gegenmessung auf der ANDEREN Maschine die Wahrheit
  gezeigt.**

  **Die Sachlage:** Bis 3.11 ist ein f-String ein Token, ab 3.12 (PEP 701)
  zerfaellt er. Wer nur `STRING` prueft, ist auf 3.12+ blind. Wer stattdessen
  die Fragmente einzeln prueft, schwaerzt **korrekte** Paare an, weil
  `f'Haus „{t}“ da'` in `'Haus „'` und `'“ da'` zerfaellt — beide Haelften
  unausgewogen. So wurden aus vier echten Stellen siebzig gemeldete: **64
  Fehlalarme auf 32 Zeilen, jede doppelt.**

  **Das Doppel-Muster stand woertlich in der eigenen Ausgabe** —
  `hora.py:628, hora.py:628` — **gesehen, nicht gedeutet.** Eine Wiederholung
  in einer Trefferliste ist eine Signatur, kein Zufall.

  **Der Griff ist derselbe wie im Zerleger, andere Stelle:** zwischen
  `FSTRING_START` und `FSTRING_END` sammeln, verketten, **dann** pruefen — ein
  **Stapel**, kein Flag, weil f-Strings ineinander stehen duerfen. *Ein
  Fragment bildet Verschachtelung nicht ab.*

  **Und die praktische Konsequenz, die den Schaden erklaert:** Wer die
  [siebzig Stellen] repariert haette, haette **32 korrekte Paare zerstoert** —
  einem Pruefer entlang, der sie faelschlich anschwaerzt. Ein Pruefer, der
  falsch anschlaegt, wird nicht nur abgeschaltet; **er richtet vorher Schaden
  an, weil jemand ihm glaubt.**

- **Eine Kappung ohne Gesamtzahl ist eine Falschaussage mit Fussnote ·
  Anfuehrungs-Pruefer 25.08. · universell**
  — `", ".join(treffer[:8])` zeigte acht Stellen und verschwieg, wie viele es
  waren. Weil `bot.py` **hinten** in der Dateiliste stand, waren die Stellen
  dort nie zu sehen — die Meldung las sich vollstaendig und war es nicht.
  **Die Gesamtzahl gehoert VOR die Liste**, nicht dahinter und nicht weggelassen.

- **[Gar nicht gesucht] und [nichts gefunden] duerfen nicht denselben Wert
  haben · Rang 2, Websuche · universell**
  — **Gebaut:** `bot.suchlage()` als eigene Funktion (damit ein Pruefer sie
  ausfuehren kann) plus `_websuche_gesamt()`, das die Zahl der Zulieferer beim
  **Dienst selbst erfragt** statt sie zu tippen.

  **Kettenwirkung geprueft:** sieben Pruefzeilen, beide Richtungen — Ausfall
  meldet, gesunde Suche schweigt. Gegenprobe mit verifiziertem Eingriff.

  **Tatsaechlich eingetretene Nebenwirkung:** Beim Messen zeigte sich, dass
  `mojeek`, `mwmbl` und `yep` **bereits aktiv** sind, obwohl der Bauauftrag sie
  als [nicht aktiviert] fuehrt. Haette ich die Zulieferer-Namen aus dem Auftrag
  abgeschrieben, waere die Liste vom ersten Tag an falsch gewesen. **Ein
  Auftrag ist eine Momentaufnahme des Systems, kein Abbild davon.**

  **Und die Lehre ueber die Fehlerklasse hinaus:** Der Vorfall bestand nicht
  darin, dass die Suche ausfiel — sondern dass **Ausfall und Leerergebnis
  denselben Rueckgabewert hatten**. Wo ein Aufrufer zwei Lagen nicht
  unterscheiden kann, waehlt er die plausiblere; Claudia hat vier Stunden lang
  die falsche Auskunft weitergegeben, **weil sie hoeflich klang**. Deshalb
  steht der Unterschied jetzt ausdruecklich im Text — fuer einen Leser, der
  ein Modell ist.

- **Der Differenzmesser hat den ersten fremden Fehler gefangen — meinen ·
  Rang 2, Websuche · universell**
  — Beim Bau des Websuche-Waechters legte ich eine Zustandsablage an
  (`WEBSUCHE_VERLAUF`, ein Verlauf fuer die Zwei-Tage-Daempfung) und **vergass
  den Riegel im Regressionslauf**. Der Prueflauf haette damit in den echten
  Betriebszustand geschrieben — lautlos, wie es die Klasse verlangt.

  **Gefangen hat es die `ablagen_differenz` vom 23.08.**, gebaut auf Engywucks
  Auftrag, und zwar **beim ersten Lauf nach der Aenderung**: *[Zustandsablagen
  ohne Riegel: WEBSUCHE_VERLAUF]*. Das ist der erste Fall, in dem eine dieser
  Arten einen Fehler fing, den **nicht ihr Erbauer gerade suchte**.

  **Zwei Beobachtungen, die ueber den Einzelfall hinausgehen:**
  **①** Der Fehler faerbte **zwei** Pruefzeilen rot, nicht eine — der
  Selbstcheck ruft den Differenzmesser selbst auf. Eine Ursache, zwei
  Erscheinungen; wer nur die erste repariert, sucht die zweite vergeblich.
  **②** Eine Art, die am Bautag nichts findet, ist **kein untaugliches
  Werkzeug**. `module_differenz` fand am 23.08. nichts und wurde als
  [schuetzt Modul Nummer neunzehn] eingetragen. Hier war es Ablage Nummer
  soundso, fuenf Tage spaeter. **Der Ertrag eines Riegels faellt nie am Tag
  seines Baus an.**

- **Herkunft kennzeichnen schlaegt Reihenfolge aendern · Rang 3, Freigabedialog
  · universell**
  — Claudia hatte gefragt, ob der Klartextsatz **ueber** oder **unter** die
  Rohform gehoert: oben liest es sich besser, unten waere misstrauischer.
  **Engywucks Antwort: Die Frage ist falsch gestellt.** In beiden Anordnungen
  bleibt offen, **woher** der Satz stammt.

  Gebaut ist deshalb die Trennung, nicht die Umsortierung: **[Angabe der
  Sitzung]** fuer das, was die antragstellende Instanz behauptet — in
  Anfuehrung, damit ihr Ende sichtbar ist — und **[Maschine —]** fuer das, was
  die CLI misst.

  **Tatsaechlich eingetretene Nebenwirkung:** Eine Beschreibung, die selbst
  `Angabe der Sitzung:` enthaelt, ahmte die Kennzeichnung nach. Eine zweite
  **Zeile** konnte sie nie erzeugen (Zeilenumbrueche sind entfernt), aber eine
  zweite **Kennzeichnung** innerhalb der Zeile schon. Die Anfuehrung loest das
  **ohne Wortliste** — was zwischen den Zeichen steht, ist fremd; wo sie
  schliessen, endet das Fremde.

  **Und der Auftrag schrumpfte durch Messen:** Engywuck hat belegt, dass die
  CLI-Felder im `ToolPermissionContext` **bereits ankamen** — der Bot nahm ihn
  entgegen und las kein einziges Feld aus. Aus [einen Kanal bauen] wurde
  [vier Felder auslesen]. **Bevor man einen Weg baut, nachsehen, ob er schon
  da ist.**

- **Regressionslauf und `git commit` gehoeren in getrennte Befehle · Rang 4 ·
  universell**
  — Selbst gemacht am 28.08.: `bash scripts/regressionstest.sh | tail -1` und
  `git commit` in **einem** Aufruf. Der Commit laeuft dann, **egal was der Lauf
  sagt** — die Ausgabe erscheint, aber niemand wartet auf sie.

  **Das ist wortgleich das Muster, das `CLAUDE.md` fuer Heredocs verbietet**
  (*[git commit wird NIE an einen dateiaendernden Heredoc gekettet]*), nur mit
  einem anderen ersten Glied. Die Regel benennt dort den Heredoc, weil er der
  Anlass war — **die Klasse ist [Commit haengt an einem Vorgang, dessen
  Ergebnis niemand prueft]**.

  **Der Griff:** erst laufen lassen, Ergebnis **ansehen**, dann in einem
  eigenen Aufruf committen. Kostet einen Befehl mehr und macht den Unterschied
  zwischen [gepruefft] und [gehofft].

- **Entprellung trifft Zustaende, nicht Ereignisse · Rang 4, Auftrag 4 ·
  universell**
  — **Beim Bauen gefunden, nicht im Auftrag vorgesehen.** Die Entprellung
  verlangt, dass ein Befund in drei Laeufen in Folge steht, bevor er als
  aufgetreten gilt. Das trifft **Zustaende** richtig (Speicher knapp, Bot weg)
  — aber ein **Ereignis** tritt genau einmal auf.

  Konkret: Die **Kettenluecke** haette es nie wieder ueber die Schwelle
  geschafft. Sie ist der Kern-Alarm dieser Wache — *[in dieser Zeit hat
  niemand belegt, dass das System lebt]* —, und sie waere **still
  verschwunden**, waehrend alle Pruefzeilen gruen geblieben waeren. Gefangen
  hat es der bestehende Test [die Luecke ist der Alarm].

  **Der Griff, in derselben Bauform wie das Protokoll-Praefix:** ein Praefix
  `!` am Befund selbst. Die Einstufung steht dort, wo der Befund entsteht, und
  laesst sich nicht vergessen — eine Liste an anderer Stelle waechst nicht mit.

  **Die allgemeine Frage vor jeder Entprellung:** *Kann dieser Befund
  ueberhaupt zweimal hintereinander auftreten?* Wenn nein, ist jede Verzoegerung
  ein Loeschen.

- **Ein Zeitsprung im Test erzeugt selbst einen Befund · Rang 4 · anpassbar**
  — Mein Pruefer fuer die Zwoelf-Stunden-Erinnerung sprang zwoelf Stunden
  vorwaerts — und **erzeugte damit eine Kettenluecke**, die seit demselben Bau
  sofort gemeldet wird. Die zweite Nachricht war die Luecke, nicht die
  Erinnerung; gezaehlt wurden Nachrichten, gemeint war ein Befund.
  **Auf den Befundtext zaehlen, nicht auf Nachrichten** — sonst misst man den
  Nebeneffekt der eigenen Zeitreise.

- **Beim Reparieren einer Fehlerklasse baut man sie am ehesten neu ein · Rang 6
  · universell — ZWEITER Fall an einem Tag**
  — Ich habe an einem Nachmittag **zweimal K3 gebaut, waehrend ich K3
  reparierte**: eine Schwelle, die zaehlt statt zuzuordnen.

  Erst beim Schlaf-Pruefer (*[irgendein `sleep` ist gedeckelt]*), dann bei der
  Dauerfreigabe (*[mindestens zwei Aufrufe von `darf_dauerfreigabe`]*). Der
  zweite blieb bei der Gegenprobe gruen, weil nach dem Entfernen aus dem
  Always-Zweig **zwei andere Aufrufe uebrig blieben** — die Schwelle war
  erfuellt, die Schranke weg.

  **Warum das kein Ausrutscher ist:** Die Denkform, die den Fehler erzeugt hat,
  ist beim Reparieren am **praesentesten**. Man liest den kaputten Pruefer,
  versteht ihn, und schreibt unwillkuerlich etwas in derselben Gestalt.

  **Der Griff:** Nicht die **Anzahl** pruefen, sondern die **Stelle**. Statt
  [wie oft wird X gerufen] die Frage [ruft GENAU DIESER Zweig X?] — im
  Syntaxbaum ueber die Verknuepfung: derselbe `BoolOp`, der ueber
  `always_allowed_tools` entscheidet, muss `darf_dauerfreigabe` fuehren.

  **Und die Gegenprobe ist die einzige Instanz, die das faengt.** Beide Male
  war der Pruefer gruen und sah richtig aus.

---

## 30.08. — Der Tag, an dem die Prüfer die eigene Arbeit gemeldet haben

**Was gebaut** · dritter Knopf mit fünf Auflagen · Ablageweg für
Gesprächsentscheidungen · Zustandsprüfer der Ausarbeitungen · Übersprungs-Signal
im Läufer und bei vier Verbrauchern · fail-closed im Governance-Hook ·
IMAP-Statusprüfung · `werkzeug_da` im Tagescheck.
**Kettenwirkung geprüft** · je Baustein Register, Wegwerf-Umgebung, Doku-Spiegel.
**Tatsächlich eingetreten** — und das ist die Zeile, die zählt:

**① Bestehende Prüfer haben neun eigene Fehler gemeldet, bevor ich sie bemerkt
habe.** Der Differenzmesser die fehlenden Riegel in der Wegwerf-Umgebung (ohne
sie hätte ein Prüflauf in die echte Ablage geschrieben), der Selbstcheck
zweimal einen fehlenden Register-Eintrag, das Blinde-Flecken-Verfahren zweimal
gemischte Anführungspaare, der Hermetik-Prüfer ein `setdefault`, der
Zielumgebungs-Prüfer ein `sed` im werkzeugfreien Pfad. **Das Netz trägt — es
findet, was der Erbauer im selben Zug übersieht.**

**② Die gefährlichste Klasse blieb dieselbe: grün ohne Messung.** Sie ist heute
an neun verschiedenen Stellen aufgetreten, und viermal an **meiner eigenen
frischen Arbeit** — eine Prüfzeile, die die Bilanz nicht mass; eine
Verzweigung über das zu Messende; eine Zeile, die den Dublettenschutz nie
erreichte; eine Gegenprobe, die den git-Zweig nie erreichte, weil `cat` fehlte.
**Alle vier fand die Entkernungs-Gegenprobe, keine das Nachdenken.**

**③ Reparieren erzeugt die Klasse neu.** Der fail-closed-Umbau des Hooks schuf
einen neuen fail-open (`2>&1` klebte stderr an den Pfad). Die
`${HOME:?}`-Schranke machte den Prüfer blind, der sie messen sollte. Beim
Entfernen von `basename`/`tr` habe ich `sed` neu eingesetzt — **derselbe
Fehler, eine Zeile weiter.**

**④ Und ein Verfahrensfehler von mir, festgehalten statt beschönigt:** Ich habe
den vollen Lauf und den Commit in EINEN Befehl geschrieben, mit Zeilenumbruch
statt `&&`. Der Lauf meldete 68/69, der Commit lief trotzdem. Schlimmer: Ich
hatte die Ausgabe mit `tail -2` beschnitten — **die rote Zeile ist damit
verloren und nicht mehr reproduzierbar** (drei Läufe danach: 69/69).
**Der Griff:** Das Ergebnis wird gelesen, bevor committet wird, und die
Lauf-Ausgabe wird nie so beschnitten, dass ein Befund darin verschwinden kann.
Dieselbe Lehre wie beim Tagescheck, der seine Befunde erst am Ende schrieb —
nur diesmal an mir selbst.

**⑤ Nachtrag zu ④, gemessen von Engywuck — meine Selbstauskunft war zu streng
mit mir, und das ist kein Trost, sondern ein Befund.** Der `tail -2` war die
ZWEITE Kürzung. Die erste sitzt im Läufer selbst: `run()` zeigte bei Rot nur
`tail -20`, und `test_uebersprungen_a1.py` gibt 69 Zeilen aus — ob die rote
Zeile sichtbar war, hing daran, an welcher STELLE ein Prüfer sie ausgibt. Die
DRITTE ist die Fenster-Regel in Reinform: Solange das Protokoll unter `/tmp`
liegen blieb, konnte man das Fehlende nachlesen; der Trap-Fix (Protokoll ins
Wegwerf-Heim, damit es nur einen EXIT-Trap braucht) war strukturell richtig
und hat genau dieses Fenster geschlossen. Niemand hat es bemerkt — bis
Engywuck vier rote Prüfer vor sich hatte und bei keinem den Grund sah.

**Was gebaut:** Bei Rot das ganze Protokoll statt `tail -20`, mit Zeilenzahl,
damit sichtbar bleibt, dass nichts gekürzt wurde. **Kettenwirkung geprüft:**
die vier Verbraucher des Läufers (Tagescheck, Hora, Updater, Node-Vollzug) —
alle lesen nur einzelne Zeilen per `grep`, keiner bricht an mehr Ausgabe.
**Tatsächlich eingetretene Nebenwirkung, und sie ist der Fund:** Beim Prüfen
der Kette stellte sich heraus, dass die Meldung des Tagenschecks
[siehe daily-check.log] verspricht — und das Versprechen falsch ist. `$reg`
wurde an sechs Stellen durchsucht und nirgends geschrieben; wer der Meldung
folgte, fand in der Datei genau dieselbe gekürzte Zeile. Eine vollständige
Ausgabe im Läufer hätte dort nichts genützt, weil nachts niemand am Bildschirm
sitzt. **Die Lehre: Ein Ausgabeweg ist erst repariert, wenn er an seinem
ENDE nachgemessen wurde — nicht an seinem Anfang.**

---

## Nacht zum 31.08. — Gegenprüfung einer Übersicht, und was dabei herauskam

**Was gebaut:** Fünf Ablage-Eingriffe aus Engywucks Standsübersicht, das Feld
`⏳ WARTET AUF ADAM`, die Übersicht ins Repo. **Kettenwirkung geprüft:** je
Eingriff die Geschwisterstellen (Register, Prüfraster, 6.6↔7.1 in beide
Richtungen). **Tatsächlich eingetretene Nebenwirkung — und sie ist der ganze
Ertrag dieser Nacht:**

**① Das Tor hat sich selbst gerechtfertigt.** Der Auftrag verlangte, jeden
Befund zu prüfen, *bevor* er ausgeführt wird — mit der Begründung, wer ihn
zuerst ausführe, habe ihn damit angenommen. Genau das trat ein: Der
5.34-Befund stimmte, aber seine Umsetzung hätte einen **nicht installierten
Dienst als fertig ausgewiesen**. Und ein zweiter Befund kippte ganz — 4.3 ist
nicht die Ordnerspiegelung. **Zwei von fünf Befunden hätten Schaden angerichtet,
wären sie mechanisch abgearbeitet worden.**

**② Der Nachtblock war seit zwei Tagen erledigt.** Sein Hauptstück — acht
sicherheitstragende Prüfzeilen, beschrieben als *substanziellste offene Arbeit
im Projekt* — war am 29.08. repariert worden. Drei Dokumente sagten offen: die
Betriebslage, der Katalog, und der darauf gebaute Auftrag. **Die Prüfregel
*Status ist ein Befund* deckt das LESEN ab; dieser Fehler entsteht beim
ERLEDIGEN.** Daraus die Umkehrung des Ablageweg-Grundsatzes: *Wer einen Punkt
abschließt, sucht die Stellen, die ihn als offen führen.* Nicht nur ein Weg
hinein — auch einer heraus.

**③ Fünf Fehlmessungen, die alle wie ein Ergebnis aussahen.** Die
Nachprüfung meldete im ersten Durchgang drei blinde Prüfer. **Keiner war
blind** — die Fehler lagen sämtlich in meiner Messung: eine zu grobe Erwartung
(`Limit` traf `Nachbarfehler`, weil dort `FEHL` steckt), zwei falsch
geschriebene (`Waechter` findet `Wächter` nicht), zwei wirkungslose Eingriffe
(im Aufrufer statt in der gelesenen Funktion; ein Pfad, den der Prüfer
mitzieht) und eine falsche Richtung. **Ergänzung zu den drei Auflagen:
`assert alt in t` beweist, dass etwas ersetzt wurde — nicht, dass es im
Sichtfeld des Prüfers lag.**

**④ Wer zwei gleiche Nummern auflöst, verschiebt die mit den wenigsten
Bezügen.** Bei 7.4 hingen an der einen sechs Prüfzeilen im Code, an der
anderen ein Doku-Verweis. Andersherum wäre der Fehler aus der Ablage in den
Code gewandert. *Universell — gilt für jede Kollision von Bezeichnern.*

**⑤ Fremde Arbeit wird nicht hineinkorrigiert.** Die Gegenprüfung liegt als
eigener Abschnitt **neben** der Übersicht, nicht in ihr. Wer korrigierend
hineinschreibt, macht seine Messung und die fremde hinterher
ununterscheidbar.

---

## Nacht zum 31.08., zweiter Block — elf F-Befunde, und was sie über Befunde lehren

**Was gebaut:** F-7, F-8, F-10, F-11, F-12, F-15, F-17 plus der Raster-Nachtrag.
**Kettenwirkung geprüft:** je Punkt die Geschwisterstellen; bei F-12 alle
Produktivmodule über den Syntaxbaum. **Tatsächlich eingetretene Nebenwirkung —
und diesmal ist sie ein Muster, kein Einzelfall:**

**① Drei von elf Befunden stimmten so nicht, und alle drei in dieselbe
Richtung: Sie waren zu klein beschrieben.** F-10 war nicht ein Filter mit
Fehlalarm, sondern in **beide** Richtungen falsch (`rm --recursive` wurde
verfehlt). F-7 war nicht eine falsche Zahl, sondern **sechzehn**. F-8 war nicht
eine tote Funktion, sondern eine tote Funktion **mit falscher Zusage** — sie
behauptete im Docstring, dieselbe Antwort wie die Entscheidung zu geben, und
tat es nicht. *Ein Befund ist eine Beobachtung, keine Vermessung. Wer ihn
umsetzt, ohne nachzumessen, repariert die halbe Sache.*

**② Zwei von elf hätten Schaden angerichtet.** F-9 hätte die 💰-Kostenschranke
gebrochen (`WebSearch` steht in `_COST_TOOLS`, die Funktion fasst beide Suchen
zusammen). F-16 stellt **jeden ausführbaren Auftrag** unter Zustimmungspflicht
und brach fünf abgenommene Prüfzeilen — gebaut, gemessen, zurückgenommen. **Der
Rückweg war ein `git checkout`, wie vorgesehen.**

**③ Der teuerste eigene Fehler war eine Shell-Form, keine Unachtsamkeit.**
`lauf | tail -1 && git commit` — **die Pipe maskiert den Fehlschlag**, weil der
Rückgabewert der einer erfolgreichen `tail` ist. Ein Commit ging mit 68/69
hinaus. Gestern war es ein Zeilenumbruch statt `&&`, heute eine Pipe. **Beide
Male half die Absicht nicht, die Form schon:** Der Lauf schreibt ohne Pipe in
eine Datei, danach wird gelesen, danach committet.

**④ Und der rote Lauf enthielt einen echten Fund** — eine Prüfzeile mit fest
verdrahtetem VPS-Pfad, die am Mac etwas anderes maß und dort nur *zufällig*
grün war. Sie fiel erst auf, als die Grund-Funktion vollständig wurde. *Ein
Fehler, der etwas findet, ist ein guter Tag.*

**⑤ Drei Messfehler in eigenen Gegenproben, alle sahen wie ein Ergebnis aus:**
eine zu grobe Erwartung (`Limit` traf die grüne Zeile *Nachbarfehler*, weil
dort `FEHL` steckt), zwei falsch geschriebene (`Waechter` findet `Wächter`
nicht), ein wirkungsloser Eingriff. **Und ein frisch gebauter Nachweis war
blind:** Er verglich `ls -l`, und das ist minutengenau — ein Lauf dauert dreißig
Sekunden, der Heartbeat ist immer gleich lang. *Gefunden von der Gegenprobe,
bevor er in den Lauf ging.*

- **Ein Sicherheits-Schalter darf nur weichen, wenn seine Begründung weicht** · 5.27 · **universell** — `Bash` stand auf der Nie-dauerhaft-Liste, weil eine Dauerfreigabe *unsichtbar fortgilt*. Nicht die Mächtigkeit war der Grund, sondern die Unsichtbarkeit. Erst als ein Umschalter den Zustand dauerhaft anzeigte, war die Begründung entkräftet — **deshalb mussten Knopf und Streichung in EINEN Commit** (getrennt entstünde dazwischen genau der Zustand, gegen den die Sperre gebaut war). **Tatsächlich eingetretene Nebenwirkung, die niemand vorhergesagt hatte:** Die Bereinigung beim Sitzungsstart hätte den neuen Knopfzustand bei jedem Neustart still geräumt — sie räumt genau, was auf der Liste steht. Der Knopf hätte funktioniert und nach jedem Neustart zurückgefallen; sichtbar wurde es nur, weil vier alte Prüfzeilen rot wurden und **einzeln umgestellt statt gelöscht** werden mussten. **Lehre: Die Prüfzeilen, die eine Entscheidung schützen, sind zugleich die Landkarte aller Stellen, die sie berührt.**
- **Eine Regel, die als Zufall schon gilt, gehört trotzdem hingeschrieben** · Zerlegung an `;`/`|` · **universell** — Zustandsverändernde Befehle (`cd`, `export`, `source`, `NAME=wert`) fielen vor dem Umbau in den Dialog, **weil sie in keiner Freiliste standen** — nicht weil jemand entschieden hätte, dass sie nicht zerlegt werden dürfen. Wer die Freiliste erweitert, hebt den Schutz auf, ohne es zu merken. **Tatsächlich eingetretene Nebenwirkung beim Prüfen:** Ohne die Bedingung bleibt das Urteil `DIALOG` — aus einem anderen Grund. Eine Prüfzeile, die nur das Urteil misst, wäre grün geblieben und hätte die Entkernung gedeckt; sie musste den **Grund** messen. **Lehre: Wo ein Schutz und ein Zufall dasselbe Ergebnis liefern, prüft man die Begründung, nicht das Ergebnis.**
- **Ein Prüfer, der nur das Urteil misst, kann aus dem falschen Grund grün sein** · A2 cd-Auflösungsbasis · **universell** — Die Prüfzeile *„nach cd wird der relative Pfad im richtigen Bereich gemessen"* blieb bei entkernter Basis-Auflösung **grün**: Ohne Basis löst der Pfad gegen das Arbeitsverzeichnis auf, und **das ist selbst ein erlaubter Bereich**. Das Urteil war zufällig richtig. Erst die Messung des *Pfades*, über den geurteilt wurde (`Entscheid.pfade`), machte sie scharf. **Zweite tatsächlich eingetretene Nebenwirkung:** Dabei fiel auf, dass `_pfad_artig` Argumente ohne Schrägstrich überspringt — die Prüfzeile maß eine **leere** Pfadliste und hätte nie etwas belegt. **Lehre: Wenn Schutz und Zufall dasselbe Ergebnis liefern, misst man die Zwischengröße, nicht das Ergebnis** — und eine Gegenprobe, die nur eine von zwei erwarteten Zeilen rot färbt, ist selbst ein Befund.
- **Eine absolut gebaute Wache ist nicht verhandelbar — auch nicht für einen freigegebenen Auftrag** · Auswerten-Knopf (B) · **universell** — Der Knopf war auftragsgemäß gebaut (kein neuer Pfad, nur bei eigenen Dateien) und scheiterte an einer Wache, die `process_user_text` im Dokument-Rückruf **absolut** verbietet. **Tatsächlich eingetretene Nebenwirkung:** Die Wache misst am *Aufrufknoten*, nicht an der *Bedingung darüber* — sie kann „nur bei eigenen Dateien" nicht sehen und soll es auch nicht. Der Reflex, sie zu verfeinern, ist der gefährliche: Eine unterscheidungsfähige Wache ist durch eine Bedingung umgehbar, die morgen jemand ändert. **Lehre: Wenn die erste Auflage eines Auftrags und eine bestehende Wache dasselbe sagen, ist das kein Zufall — dann ist der Auftrag in dieser Form nicht baubar, und das Melden ist das Ergebnis.**
- **Eine Stichwortsuche findet nur, was ihre eigenen Begriffe trägt** · Kontrollzählung (D) · **universell** — Vier Punkte galten als fehlend und existierten alle: Sie lagen auftragsgemäß woanders (zusammengeführt statt einzeln, im `docs`-Papier statt im Drehbuch, im Gedächtnis statt im Repo). **Zweiter Fall derselben Art binnen zweier Tage** (nach dem 5.26-Fehlbefund). **Lehre: Wer prüft, ob ein Auftrag angekommen ist, sucht am Ort des Ergebnisses — nicht mit den Wörtern des Auftrags.**
- **Eine Entscheidung, die auf einer Bedingung ruht, muss die Bedingung nennen** · F-19 · **universell** — Der Changelog vom 23.08. stellte einen Befund zurueck und nannte den Grund in einer Klammer: *seit H7 ist nichts Maechtiges mehr dauerfreigebbar*. Am 01.09. verliess `Bash` diese Liste — richtig, gegengeprueft, Adams Wunsch. **Niemand ging danach zu der Entscheidung zurueck, die auf der Klammer stand.** Die Klammer war das Beste am Eintrag: Ohne sie waere gar nicht messbar gewesen, dass er entwertet wurde. **Tatsaechlich eingetretene Nebenwirkung beim Nachtragen:** Derselbe Eintrag verwies auf die F-Liste — und **stand nie darin**, obwohl die Datei da schon existierte. Zwei unabhaengige Ablage-Fehler in einem Satz, keiner davon durch Unachtsamkeit: der eine, weil ein Verweis kein Eintrag ist, der andere, weil eine Bedingung keinen Rueckwaertszeiger hat. **Lehre: Wer eine Bedingung entfernt, sucht die Entscheidungen, die auf ihr standen** — das ist die Fenster-Regel eine Ebene hoeher: dort fragt man, was eine Verlaengerung offenlegt, hier, was eine Entfernung entwertet.
- **Ein Zeitgeber vor einem Schritt, der ohnehin wartet, beschleunigt nichts** · U-6 Route A · **universell** — Der Auftrag sah zwei Haelften vor: Server→Mac als Zeitgeber, Mac→iCloud beim Sitzungsstart (weil `launchd` die iCloud-Freigabe nicht erbt). Die Trennung war richtig, der Zeitgeber sinnlos: Wenn die zweite Haelfte auf den Sitzungsstart wartet, ist die Kette so schnell wie der Sitzungsstart — der Zeitgeber haette nur eine **zweite Stelle geschaffen, die still ausfallen kann.** Genau der tote `mirror-ki`: 330 Laeufe, alle gescheitert, drei Monate unbemerkt. **Tatsaechlich eingetretene Nebenwirkung:** Beim Bauen zeigte sich, dass das eigentliche Hindernis gar nicht die Technik war, sondern die **Ablage** — es gibt in iCloud keinen Rechnungsordner, sondern eine gewachsene Kundenstruktur, und der Generator kennt kein Schema. Ein geratener Zielordner haette in Adams Ablage hineingeschrieben. **Lehre: Bevor man eine Kette schneller macht, prueft man, ob ihr Ende ueberhaupt einen bestimmten Ort hat** — und wo keiner bestimmt ist, stellt man zu, statt einzusortieren.
- **Eine Aufzaehlung schuetzt, was darin steht, und nichts sonst — auch im Prueferselbst** · Register-Waechter · **universell** — Der Register-Waechter bildete seine Menge als `glob("*.py")`: nur Python, nur direkt unter `scripts/`. Alle Betriebsskripte (`.sh`) standen im Register **durch Disziplin, nicht durch Pruefung**, und `scripts/mac/` sah er ueberhaupt nicht. Aufgefallen ist es nur, weil ein neues Skript dort landete und der Waechter gruen blieb. **Tatsaechlich eingetretene Nebenwirkung, die die Reparatur ueberhaupt erst erlaubte:** Vor der Aenderung gemessen, wie gross die Luecke ist — **genau eins**, naemlich das eigene. Waeren es zwanzig gewesen, haette die Erweiterung einen Berg Altlasten aufgerissen und den Block gesprengt. **Lehre: Vor dem Schliessen einer Luecke misst man ihre Groesse** — dieselbe Erweiterung ist je nach Zahl eine Kleinigkeit oder ein eigenes Vorhaben.
- **Eine Gegenprobe braucht die Bedingung, nicht nur den Bereich** · U-3 Schalter-Strenge · **universell** — Ich hatte drei erwartete rote Zeilen benannt und zwei wurden rot. Kein Befund, sondern eine zu grob geschnittene Erwartung: Die dritte haengt an `len(teile) < 2`, einer **anderen** Bedingung im selben Zweig. **Tatsaechlich eingetretene Nebenwirkung:** Bei der naechsten Gegenprobe (U-4) habe ich die Erwartung je Zeile an ihre Bedingung gebunden — und dort stimmten fuenf von fuenf, waehrend die sechste erklaerbar gruen blieb. **Lehre: Die erwartete rote Zeile wird nicht nach Thema notiert, sondern nach der Codezeile, an der sie haengt** — sonst haelt man die eigene Ungenauigkeit fuer einen Befund oder, schlimmer, einen Befund fuer Ungenauigkeit.
