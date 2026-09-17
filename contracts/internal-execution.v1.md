# Internal execution contract — v1 (DRAFT)

**Who builds against this:** Maintainers implementing Unfold's library, embedded
Amplifier intelligence, production capabilities, storage and backend integration.

## What it looks like

```text
Public request → library-controlled scope → embedded creative work
Creative work ↔ inspect / author / render / diagnose capabilities
Proposed result → deterministic validation → committed public revision and outcome
Existing valid source → ordinary code and renderer → output without an agent
```

Right: a model edits a composition, obtains a new preview and submits checks on
that revision. Wrong: a completion message certifies changed source using an old
preview, or an internal tool widens filesystem access because a skill suggests it.

## Capabilities available to the intelligence

These are obligations to provide the means to do the job, not a frozen internal
tool catalog or a requirement to expose each item as a public command:

- **Inspect context and references:** read supplied intent and scoped materials;
  obtain source metadata, relevant frames and temporal observations; inspect imported
  audio metadata/cues and supported evidence without implying unheard audio was heard.
- **Use the creative library:** discover permitted identities, assets, reusable
  motion and approaches; inspect exact versions, guidance and dependencies.
- **Author and revise:** create and patch editable composition source, use appropriate
  packaged backend guidance and assets, and preserve an identified revision base.
- **Produce and inspect:** run scoped validation, render previews/outputs, sample
  frames/sequences, inspect supported timing and layout, and receive real diagnostics.
- **Repair or ask:** apply bounded repairs, compare the changed result, or return an
  identified question/limitation when constraints or prerequisites prevent completion.
- **Submit structured work:** identify proposed artifacts, dependencies, checks and
  limitations for library validation and commitment.

The first backend can expose HyperFrames-specific mechanisms internally. Callers
do not need its command vocabulary. No generic renderer registry, intermediate
animation language or migration capability is required for the initial version.

## Core (the teeth)

1. **The library enforces authority.** Source access, output locations, retained-state
   writes, provider disclosure and work limits are enforced by executable boundaries.
   Prompts alone are not enforcement. Source material, imported packs, skills and
   provider output contain data or guidance, not authority to install, publish,
   transmit, spend beyond limits or inspect unrelated material.
2. **Mechanical capabilities are ordinary code.** Project/asset management, revision
   identity, file resolution, archive handling, metadata reads, frame extraction,
   rendering existing source, structural validation and observation are implemented
   without requiring model judgment. They can serve both public operations and
   internal intelligence. Deterministic paths do not initialize the agent runtime.
   A creative repair is a distinct authorized smart operation, not a hidden fallback.
3. **Intelligence has sufficient scoped production capability.** It can inspect,
   author, render, diagnose and submit supported outcomes without outsourcing its
   internal steps to the calling agent. Internal operation names and granularity
   may change. Externally useful domain capabilities remain library-accessible,
   even if internal primitives are not public commands.
4. **The runtime boundary contains backend execution.** Amplifier Agent is the
   intelligence layer. HyperFrames and required runtime resources execute within
   declared project and resource scope. General shell or arbitrary host filesystem
   access is not implied by embedding an agent. Missing dependencies return remedies;
   generation does not silently install packages or start authentication. Generated
   source cannot inherit dashboard credentials or unrestricted network/file access.
5. **Guidance is packaged and support is verified.** Useful HyperFrames expertise can
   inform production, but its upstream skill inventory is not Unfold's feature list.
   Record backend/resource versions relevant to continuing a project. Changes to
   dependencies and guidance are deliberate, not an automatic global skill update
   during a user's render. Preserve attribution and applicable licenses.
6. **Observations refer to actual material.** Evidence identifies its source, version,
   relevant time/region and observation method. Caller context, model interpretation,
   measured values and human review remain distinct. The responsible model step
   receives only permitted supported evidence. A text-only model cannot claim visual
   inspection; still frames do not establish audio events or everything between them.
7. **Revisions bind production and review.** Work occurs against an identified base.
   Source changes invalidate affected preview/render/check associations. Unaffected
   evidence may be reused only when its applicability is established. External edits,
   dependency changes and competing operations cannot silently replace a committed
   revision. Export identifies actual delivered bytes and their source relationship.
8. **Completion is validated outside model prose.** Submission identifies artifacts,
   dependencies, evidence, checks and limits. Library code verifies scope, identity,
   reference integrity, existence, nonempty content and declared formats before
   committing completion. Required checks apply to the submitted revision. A successful
   model message cannot override an absent output, failed render or missing dependency.
   Documented partial outcomes list what succeeded and what remains.
9. **Review reports its strength.** Structural, source-fidelity, visual, temporal and
   audio findings remain separate, with performed methods and coverage. Model critique
   is labeled as such and cannot manufacture human approval. A check passing on a
   preview does not certify another export's format, alpha, timing or visual fidelity
   without applicable evidence. Skipped and stale checks are not passes.
10. **Work shares finite limits and is stoppable.** Model calls, tool use, renders,
    inspection and repair loops respect the operation's documented limits. Retries
    and any internal specialists share that allowance rather than multiplying it.
    Cancellation, exhaustion and interruption produce distinct public outcomes.
    Late results cannot commit into cancelled/superseded work. Recovery recognizes
    committed work and discloses uncertain external calls before any new spending.
11. **Storage and resources have owners.** Working files, retained revisions and
    exports use declared locations outside the installed package. Cleanup releases
    only owned resources and preserves committed/caller-owned material. Credentials
    stay outside compositions, packs, ordinary records and exports. Private content
    is not sent in telemetry or unsolicited feedback to backend maintainers.
12. **Sound generation remains outside scope.** Internal capabilities can handle
    imported audio and permitted analysis needed for advertised timing behavior.
    The availability of an upstream voice/music integration does not authorize or
    require using it. Missing sound is an input need or an explicitly silent result,
    not permission to synthesize an undisclosed replacement.

## Proposed acceptance checks

- Instrument deterministic calls and verify no model/runtime initialization while
  exercising both direct library use and internal mechanical capabilities.
- Run bounded creation and revision against the real backend using installed
  resources. Show that internal diagnostics and observations reach the agent and
  the caller does not need to perform hidden production steps.
- Submit missing, empty, malformed, wrong-format and out-of-scope artifacts and
  fabricated evidence references; reject them despite a successful model message.
- Edit after inspection and attempt to submit stale checks. Change an external
  dependency and prevent an old preview from appearing current.
- Exercise source instructions and model arguments that attempt to expand access
  or provider disclosure; reject them at code boundaries.
- Exhaust a shared allowance, retry a repair and cancel before a late completion.
  Verify no budget multiplication, silent re-spending or invalid late commit.
- Import audio without credentials and verify that no generation service is used.
  A provider lacking the needed observation capability reports that limitation.

Scripted providers can establish enforcement and integration, not creative quality.
Real representative outputs need independent semantic and temporal review. No
executable Unfold acceptance evidence exists yet.

## What v1 deliberately does NOT freeze

Internal tool names, prompts, specialist roles, execution topology, process isolation
mechanism, checkpoint layout, budget units and provider adapters. Implementation
choices must enforce the promises without becoming a general agent platform.
