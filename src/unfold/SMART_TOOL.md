---
smart_tool_format: 1
name: unfold
version: 0.1.0.dev0
description: >-
  Create and revise silent motion explanations using embedded Amplifier Agent.
  Retain editable source, encoded output, frame evidence and revision history.
use_cases:
  - Explain a technical or mathematical idea through animated geometry and text
  - Revise an explanation while retaining the previous version
  - Review, rename and export saved outputs without a model
platforms:
  - macos
requires:
  - name: Node.js, HyperFrames 0.8.33 and GSAP 3.14.2
    purpose: Render existing compositions; not needed for help or retained-state reads.
    install: https://github.com/heygen-com/hyperframes
    optional: true
  - name: FFmpeg and FFprobe
    purpose: Decode video observations and inspect encoded media.
    install: https://ffmpeg.org/download.html
    optional: true
---
# Unfold

The Python library is the product. The CLI and optional loopback dashboard adapt
the same operations. This working slice creates silent, opaque 1280×720 H.264 MP4
explanations at 30 fps, lasting 5–60 seconds. Its authoring profile supports animated
cards, text, lines, dots, vector paths, polygons, circles and circular arcs. Shapes support stroke
drawing, translation, scaling and rotation, with shared camera pans and zooms.
It is not the full scope of the draft
vision/contracts.
Identity ZIP exchange, imported video/audio, transparent overlays, arbitrary HTML
authoring, external-edit adoption and automatic dashboard refinement are not yet
implemented. Identity guidance is currently supplied as text with each brief.

## Installation

Python 3.12+, Node.js and FFmpeg are prerequisites. From a checkout:

```sh
uv sync --extra smart
uv run unfold manifest
```

Git installation after these changes are published:
`uv tool install "amplifier-smart-tool-unfold[smart] @ git+https://github.com/robotdad/amplifier-smart-tool-unfold"`.
The repository is private; the installing caller needs access. Without `[smart]`,
deterministic capabilities work but creative operations require installing the extra.

Install pinned renderer dependencies into a selected directory outside the Python
installation, once. For the default backend directory:

```sh
mkdir -p ~/.local/share/unfold-backend
unfold backend-package > ~/.local/share/unfold-backend/package.json
npm install --prefix ~/.local/share/unfold-backend
unfold doctor
```

Only run that redirection for a new dedicated backend directory; it writes a package
manifest. HyperFrames may prepare its Chromium binary on the first render. Creative
calls do not run npm or initiate authentication. Amplifier Agent v0.17.0 and provider
module revisions are pinned; first Agent preparation can fetch its runtime modules.
Production guidance is packaged. No private skills directory is required.

## Library and authority

```python
from unfold import Unfold, Brief, Grant

tool = Unfold(library="/chosen/library", backend="/chosen/backend")
grant = Grant(
    provider="gemini", model="gemini-3.7-flash", allow_context=True, allow_frames=True, vision=True
)
outcome = tool.create(
    Brief(
        title="A request through our system",
        intent="Show how the caller delegates to an agent and receives an artifact.",
        context="Actual component roles and relationships supplied by the caller.",
        identity="Navy, mint and gold; restrained movement.",
        duration=20,
    ),
    grant,
)
if outcome["status"] == "completed":
    revision = tool.inspect(outcome["revision_id"])
    artifact = tool.artifact(revision["artifacts"][0])
```

`Brief.context` is actual supplied content, not a filename the agent should discover.
The caller explicitly permits disclosure of brief, context, identity, feedback,
composition data and sampled generated frames to the chosen model. No unrelated
filesystem material is available to the embedded agent. This profile requires a
vision-capable model; a false capability declaration will not make a text-only model
see images. `Grant` limits calls, tool actions, renders, frames, bytes, response tokens
and wall time; `unfold schemas` exposes bounds. Models are chosen explicitly; no
model fallback or authentication is initiated. Set `GEMINI_API_KEY`, `OPENAI_API_KEY`
or `ANTHROPIC_API_KEY` for the selected provider. Credentials never enter scene data.

The embedded agent authors validated scene data. Code emits executable HyperFrames
source; arbitrary model JavaScript, remote assets and custom CSS are not accepted.
The agent can render, sample encoded frames, repair and submit within one shared
allowance. A model completion sentence alone is not a result. Sampled-frame model
review is labeled and is not continuous playback inspection or human approval.

