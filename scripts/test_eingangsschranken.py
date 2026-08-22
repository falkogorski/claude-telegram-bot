#!/usr/bin/env python3
# <!-- ROLLE: test-eingangsschranken -->
"""Die Schranken gegen Anweisungen aus Fremdinhalten — **ausgeführt, nicht gelesen.**

**Adams Kopfsatz, der die ganze Kette begründet (22.08.):**

> Einen Auftrag zu geben heißt, das **Lesen** zu beauftragen — niemals das
> Handeln nach dem Gelesenen.

Deshalb fragt keine dieser Prüfungen *„ist das ein Befehl?"* — das wäre eine
Inhaltsfrage, und Inhalt lässt sich beliebig tarnen (weiße Schrift,
Zero-Width-Zeichen, Text in Bildern). Gefragt wird stattdessen: **erreicht
Fremdinhalt eine Handlung?** Darauf gibt es eine bauartbedingte Antwort.

Grundlage: `docs/befund-eingangs-firewall-analyse.md` (26 Agenten, 58
Angriffsbefunde), freigegeben von Engywuck am 22.08.

**Warum ausführend:** In diesem Projekt haben lesende Prüfer schon zweimal
einen Fehler nicht nur übersehen, sondern **gedeckt** — einmal, indem eine
AST-Regel nur die Schreibweise maß und den schwersten Fehler des Projekts
erzeugte; einmal, indem eine Attrappe genau die falsche Signatur nachbaute.
"""
import asyncio
import os
import sys
import tempfile
from pathlib import Path

_TMP = Path(tempfile.mkdtemp(prefix="schranken-"))
os.environ["TELEGRAM_BOT_TOKEN"] = "1:test"
os.environ["ALLOWED_USER_IDS"] = "4711"
os.environ["USER_PREFS_FILE"] = str(_TMP / "prefs.json")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import bot  # noqa: E402

fails = []


def check(name, fn):
    try:
        fn()
        print(f"✓ {name}")
    except AssertionError as e:
        print(f"✗ {name}: {e}")
        fails.append(name)
    except Exception as e:
        print(f"✗ {name}: {type(e).__name__}: {e}")
        fails.append(name)


# --------------------------------------------------------------------------
# ① Absender-Schranke beim Kanal-Eintrag
# --------------------------------------------------------------------------

class _Chat:
    def __init__(self, cid, typ="channel", titel="Fremder Kanal"):
        self.id = cid
        self.type = typ
        self.title = titel
        self.username = None
        self.is_forum = False


class _Mitglied:
    def __init__(self, status="administrator"):
        self.status = status


class _MemberUpdate:
    def __init__(self, chat, von_id):
        self.chat = chat
        self.new_chat_member = _Mitglied()
        self.from_user = type("U", (), {"id": von_id})()


class _Update:
    def __init__(self, chat, von_id):
        self.my_chat_member = _MemberUpdate(chat, von_id)

    def get_bot(self):
        class _B:
            async def send_message(self, *a, **k):
                return None
        return _B()


def _fremder_darf_den_ausgabekanal_nicht_setzen():
    """**Der Kern von ①.**

    Ein Fremder trägt den Bot in seinen Kanal als Administrator ein. Vorher
    wurde daraus der Ausgabekanal — Zusammenfassungen, Dateien und
    Sprachausgabe wären dorthin gegangen. Geprüft wird der **Zustand danach**,
    nicht ob eine Prüfzeile dasteht.
    """
    bot._USER_PREFS.pop("output_channel_id", None)
    asyncio.run(bot.on_my_chat_member(_Update(_Chat(-1009999999999), 666), None))
    assert "output_channel_id" not in bot._USER_PREFS, \
        ("ein Fremder hat den Ausgabekanal gesetzt — der Rueckweg steht offen: "
         f"{bot._USER_PREFS.get('output_channel_id')}")


def _adam_darf_den_ausgabekanal_setzen():
    """Die Gegenrichtung — sonst prueft die Zeile oben nur Untaetigkeit.

    Eine Schranke, die alles abweist, besteht jede Sicherheitspruefung und
    macht das Feature kaputt.
    """
    bot._USER_PREFS.pop("output_channel_id", None)
    asyncio.run(bot.on_my_chat_member(_Update(_Chat(-1001234567890), 4711), None))
    assert bot._USER_PREFS.get("output_channel_id") == -1001234567890, \
        "Adam selbst konnte den Ausgabekanal nicht mehr setzen"


