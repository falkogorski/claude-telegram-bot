**Zweck: WEITERGABE → Mick** · **Zu tun: nach Block 5 einplanen; die Quellenliste kommt von Claudia (eigener Auftrag).**

# Block 6 für Mick: Frische-Strang (Alternativen · Zufluss · Vorschlagsweg)

23.09.2026, 17:4x · Engywuck · Adams Entscheide von 17:3x: Block 6 nach den fünf laufenden; Bewertung nur auf Adams Wort; kein Modellaufruf am Zeitgeber. Konzept: `20260923_konzept_frische_strang.md` (bei Adam).

**Gut genug wenn:** Der Wochenlauf des Monitors legt neue Feed-Einträge ab und meldet fällige Alternativen; `/neues` liefert Adam eine Sichtung mit Knopf, der einen Laufplan-Eintrag erzeugt; kein Zeitgeber ruft ein Modell.

## 6.1 Fähigkeits-Register (Erweiterung von `components.json`, kein neues Register)

Je Eintrag drei optionale Felder: `zweck` (Fähigkeit in einem Satz), `alternativen` (Liste: Name, Adresse, zuletzt gesichtet), `ersatz_aufwand_h`. Der Monitor (`version_monitor.py`) meldet **[Alternativen fällig]** wie heute bei `manual` nach `intervall_tage`; gleiche Meldezeile, gleiche `gesehen`-Logik. Erste Einträge: Fremddienst Transkripte (freetranscriptapi.com, Alternative youtube-transcript.ai), Websuche-Anbieter, edge-tts, faster-whisper, PDF-Weg, Modelle. Register-Zeile in `ABHAENGIGKEITEN.md`.

## 6.2 Zufluss `scripts/zufluss.py`

- Liest `quellen.json` (Adams Hand; Claudias Liste als Vorlage), holt RSS/Atom mit Zeitlimit je Quelle, legt neue Einträge (Kennung, Datum, Quelle, Titel, Adresse) nach `~/.claude/zufluss/eingang.jsonl`, entdoppelt über Kennung, hält 60 Tage.
- Hängt am **bestehenden** Monitor-Timer (Mo 04:20), kein eigener Zeitgeber. Kein Modell, kein Telegram. Gescheiterte Quellen als Zeile im Monitor-Log, nicht an Adam (Claudias Auftrag [Meldungen nur, was Adam betrifft]).
- Der Log-Kurier nimmt `eingang.jsonl` mit (Include-Regel prüfen, Wirkungs-Regel: Dateiliste danach ansehen).
- **Fremdinhalt ist Daten:** Titel und Adressen werden nur abgelegt, nie ausgeführt oder als Anweisung gelesen; die Datei wird bei `/neues` als Mitschrift übergeben, nicht als Stimme (Eingangs-Absicherung 23.08.).

## 6.3 `/neues` mit Wirkung

- Adams Befehl. Claudia bekommt den Eingang seit der letzten Sichtung, gruppiert nach Bauteil (über `zweck`/`alternativen`) und Landschaft, höchstens drei Vorschläge.
- Je Vorschlag Knopf **[in den Laufplan]** → deterministischer Eintrag ins Auftragsbuch/Freigabe-Postfach; kein Modelllauf beim Knopf. Merker [gesichtet bis] wird beim Antworten gesetzt.
- Kurs-Blick bekommt die Zeile [Neu am Markt, für uns relevant] aus derselben Datei (Engywuck liest sie im Log-Archiv).

## Prüfzeilen, ausführend

1. Zufluss mit Attrappen-Feed: zwei Einträge, einer doppelt → genau zwei Zeilen im Eingang, zweiter Lauf fügt nichts hinzu.
2. Quelle antwortet nicht → Lauf endet grün mit Log-Zeile, kein Telegram-Aufruf (Attrappe zählt Aufrufe: 0).
3. Monitor mit Eintrag, dessen Alternativen-Sichtung älter als `intervall_tage` → Meldezeile [Alternativen fällig].
4. Knopf [in den Laufplan] → Eintrag vorhanden, kein Modellaufruf (Attrappe zählt 0). Gegenprobe: Knopf-Handler entfernen → rot.
5. `scripts/test_zielumgebung.sh` fährt `zufluss.py` mit `env -i` (root-Dienst ohne HOME, Lehre vom 29.07.).

## Was nicht dazugehört

Kein automatischer Wochenbericht, keine Stichwortfilter, keine Newsletter per Mail, keine Konten. Was eine Quelle nur per Seite bietet, wird `manual` mit Intervall.
