# Level2_Tokyo temporary collision repair (UE 5.4.4)

## Verified from committed Editor log
- Python diagnostic executed, with 1 loaded street component and 1 PlayerStart.
- Street component: BlockAll / Query and Physics / Pawn Block.
- StaticMesh collision trace flag reported CTF_USE_DEFAULT; this alone does not prove that its simple collision geometry exists.
- PlayerStart: (900, 850, 92.013) cm.
- PIE log warned: FindPlayerStart: PATHS NOT DEFINED or NO PLAYERSTART with positive rating.
- The diagnostics JSON was mistakenly imported as a DataTable and committed as Content/collision_spawn_diagnostics.uasset. It is not a collision repair.

## Apply a temporary collision platform, outside PIE
1. Back up Level2_Tokyo and relevant external-actor packages.
2. Pull feature/neo-tokyo-optimization-foundation in GitHub Desktop.
3. Open L1.uproject in UE5.4.4, open Level2_Tokyo and load its road's World Partition cell.
4. Enable Python Editor Script Plugin if necessary.
5. Tools > Execute Python Script > Tools/ue54_apply_walkable_road.py.
6. Check Output Log. The script requires exactly 1 road component and 1 PlayerStart.
7. Inspect the new actor labelled NT_TEMP_WalkableRoadCollision in the Outliner. It uses an Engine Cube with BlockAll, hidden in game.
8. Confirm the collider is actually over the walkable road (not over other geometry). Save the level with Ctrl+S only if its placement is correct.
9. Press Play to check whether the character stands on the platform.

## Important limitations
- This is a temporary *flat* box collider for diagnostics, not final AAA collision.
- If the road bounds are irregular or tall, the script fails before making changes.
- The asset is not modified directly by GitHub. The script must execute inside UE on the user's computer, where changes to the world become binary packages.
- The temporary collider may cover space outside an irregular road: if this happens, DO NOT save it.
- The restore JSON lives in Saved/NeoTokyoAudit/walkable_road_restore.json. Git ignores Saved/.
- If successful, replace it with segmented Blocking Volumes / simple collision for production.

## Undo
- Before saving: close the level and discard modifications.
- After saving: delete actor NT_TEMP_WalkableRoadCollision in Outliner, restore PlayerStart from the JSON, save level.
- Do not rerun when a restore record already exists. Review the initial attempt first.
