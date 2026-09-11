> **An Adam, zur Weitergabe an Mick, eine Zeile an Claudia** · Engywuck · 10.09.2026, 13:42 · geprüft: Diff `98712ea..3c8c0ed` (Code vollständig gelesen), vier Prüfer hier ausgeführt, eigene Gegenprobe H-1 mit echtem git

# Hotfix 3c8c0ed: abgenommen. Deploy jetzt, mit Neustart. Eine Zeile an Claudia gehört dazu.

## Gemessen

| | Ergebnis |
|---|---|
| `test_bashfreigabe` 148 · `test_hotfix_h3_h5` 12 · `test_konzept_pdf` 18 · `test_postfach_wiederaufgriff` | alle grün |
| **H-1, eigene Gegenprobe mit echtem git-Repo im Wegwerf-Heim:** Dreischritt (schreiben, hineinschieben, ausführen) | **Dialog** mit Grund „ist nicht versioniert" |
| committet und unverändert | frei |
| committet, dann überschrieben | Dialog „seit dem letzten Commit geaendert" |
| zurückgesetzt | wieder frei |
| Ordner ohne `.git` | Dialog |
| `unshare -rn true` hier | 0, der Probelauf trägt |

Micks Bauform ist besser als mein Vorschlag: Der Inhaltsschutz ist ein **Feld je Basis** (`sperre` oder `git`), keine Ausnahme im Code. Eine dritte Basis muss ihren Schutz benennen. Fail-closed in jede Richtung, der Grund steht im Dialog. H-2 mit echtem Probelauf statt `which`, Verweigerung ohne Namensraum, keine Abschaltung. H-3 bis H-5 wie beauftragt, Micks Nebenfund zur gegenläufigen Prüfzeile ist richtig eingeordnet und richtig umgestellt.

## Was der Hotfix nach sich zieht, und Mick nicht sehen konnte

**Claudia ruft `postfach_ablegen.py` ohne `--herkunft`.** Genau deshalb hatte M-1 die Vorgabe „Claudia" bekommen. Mit der Vorgabe `None` ist sie ab dem Deploy wieder „ohne Absender" mit 5/h, also der Stau vom 07.09., diesmal mit Sofortmeldung. Die Doku nennt die richtige Form bereits (`--herkunft claudia`). **Eine Zeile an Claudia, vor dem Deploy oder direkt danach:**

> Ab dem nächsten Deploy nennst du dich beim Postfach ausdrücklich: `--herkunft claudia` an jedem Aufruf von `scripts/postfach_ablegen.py`. Ohne die Angabe gilt die strenge Grenze von 5 pro Stunde. Trag es ins Register ein.

**Micks Frage zum Mac:** Meine Empfehlung: kein zweiter Weg. Am Mac gilt der direkte pandoc-Aufruf aus CLAUDE.md, das Skript ist für den Server gebaut. Wenn du es am Mac gebraucht hast, sag es Mick; sonst bleibt es so.

## Deploy-Block, Prüfzeilen

Schritt 0 bis 2 wie gehabt: Stand ablesen (erwartet `33d7cdf`), `merge --ff-only 9801c64`, `rc=0` oder `77`, Neustart, `active`. Danach, Micks vier plus eine:

1. `ssh claudebot 'git -C ~/workspace/rechnungen status --porcelain; echo rc=$?'` → `rc=0`, keine Zeile „not a git repository". Kommt sie, ist E-2 auf dem Server nicht vollzogen, und **jeder** Rechnungslauf fragt ab jetzt. Sichere Richtung, aber dann an mich.
2. `ssh claudebot 'unshare -rn true; echo rc=$?'` → `rc=0`. Sonst setzt das PDF-Skript nichts mehr.
3. Ein Rechnungslauf über Claudia geht ohne Dialog durch (H-1 Gegenrichtung).
4. Claudias nächster Postfach-Auftrag mit `--herkunft claudia` kommt ohne 🔇 an.
5. Später, kein Halt: ein Papier mit Referenzbild `![a][l]` durch `konzept_pdf.py` auf dem VPS, mit `ss -tnp` oder `tcpdump` als Horchposten, kein Verbindungsversuch. Das misst H-2 in der Wirkung und H-8 gleich mit.

Danach Block 3b. Mick arbeitet daran bereits.
