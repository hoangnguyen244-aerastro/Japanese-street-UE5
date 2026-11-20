# -*- coding: utf-8 -*-
"""UE5.4 editor one-shot: controlled PlayerStart collision test platform.

Run when Level2_Tokyo open, PIE stopped. Adds one 6x6m collision platform
centered on PlayerStart XY, with platform top 140 cm below PlayerStart Z.
This is DIAGNOSTIC ONLY; no original Tokyo asset is modified and no level saved.
Before Save verify the platform is beneath PlayerStart (may intersect scenery).
"""
import unreal
import os
import json

LABEL = "NT_DIAGNOSTIC_SPAWN_PLATFORM"
PLATFORM_WIDTH_CM = 600.0
PLATFORM_THICKNESS_CM = 30.0
DROP_DISTANCE_CM = 140.0
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world is None or "Level2_Tokyo" not in world.get_path_name():
    raise RuntimeError("Open Level2_Tokyo in Unreal Editor, outside PIE.")
actor_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = actor_api.get_all_level_actors()
if any(a.get_actor_label() == LABEL for a in actors):
    raise RuntimeError("Diagnostic platform already exists; inspect it instead of duplicating.")
starts = [a for a in actors if isinstance(a, unreal.PlayerStart)]
if len(starts) != 1:
    raise RuntimeError("Expected exactly one loaded PlayerStart; found {}. No changes made.".format(len(starts)))
p = starts[0].get_actor_location()
cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
if not isinstance(cube, unreal.StaticMesh):
    raise RuntimeError("Engine Cube mesh unavailable; no changes made.")
top = p.z - DROP_DISTANCE_CM
actor = actor_api.spawn_actor_from_class(
    unreal.StaticMeshActor, unreal.Vector(p.x, p.y, top - PLATFORM_THICKNESS_CM / 2))
if actor is None:
    raise RuntimeError("Could not spawn diagnostic platform.")
actor.set_actor_label(LABEL)
comp = actor.get_component_by_class(unreal.StaticMeshComponent)
comp.set_static_mesh(cube)
actor.set_actor_scale3d(unreal.Vector(
    PLATFORM_WIDTH_CM / 100.0, PLATFORM_WIDTH_CM / 100.0,
    PLATFORM_THICKNESS_CM / 100.0))
comp.set_collision_profile_name("BlockAll")
comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
# Keep visually visible during test so position is obvious.
comp.set_editor_property("cast_shadow", False)

log_dir = os.path.join(unreal.Paths.project_saved_dir(), "NeoTokyoAudit")
os.makedirs(log_dir, exist_ok=True)
path = os.path.join(log_dir, "spawn_platform_test.json")
with open(path, "w", encoding="utf-8") as f:
    json.dump({
        "platform_actor": LABEL,
        "player_start_xyz_cm": [p.x,p.y,p.z],
        "platform_top_z_cm": top,
        "size_xy_cm": PLATFORM_WIDTH_CM,
        "note": "Not production collision. Remove the actor after test."
    }, f, indent=2)
unreal.log("NeoTokyo: SPAWN PLATFORM TEST CREATED: " + LABEL)
unreal.log("NeoTokyo: PlayerStart at {} and platform top z={:.2f}cm".format(p, top))
unreal.log_warning("Check placement in Editor; temporarily select Spawn Player At > Default Player Start before PIE. Do not commit this diagnostic actor as production geometry.")
