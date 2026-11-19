# -*- coding: utf-8 -*-
"""UE 5.4 Editor script: create *new* optimized texture asset variants.

No existing binary assets, level, or materials are altered. New copies are
created below /Game/NeoTokyo/OptimizedTextures, subject to explicit approval.
Start with --dry-run (default). To run from UE Python console:

exec(open(r"D:\PATH\TO\Japanese-street-UE5\Tools\ue54_make_optimized_variants.py", encoding="utf-8").read())

The script's APPLY flag below controls creation. Never enable while PI E is running.
"""
import unreal

# Review generated inventory and backup before changing this to True.
APPLY = False
SOURCE_ROOT = "/Game/MyAsset/Tokyo/Textures/"
DEST_ROOT = "/Game/NeoTokyo/OptimizedTextures/"
# Only oversized 4K+ textures, and only within Tokyo's original texture tree.
SOURCE_DIMENSION_THRESHOLD = 4096
TARGET_MAX_SIZE = 2048
MAX_NEW_ASSETS_PER_RUN = 10

asset_registry = unreal.AssetRegistryHelpers.get_asset_registry()
editor_assets = unreal.EditorAssetLibrary
registry_assets = asset_registry.get_assets_by_path(SOURCE_ROOT, recursive=True)
candidates = []

for data in registry_assets:
    source = str(data.package_name)
    asset = editor_assets.load_asset(source)
    if not isinstance(asset, unreal.Texture2D):
        continue
    try:
        width, height = asset.blueprint_get_size_x(), asset.blueprint_get_size_y()
    except Exception:
        unreal.log_warning("NeoTokyo: unable to read size for " + source)
        continue
    if max(width, height) < SOURCE_DIMENSION_THRESHOLD:
        continue
    candidates.append((source, int(width), int(height)))

unreal.log("NeoTokyo: {} potential oversized Tokyo textures".format(len(candidates)))
for source, width, height in candidates:
    unreal.log("  {}: {}x{}".format(source, width, height))

if not APPLY:
    unreal.log_warning("NeoTokyo: DRY-RUN only. Set APPLY=True after backup and review.")
else:
    created = 0
    for source, width, height in candidates:
        if created >= MAX_NEW_ASSETS_PER_RUN:
            break
        relative = source[len(SOURCE_ROOT):]
        target = DEST_ROOT + relative + "_2K"
        if editor_assets.does_asset_exist(target):
            unreal.log("NeoTokyo: skipped existing " + target)
            continue
        destination_folder = target.rpartition("/")[0]
        editor_assets.make_directory(destination_folder)
        if not editor_assets.duplicate_asset(source, target):
            unreal.log_warning("NeoTokyo: duplication failed: " + source)
            continue
        duplicate = editor_assets.load_asset(target)
        if not isinstance(duplicate, unreal.Texture2D):
            unreal.log_error("NeoTokyo: unexpected duplicated asset class: " + target)
            continue
        try:
            duplicate.set_editor_property("max_texture_size", TARGET_MAX_SIZE)
            editor_assets.save_loaded_asset(duplicate, only_if_is_dirty=True)
            created += 1
            unreal.log("NeoTokyo: created {} with max_texture_size {}".format(target, TARGET_MAX_SIZE))
        except Exception as exc:
            unreal.log_error("NeoTokyo: failed to set max texture size for {}: {}".format(target, exc))
    unreal.log("NeoTokyo: created {} variants. Existing material references NOT changed.".format(created))
