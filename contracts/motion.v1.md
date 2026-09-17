# Motion creation and delivery contract — v1 (DRAFT)

**Who builds against this:** People requesting animations, technical reviewers,
calling agents and consumers placing Unfold contributions into a production.

## What it looks like

```text
Technical intent → visual approaches → selected composition → targeted refinement
Reference demo + identity + cues → contextual preview → separate graphics layer
Existing valid composition + explicit output settings → deterministic render
```

Right: show selected source passages entering a model's input and distinguish that
from training. Wrong: animate those passages changing the model's weights while
retaining technically correct labels about retrieval.

## Core (the teeth)

1. **Creative breadth is outcome-driven.** Unfold accepts ordinary descriptions of
   motion graphics and explanatory material, with relevant sources and constraints.
   Initial verification emphasizes technical concepts, demo annotations and reusable
   branded material. Those cases do not form a template-only admission rule, nor does
   access to upstream skills guarantee arbitrary requests will succeed.
2. **Exploration distinguishes explanation from style.** When alternatives are
   requested or useful under the current brief, approaches differ in a meaningful
   explanatory choice and show that difference visually. Cosmetic variants are
   labeled as style exploration. Fidelity follows the decision: storyboard, moving
   sketch or finished scene. Direct production is available when direction is clear;
   the tool does not require several full renders or a separate brief approval gate.
3. **Intent and evidence remain correctable.** Supplied requirements, inferred
   choices, reference observations and illustrative inventions stay distinguishable.
   Accepted intent corrections revise the brief and identify affected compositions
   as updated or superseded. Technical claims retain supplied support and qualifiers.
   Ambiguous causal or temporal relationships are surfaced rather than confidently
   invented because they make a compelling animation.
4. **Revision separates change from preservation.** Feedback targets an identified
   base and describes what should change or remain. Unaffected identity, content,
   timing and motion choices are preserved. If readability, placement, duration or
   other constraints conflict, Unfold reports the conflict or a qualified option
   rather than silently sacrificing a requested property. Earlier choices and
   alternatives remain available under retention policy.
5. **Identity guides composition.** A selected identity version supplies assets,
   required rules and adaptable preferences. Unfold uses that guidance during
   creation, not only as final color substitution. Missing fonts/assets and meaningful
   departures are visible. A model cannot quietly relax a declared requirement.
   Exact visual enforcement is advertised only for rules that can actually be checked.
6. **Reference footage and delivered footage are separate choices.** An overlay may
   be made without footage using explicit placement constraints, or designed against
   permitted footage/frames and cues. Results identify the reference revision and
   inspected scope. A contextual preview may include footage without baking it into
   a separately requested overlay. A combined-video export deliberately includes the
   specified footage. Unavailable context limits alignment claims, not all creation.
7. **Transparency and placement are real output properties.** An advertised overlay
   profile produces a usable transparent layer with declared dimensions, duration,
   timing, alpha/format behavior and placement data. An ordinary flattened MP4 is not
   passed off as transparent. Validate compatibility with the first intended consumer;
   do not promise every compositor or format. Required crop/transform and safe regions
   are preserved or their conflicts reported.
8. **Imported audio can guide and accompany motion.** The caller may supply narration,
   music, effects, audio signatures and timing cues. Unfold supports documented
   placement, synchronization and mixing of those assets. Audio inclusion is explicit:
   an overlay may be silent, reference existing sound, or deliver separate sound with
   its timing. A combined preview does not authorize duplicating a recording's audio
   in downstream delivery. Sound, music and voice generation are outside initial scope.
   Transcription or model audio analysis, if later supported, needs its own declared
   capability and authority; import alone does not initiate them.
9. **Captured and illustrative behavior stay distinguishable.** Retained records and
   handoffs identify actual capture, simulated UI and illustrative graphics. The
   presentation makes material distinctions apparent where viewers could otherwise
   be misled. Animation cannot be treated as evidence of measured performance,
   successful execution or an observed event merely because it looks convincing.
10. **Delivery identifies the exact work.** Preview, editable source, render and
    export records name their source revision. A requested output must exist, match
    its declared format and carry material limitations. Missing or broken artifacts
    are not success. Rendered exports do not silently incorporate drafts, newer
    revisions or changes outside the request. No-model rendering of existing source
    does not guarantee creative validity or repair malformed source.
11. **Review covers time as well as pixels.** Structural correctness, visual layout,
    source fidelity and temporal behavior are separate findings. Text visibility,
    event order, transitions and synchronization need suitable sequence evidence.
    Sampled stills are not proof of smooth motion, and visual inspection is not proof
    sound was heard. Reviews name the exact revision, inspected times/method, findings
    and omissions. Human acceptance is distinct from model review and rendering success.
12. **Reuse does not imply universal conversion.** Editable native source and needed
    dependencies are retained for supported continuation. Handoffs can include reusable
    motion elements and their configurable inputs. Another renderer, generic animation
    interchange and migration of existing compositions are not initial requirements.

## Proposed acceptance checks

- Use a technical brief with two independently recognizable approaches. Reject
  cosmetic recolors labeled as explanatory alternatives and a beautiful animation
  that conveys the wrong causal relationship.
- Select one approach and request a bounded change. Compare retained choices,
  source intent and actual rendered sequence, including a deliberately conflicting
  duration/readability request.
- Against known footage and cues, render a transparent overlay and a contextual
  preview. Composite the layer independently over a different test background to
  establish actual alpha and absence of baked-in reference footage.
- Include trimmed footage and a moved region; verify synchronization and placement
  from the handoff rather than hidden authoring knowledge.
- Import audio with known cue markers. Inspect decoded synchronization, channel
  policy and separate-asset handoff; assert no provider generation was invoked.
- Revise after review and verify that stale checks cannot certify the new output.
  Evaluate a full temporal sequence as well as selected frames, with sound where
  sound is part of the claim.

These scenarios need accepted fixtures and human quality criteria. They are not
executed checks. Numerical timing tolerances and output support must be established
before advertising them; attractive samples alone are insufficient evidence.

## What v1 deliberately does NOT freeze

Duration limits, number of alternatives, scene representation, animation techniques,
default aesthetics, codecs, render profiles, synchronization tolerances and automated
quality thresholds. The chosen first implementation must document its actual support.
