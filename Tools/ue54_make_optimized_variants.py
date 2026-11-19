# -*- coding: utf-8 -*-
"""UE 5.4 Editor: inspect selected Tokyo textures and optionally make safe copies.

Run in Unreal Editor via Tools > Execute Python Script (Python Editor Script Plugin).
Dry run by default; writes no assets until APPLY=True.
Only duplicates explicitly allowlisted textures, never updates original references.
"""
import unreal

APPLY = False  # Leave False for first run. Requires prior backup for True.
TARGET_MAX_SIZE = 2048
MAX_NEW_ASSETS_PER_RUN = 3
DEST_ROOT = "/Game/NeoTokyo/OptimizedTextures"

# Based on actual on-disk asset_inventory.csv; byte size does NOT reveal resolution,
# texture quality, current streaming residency, or whether a texture is on-screen.
# Street and B7 are hero candidates: audit only; do not downgrade automatically.
CANDIDATES = [
    ("B5/Building_05_Building5_mat_Normal", "review", 13086704),
    ("B7/Building_07_Building7_mat_BaseColor", "review", 6492206),
    ("B2/Building_02_04_10_Building2_mat_BaseColor", "allow", 5411916),
    ("Street/Street_Car_Signal_Streets_groundMat_Normal", "review", 5090918),
    ("B3/Building_01_03_08_Building3_mat_Normal", "allow", 5036549),
    ("B5/Building_05_Building5_mat_BaseColor", "review", 4746711),
    ("B4/Building_02_04_10_Building4_mat_2_Normal", "allow", 4086586),
    ("B8/Building_01_03_08_Building8_mat_Normal", "allow", 4082068),
]

SOURCE_ROOT = "/Game/MyAsset/Tokyo/Textures"
assets = unreal.EditorAssetLibrary
selected = []
unreal.log("NeoTokyo: texture priority audit (safe/explicit allowlist)")
for relative, policy, disk_bytes in CANDIDATES:
    source = SOURCE_ROOT + "/" + relative
    texture = assets.load_asset(source)
    if not isinstance(texture, unreal.Texture2D):
        unreal.log_warning("MISSING/NOT TEXTURE2D: " + source)
        continue
    try:
        width = int(texture.blueprint_get_size_x())
        height = int(texture.blueprint_get_size_y())
    except Exception as exc:
        unreal.log_warning("SIZE UNAVAILABLE {}: {}".format(source, exc))
        continue
    try:
        current_max = texture.get_editor_property("max_texture_size")
    except Exception:
        current_max = "unknown"
    unreal.log("{} | {}x{} | existing_max={} | {:.2f}MiB disk | {}".format(
        policy.upper(), width, height, current_max,
        disk_bytes / (1024.0 * 1024.0), source))
    # Only permitted, verified oversized textures; keep critical hero assets.
    if policy == "allow" and max(width, height) > TARGET_MAX_SIZE:
        selected.append((source, relative))

unreal.log("NeoTokyo: {} approved candidate(s) with dimension > {}px".format(
    len(selected), TARGET_MAX_SIZE))
if not APPLY:
    unreal.log_warning("NeoTokyo DRY-RUN: NO ASSETS MODIFIED. Backup + inspect output before APPLY=True.")
else:
    created = 0
    for source, relative in selected[:MAX_NEW_ASSETS_PER_RUN]:
        # Keep original subfolders to avoid collisions.
        target = DEST_ROOT + "/" + relative + "_2K"
        if assets.does_asset_exist(target):
            unreal.log("SKIP already exists: " + target)
            continue
        assets.make_directory(target.rsplit("/", 1)[0])
        if not assets.duplicate_asset(source, target):
            unreal.log_error("Duplication failed: " + source)
            continue
        duplicate = assets.load_asset(target)
        if not isinstance(duplicate, unreal.Texture2D):
            unreal.log_error("Unexpected duplicated class: " + target)
            continue
        try:
            duplicate.set_editor_property("max_texture_size", TARGET_MAX_SIZE)
            assets.save_loaded_asset(duplicate)
            created += 1
            unreal.log("CREATED optimized copy: " + target)
        except Exception as exc:
            unreal.log_error("FAILED configuring {}: {}".format(target, exc))
    unreal.log("Created {} copies. Existing scene and materials unchanged.".format(created))
