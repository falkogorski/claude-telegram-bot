<!-- ROLLE: sitzungsstart -->
# SITZUNGSSTART — für jede neue Instanz, vor der ersten inhaltlichen Arbeit

> **Warum dieses Dokument existiert:** Der Scratchpad einer Sitzung ist kein
> Archiv — er verschwindet mit ihr. Was eine Sitzung beim Start braucht, muss
> deshalb **hier** stehen und nicht in der Erinnerung der vorigen.
>
> Es ergänzt `WIEDERANLAUF.md` (ROLLE: `wiederanlauf`): Dort steht, **wie man
> sich einarbeitet**; hier steht, **was vor dem ersten Handgriff geschehen muss**.

---

## 1. Repos anhängen — beim START, nachträglich geht es nicht

**Am 25.07.2026, 15:45 belegt:** `claude-telegram-bot` war zugänglich,
`claude-bot-logs` wurde verweigert — gleicher Weg, gleiche Zugangsdaten. **Eine
laufende Sitzung lässt sich nicht nachträglich erweitern.**

| Repo | Pflicht? | Achtung |
|---|---|---|
| **`claude-bot-logs`** | **Ja** für Kontroll-/Planungssitzungen | Ohne das Log-Repo hat die Sitzung keine eigenen Augen und muss sich auf Erzählungen verlassen |
| **`claude-telegram-bot`** | Ja | ⚠️ **Branch `mac-produktivstand`, nicht `main`.** `main` steht seit Mai auf dem Initial commit — wer dort nachsieht, liest einen **toten Stand**. Genau dieser Fehler ist in der Nacht zum 25.07. passiert |
| **Business-Repo** | sobald es existiert | — |

### Das Zielbild dahinter — „Option E" [NEU 2026-07-25]

Der Kasten oben beschreibt eine **Einschränkung**, mit der wir heute leben. Sie
hat einen dokumentierten Grund: **Cloud-Sitzungen haben genau ein Repository,
und das ist auch von Anfang an nicht erweiterbar.** Adams Befund stimmte; die
Gegenvermutung war falsch.

Die Kombination, die alle drei Anforderungen zugleich erfüllt — **mehrere Repos**
· **Dauerbetrieb** · **Zugriff vom Handy** — ist:

> **VPS + tmux + Remote Control**, mit `additionalDirectories` für die weiteren
> Repos, optional ergänzt um **Channels** (offizielles MCP-Plugin, das
> Telegram-Nachrichten zweiseitig in die laufende Sitzung schiebt).

**Was das erspart:** die Suche nach einer eigenen Steuerungs-Schnittstelle. Es
gibt sie offiziell — **kein zweiter Bot** muss dafür gebaut werden.

**Was es nicht ersetzt:** Channels ist eine **Brücke, kein Assistent.** Ampel,
Freigabe-Postfach, Warteschlange, Sprachausgabe und Boten-Postfach kann es
nicht — das ist alles Claudia. Beides nebeneinander ist die sinnvolle Aufteilung,
nicht das eine statt des anderen.

**⚠️ Ungeprüft, bevor jemand darauf baut:** ob `additionalDirectories` auch in
Sitzungen greift, die der Server-Modus per `--spawn worktree` erzeugt. **Einmal
praktisch ausprobieren** — nicht annehmen. (Belegregel: ein Merkmal, das nicht
nachgemessen wurde, gilt nicht.)

## 2. Pflichtlektüre — lesen, nicht erinnern

In dieser Reihenfolge, jedes Mal frisch:

1. **`MIGRATION.md`** — das Drehbuch. Die **Änderungshistorie oben** trägt den
   jüngsten Stand; von dort rückwärts lesen, so weit nötig.
2. **`CLAUDE.md`** — die Grundregeln. Besonders: Kostenregel, Arbeitsmodus,
   Ablageweg-Grundsatz, Prüfregel „Status ist ein Befund".
3. **`ABHAENGIGKEITEN.md`** — welche Kette hängt woran, und was bricht still.
4. **`WIEDERANLAUF.md`** — Rituale, Landkarte, Rücksprung-Anleitung.

