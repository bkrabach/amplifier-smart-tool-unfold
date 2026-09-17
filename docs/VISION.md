# Unfold — Vision (DRAFT)

*The intended experience. Specific promises live in [contracts](../contracts/README.md).
No implementation or product acceptance is claimed.*

## What Unfold is

Unfold helps people express ideas through motion and refine the result without
losing their intent. A person or calling agent describes what should be understood,
supplies relevant material and constraints, and receives an editable composition
and usable outputs. The caller does not need to become a motion designer or operate
the production backend's specialist tools.

The initial emphasis is technical communication, especially AI and software:
explaining a handoff between agents, showing information moving through a system,
making a data relationship understandable, and helping an audience follow a real
working demo. Titles, transitions, branded segments and reusable overlays belong
alongside explanatory graphics. These examples guide verification without becoming
a closed menu or a promise to handle every visual request.

Unfold is an Amplifier-powered Smart Tool. The library is the product; its thin CLI
and optional built-in dashboard are adapters. Embedded intelligence interprets
requests, develops visual approaches, authors compositions and responds to feedback.
Code performs work that does not need a model. A caller can manage assets, inspect
retained work, render an existing valid composition and export available results
without model credentials. The calling agent need not use Amplifier or share its
internal sessions. Provider and model choices are explicit configuration.

HyperFrames is the initial production backend. Unfold can use its skills and
capabilities internally while presenting its own product boundary to callers.
Editable compositions may depend on that backend, and those dependencies remain
visible. Supporting another renderer, migrating old projects or designing a
universal animation representation is outside the initial scope.

## Explore an explanation, then develop it

The same idea can unfold in different ways. An agent handoff might be shown as a
system diagram, a message passing between participants, or a concrete demonstration
with annotations. When exploration helps, Unfold offers visually meaningful
alternatives and explains their tradeoffs. Different colors alone do not count as
different explanations, although exploring style is useful in its own right.

The preview suits the question. A storyboard may establish sequence; a rough moving
sketch may establish pacing; a more finished scene may establish appearance. People
can request a direct result when their direction is already clear. Neither an intake
wizard nor multiple alternatives is mandatory for every task.

Feedback identifies both what should change and what should stay. “Make this
handoff clearer, but keep the timing and visual treatment” continues the selected
work. If those constraints conflict, Unfold makes the conflict understandable.
Review may also expose a mistaken interpretation of the brief; accepting that
correction updates the intent and identifies affected work rather than leaving
contradictory material looking current.

## Develop a reusable identity

People build a visual language across projects. An identity includes fonts, colors,
logos, diagram conventions, motion preferences, examples and guidance about what
must stay consistent and what may adapt. It is more than a palette applied after
creation. Unfold interprets flexible guidance in context while preserving declared
requirements and identifying consequential departures.

A local creative library holds projects, identities, media, reusable motion
elements and reusable creative approaches. A person may maintain several personal,
team or project identities, organize them, preview them and choose which version
to use. Revising a shared identity does not silently restyle existing projects.
Adopting an update is a deliberate revision that can be reviewed.

Identity packs can be exported and imported as ZIP files so a teammate can use
them without reconstructing the creator's machine. Packs carry their guidance,
eligible assets, version information and declared dependencies. Finished videos,
editable projects and reusable identity packs are distinct exports. A shared online
library service is not required for the initial product.

## Contribute to a larger production

A calling agent may combine Stories for narrative and storyboarding, a future
capture tool for demonstrations, Unfold for motion and explanatory material, and
a compositor for the final production. Unfold also works independently. Those
other tools need not be installed to create or inspect an Unfold project.

The caller owns the larger production and supplies the segment's purpose,
constraints and relevant context. Unfold owns its contribution and returns enough
identity, timing, placement and dependency information for another tool to use it.
It can produce a complete rendered scene, a transparent overlay, or a combined
video where supported. Reference footage may guide an overlay and appear in its
review preview while remaining absent from the delivered graphics layer.

