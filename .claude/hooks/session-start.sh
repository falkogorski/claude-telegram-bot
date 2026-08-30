#!/usr/bin/env bash
# SessionStart-Hook (Führungs-Register, siehe CLAUDE.md):
# Banner + unübersehbare Warnung, wenn die Arbeitskopie hinter dem Master
# liegt oder unkommittete Änderungen an den Master-Dateien vorliegen.
set -uo pipefail

# **[NEU 30.08.] HOME wird BENANNT eingefordert** (Faecher-Fund [19], A2).
# Unter `set -u` bricht `$HOME` ohne HOME mit "unbound variable" ab — auch
# innerhalb eines Rueckfalls wie `${VAR:-$HOME/x}`, denn dort wird $HOME
# expandiert, sobald VAR fehlt. Genau daran starb am 29.07. ein Waechter,
# einundzwanzig Tage unbemerkt. Diese Zeile macht daraus einen Abbruch mit
# Grund statt einer Fehlermeldung, die niemand einem fehlenden Zuhause
# zuordnet — und sie sichert alle folgenden $HOME-Stellen auf einmal.
: "${HOME:?HOME ist nicht gesetzt — als Dienst ohne User= gestartet?}"
cd "${CLAUDE_PROJECT_DIR:-.}" 2>/dev/null || exit 0

echo "🧭 Master-Branch: mac-produktivstand · Führende Sitzung: Migrations-Sitzung (siehe CLAUDE.md → Führungs-Register)"
echo "   Alle anderen Sitzungen: NUR LESEN — Änderungswünsche als Text an Adam/Migrations-Sitzung."

# --- Papierweg: die Ausarbeitungen aus iCloud holen (Adams Entscheid 29.08.) --
#
# **Hier statt in einem Zeitgeber, und das ist der ganze Kniff.** Der Versuch
# mit einem LaunchAgent ist gemessen gescheitert: Er läuft unter `launchd`,
# erbt Adams iCloud-Freigabe nicht und meldete alle fünf Minuten
# [nicht lesbar (TCC?)]. Ein Job, der ständig scheitert, wird nicht
# beobachtet, sondern abgeschaltet.
#
# Dieser Hook dagegen läuft **unter Claude Code**, also unter der App, für die
# die Freigabe gesetzt ist. **Keine einzige neue Berechtigung** — insbesondere
# kein iCloud-Zugriff für `/bin/bash`, was jedem Skript auf diesem Rechner die
# Tür geöffnet hätte.
#
# Der Preis, den Adam ausdrücklich als keinen bezeichnet hat: Er läuft nur,
# wenn gearbeitet wird. Genau dann werden die Papiere gebraucht.
if [ -d "$HOME/Library/Mobile Documents/com~apple~CloudDocs/KI/Telegram-Bot" ]; then
  _sp=$(bash "${CLAUDE_PROJECT_DIR:-.}/scripts/mac/icloud_spiegel.sh" 2>/dev/null; \
        tail -1 "$HOME/.claude/icloud-spiegel.log" 2>/dev/null)
  case "$_sp" in
    *"0 uebertragen"*) : ;;                      # nichts Neues — still bleiben
    *FEHLER*|*GEBREMST*) echo "📥 Papierweg: ${_sp#*] }" ;;
    *) [ -n "$_sp" ] && echo "📥 Papierweg: ${_sp#*] }" ;;
  esac
fi

# --- Zweite Kopie des KI-Ordners (Ersatz für den toten Mai-Spiegel) --------
#
# Höchstens ein Lauf je Kalendertag — die Marke sitzt im Skript. Ein rsync
# über den ganzen Ordner bei jedem Sitzungsstart würde spürbar bremsen, und
# was bremst, wird abgeschaltet.
#
# Beim ersten Lauf am 29.08.: **221 von 368 Dateien waren seit dem 25. Mai
# ungesichert.** iCloud allein schützt nicht vor versehentlichem Löschen —
# die Löschung wird auf alle Geräte gespiegelt.
if [ -d "$HOME/Library/Mobile Documents/com~apple~CloudDocs/KI" ]; then
  bash "${CLAUDE_PROJECT_DIR:-.}/scripts/mac/icloud_backup.sh" 2>/dev/null
  _bk=$(tail -1 "$HOME/.claude/icloud-backup.log" 2>/dev/null)
  case "$_bk" in
    *FEHLER*) echo "🗄️ Zweitkopie: ${_bk#*] }" ;;
  esac
fi

git fetch origin --quiet 2>/dev/null || { echo "   (offline — Remote-Abgleich übersprungen)"; exit 0; }

BEHIND=$(git rev-list HEAD..origin/mac-produktivstand --count 2>/dev/null || echo 0)
if [ "${BEHIND:-0}" -gt 0 ]; then
  echo ""
  echo "🚨🚨🚨 WARNUNG: Diese Arbeitskopie ist ${BEHIND} Commit(s) HINTER origin/mac-produktivstand! 🚨🚨🚨"
  echo "🚨 ERST 'git pull origin mac-produktivstand', BEVOR irgendetwas geschrieben wird."
fi

DIRTY=$(git status --porcelain -- MIGRATION.md CLAUDE.md 2>/dev/null)
if [ -n "$DIRTY" ]; then
  echo ""
  echo "🚨 WARNUNG: Unkommittete Änderungen an Master-Dateien (MIGRATION.md/CLAUDE.md):"
  echo "$DIRTY"
  echo "🚨 Vor weiterer Arbeit klären: committen (nur führende Sitzung!) oder verwerfen."
fi
exit 0
