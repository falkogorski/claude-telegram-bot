#!/usr/bin/env python3
"""Die Anhang-Erkennung zerlegt die Struktur — sie durchsucht sie nicht.

**Engywucks Rang 2 der Erkennungsseite, Punkt 1.** Die alte Fassung suchte mit
einem regulaeren Ausdruck nach je zwei Zeichenketten in Anfuehrungszeichen.
In einer BODYSTRUCTURE stehen dutzende solcher Paare, die keine MIME-Typen
sind — Parameter, Dateinamen, Begrenzer.

**Selbst nachgemessen, alle drei Faelle seines Befunds bestaetigt:**

    einfache Textmail                      -> [1 Anhang (unbekannt)]
    Text + eine PDF                        -> [5 Anhaenge]
    charset=utf-8; image=x; audio=y; …     -> [4 Anhaenge] OHNE JEDEN ANHANG

**Der letzte Fall ist der schwere:** Die Parameter im Content-Type schreibt der
ABSENDER. Damit stammte die Wortwahl in Adams Uebersicht doch von ihm — und die
Zusage aus Engywucks Punkt ④ vom 23.08. war in der Umsetzung gekippt.

Gemessen wird hier **ausgefuehrt**, gegen Strukturen nach RFC 3501 §7.4.2 —
kein Blick in den Quelltext.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import email_kanal as ek                                       # noqa: E402

fehler: list[str] = []
n = 0


def zeile(name: str, bedingung, *, gemessen: str = "") -> None:
    global n
    n += 1
    if bedingung:
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}" + (f" — {gemessen}" if gemessen else ""))
        fehler.append(name)


TEXT = '("text" "plain" ("charset" "utf-8") nil nil "7bit" 234 12 nil nil nil nil)'
PDF = ('("application" "pdf" ("name" "rechnung.pdf") nil nil "base64" 9000 nil '
       '("attachment" ("filename" "rechnung.pdf")) nil nil)')
HTML = '("text" "html" ("charset" "utf-8") nil nil "7bit" 300 9 nil nil nil nil)'


def arten(bs: str) -> list[str]:
    return ek.arten_aus_bodystructure(bs)


print("== Anhang-Erkennung: die drei Faelle aus dem Befund ==")

zeile("einfache Textmail hat KEINEN Anhang", arten(TEXT) == [],
      gemessen=str(arten(TEXT)))

eine_pdf = f'({TEXT}{PDF} "mixed" ("boundary" "x") nil nil nil)'
zeile("Text + eine PDF ergibt GENAU EINEN Anhang",
      arten(eine_pdf) == ["PDF"], gemessen=str(arten(eine_pdf)))

# **Der schwerste Fall: der Absender schreibt die Parameter.**
koeder = ('("text" "plain" ("charset" "utf-8" "image" "x" "audio" "y" '
          '"video" "z") nil nil "7bit" 234 12 nil nil nil nil)')
zeile("Absender-Parameter erzeugen KEINEN Anhang", arten(koeder) == [],
      gemessen=str(arten(koeder)))
zeile("…und auch keine Wortwahl in Adams Uebersicht",
      not any(w in str(arten(koeder)) for w in ("Bild", "Audio", "Video")),
      gemessen=str(arten(koeder)))

print("-- und die Faelle, die der Zerleger richtig treffen muss --")
alternative = f'({TEXT}{HTML} "alternative" ("boundary" "y") nil nil nil)'
zeile("HTML-Alternative ist kein Anhang", arten(alternative) == [],
      gemessen=str(arten(alternative)))

bild = ('("image" "jpeg" ("name" "foto.jpg") nil nil "base64" 40000 nil '
        '("attachment" ("filename" "foto.jpg")) nil nil)')
zwei = f'({TEXT}{bild}{PDF} "mixed" ("boundary" "z") nil nil nil)'
zeile("Bild + PDF ergibt genau zwei", arten(zwei) == ["Bild", "PDF"],
      gemessen=str(arten(zwei)))

txt_anhang = ('("text" "plain" ("name" "notiz.txt") nil nil "7bit" 50 2 '
              '("attachment" ("filename" "notiz.txt")) nil nil)')
mit_txt = f'({TEXT}{txt_anhang} "mixed" ("boundary" "q") nil nil nil)'
zeile("eine angehaengte .txt zaehlt trotz Typ text/plain",
      arten(mit_txt) == ["Text"], gemessen=str(arten(mit_txt)))

verschachtelt = (f'(({TEXT}{HTML} "alternative" ("boundary" "in") nil nil nil)'
                 f'{PDF} "mixed" ("boundary" "out") nil nil nil)')
zeile("verschachtelt: alternative in mixed, dazu eine PDF",
      arten(verschachtelt) == ["PDF"], gemessen=str(arten(verschachtelt)))

print("-- fail-quiet: was sich nicht lesen laesst, sagt nichts --")
#
# **Die Gegenprobe hat gezeigt, dass die vier Zeilen darunter zu schwach
# sind.** Sie pruefen Eingaben, die auch OHNE die Balance-Pruefung leer
# bleiben — man kann `return stapel[0] if len(stapel) == 1 else []` zu
# `return stapel[0]` entkernen, und sie bleiben gruen.
#
# Der Fall, der wirklich unterscheidet, braucht **einen unvollstaendigen
# Ausdruck, dessen Teilbaum eine Aussage ergaebe**: eine abgeschnittene
# Antwort, in der eine PDF schon dasteht. Ohne die Pruefung meldete der
# Zerleger dann [1 Anhang] — **eine Behauptung aus einer halben Antwort.**
abgeschnitten = f'({TEXT}{PDF}'          # schliessende Klammer fehlt
zeile("abgeschnittene Antwort mit erkennbarem Teil sagt NICHTS",
      arten(abgeschnitten) == [],
      gemessen=f"{arten(abgeschnitten)} — eine Behauptung aus einer halben Antwort")

for kaputt, was in [
    ('("text" "plain" (((((', "unbalancierte Klammern"),
    ("", "leer"),
    ("völliger unsinn ohne klammern", "kein Ausdruck"),
    (')(', "verdrehte Klammern"),
]:
    zeile(f"[{was}] ergibt keine Behauptung", arten(kaputt) == [],
          gemessen=str(arten(kaputt)))

print("-- der Zerleger selbst --")
zeile("nil wird zu None", ek._lese_sexp('("a" nil "b")') == [["a", None, "b"]])
zeile("Zahlen bleiben stehen", ek._lese_sexp('("a" 234)') == [["a", "234"]])
zeile("Verschachtelung bleibt erhalten",
      ek._lese_sexp('(("a")("b"))') == [[["a"], ["b"]]])

# ---------------------------------------------------------------- Punkt 5
print()
print("== Rang 2, Punkt 5: eine Menge fuer beide Leser ==")
import mailtext as mt                                          # noqa: E402

# **U+202E ist der Kern der Bedrohung, nicht ein Randfall.** RIGHT-TO-LEFT
# OVERRIDE kehrt die Darstellungsrichtung um: Ein Betreff zeigt in Adams
# Anzeige etwas anderes, als in den Daten steht — ausgerechnet an der Stelle,
# die den Absender ausweist.
BIDI = {
    "U+202A LRE": "‪", "U+202B RLE": "‫", "U+202C PDF": "‬",
    "U+202D LRO": "‭", "U+202E RLO": "‮",
    "U+2066 LRI": "⁦", "U+2067 RLI": "⁧",
    "U+2068 FSI": "⁨", "U+2069 PDI": "⁩",
}
for name, z in BIDI.items():
    zeile(f"{name} wird in Kopfzeilen gefangen",
          bool(ek._STEUERZEICHEN.search(z)))
    zeile(f"{name} wird im Nachrichtentext gefangen",
          bool(mt._UNSICHTBARE_ZEICHEN.search(z)))

# Der gemessene Widerspruch zwischen den beiden Listen.
zeile("U+00AD faengt jetzt auf BEIDEN Seiten",
      bool(ek._STEUERZEICHEN.search("­"))
      and bool(mt._UNSICHTBARE_ZEICHEN.search("­")))

# **Eine Menge, nicht zwei** — sonst driften sie wieder auseinander.
zeile("beide Seiten benutzen dieselbe Zeichenklasse",
      mt.TRUEGERISCHE_ZEICHEN_KLASSE in ek._STEUERZEICHEN.pattern,
      gemessen="email_kanal baut seine Klasse nicht aus mailtext")

# Und die Gegenrichtung: harmloser Text bleibt unangetastet.
for harmlos in ("Rechnung Mai", "Grüße aus Köln", "Re: Angebot 2026"):
    zeile(f"harmloser Betreff bleibt: {harmlos!r}",
          not ek._STEUERZEICHEN.search(harmlos))

# Kopfzeilen-Umbrueche bleiben Sache von email_kanal — dort brechen sie die
# Faltung; im Nachrichtentext sind sie legitim.
zeile("Zeilenumbruch faengt nur die Kopfzeilen-Seite",
      bool(ek._STEUERZEICHEN.search("\n"))
      and not mt._UNSICHTBARE_ZEICHEN.search("\n"))


print()
if fehler:
    print(f"❌ {len(fehler)} von {n} Zeilen rot:")
    for f in fehler:
        print(f"   · {f}")
    sys.exit(1)
print(f"✅ Alle {n} Zeilen von Rang 2 bestanden")
