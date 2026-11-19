# -*- coding: utf-8 -*-
"""UE 5.4 EDITOR ONLY: make Tokyo street walkable using triangle collision.

Open Level2_Tokyo, enable Python Editor Script Plugin, then Tools > Execute Python Script.
The actual .uasset changes happen ONLY when this is executed in UE Editor.
- Makes one backup copy of the ORIGINAL street mesh under /Game/NeoTokyo/CollisionBackup/
- Sets the original street StaticMesh to Use Complex Collision As Simple.
- Sets collision profile to BlockAll for matching loaded StaticMeshComponents.
- Saves modified mesh, but NOT the level; review and press Ctrl+S in Editor.
- Does not modify other meshes. No placement/scale/UV/material alterations.

Complex as Simple is appropriate as a temporary WALKABLE STATIC FLOOR fix,
not suitable for dynamic physics simulation; later replace with simple collision.
"""
import unreal

STREET_ASSET = "/Game/MyAsset/Tokyo/TokyoStreet_UVremapping_Streets_ground"
BACKUP = "/Game/NeoTokyo/CollisionBackup/TokyoStreet_UVremapping_Streets_ground_BEFORE_COLLISION"
EXPECTED_WORLD = "Level2_Tokyo"

assets = unreal.EditorAssetLibrary
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world or EXPECTED_WORLD not in world.get_path_name():
    raise RuntimeError("Open Level2_Tokyo in UE Editor before applying collision. World was: {}".format(
        world.get_path_name() if world else "None"))

mesh = assets.load_asset(STREET_ASSET)
if not isinstance(mesh, unreal.StaticMesh):
    raise RuntimeError("Could not load expected Tokyo street StaticMesh: " + STREET_ASSET)

# First create a persistent rollback copy, never overwrite an existing backup.
if not assets.does_asset_exist(BACKUP):
    if not assets.make_directory(BACKUP.rsplit("/", 1)[0]):
        unreal.log_warning("Collision backup folder may already exist.")
    if not assets.duplicate_asset(STREET_ASSET, BACKUP):
        raise RuntimeError("Backup duplication failed: no collision changes applied.")
    backup_asset = assets.load_asset(BACKUP)
    if not backup_asset or not assets.save_loaded_asset(backup_asset):
        raise RuntimeError("Could not persist backup. Aborting before modifying street.")
unreal.log("NeoTokyo: rollback copy available: " + BACKUP)

editor_mesh = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
if not editor_mesh:
    raise RuntimeError("StaticMeshEditorSubsystem is unavailable.")
# Set triangle/per-poly collision for static world geometry. Do not change geometry.
body_setup = mesh.get_editor_property("body_setup")
if not body_setup:
    raise RuntimeError("Street StaticMesh has no BodySetup. Stop and inspect the mesh in Static Mesh Editor.")
body_setup.set_editor_property("collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE)
if not assets.save_loaded_asset(mesh):
    raise RuntimeError("Unable to save street mesh collision settings.")

actor_system = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
updated = 0
for actor in actor_system.get_all_level_actors():
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        try:
            current = component.get_editor_property("static_mesh")
        except Exception:
            continue
        if current and current.get_path_name().split(".")[0] == STREET_ASSET:
            component.set_collision_profile_name("BlockAll")
            component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
            component.modify()
            updated += 1
            unreal.log("NeoTokyo: enabled BlockAll on {}".format(actor.get_actor_label()))

unreal.log("NeoTokyo collision applied. Street components updated: {}".format(updated))
unreal.log_warning("IMPORTANT: Ctrl+S to SAVE the LEVEL and external actors, then Play. If updated=0, load World Partition cells and rerun. The street asset's collision was saved.")
