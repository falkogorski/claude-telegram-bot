#!/bin/bash
# <!-- ROLLE: icloud-spiegel -->
#
# Spiegelt Adams Ausarbeitungen aus iCloud in den Auftrags-Eingang des Repos.
# **Adams Auftrag vom 29.08.2026** (Weg 3), nachdem das Kopieren über den Chat
# zweimal an einem Tag Arbeit aufgehalten hat.
#
# GRUNDSATZ: kopieren, nie loeschen. Kein --delete, keine Ruecksynchronisation.
# Was Adam in iCloud loescht, bleibt hier liegen — eine Datei zu viel ist
# harmlos, eine fehlende nicht.
#
# WARUM DIESES SKRIPT LAUT SCHEITERT (und der Vorgaenger es nicht tat):
# Auf diesem Mac laeuft seit Mai ein zweiter Spiegel, `com.jakuna.mirror-ki`.
# Er startet alle fuenf Minuten, steht auf Exit-Status 78 und hat seit dem
# 25.05. keine Zeile mehr protokolliert — **drei Monate stiller Ausfall bei
# laufendem Zeitgeber.** Genau die Fehlerform, die dieses Projekt schon
# einundzwanzig Tage lang beim Tagescheck erlebt hat: Der Ausfall SIEHT AUS
# WIE RUHE.
#
# Deshalb schreibt dieses Skript **bei jedem Lauf** eine Zeile — auch wenn es
# nichts zu tun gab und erst recht, wenn es scheitert. Eine Logdatei, die
# nicht mehr waechst, ist damit selbst das Alarmzeichen, und der Tagescheck
# kann ihr Alter messen.
#
# TCC (macOS-Datenschutz): Ein LaunchAgent laeuft unter `launchd`, NICHT unter
# Claude.app. Die Freigabe, die Adam fuer die Claude-Eintraege gesetzt hat,
# gilt hier NICHT — dieser Job braucht seine eigene. Scheitert der Zugriff,
# steht das als Klartextzeile im Protokoll statt als leerer Lauf.

set -u

QUELLE="${ICLOUD_SPIEGEL_QUELLE:-$HOME/Library/Mobile Documents/com~apple~CloudDocs/KI/Telegram-Bot}"
ZIEL="${ICLOUD_SPIEGEL_ZIEL:-$HOME/Projects/claude-telegram-bot/docs/auftraege}"
LOG="${ICLOUD_SPIEGEL_LOG:-$HOME/.claude/icloud-spiegel.log}"

mkdir -p "$(dirname "$LOG")" 2>/dev/null

sag() { printf '[%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S')" "$*" >> "$LOG"; }

# ---------------------------------------------------------------- Vorbedingungen
if [ ! -d "$QUELLE" ]; then
  sag "FEHLER: Quelle nicht erreichbar — $QUELLE"
  sag "        Bei einem Hintergrund-Job ist die haeufigste Ursache die"
  sag "        fehlende iCloud-Freigabe fuer launchd, nicht ein falscher Pfad."
  exit 78
fi

# Der Lesetest ist der eigentliche TCC-Test: Ein gesperrter Ordner laesst sich
# oft auflisten, aber nicht lesen. `ls` allein haette das durchgehen lassen.
if ! ls "$QUELLE" >/dev/null 2>&1; then
  sag "FEHLER: Quelle vorhanden, aber nicht lesbar (TCC?) — $QUELLE"
  exit 78
fi

mkdir -p "$ZIEL" 2>/dev/null || { sag "FEHLER: Ziel nicht anlegbar — $ZIEL"; exit 78; }

