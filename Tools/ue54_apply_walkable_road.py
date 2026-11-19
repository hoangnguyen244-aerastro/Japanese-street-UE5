# -*- coding: utf-8 -*-
"""Temporary UE5.4 Level2_Tokyo road and spawn repair. Run inside UE Editor, not PIE.

Uses an Engine Cube simple collider on a sufficiently FLAT road. Logs an original
PlayerStart restore record first. Does not change the original street mesh asset.
Does not save the level automatically; inspect, then Ctrl+S and Play.
"""
import json
import os
import unreal

ROAD = "/Game/MyAsset/Tokyo/TokyoStreet_UVremapping_Streets_ground"
LABEL = "NT_TEMP_WalkableRoadCollision"
actor_api = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not world or "Level2_Tokyo" not in world.get_path_name():
    raise RuntimeError("Open Level2_Tokyo outside PIE before running.")
actors = actor_api.get_all_level_actors()
road_actors = []
starts = []
for actor in actors:
    if actor.get_actor_label() == LABEL:
        raise RuntimeError("Temporary collision floor already exists. Stop to avoid duplicates.")
    if isinstance(actor, unreal.PlayerStart):
        starts.append(actor)
    for component in actor.get_components_by_class(unreal.StaticMeshComponent):
        mesh = component.get_editor_property("static_mesh")
        if mesh and mesh.get_path_name().split(".")[0] == ROAD:
            road_actors.append((actor, component))

if len(road_actors) != 1 or len(starts) != 1:
    raise RuntimeError("Need one LOADED road and one PlayerStart; found road={}, start={}. Check World Partition.".format(
        len(road_actors), len(starts)))
road_actor, road_component = road_actors[0]
player_start = starts[0]
center, half = road_actor.get_actor_bounds(False)
if min(half.x, half.y) < 100 or half.z > 120:
    raise RuntimeError("Street bounding box unsuitable for a temporary flat collider. Half extents cm: {}".format(half))
cube = unreal.EditorAssetLibrary.load_asset("/Engine/BasicShapes/Cube.Cube")
if not isinstance(cube, unreal.StaticMesh):
    raise RuntimeError("Engine cube mesh not available. No scene changes made.")

out = os.path.join(unreal.Paths.project_saved_dir(), "NeoTokyoAudit")
os.makedirs(out, exist_ok=True)
restore = os.path.join(out, "walkable_road_restore.json")
if os.path.exists(restore):
    raise RuntimeError("Restore record already exists; review before rerun: " + restore)
old_pos = player_start.get_actor_location()
with open(restore, "w", encoding="utf-8") as f:
    json.dump({"player_start_original_xyz_cm": [old_pos.x, old_pos.y, old_pos.z],
               "road_actor": road_actor.get_actor_label(),
               "road_half_extents_cm": [half.x, half.y, half.z],
               "temporary_actor_label": LABEL}, f, indent=2)

top = center.z + half.z
floor_thickness = 20.0
floor_actor = actor_api.spawn_actor_from_class(
    unreal.StaticMeshActor,
    unreal.Vector(center.x, center.y, top - floor_thickness / 2))
if not floor_actor:
    raise RuntimeError("Could not spawn floor actor; see Editor Output Log.")
floor_actor.set_actor_label(LABEL)
comp = floor_actor.get_component_by_class(unreal.StaticMeshComponent)
comp.set_static_mesh(cube)
floor_actor.set_actor_scale3d(
    unreal.Vector(2 * half.x / 100.0, 2 * half.y / 100.0, floor_thickness / 100.0))
comp.set_collision_profile_name("BlockAll")
comp.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
comp.set_editor_property("cast_shadow", False)
floor_actor.set_actor_hidden_in_game(True)

road_component.set_collision_profile_name("BlockAll")
road_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
player_start.set_actor_location(unreal.Vector(center.x, center.y, top + 180), False, False)
unreal.log("NeoTokyo: created TEMP flat collider: " + LABEL)
unreal.log("NeoTokyo: moved PlayerStart above road: {}".format(player_start.get_actor_location()))
unreal.log("NeoTokyo: restore position saved: " + restore)
unreal.log_warning("INSPECT position of temporary floor, then Ctrl+S and Play. Temporary flat floor may cover non-road areas and is NOT production collision.")
