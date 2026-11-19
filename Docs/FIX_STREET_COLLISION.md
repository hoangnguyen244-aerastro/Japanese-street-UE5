# Level2_Tokyo: fixing player falling through street (UE 5.4)

A GitHub commit alone CANNOT change the binary collision stored in Unreal's .uasset or
the collision state in .umap/external actor packages. The Python file in this commit
applies the change **in the editor on your laptop**, after one explicit execution.

## One-time apply
1. In GitHub Desktop pull branch feature/neo-tokyo-optimization-foundation.
2. Close Play/PIE. Open Content/Level2_Tokyo.umap in UE5.4.4.
3. Enable Python Editor Script Plugin in Edit > Plugins if needed.
4. Tools > Execute Python Script > Tools/ue54_fix_street_collision.py.
5. Check Output Log: "Street components updated: N". N should be >=1.
6. Press Ctrl+S to save level/external actors. Close and reopen level to confirm.
7. Player Start/Spawn at Current Camera Location should be ABOVE the street.
8. Press Play and confirm the pawn/capsule remains on the street.
9. GitHub Desktop > Changes: review changed .uasset, .umap/external actor packages and new backup, then commit after testing.

## Technical decisions
- Original street mesh is backed up first in /Game/NeoTokyo/CollisionBackup/
- Original street gets CTF_USE_COMPLEX_AS_SIMPLE; accurate to an irregular static road but
  more expensive than simple collision, and unsuitable for physics-simulated moving bodies.
- Loaded street mesh components use BlockAll and Query and Physics.
- Not a final production optimization. Following collision validation, create segmented
  box/convex collision or Blocking Volumes based on real road shape.

## Troubleshooting
- "Updated: 0": street actor is in an unloaded World Partition cell, or uses a different mesh. Load cell and rerun; never guess actor positions.
- Player still falls: test from Player Start above road, inspect Pawn collision and component mobility, check Show > Collision in viewport.
- Script exception: send the full Output Log. No assumption that a GitHub commit alone resolved the issue.