# ---------------------------------------------------------------- Geheimnis-Bremse
#
# **Nicht bestellt, aber notwendig, und deshalb hier benannt statt versteckt.**
# Der Zielordner ist versioniert und wird nach GitHub gespiegelt. Bisher hat
# Adam jede Datei von Hand kopiert und dabei gesehen, was er kopiert. Ein
# selbsttaetiger Spiegel nimmt genau diesen Blick heraus.
#
# Die Bremse ist bewusst ENG: Sie sucht Zugangsdaten in ihrer typischen Form
# (Schluessel-Zuweisung, Token-Praefixe, privater Schluesselkopf), nicht
# irgendein Wort. Eine breite Wortliste haette staendig blockiert und waere
# binnen einer Woche abgeschaltet worden.
#
# Sie ist **kein Tor, sondern eine Bremse** — eine Textsuche findet nicht
# jede Form. Der eigentliche Schutz bleibt, dass Geheimnisse dort nichts zu
# suchen haben (siehe README des Auftragsordners).
#
# **NACHGESCHAERFT beim ersten Probelauf, und der Probelauf war der Grund.**
# Die erste Fassung suchte nur das Praefix `sk-ant-`. Sie hat 2 von 62 Dateien
# gebremst — beide FEHLALARME, und ausgerechnet die beiden inhaltlich
# wichtigsten: den Entkernungskatalog (meine eigene Arbeitsgrundlage) und den
# Modell-Strategiebericht. Beide schreiben ueber Zugangsdaten und enthalten
# deshalb Beispielwerte wie `sk-ant-echt123`.
#
# Das ist die vorhersehbare Falle dieses Projekts: **Wir dokumentieren
# staendig ueber Geheimnisse.** Eine Bremse am Praefix blockiert genau die
# Dokumentation und nicht das Geheimnis.
#
# Das trennscharfe Merkmal ist nicht das Praefix, sondern die **Laenge des
# Restes**: Ein besprochener Schluessel ist kurz, ein echter hat dutzende
# Zeichen. Deshalb ueberall eine Mindestlaenge — und bei der allgemeinen
# Zuweisung zusaetzlich der Ausschluss offensichtlicher Platzhalter.
GEHEIM_MUSTER='(sk-ant-[A-Za-z0-9_-]{30,}|ghp_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|xox[baprs]-[A-Za-z0-9-]{20,}|BEGIN [A-Z ]*PRIVATE KEY|AKIA[0-9A-Z]{16}|(TOKEN|SECRET|PASSWORD|PASSWORT|API_KEY)[[:space:]]*[:=][[:space:]]*[A-Za-z0-9/+_-]{24,})'

uebertragen=0
gebremst=0
geprueft=0

# Nur *.md und *.pdf, wie beauftragt. Keine Rekursion in Unterordner: Der
# Quellordner ist flach, und eine Rekursion wuerde bei einem versehentlich
# dort abgelegten Projektordner unbemerkt sehr viel mitnehmen.
while IFS= read -r datei; do
  [ -e "$datei" ] || continue
  geprueft=$((geprueft + 1))
  name="$(basename "$datei")"
  zieldatei="$ZIEL/$name"

  # Nur Neueres ueberschreiben. `-nt` ist falsch herum sicher: Bei gleichem
  # Zeitstempel geschieht nichts, und das ist der haeufige Fall.
  if [ -e "$zieldatei" ] && [ ! "$datei" -nt "$zieldatei" ]; then
    continue
  fi

  # Die Bremse greift nur bei Textdateien; ein PDF ist binaer und wuerde
  # zufaellige Treffer erzeugen.
  if [ "${name##*.}" = "md" ] && grep -aElq "$GEHEIM_MUSTER" "$datei" 2>/dev/null; then
    sag "GEBREMST: $name traegt ein Zugangsdaten-Muster — NICHT kopiert."
    sag "          Wenn das ein Fehlalarm ist, die Datei von Hand kopieren."
    gebremst=$((gebremst + 1))
    continue
  fi

  if cp -p "$datei" "$zieldatei" 2>/dev/null; then
    sag "kopiert: $name"
    uebertragen=$((uebertragen + 1))
  else
    sag "FEHLER: konnte nicht kopieren — $name"
  fi
done < <(find "$QUELLE" -maxdepth 1 -type f \( -name '*.md' -o -name '*.pdf' \) 2>/dev/null)

sag "Lauf beendet: $geprueft geprueft, $uebertragen uebertragen, $gebremst gebremst."
exit 0
