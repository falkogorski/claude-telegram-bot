#!/usr/bin/env python3
# <!-- ROLLE: test-postfach-wiederaufgriff -->
"""Verhaltenstest A1 — was schiefgehen kann, geht irgendwann schief.

**Der Befund, aus dem das entstand** (Claudia, 20.08.): `failed/` war ein
Endlager ohne zweiten Versuch, und dort lagen zwei grundverschiedene Klassen
im selben Ordner. Fünf Stundenblumen-Meldungen vom 16.08. warteten dort seit
vier Tagen auf einen Versuch, der nie kam — sämtlich Zeitüberschreitungen.

**Ausführend, nicht lesend.** Die Zustellung läuft echt gegen eine Attrappe am
äußersten Rand — dem Telegram-Aufruf. Alles davor ist der echte Code: das
Lesen der Datei, die Klassifizierung, das Zurückstellen, die Wiedervorlage.
"""
import asyncio
import json
import os
import sys
import tempfile
import time
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="a1-"))
os.environ["POSTFACH_DIR"] = str(_TMP / "postfach")
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

OUT = _TMP / "postfach" / "outbox"
SENT = _TMP / "postfach" / "sent"
FAILED = _TMP / "postfach" / "failed"
for d in (OUT, SENT, FAILED):
    d.mkdir(parents=True, exist_ok=True)

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:
        # Auch eine Ausnahme ist ein Befund, kein Abbruchgrund — sonst laufen
        # die nachfolgenden Prüfungen nicht und ihre Ergebnisse gehen still
        # verloren (Lehre des Tagenschecks, der am 29.07. mitten im Lauf starb).
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


# ── Der RAND: hier ginge etwas zu Adam hinaus ───────────────────────────────
_GESENDET: list[str] = []


class _Bot:
    def __init__(self, fehler: Exception | None = None):
        self._fehler = fehler

    async def send_message(self, chat_id, text, **kw):
        if self._fehler:
            raise self._fehler
        _GESENDET.append(text)

    async def send_document(self, **kw):
        if self._fehler:
            raise self._fehler


class _App:
    def __init__(self, fehler=None):
        self.bot = _Bot(fehler)


def _frisch():
    _GESENDET.clear()
    bot._postfach_zaehler.clear()
    bot._postfach_zurueckgehalten.clear()
    for d in (OUT, SENT, FAILED):
        for f in d.glob("*"):
            f.unlink()


def _auftrag(name="probe-1.json", **felder) -> Path:
    daten = {"target_chat_id": 4711, "text": "Eine Meldung",
             "herkunft": "blume"}
    daten.update(felder)
    p = OUT / name
    p.write_text(json.dumps(daten, ensure_ascii=False), encoding="utf-8")
    return p


def _zustellen(app, job: Path):
    claimed = job.with_name(job.name + ".processing")
    job.rename(claimed)
    asyncio.run(bot._postfach_send_one(app, claimed, SENT, FAILED))


# ── Die Prüfungen ───────────────────────────────────────────────────────────
def _voruebergehender_fehler_kommt_zurueck():
    """Claudias erster fehlender Prüfer: einmal Zeitüberschreitung, Erwartung
    — der Auftrag liegt wieder in `outbox/` mit `versuche == 1`."""
    _frisch()
    job = _auftrag()
    _zustellen(_App(TimeoutError("Timed out")), job)
    zurueck = list(OUT.glob("*.json"))
    assert zurueck, f"der Auftrag ist nicht zurückgekommen: {list(FAILED.glob('*'))}"
    d = json.loads(zurueck[0].read_text())
    assert d["versuche"] == 1, f"Versuchszähler falsch: {d.get('versuche')}"
    assert d["nicht_vor"] > time.time(), "keine Wiedervorlage gesetzt"
    assert not list(FAILED.glob("*.json")), "er liegt zusätzlich im Endlager"


def _dauerhafter_fehler_wandert_sofort_ins_endlager():
    """**Die Gegenrichtung, und sie ist die wichtigere.** Würde alles
    wiederholt, liefe ein dauerhafter Fehler fünfmal ins Leere und Adam wartete
    fünfmal. Die Liste der vorübergehenden Fehler ist deshalb geschlossen."""
    _frisch()
    job = _auftrag()
    _zustellen(_App(ValueError("chat not found")), job)
    assert list(FAILED.glob("*.json")), "ein dauerhafter Fehler wurde wiederholt"
    assert not list(OUT.glob("*.json")), "er liegt zusätzlich in der outbox"


