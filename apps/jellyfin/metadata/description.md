# Jellyfin (saját)

Ez a Runtipi app a **már meglévő, kézzel futtatott Jellyfin példányodat** hozza át Runtipi felügyelet alá — nem a Runtipi gyári, `linuxserver/jellyfin` alapú app store bejegyzését használja.

## Miért külön app a gyári helyett?

A gyári Runtipi Jellyfin app más image-csomagolást (linuxserver, PUID/PGID, más mappaszerkezet) használ. Mivel a meglévő adataid (könyvtár, felhasználók, nézettségi előzmények) a hivatalos `jellyfin/jellyfin` image mappaszerkezetéhez lettek létrehozva, az egyszerű és biztonságos út az, ha ugyanazt az image-et és ugyanazokat a host mappákat használjuk tovább — nincs adatmozgatás, nincs konverzió.

## Mappák

| Host mappa | Konténer mappa | Tartalom |
|---|---|---|
| `/home/a/jellyfin/config` | `/config` | Adatbázis, felhasználók, beállítások |
| `/home/a/jellyfin/cache` | `/cache` | Transzkódolási / képcache |
| `/mnt/nas/pk` | `/data` | Média könyvtár (SMB mount) |

## Port

A telepítéskor megadott port (`APP_PORT`) közvetlenül a konténer 8096-os portjára van kiadva (`ports: - APP_PORT:8096`), nincs Traefik/domain integráció — ugyanúgy érhető el kívülről, mint eddig a manuálisan indított konténer (DDNS + port forward).

## Verzió rögzítve

A `docker-compose.yml`-ben a `jellyfin/jellyfin:10.11.6` tag van rögzítve, hogy ne induljon automatikus, esetlegesen visszavonhatatlan adatbázis-migrációt okozó frissítés a háttérben. Frissítéshez tudatosan kell bumpolni a tagot.

## Fontos

Telepítés előtt a régi, kézzel indított `jellyfin` nevű konténert le kell állítani és törölni (`docker rm jellyfin`) — a névütközés miatt a Runtipi telepítése különben elszáll. A host mappákat (`config`, `cache`, `/mnt/nas/pk`) **nem** kell törölni, azokra épp szükség van.

## Forrás

[github.com/jellyfin/jellyfin](https://github.com/jellyfin/jellyfin)
