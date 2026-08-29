# Bauauftrag — Die offenen Updates einspielen, in drei getrennten Schritten

**Zustand: vereinbart, nicht gebaut**
**Weg:** Claudia → Engywuck (Prüfung) → Mick (Bau)
**Angelegt:** 29.08.2026, 00:55 Uhr
**Grundlage:** `2026-08-25_empfehlung-offene-updates.md` — die Reihenfolge dort
gilt unverändert, dieser Auftrag macht sie ausführbar.
**Anlass:** Adam am 29.08.2026, 00:33 Uhr — „Node darf auch bald dran kommen.
Die anderen Updates schon vollzogen?"

---

## Der Stand, gemessen am 29.08.2026 um 00:46 Uhr

| Posten | installiert | Ziel | Zustand |
|---|---|---|---|
| `anthropic` in der Anforderungsliste | gestrichen | — | ✅ erledigt (Adams Entscheid 28.08., `requirements.txt` Zeile 12) |
| `pymupdf` | 1.28.0 | 1.28.2 | offen |
| `claude-agent-sdk` | 0.2.127 | 0.2.144 | offen |
| `claude-code-cli` (global, npm) | 2.1.209 | 2.1.241 | offen |
| `nodejs` | v22.23.1 | v24.19.0 | offen |
| `litellm` | **nicht installiert** | — | ✅ entfällt |

**Zwei Posten haben sich seit dem 25.08. erledigt**, beide ohne Update:

1. **`anthropic`** steht nicht mehr als direkte Anforderung. Das Paket ist in der
   Umgebung noch vorhanden (0.120.0), jetzt als Mitzieher. **Kein Handlungsbedarf**
   — es zieht keine Aufmerksamkeit mehr auf sich, sobald der Wächter die
   Anforderungsliste als Maßstab nimmt (siehe Auftrag 4).
2. **`litellm`** ist in der Bot-Umgebung gar nicht installiert. Die offene Frage
   aus der Empfehlung — liegt der Vermittler im Pfad oder nur bereit — ist damit
   beantwortet: **er liegt nicht im Pfad.**

**Der Versions-Wächter läuft ordnungsgemäß**, montags um 04:20 Uhr
(`claude-version-monitor.timer`, letzter Lauf 24.08., nächster 31.08.). Sein
Schweigen war sein Takt, kein Ausfall.

---

## Vorbedingung — sie geht allem voraus

**Rang A des Entkernungs-Befunds gehört VOR den SDK-Block.** Der Start-Wächter
ist das Sicherheitsnetz für jedes dieser Updates, und er steht selbst auf der
Liste der blind gemessenen Prüfzeilen: Im abgekoppelten Betrieb meldet er
„sauber hochgekommen" über einem toten Bot.

**Ein Netz mit bekannter Masche darf nicht gespannt werden, während man
darüber läuft.** Solange Rang A offen ist, bleibt Schritt 2 dieses Auftrags
gesperrt. Schritt 1 (Patch) ist davon nicht berührt.

**Zweite Vorbedingung, aus der Empfehlung übernommen:** Der Ist-Stand aller drei
Maschinen wird vorher eingefroren — Mac 3.12.13, VPS 3.13.5, Engywucks Container
3.11.15. Drei Python-Fassungen bedeuten, dass ein grüner Prüflauf auf einer
Maschine über die beiden anderen nichts aussagt.

---

## Schritt 1 — `pymupdf` 1.28.0 → 1.28.2

Zwei Patch-Stufen, keine Schnittstellenänderung, betrifft die PDF-Verarbeitung.
Läuft im normalen Updater-Lauf mit Regressionstest und automatischem Rückbau.

**Eigener Commit.** Kein Wartezimmer, keine Bündelung mit Schritt 2.

**Nachweis:** Ein PDF erzeugen und über das Postfach zustellen — der Weg, den
Adam täglich benutzt. Ein grüner Regressionslauf allein genügt hier nicht, weil
die PDF-Strecke Werkzeuge außerhalb von Python berührt.

---

## Schritt 2 — `claude-agent-sdk` und `claude-code-cli` als ein Block

**Sie gehören zusammen und dürfen nicht auseinanderlaufen:** Das SDK bringt die
CLI mit; eine global abweichende Fassung erzeugt einen Unterschied, den niemand
sieht, bis etwas klemmt.

- `claude-agent-sdk` 0.2.127 → 0.2.144 (siebzehn Stufen, bewusst gepinnt)
- `claude-code-cli` global 2.1.209 → 2.1.241 (npm, gehört root, von Hand)

**Auflagen:** eigener Arbeitsbaum neben dem Repo, eigene virtuelle Umgebung,
vollständiger Regressionslauf dort, erst dann übernehmen. Pin danach nachziehen.

