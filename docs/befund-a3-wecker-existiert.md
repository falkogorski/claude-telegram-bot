<!-- ROLLE: befund-a3-wecker -->
# Befund A3: Der Wecker war schon da — er heißt nur nicht so

**Stichtag:** 2026-08-20 · **überholt durch:** — · **maßgeblich ist diese
Datei** · **Auftrag:** Claudia 20.08., freigegeben durch Adams Linien-Entscheid

## Das Ergebnis

**Gebaut wurde nichts. Gemessen wurde alles.** Adams drei Bedingungen sind im
Bestand bereits erfüllt; was fehlte, war nicht der Mechanismus, sondern **der
Beleg**. Den liefert jetzt `scripts/test_wecker_a3.py` mit sechs ausführenden
Prüfungen.

## Warum der Auftrag von einer Fehlannahme ausging

Claudias Diagnose lautete: *„Greift das Limit, ruht die Sitzung. Sie läuft
nicht im Hintergrund weiter … Ohne einen äußeren Anstoß **kann** sie nicht
bemerken, dass wieder gearbeitet werden darf."* Und: *„Einen solchen
Selbstanstoß gibt es heute nicht — im Quelltext gesucht, keine Fundstelle."*

**Die Suche war richtig und das Ergebnis stimmt: Einen expliziten Wecker gibt
es nicht.** Übersehen wurde etwas anderes — **der Worker schläft gar nicht
ein.** Im Kontingent-Zweig (H2 Ebene 1, seit 25.07.) geschieht dreierlei:

1. Die Nachricht geht **an den Kopf** der Warteschlange zurück.
2. `pausiert_bis` wird auf den Rücksetzzeitpunkt gesetzt.
3. Der Persistenz-Vermerk geht auf **„offen"**.

Und die Worker-Schleife wartet diese Pause **in Häppchen von höchstens
dreißig Sekunden** ab, meldet dann „Kontingent ist wieder da" und arbeitet
weiter. **Es gibt keinen Weckruf, weil niemand einschläft.**

Für den Fall, dass der Bot **während** der Pause neu startet, greift der
Startup-Reconcile: Status „offen" heißt *nachweislich nie an Claude geschickt*
und wird **automatisch** nachgeholt — im Gegensatz zu „in Bearbeitung", das nur
gemeldet wird, weil dort schon eine halbe Antwort draußen sein könnte.

## Adams drei Bedingungen, einzeln gemessen

| Bedingung (20.08.) | Wo sie steht | Gemessen |
|---|---|---|
| **genau ein nachgeholter Lauf** | Worker arbeitet die Queue ab, kein zweiter Anstoß | Pause abgewartet, Nachricht danach abgearbeitet |
| **nur bei vermerkten Nachrichten** | `pending` mit Status „offen" | ohne Vermerk meldet der Reconcile nichts |
| **höchstens drei Weckversuche** | `_MAX_RESUME_ATTEMPTS = 3` | Wert geprüft, Bremse aktiv |

## Warum kein zweiter Wecker gebaut wurde

**Die Kurs-Regel verlangt für einen neuen Wächter einen echten Vorfall und den
Nachweis, dass kein bestehender erweiterbar ist.** Beides fehlt hier. Ein
zweiter Wecker neben dem wartenden Worker wäre ein Wächter dritter Ordnung —
und schlimmer als überflüssig: Zwei Stellen, die dieselbe Nachricht nachholen,
erzeugen Doppelantworten. Genau das verhindert die Hybrid-Logik von 5.2.

## Die Lehre

**Ein Auftrag kann sorgfältig recherchiert und trotzdem von einer Fehlannahme
getragen sein.** Claudia hat im Quelltext gesucht, das Richtige gefunden und
den falschen Schluss gezogen — weil sie nach einem *Ding* suchte (einem
Wecker) statt nach einem *Verhalten* (wartet der Worker?). Die Frage „gibt es
X?" ist schwächer als „was geschieht in Fall Y?".

**Und der Wert des Auftrags bleibt trotzdem:** Ohne ihn hätte niemand gemessen,
ob die Zusage trägt. Sie trug — aber das wusste bis heute niemand, sondern alle
nahmen es an. Ein Beleg, der eine Vermutung bestätigt, ist keine verlorene
Arbeit; er ist der Unterschied zwischen Wissen und Hoffen.

## Im selben Zug richtiggestellt

Der Kopftext der Stundenblume versprach: *„Sieht sie etwas Auffälliges, weckt
sie ein Modell."* **Das war nie gebaut** — sie führt ausschließlich
Systembefehle aus. Claudias Randbefund, gefunden bei genau dieser Suche. Wer
sich darauf verlassen hätte, wartete auf einen Mechanismus, den es nie gab.
