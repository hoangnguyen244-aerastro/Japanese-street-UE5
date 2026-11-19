# Sprint 02 — GPU / Lighting Audit (UE 5.4.4)

## Scope and safety
- Read-only Unreal Editor audit; output is written into `Saved/NeoTokyoAudit/`.
- Does **not** modify, rename or save `.umap`/`.uasset` files.
- `Level2_Tokyo` uses World Partition: the audit lists only **currently loaded** actors. Load required cells in the World Partition editor if you need full coverage.
- This is not a performance benchmark. GPU timings must be gathered from PIE/Standalone separately.

## Run the level audit
1. GitHub Desktop: **Fetch origin**, then **Pull origin** on `feature/neo-tokyo-optimization-foundation`.
2. In UE5.4: Edit > Plugins > enable **Python Editor Script Plugin**; restart Editor if prompted.
3. Open `Content/Level2_Tokyo.umap`. Do not press Play.
4. In UE: **Tools > Execute Python Script**, select `Tools/ue54_level_audit.py` from the repository.
5. Look for `NeoTokyo audit complete` in Output Log.
6. Collect (from `Saved/NeoTokyoAudit/`):
   - `level_summary.json` — world/actor counts
   - `light_actors.csv` — light components, intensity, shadow settings, attenuation
   - `static_mesh_actors.csv` — currently loaded mesh references and material paths
7. Share reports for a lighting/mesh improvement plan. Audit does not automatically change assets.

## A/B GPU test — same camera, same conditions
Do this after closing asset audit. Compare **GPU ms**, not capped FPS.

1. Open Level2_Tokyo, set the camera at a reproducible street-level viewpoint.
2. Capture baseline screenshot after rendering stabilizes. Use `stat unit`, `stat gpu`; note viewport resolution and screen percentage.
3. Enter `r.Lumen.Reflections.Allow 0`, wait 10–20 seconds, capture GPU timing and visual difference.
4. Restore using `r.Lumen.Reflections.Allow 1` (or restart Editor if uncertain).
5. Repeat at the hero-signage area; do not change more than one setting per experiment.
6. Save screenshots and your readings **outside Git** (e.g. `Saved/NeoTokyoAudit/`).

| Test | Resolution | Baseline GPU ms | No Lumen reflections GPU ms | Visual difference |
|---|---|---:|---:|---|
| Street | fill in | fill in | fill in | fill in |
| Hero signage | fill in | fill in | fill in | fill in |

## Interpretation gates
- If disabling Lumen reflections saves significant GPU time, first optimize reflected materials/scene and Lumen quality, instead of permanently disabling reflections.
- If lighting dominates, inspect `light_actors.csv` and reduce overlapping shadow-casting hero lights **after** a working-map backup.
- Until a baseline exists, do not globally enable Nanite, rewrite asset references, or raise texture pool.
- Target small scene, **source project <20 GiB**, 1080p playable, offline cinematic separately.
