# Transmission (saját)

A már meglévő, kézzel futtatott Transmission példányt hozza át Runtipi felügyelet alá, változatlan konfigurációval — nincs adatmozgatás, nincs port- vagy mappa-módosítás.

## Portok

| Port | Protokoll | Cél |
|---|---|---|
| 9091 | TCP | Web UI |
| 34567 | TCP + UDP | Peer port (bejövő torrent kapcsolatok) |

A `34567`-es peer port szándékosan **fix**, nem a Runtipi telepítő-portválasztóján keresztül megy, mert a routeren erre a konkrét portra van beállítva a port forward. Ha ezt megváltoztatod, a routeren is módosítanod kell.

## Mappák

| Host mappa | Konténer mappa | Tartalom |
|---|---|---|
| `/home/a/transmission/config` | `/config` | Beállítások, torrent állapotok |
| `/home/a/transmission/incomplete` | `/incomplete` | Félkész letöltések |
| `/mnt/nas/pk` | `/downloads` | Kész letöltések — ugyanaz a NAS mount, amit a Jellyfin is használ médiakönyvtárként |

## Fontos telepítés előtt

A régi, kézzel indított `transmission` nevű konténert állítsd le és távolítsd el, különben névütközés miatt a telepítés `exit code 1`-gyel elszáll. A host mappákat (`config`, `incomplete`, `/mnt/nas/pk`) **ne** töröld:

```bash
docker stop transmission
docker rm transmission
```

## Verzió rögzítve

A `docker-compose.yml`-ben a `lscr.io/linuxserver/transmission:4.1.0-r0-ls328` tag van rögzítve a jelenleg futó verzió alapján, hogy ne fusson le automatikus frissítés a háttérben.

## Forrás

[github.com/linuxserver/docker-transmission](https://github.com/linuxserver/docker-transmission)