**Die Prüfregel gilt vom ersten Moment an:** Ein Punkt ist **nicht** offen, weil
eine Status-Zeile „OFFEN" sagt, und **nicht** fertig, weil ein Bericht es
behauptet. Changelog, Teilbauten, Code — erst danach gilt eine Aussage.

## 3. Rolle und Rechte klären

- **Wer führt gerade?** Das Führungs-Register in `CLAUDE.md` nennt pro Vorgang
  **genau eine** führende Sitzung. Alle anderen: **nur lesen**,
  Änderungswünsche als fertigen Textvorschlag.
- **Was darf ich nicht?** Der Bot editiert sein Repo nie (8.7) — auch die
  VPS-Kopie nicht. Geheimnis-Pfade sind auch fürs Lesen gesperrt.
- **Wo brauche ich Adams Zustimmung?** Alles mit Kostenanteil („unklar" zählt
  als „ja, warnen"), jede Änderung an 8.7, alles Unumkehrbare. Seit 9.4 gibt es
  dafür den **Parkplatz**: Anfrage ins Freigabe-Postfach, nicht selbst
  entscheiden.

### Die Namen der Instanzen (Adam-Entscheid 25.07.2026)

Namen sind hier kein Schmuck: Wer weiß, **wessen** Bericht er liest, weiß auch,
**wie weit** dieser Bericht trägt.

| Name | Rolle | Woher |
|---|---|---|
| **Claudia** | der Telegram-Bot — Alltag, Ampel, Freigaben, Warteschlange, Sprachausgabe | gewachsen; bleibt vorerst |
| **Engywuck** | die Kontroll-/Planungssitzung — liest jede Zeile Code, gegenliest Berichte | der Gnom, der das Südliche Orakel jahrzehntelang **vermisst und katalogisiert**, ohne je drinnen gewesen zu sein. Das ist genau diese Rolle: alles gelesen, die Maschine nie berührt |
| **Fuchur** | vorgemerkt — „der Träger" | für später, wenn eine tragende Rolle einen Namen braucht |

**Verworfen: Morla.** Ihr Kern ist Gleichgültigkeit („uns ist alles einerlei") —
die falsche Vorlage für eine Instanz, deren ganze Aufgabe genaues Hinsehen ist.

**Warum Claudia noch nicht umbenannt wird:** Eine Umbenennung ist eine
**Bezugs-Änderung** (Grundsatz „Struktur über Namen") — Rollen-Marker,
Register, Dokumentation müssten im selben Zug mit. Das lohnt erst, wenn aus dem
Entwicklungs-Bot das Produkt **Momo** wird, nicht mittendrin.

## 4. Die Zuerst-Prüfung (Adam-Anweisung 25.07.)

**Vier Fragen beantworten, bevor die erste inhaltliche Arbeit beginnt** — und
**das Ergebnis Adam kurz vorlegen**, damit er Lücken sofort schließen kann:

1. **Welche Rechte und Zugänge fehlen mir noch**, um wirksam zu arbeiten?
2. **Welches Wissen muss ich lesen statt erinnern?**
3. **Welche Bezüge und Abhängigkeiten bestehen** zu dem, was ich anfassen werde?
4. **Wo ist Adams Zustimmung nötig**, bevor etwas geschieht?

Eine Sitzung, die ohne diese Prüfung startet, arbeitet zwangsläufig mit Lücken,
die niemand kennt — und merkt es erst, wenn es teuer wird.

## 5. Was diese Sitzung am Ende hinterlassen muss

**Nichts Entscheidungs- oder Auftragsrelevantes darf ausschließlich im
Chatverlauf existieren.** Vor dem Ende (oder vor jeder Verdichtung):

- Beschlüsse → `MIGRATION.md` (Status-Zeile **und** Änderungshistorie)
- Übertragbares → `blaupause-notizen.md`, eine Zeile: **was gebaut · welche
  Kettenwirkung geprüft · welche Nebenwirkung tatsächlich auftrat**
- Neue Bezüge → `ABHAENGIGKEITEN.md`
- Offenes, das Adam betrifft → Freigabe-Postfach (9.4) oder ausdrücklich
  benannt im Weitergabe-Block

**Zeitstempel im Blockkopf aus dem Commit übernehmen**, nicht tippen:

```bash
git log -1 --format='%ad · %h' --date=format:'%d.%m.%Y, %H:%M'
```
