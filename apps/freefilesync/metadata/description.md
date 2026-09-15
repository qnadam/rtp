# FreeFileSync

Grafikus, webes feluleten (noVNC-n keresztul, bongeszobol) hasznalhato
FreeFileSync a [jlesage/docker-freefilesync](https://github.com/jlesage/docker-freefilesync)
konteneresitett buildjeben.

## Mire jo itt

- Nem futtat automatikus, sajat tarolasi formatumu (dedup-olt) mentest:
  sima fajlmasolast/tukrozest vegez, a celon (pl. Synology NAS-on, SFTP-n
  keresztul) kozvetlenul bongeszheto fajlok maradnak.
- Inditas elott mindig megmutatja a forras es a cel osszehasonlitasat
  (mit hozunk letre, mit irunk felul, mit torolnenk), es csak jovahagyas
  utan indul a tenyleges szinkron/mentes.
- A cel (pl. Synology) SFTP/FTP-n kozvetlenul a FreeFileSync feluleterol
  konfigauralhato, nem kell host-szintu mountolas hozza.

## Beallitas elso inditas utan

1. Nyisd meg az app webes feluletet (noVNC asztal a bongeszoben).
2. FreeFileSync-ben allitsd be a forras oldalt (`/storage` - ide van
   mountolva a Debian gep tartalma) es a cel oldalt (Synology, SFTP
   kapcsolatkent, pl. `sftp://user@synology-host/utvonal`, vagy
   Tailscale-en keresztuli cim).
3. Futtasd le a "Compare"-t, nezd at a lista, csak utana "Synchronize".
4. Ha ismetlodo, utemezett mentest szeretnel, mentsd el a jobot
   `.ffs_batch` fajlkent a `/config` ala, es allitsd be a
   `FFS_SCHEDULED_BATCH_JOB_<ID>_NAME` / `..._CRON` kornyezeti
   valtozokat a docker-compose.yml-ben.

## Megjegyzes

A `/storage` alatti utvonal a docker-compose.yml-ben cserelendo a
tenyleges host-oldali mount pontra, ahol a docker gep eleri a Debian
gep tartalmat.
