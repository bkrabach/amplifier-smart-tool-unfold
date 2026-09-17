# Creative library and identity packs contract — v1 (DRAFT)

**Who builds against this:** People managing retained work, calling agents,
teammates exchanging packs and consumers of editable project exports.

## What it looks like

```text
Local library → projects + identities + media + reusable motion and approaches
Project revision → exact dependency versions → source / preview / exports / checks
Identity version → portable ZIP → fresh library → deliberate adoption or variation
```

Right: a teammate imports an identity and sees a required font that could not be
included. Wrong: import reports success while the composition silently uses a
different font or reads files from the creator's absolute paths.

## Core (the teeth)

1. **Retention is discoverable and configurable.** The library has a documented
   per-user default outside the installation tree and accepts a user/caller-selected
   location. Projects and reusable material can be listed, inspected, named, renamed,
   organized, duplicated and reopened through public capabilities. Work does not
   depend on a browser session or developer checkout. Permission or storage failures
   do not silently send material to a different location.
2. **Durable records explain files.** Public identities and manifests resolve
   editable source, assets, previews, exports, feedback, dependencies and checks to
   actual accessible material. They describe relationships, provenance and versions
   without requiring private database access. Ordinary filesystem inspection is
   useful, but private storage layout is not the integration API. Moved or imported
   work resolves through its new location, not assumed creator paths.
3. **Projects retain enough to continue.** Retained context includes the brief,
   deliberate choices, selected identity, source/reference material relationships,
   native composition, revision history and exported results within documented
   retention. Saving a final video is not a full editable project backup. Missing
   dependencies, expired retained material and unavailable reference footage are
   explicit. Reopening for inspection needs no model.
4. **Identities describe guidance as well as assets.** An identity can include fonts,
   colors, logos, diagram conventions, motion and pacing preferences, examples,
   required rules, adaptable guidance and optional imported audio signatures.
   Multiple identities and project-specific selections are supported. Media,
   reusable motion elements and creative approaches have distinct documented roles;
   an executable composition is not mistaken for inert design guidance.
5. **Versions protect prior work.** Projects record the exact identity and asset
   revisions used. Changing shared material creates an identified version and does
   not silently modify existing compositions or exports. Adopting an update creates
   reviewable work and reports affected dependencies. Duplicating or varying an
   identity preserves its origin while identifying the local variation. Automatic
   inheritance, merging or online synchronization is not required.
6. **External edits are detected and deliberately adopted.** Before reusing or
   exporting affected material, compare it with its recorded identity/content.
   Changed source cannot be presented as the bytes previously reviewed. A caller
   can inspect and adopt supported edits as a new revision; affected previews,
   renders and checks become stale. Unchanged committed revisions remain retrievable.
   Invalid edits report problems rather than replacing valid work. Continuous file
   watching is not implied; conflict with concurrent internal work is explicit.
7. **Export types are distinct.** Finished media, editable projects and reusable
   identity packs each declare their contents and purpose. Editable project export
   includes the material needed for the documented round trip, or lists missing
   dependencies before claiming portability. It need not include every historic
   revision. Export is a snapshot; it neither ends the project nor publishes it.
8. **Identity ZIPs support a real round trip.** A pack contains a versioned manifest,
   guidance, included assets and relevant origin/attribution/usage information.
   It declares external prerequisites and omissions. Eligible imported audio can
   travel with the identity. No credentials, caches, temporary data, unrelated
   projects or reference footage enter a pack merely because they share storage.
   Inclusion follows the selected content and its known redistribution constraints;
   unknown rights are not represented as verified permission.
9. **Import is deterministic, bounded and conflict-aware.** Inspect the manifest,
   pack version, file integrity and declared dependencies. Reject unsupported or
   malformed packs actionably, prevent path traversal and unsafe link extraction,
   and enforce documented archive limits. Import does not execute included code,
   install dependencies, call a provider or overwrite an existing identity silently.
   Existing identical content can be recognized; conflicting identity/version
   claims require an explicit resolution or separate import. Failed imports leave
   existing work intact and disclose any partial new material.
