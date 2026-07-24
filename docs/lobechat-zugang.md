<!-- ROLLE: lobechat-zugang -->
# LobeChat — Zugang (nur via SSH-Tunnel)

**Sicherheits-Grundsatz (rote Auflage 3.1):** LobeChat ist **niemals öffentlich**
erreichbar. Es lauscht ausschließlich auf `127.0.0.1:3210` des VPS, und die
Firewall lässt Port 3210 von außen nicht durch. Der einzige Weg hinein ist ein
**SSH-Tunnel** — der ist selbst verschlüsselt, deshalb braucht es kein extra
HTTPS.

## Vom Mac (Terminal)

1. Tunnel öffnen (nutzt den bestehenden `claudevps`-SSH-Zugang):
   ```bash
   ssh -N -L 3210:127.0.0.1:3210 claudevps
   ```
   (Das Fenster offen lassen, solange du LobeChat nutzt. `-N` = nur Tunnel,
   keine Shell.)
2. Im Browser öffnen: **http://localhost:3210**
3. Beim ersten Öffnen nach dem **Access-Code** gefragt — den gebe ich dir
   sicher, wenn wir den Login gemeinsam testen (er liegt root-only in
   `/etc/lobe-chat.env` auf dem VPS, kommt nie in den Chat).

## Vom iPhone

Ein SSH-Tunnel vom iPhone braucht eine SSH-App (z. B. „Termius"):
- Host `claudevps` einrichten (gleicher Key/Zugang wie am Mac),
- Port-Weiterleitung `localhost:3210 → 127.0.0.1:3210`,
- dann in Safari `http://localhost:3210`.
Das richten wir beim gemeinsamen Test einmal ein (Sprint SA-Tag).

## Was dahinter steckt

- **Backend:** LiteLLM (`127.0.0.1:4000`) → aktuell das lokale Modell
  `local` (Ollama phi4-mini). LobeChat hat **keinen** Zugang zum Claude-Abo
  (das läuft nur über den Telegram-Bot) — bewusst, für Datenschutz/lokale Modelle.
- **Container:** `lobehub/lobe-chat`, `docker restart always` → überlebt
  VPS-Neustarts (Docker-Dienst ist enabled).

## Rollback / Stoppen

```bash
docker stop lobe-chat        # anhalten
docker start lobe-chat       # wieder starten
docker rm -f lobe-chat       # entfernen (Image bleibt)
```
Nichts davon berührt Bot, LiteLLM, Ollama oder SearxNG.
