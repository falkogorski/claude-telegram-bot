#!/bin/bash
# <!-- ROLLE: icloud-backup -->
#
# Zweite Kopie des iCloud-KI-Ordners auf die lokale Platte.
# **Adams Entscheid vom 29.08.2026: ERSETZEN, nicht reparieren.**
#
# ## Warum ersetzt und nicht wiederbelebt
#
# Der Vorgaenger `com.jakuna.mirror-ki` (Mai 2026, App-Huelle + LaunchAgent,
# alle fuenf Minuten) steht seit dem 25.05. auf Rueckgabewert 78 und hat
# seither **keine einzige Protokollzeile** geschrieben. 330 Laeufe, alle
# gescheitert, drei Monate lang unbemerkt.
#
# **Die Ursache ist dieselbe, die auch den neuen Papierweg-Zeitgeber
# scheitern liess, und sie ist nicht reparierbar:** Ein LaunchAgent laeuft
# unter `launchd` und erbt Adams iCloud-Freigabe nicht. Ihn wiederzubeleben
# hiesse, ihn in drei Monaten wieder still sterben zu lassen.
#
# Deshalb derselbe Zuschnitt wie beim Papierweg: **beim Sitzungsstart und auf
# Zuruf, kein Zeitgeber.** Dann laeuft er unter Claude Code — also unter der
# App, fuer die die Freigabe gilt — und braucht **keine neue Berechtigung**.
# Ausdruecklich nicht: iCloud-Zugriff fuer `/bin/bash` (das ist die Shell,
# nicht eine App) und erst recht kein Festplattenvollzugriff.
#
# ## Warum das nicht blosses Aufraeumen ist
#
# **Adams gesamter iCloud-KI-Ordner ist seit dem 25.05. ohne zweite Kopie.**
# iCloud schuetzt nicht vor versehentlichem Loeschen — eine Loeschung wird auf
# alle Geraete gespiegelt. Das ist der eigentliche Grund fuer den Ersatz.
#
# ## Der Unterschied zum Papierweg (`icloud_spiegel.sh`)
#
# | | Papierweg | dieses Backup |
# |---|---|---|
# | Ziel | `docs/auftraege/` (versioniert) | `~/Backups/…` (nicht versioniert) |
# | Umfang | nur `*.md`/`*.pdf`, flach | **alles**, rekursiv |
# | Geheimnis-Bremse | ja (Git!) | **nein** — ein Backup sichert alles |
# | Dublettenschutz | ja | **nein** — Namen sind hier die Ordnung |
# | Takt | jeder Sitzungsstart | **hoechstens einmal taeglich** |
#
# Die Tagesmarke ist kein Sparzwang: Ein rsync ueber den ganzen Ordner bei
# **jedem** Sitzungsstart wuerde den Start spuerbar bremsen — und was bremst,
# wird abgeschaltet.

set -u

# **[NEU 30.08.] HOME wird BENANNT eingefordert** (Faecher-Fund [19], A2).
# Unter `set -u` bricht `$HOME` ohne HOME mit "unbound variable" ab — auch
# innerhalb eines Rueckfalls wie `${VAR:-$HOME/x}`, denn dort wird $HOME
# expandiert, sobald VAR fehlt. Genau daran starb am 29.07. ein Waechter,
# einundzwanzig Tage unbemerkt. Diese Zeile macht daraus einen Abbruch mit
# Grund statt einer Fehlermeldung, die niemand einem fehlenden Zuhause
# zuordnet — und sie sichert alle folgenden $HOME-Stellen auf einmal.
: "${HOME:?HOME ist nicht gesetzt — als Dienst ohne User= gestartet?}"

QUELLE="${ICLOUD_BACKUP_QUELLE:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/KI}"
ZIEL="${ICLOUD_BACKUP_ZIEL:-$HOME/Backups/iCloud-Mirror/KI}"
LOG="${ICLOUD_BACKUP_LOG:-$HOME/.claude/icloud-backup.log}"
MARKE="${ICLOUD_BACKUP_MARKE:-$HOME/.claude/icloud-backup.tag}"

mkdir -p "$(dirname "$LOG")" 2>/dev/null
sag() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

# --- Tagesmarke: hoechstens ein Lauf je Kalendertag, ausser bei --jetzt
if [ "${1:-}" != "--jetzt" ]; then
  heute="$(date '+%Y-%m-%d')"
  [ -f "$MARKE" ] && [ "$(cat "$MARKE" 2>/dev/null)" = "$heute" ] && exit 0
fi

# --- Vorbedingungen. **Ein Fehlschlag ist LAUT** — das ist der ganze
#     Unterschied zum Vorgaenger, der drei Monate schwieg.
if [ ! -d "$QUELLE" ]; then
  sag "FEHLER: Quelle nicht erreichbar — $QUELLE"
  exit 78
fi
if ! ls "$QUELLE" >/dev/null 2>&1; then
  sag "FEHLER: Quelle vorhanden, aber nicht lesbar (TCC?) — $QUELLE"
  sag "        Bei einem Hintergrund-Job ist das die uebliche Ursache; dieses"
  sag "        Skript gehoert deshalb an den Sitzungsstart, nicht an launchd."
  exit 78
fi
mkdir -p "$ZIEL" 2>/dev/null || { sag "FEHLER: Ziel nicht anlegbar — $ZIEL"; exit 78; }

# --- Der Abgleich. **Kein `--delete`** (Adams Auflage): Was in iCloud
#     verschwindet, bleibt hier liegen. Eine Datei zu viel ist harmlos, eine
#     fehlende nicht — und das versehentliche Loeschen ist genau der Fall,
#     gegen den diese Kopie ueberhaupt existiert.
ausgabe="$(rsync -a --stats \
    --exclude '.DS_Store' --exclude '._*' \
    "$QUELLE/" "$ZIEL/" 2>&1)"
rc=$?

if [ $rc -ne 0 ]; then
  sag "FEHLER: rsync endete mit $rc"
  printf '%s\n' "$ausgabe" | tail -5 | while IFS= read -r z; do sag "  $z"; done
  exit $rc
fi

dateien="$(printf '%s' "$ausgabe" | grep -m1 'Number of files:' | tr -d ' ' | cut -d: -f2)"
neu="$(printf '%s' "$ausgabe" | grep -m1 'files transferred:' | tr -d ' ' | cut -d: -f2)"
sag "Lauf beendet: ${dateien:-?} Dateien im Bestand, ${neu:-0} neu oder geaendert."
date '+%Y-%m-%d' > "$MARKE" 2>/dev/null
exit 0
