# Lesson 1: build and understand the dataset

## 1. Get the code

After this repository is published:

```powershell
git clone https://github.com/sepehrfathi43/met-multimodal-art-lab.git
cd met-multimodal-art-lab
python --version
```

If your Windows Python launcher is `py`, use `py` instead of `python` throughout. Use Python 3.10 or later. The first milestone has no external dependencies.

## 2. Run a small pilot

```powershell
python met_pipeline.py --limit 25 --max-records 500
```

Read the script from top to bottom:

1. `fetch` makes HTTP requests with timeouts, a conservative pause, and retry/backoff for transient errors.
2. `/objects` provides official object IDs. Caching this inventory fixes the population for repeat runs.
3. A seeded shuffle establishes a repeatable candidate order.
4. Object records are fetched and cached individually.
5. `eligible` requires a public-domain flag and an image URL.
6. JPEG images are saved atomically and hashed. Smaller source images keep the pilot manageable; later training may need higher resolution.
7. A JSON Lines manifest links images to catalog metadata, and a JSON report summarizes the run.

`--limit` counts eligible images, whereas `--max-records` bounds how many candidate records are inspected. Many objects have no eligible image. If the requested image count is not reached, inspect failures first, then rerun with a larger candidate budget.

## 3. Inspect your results

```powershell
Get-Content data/report.json
Get-Content data/manifest.jsonl -TotalCount 3
```

Open several files in `data/images/` and compare them with the corresponding catalog links. Answer these questions before moving on:

- How many catalog objects were available in the inventory?
- Did the run reach 25 images? How many failures occurred?
- How many sampled records have no culture value?
- How many bytes do the downloaded images occupy?
- Which fields describe visual content, and which require historical evidence?

Keep missing values intact. Do not substitute a guessed culture or era.

## 4. Verify the data contract

```powershell
python -m unittest -v
```

These offline checks verify rights/image eligibility and atomic file replacement. They do not prove API availability, JPEG decodability, historical accuracy, or model performance.

## 5. Next lesson

Once we review the pilot report together, add image decoding checks and a pretrained CLIP embedding pipeline. Start with a small collection, learn how image/text cosine similarity works, and manually judge the top results before scaling. Do not download the full image collection yet.
