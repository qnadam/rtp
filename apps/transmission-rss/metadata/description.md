# Transmission RSS

RSS feedeket figyel (pl. showrss.info, ezrss.it, vagy saját Prowlarr/seriesly
feedek), és az új, illeszkedő elemeket automatikusan hozzáadja a már futó
**Transmission** torrentlistájához az RPC API-n keresztül. Nincs saját web
felülete — daemonként fut a háttérben.

Forrás: [github.com/nning/transmission-rss](https://github.com/nning/transmission-rss)

## Image forrása

A hivatalos, előre épített `nning2/transmission-rss` Docker Hub image 3+ éve
nem kapott új build-et, miközben a repó forráskódja aktívan karbantartott.
Ezért egy saját GitHub Actions workflow (`.github/workflows/build-transmission-rss.yml`
ebben a repóban) építi friss Alpine alapra a repó jelenlegi forrásából, és
tolja fel a te GHCR (`ghcr.io`) registrydedbe.

**Első használat előtt:**

1. Futtasd le kézzel a workflow-t (GitHub -> Actions -> "Build
   transmission-rss image" -> Run workflow).
2. A lefutás után nézd meg a GitHub-on a csomagjaid (Packages) között
   létrejött `transmission-rss` package-et, és állítsd **Public**-ra a
   láthatóságát — enélkül a Runtipi szervered nem fogja tudni lehúzni az
   image-et (nincs beállítva GHCR hitelesítés a `docker compose pull`-hoz).
3. Az `apps/transmission-rss/docker-compose.yml`-ben cseréld le a
   `<GITHUB_USERNAME>`-t a saját GitHub felhasználó-/szervezetnevedre.

## Kötelező: konfigurációs fájl telepítés ELŐTT

A konfiguráció egy `/etc/transmission-rss.conf` YAML fájlban történik, amit
a konténer **csak olvas** — ezt neked kell létrehoznod a host oldalon,
mielőtt telepítenéd az appot:

```bash
mkdir -p /home/a/runtipi/app-data/a/transmission-rss/data/state
cat > /home/a/runtipi/app-data/a/transmission-rss/data/transmission-rss.conf << 'CONF'
feeds:
  - url: http://example.com/feed1

update_interval: 600

server:
  host: host.docker.internal
  port: 9091
  tls: false

seen_file: /data/seen

log:
  target: :stdout
  level: info
CONF
```

(Az útvonal `APP_DATA_DIR`-nek felel meg — ha a te store-slugod nem `a`,
igazítsd a mappanevet.)

A `server.host: host.docker.internal` + a compose-ban lévő `extra_hosts`
trükk miatt éri el a már futó Transmission app RPC portját (9091) a host
gépen keresztül, anélkül hogy a meglévő transmission app hálózati
beállításait módosítani kellene.

## Lehetséges buktató: Transmission RPC whitelist

A linuxserver/transmission image alapértelmezés szerint csak néhány IP-ről
(jellemzően csak localhost) fogadja el az RPC hívásokat. Ha a
transmission-rss logjában `409`-es vagy "forbidden" hibát látsz, a saját
`apps/transmission/docker-compose.yml`-edben (a te custom store-odban, nem
kell hivatalos appot módosítani) add hozzá:

```yaml
environment:
  - TRANSMISSION_RPC_WHITELIST_ENABLED=false
```

vagy pontosabb megoldásként sorold fel a Docker gateway IP tartományát a
`TRANSMISSION_RPC_WHITELIST` változóban.

## Mappa

| App adat mappa | Konténer mappa | Tartalom |
|---|---|---|
| `data/transmission-rss.conf` | `/etc/transmission-rss.conf` | Feed-lista és beállítások (csak olvasható) |
| `data/state` | `/data` | `seen_file` — melyik elemeket adta már hozzá |

## Frissítés

Mivel saját build-ről van szó: a workflow hetente automatikusan újraépíti
az image-et a `nning/transmission-rss` aktuális `main` ágából, és
`latest` + dátumozott tag alatt publikálja. A Runtipi app `config.json`-jában
a `tipi_version` kézi bumpolásával tudod jelezni magadnak, hogy érdemes
Update-elni (lásd a korábban megbeszélt mechanizmust) — ha ragaszkodsz
egy adott, tesztelt build-hez, a `docker-compose.yml`-ben a `latest` helyett
a dátumozott tag-et is beírhatod.
