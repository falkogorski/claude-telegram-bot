<!-- ROLLE: befund-gleichstand-messung -->
# Die Hälfte, die kein Repo-Scan sehen kann: 18 Fassungsunterschiede

**Stichtag:** 29.08.2026, 17:0x · **überholt durch:** — · **maßgeblich ist diese Datei**
**Von:** Mick · **Ergänzt:** Engywucks `BEFUND-maschinen-gleichstand.md`

Er schreibt: *„Der Fächer liest das Repo. Er sieht nicht, was auf Mac und VPS
tatsächlich installiert ist … **Genau dort sitzt aber die Hälfte von Adams
Anliegen.**"* Das ist jetzt gemessen — beide `pip freeze` verglichen.

## Das Ergebnis

**79 Pakete auf beiden Maschinen, keines fehlt hier oder dort — aber 18
tragen verschiedene Fassungen.**

| Paket | Mac | VPS |
|---|---|---|
| `anthropic` | 0.109.1 | **0.120.0** |
| `cryptography` | 48.0.0 | **49.0.0** |
| `mcp` | 1.27.1 | **1.28.1** |
| `python-telegram-bot` | 22.7 | **22.8** |
| `starlette` | 1.1.0 | **1.3.1** |
| `uvicorn` | 0.47.0 | **0.51.0** |
| `rpds-py` | 0.30.0 | **2026.6.3** |
| `anyio` · `certifi` · `cffi` · `idna` · `jiter` · `aiohappyeyeballs` · `pydantic-settings` · `python-multipart` · `sse-starlette` · `typing_extensions` | jeweils älter | jeweils neuer |
| **`pymupdf`** | **1.28.2** | ~~1.28.0~~ → **behoben, siehe unten** |

## Der eine, der akut war — und die Lehre daraus

**`pymupdf` stand auf dem VPS auf 1.28.0, während die Anforderungsliste seit
heute Nacht `>=1.28.2` verlangt.**

**Der Grund ist strukturell und betrifft jedes künftige Update:** `git pull`
bringt den Code, **nicht die Pakete.** Der Pin im Repo ist eine Absichts-
erklärung; installiert wird erst, wenn jemand `pip install -r
requirements.txt` fährt. Zwischen Anspruch und Wirklichkeit lag also eine
Lücke, die **kein Prüfer bemerkt hätte** — der Regressionslauf war auf beiden
Maschinen grün, weil 1.28.0 für unsere Zwecke genügt.

Nachgezogen und **ausgeführt geprüft**, nicht angenommen: PDF auf dem VPS
erzeugt, wieder ausgelesen, Umlaute erhalten. Bot läuft weiter.

## Was das für Adams Regel bedeutet

Seine Regel lautet *„Alle Maschinen müssen immer konsequent auf demselben
Stand sein."* **Engywucks Präzisierung trifft es:** Gleichstand ist die harte
Regel, Aktualität das Ziel mit Prüfschritt davor — *welche* Fassung gilt,
entscheidet der Pin, nicht der Kalender.

Die 17 übrigen Unterschiede sind **Mitzieher**: Pakete, die niemand direkt
anfordert, sondern die als Abhängigkeit hereinkommen. Sie anzugleichen ist
eine Entscheidung, keine Reparatur — und sie hat zwei Seiten:

**Dafür:** Ein Prüflauf auf dem Mac sagt derzeit nichts sicher über den VPS.
Genau diese Divergenz hat in der Nacht zum 25.08. schon einmal einen Prüfer
blind gemacht.

**Dagegen:** Ein `pip install --upgrade` über 79 Pakete auf dem Produktiv-
system ist ein Fundament-Eingriff. Er gehört in einen Klon, mit Regressions-
lauf, mit Rückweg — nicht nebenbei.

**Mein Vorschlag:** Beim nächsten Wartungsfenster **einen** Weg gehen — die
Mac-venv aus der VPS-Fassung nachziehen, nicht umgekehrt. Der VPS trägt den
Betrieb; der Mac soll ihm folgen, nicht er dem Mac. Das ist der risikoärmere
Weg und macht Prüfläufe hier wieder aussagekräftig.

**Zu entscheiden von Adam.** Bis dahin gilt: Was auf einer Maschine gemessen
wurde, gilt auf der anderen nicht — dritter Fall dieser Klasse in fünf Tagen.

## Was weiterhin ungemessen ist

Node, npm-Pakete und Systempakete sind **nicht** verglichen — der Mac hat
Homebrew-Node und arm64, der VPS nodesource und amd64. Ein Vergleich wäre
dort wenig aussagekräftig; die Claude-CLI ist ohnehin eine eigenständige
Binärdatei ohne Node-Bindung (siehe `ZETTEL-node-22-auf-24.md`).
