<!-- ROLLE: vorpruefung-business-anbindungen -->
# Vorprüfung: Business-Anbindungen (I)

> **Gültigkeits-Kopf** (Regel ⑪)
> **Stichtag:** 25.07.2026 · **Überholt durch:** —
> **Maßgeblich** bleibt die Status-Zeile im Drehbuch.
>
> **Dies ist eine Vorprüfung, keine Empfehlung und kein Bau.** Ergebnis soll
> vorliegen, wenn Adam am 15. August zurückkommt.
>
> **💰 Diese Prüfung hat nichts gekostet:** ausschließlich kostenfreies Abrufen
> der Herstellerdokumentation, keine bezahlte Suche.

**Je Plattform drei Fragen:** Gibt es einen **offiziellen Weg**? Was **kostet**
er? Welche **Ampel-Farbe** trägt er?

**Wie „geprüft" hier zu lesen ist:** ✅ = an der Herstellerdokumentation
nachgelesen · ⚠️ = **ungeprüfte Annahme**, muss vor jedem Bau nachgemessen
werden. Diese Trennung ist der eigentliche Wert des Dokuments — eine
Vorprüfung, die Vermutung und Beleg vermischt, ist schlimmer als keine.

---

## Übersicht

| Plattform | Offizieller Weg | Gebühr für die Schnittstelle | Ampel | Hürde |
|---|---|---|---|---|
| **Instagram** | ✅ ja (Instagram API, mehrere Varianten) | ⚠️ keine genannt | 🟡 | **Business- oder Creator-Konto**, verknüpft mit einer Facebook-Seite |
| **Facebook** | ✅ ja (Pages API, Beiträge veröffentlichen) | ⚠️ keine genannt | 🟡 | Berechtigungen `pages_manage_posts` u. a.; **App-Review nur nötig, wenn man die Seite nicht selbst verwaltet** |
| **TikTok** | ✅ ja (Content Posting API) | ⚠️ keine genannt | 🟡 | **Audit ist Pflicht** — ohne Prüfung sind veröffentlichte Inhalte auf „privat" beschränkt |
| **Canva** | ✅ ja (Connect APIs) | ⚠️ keine Gebühr genannt, **aber:** private Integrationen verlangen den **Enterprise-Plan** | 🟡 | Enterprise-Plan **oder** öffentliche Integration mit Canva-Review |
| **Digistore24** | ⚠️ ungeprüft | ⚠️ ungeprüft | 🟡 | Hilfe-Seiten antworten mit 403, von hier nicht lesbar |
| **CapCut** | ⚠️ vermutlich keiner | — | — | Keine öffentliche Entwickler-Dokumentation gefunden |
| **E-Mail** | ✅ ja — **Standardprotokolle**, kein Anbieter dazwischen | **keine** | 🟢 | Je Konto ein anwendungsspezifisches Kennwort |

---

## Was daraus folgt — drei Beobachtungen

**① E-Mail ist der einzige grüne Weg, und das ist kein Zufall.** IMAP und SMTP
sind **offene Protokolle**: kein Betreiber kann den Zugang entziehen, keine
Prüfung, keine Kontobindung, keine Gebühr. Alle anderen Wege führen über einen
Anbieter, der die Regeln jederzeit ändern kann. Das deckt sich mit dem
Grundwert der Souveränität — und es ist ein Argument, **9.5 (E-Mail) vorzuziehen**,
wenn es um Wirkung je Aufwand geht.

**② Die Gebührenfrage ist nicht die eigentliche Hürde — die Kontobindung ist es.**
Keine der Plattformen verlangt laut Dokumentation Geld für die Schnittstelle.
Was sie verlangen, ist ein **Konto der richtigen Art** (Business, Creator,
Enterprise) und in den meisten Fällen eine **Prüfung durch den Anbieter**. Bei
Canva ist die Hürde am teuersten versteckt: „kostenlos" gilt nur für öffentliche
Integrationen; die private, die wir bräuchten, hängt am Enterprise-Plan.

**③ Connis Kenntnisstand hat sich weitgehend bestätigt — mit einer wichtigen
Abschwächung.** Meta verlangt tatsächlich Geschäftskonto und Prüfung, und TikToks
Audit-Pflicht ist real. **Aber:** Bei Facebook ist die App-Review **nur** nötig,
wenn man die Seite *nicht selbst verwaltet*. Für Adams eigene Seite entfällt sie
also. Das ist ein spürbarer Unterschied — er verschiebt Facebook von „hohe
Hürde" auf „machbar".

---

## Was ausdrücklich offen bleibt

- **Digistore24** — die Hilfe-Seiten sind von hier nicht abrufbar (403). Adam
  hat dort ein Konto und kommt an die Dokumentation; **eine Frage an ihn, keine
  Recherche-Aufgabe.**
- **Kontosperr-Risiko bei Drittweg-Automatisierung** (Connis Warnung) — ließ
  sich in der Dokumentation nicht belegen. **Bleibt als Annahme stehen**, weil
  sie plausibel ist und im Zweifel die vorsichtigere Haltung stützt.
- **Gebühren bei hohem Volumen** — für unsere Größenordnung nicht relevant, aber
  auch nicht ausgeschlossen; keine der Seiten nennt Zahlen.
- **CapCut** — kein offizieller Weg gefunden. Vor jedem Umweg gilt die Regel
  „Fremdes nehmen, wo es nicht ans Herz geht" **nicht**: Ein inoffizieller Weg
  bei einem Anbieter, der keinen anbietet, ist genau die Art Abhängigkeit, die
  später bricht.

## Empfehlung für den 15. August

**Reihenfolge nach Wirkung je Aufwand:** E-Mail (🟢, keine Hürde, größter
Alltagsnutzen) → Facebook-Seite (Review entfällt bei eigener Seite) → Instagram
(dieselbe Konto-Welt, ein Schritt mehr) → TikTok (Audit-Pflicht einplanen) →
Canva (erst prüfen, ob der Enterprise-Plan überhaupt in Frage kommt) →
Digistore24 (Adams Dokumentation abwarten) → CapCut (vorerst nicht).

**Vor jedem Bau gilt unverändert:** 💰-Dialog, wenn irgendwo eine Gebühr
auftaucht, und Ampel-Einstufung der Daten, die dorthin fließen würden.
