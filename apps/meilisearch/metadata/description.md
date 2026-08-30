# Meilisearch

Gyors, kis erőforrásigényű keresőmotor. Ebben a setupban elsősorban azért kell, hogy a **Linkwarden** ki tudja szolgálni a haladó (advanced) keresést a mentett linkek között.

Önmagában nincs felhasználói felülete/nem kell hozzá domain — más Runtipi appok a közös Docker hálózaton (`tipi_main_network`) keresztül érik el, a konténer neve alapján: `http://meilisearch:7700`.

## Master Key

A telepítő űrlapon alapértelmezetten ki van töltve egy véletlen kulccsal. **Ezt a pontos értéket másold át** annak az appnak (pl. Linkwarden) a `MEILI_MASTER_KEY` beállításába is, amelyik használni fogja — a két oldalon egyeznie kell, különben a hitelesítés elutasítja a kéréseket.

## Linkwarden bekötése (ha a hivatalos Runtipi store-ból van telepítve)

A hivatalos Linkwarden app store bejegyzés nem tartalmazza a Meilisearch env változókat, ezért a Runtipi "customize app config" mechanizmusával kell hozzáadni, a hivatalos bejegyzés módosítása nélkül:

```bash
docker exec runtipi mkdir -p /data/user-config/migrated/linkwarden
docker exec runtipi sh -c 'cat > /data/user-config/migrated/linkwarden/app.env << EOF
MEILI_HOST=http://meilisearch:7700
MEILI_MASTER_KEY=<ide-a-meilisearch-master-key-erteke>
EOF'
```

Utána a Linkwarden appot újra kell indítani, hogy felvegye az új env változókat (Runtipi felületen Stop, majd Start — vagy CLI-vel: `docker exec runtipi ./runtipi-cli app stop linkwarden:migrated && docker exec runtipi ./runtipi-cli app start linkwarden:migrated`).

## Meglévő linkek indexelése

Az újonnan hozzáadott/módosított linkeket a Linkwarden automatikusan indexeli, amint van elérhető Meilisearch. A Meilisearch bekapcsolása **előtt** felvitt, régebbi linkeknél is ennek automatikusan meg kellene történnie a háttérben — ha pár óra után sem jelennek meg keresésben, egy ismert workaround (Linkwarden Postgres adatbázisában) az `indexVersion` mező nullázása, ami újra kényszeríti az indexelést:

```sql
UPDATE "Link" SET "indexVersion" = NULL;
```

## Mappa

| App adat mappa | Konténer mappa | Tartalom |
|---|---|---|
| `data/meili_data` | `/meili_data` | Keresési index |

## Forrás

[github.com/meilisearch/meilisearch](https://github.com/meilisearch/meilisearch)
