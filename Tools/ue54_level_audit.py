# -*- coding: utf-8 -*-
"""UE 5.4 editor-only, read-only audit of the currently open level.

Usage: Enable 'Python Editor Script Plugin', open Level2_Tokyo, then use
Tools > Execute Python Script and select this file.
Writes JSON + CSV to Saved/NeoTokyoAudit only. Does NOT modify UE assets.
Only currently loaded actors are listed (World Partition cells may be unloaded).
"""
import csv
import json
import os
from collections import Counter

import unreal


def prop(obj, name):
    try:
        value = obj.get_editor_property(name)
        if isinstance(value, (int, float, str, bool)) or value is None:
            return value
        return str(value)
    except Exception:
        return None


def asset_path(obj):
    try:
        return obj.get_path_name() if obj else None
    except Exception:
        return None


def actor_name(actor):
    try:
        return actor.get_actor_label()
    except Exception:
        return actor.get_name()


def main():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    if actor_subsystem is None:
        raise RuntimeError("EditorActorSubsystem unavailable. Run inside Unreal Editor.")
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    level_path = world.get_path_name() if world else "unknown"
    if "Level2_Tokyo" not in level_path:
        unreal.log_warning(
            "NeoTokyo audit: current world is not Level2_Tokyo: " + level_path
        )
    actors = actor_subsystem.get_all_level_actors()
    light_rows = []
    mesh_rows = []
    classes = Counter()
    for actor in actors:
        name = actor_name(actor)
        classes[actor.get_class().get_name()] += 1
        for component in actor.get_components_by_class(unreal.LightComponentBase):
            light_rows.append({
                "actor": name,
                "actor_class": actor.get_class().get_name(),
                "component": component.get_name(),
                "component_class": component.get_class().get_name(),
                "intensity": prop(component, "intensity"),
                "attenuation_radius": prop(component, "attenuation_radius"),
                "cast_shadows": prop(component, "cast_shadows"),
                "visible": prop(component, "visible"),
                "mobility": prop(component, "mobility"),
            })
        for component in actor.get_components_by_class(unreal.StaticMeshComponent):
            try:
                mesh = component.get_editor_property("static_mesh")
            except Exception:
                mesh = None
            try:
                materials = [
                    asset_path(component.get_material(i))
                    for i in range(component.get_num_materials())
                ]
            except Exception:
                materials = []
            mesh_rows.append({
                "actor": name,
                "component": component.get_name(),
                "mesh": asset_path(mesh),
                "materials": ";".join(x or "" for x in materials),
                "cast_shadows": prop(component, "cast_shadow"),
                "mobility": prop(component, "mobility"),
            })

    base = unreal.Paths.project_saved_dir()
    output_dir = os.path.join(base, "NeoTokyoAudit")
    os.makedirs(output_dir, exist_ok=True)

    def write_csv(filename, rows, columns):
        with open(os.path.join(output_dir, filename), "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

    write_csv("light_actors.csv", light_rows, [
        "actor", "actor_class", "component", "component_class",
        "intensity", "attenuation_radius", "cast_shadows", "visible", "mobility"
    ])
    write_csv("static_mesh_actors.csv", mesh_rows, [
        "actor", "component", "mesh", "materials", "cast_shadows", "mobility"
    ])
    summary = {
        "world": level_path,
        "loaded_actor_count": len(actors),
        "loaded_light_component_count": len(light_rows),
        "loaded_static_mesh_component_count": len(mesh_rows),
        "actors_by_class": dict(classes.most_common()),
        "scope_note": "Loaded editor actors only. World Partition unloaded cells are excluded.",
        "read_only": True,
    }
    with open(os.path.join(output_dir, "level_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    unreal.log("NeoTokyo audit complete: " + output_dir)
    unreal.log("Lights: {}, static meshes: {}".format(len(light_rows), len(mesh_rows)))


if __name__ == "__main__":
    main()