**Der Grund, warum dieser Schritt der lohnende ist:** Neue SDK- und CLI-Fassungen
bringen regelmäßig Änderungen an Werkzeugen, Freigabewegen und Fähigkeiten mit.
**Es ist möglich, dass sich Punkte, an denen wir gerade selbst bauen, damit
erledigen** — der Freigabedialog und die Berechtigungsprüfung sind die
naheliegenden Kandidaten. Das ist ein begründeter Verdacht, keine Zusage, und er
lässt sich nur durch das Update prüfen.

**Deshalb eine Auflage, die über das übliche hinausgeht:** Nach dem Einspielen
werden die Änderungsnotizen der übersprungenen Fassungen daraufhin gelesen, ob
sie den Bash-Freigabe-Auftrag
(`2026-08-29_bauauftrag-bash-freigaben-weniger-druecke.md`) ganz oder teilweise
überflüssig machen. **Ein Befund dazu geht an Adam, bevor gebaut wird** — sonst
bauen wir etwas nach, das mitgeliefert wurde.

---

## Schritt 3 — `nodejs` v22.23.1 → v24.19.0, eigener Termin

Adam am 29.08., 00:33 Uhr: „Node darf auch bald dran kommen." **Bald heißt hier:
nach Schritt 2, und getrennt davon.**

Node 22 ist eine gepflegte Langzeitfassung und läuft. Der Sprung auf 24 berührt
die CLI, alles npm-Installierte und möglicherweise Werkzeuge, die außerhalb des
Prüflaufs stehen.

**Die Trennung hat einen Grund, der nichts mit Vorsicht zu tun hat:** Zwei
Fundament-Updates im selben Block machen die Ursachensuche unmöglich, falls
danach etwas klemmt. Getrennt ist die Ursache eindeutig.

**Auflagen:** Probelauf im Klon, geplanter Rückweg, und eine Liste der Werkzeuge,
die npm-abhängig sind, **bevor** umgeschaltet wird.

---

## Auftrag 4 — Der Wächter misst gegen die Anforderungsliste

`anthropic` hat drei Wächterläufe lang einen roten Punkt erzeugt, obwohl es
niemand einbindet. **Ein roter Punkt, für den es nichts zu tun gibt, entwertet
die übrigen** — genau der Ermüdungseffekt, der auch die Bash-Dialoge unbrauchbar
gemacht hat.

**Auftrag:** Der Versions-Wächter meldet nur Posten, die als direkte Anforderung
geführt sind oder ausdrücklich in seiner Beobachtungsliste stehen. Mitzieher
erscheinen nicht.

---

## Was kann brechen und wer merkt es

| Was | Wer merkt es | Vorkehrung |
|---|---|---|
| **Ein Update geht durch, der Bot kommt nicht mehr hoch** | Der Start-Wächter — der aber selbst die bekannte Masche hat | Rang A des Entkernungs-Befunds ist Vorbedingung. Ohne ihn ist Schritt 2 gesperrt |
| **Der Regressionslauf ist grün, obwohl etwas gebrochen ist** | Niemand sofort | Probelauf im getrennten Arbeitsbaum, Übernahme erst danach, je Posten ein eigener Commit — damit ein Rückweg je Posten existiert |
| **Node bricht etwas außerhalb des Prüflaufs** (PDF-Erzeugung, Medienverarbeitung, Sprachausgabe) | Adam, beim nächsten Gebrauch, unter Umständen Wochen später | Node getrennt einspielen. Danach die selten laufenden Werkzeuge einmal von Hand auslösen, statt auf den Prüflauf zu vertrauen |
| **Die drei Python-Fassungen laufen weiter auseinander** und ein Prüfer wird blind, wie in der Nacht zum 25.08. | Niemand | Ist-Stand aller drei Maschinen vor dem Beginn einfrieren, danach vergleichen |
| **Der SDK-Sprung ändert das Verhalten der Freigaben**, und der Bash-Auftrag wird parallel gebaut | Niemand — beide Seiten halten sich für zuständig | Die Auflage aus Schritt 2: erst die Änderungsnotizen lesen, Befund an Adam, dann bauen |
| **Der Rückstand wächst wieder still** | Der Wächter meldet montags, aber eine Meldung ohne Entscheidung wird zur Tapete | Adams Vorschlag aus der Empfehlung: ein festes monatliches Wartungsfenster für grüne und gelbe Posten. **Diese Entscheidung steht noch aus** |

---

## Was Engywuck entscheiden darf

1. **Ob Schritt 1 wirklich vor Rang A laufen darf.** Ich halte einen
   Patch-Sprung für unkritisch genug; wenn er das anders sieht, wartet alles.
2. **Ob die Auflage in Schritt 2** — Änderungsnotizen lesen, bevor der
   Bash-Auftrag gebaut wird — die Reihenfolge der beiden Aufträge umkehrt.
   Möglich ist, dass der Bash-Auftrag ganz entfällt.
3. **Ob das monatliche Wartungsfenster** als eigener Auftrag ausgearbeitet wird.
   Es ist Adams Vorschlag aus dem 25.08. und bis heute unentschieden.
