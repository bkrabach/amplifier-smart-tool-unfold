# Portable invocation contract — v1 (DRAFT)

**Who builds against this:** Applications importing Unfold, agents invoking its
CLI and authors of presentation adapters.

The upstream baseline reviewed for this draft is
[Smart Tools at 0f89dd9](https://github.com/microsoft/amplifier-smart-tools/tree/0f89dd9263338918d9b27bb48670c688c3e9bac1/spec).
No distribution or conformance result exists yet.

## What it looks like

```text
Application → library capability → typed outcome and artifact references
CLI → argument parsing and I/O → the same library behavior
Existing composition → deterministic validation/render → result without a model
```

Right: inspecting a saved project works without a provider. Wrong: importing the
library boots an agent or demands a host's conversational session.

## Core (the teeth)

1. **The library owns every externally useful capability.** Creation, review state,
   asset management, settings, revisions, observation, rendering, export and cleanup
   are library behavior. The default CLI is thin. The dashboard and other adapters
   cannot contain exclusive domain logic. The library may invoke renderer processes
   internally; callers need not shell out to Unfold to embed it.
2. **The installed tool is self-contained in its expertise.** Production guidance,
   prompts and required resources ship or resolve through documented dependencies.
   Callers need no source checkout, separately configured Amplifier app, private
   skills directory or existing internal session. The distribution is installable
   from its Git repository with documented prerequisites.
3. **Deterministic work needs no model.** Imports, help, manifests, retained-state
   reads, mechanical edits, asset I/O, packaging, frame extraction, validation and
   rendering an already valid composition run without model credentials or runtime
   initialization where advertised. Compute and renderer dependencies remain real.
   A deterministic failure never silently invokes a model to repair it.
4. **Smart work embeds Amplifier Agent.** Creative interpretation, composition and
   feedback handling run within Unfold's library. Effective provider/model settings,
   permitted disclosure and limits are inspectable. Unfold does not assume it inherits
   a caller's subscription or credentials. Missing configuration names a remedy
   rather than producing an undisclosed substitute or launching login.
5. **Self-description is library-owned and truthful.** The eventual distribution
   provides the upstream descriptor, one packaged smart-tool manifest, structured
   manifest access, terse help, full agent-facing help and per-capability help.
   Documentation identifies inputs, outputs, dependencies, failure behavior and
   model use. A real provider-free smoke capability and matching package metadata
   are required before claiming conformance. Draft documents do not substitute.
6. **Inputs do not assume shared ambient context.** Additional caller context can
   be supplied as actual content. Adapters may mechanically load selected files.
   Large media can be supplied through scoped path references or managed asset IDs;
   callers need not embed video/audio bytes in a request or model context. These are
   explicit library inputs, not a CLI-only convenience. Document which process must
   be able to read a reference; a path on another host is not presumed accessible.
   Any required transfer or retained copy is explicit, with source, destination and
   ownership reported under the [creative-library contract](creative-library.v1.md).
   Supplying a path grants no right to move, overwrite or delete its source. Supplied
   summaries remain distinguishable from originals actually inspected.
7. **Results and failures compose.** Library results are typed and usable directly.
   The CLI provides documented machine-usable results on stdout and diagnostics on
   stderr. Errors name a cause and remedy and exit nonzero. Closed-stdin calls never
   wait for inaccessible prompts. Partial completion is valid only where documented
   and explicitly identifies the completed and missing parts.
8. **State and side effects have declared scope.** Retained work uses a documented
   platform per-user default or selected location outside the installation tree;
   exports use selected destinations. Creation does not implicitly publish, share,
   install dependencies, modify unrelated repositories or open applications. An
   explicitly selected dashboard can start within existing presentation authority
   under the [dashboard contract](dashboard.v1.md).
9. **Dependencies do not become public workflow requirements.** HyperFrames is the
   initial backend and its prerequisites are disclosed. Callers use Unfold's public
   behavior without managing HyperFrames commands. Retained native source may remain
   backend-specific; neither migration nor byte-identical cross-platform rendering
   is promised. Availability of an upstream feature is not proof of Unfold support.

## Proposed acceptance checks

- Install outside the checkout and invoke both library and CLI using packaged help.
  Verify descriptor and manifest behavior with the upstream conformance kit.
- Deny provider access and assert no agent boot during imports and deterministic
  operations. A missing renderer fails specifically and does not call a model.
- Run an authorized smart request from an unrelated host harness without its own
  Amplifier session; missing credentials return a useful failure.
- Compare library and CLI outcomes and side effects for the same operations.
  Ensure machine results parse and closed stdin never produces a hanging prompt.
- Inspect writes and process starts for out-of-scope mutation or implicit services.
- Supply a large local media file by reference without inlining its bytes. Exercise
  a retained-copy request and an inaccessible remote-host path; report the actual
  copy or access failure while preserving the source and avoiding model disclosure.

These are proposed assertions, not executed checks. Upstream conformance does not
prove creative quality, media correctness or dashboard behavior.

## What v1 deliberately does NOT freeze

Implementation language, command spellings, import names, schemas, provider list,
platform support, dependency pins and additional transports. Establish these through
installed caller examples before advertising them.
