# Working on Unfold

Read [the vision](docs/VISION.md) and [the contracts](contracts/README.md) before
planning or changing product behavior. The contracts remain drafts. The packaged
SMART_TOOL.md documents the implemented slice; do not infer full product support
or acceptance from either the vision or packaging conformance alone.

## Architecture

- The library is the product. Every externally useful domain capability belongs
  there; the CLI and dashboard adapt arguments, presentation and I/O.
- Use Amplifier Agent for model-backed execution behind the library boundary.
  Imports, help and deterministic operations must not initialize intelligence.
- Implement mechanical work in code: asset management, revision records, packaging,
  frame extraction, rendering existing compositions, validation and observations.
- HyperFrames is the first production backend. Keep its commands and internal
  machinery out of the public caller contract. Do not build a renderer framework,
  universal animation format or migration system in anticipation of another backend.
- Internal production tools need not be public commands. The intelligence must
  nevertheless have scoped ways to author, inspect, render, repair and submit work.
- Sound generation is outside the initial scope. Support imported audio, timing
  and relevant asset handoffs without silently invoking generation services.

## Documents and changes

- Keep vision and contracts DRAFT until the owner explicitly locks them. Explain
  discrepancies between promises and implementation rather than quietly weakening
  the documents. Propose changes to locked promises separately.
- Preserve the broad creative scope. Acceptance examples are obligations to prove,
  not an exhaustive catalog of requests or a fixed sequence of specialists.
- Do not freeze command names, schemas or storage layout merely to make planning
  look complete. Establish those through concrete caller and installation examples.
- Keep tracked files focused on deliverables and durable contributor guidance.
  Put research, deliberations, trial media, scratch scripts and local review records
  in gitignored `.work/` or caller-owned storage. Never depend on private trial files.
- Keep document indexes to links; requirements belong in their governing documents.
  Write the user-facing README when working behavior can be documented. Keep
  intermediate plans and phased delivery notes in `.work/`, not the vision.
- Keep credentials, local viewer secrets, generated stores and private footage out
  of Git. Preserve upstream attribution and licenses when reusing code or assets.
- Keep runtime state outside the installation tree; use documented per-user
  defaults or explicitly selected library/output destinations.
- Package production guidance, prompts and required resources for installed use.
  Update library-owned help and manifest documentation with capability changes.

## Verification

- Define expected behavior independently before running acceptance scenarios.
  Check library behavior and adapter semantics, not just happy-path CLI output.
- Inspect actual rendered media. File existence, a model's completion message,
  schema checks and sampled stills establish different things; report their limits.
- Exercise identity ZIP exchange and continuation on a fresh store without original
  absolute paths, caches, provider sessions or the creator's conversation.
- Test deterministic paths with credentials absent and no agent initialization.
  Live provider trials require applicable bounded authority; fixtures do not prove
  creative quality or real model performance.
- Run the upstream Smart Tools conformance kit when a distribution exists. Report
  its packaging checks separately from Unfold's product acceptance scenarios.
- Keep patches scoped and preserve unrelated work. Commit or push when requested.
