# Omada Controller (OpenJ9)

TP-Link Omada szoftveres SDN kontroller a [mbentley/docker-omada-controller](https://github.com/mbentley/docker-omada-controller) image **OpenJ9** (Eclipse OpenJ9 JVM) változatával. Ezzel a build-del a kontroller jelentősen kevesebb memóriát fogyaszt, mint a hivatalos TP-Link image, így kisebb VPS-en vagy homelab szerveren is kényelmesen elfér.

A kontrollerrel Omada eszközöket (access pointok, switchek, routerek) lehet felfedezni a hálózaton, adoptálni és egy központi felületről menedzselni.

## Fontos: host hálózati mód

Ez az app **host hálózati módban** fut, Traefik/reverse proxy integráció **nélkül**. Ennek oka, hogy az Omada eszközök adoptáláskor L2 broadcast/multicast csomagokkal keresik meg a kontrollert — ez bridge módban, NAT mögött megbízhatatlanul vagy egyáltalán nem működik.

Emiatt:

- a felület **közvetlenül a szerver IP-jén** érhető el, nem `alkalmazás.tedomained.hu` formában
- a portok nem konfigurálhatók a Runtipi telepítő űrlapján keresztül; ha ütköznek egy másik, szintén host módban futó konténerrel, a `docker-compose.yml`-t kell utólag módosítani ([Runtipi custom app config guide](https://runtipi.io/docs/guides/customize-app-config))

## Első belépés

1. Nyisd meg: `https://<szerver-ip>:8043`
2. Fogadd el a böngésző figyelmeztetését (a kontroller alapból önaláírt tanúsítványt használ)
3. Hozz létre admin felhasználót, majd hozd létre / állítsd be a site-ot

## Portok

| Port | Protokoll | Cél |
|---|---|---|
| 8088 | TCP | Admin felület, HTTP |
| 8043 | TCP | Admin felület, HTTPS |
| 8843 | TCP | Felhasználói portál, HTTPS |
| 19810 | UDP | Eszközfelfedezés |
| 27001 | UDP | Mobilapp-felfedezés |
| 29810–29817 | TCP/UDP | Eszközmenedzsment, adoptálás, firmware-frissítés |

## Mappák

| App adat mappa | Konténer mappa | Tartalom |
|---|---|---|
| `data/data` | `/opt/tplink/EAPController/data` | Adatbázis, kontroller állapota |
| `data/logs` | `/opt/tplink/EAPController/logs` | Naplófájlok |

## Beállítható mezők

- **Java max/min heap méret** — az OpenJ9 JVM heap korlátai. Kevés memóriájú gépen (1–2 GB RAM) érdemes a max heapet 512m-re csökkenteni.

## Frissítés

Az image tag (`6.2-openj9`) rögzített a `docker-compose.yml`-ben. Frissítéshez a saját app store repódban bumpold a tag-et és a `config.json` `version` mezőjét, push-old, majd a Runtipi felületén futtasd az "Update App Stores" és utána az app "Update" műveletét. Frissítés előtt érdemes biztonsági mentést készíteni a `data/data` mappáról.

## Forrás

[github.com/mbentley/docker-omada-controller](https://github.com/mbentley/docker-omada-controller)
