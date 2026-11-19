# Neo Tokyo — AAA Hybrid Micro Scene

## Status
**Phase 0: baseline + safety tooling.** This branch does not alter any Unreal binary assets or the default game map.

Repository: `Japanese-street-UE5`; UE version declared in `L1.uproject`: 5.4.

## Goal
- Source project target: **2–5 GB initially**, hard cap **20 GB** (exclude engine installation and generated caches/renders).
- Playable: 1080p RTX 3060 Laptop 6 GB, test **45–60 FPS**; measure before claiming results.
- Cinematic: five shots, 60–90 seconds, offline render after memory tests.
- Keep `Content/MyAsset/Tokyo` intact until in-editor asset reference checks are complete.
- Prefer a compact street with one hero storefront, reusable geometry, wet asphalt, and carefully budgeted lighting.

## Confirmed repository starting points
- Primary candidate: `Content/Level2_Tokyo.umap`.
- Existing meshes: `Content/MyAsset/Tokyo/TokyoStreet_UVremapping_*.uasset`.
- Existing building material sets and textures: `Content/MyAsset/Tokyo/`.
- `Config/DefaultEngine.ini` points startup and game maps to FirstPersonMap. **Do not repoint until Level2_Tokyo has been opened and tested.**
- `Saved` and `Intermediate` are tracked in old commits; `.gitignore` prevents *new untracked* generated files, but does not untrack existing ones.

## Step-by-step release gates

### Gate 0 — Data safety
1. Clone and backup entire repository (including `Saved/Autosaves`) outside the working copy.
2. Open `L1.uproject` in installed UE 5.4.4 and verify the engine version.
3. Open `Level2_Tokyo`, save any recoverable autosave changes before cleaning generated folders.
4. Run Map Check; record output and screenshots.
5. Only after backup, remove generated directories from Git tracking in a **separate reviewed commit**.

### Gate 1 — Baseline capture
1. Set editor viewport 1920×1080; plug the laptop into power and select discrete GPU.
2. Measure PIE/Standalone using `stat fps`, `stat unit`, `stat gpu`, `stat streaming`, `profilegpu`.
3. Take five reproducible viewpoint screenshots: entrance, hero shop, signage cluster, wet street, vista.
4. Record GPU model/TGP, temperature, VRAM, CPU and GPU frame times, engine scalability settings.
5. Export asset listing: `python Tools/asset_budget_audit.py --project . --output AuditOutput`.

### Gate 2 — Non-destructive vertical slice
- Make a working map using Unreal Editor, e.g. `L_NeoTokyo_Hybrid`. Validate World Partition/external actors.
- New assets go under `Content/NeoTokyo/`; do not move imported `MyAsset` content with Windows Explorer.
- Add one wet asphalt material, one hero storefront, a few selective local lights, and localized Niagara rain.
- Benchmark after **each** significant lighting/VFX pass.

### Gate 3 — Gameplay and cinematic
- First-person explorer and three lightweight environmental interactions.
- Shared world; cinematic cameras/sequences and render quality overrides only where needed.
- Package Development build; test it separately from PIE.
- Test one short MRQ render before exporting 4K footage.

## Baseline resource policy
- 6 GB VRAM is the primary runtime constraint.
- Trial streaming pool: 1,800 MB, **not an unconditional preset**; validate `stat streaming`.
- Prefer 512–2,048 pixel textures according to screen coverage, with exceptions justified per hero asset.
- Keep high-cost dynamic shadow-casting lights in a small hero zone.
- Use a small number of material masters + instances, selective instancing, and no unnecessary per-actor Tick.
- Distinguish *on-disk project size*, *texture pool*, and *actual GPU allocation*.

## Change policy
No binary `.uasset`/`.umap` modifications, moving existing asset paths, deleting autosaves, or gameplay map switch until a UE Editor validation pass is complete.