Real captured behavior, illustrative animation and simulated interfaces remain
distinguishable. Technical clarity includes what the motion implies, not only the
correctness of labels. An animation must not turn a hypothetical sequence into
apparent evidence that a system performed it.

Imported narration, sound effects, music and audio signatures can guide timing
and accompany output or identity packs. Separate assets and their timing remain
available for a compositor when requested. Unfold does not generate voices, music
or sound effects in its initial scope.

## Review and return to the same work

The dashboard is a built-in, optional way to participate. It opens retained work
created headlessly, lets a person compare approaches, play and scrub previews,
give targeted feedback, manage the creative library, select identities and export
the revision they reviewed. It need not become a full timeline editor.

People and calling agents work against the same identified projects and revisions.
Comments can concern a whole composition, a scene, a time interval or a supported
visual element. Submitted feedback can be handled by internal intelligence within
existing authority. A returning caller can observe the feedback, resulting changes
and pending needs without screen scraping or replaying an internal conversation.
Unsubmitted drafts remain distinct from instructions. Background updates preserve
the person's place and unfinished input.

The work is retained in a discoverable local location selected by the person or
caller, with documented defaults. Editable source, assets, previews, exports and
records can be traced on disk through public identities and manifests. A fresh
caller can discover what produced an asset, what superseded it and which reference
material it used. Exporting a snapshot does not erase the ongoing project.

External source edits are detected and can be adopted as a new revision; they do
not silently overwrite the reviewed record or inherit checks on earlier bytes.
People can reopen, duplicate, organize and remove work deliberately. Removing a
shared asset exposes its dependents, and disposable caches are separate from
creative work worth retaining.

## Principles

1. **The library is the product.** No externally useful behavior exists only in
   the CLI or dashboard. Internal production details need not become public APIs.
2. **Use code where code is enough.** Deterministic work does not require a model
   or initialize intelligence. Creative judgment uses the configured embedded agent.
3. **The explanation sets the direction.** Motion, style and representation serve
   the intended understanding. Creative breadth does not imply universal support.
4. **Refinement preserves deliberate choices.** Feedback targets the reviewed work;
   unrelated choices and earlier revisions survive unless deliberately changed.
5. **Identity accumulates and travels.** Shared assets and guidance can be reused,
   versioned and exchanged without relying on the creator's private environment.
6. **Handoffs preserve meaning and context.** Another tool can identify what it
   received, place it correctly and discover when its reference assumptions change.
7. **Checks name their evidence.** Structural, visual, temporal and source-fidelity
   findings remain distinct. Successful rendering is not proof of a useful explanation.
8. **Authority and resources remain bounded.** Existing valid authority supports
   follow-up without repeated approval; content or model output cannot expand it.

## Initial boundaries

- Build a useful demonstration and get feedback before adding infrastructure.
- Keep creative requests open while proving a small set of representative outcomes.
- Use HyperFrames first; defer migration and a general renderer abstraction framework.
- Support imported audio and its handoff; exclude sound generation.
- Share identities through ZIP files; defer hosted libraries and real-time team editing.
- Do not build demo capture, a general video editor or an entire production orchestrator.
- Do not assume every upstream skill, integration, codec or platform is supported.
- Creation and export do not imply publication, external sharing or account setup.

## How you can tell it is working

- A technical audience understands a relationship more clearly because of the motion.
- A person compares genuinely different approaches, selects one and recognizes the
  requested change without losing the parts they wanted to keep.
- An overlay is reviewed against real footage and placed by another tool using the
  delivered timing and placement information, without hidden background footage.
- Several compositions share an identity while adapting to their individual content.
- A teammate imports an identity ZIP into a fresh library and can use it without
  the creator's paths, caches or credentials.
- A fresh calling agent finds the source and exact revisions, sees subsequent
  review activity, and continues without the original conversation.
- Deterministic operations remain usable when no provider is configured.

## Changelog

- **2026-09-16** — First draft from the Unfold ideation discussion. No lock or
  implementation claim.
