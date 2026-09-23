# Met Multimodal Art Lab

Can you find a painting by describing something its catalog entry never mentions?

That's the starting question for this project. I'm using the Metropolitan Museum of Art's public collection to explore image search, style transfer, and the limits of machine-generated artwork descriptions.

## Current milestone: public-data ingestion

The first piece is a small data pipeline. It samples the Met's catalog, keeps records with public-domain images, and downloads a reproducible pilot collection. It caches progress so interrupted runs can resume, records image hashes, and writes a report of missing metadata and download failures.

The models come next. CLIP search, style transfer, and captioning are still planned; there are no model results to report yet.

The first live smoke test on September 23, 2026 found 502,816 catalog records and downloaded three eligible images (206,065 bytes total) without request failures. One of the three records had no culture value. Five offline checks passed. This verifies a small run, not collection-wide coverage.

Start with [WALKTHROUGH.md](WALKTHROUGH.md). Python 3.10+ is sufficient for this milestone; no packages, API key, GPU, or paid services are required.

```powershell
python met_pipeline.py --limit 25 --max-records 500
python -m unittest -v
```

The first command contacts the Met API and downloads images. `data/` is intentionally excluded from Git. An incomplete pilot returns a nonzero exit code and a report explaining failures. Repeated runs reuse cached records and images. The manifest represents the requested sample for the latest run, not every image retained on disk. Do not run simultaneous writers against the same data directory.

## Where this is going

**Search beyond keywords.** Use CLIP to search images with phrases such as "dogs wearing armor." Compare the results with a regular catalog search and manually score the top ten matches. A funny query isn't evidence that the model understands it.

**Work up to a larger collection.** Begin with 25 images, review them, then move to 1,000 and beyond. Track storage, processing time, and search latency as the collection grows. The small pilot is for checking the pipeline, not demonstrating big-data performance.

**Try style transfer.** Explore Dutch still lifes and Edo-period prints, starting with a pretrained baseline. Training a GAN is a later experiment, depending on the available images and compute.

**Test what captions get wrong.** Compare descriptions based only on an image with descriptions that also use catalog metadata. Dates, culture, and attribution need evidence. A fluent caption can still be wrong, and the catalog doesn't automatically provide the paired descriptions needed for fine-tuning.

## Data provenance and limitations

- Official API: https://metmuseum.github.io/
- Open Access dataset: https://github.com/metmuseum/openaccess
- Open Access policy: https://www.metmuseum.org/hubs/open-access
- Download only records with `isPublicDomain == true` and a nonempty image URL. Not every catalog record has an image or qualifies for this pipeline.
- Preserve object IDs, collection links, source URLs and SHA-256 hashes. Retain the cached inventory to reproduce selection; upstream metadata can change.
- This pilot samples a seeded shuffle of the full object inventory, then filters for eligible images. It represents that eligible subset, not all art history. Missing culture or dates must remain unknown, not be inferred as labels.
- The pipeline uses `/v1/objects`, not the deprecated `/v1/search` endpoint. The documented search migration does not change this inventory workflow.
- Code licensing and artwork rights are separate. This repository does not relicense the Met's assets. No affiliation with or endorsement by the Met is implied.
