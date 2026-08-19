# Saját Runtipi app store — Omada Controller + Jellyfin + Transmission

Ez a repó három saját Runtipi app-ot tartalmaz:

- **omada-controller** — [mbentley/docker-omada-controller](https://github.com/mbentley/docker-omada-controller) OpenJ9 build, host hálózati módban
- **jellyfin** — a már meglévő, kézzel futtatott Jellyfin példány áthozva Runtipi alá, ugyanazokkal a host mappákkal (nincs adatmozgatás)
- **transmission** — a már meglévő, kézzel futtatott Transmission példány áthozva Runtipi alá, ugyanazokkal a portokkal és host mappákkal (nincs adatmozgatás)

```
omada-runtipi-app/
├── standalone-docker-compose.yml     <- gyors teszt SSH-n, Runtipi nélkül (csak omada)
└── apps/
    ├── omada-controller/
    │   ├── config.json
    │   ├── docker-compose.yml
    │   └── metadata/{description.md, logo.jpg}
    ├── jellyfin/
    │   ├── config.json
    │   ├── docker-compose.yml
    │   └── metadata/{description.md, logo.jpg}
    └── transmission/
        ├── config.json
        ├── docker-compose.yml
        └── metadata/{description.md, logo.jpg}
```

Mindkét `docker-compose.yml` tartalmazza a Runtipi v2 dinamikus compose formátumához **kötelező** blokkot:

```yaml
x-runtipi:
  schema_version: 2
```

Enélkül a telepítés séma-validációs hibával elszáll ("schemaVersion must be 2").

## Az app store feltöltése / frissítése

Kétféleképpen viheted be a repódba:

**A) GitHub webes felület** (amit eddig is használtál): a repód oldalán *Add file → Upload files*, húzd be a megfelelő `apps/<app-neve>` mappát, majd Commit. Ellenőrizd utána a GitHubon, hogy a fájlok tényleg a jó útvonalon landoltak (`apps/omada-controller/...`, `apps/jellyfin/...`), és hogy a `docker-compose.yml` tartalmazza a fenti `x-runtipi` blokkot.

**B) git CLI a szerveren:**

```bash
cd <saját-repo>
git pull
cp -r apps/jellyfin apps/omada-controller <saját-repo>/apps/
git add apps/jellyfin apps/omada-controller
git commit -m "Add/update jellyfin + omada-controller apps"
git push
```

Utána mindkét esetben: Runtipi felület → **Update App Stores**.

## Omada Controller telepítése

Lásd korábbi útmutató röviden:

1. App Store-ban keresd meg **"Omada Controller (OpenJ9)"**, telepítsd
2. Első belépés: `https://<szerver-ip>:8043` (önaláírt tanúsítvány, fogadd el)
3. Host hálózati módban fut (szándékosan, az eszközfelfedezés miatt), nincs Traefik/domain integráció

## Jellyfin telepítése — FONTOS sorrend

A meglévő, kézzel indított `jellyfin` konténer neve ütközni fog az újjal, ezért **telepítés előtt** állítsd le és távolítsd el a régit (a host mappákat, `config`/`cache`/`/mnt/nas/pk`, **NE** töröld, azokra szükség van):

```bash
docker stop jellyfin
docker rm jellyfin
```

Utána a Runtipi App Store-ban keresd meg **"Jellyfin (saját)"**-t, és telepítsd. A telepítő űrlapon az alapértelmezett port `8096` — ezt hagyd úgy, ahogy van, hogy a meglévő router port forward változtatás nélkül tovább működjön.

Telepítés után nyisd meg `http://<szerver-ip>:8096`-on — a könyvtárnak, felhasználóknak és nézettségi előzményeknek azonnal ott kell lenniük, mivel ugyanazokat a host mappákat használja (`/home/a/jellyfin/config`, `/home/a/jellyfin/cache`, `/mnt/nas/pk`), amiket eddig is.

A verzió (`10.11.6`) szándékosan rögzített a `docker-compose.yml`-ben, hogy ne fusson le automatikus, esetleg visszavonhatatlan adatbázis-migrációt okozó frissítés a háttérben.

## Transmission telepítése — FONTOS sorrend

A meglévő, kézzel indított `transmission` konténer neve ütközni fog az újjal, ezért **telepítés előtt** állítsd le és távolítsd el a régit (a host mappákat, `config`/`incomplete`/`/mnt/nas/pk`, **NE** töröld):

```bash
docker stop transmission
docker rm transmission
```

Utána a Runtipi App Store-ban keresd meg **"Transmission (saját)"**-t, és telepítsd. A portok (`9091` web UI, `34567` tcp+udp peer port) fixen be vannak drótozva a compose fájlba, nem kérdez rá telepítéskor — így a routeren beállított port forwardot nem kell módosítani.

Telepítés után nyisd meg `http://<szerver-ip>:9091`-en — a torrentlistának és beállításoknak azonnal ott kell lenniük.

## Frissítés később (bármelyik app)

1. `apps/<app>/docker-compose.yml`-ben cseréld le az image tag-et
2. `apps/<app>/config.json`-ben frissítsd a `version` mezőt
3. push a saját store repódba (webes feltöltés vagy git CLI)
4. Runtipiban: **Update App Stores**, majd az app **Update** gombja
5. Frissítés előtt érdemes mentést készíteni az érintett app adat mappájáról

## Hasznos linkek

- [mbentley/docker-omada-controller](https://github.com/mbentley/docker-omada-controller)
- [jellyfin/jellyfin](https://github.com/jellyfin/jellyfin) — hivatalos image, tagek
- [linuxserver/docker-transmission](https://github.com/linuxserver/docker-transmission) — image, tagek
- [Runtipi — Create your own app store](https://runtipi.io/docs/guides/create-your-own-app-store)
- [Runtipi — Creating apps](https://runtipi.io/docs/developers/creating-apps)
- [Runtipi — config.json reference](https://runtipi.io/docs/reference/config-json)
- [Runtipi — Customize app config](https://runtipi.io/docs/guides/customize-app-config) (portütközés esetén ide kell nyúlni telepítés után)
