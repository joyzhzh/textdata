---
name: eisenhardt-corpus-maintainer
description: Audit, organize, verify, and maintain an Eisenhardt case-method workspace containing reader releases, discovery evidence, sealed campaign provenance, checkpoints, and operational tools. Use for housekeeping or intake of new Eisenhardt outputs; do not use it for literature discovery, evidence admission, or unapproved deletion.
---

# Eisenhardt Corpus Maintainer

Keep the workspace understandable without weakening provenance. Treat a
completed campaign tree as an immutable package and expose human-facing files
through lightweight relative aliases.

## Choose a mode

- `audit` — inventory the workspace without mutation. Report counts, logical
  bytes, symlinks, devices, inodes, hardlink statistics, manifests, and path
  dependencies.
- `plan` — write an exact source-to-target plan plus a separate SHA-256 seal.
  Do not mutate the layout.
- `apply-approved` — apply only the exact plan hash the user approved, after a
  fresh dry-run passes without drift or collisions.
- `verify` — compare post-move targets with pre-move snapshots, replay
  applicable manifests and release validators, resolve aliases, and record a
  receipt.
- `intake` — route new work into a dated writable package. Never promote a
  release implicitly.

Read [references/layout-contract.md](references/layout-contract.md) before
planning, applying, or verifying a migration. Ordinary read-only inventory
does not require loading the reference.

## Audit

Resolve this skill's directory from the loaded `SKILL.md`, then run:

```bash
python3 -B <skill-dir>/scripts/inventory_workspace.py <workspace-root>
```

Use `find -P` or equivalent for supplemental inspection. Never follow active
aliases while counting; that double-counts provenance. Treat logical duplicate
bytes separately from reclaimable storage, especially when link counts exceed
one.

## Plan and apply

Build a schema-1.0 plan following the layout contract. Bind every movable tree
to its device, root inode, directory count, regular-file count, symlink count,
logical bytes, hardlink count, and unique file-inode count. Bind promoted
release files and manifests by SHA-256.

Seal the completed plan in a separate checksum file. Run the applicator without
`--apply`; dry-run is the default:

```bash
python3 -B <skill-dir>/scripts/apply_move_plan.py --plan <plan.json> --seal <plan.sha256>
```

Only after the user approves that exact plan hash may the mutating form run:

```bash
python3 -B <skill-dir>/scripts/apply_move_plan.py --plan <plan.json> --seal <plan.sha256> --apply --approve-plan-sha <exact-sha256>
```

If any source, target, count, inode, device, hash, alias, or plan seal drifts,
stop. Generate a new plan; never edit or reuse an approved sealed plan.
The applicator uses sequential atomic renames, not a multi-operation filesystem
transaction. If the host or filesystem fails mid-apply, do not retry blindly:
inventory the partial state, preserve the original plan and output, and prepare
an explicit recovery plan for the remaining operations.

## Verify and record

Run the structural verifier after relocation:

```bash
python3 -B <skill-dir>/scripts/verify_workspace.py --plan <plan.json> --seal <plan.sha256> --output <new-report.json>
```

Choose a new report path inside the workspace but outside every preserved
move target, for example under `operations/`. An alias into a preserved
target is also refused before any report directory or file is created.

Then run each recognized checksum manifest from its own canonical root and the
release-specific read-only validators recorded by that release. A manifest
path is relative to the directory where it was generated, not to a convenience
alias.

The migration receipt must bind the plan, pre-inventory, structural report,
workspace catalog, and validation results by SHA-256. State the counts of
renames, aliases, copies, overwrites, deletions, and sealed-content edits.

## Intake

Place newly authorized work under `work/<yyyy-mm-dd>-<purpose>/`. Preserve an
incoming sealed package intact. Classify it in the catalog only after its own
manifest and identity bindings pass. Promotion to `current/` requires a
separate explicit decision and new release evidence.

## Hard boundaries

- Never delete, overwrite, deduplicate, compress-replace, or rewrite sealed
  content as housekeeping.
- Never reorganize children inside a sealed tree. Move the whole tree on the
  same filesystem.
- Never mass-rewrite historical absolute paths; they document earlier runs.
- Never treat archived authorizations, checkpoints, or runners as executable
  after relocation without a newly prepared and validated working package.
- Never infer evidence admission, release promotion, or a saturation claim from
  successful housekeeping.
