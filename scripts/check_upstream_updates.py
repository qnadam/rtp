#!/usr/bin/env python3
"""
Megnézi a megadott appok Docker Hub tag-jeit, és ha a jelenleg
a docker-compose.yml-ben rögzítettnél újabb (a megadott minta szerint
"valódi" verziót jelentő) tag-et talál, frissíti:

  - apps/<app>/docker-compose.yml   -> image tag
  - apps/<app>/config.json          -> "version" + "tipi_version" (+1) + "updated_at"

Ez a script CSAK a fájlokat módosítja a checkout-olt repóban; a git
commit/push a workflow YAML-ban történik, ha lett változás.

Ha módosítani akarod, mely appokat figyeli, vagy milyen tag-mintát fogad
el "valódi verziónak", az APPS lista az, amit szerkesztened kell.
"""

import json
import re
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

APPS = [
    {
        "id": "jellyfin",
        "namespace": "jellyfin",
        "repo": "jellyfin",
        # pl. "12.2", "12.11", "10.11.6" - de a bare "12", "latest", "unstable",
        # dátumozott build tag-ek és arch-specifikus tag-ek kizárva
        "tag_pattern": re.compile(r"^\d+\.\d+(\.\d+)?$"),
        "image_prefix": "jellyfin/jellyfin:",
        "compose_path": "apps/jellyfin/docker-compose.yml",
        "config_path": "apps/jellyfin/config.json",
        "strip_prefix": "",
    },
    {
        "id": "omada-controller",
        "namespace": "mbentley",
        "repo": "omada-controller",
        # csak az OpenJ9 build-eket figyeljük, mivel ezt használjuk
        "tag_pattern": re.compile(r"^\d+\.\d+(\.\d+)?-openj9$"),
        "image_prefix": "mbentley/omada-controller:",
        "compose_path": "apps/omada-controller/docker-compose.yml",
        "config_path": "apps/omada-controller/config.json",
        "strip_prefix": "",
    },
    {
        "id": "transmission",
        "namespace": "linuxserver",
        "repo": "transmission",
        # pl. "4.1.0-r0-ls328"
        "tag_pattern": re.compile(r"^\d+\.\d+\.\d+-r\d+-ls\d+$"),
        "image_prefix": "lscr.io/linuxserver/transmission:",
        "compose_path": "apps/transmission/docker-compose.yml",
        "config_path": "apps/transmission/config.json",
        "strip_prefix": "",
    },
    {
        "id": "meilisearch",
        "namespace": "getmeili",
        "repo": "meilisearch",
        # pl. "v1.12.8" - a config.json-ban a "v" prefix nélkül szerepel
        "tag_pattern": re.compile(r"^v\d+\.\d+\.\d+$"),
        "image_prefix": "getmeili/meilisearch:",
        "compose_path": "apps/meilisearch/docker-compose.yml",
        "config_path": "apps/meilisearch/config.json",
        "strip_prefix": "v",
    },
]

HEADERS = {"User-Agent": "runtipi-appstore-update-checker/1.0"}


def fetch_tags(namespace: str, repo: str, max_pages: int = 10) -> list[str]:
    """Docker Hub public tag lista lekérése (lapozva)."""
    tags: list[str] = []
    url = f"https://hub.docker.com/v2/repositories/{namespace}/{repo}/tags?page_size=100"

    for _ in range(max_pages):
        if not url:
            break
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)

        tags.extend(r["name"] for r in data.get("results", []))
        url = data.get("next")

    return tags


def version_key(tag: str) -> tuple[int, ...]:
    """A tag-ben szereplő számokból épít összehasonlítható tuple-t."""
    return tuple(int(n) for n in re.findall(r"\d+", tag))


def pick_latest(tags: list[str], pattern: re.Pattern) -> str | None:
    candidates = [t for t in tags if pattern.match(t)]
    if not candidates:
        return None
    return max(candidates, key=version_key)


def get_current_tag(compose_text: str, image_prefix: str) -> str | None:
    for line in compose_text.splitlines():
        line = line.strip()
        if line.startswith("image:") and image_prefix in line:
            value = line.split("image:", 1)[1].strip()
            if value.startswith(image_prefix):
                return value[len(image_prefix):]
    return None


def bump_compose(compose_text: str, image_prefix: str, old_tag: str, new_tag: str) -> str:
    old_image = f"{image_prefix}{old_tag}"
    new_image = f"{image_prefix}{new_tag}"
    return compose_text.replace(old_image, new_image)


def bump_config(config_path: Path, new_version_display: str) -> None:
    data = json.loads(config_path.read_text(encoding="utf-8"))
    data["version"] = new_version_display
    data["tipi_version"] = int(data.get("tipi_version", 1)) + 1
    data["updated_at"] = int(time.time() * 1000)
    config_path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    any_changes = False

    for app in APPS:
        compose_path = REPO_ROOT / app["compose_path"]
        config_path = REPO_ROOT / app["config_path"]

        if not compose_path.exists() or not config_path.exists():
            print(f"[{app['id']}] fájlok nem találhatók, kihagyva.")
            continue

        compose_text = compose_path.read_text(encoding="utf-8")
        current_tag = get_current_tag(compose_text, app["image_prefix"])

        if current_tag is None:
            print(f"[{app['id']}] jelenlegi tag nem állapítható meg, kihagyva.")
            continue

        try:
            tags = fetch_tags(app["namespace"], app["repo"])
        except Exception as exc:  # noqa: BLE001
            print(f"[{app['id']}] Docker Hub lekérés sikertelen: {exc}")
            continue

        latest_tag = pick_latest(tags, app["tag_pattern"])

        if latest_tag is None:
            print(f"[{app['id']}] nem található a mintának megfelelő tag.")
            continue

        if latest_tag == current_tag:
            print(f"[{app['id']}] már a legfrissebb ({current_tag}).")
            continue

        if version_key(latest_tag) <= version_key(current_tag):
            print(f"[{app['id']}] a talált tag ({latest_tag}) nem újabb, mint a jelenlegi ({current_tag}), kihagyva.")
            continue

        print(f"[{app['id']}] új verzió: {current_tag} -> {latest_tag}")

        new_compose_text = bump_compose(compose_text, app["image_prefix"], current_tag, latest_tag)
        compose_path.write_text(new_compose_text, encoding="utf-8")

        display_version = latest_tag
        if app["strip_prefix"] and display_version.startswith(app["strip_prefix"]):
            display_version = display_version[len(app["strip_prefix"]):]

        bump_config(config_path, display_version)
        any_changes = True

    if not any_changes:
        print("Nincs frissítendő app.")


if __name__ == "__main__":
    main()
