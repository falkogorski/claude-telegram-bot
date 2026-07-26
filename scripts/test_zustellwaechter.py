#!/usr/bin/env python3
# <!-- ROLLE: test-zustellwaechter -->
"""Verhaltenstest — erreicht Telegram uns noch?

**Zwei Schwerpunkte, und der zweite ist der wichtigere:**

1. Erkennt der Wächter die vier Arten, auf die eine Zustellung ausfallen kann?
2. **Bleibt der Schlüssel drinnen?** Telegram nimmt ihn als Teil der Adresse
   entgegen — er steht damit in jeder Fehlermeldung, die eine Adresse enthält,
   und Fehlermeldungen wandern in Protokolle, Marken und Nachrichten. Genau
   dieser Fund hat bei 5.34 den Zwischenlager-Pfad zur roten Klasse gemacht;
   hier trifft er uns selbst.
"""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="zustell-"))
os.environ["ZUSTELL_MARKE"] = str(_TMP / "zustellung-gestoert")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import zustellmarke as z  # noqa: E402

fails = []
GEHEIM = "8123456789:AAHxK_dieser_Schluessel_darf_nirgends_auftauchen_xyz"


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)


def _info(**kw):
    d = {"url": "https://1.2.3.4:8443/geheimerpfad", "pending_update_count": 0,
         "last_error_message": "", "last_error_date": 0}
    d.update(kw)
    return d


# --- Die vier Ausfallarten -------------------------------------------------
def _gesunde_lage_schweigt():
    gestoert, text = z.bewerten(_info())
    assert not gestoert, f"Fehlalarm bei gesunder Lage: {text}"


def _keine_adresse_ist_der_stillste_ausfall():
    gestoert, text = z.bewerten(_info(url=""))
    assert gestoert, "eine fehlende Zustelladresse gilt als in Ordnung"
    assert "keine Zustelladresse" in text


def _frischer_fehler_wird_gemeldet():
    jetzt = time.time()
    gestoert, text = z.bewerten(
        _info(last_error_message="SSL error: certificate has expired",
              last_error_date=jetzt - 600), jetzt=jetzt)
    assert gestoert, "ein frischer Zustellfehler wurde übergangen"
    assert "10 Minuten" in text, f"der Zeitbezug fehlt: {text}"


def _alter_fehler_ist_geschichte():
    """Ein Fehler von vorgestern, nach dem alles wieder lief, ist keiner mehr —
    sonst wäre der Wächter ein Dauer-Alarm und binnen zwei Tagen abgeschaltet."""
    jetzt = time.time()
    gestoert, _ = z.bewerten(
        _info(last_error_message="irgendwas", last_error_date=jetzt - 48 * 3600),
        jetzt=jetzt)
    assert not gestoert, "ein längst überstandener Fehler schlägt noch Alarm"


def _rueckstau_faellt_auf():
    gestoert, text = z.bewerten(_info(pending_update_count=140))
    assert gestoert, "ein Rückstau von 140 Nachrichten gilt als in Ordnung"
    assert "140" in text and "läuft" in text

    # Aber nicht bei einem einzelnen liegengebliebenen Update — das kann ein
    # Neustart im falschen Augenblick sein.
    gestoert, _ = z.bewerten(_info(pending_update_count=1))
    assert not gestoert, "ein einzelnes wartendes Update löst schon Alarm aus"


# --- Der Schlüssel bleibt drinnen ------------------------------------------
def _schluessel_taucht_nirgends_auf():
    """Der Kern. Vier Wege, auf denen er entkommen könnte — alle vier dicht."""
    adresse = f"https://api.telegram.org/bot{GEHEIM}/setWebhook"
    jetzt = time.time()

    # (1) Über die Fehlermeldung in den Klartext des Befunds.
    _, text = z.bewerten(_info(last_error_message=f"failed to POST {adresse}",
                               last_error_date=jetzt - 60), jetzt=jetzt)
    assert GEHEIM not in text, "der Schlüssel steht im Befundtext!"
    assert "api.telegram.org" not in text, \
        "die Adresse steht im Befundtext — auch ohne Schlüssel unerwünscht"

    # (2) Über die Marke auf die Platte.
    z.setzen(f"Zustellung an {adresse} gescheitert")
    roh = Path(os.environ["ZUSTELL_MARKE"]).read_text(encoding="utf-8")
    assert GEHEIM not in roh, "der Schlüssel steht in der Marke!"
    assert "telegram.org" not in roh, "die Adresse steht in der Marke!"

    # (3) Über die Säuberung selbst — auch ein Schlüssel ohne Adresse drumherum.
    assert GEHEIM not in z.saeubern(f"Token: {GEHEIM}"), \
        "ein nackter Schlüssel überlebt die Säuberung"

    # (4) Über ein UNBEKANNTES Schlüsselformat: Deshalb fliegt die ganze
    #     Adresse raus, nicht nur der erkannte Schlüssel.
    seltsam = "https://api.telegram.org/botKUERZER/x"
    assert "KUERZER" not in z.saeubern(f"POST {seltsam}"), \
        "ein kurzer, unerkannter Schlüssel überlebt in der Adresse"


def _marke_ist_lesbar_und_knapp():
    z.setzen("Telegram konnte vor 5 Minuten nicht zustellen", adresse_gleich=False)
    m = z.gesetzt()
    assert m and not m["adresse_unveraendert"], "der Adress-Hinweis fehlt"
    assert set(m) == {"zeit", "menschlich", "grund", "adresse_unveraendert"}, \
        f"die Marke führt mehr Felder als vorgesehen: {sorted(m)}"
    z.loeschen()
    assert z.gesetzt() is None, "die Marke ließ sich nicht zurücknehmen"


def _kein_modellaufruf_im_modul():
    quelle = Path(z.__file__).read_text(encoding="utf-8")
    for verboten in ("ClaudeSDKClient", "anthropic", "query("):
        assert verboten not in quelle, f"Modell-Aufruf im Modul: {verboten}"


check("gesunde Lage schweigt", _gesunde_lage_schweigt)
check("keine Zustelladresse — der stillste Ausfall", _keine_adresse_ist_der_stillste_ausfall)
check("frischer Zustellfehler wird gemeldet", _frischer_fehler_wird_gemeldet)
check("alter Fehler ist Geschichte, kein Dauer-Alarm", _alter_fehler_ist_geschichte)
check("Rückstau fällt auf, ein einzelnes Update nicht", _rueckstau_faellt_auf)
check("der Schlüssel taucht NIRGENDS auf (vier Wege)", _schluessel_taucht_nirgends_auf)
check("Marke ist knapp und rücknehmbar", _marke_ist_lesbar_und_knapp)
check("kein Modell-Aufruf im Modul", _kein_modellaufruf_im_modul)

print()
if fails:
    print(f"❌ {len(fails)} Zustell-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Zustell-Wächter-Tests bestanden.")