def _nach_fuenf_versuchen_endlager_mit_meldung():
    """Claudias zweiter fehlender Prüfer: fünfmal gescheitert, Erwartung — er
    liegt in `failed/` **und eine Meldung ging hinaus**. Ohne die Meldung wäre
    der Verlust am Ende doch lautlos, nur seltener."""
    _frisch()
    job = _auftrag(versuche=bot.WIEDERVERSUCH_MAX - 1)
    # Die Attrappe wirft beim Zustellen, nicht beim Melden — sonst prüfte man
    # den Melde-Weg gegen einen Boten, der ohnehin nichts kann.
    class _Zweischichtig(_Bot):
        def __init__(self):
            super().__init__(None)
            self._erste = True

        async def send_message(self, chat_id, text, **kw):
            if self._erste:
                self._erste = False
                raise TimeoutError("Timed out")
            _GESENDET.append(text)

    app = _App()
    app.bot = _Zweischichtig()
    _zustellen(app, job)
    assert list(FAILED.glob("*.json")), "nach dem letzten Versuch kein Endlager"
    assert _GESENDET, "der endgültige Verlust wurde verschwiegen"
    assert "nicht zustellen" in _GESENDET[-1], f"unklare Meldung: {_GESENDET[-1]}"


def _gedrosseltes_landet_in_der_outbox_nicht_in_sent():
    """**Der Ordner darf nicht mehr lügen.** Am 20.08. um 10:55 vermisste Adam
    eine angeforderte Datei — sie lag in `sent/` mit der Notiz
    „zurückgehalten". Von außen sah das aus wie zugestellt."""
    _frisch()
    for i in range(bot.POSTFACH_GRENZE):
        _zustellen(_App(), _auftrag(f"durch-{i}.json"))
    assert len(list(SENT.glob("*.json"))) == bot.POSTFACH_GRENZE, "Vorlauf falsch"
    _zustellen(_App(), _auftrag("zuviel.json"))
    zurueck = list(OUT.glob("*.json"))
    assert zurueck, "das Gedrosselte liegt nicht in der outbox"
    d = json.loads(zurueck[0].read_text())
    assert "gedrosselt" in d.get("letzter_grund", ""), f"falscher Grund: {d}"
    assert d["nicht_vor"] > time.time(), "keine Wiedervorlage am Fensterende"
    assert not (SENT / "zuviel.json").exists(), \
        "das Gedrosselte liegt weiterhin in sent/ — der Ordner lügt"


def _wiedervorlage_wird_respektiert():
    """Ein Auftrag mit Zukunfts-Termin wird übersprungen — und ein fälliger
    nicht. Die Gegenrichtung gehört dazu, sonst wüsste man nur, dass etwas
    liegen bleibt, nicht dass es je wieder anläuft."""
    _frisch()
    kuenftig = _auftrag("spaeter.json", nicht_vor=time.time() + 600)
    assert bot._postfach_wartet_noch(kuenftig), "die Wiedervorlage greift nicht"
    faellig = _auftrag("jetzt.json", nicht_vor=time.time() - 5)
    assert not bot._postfach_wartet_noch(faellig), "ein fälliger Auftrag wartet"


def _unlesbarer_auftrag_wartet_nicht_ewig():
    """**Sonst bliebe eine beschädigte Datei für immer liegen** — dieselbe
    Klasse wie der kaputte Zeitstempel im Versions-Monitor, der einen Eintrag
    dauerhaft stillgelegt hat, während das Protokoll Ruhe meldete."""
    _frisch()
    kaputt = OUT / "kaputt.json"
    kaputt.write_text("{das ist kein json", encoding="utf-8")
    assert not bot._postfach_wartet_noch(kaputt), \
        "ein unlesbarer Auftrag wird auf ewig zurückgestellt"


def _fensterrest_ist_das_echte_ende_kein_geratener_abstand():
    """Die Drosselung ist der einzige vorübergehende Zustand mit **bekanntem**
    Ende. Ihn zu raten wäre unnötig — und entweder zu früh (wieder gedrosselt)
    oder zu spät (Nachricht liegt grundlos)."""
    _frisch()
    jetzt = time.time()
    bot._postfach_zaehler["blume"] = [jetzt - 100]
    rest = bot._postfach_fenster_rest("blume", jetzt)
    erwartet = bot.POSTFACH_FENSTER_S - 100
    assert abs(rest - (erwartet + 10)) < 2, \
        f"Fensterrest falsch gerechnet: {rest:.0f} statt ~{erwartet + 10}"


def _klassifizierung_trifft_die_echten_faelle():
    """Gemessen an den Fehlertexten, die **tatsächlich** in `bot-errors.log`
    stehen — nicht an ausgedachten."""
    for echt in ("TimedOut: Timed out",
                 "NetworkError: httpx.ReadError",
                 "RuntimeError('This HTTPXRequest is not initialized!')"):
        assert bot._ist_voruebergehend(echt), f"nicht erkannt: {echt}"
    for dauerhaft in ("parse-Fehler: Expecting ':' delimiter",
                      "Chat not found", "Forbidden: bot was blocked"):
        assert not bot._ist_voruebergehend(dauerhaft), \
            f"faelschlich als vorübergehend eingestuft: {dauerhaft}"