def _auch_gruppen_brauchen_den_absender():
    """Der Gruppen-Zweig legt Zimmer an und meldet an Adam — auch das ist
    eine Handlung, die ein Fremder nicht ausloesen darf."""
    gesendet = []

    class _U(_Update):
        def get_bot(self):
            class _B:
                async def send_message(self, *a, **k):
                    gesendet.append(k.get("text", ""))
            return _B()

    asyncio.run(bot.on_my_chat_member(
        _U(_Chat(-1008888888888, "supergroup", "🔧 Werkstatt"), 666), None))
    assert not gesendet, \
        "ein Fremder konnte ueber eine Gruppe eine Meldung an Adam ausloesen"


check("Fremder setzt KEINEN Ausgabekanal", _fremder_darf_den_ausgabekanal_nicht_setzen)
check("Adam setzt ihn weiterhin", _adam_darf_den_ausgabekanal_setzen)
check("auch der Gruppen-Zweig prueft den Absender", _auch_gruppen_brauchen_den_absender)


# --------------------------------------------------------------------------
# (2) Neben-Laeufe bekommen kein Werkzeug
# --------------------------------------------------------------------------

def _nebenlauf_hat_keine_werkzeuge():
    """**Der Kern von (2) - ausgefuehrt, nicht gelesen.**

    Die Optionen werden ERZEUGT und ihre Felder gemessen. Ein Text-Pruefer
    haette hier versagt: Die alte Fassung sah mit `allowed_tools=[]` aus wie
    "keine Werkzeuge" und bedeutete das Gegenteil.
    """
    o = bot.werkzeugfreie_optionen("egal")
    assert o.permission_mode == "dontAsk", (
        f"Modus ist {o.permission_mode!r} - bei 'bypassPermissions' wird JEDER "
        "Werkzeugaufruf automatisch genehmigt und der Rueckruf nie gefragt")
    assert o.allowed_tools == [], \
        f"die Positivliste ist nicht leer: {o.allowed_tools}"
    assert "Bash" in o.disallowed_tools, \
        "der zweite Riegel fehlt - Bash steht nicht auf der Verbotsliste"


def _die_gefaehrliche_kombination_kommt_nicht_zurueck():
    """`bypassPermissions` darf im ausfuehrbaren Code nicht wieder auftauchen.

    Zugegeben eine Textpruefung - aber sie misst eine Abwesenheit, und die
    laesst sich nicht ausfuehren. Kommentare sind ausgenommen, sonst schlaegt
    die Zeile ueber ihre eigene Begruendung an (dieser Fehler ist in diesem
    Projekt schon vorgekommen).
    """
    quelle = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
    treffer = [z.strip() for z in quelle.splitlines()
               if "bypassPermissions" in z and not z.lstrip().startswith("#")
               and "``" not in z and not z.lstrip().startswith("bypassPermissions")]
    assert not treffer, f"bypassPermissions steht wieder im Code: {treffer[:2]}"


def _beide_nebenlaeufe_nutzen_die_fabrik():
    """Eine Sicherheitsentscheidung, EINE Stelle.

    Zwei Stellen mit derselben Entscheidung laufen auseinander - dieselbe
    Klasse wie die fuenf Kanal-Verweise am 20.08.
    """
    quelle = (Path(__file__).resolve().parent.parent / "bot.py").read_text(encoding="utf-8")
    zeilen = [z for z in quelle.splitlines()
              if "werkzeugfreie_optionen(" in z
              and not z.lstrip().startswith(("def ", "async def"))]
    assert len(zeilen) >= 2, (
        f"nur {len(zeilen)} Aufrufstelle(n) der Fabrik - baut jemand die "
        "Optionen wieder von Hand?")


check("Nebenlauf hat kein Werkzeug", _nebenlauf_hat_keine_werkzeuge)
check("bypassPermissions kommt nicht zurueck", _die_gefaehrliche_kombination_kommt_nicht_zurueck)
check("beide Nebenlaeufe nutzen die Fabrik", _beide_nebenlaeufe_nutzen_die_fabrik)


# --------------------------------------------------------------------------
# (3) Die Vertrauensliste fuer Web-Abrufe
# --------------------------------------------------------------------------

def _dateinamen_werden_keine_vertrauten_domains():
    """**Der Kern von (3b).**

    `.md` ist Moldawien, `.py` Paraguay, `.sh` St. Helena. Der alte Kommentar
    hielt "bot.py" fuer harmlos, weil "niemand ruft sie ab" - man KANN sie
    abrufen, wenn jemand die Domain registriert. Und wir schreiben diese
    Dateinamen in fast jeder Nachricht.
    """
    text = "Schau in MIGRATION.md und bot.py, dann auf de.wikipedia.org"
    vertrauen = bot._extract_hosts(text, fuer_vertrauen=True)
    assert "migration.md" not in vertrauen, \
        f"ein Dateiname wurde zur vertrauten Domain: {sorted(vertrauen)}"
    assert "bot.py" not in vertrauen, \
        f"ein Dateiname wurde zur vertrauten Domain: {sorted(vertrauen)}"
    assert "de.wikipedia.org" in vertrauen, \
        "eine echte Adresse faellt jetzt heraus - zu scharf geschnitten"


