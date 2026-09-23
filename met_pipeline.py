"""Download a reproducible public-domain Met pilot using only Python's stdlib."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

API = "https://collectionapi.metmuseum.org/public/collection/v1"


def fetch(url, attempts=4):
    for attempt in range(attempts):
        time.sleep(0.25)
        try:
            request = Request(url, headers={"User-Agent": "met-multimodal-art-lab/0.1"})
            with urlopen(request, timeout=30) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as error:
            if isinstance(error, HTTPError) and error.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == attempts - 1:
                raise
            time.sleep(2 ** attempt)


def eligible(record):
    return record.get("isPublicDomain") is True and bool(record.get("primaryImageSmall") or record.get("primaryImage"))


def atomic_write(path, content):
    temporary = path.with_suffix(path.suffix + ".part")
    temporary.write_bytes(content)
    temporary.replace(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=25, help="Maximum usable images in this pilot")
    parser.add_argument("--max-records", type=int, default=500, help="Bound metadata requests per run")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    args = parser.parse_args()
    if args.limit < 1 or args.max_records < 1:
        parser.error("limits must be positive")
    root = args.data_dir
    for folder in (root, root / "records", root / "images"):
        folder.mkdir(parents=True, exist_ok=True)
    inventory = root / "object_ids.json"
    if not inventory.exists():
        atomic_write(inventory, fetch(API + "/objects"))
    ids = sorted(set(json.loads(inventory.read_text(encoding="utf-8"))["objectIDs"]))
    random.Random(args.seed).shuffle(ids)
    rows, failures = [], []
    for object_id in ids[:args.max_records]:
        try:
            cached = root / "records" / f"{object_id}.json"
            if not cached.exists():
                atomic_write(cached, fetch(f"{API}/objects/{object_id}"))
            record = json.loads(cached.read_text(encoding="utf-8"))
            if not eligible(record):
                continue
            url = record.get("primaryImageSmall") or record["primaryImage"]
            destination = root / "images" / f"{object_id}.jpg"
            if not destination.exists():
                image = fetch(url)
                if not image.startswith(b"\xff\xd8\xff"):
                    raise ValueError("Response is not a JPEG")
                atomic_write(destination, image)
            content = destination.read_bytes()
            if not content.startswith(b"\xff\xd8\xff"):
                raise ValueError("Cached file is not a JPEG; remove it and rerun")
            row = {key: record.get(key) for key in (
                "objectID", "title", "artistDisplayName", "culture", "period", "objectDate",
                "objectBeginDate", "objectEndDate", "medium", "dimensions", "department",
                "classification", "isPublicDomain", "objectURL")}
            row.update(image_url=url, image_path=f"images/{object_id}.jpg",
                       image_bytes=len(content), sha256=hashlib.sha256(content).hexdigest())
            rows.append(row)
            print(f"[{len(rows)}/{args.limit}] {object_id}: {record.get('title', '')}", flush=True)
            if len(rows) >= args.limit:
                break
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            failures.append({"objectID": object_id, "error": str(error)})
            print(f"Skipped {object_id}: {error}", flush=True)
    atomic_write(root / "manifest.jsonl", "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows).encode("utf-8"))
    report = {"source": API, "seed": args.seed, "inventory_count": len(ids),
              "inventory_sha256": hashlib.sha256(inventory.read_bytes()).hexdigest(),
              "requested_images": args.limit, "max_records": args.max_records,
              "downloaded_images": len(rows), "image_bytes": sum(r["image_bytes"] for r in rows),
              "missing_culture": sum(not r.get("culture") for r in rows), "failures": failures,
              "complete": len(rows) == args.limit}
    atomic_write(root / "report.json", json.dumps(report, indent=2).encode("utf-8"))
    print(json.dumps(report, indent=2))
    if len(rows) < args.limit:
        raise SystemExit("Pilot incomplete; inspect report.json and increase --max-records or retry.")


if __name__ == "__main__":
    main()