def _nachgereichtes_ist_als_solches_erkennbar():
    """Ein wiederholter Auftrag kommt später an als ein frisch gelegter. Ohne
    Hinweis wirkt die Reihenfolge im Chat willkürlich — mit ihm ist sie
    erklärt. Gegenrichtung: ein Erstversuch trägt den Vorspann NICHT."""
    _frisch()
    _zustellen(_App(), _auftrag("wiederholt.json", versuche=2,
                                gelegt="2026-08-20 09:15:00"))
    assert _GESENDET and _GESENDET[-1].startswith("↩️ Nachgereicht"), \
        f"der Nachreich-Hinweis fehlt: {_GESENDET[-1][:80]}"
    assert "09:15" in _GESENDET[-1], "der ursprüngliche Zeitpunkt fehlt"
    _frisch()
    _zustellen(_App(), _auftrag("erstmals.json"))
    assert not _GESENDET[-1].startswith("↩️"), \
        f"ein Erstversuch wird als nachgereicht ausgegeben: {_GESENDET[-1][:80]}"


def _drosselung_verbraucht_den_versuchszaehler_nicht():
    """**Engywucks Befund vom 20.08.** Eine gedrosselte Nachricht ist nicht
    gescheitert — sie war noch nicht dran. Zaehlte sie gegen die fuenf
    Versuche, landeten bei laengerem Rueckstau hintere Nachrichten im
    Endlager, obwohl nie ein Versuch fehlschlug.

    Gemessen ueber SECHS Drossel-Runden: mehr als die Versuchsgrenze."""
    _frisch()
    for i in range(bot.POSTFACH_GRENZE):
        _zustellen(_App(), _auftrag(f"durch-{i}.json"))
    job = _auftrag("gestaut.json")
    for runde in range(bot.WIEDERVERSUCH_MAX + 1):
        _zustellen(_App(), job)
        liegend = list(OUT.glob("gestaut.json"))
        assert liegend, f"nach Drossel-Runde {runde + 1} ist die Nachricht fort"
        job = liegend[0]
        d = json.loads(job.read_text())
        assert d.get("versuche", 0) == 0, \
            f"die Drosselung hat den Versuchszaehler verbraucht: {d}"
    assert not list(FAILED.glob("gestaut.json")), \
        "eine nie gescheiterte Nachricht landete im Endlager"
    assert d["drossel_runden"] == bot.WIEDERVERSUCH_MAX + 1, \
        f"die Drossel-Runden werden nicht gezaehlt: {d}"


def _echte_fehlschlaege_zaehlen_weiterhin():
    """**Die Gegenrichtung.** Wuerde gar nichts mehr zaehlen, liefe ein
    dauerhaft unzustellbarer Auftrag ewig im Kreis — die Endlosschleife, die
    der Zaehler gerade verhindern soll."""
    _frisch()
    job = _auftrag("kaputt-aber-transient.json")
    _zustellen(_App(TimeoutError("Timed out")), job)
    d = json.loads(list(OUT.glob("*.json"))[0].read_text())
    assert d["versuche"] == 1, f"ein echter Fehlschlag zaehlt nicht mehr: {d}"


check("vorübergehender Fehler kommt zurück in die outbox",
      _voruebergehender_fehler_kommt_zurueck)
check("dauerhafter Fehler wandert sofort ins Endlager (Gegenrichtung)",
      _dauerhafter_fehler_wandert_sofort_ins_endlager)
check("nach dem letzten Versuch: Endlager MIT Meldung",
      _nach_fuenf_versuchen_endlager_mit_meldung)
check("Gedrosseltes landet in der outbox, nicht in sent/",
      _gedrosseltes_landet_in_der_outbox_nicht_in_sent)
check("die Wiedervorlage wird respektiert (beide Richtungen)",
      _wiedervorlage_wird_respektiert)
check("ein unlesbarer Auftrag wartet nicht ewig",
      _unlesbarer_auftrag_wartet_nicht_ewig)
check("der Fensterrest wird gerechnet, nicht geraten",
      _fensterrest_ist_das_echte_ende_kein_geratener_abstand)
check("die Klassifizierung trifft die echten Fälle",
      _klassifizierung_trifft_die_echten_faelle)
check("Nachgereichtes ist als solches erkennbar (beide Richtungen)",
      _nachgereichtes_ist_als_solches_erkennbar)
check("Drosselung verbraucht den Versuchszaehler nicht (Engywuck)",
      _drosselung_verbraucht_den_versuchszaehler_nicht)
check("echte Fehlschlaege zaehlen weiterhin (Gegenrichtung)",
      _echte_fehlschlaege_zaehlen_weiterhin)

print()
if fails:
    print(f"❌ {len(fails)} A1-Prüfung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle A1-Wiederaufgriff-Tests bestanden.")
