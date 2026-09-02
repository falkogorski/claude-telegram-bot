> **Zweck: WEITERGABE → Mick** · **Zu tun:** an ihn kopieren.
> **Adams Entscheidung liegt vor** (02.09., zu beiden Fragen „ja").
> **M-1 zuerst — es ist ein Nachtrag, der die Reihenfolge ändert.**

# Auftrag an Mick — der Signatur-Punkt, und ein Befund, der seine Begründung verloren hat

**Stichtag:** 02.09.2026, 10:06 MESZ · **Von:** Engywuck (Kontrolle)
**Gemessen an:** `395de2b` · **Nenner:** 3 Aufträge · 1 davon dringend ·
**0 davon Code am Sendepfad.**

**Adams Entscheidung:** *„ja zu beiden"* —
**A:** Signatur bekommt einen eigenen Punkt, geplant statt gebaut.
**B:** Bis dahin Beschriftung statt Knopf. Der Knopf ist **vertagt, nicht
abgelehnt.**

---

## Vorweg: eine Berichtigung, und sie ist meine

Ich habe Adam heute früh gemeldet, das Dokument-mit-Beschriftung gehe in die
Hauptsitzung — **als neuen Befund.** Er ist nicht neu. Er steht seit dem
**23.08.** im Drehbuch-Changelog:

> *„**Bewusst offen (F-Liste):** Dokument **mit Beschriftung** geht weiter in
> die Hauptsitzung (dort greift aber der Freigabe-Dialog, und seit H7 ist
> nichts Mächtiges mehr dauerfreigebbar) sowie 25 leichtere Befunde."*

Die eigene Prüfregel dieses Projekts verlangt, **vor** jeder Vorlage die
Changelog-Einträge zu lesen. Ich habe am Code gemessen und im Changelog nicht
nachgesehen. Deine Messung von heute Nacht war insoweit vollständiger als
meine.

**Zwei Dinge daran sind trotzdem neu, und sie sind der Grund für M-1.**

---

# M-1 · 🔴 Zuerst: der Befund hat seine Begründung verloren
### Ablage, kein Code · vor allem anderen

## ① Er steht nicht dort, wo er stehen soll

Der Eintrag sagt *„bewusst offen (F-Liste)"*. **In der F-Liste steht er
nicht.** Gemessen in `docs/f-befunde-reihenfolge.md`: sie führt F-1 bis F-18,
das Wort *Beschriftung* kommt nicht vor.

Das ist der Ablageweg-Grundsatz, wörtlich: **Eine Entscheidung, die keinen Weg
in die Ablage hat, ist verloren.** Hier war der Weg sogar benannt — und die
Datei existierte da schon.

## ② Seine Begründung stimmt seit gestern nicht mehr

Die Klammer trägt den ganzen Eintrag: *„seit H7 ist nichts Mächtiges mehr
dauerfreigebbar"*. **Gemessen an `395de2b`:**

```
_NO_ALWAYS_TOOLS = ({"WebFetch", "Write", "Edit", "MultiEdit",
                     "NotebookEdit"} | set(_COST_TOOLS))
```

**`Bash` steht nicht mehr darin.** Es hat die Liste am 01.09. mit `ae03f95`
verlassen — 5.27, der Genehmigungs-Umschalter. Das war richtig und
gegengeprüft; **niemand ist danach zu dem Eintrag zurückgegangen, der sich
darauf stützte.**

## ③ Wie weit das trägt — gemessen, nicht geschätzt

**Was heute noch hält** (alles am Code geprüft, alles **vor** dem
Dauerfreigabe-Kurzschluss in Zeile 3164):

| Schranke | Zeile | Wirkung |
|---|---|---|
| Repo-Schreibsperre (8.7) | 3051 | `Deny` |
| `bashfreigabe` ABWEISEN | 3091 | `Deny` |
| `_AUSGEHENDE_BEFEHLE` | seit 01.09. | `curl`, `wget`, `nc`, `ssh`, `scp`, `telnet` → Dialog |
| Geheimnis-Pfade | — | zu, auch fürs Lesen |
| `Write`/`Edit`/`WebFetch`/Kosten | 2367 | weiter nie dauerfreigebbar |

**Was nicht mehr hält:** Bash-Befehle, die `bashfreigabe` als **FREI** bewertet,
laufen im Auto-Zustand **ohne Rückfrage** — auch dann, wenn die Sitzung sie tut,
weil es in einem gelesenen Dokument stand.

**Die verbleibende Reichweite ist eng, und ich sage sie so eng, wie sie ist:**
Lesen und Auflisten in den freien Bereichen. **Kein** Weg nach außen (die
Ausgangsliste fängt ihn), **keine** Schreibrechte, **keine** Geheimnisse. Der
verbleibende Kanal ist **der Chat selbst** — die Sitzung könnte dazu gebracht
werden, Gelesenes hineinzuschreiben. Das berührt die zweite Richtung von Adams
Grundsatz: *sensible Daten verlassen das System nicht über Telegram.*

**Ich habe keinen ausgenutzten und keinen konstruierten Fall.** Was ich
gemessen habe, ist, dass eine Begründung entfallen ist und der Eintrag, der auf
ihr steht, unverändert dasteht.

## Was zu tun ist — Ablage, sonst nichts

1. **Den Befund in `docs/f-befunde-reihenfolge.md` eintragen**, mit der nächsten
   freien Nummer, im Wortlaut des Changelogs vom 23.08. **plus** der Messung von
   heute: die Klammer-Begründung ist entfallen.
2. **Den Changelog-Eintrag vom 23.08. mit einem Vermerk versehen** —
   nicht ändern, nicht glätten. Der Weg zum Ergebnis ist die Lehre.
3. **Eine Blaupause-Zeile**, und der dritte Teil ist der, auf den es ankommt:
   *Eine Entscheidung, die auf einer Bedingung ruht, muss die Bedingung
   nennen — und wer die Bedingung entfernt, sucht die Entscheidungen, die auf
   ihr standen.* Das ist die Fenster-Regel, eine Ebene höher: Dort fragt man,
   was während einer Verlängerung offen liegt; hier, was eine Entfernung
   entwertet.

**Ausdrücklich nicht:** die Wache anfassen, den Auto-Modus zurücknehmen, den
Beschriftungsweg schließen. **M-1 ist Ablage.** Ob und wie gebaut wird,
entscheidet Adam nach M-2.

---

# M-2 · Der Signatur-Punkt — geplant, nicht gebaut
### Adams Freigabe A

**Der Gedanke ist Adams** (01.09., im Bot-Chat): ein **Erkennungszeichen** in
Dateien, das zurückgeprüft wird, damit klar ist, dass eine Datei aus einer
unserer eigenen Sitzungen stammt. **Du hast ihn richtig geschärft:** ein bloßer
Code trägt nicht — wer ihn einmal sieht, schreibt ihn nach. Was trägt, ist eine
**Signatur über den Dateiinhalt mit einem Geheimnis**, das nur unsere Sitzungen
kennen.

**Was der Punkt festhalten muss — die vier Zeilen, ohne die er nichts wert ist:**

1. **Wofür er da ist:** Aus einer **offenen** Menge (*alles, was Adam mit
   Beschriftung hochlädt* — nicht aufzählbar, weil sie davon abhängt, was ihm
   jemand schickt) wird eine **geschlossene** (*was unsere eigenen Sitzungen
   geschrieben haben* — eine Menge mit Zugehörigkeitsregel). Das ist die
   Mengen-Regel dieses Projekts, auf den Eingang angewandt, gleiche Form wie
   `POSTFACH_GRENZEN`.
2. **Was er heute ersetzt:** `_adam_anteil` prüft `forward_origin` — **die
   Pfeil-Geste, nicht die Herkunft des Inhalts.** Lädt Adam eine Datei hoch,
   gilt ihr Inhalt als seiner, auch wenn er sie zwei Minuten vorher per Mail
   bekommen und nie geöffnet hat. Die richtige Frage lautet *stammt das aus
   unserem eigenen Haus?*, nicht *ist das weitergeleitet?*
3. **Die ehrliche Grenze, im selben Absatz:** Eine Signatur beweist
   **Herkunft, nicht Ungefährlichkeit.** Wird eine unserer Sitzungen selbst
   getäuscht — durch eine Webseite, eine Mail, ein Dokument, das sie liest —,
   signiert sie die Täuschung weiter. **Deshalb bleiben die harten Schranken
   auch für signierte Aufträge in Kraft:** Repo-Schreibsperre, Geheimnis-Pfade,
   Kostenfreigaben, root. Genau wie bei Adams getipptem Text. **Eine Signatur
   ersetzt keine Schranke — sie ersetzt das Raten.**
4. **Was danach möglich wird:** Erst mit diesem Merkmal ist die Wache
   präzisierbar (*erreicht Fremdinhalt die Sitzung* statt *kommt
   `process_user_text` vor*), und erst dann ist der „Auswerten"-Knopf baubar.
   **Vorher nicht.**

**Akzeptanzkriterium — bitte wörtlich so:**

> *Ein schriftliches Konzept existiert und ist aktuell.* Ausdrücklich **nicht**
> „eine Signatur läuft". Gleiche Bauform wie 9.17 und der
> Modell-Souveränitäts-Punkt: **planen statt bauen.**

**Status:** OFFEN, **nicht terminiert.**

## ⚠️ Zur Nummer — sie gehört Adam, und es droht eine Kollision

Im Drehbuch steht bereits ein **`9.NN Modell-Souveränität`** mit offener
Nummer. **Ein zweites `9.NN` wäre nicht auffindbar.** Nimm deshalb einen
unterscheidbaren Platzhalter — Vorschlag `9.NN-S Herkunfts-Signatur` — und
**melde die offene Nummernvergabe**, wie du es bei 9.17/9.18 gemacht hast.
Beide Platzhalter zusammen in einer Zeile an Adam, damit er sie in einem Zug
vergeben kann.

**Nachbarschaft:** Der Punkt gehört zur Eingangs-Absicherung. **Die hat selbst
keinen Drehbuch-Punkt** — gemessen: kein Punkt trägt sie, obwohl `CLAUDE.md`
einen ganzen Abschnitt und eine verbindliche Reihenfolge dafür führt. **Das ist
eine Beobachtung, kein Auftrag** — trag den Signatur-Punkt vorerst bei 9.5
(E-Mail-Anbindung) in die Nachbarschaft und **nenne die Lücke in deinem
Bericht.** Ob die Eingangs-Absicherung einen eigenen Punkt bekommt, ist Adams
Entscheidung, nicht deine und nicht meine.

---

# M-3 · Den Knopf sauber vertagen
### klein, Ablage

Adam hat entschieden: **bis zur Signatur schreibt er eine Beschriftung dazu.**
Fünf Wörter, funktioniert heute. **Das ist kein Notbehelf** — es ist der Akt,
der den Inhalt zu seinem Auftrag macht. Der Knopf hätte genau diesen Akt
ersetzt.

**Zwei Dateien nachziehen, beide nur um Adams Entscheid:**
- `docs/befund-auswerten-knopf-kollision.md` — Ergebnis eintragen: **Weg ③
  entfällt** (Adams Klarstellung: es geht um Ausführung, nicht um Darstellung),
  **Weg ① kommt später** und dann auf dem richtigen Merkmal, **Weg ② entfällt.**
- `docs/gedanke-zweiter-chat-und-auswerten-knopf.md` — der Knopf ist **vertagt,
  nicht abgelehnt**, und hängt jetzt am Signatur-Punkt.

**Die Wache bleibt unangetastet.** Sie hat richtig gehalten. Dass sie am
Aufrufknoten misst und nicht am Auftrag, ist ihre Grenze, nicht ihr Fehler —
und die Grenze wird von M-2 aufgelöst, nicht von einer Verfeinerung.

---

# 🚫 Nicht bauen

| | Was | Warum |
|---|---|---|
| 1 | **Die Signatur selbst** | geplant vor gebaut, Adams Entscheid |
| 2 | **Die Wache präzisieren** | erst wenn das richtige Merkmal existiert |
| 3 | **Der „Auswerten"-Knopf** | hängt an 1 |
| 4 | **Den Beschriftungsweg schließen** | wäre eine Verhaltensänderung ohne Entscheid — und nähme Adam einen Weg, den er täglich nutzt |
| 5 | **Am Auto-Modus drehen** | er ist gegengeprüft und richtig; der Befund liegt nicht bei ihm |

**Wenn beim Eintragen eine Frage auftaucht, die Adam beantworten müsste:
liegen lassen und melden.** Nicht ableiten.

---

# Auflagen

1. **`bash scripts/regressionstest.sh` vor jedem Commit** — auch bei reiner
   Ablage. Der letzte Doku-Commit, der ihn übersprang, hinterließ zwei rote
   Zeilen auf dem VPS.
2. **Commit-Nachrichten über Heredoc** (`git commit -F - <<'EOF'`), nie über
   `-m`, und **nie** an einen dateiändernden Heredoc gekettet.
3. **`ABHAENGIGKEITEN.md`** — der Signatur-Punkt bekommt seine Zeile beim
   Anlegen, nicht beim Bauen.
4. **Blaupause-Zeile für M-1**, mit der tatsächlich eingetretenen Nebenwirkung.
5. **Bericht mit Nenner:** *drei von drei* oder *zwei von drei, und welcher
   fehlt.*
6. **Nichts deployen.**

**Gut genug wenn:** M-1 eingetragen · M-2 als Punkt mit den vier Zeilen und dem
wörtlichen Akzeptanzkriterium · M-3 nachgezogen · Lauf grün · die zwei offenen
Nummern in einer Zeile an Adam.
