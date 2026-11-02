# Layout and migration contract

Read this reference for `plan`, `apply-approved`, and `verify` modes.

## Recommended zones

```text
workspace/
├── README.md
├── CURRENT_RELEASE.md
├── WORKSPACE_MANIFEST.json
├── current/       # relative aliases to promoted reader artifacts
├── evidence/      # relative aliases to discovery and integration evidence
├── provenance/    # intact source-of-truth trees
├── operations/    # maintenance evidence and historical tools
└── work/          # new writable packages only
```

Keep mutually linked provenance directories as exact-basename siblings when
their internal documents use `../name/...` links. Do not normalize names inside
`provenance/`.

## Plan schema 1.0

The plan is JSON with these required fields:

- `schema_version`: `"1.0"`
- `plan_id`, `created_at_utc`, `workspace_root`, and `intent`
- `policy`: must refuse copies, deletions, overwrites, sealed edits, absolute
  aliases, out-of-root paths, cross-device moves, and apply without an exact
  plan SHA
- `mkdirs`: parent-before-child relative directories
- `moves`: exact relative `source`, `target`, and `expected` snapshot
- `critical_hashes_before_and_after`: exact pre/post paths and SHA-256
- `symlinks`: exact link path and relative target text
- `post_artifacts` and `required_validations`

Each move's `expected` object contains:

```json
{
  "device_id": 16777229,
  "root_inode": 123456,
  "directories_including_root": 10,
  "regular_files": 100,
  "symlinks": 0,
  "logical_bytes": 123456789,
  "files_with_nlink_gt_1": 25,
  "unique_regular_file_inodes": 100
}
```

Create a separate seal containing the plan hash and basename:

```text
<64-character-sha256>  move-plan.json
```

The plan never contains its own hash.
The applicator also requires the seal's filename token to match the actual plan
basename.

## Preflight requirements

Before mutation, confirm:

1. The workspace root is exact and is a real directory.
2. Every source is a real directory with the sealed snapshot.
3. Every target and alias path is absent.
4. Every source and target parent is on the workspace filesystem.
5. Critical pre-move hashes match.
6. Aliases are relative and normalize inside the workspace.
7. No process is actively writing to a moved tree.
8. Sufficient disk space remains, although same-volume rename should allocate
   negligible research-data bytes.

Human approval is still required for the exact plan hash. A prior approval is
not reusable after any drift.

The apply phase is a sequence of same-volume atomic renames, not one atomic
transaction across the whole plan. If an unexpected host or filesystem failure
interrupts it, preserve the partial state and logs, inventory again, and write
a separately approved recovery plan. Never rerun the original plan blindly.

## Post-move proof

For every moved tree, require source absence and target preservation of:

- device ID and root inode;
- directories, regular files, and symlinks;
- logical bytes;
- files with multiple links and unique file inodes.

Rehash critical release files. Resolve every alias and confirm it remains
inside the workspace. Replay each internal checksum manifest from its own root.
Run only read-only, release-appropriate validators; inspect them before use.

Record all results in a new validation report and bind that report in a new
migration receipt. Never overwrite an earlier plan, report, or receipt.
Save the report inside the workspace but outside every preserved move target,
for example under `operations/`. The verifier resolves aliases and refuses
destinations inside a preserved target before creating directories or files.

## Storage and history

Logical duplicate content is not proof of reclaimable space. Multiple paths
may already be hardlinked outside the visible workspace. Deduplication,
hardlink creation, compression replacement, and safe-trash operations are
separate decisions and never part of structural migration.

Historical absolute paths, authorizations, provider cursors, runtime receipts,
and tool hashes remain historical evidence. Moving a package does not refresh
or authorize them.
