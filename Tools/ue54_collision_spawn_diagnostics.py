# -*- coding: utf-8 -*-
"""Read-only collision and PlayerStart diagnostics for UE 5.4 Editor.

Execute with Level2_Tokyo open, outside PIE. Does not modify assets or levels.
Writes reports into Saved/NeoTokyoAudit (ignored by git).
Only loaded actors are represented; load relevant World Partition cells first.
"""
import csv
import json
import os
import unreal

WORLD_KEY = "Level2_Tokyo"
STREET_ASSET = "/Game/MyAsset/Tokyo/TokyoStreet_UVremapping_Streets_ground"


def safe_get(obj, name):
    try:
        val = obj.get_editor_property(name)
        return str(val)
    except Exception:
        return "unavailable"


def vector_data(vec):
    return {"x": round(vec.x, 3), "y": round(vec.y, 3), "z": round(vec.z, 3)}


def loc(actor):
    try:
        return vector_data(actor.get_actor_location())
    except Exception:
        return None


def mesh_path(comp):
    try:
        mesh = comp.get_editor_property("static_mesh")
        return mesh.get_path_name().split(".")[0] if mesh else ""
    except Exception:
        return ""


def component_report(comp):
    try:
        profile = str(comp.get_collision_profile_name())
    except Exception:
        profile = "unavailable"
    try:
        enabled = str(comp.get_collision_enabled())
    except Exception:
        enabled = safe_get(comp, "body_instance")
    try:
        pawn_response = str(comp.get_collision_response_to_channel(unreal.CollisionChannel.ECC_PAWN))
    except Exception:
        pawn_response = "unavailable"
    return {
        "component": comp.get_name(),
        "mesh": mesh_path(comp),
        "collision_profile": profile,
        "collision_enabled": enabled,
        "pawn_response": pawn_response,
        "visible": safe_get(comp, "visible"),
        "mobility": safe_get(comp, "mobility"),
    }


def main():
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    if not world or WORLD_KEY not in world.get_path_name():
        raise RuntimeError("Open Level2_Tokyo in Editor (not PIE). Current world: {}".format(
            world.get_path_name() if world else "none"))
    subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = subsystem.get_all_level_actors()
    starts, street, nearby = [], [], []
    for actor in actors:
        kind = actor.get_class().get_name()
        label = actor.get_actor_label()
        if isinstance(actor, unreal.PlayerStart) or "PlayerStart" in kind:
            starts.append({"actor": label, "class": kind, "location_cm": loc(actor)})
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            path = mesh_path(component)
            if path == STREET_ASSET:
                row = {"actor": label, "actor_location_cm": loc(actor),
                       "actor_scale": str(actor.get_actor_scale3d())}
                row.update(component_report(component))
                street.append(row)
            elif "street" in label.lower() or "ground" in label.lower() or "floor" in label.lower():
                row = {"actor": label, "actor_location_cm": loc(actor)}
                row.update(component_report(component))
                nearby.append(row)
    original = unreal.EditorAssetLibrary.load_asset(STREET_ASSET)
    mesh_settings = {"path": STREET_ASSET, "loadable": isinstance(original, unreal.StaticMesh)}
    if isinstance(original, unreal.StaticMesh):
        try:
            body = original.get_editor_property("body_setup")
            mesh_settings["body_setup_available"] = body is not None
            if body:
                mesh_settings["collision_trace_flag"] = safe_get(body, "collision_trace_flag")
        except Exception as e:
            mesh_settings["body_setup_error"] = str(e)
    report = {
        "world": world.get_path_name(),
        "scope": "Loaded actors only; World Partition unloaded cells excluded",
        "loaded_actor_count": len(actors),
        "player_starts": starts,
        "street_mesh_settings": mesh_settings,
        "matching_street_components": street,
        "other_ground_named_components": nearby[:150],
        "interpretation": {
            "no_street_components": "Load World Partition region or inspect alternate mesh/actor in Outliner.",
            "no_player_starts": "PIE may spawn at editor camera or use other gameplay logic.",
            "collision_still_fails": "Check active GameMode pawn capsule and spawn position in PIE."
        },
        "read_only": True
    }
    out = os.path.join(unreal.Paths.project_saved_dir(), "NeoTokyoAudit")
    os.makedirs(out, exist_ok=True)
    path = os.path.join(out, "collision_spawn_diagnostics.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    unreal.log("NeoTokyo DIAGNOSTIC REPORT: " + path)
    unreal.log("NeoTokyo: loaded actors={}, PlayerStarts={}, matching street components={}".format(
        len(actors), len(starts), len(street)))
    unreal.log("NeoTokyo: street mesh collision flag={}".format(
        mesh_settings.get("collision_trace_flag", "unavailable")))
    for ps in starts:
        unreal.log("NeoTokyo PlayerStart: {} @ {}".format(ps["actor"], ps["location_cm"]))
    for row in street:
        unreal.log("NeoTokyo Street: {} profile={} enabled={} pawn={}".format(
            row["actor"], row["collision_profile"], row["collision_enabled"], row["pawn_response"]))


if __name__ == "__main__":
    main()