State defaults to `~/.local/share/unfold`; select `library` explicitly to change it.
The backend defaults to `~/.local/share/unfold-backend`. Both paths belong to the
process running Unfold. Output references identify Unfold-managed bytes; export
creates a new caller-owned copy and refuses overwrite. This slice accepts no external
media paths and has no removal operation. Do not delete managed files as an API.

## Capabilities

All results are JSON-compatible dictionaries/lists; validated creative inputs are
`Brief` and `Grant` objects or matching dictionaries. Errors use `UnfoldError` with
code, message and remedy. CLI stdout is JSON; diagnostics use stderr, and errors or
failed/cancelled operations exit nonzero. Closed stdin never triggers a prompt.
Use library return values for chaining. `--help` prints this skill, `-h` prints a
synopsis, and each subcommand accepts `--help`.

Global CLI options `--library PATH` and `--backend PATH` precede the subcommand.

- `create(brief, grant, request_id=None)` / `create --brief brief.json --grant grant.json`:
  model-backed. Returns a retained operation; completion identifies the revision.
- `revise(revision_id, feedback, grant, request_id=None)` /
  `revise REVISION --feedback TEXT --grant grant.json`: model-backed. Requires the
  current intact base. Creates a new revision; preserves the earlier one.
- `projects()` / `projects`: list retained projects and revision IDs.
- `inspect(id)` / `inspect ID`: records, resolved artifacts, source integrity,
  feedback, grant and checks as applicable. Reading never starts model work.
- `artifact(id)`: resolve a saved output's current name, path, ownership and integrity.
- `observe(after=0)` / `observe --after CURSOR`: ordered durable changes with cursors.
- `rename(id, name)` / `rename ID NAME`: rename project or saved output without
  rerendering. Labels may repeat; IDs are unique. Downloads use the current name.
- `export(artifact_id, directory)` / `export ARTIFACT DIRECTORY`: verified MP4 copy,
  no overwrite. Previously exported copies are not renamed or deleted.
- `render(revision_id)` / `render REVISION`: deterministic re-render of intact source;
  returns a new saved output without model initialization. No automatic repair.
- `feedback(revision_id, text)` / `feedback REVISION TEXT`: save a pending, targeted
  comment. A caller must explicitly initiate `revise`; viewing/submitting a comment
  does not launch model work in this slice.
- `address_feedback(feedback_id, revision_id)` / `address-feedback FEEDBACK REVISION`:
  link a submitted comment to the revision carrying its exact text and original base.
  Records the outcome without claiming human approval or triggering model work.
- `cancel(operation_id)` / `cancel OPERATION`: request cancellation; status remains
  `cancelling` until the active caller stops the worker and records the outcome.
- `doctor()` / `doctor`: report prerequisite versions and credential presence only.
- `dashboard(port=0)` / `dashboard [--port PORT]`: start a loopback, cookie-protected
  review service. Returned object has `url`, `close()` and context-manager support.
  CLI prints the private viewer URL, waits, and stops on Ctrl-C. No browser opens
  implicitly. Dashboard plays/scrubs, compares, renames and saves feedback; it only
  serves encoded video, never executable composition source.
- `unfold.help.manifest()`, `schemas()`, `skill()`, `backend_package()` correspond
  to CLI `manifest`, `schemas`, `--help`, `backend-package` and need no provider.

Creative operations are synchronous but their operation record and ordered progress
are readable from another process. Supply a 32-character lowercase hexadecimal
`request_id` (CLI `--request-id`) for acknowledged retry protection: exact retries
return the prior state, including running/failed states, without spending again.
Different input with the same ID fails. After caller/process loss a record may remain
running; this means uncertain interruption, not permission to retry automatically.
Cancellation needs a live executing caller; recovery of orphaned work is not yet
implemented. A new creative attempt requires a new request identity.

Retained source is native to this backend profile. Unexpected edits/missing files
are reported; they do not silently inherit checks. Do not treat SQLite tables or
directory naming as a supported caller protocol. Use public IDs and file references.
The full vision and contracts remain draft; packaging conformance is separate from
creative quality, motion correctness and review acceptance.
