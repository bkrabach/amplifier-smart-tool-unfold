# Unfold contracts (DRAFT)

These documents turn the [vision](../docs/VISION.md) into behavioral promises.
They are not API specifications, implementation plans or claims of shipped support.
No Unfold implementation, approved acceptance fixtures or executable acceptance
evidence exists yet. The separate HyperFrames capability experiment is not an
Unfold product acceptance run.

| Contract | Owns |
| --- | --- |
| [Portable invocation](invocation.v1.md) | Library-first packaging, CLI, help, deterministic paths and failures |
| [Caller interaction](caller-interaction.v1.md) | Context, authority, results, questions, observation and production handoffs |
| [Motion creation and delivery](motion.v1.md) | Creative alternatives, preservation, reference footage, audio and actual outputs |
| [Creative library and identity packs](creative-library.v1.md) | Retention, versions, dependencies, on-disk traceability, external edits and ZIP exchange |
| [Review dashboard](dashboard.v1.md) | Human participation, targeted feedback, library management and service lifecycle |
| [Internal execution](internal-execution.v1.md) | Scoped intelligence capabilities, deterministic mechanisms and result validation |

The public boundary promises product behavior. Internal HyperFrames operations,
specialist prompts and agent session state are not caller prerequisites. All
externally useful capabilities belong to the library; that does not require every
internal production primitive to have a public command.

## Representative acceptance scenarios

These are a small initial proof set, not an exhaustive creative menu. Each needs
independently prepared inputs, expected outcomes and review criteria before its
acceptance run. Skipped, blocked and unverified cases are never passes.

| Scenario | Observable outcome | A misleading apparent success |
| --- | --- | --- |
| Explain a technical concept | Compare distinct explanatory approaches, select one, then revise while preserving specified choices. | Attractive recolors counted as different explanations; labels are correct but motion implies a false relationship. |
| Overlay a working demo | Review against an identified recording, export a separate transparent layer, and place it using the handoff. | Background footage is baked into the overlay; alignment depends on an undocumented offset. |
| Reuse and share an identity | Apply the same version across different compositions; export/import ZIP into a fresh library and reuse it. | Correct appearance depends on the creator's font cache, absolute paths or unbundled assets. |
| Continue after review and external edits | Dashboard feedback and an adopted source edit produce identified revisions; a fresh caller finds the changes and files. | Private browser state is required; old previews or checks appear current for changed source. |
| Work with imported audio | Synchronize a graphic to supplied cues, preview it with sound and hand off separate assets and timing. | A silent preview is treated as audio verification; audio generation happens implicitly. |

The first runnable demonstration may exercise a subset. Its report must name that
subset rather than treating the entire intended scope as delivered. The optional
dashboard is optional to use, not silently omitted from the intended product.

## Decisions deliberately left open

- Public capability names, typed schemas, identity encoding and storage layout.
- Implementation language, package/import naming, CLI spelling and dependency pins.
- Exact output profiles, transparent formats, audio formats and supported platforms.
- Which representative fixtures and human review rubrics establish useful quality.
- Supported visual-element targeting, annotation granularity and external-edit types.
- How reference cues and placement data are represented for the first real compositor.
- Provider/model support, bounded work units, retention policy and change transport.

These choices should be resolved by actual consumers and installed trials, not a
universal interchange schema. HyperFrames as the first backend, a library with a
thin default CLI, Amplifier Agent for intelligence, imported rather than generated
sound, local retention and ZIP identity exchange are already product decisions.

## Document lifecycle

Keep these documents DRAFT while behavior is developed and exercised. Implementation
evidence must identify exact scenarios and limitations. Locking governing documents
requires explicit owner acceptance; passing unit tests or upstream packaging checks
does not implicitly ratify them.
