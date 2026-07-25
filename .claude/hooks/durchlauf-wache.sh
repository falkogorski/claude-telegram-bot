#!/usr/bin/env bash
# <!-- ROLLE: durchlauf-wache -->
# ============================================================================
# Stop-Hook: verhindert, dass die Sitzung anhält, während noch Arbeit offen ist.
#
# WARUM ES DIESEN HOOK GIBT (Adam, 25.07.2026, dritte Erinnerung):
# Die Regel „Durchlauf ist der Normalfall — ein Weitergabe-Block ist ein
# Meilenstein, kein Halteschild" stand in CLAUDE.md. Sie hat trotzdem dreimal
# nicht gegriffen, und zwar aus einem strukturellen Grund: CLAUDE.md wird beim
# SITZUNGSSTART gelesen, der Fehler passiert aber am ZUGENDE. Dort feuert kein
# Dokument.
#
# Das ist exakt dasselbe Muster, das dieses Projekt heute viermal diagnostiziert
# hat — Register-Pflicht ohne Prüfer, Vorlage ohne Gültigkeitsvermerk, Audit-Tor
# ohne Einholung, Filter ohne Wirkungsprüfung. Eine Regel ohne Prüfer ist eine
# Bitte. Also der Prüfer statt einer vierten Ermahnung.
#
# SO ARBEITET ER:
#   * Gelesen wird `.claude/laufplan.md` — die offene Reihe der Sitzung.
#   * Steht dort noch ein unerledigter Punkt (`- [ ]`) und ist die Sitzung nicht
#     ausdrücklich auf Warten gestellt, wird das Anhalten BLOCKIERT.
#   * Die Blockade nennt die offenen Punkte, damit sofort klar ist, was folgt.
#
# DIE NOTBREMSE (bewusst eingebaut):
# Ein Wächter, der nie durchlässt, ist ein Ausfall, kein Schutz. Deshalb:
#   * `WARTET: ja` in der ersten Zeile hält ihn an — für Fälle, in denen wirklich
#     nur Adams Zug weiterhilft.
#   * Nach ZWEI Blockaden in Folge lässt er durch. Wenn zweimaliges Erinnern
#     nichts bewirkt, liegt das Hindernis woanders, und Festhalten macht es
#     schlimmer.
# ============================================================================
set -uo pipefail

PLAN="${CLAUDE_PROJECT_DIR:-.}/.claude/laufplan.md"
ZAEHLER="${CLAUDE_PROJECT_DIR:-.}/.claude/.durchlauf-blockaden"

# Kein Plan = keine Aussage. Der Wächter erfindet keine Arbeit.
[ -f "$PLAN" ] || exit 0

# Ausdrücklich auf Warten gestellt?
if head -3 "$PLAN" | grep -qi '^WARTET:[[:space:]]*ja'; then
  rm -f "$ZAEHLER"
  exit 0
fi

OFFEN="$(grep -n '^[[:space:]]*-[[:space:]]*\[[[:space:]]\]' "$PLAN" 2>/dev/null | head -8)"
if [ -z "$OFFEN" ]; then
  rm -f "$ZAEHLER"
  exit 0
fi

# Notbremse: nach zwei Blockaden in Folge durchlassen.
N=0
[ -f "$ZAEHLER" ] && N="$(cat "$ZAEHLER" 2>/dev/null || echo 0)"
case "$N" in ''|*[!0-9]*) N=0 ;; esac
if [ "$N" -ge 2 ]; then
  rm -f "$ZAEHLER"
  exit 0
fi
echo $((N + 1)) > "$ZAEHLER"

ANZAHL="$(grep -c '^[[:space:]]*-[[:space:]]*\[[[:space:]]\]' "$PLAN" 2>/dev/null || echo 0)"

{
  echo "DURCHLAUF-WACHE: Es sind noch ${ANZAHL} Punkte offen — nicht anhalten."
  echo ""
  echo "Offen laut .claude/laufplan.md:"
  echo "$OFFEN" | sed 's/^[0-9]*:/  /'
  echo ""
  echo "Arbeite den naechsten Punkt ab. Ein Weitergabe-Block ist ein Meilenstein,"
  echo "kein Halteschild — schreib ihn und mach weiter."
  echo ""
  echo "Wenn wirklich nur Adams Zug weiterhilft: erste Zeile des Laufplans auf"
  echo "'WARTET: ja' setzen und den Grund dazuschreiben. Erledigtes abhaken (- [x])."
} >&2
exit 2
