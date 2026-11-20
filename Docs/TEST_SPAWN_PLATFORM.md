# Test: isolating Pawn spawning from road collision

Run Tools/ue54_test_spawn_platform.py in Unreal Editor 5.4 with Level2_Tokyo open and PIE stopped.

This creates a VISIBLE 6×6 meter engine Cube with BlockAll collision precisely at the XY of the *loaded* PlayerStart, top 140cm below its Z. It never edits original Tokyo meshes and does not automatically save the map.

1. Pull new commits in GitHub Desktop.
2. Open Level2_Tokyo. Keep World Partition cell containing PlayerStart loaded.
3. Tools > Execute Python Script > Tools/ue54_test_spawn_platform.py.
4. Stop if Output Log raises error. Check Outliner for NT_DIAGNOSTIC_SPAWN_PLATFORM.
5. Locate that actor using F (focus), ensure it sits under PlayerStart. If visually incorrect, delete it and do not save.
6. For PIE choose Spawn Player At: **Default Player Start**, not Current Camera Location.
7. Press Play. If character lands on visible test platform, default Pawn physics is working and road collision is missing/wrong. If falling persists, investigate GameMode pawn class, capsule collision and spawn fallback.
8. Record a screenshot and Output Log. Remove NT_DIAGNOSTIC_SPAWN_PLATFORM after test; do not keep it in AAA production scene.

This test does not solve the real road's collision; it provides a reliable isolated result. Do not import JSON as DataTable or into Content Browser. Diagnostics JSON is plain text in Saved/NeoTokyoAudit.
