# Unfold

**Explain ideas through motion. Keep what makes them yours.**

Unfold is a planned Amplifier Smart Tool for creating, reviewing and revising motion
graphics. Describe what you want to communicate, supply relevant material and choose
an identity. Unfold develops the animation and returns work that a person can review
and another tool can use.

The initial emphasis is technical communication: explaining AI and software concepts,
adding callouts to real demos, and creating consistent visual material for larger
productions. Reusable identities, media and motion elements accumulate in a local
library. Identity packs can travel between teammates as ZIP files.

The library is the product. A thin CLI and an optional built-in dashboard expose the
same behavior. Embedded Amplifier intelligence handles creative interpretation;
ordinary code handles operations that need no model. HyperFrames is the initial
production backend, kept behind Unfold's public boundary.

**Status:** vision and behavioral contracts only. Unfold is not implemented or
available to install. No commands, API signatures, runtime compatibility or product
acceptance results are claimed by this repository.

## Project documents

- [Vision](docs/VISION.md) — intended experience, principles and initial boundaries.
- [Contract map](contracts/README.md) — promises, representative scenarios and open decisions.
- [Portable invocation](contracts/invocation.v1.md) — library, CLI, deterministic paths and packaging.
- [Caller interaction](contracts/caller-interaction.v1.md) — context, handoffs, observation and continuity.
- [Motion creation and delivery](contracts/motion.v1.md) — exploration, revision, footage, audio and outputs.
- [Creative library and identity packs](contracts/creative-library.v1.md) — retained work, reuse, versions and ZIP exchange.
- [Review dashboard](contracts/dashboard.v1.md) — shared review, management and presentation lifecycle.
- [Internal execution](contracts/internal-execution.v1.md) — embedded intelligence, production capabilities and validation.
- [Contributor guidance](AGENTS.md) — how to develop from these drafts.

All governing documents remain **DRAFT**. They describe intended behavior, not
implemented features or locked interfaces.