10. **Removal respects dependencies and ownership.** Before deleting shared material,
    expose the retained projects/revisions that rely on it and the documented effect.
    Do not silently break those dependencies or cascade-delete unrelated work.
    A requested destructive removal with dependents needs an explicit choice; exact
    retention/refusal behavior is documented. Generated output removal does not
    delete original footage. Cache cleanup is separate from project/asset deletion.
    Deletion of Unfold-managed material goes through the public library API, including
    when initiated by a caller, CLI or dashboard. Returned paths support inspection
    and consumption; they are not a deletion interface. The operation updates records,
    dependency state and caller-visible observations. A deletion result identifies
    what was removed, missing, retained or failed. Unexpected missing files are
    reported, not silently treated as an accounted-for API deletion.
11. **Source references and retained copies have explicit ownership.** Each intake
    declares whether Unfold reads an external reference or copies material into its
    managed library, such as an identity's assets. Document the default and allow the
    caller to select the supported mode. Report the original reference, resulting
    managed identity/location, completed copy and remaining external dependencies.
    Copying preserves the original; a supplied input path never authorizes a move,
    overwrite or deletion. Unfold does not delete external originals during import,
    export, removal or cleanup. Any separately user-directed deletion by a caller
    outside Unfold is the caller's operation, not an Unfold side effect.
    A retained copy is usable independently of its original where the import promises
    that; reference-only use reports loss or changes of the external source. Failed
    copies do not claim a complete import or delete the original. Removing a managed
    copy does not remove already shared ZIPs or downstream copies.
12. **Useful metadata survives sharing.** Imported material retains origin, declared
    versions, configurable inputs, required dependencies and applicable guidance.
    Source file identity does not masquerade as a global path. A fresh caller can
    trace a project contribution to its imported identity version without access
    to the exporting user's account, private history or agent session.
13. **Renaming changes a label without recreating the asset.** Projects, identities,
    media, reusable elements and saved outputs can be renamed through the public
    library without a model call, render or re-export. Stable identity, content bytes,
    composition revisions and dependency references remain intact. The current
    display name and subsequent download filename reflect the change where applicable;
    prior exported copies are not rewritten. Names are collision-safe labels, not
    paths or identities. Report naming conflicts without overwriting another item.
    Renaming is recorded and observable to callers. Physical file relocation is not
    required; any managed path change preserves reference resolution and is reported.

## Proposed acceptance checks

- Create two identities and several projects in a non-default library. Reopen them
  in a fresh process with credentials absent and resolve files through public records.
- Update a shared identity and verify earlier renders/source remain unchanged;
  explicitly adopt the update into one project and compare affected revisions.
- Export an identity ZIP with guidance, images and an eligible audio asset. Import
  into a fresh directory with original paths and caches unavailable, then use it.
  Exercise a declared missing font and confirm there is no silent substitution.
- Import a duplicate and a conflicting pack, an unsupported version, tampered bytes,
  a path-escaping entry and an excessive archive. Assert no execution, out-of-root
  writes, silent overwrite or damage to existing material.
- Modify composition source externally. Detect the mismatch, adopt it as a new
  revision, preserve the previous one and invalidate relevant checks and previews.
- Delete a shared asset with dependents and verify the chosen policy; separately
  clear caches and delete an export without damaging source or retained work.
- Rename an asset used by two projects, an identity and a saved export through the
  library and dashboard. Verify stable IDs, unchanged bytes/revisions, intact
  references, updated labels/download names and a caller-visible change, with no
  model call, render or re-export. Exercise duplicate names without overwriting.
- Import by path once as a retained copy and once as an external reference. Verify
  reported locations and ownership, unchanged originals, independent use of the
  copy and a useful failure when the external reference becomes unavailable.
  Interrupt a copy and confirm no false completion or original deletion.
- Remove managed material through the API and verify records and observations agree
  with disk. Remove a fixture externally and verify the missing-file discrepancy is
  surfaced; do not invent an API deletion receipt for it.
- Export and reopen an editable project; identify omitted history and dependencies
  rather than confusing that export with either a video or complete library backup.

No implementation or executable acceptance evidence exists yet.

## What v1 deliberately does NOT freeze

Folder hierarchy, storage engine, manifest schema, pack-version syntax, hashing
algorithm, organization vocabulary, deduplication strategy, retention periods and
dependency-deletion policy. Hosted sharing and automatic team synchronization are
outside the initial scope; portable ZIP exchange is sufficient.
