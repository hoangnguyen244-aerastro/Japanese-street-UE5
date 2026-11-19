# Sprint 03 — Changes introduced on GitHub

## Direct project config change
`Config/DefaultScalability.ini` has been added to this branch. It limits the
Texture Streaming pool to **1,200 MiB** for Unreal's **High** texture scalability
setting and disables motion blur in the High postprocess group. These are
conservative experiment defaults, **not** validated optimization results. The
original renderer defaults in `DefaultEngine.ini` remain intact. Compare GPU
timings and visuals with and without this override.

## Why not patch .uasset bytes via GitHub?
UE `.uasset`/`.umap` are serialized binary packages with reference graphs
and engine-version-sensitive data. Editing raw bytes without Unreal Editor
validation can corrupt the project. GitHub alone cannot execute the UE editor.

## Prepare actual new optimized binary assets
The optional `Tools/ue54_make_optimized_variants.py` script:
1. Locates Tokyo Texture2D assets that are >=4096 pixels on either dimension.
2. By default prints candidate files and **does not save anything**.
3. On setting `APPLY=True`, duplicates **up to 10** candidates into
   `/Game/NeoTokyo/OptimizedTextures/` and sets Max Texture Size to 2048.
4. Never rewrites the original textures or existing material references.

Before applying:
- Ensure a **complete backup**; inspect `Saved/Autosaves` before cleaning.
- Start the editor with `Level2_Tokyo` loaded.
- Enable `Python Editor Script Plugin`.
- Run the script from **Tools > Execute Python Script**.
- Inspect the Output Log candidate list; only then set `APPLY=True` and rerun.
- Inspect copies in Content Browser; verify visual quality and manually switch
  specific material instances to variants **in an Unreal working map**, not on
  the original map.
- The script creates local binary assets; commit them with GitHub Desktop once
  checked, then GitHub will contain the actual optimized asset variants.

## Evaluation criteria
- Baseline editor screenshot showed ~19.55 ms GPU and 4.52 ms Lumen Reflections
  at a street-level viewpoint. Those measurements are not packaged-build FPS.
- Measure `stat gpu`, `stat streaming`, and `profilegpu` for at least 2
  repeated passes before considering the variants an improvement.
- Source project must remain under **20 GiB**; target much lower if possible.

## Rollback
- For the config: revert the `Config/DefaultScalability.ini` commit.
- For generated variants: delete only the new assets in Unreal Content Browser,
  after verifying no new material depends on them. Do not delete the original
  textures or `Level2_Tokyo`.