def _die_erkennung_bleibt_grosszuegig():
    """Gegenrichtung: OHNE Vertrauens-Flagge bleibt alles wie bisher.

    Sonst haette Adams "schau auf de.wikipedia.org/xy" wieder eine Rueckfrage
    ausgeloest - der Komfort-Fund vom 23.07., den wir nicht zurueckdrehen.
    """
    hosts = bot._extract_hosts("Schau in MIGRATION.md")
    assert "migration.md" in hosts, \
        "die reine Erkennung wurde mitverschaerft - das war nicht beauftragt"


def _adresse_mit_anhang_wird_nicht_automatisch_freigegeben():
    """**Der Kern von (3c) - ausgefuehrt ueber den echten Rueckruf.**

    Eine vertraute Domain mit Frageteil ist der Weg nach draussen:
    `wikipedia.org/?x=<Geheimnis>`. Der Name allein darf nicht mehr genuegen.
    """
    from claude_agent_sdk import PermissionResultAllow
    # Echte Sitzung statt handgebauter Attrappe: Eine Attrappe traegt genau
    # die Felder, an die der Schreiber gedacht hat - und deckt damit den
    # Fehler, den sie finden soll (in diesem Projekt schon vorgekommen).
    sess = bot.UserSession(client=object())
    sess.task_origins = {"wikipedia.org"}
    sess.bot = object()
    sess.chat_id = 4711
    sess.user_id = 4711
    bot.SESSIONS[4711] = sess
    rueckruf = bot.make_permission_callback(4711)

    class _Ctx:
        suggestions = None

    def frage(url):
        return asyncio.run(rueckruf("WebFetch", {"url": url}, _Ctx()))

    ohne = frage("https://wikipedia.org/wiki/Koeln")
    assert isinstance(ohne, PermissionResultAllow), \
        "eine schlichte vertraute Adresse loest jetzt eine Rueckfrage aus"

    mit = frage("https://wikipedia.org/?x=sk-geheim-1234")
    assert not isinstance(mit, PermissionResultAllow), \
        "eine vertraute Adresse MIT Anhang wurde ohne Rueckfrage freigegeben"


check("Dateinamen werden keine vertrauten Domains", _dateinamen_werden_keine_vertrauten_domains)
check("die Erkennung bleibt grosszuegig", _die_erkennung_bleibt_grosszuegig)
check("Adresse mit Anhang braucht Rueckfrage", _adresse_mit_anhang_wird_nicht_automatisch_freigegeben)


# --------------------------------------------------------------------------
# (4) Die Suchanfrage ist ein Ausgangskanal
# --------------------------------------------------------------------------

def _suche_mit_geheimnis_wird_nicht_durchgewunken():
    """**Der Kern von (4) - ausgefuehrt ueber den echten Rueckruf.**

    Die Suchfreigabe stand als eine der ERSTEN Regeln, noch vor der
    Geheimnis-Pruefung. Was in eine Suchanfrage geschrieben wird, verlaesst
    das System - ein Zugangsschluessel waere abgeflossen, ohne dass jemand
    gefragt worden waere.
    """
    from claude_agent_sdk import PermissionResultAllow
    sess = bot.UserSession(client=object())
    sess.bot = object()
    sess.chat_id = 4711
    sess.user_id = 4711
    bot.SESSIONS[4711] = sess
    rueckruf = bot.make_permission_callback(4711)

    class _Ctx:
        suggestions = None

    def suche(frage):
        return asyncio.run(rueckruf(bot._SEARCH_TOOL_NAME, {"query": frage}, _Ctx()))

    normal = suche("Wetter in Koeln morgen")
    assert isinstance(normal, PermissionResultAllow), \
        "eine normale Suche loest jetzt eine Rueckfrage aus - zu scharf"

    heikel = suche("was bedeutet dieser token aus der .env datei")
    assert not isinstance(heikel, PermissionResultAllow), \
        "eine Suche mit Geheimnis-Bezug wurde ohne Rueckfrage nach draussen gelassen"


check("Suche mit Geheimnis braucht Rueckfrage", _suche_mit_geheimnis_wird_nicht_durchgewunken)

print()
if fails:
    print(f"❌ {len(fails)} Schranken-Pruefung(en) fehlgeschlagen: {', '.join(fails)}")
    sys.exit(1)
print("Alle Eingangsschranken-Tests bestanden.")
