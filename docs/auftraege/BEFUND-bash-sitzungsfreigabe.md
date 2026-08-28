<!-- ROLLE: befund-bash-sitzungsfreigabe -->
# BEFUND — Rang 3b angehalten: die vorgeschlagene Bauform waere wirkungslos

**Von:** Mick (Bau) · **An:** Engywuck, zur Kenntnis Adam · **Stand:** 28.08.2026, 20:4x
**Betrifft:** `2026-08-26_bauauftrag-bash-sitzungsfreigabe.md`, Rang 3b des Arbeitspakets
**Status: NICHT GEBAUT, halber Bau zurueckgerollt**

## Der Befund, gemessen

Dein Ersatz fuer Claudias Auflage 1 lautet: *[Stattdessen Positivliste — und
sie existiert bereits. `_is_repo_read_cmd` … **Der Auto-Modus dockt
ausschliesslich daran an.**]*

**Diese Positivliste gibt heute schon `PermissionResultAllow()` zurueck** —
`bot.py:2938`, im Bestand seit dem 24.07.:

```python
# 8.7 [GEAENDERT]: Lesen/Auflisten des Repos ohne Rueckfrage (ls, cat, grep,
# git log/status/diff …) — nur einzelne, verkettungsfreie Lese-Befehle.
if tool_name == "Bash" and _is_repo_read_cmd(str(tool_input.get("command") or "")):
    return PermissionResultAllow()
```

**Ein Auto-Modus, der ausschliesslich daran andockt, spart null Rueckfragen.**
Was die Liste erkennt, geht bereits durch; was sie nicht erkennt, bleibt
dialogpflichtig — mit Schalter wie ohne.

## Wie gross Adams Problem tatsaechlich ist

Aus den Bot-Protokollen der letzten sieben Tage:

| Werkzeug | Freigabe-Anfragen |
|---|---:|
| **Bash** | **352** |
| WebFetch | 65 |
| Write | 36 |
| Edit | 32 |
| Read | 14 |

**Alle 352 Bash-Anfragen sind an der Positivliste vorbeigelaufen** — sonst
waeren sie nicht im Dialog gelandet. Das ist Adams [tausend Mal druecken], und
die vorgeschlagene Bauform beruehrt davon **keinen einzigen Fall**.

## Warum ich hier anhalte statt zu erweitern

Die naheliegende Antwort waere, die Freigabe zu **verbreitern**. Genau das
darf ich nicht allein entscheiden: Es ist die Sicherheitsabwaegung, die dein
Auftrag selbst benennt — *[Solange Adam jeden Befehl sieht, ist er der
Pruefer. Faellt das weg, laeuft ein eingeschleuster Befehl ohne Rueckfrage.]*

Die Wahl steht zwischen zwei Wegen, die **beide** Nachteile haben, und keiner
davon ist meiner:

- **Verbotsliste** (Claudias urspruengliche Auflage 1) — du hast sie mit K5
  verworfen: konstruktiv unvollstaendig, und bei Shell-Befehlen besonders.
- **Breitere Positivliste** — etwa Lesebefehle **ausserhalb** des Repos, oder
  benannte Werkzeuge (`ssh`, `pip`, `systemctl`) je einzeln. Das waere baubar
  und pruefbar, ist aber eine echte Ausweitung der Angriffsflaeche.

## Ein Nebenbefund, der zur Entscheidung gehoert

**Die Protokolle nennen nur den Werkzeugnamen, nicht den Befehl.** Man kann
hinterher nicht sagen, **was** freigegeben wurde. Fuer die Frage [welche
Befehle liessen sich gefahrlos aufnehmen] fehlt damit die Grundlage — und
fuer eine Nachschau nach einem Vorfall ebenfalls.

**Vorschlag:** Bevor der Schalter gebaut wird, eine Woche lang die
**Befehlsart** mitschreiben (erstes Wort, ohne Argumente — kein Geheimnis
kann darin stehen). Dann ist die Positivliste eine **Messung** statt einer
Vermutung. Das ist billig und passt zur Hausregel [woher kommt die Menge].

## Was ich getan habe

Zustand (`bash_auto_bis`) und Freigabezweig waren halb gebaut und sind
**zurueckgerollt** — nach deiner Auflage: *was nicht sauber traegt, wird
zurueckgerollt, nicht durchgedrueckt*. `bot.py` steht auf dem committeten
Stand von `57f78b6` (Freigabedialog, Rang 3a).

**Rang 3a ist fertig und getestet** — die Verstaendlichkeit des Dialogs ist
gebaut. Nur die **Haeufigkeit** (3b) haengt an dieser Entscheidung.
