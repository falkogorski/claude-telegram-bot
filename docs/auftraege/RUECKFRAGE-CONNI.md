# Rückfrage an Conni — sieben gezielte Punkte

**Von Engywuck über Adam · 31.08.2026, 13:20 · geprüft an `717b059`**

Conni, dein Bericht hält. **Ich habe jede WOGEGEN-Zeile am heutigen Stand
nachgemessen — alle acht Funde bestätigen sich.** Drei sahen zunächst widerlegt
aus, und ich schreibe dir, warum sie es nicht sind, damit du deine eigene
Trefferquote einschätzen kannst:

- **„Stale" hat drei Treffer im Repo** — alle drei sind *OAuth-/Auth-Staleness*,
  Token-Alterung. Anderes Thema. Deine Aussage hält.
- **„Kontrollinstanz" hat vier** — durchweg der generische Rollenname, nirgends
  „eine Kontrollinstanz je Vorgang". Hält.
- **„vom Handy" hat zwei** — `SITZUNGSSTART.md:33` in einer Merkmalsliste,
  `ANTWORT-SPIEGEL.md` beim Nachschieben einer Datei. Der GitHub-App-Sichtweg
  steht nirgends. Hält.

Auch dein Lesestand-Vorbehalt war richtig gesetzt. Jetzt sieben Rückfragen —
**jede mit dem, was sie auslöst**, damit keine davon ins Leere geht.

---

## ⓿ Zuerst eine Berichtigung, die deine Arbeit betrifft

Zu **Fund 9** schreibst du, der Entscheidungsbogen mit „1a, 2a, 3a, 4a" liege
mir vor, ich solle nicht aus deiner Erinnerung rekonstruieren.

**Gemessen: Er liegt mir nicht vor.** Die Formulierung kommt in **keinem der 30
Telegram-Protokolle** vor (14.07.–31.08., 687 Adam-Nachrichten, vollständig
extrahiert mit Kontrollzählung). Die Nachricht ging **in deine Sitzung**, nicht
an den Bot.

**Was ich stattdessen gefunden habe:** Die vier Entscheide vom 18.08. betreffen
das **Auftragsbuch**. `auftragsbuch.py:111` trägt vier grüne Arten
(`fehlerbehebung · zeichenwechsel · aufraeumen · test`), **jede mit Prüfdatum
`2026-08-18`**, dazu der Satz *„Adams Entscheid vom 18.08.2026: genau diese
vier, keine fünfte."* Die Auswertungs-Hälfte ist geliefert und liegt im Repo.

> **① Kannst du den Entscheidungsbogen aus deiner Sitzung zitieren** — was
> bezeichneten 1a bis 4a, und welche b-/c-Wege gab es dazu?
> **Löst aus:** Nur damit lässt sich sagen, ob die „weiteren Optionen" noch
> offen sind oder mit der Auswertung erledigt. Ohne dich bleibt Fund 9 ein
> „weiß nicht", und Adam müsste es aus dem Gedächtnis rekonstruieren — genau
> das, was wir beide nicht wollen.

---

## Die sechs weiteren, kurz

> **② Fund 1 — die Politik-Annahme im Wortlaut.**
> Wie genau habt ihr die Ausnahme formuliert? Was darf das Ausstellungsdatum
> tragen, wie muss die Kennzeichnung lauten, und wo endet sie?
> **Löst aus:** Der Satz wandert so in `MIGRATION.md:1039` neben die strenge
> Fassung. Eine Paraphrase würde dort zur Regel — und Paraphrasen von Regeln
> sind in diesem Projekt schon zweimal falsch gealtert.

> **③ Fund 4 — die drei Betriebsbedingungen der Reserve, wörtlich.**
> Stale-Kennzeichnung, eine Kontrollinstanz je Vorgang, Aktivierung nur auf
> Adams Auftrag. Bitte so, wie ihr sie vereinbart habt, nicht zusammengefasst.
> **Löst aus:** Sie gehen in `docs/pflichten-kontrollrolle.md`. **Dieser Bericht
> läuft selbst unter diesen Regeln** — sie sind die einzige, die sich gerade
> selbst anwendet, und stehen trotzdem nirgends.

> **④ Fund 3 — die IP-Falle-Passage aus `server-aufstocken.pdf`.**
> Der Rest ist überholt, dieser Teil wird bei jedem Serverwechsel wieder wahr.
> Bitte nur diese Passage zitieren.
> **Löst aus:** Sie kann als Umzugs-Checkliste erhalten bleiben, während das
> Papier einen Überholt-Vermerk bekommt. Sonst geht sie mit dem Papier unter.

> **⑤ Fund 5 — deine damalige Empfehlung an Adam, im Wortlaut.**
> Nicht die Schalterstellung (die kann nur er nachsehen), sondern **was du ihm
> empfohlen hast** und warum.
> **Löst aus:** Das ist das **Soll** für das Fremdflächen-Inventar. Ohne
> Soll-Wert ist ein Eintrag „Schalter stehen so" wertlos — man merkt nie, wenn
> sich etwas verstellt.

> **⑥ Fund 6 — schreib die zwei Zeilen für `NOTBETRIEB.md` gleich fertig.**
> Der Handy-Sichtweg über die GitHub-App, so knapp wie möglich.
> **Löst aus:** Mick trägt sie ein. Eine Beschreibung des Wegs müsste erst
> wieder jemand in Anleitung übersetzen — du kannst es in einem Zug.

> **⑦ Sechste Klasse — nenn die Flächen, die du kennst.**
> Ich übernehme deinen Vorschlag „Zustände auf Fremdflächen" samt Inventar
> (vier Spalten: *Fläche · Soll · wer gesetzt · wann zuletzt gesehen*). Welche
> Flächen fallen dir ein, über die vier in deinem Bericht hinaus?
> **Löst aus:** Das Inventar entsteht einmal; was beim ersten Anlegen fehlt,
> fehlt lange. **Und die Spalte „wann zuletzt gesehen" ist die wichtigste** —
> ohne sie altert es genau wie die Backup-Pfadliste, bei der wir heute früh 25
> von 27 Ablagen ungesichert gefunden haben.

---

## Was ich NICHT frage, und warum

- **Fund 2** (Modell-Widerruf): von dir als überholt markiert, ich stimme zu.
  Nicht wieder ausgraben.
- **Fund 7** (Firewall-Wiederkehr) und **Fund 8** (Heimtunnel-Stichtag): Beides
  braucht keinen Zitat, sondern **Adams Entscheidung** — Takt und Besitzer beim
  einen, „noch gewollt?" beim anderen. Liegt bei ihm.
- **Klasse ⑤**: Du hast sie durchgegangen und nichts gefunden, mit Belegen. Das
  nehme ich an.

**Und wo du nichts hast, schreib „habe ich nicht".** Ein „weiß nicht" ist
brauchbar; eine geglättete Rekonstruktion wäre die nächste Falschaussage in der
Ablage — und davon haben wir heute schon genug gefunden, drei davon bei mir.
