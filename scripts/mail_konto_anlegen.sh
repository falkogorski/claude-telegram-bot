#!/usr/bin/env bash
# <!-- ROLLE: mail-konto-helfer -->
# ============================================================================
# Legt ein E-Mail-Konto in der geschuetzten Umgebung an (Punkt 9.5).
#
# WARUM ES DIESES SKRIPT GIBT statt eines Befehlsblocks zum Kopieren:
# Ein Block mit mehreren `read`-Zeilen funktioniert beim Einfuegen NICHT — die
# Shell liest dann die naechste eingefuegte Zeile als Antwort, statt auf die
# Tastatur zu warten. Das Kennwort wuerde nie abgefragt, und in der Datei
# stuende Unsinn. Adam hat genau das am 21.08. erfragt, bevor er es ausfuehrte.
# Bei vier Konten waeren vier lange Einzeiler zumutbar-grenzwertig; ein
# gefuehrter Helfer ist der ehrlichere Weg.
#
# WAS ES NICHT TUT: Es prueft die Zugangsdaten nicht. Ein Konto, das hier
# angelegt wird, kann trotzdem falsch sein — der Bot sagt das dann beim ersten
# Abruf. Absichtlich so: Ein Verbindungstest an dieser Stelle braeuchte das
# Kennwort im Klartext in einem weiteren Prozess.
#
# Aufruf als root auf dem Server:
#   bash /home/claudebot/claude-telegram-bot/scripts/mail_konto_anlegen.sh
# ============================================================================
set -euo pipefail

ENVDATEI=/etc/claude-telegram-bot.env

if [ "$(id -u)" -ne 0 ]; then
  echo "Bitte als root ausfuehren (ssh claudevps)." >&2
  exit 1
fi

echo "E-Mail-Konto anlegen"
echo "===================="
echo
echo "Welcher Anbieter?"
echo "  1) mailbox.org   (geschaeftlich)"
echo "  2) Posteo         (privat)"
echo "  3) iCloud / me.com"
echo "  4) web.de"
echo "  5) Gmail"
echo "  6) anderer (Server von Hand eingeben)"
read -rp "Zahl: " WAHL < /dev/tty

case "$WAHL" in
  1) VORNAME=mailbox; IMAP=imap.mailbox.org; SMTP=smtp.mailbox.org
     HINWEIS="mailbox.org: Das normale Kennwort funktioniert. Sicherer ist ein
     eigenes App-Passwort in den Kontoeinstellungen." ;;
  2) VORNAME=posteo;  IMAP=posteo.de;          SMTP=posteo.de
     HINWEIS="Posteo: Das normale Kennwort funktioniert. Ist bei dir die
     Zwei-Faktor-Anmeldung aktiv, wird stattdessen das dafuer vorgesehene
     Kennwort gebraucht." ;;
  3) VORNAME=icloud;  IMAP=imap.mail.me.com; SMTP=smtp.mail.me.com
     HINWEIS="iCloud verlangt ein ANWENDUNGSSPEZIFISCHES Kennwort
     (appleid.apple.com). Das normale Apple-Kennwort wird abgewiesen." ;;
  4) VORNAME=webde;   IMAP=imap.web.de;      SMTP=smtp.web.de
     HINWEIS="web.de: IMAP muss im Postfach unter Einstellungen erst
     FREIGESCHALTET werden, sonst schlaegt die Anmeldung fehl. Ob das im
     kostenlosen Tarif geht, ist hier NICHT geprueft — bitte im Postfach
     nachsehen." ;;
  5) VORNAME=gmail;   IMAP=imap.gmail.com;   SMTP=smtp.gmail.com
     HINWEIS="Gmail verlangt ein APP-PASSWORT und dafuer aktive
     Zwei-Faktor-Anmeldung; zusaetzlich muss IMAP in den Gmail-Einstellungen
     eingeschaltet sein. Das normale Google-Kennwort wird abgewiesen." ;;
  6) VORNAME=""; IMAP=""; SMTP=""; HINWEIS="" ;;
  *) echo "Ungueltige Auswahl." >&2; exit 1 ;;
esac

[ -n "$HINWEIS" ] && { echo; echo "Hinweis: $HINWEIS"; echo; }

read -rp "Kurzname fuers Kommando (klein, ohne Leerzeichen) [${VORNAME}]: " NAME < /dev/tty
NAME="${NAME:-$VORNAME}"
NAME="$(echo "$NAME" | tr '[:lower:]' '[:upper:]' | tr -cd 'A-Z0-9')"
[ -n "$NAME" ] || { echo "Kurzname fehlt." >&2; exit 1; }

if grep -q "^MAIL_${NAME}_ADRESSE=" "$ENVDATEI" 2>/dev/null; then
  echo "Ein Konto mit dem Kurznamen ${NAME} ist bereits hinterlegt." >&2
  echo "Doppelte Zeilen ueberschreiben sich still — bitte erst pruefen." >&2
  exit 1
fi

read -rp "E-Mail-Adresse: " ADRESSE < /dev/tty
read -rp "Benutzername fuer die Anmeldung [${ADRESSE}]: " BENUTZER < /dev/tty
BENUTZER="${BENUTZER:-$ADRESSE}"
if [ -z "$IMAP" ]; then
  read -rp "IMAP-Server (z. B. imap.anbieter.de): " IMAP < /dev/tty
  read -rp "SMTP-Server (z. B. smtp.anbieter.de): " SMTP < /dev/tty
fi
# Das Kennwort wird GETIPPT, nie eingefuegt: `read -s` zeigt nichts an, und
# weil der Wert nur in einer Variablen lebt, landet er weder in der
# Shell-Historie noch in einem Protokoll.
read -rsp "Kennwort (bleibt unsichtbar): " KENNWORT < /dev/tty
echo
read -rp "Weitere Adressen desselben Postfachs, mit Komma (optional): " ALIASSE < /dev/tty

{
  printf 'MAIL_%s_ADRESSE=%s\n'  "$NAME" "$ADRESSE"
  printf 'MAIL_%s_BENUTZER=%s\n' "$NAME" "$BENUTZER"
  printf 'MAIL_%s_KENNWORT=%s\n' "$NAME" "$KENNWORT"
  printf 'MAIL_%s_IMAP=%s\n'     "$NAME" "$IMAP"
  printf 'MAIL_%s_SMTP=%s\n'     "$NAME" "$SMTP"
  [ -n "$ALIASSE" ] && printf 'MAIL_%s_ALIASSE=%s\n' "$NAME" "$ALIASSE"
} >> "$ENVDATEI"

unset KENNWORT
chmod 600 "$ENVDATEI"

echo
echo "Konto '${NAME}' hinterlegt."
echo "Noch NICHT aktiv — der Dienst laedt die Umgebung erst beim Neustart."
echo "Wenn alle Konten angelegt sind:"
echo
echo "    systemctl restart claude-telegram-bot"
echo
echo "Danach im Bot /mail tippen: dort muessen die Konten auftauchen."
