const $ = (id) => document.getElementById(id),
  E = (tag, value, cls) => {
    const e = document.createElement(tag);
    if (value !== undefined) e.textContent = value;
    if (cls) e.className = cls;
    return e;
  };
let state,
  projectId,
  revisionId,
  compareId,
  comparison = false,
  packId,
  packVersionId,
  draftTimer,
  draftSequence = Date.now(),
  submissionId = null,
  loadedDraft = null;
const notice = (m) => ($("notice").textContent = m);
const guarded =
  (fn) =>
  async (...args) => {
    try {
      return await fn(...args);
    } catch (e) {
      notice(e.message);
    }
  };
async function api(path, data) {
  const r = await fetch(
    path,
    data === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        },
  );
  const v = await r.json();
  if (!r.ok)
    throw Error(
      typeof v.error === "string"
        ? v.error
        : v.error?.message || JSON.stringify(v),
    );
  return v;
}
const call = (capability, arguments) => api("/call", { capability, arguments });
const current = () => state?.revisions.find((r) => r.id === revisionId);
const project = () => state?.projects.find((p) => p.id === projectId);
const revisions = () =>
  state?.revisions.filter((r) => r.project_id === projectId) || [];
function option(select, id, name) {
  const o = E("option", name);
  o.value = id;
  select.append(o);
}
function fill(select, items, value) {
  select.replaceChildren();
  items.forEach((i) => option(select, i.id, i.name));
  select.value = value || "";
}
function button(name, fn, title) {
  const b = E("button", name);
  b.onclick = guarded(fn);
  if (title) b.title = title;
  return b;
}
function show(page) {
  document
    .querySelectorAll(".screen")
    .forEach((e) => (e.hidden = e.id !== page));
  document
    .querySelectorAll("nav button")
    .forEach((b) => b.classList.toggle("on", b.dataset.page === page));
  $("crumb").textContent = "Project / " + page[0].toUpperCase() + page.slice(1);
  if (page === "delivery") drawDelivery();
  if (page === "library") drawLibrary();
}
document
  .querySelectorAll("nav button")
  .forEach((b) => (b.onclick = () => show(b.dataset.page)));
function toggle(name) {
  const open = $(name + "Drawer").hidden;
  $(name + "Drawer").hidden = !open;
  $(name + "Toggle").classList.toggle("on", open);
  $(name + "Toggle").setAttribute("aria-expanded", String(open));
}
$("feedbackToggle").onclick = () => toggle("feedback");
$("historyToggle").onclick = () => toggle("history");
function revisionName(r) {
  return (
    "Revision " +
    (project()?.revisions.indexOf(r.id) + 1) +
    " · " +
    r.id.slice(0, 8)
  );
}
function drawPlayers() {
  const held = Number($("scrub").value);
  $("players").replaceChildren();
  $("players").classList.toggle("compare", comparison);
  $("single").classList.toggle("on", !comparison);
  $("compare").classList.toggle("on", comparison);
  (comparison ? [compareId, revisionId] : [revisionId])
    .filter(Boolean)
    .forEach((id, index) => {
      const r = state.revisions.find((r) => r.id === id);
      if (!r) return;
      const p = E("div", undefined, "pane"),
        s = E("select");
      s.setAttribute(
        "aria-label",
        comparison && index === 0 ? "Compare revision" : "Viewed revision",
      );
      revisions().forEach((r) => option(s, r.id, revisionName(r)));
      s.value = id;
      s.onchange = guarded(async () => {
        if (comparison && index === 0) {
          compareId = s.value;
          drawPlayers();
        } else await chooseRevision(s.value);
      });
      p.append(s);
      const a = r.resolved_artifacts?.[0];
      if (a && a.integrity === "intact") {
        const v = E("video");
        v.controls = true;
        v.preload = "metadata";
        v.muted = comparison && index === 0;
        v.onplay = () => {
          if (comparison)
            document.querySelectorAll("#players video").forEach((other) => {
              if (other !== v && other.paused) {
                other.currentTime = Math.min(v.currentTime, other.duration);
                other.play().catch((e) => notice(e.message));
              }
            });
        };
        v.onpause = () => {
          if (comparison)
            document.querySelectorAll("#players video").forEach((other) => {
              if (other !== v && !other.paused) other.pause();
            });
        };
        v.onseeked = () => {
          if (comparison)
            document.querySelectorAll("#players video").forEach((other) => {
              const time = Math.min(v.currentTime, other.duration);
              if (
                other !== v &&
                Number.isFinite(time) &&
                Math.abs(other.currentTime - time) > 0.08
              )
                other.currentTime = time;
            });
        };
        v.src = "/media/" + a.id;
        v.onloadedmetadata = () => {
          v.currentTime = Math.min(held, v.duration);
        };
        v.ontimeupdate = () => {
          if (!comparison || index === 1) {
            if (comparison && !v.paused)
              document.querySelectorAll("#players video").forEach((other) => {
                if (
                  other !== v &&
                  !other.seeking &&
                  Math.abs(other.currentTime - v.currentTime) > 0.08
                )
                  other.currentTime = Math.min(v.currentTime, other.duration);
              });
            $("scrub").value = v.currentTime;
            $("time").textContent = v.currentTime.toFixed(2) + "s";
          }
        };
        v.onerror = () =>
          notice(
            "This output could not be played. Inspect its integrity in History.",
          );
        p.append(v);
      } else p.append(E("div", "Output missing or changed.", "empty"));
      p.append(
        E("div", revisionName(r) + " · " + (a?.name || "No output"), "caption"),
      );
      $("players").append(p);
    });
  $("scrub").max = current()?.brief.duration || 60;
  $("selection").textContent = current()
    ? revisionName(current())
    : "No revision";
  $("feedbackTarget").textContent = current()
    ? revisionName(current()) + " · composition seconds"
    : "";
  loadDraft();
  drawStatus();
}
async function chooseRevision(id) {
  await saveDraft();
  revisionId = id;
  localStorage.setItem("unfold.revision", id);
  submissionId = null;
  loadedDraft = null;
  drawPlayers();
}
function loadDraft() {
  if (loadedDraft === revisionId) return;
  loadedDraft = revisionId;
  const d = state.drafts.find((d) => d.revision_id === revisionId);
  $("feedback").value = d?.text || "";
  $("at").value = d?.at || 0;
  $("end").value = d?.end ?? "";
  $("draftStatus").textContent = d?.submitted_job
    ? "Submitted · " + d.submitted_job.slice(0, 8)
    : "Unsubmitted draft";
  draftSequence = Math.max(Date.now(), (d?.sequence || 0) + 1);
}
async function saveDraft() {
  clearTimeout(draftTimer);
  if (!revisionId) return;
  const body = {
    revision_id: revisionId,
    text: $("feedback").value,
    at: Number($("at").value),
    end: $("end").value === "" ? null : Number($("end").value),
    sequence: ++draftSequence,
  };
  $("draftStatus").textContent = "Saving…";
  const saved = await api("/draft", body);
  state.drafts = state.drafts
    .filter((d) => d.revision_id !== body.revision_id)
    .concat(saved);
  if (revisionId === body.revision_id)
    $("draftStatus").textContent = saved.submitted_job
      ? "Submitted · " + saved.submitted_job.slice(0, 8)
      : "Draft retained · not submitted";
}
["feedback", "at", "end"].forEach(
  (id) =>
    ($(id).oninput = () => {
      submissionId = null;
      $("draftStatus").textContent = "Unsaved changes";
      clearTimeout(draftTimer);
      draftTimer = setTimeout(guarded(saveDraft), 350);
    }),
);
$("apply").onclick = guarded(async () => {
  await saveDraft();
  submissionId ??= crypto.randomUUID().replaceAll("-", "");
  const result = await api("/refine", {
    revision_id: revisionId,
    text: $("feedback").value,
    at: Number($("at").value),
    end: $("end").value === "" ? null : Number($("end").value),
    request_id: submissionId,
  });
  $("draftStatus").textContent = "Submitted · " + result.id.slice(0, 8);
  notice(
    "Feedback accepted · " +
      result.id.slice(0, 8) +
      ". Your viewed revision stays selected.",
  );
  await refresh();
});
$("note").onclick = guarded(async () => {
  await saveDraft();
  const n = await api("/feedback", {
    revision_id: revisionId,
    text: $("feedback").value,
  });
  notice("Comment retained · " + n.id.slice(0, 8) + ". No refinement started.");
  await refresh();
});
$("single").onclick = () => {
  comparison = false;
  drawPlayers();
};
$("compare").onclick = () => {
  comparison = true;
  if (!compareId || compareId === revisionId) {
    const index = revisions().findIndex((r) => r.id === revisionId);
    compareId = revisions()[Math.max(0, index - 1)]?.id || revisionId;
  }
  drawPlayers();
};
$("latest").onclick = guarded(() => chooseRevision(project().current_revision));
$("project").onchange = guarded(async () => {
  await saveDraft();
  projectId = $("project").value;
  revisionId = project().current_revision;
  localStorage.setItem("unfold.revision", revisionId);
  $("scrub").value = 0;
  compareId = project().revisions.at(-2) || revisionId;
  loadedDraft = null;
  $("title").textContent = project().name;
  drawPlayers();
});
$("play").onclick = guarded(async () => {
  const videos = [...$("players").querySelectorAll("video")];
  for (const v of videos) {
    v.currentTime = Math.min(Number($("scrub").value), v.duration);
    await v.play();
  }
});
$("pause").onclick = () =>
  document.querySelectorAll("#players video").forEach((v) => v.pause());
$("scrub").oninput = () => {
  document.querySelectorAll("#players video").forEach((v) => {
    v.pause();
    v.currentTime = Number($("scrub").value);
  });
  $("time").textContent = Number($("scrub").value).toFixed(2) + "s";
};
function drawStatus() {
  const a = state.authorities.find((a) => a.project_id === projectId);
  $("allowance").textContent = a
    ? `${a.remaining} authorized refinements remaining · ${a.grant.provider} / ${a.grant.model}`
    : "Caller authorization is needed before Apply.";
  $("apply").disabled = (!a?.remaining && !submissionId) || !current();
  $("latest").hidden =
    !project()?.current_revision || project().current_revision === revisionId;
  $("jobs").replaceChildren();
  state.jobs
    .filter((j) => j.project_id === projectId)
    .reverse()
    .forEach((j) => {
      const e = E("div", undefined, "event");
      e.append(E("b", j.status), E("p", j.text), E("small", j.id.slice(0, 8)));
      const err = j.error || j.result?.error;
      if (err)
        e.append(
          E(
            "p",
            typeof err === "string" ? err : err.message + " " + err.remedy,
          ),
        );
      if (["queued", "running", "cancelling"].includes(j.status))
        e.append(
          button("Cancel", async () => {
            await api("/cancel", { job_id: j.id });
            await refresh();
          }),
        );
      if (j.result?.revision_id)
        e.append(button("Open", () => chooseRevision(j.result.revision_id)));
      $("jobs").append(e);
    });
  $("history").replaceChildren();
  const detail = E("details");
  detail.append(
    E("summary", "Revision evidence"),
    E("pre", JSON.stringify(current(), null, 2)),
  );
  $("history").append(detail);
  state.events
    .filter(
      (e) =>
        e.subject === projectId ||
        revisions().some(
          (r) => r.id === e.subject || r.operation_id === e.subject,
        ) ||
        e.data?.project_id === projectId ||
        state.jobs.some(
          (j) =>
            j.project_id === projectId &&
            (j.id === e.subject || j.operation_id === e.subject),
        ),
    )
    .slice(-30)
    .reverse()
    .forEach((e) => {
      const d = E("div", undefined, "event");
      d.append(
        E("b", e.kind.replaceAll("_", " ")),
        E("small", " · " + new Date(e.time * 1000).toLocaleTimeString()),
        E("pre", JSON.stringify(e.data, null, 2)),
      );
      $("history").append(d);
    });
}
function modal(title) {
  $("dialogBody").replaceChildren();
  const head = E("div", undefined, "row spread");
  head.append(
    E("h2", title),
    button("Close", () => $("dialog").close()),
  );
  $("dialogBody").append(head);
  $("dialog").showModal();
  return $("dialogBody");
}
function rename(id, name) {
  const body = modal("Rename"),
    input = E("input");
  input.value = name;
  input.setAttribute("aria-label", "Name");
  body.append(
    input,
    button("Save", async () => {
      await api("/rename", { id, name: input.value });
      $("dialog").close();
      await refresh();
      drawLibrary();
    }),
  );
}
$("renameProject").onclick = () =>
  project() && rename(projectId, project().name);
function preview(a, url) {
  let e;
  if (a.mime?.startsWith("image/") && a.mime !== "image/svg+xml") {
    e = E("img");
    e.src = url;
    e.alt = a.name;
  } else if (a.mime?.startsWith("audio/")) {
    e = E("audio");
    e.controls = true;
    e.src = url;
  } else if (a.mime?.startsWith("video/")) {
    e = E("video");
    e.controls = true;
    e.preload = "metadata";
    e.src = url;
  } else {
    e = E("div", a.role === "font" ? "Aa Bb Cc 123" : a.role, "empty");
    if (a.role === "font") {
      const family = "asset" + a.id;
      new FontFace(family, "url(" + url + ")")
        .load()
        .then((f) => {
          document.fonts.add(f);
          e.style.fontFamily = family;
          e.style.fontSize = "24px";
        })
        .catch(() => (e.textContent = "Font preview unavailable"));
    }
  }
  return e;
}
function assetCard(a) {
  const card = E("div", undefined, "asset");
  card.append(
    preview(a, "/asset/" + a.id),
    E("b", a.name),
    E("small", a.role + " · " + a.ownership),
    E("small", a.integrity),
  );
  const row = E("div", undefined, "row");
  row.append(
    button("Rename", () => rename(a.id, a.name)),
    button("Details", () => assetDetails(a)),
    button("Remove", () => remove(a.id)),
  );
  card.append(row);
  return card;
}
function assetDetails(a) {
  const b = modal("Asset");
  b.append(
    E("h3", a.name),
    E("p", a.ownership + " · " + a.integrity),
    E("label", "Redistribution"),
  );
  const rights = E("select");
  ["unknown", "redistributable", "restricted"].forEach((v) =>
    option(rights, v, v),
  );
  rights.value = a.rights;
  b.append(rights, E("label", "Attribution (optional)"));
  const attribution = E("textarea");
  attribution.value = a.attribution;
  b.append(
    attribution,
    E(
      "p",
      "These are your declarations. Unfold does not verify rights; unknown or restricted assets are omitted from identity ZIPs.",
      "muted",
    ),
    button("Save", async () => {
      await call("update-asset", {
        asset_id: a.id,
        rights: rights.value,
        attribution: attribution.value,
      });
      $("dialog").close();
      await refresh();
      drawLibrary();
    }),
  );
}
async function remove(id) {
  const deps = await call("dependencies", { identity: id });
  const b = modal("Remove");
  b.append(
    E(
      "p",
      deps.length
        ? "This item is used by retained work. Removal is blocked."
        : "Remove this managed item? External originals remain untouched.",
    ),
    E("pre", deps.length ? JSON.stringify(deps, null, 2) : ""),
  );
  if (!deps.length)
    b.append(
      button("Remove", async () => {
        await call("remove", { identity: id });
        $("dialog").close();
        await refresh();
        drawLibrary();
      }),
    );
}
function guidanceView(guidance) {
  const body = E("div");
  Object.entries(guidance).forEach(([key, value]) => {
    if (value) {
      body.append(
        E("h3", key[0].toUpperCase() + key.slice(1)),
        E("p", typeof value === "string" ? value : JSON.stringify(value)),
      );
    }
  });
  return body;
}
function drawLibrary() {
  $("packs").replaceChildren();
  state.packs.forEach((p) => {
    const b = button(p.name, () => {
      packId = p.id;
      packVersionId = null;
      drawLibrary();
    });
    b.className = "pack" + (p.id === packId ? " on" : "");
    const v = state.versions.find((v) => v.id === p.current_version);
    b.append(E("small", ` · v${v?.number} · ${v?.assets.length} assets`));
    const shell = E("div", undefined, "card");
    shell.style.marginBottom = "10px";
    shell.append(b);
    const first = v?.assets
      .map((id) => state.assets.find((a) => a.id === id))
      .find(Boolean);
    if (first) shell.append(preview(first, "/asset/" + first.id));
    $("packs").append(shell);
  });
  $("assets").replaceChildren(...state.assets.map(assetCard));
  const p = state.packs.find((p) => p.id === packId);
  if (!p) {
    $("packDetail").replaceChildren(
      E("h2", "Selected pack"),
      E("p", "Select or create a pack.", "muted"),
    );
    return;
  }
  if (!p.versions.includes(packVersionId)) packVersionId = p.current_version;
  const v = state.versions.find((v) => v.id === packVersionId),
    body = $("packDetail");
  body.replaceChildren(E("small", "Selected pack"));
  const row = E("div", undefined, "row spread"),
    actions = E("div", undefined, "row");
  actions.append(
    button("Edit", () => editPack(p, v)),
    button("Export", () => exportPack(v)),
    button("Copy", async () => {
      const result = await call("duplicate-pack", {
        pack_id: p.id,
        name: p.name + " copy",
      });
      packId = result.id;
      await refresh();
      drawLibrary();
    }),
    button("Remove", () => remove(p.id)),
  );
  row.append(E("h2", p.name), actions);
  body.append(row, E("p", "Version " + v.number), guidanceView(v.guidance));
  const versionPicker = E("select");
  versionPicker.setAttribute("aria-label", "Pack version");
  p.versions.forEach((id) => {
    const version = state.versions.find((v) => v.id === id);
    option(
      versionPicker,
      id,
      "Version " +
        version.number +
        (id === p.current_version ? " · latest" : ""),
    );
  });
  versionPicker.value = v.id;
  versionPicker.onchange = () => {
    packVersionId = versionPicker.value;
    drawLibrary();
  };
  body.append(versionPicker);
  if (v.prerequisites.length)
    body.append(
      E("p", "Unresolved prerequisites"),
      E("pre", JSON.stringify(v.prerequisites, null, 2)),
    );
  const gallery = E("div", undefined, "gallery");
  v.assets.forEach((id) => {
    const a = state.assets.find((a) => a.id === id);
    if (a) gallery.append(assetCard(a));
  });
  body.append(gallery);
  const pin = current()?.identity_version;
  body.append(
    E(
      "p",
      pin
        ? "Viewed revision uses identity " + pin.slice(0, 8)
        : "Viewed revision has no selected identity.",
      "muted",
    ),
  );
  body.append(
    button(
      "Adopt",
      async () => {
        const b = modal("Adopt");
        b.append(
          E(
            "p",
            "Apply " +
              p.name +
              " v" +
              v.number +
              " to the viewed composition? This uses one authorized refinement and creates a new reviewable revision.",
          ),
          button("Apply", async () => {
            await api("/refine", {
              revision_id: revisionId,
              text: "Adopt this identity version, preserving the explanation, timing and unrelated choices.",
              identity_version: v.id,
              request_id: crypto.randomUUID().replaceAll("-", ""),
            });
            $("dialog").close();
            notice(
              "Identity adoption accepted. The viewed revision remains unchanged.",
            );
            await refresh();
          }),
        );
      },
      "Use this exact pack version in a new composition revision",
    ),
  );
  body.append(E("small", "Editing a pack leaves existing projects unchanged."));
}
function editPack(p, v) {
  const b = modal(p ? "Edit" : "Create");
  function input(id, title, value, multi = false) {
    const l = E("label", title);
    l.htmlFor = id;
    b.append(l);
    const e = E(multi ? "textarea" : "input");
    e.id = id;
    e.value = value || "";
    b.append(e);
    return e;
  }
  const name = input("packName", "Name", p?.name),
    required = input("required", "Required", v?.guidance.required, true),
    adapt = input("adaptable", "Adaptable", v?.guidance.adaptable, true),
    examples = input("examples", "Examples", v?.guidance.examples, true);
  b.append(E("h3", "Assets"));
  const choices = [];
  state.assets.forEach((a) => {
    const l = E("label", undefined, "check"),
      c = E("input");
    c.type = "checkbox";
    c.checked = v?.assets.includes(a.id) || false;
    choices.push([c, a.id]);
    l.append(c, E("span", a.name + " · " + a.role));
    b.append(l);
  });
  b.append(
    button("Save", async () => {
      const result = await call("save-pack", {
        name: name.value,
        guidance: {
          required: required.value,
          adaptable: adapt.value,
          examples: examples.value,
        },
        asset_ids: choices.filter(([c]) => c.checked).map(([, id]) => id),
        pack_id: p?.id || null,
        prerequisites: v?.prerequisites || [],
      });
      packId = result.id;
      packVersionId = result.current_version;
      $("dialog").close();
      await refresh();
      drawLibrary();
    }),
  );
}
$("createPack").onclick = () => editPack();
async function chooseFile(accept) {
  const f = $("file");
  f.accept = accept;
  f.value = "";
  return new Promise((resolve) => {
    f.onchange = () => resolve(f.files[0]);
    f.oncancel = () => resolve(null);
    f.click();
  });
}
async function upload(file, params) {
  const r = await fetch(
    "/upload?" + new URLSearchParams({ name: file.name, ...params }),
    { method: "POST", body: file },
  );
  const v = await r.json();
  if (!r.ok) throw Error(v.error);
  return v;
}
$("addAsset").onclick = guarded(async () => {
  const b = modal("Add");
  b.append(
    E("p", "A managed copy will be retained; your original stays in place."),
  );
  const role = E("select");
  ["image", "video", "audio", "font", "example", "motion", "recipe"].forEach(
    (r) => option(role, r, r),
  );
  b.append(
    role,
    button("Select", async () => {
      const f = await chooseFile("");
      if (!f) return;
      await upload(f, { kind: "asset", role: role.value });
      $("dialog").close();
      await refresh();
      drawLibrary();
    }),
  );
});
$("importPack").onclick = guarded(async () => {
  const file = await chooseFile(".zip");
  if (!file) return;
  notice("Inspecting pack…");
  const result = await upload(file, { kind: "pack" });
  notice("");
  const b = modal("Import"),
    m = result.manifest,
    actions = E("div", undefined, "row");
  actions.append(
    button("Cancel", () => $("dialog").close()),
    button("Import", async () => {
      const r = await api("/import", { upload_id: result.upload_id });
      packId = r.pack_id;
      $("dialog").close();
      await refresh();
      drawLibrary();
    }),
  );
  b.append(actions, E("h3", m.name), guidanceView(m.guidance));
  const gallery = E("div", undefined, "gallery");
  m.assets.forEach((a, i) => {
    const c = E("div", undefined, "asset");
    c.append(
      preview(a, "/pack-preview/" + result.upload_id + "/" + i),
      E("b", a.name),
    );
    gallery.append(c);
  });
  b.append(gallery);
  if (m.omissions.length || m.prerequisites.length)
    b.append(
      E("h3", "Prerequisites and omissions"),
      E("pre", JSON.stringify([...m.prerequisites, ...m.omissions], null, 2)),
    );
});
async function saveURL(url, name) {
  if (window.showSaveFilePicker) {
    const handle = await window.showSaveFilePicker({ suggestedName: name });
    const response = await fetch(url);
    if (!response.ok) throw Error("Export could not be read.");
    const writable = await handle.createWritable();
    await writable.write(await response.blob());
    await writable.close();
    notice("Saved.");
  } else {
    const link = E("a");
    link.href = url;
    link.download = name;
    link.click();
    notice(
      "This browser controls the save location. Enable “ask where to save” in its download settings to choose a destination.",
    );
  }
}
async function exportPack(v) {
  const b = modal("Export");
  b.append(
    E("p", "Identity pack · guidance, eligible assets and declared omissions."),
  );
  const result = await api("/prepare", { kind: "pack", id: v.id });
  b.append(
    E("h3", "Included"),
    E(
      "p",
      result.manifest.assets.map((a) => a.name).join(", ") || "Guidance only",
    ),
    E("h3", "Omissions"),
    E(
      "p",
      result.manifest.omissions
        .map((a) => a.name + ": " + a.reason)
        .join("; ") || "None",
    ),
    E("h3", "Prerequisites"),
    E(
      "p",
      result.manifest.prerequisites
        .map((a) =>
          typeof a === "string" ? a : a.name || a.reason || JSON.stringify(a),
        )
        .join("; ") || "None",
    ),
    button("Save", async () => {
      await saveURL(
        "/download/" + result.id,
        (state.packs.find((p) => p.id === v.pack_id)?.name || "Unfold") +
          ".zip",
      );
      $("dialog").close();
    }),
  );
}
function drawDelivery() {
  $("exportRevision").textContent = current()
    ? revisionName(current())
    : "No revision";
  for (const [id, role] of [
    ["reference", "video"],
    ["audio", "audio"],
  ]) {
    const old = $(id).value;
    fill(
      $(id),
      [
        { id: "", name: "None" },
        ...state.assets.filter(
          (a) => a.role === role && a.integrity === "intact",
        ),
      ],
      old,
    );
  }
  $("outputs").replaceChildren();
  state.outputs
    .filter((a) => a.revision_id === revisionId)
    .reverse()
    .forEach((a) => {
      const c = E("div", undefined, "event");
      c.append(
        E("b", a.name),
        E(
          "p",
          `${a.profile === "overlay" ? "Overlay only" : a.profile === "video" ? "Video" : "Animation"} · ${a.format || "mp4"} · ${a.duration?.toFixed(2) || "?"}s`,
        ),
      );
      if (a.format !== "mov") {
        const v = E("video");
        v.controls = true;
        v.preload = "metadata";
        v.src = "/media/" + a.id;
        c.append(v);
      } else
        c.append(
          E(
            "p",
            "ProRes 4444 · alpha. Save for a compatible compositor; browser playback is not assumed.",
            "muted",
          ),
        );
      const row = E("div", undefined, "row");
      row.append(
        button("Save", () =>
          saveURL("/media/" + a.id + "?download=1", a.download_name),
        ),
        button("Rename", () => rename(a.id, a.name)),
      );
      if (a.delivery_id)
        row.append(
          button("Handoff", async () => {
            const b = modal("Export");
            b.append(
              E(
                "p",
                "Output, separate audio assets and timing manifest. Reference footage is excluded from an overlay handoff.",
              ),
            );
            const result = await api("/prepare", { kind: "handoff", id: a.id });
            b.append(
              button("Save", async () => {
                await saveURL("/download/" + result.id, "Unfold handoff.zip");
                $("dialog").close();
              }),
            );
          }),
        );
      c.append(row);
      $("outputs").append(c);
    });
}
async function render(mode) {
  if (!revisionId) throw Error("Select a revision first.");
  $("renderVideo").disabled = $("renderOverlay").disabled = true;
  notice(
    "Rendering " +
      (mode === "overlay" ? "transparent overlay" : "video") +
      "… You can continue reviewing.",
  );
  try {
    const d = await call("configure-delivery", {
      revision_id: revisionId,
      reference_id: $("reference").value || null,
      reference_start: Number($("referenceStart").value),
      audio: $("audio").value
        ? [
            {
              asset_id: $("audio").value,
              start: Number($("audioStart").value),
              offset: Number($("audioOffset").value),
            },
          ]
        : [],
      cues: $("cueText").value
        ? [{ at: Number($("scrub").value), text: $("cueText").value }]
        : [],
    });
    const a = await call("render-delivery", { delivery_id: d.id, mode });
    notice("Output ready · " + a.id.slice(0, 8));
    await refresh();
    drawDelivery();
  } finally {
    $("renderVideo").disabled = $("renderOverlay").disabled = false;
  }
}
$("renderVideo").onclick = guarded(() => render("video"));
$("renderOverlay").onclick = guarded(() => render("overlay"));
async function refresh() {
  const next = await api("/state"),
    first = !state;
  state = next;
  if (!projectId) {
    const retained = localStorage.getItem("unfold.revision");
    revisionId = state.revisions.some((r) => r.id === retained)
      ? retained
      : state.projects.find((p) => p.current_revision)?.current_revision;
    projectId =
      state.revisions.find((r) => r.id === revisionId)?.project_id ||
      state.projects[0]?.id;
    compareId = project()?.revisions.at(-2) || revisionId;
  }
  fill($("project"), state.projects, projectId);
  $("title").textContent = project()?.name || "No projects yet";
  if (first) {
    if (revisionId) drawPlayers();
    else
      $("players").append(
        E(
          "div",
          "Create a project through the Unfold library or CLI to begin.",
          "empty",
        ),
      );
    packId = state.packs[0]?.id;
    drawLibrary();
    drawDelivery();
  } else {
    document.querySelectorAll("#players select").forEach((s) => {
      const old = s.value;
      fill(
        s,
        revisions().map((r) => ({ id: r.id, name: revisionName(r) })),
        old,
      );
    });
    drawStatus();
  }
}
refresh().catch((e) => notice(e.message));
setInterval(
  () => refresh().catch((e) => notice("Disconnected: " + e.message)),
  3000,
);

function drawTheme() {
  const mode = document.documentElement.dataset.theme || "system";
  const next = { system: "light", light: "dark", dark: "system" }[mode];
  const label =
    "Theme: " +
    mode[0].toUpperCase() +
    mode.slice(1) +
    ". Switch to " +
    next[0].toUpperCase() +
    next.slice(1) +
    ".";
  $("theme").title = label;
  $("theme").setAttribute("aria-label", label);
  const icons = {
    system:
      '<rect x="3" y="4" width="18" height="13" rx="2"/><path d="M8 21h8M12 17v4"/>',
    light:
      '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M5 5l1.5 1.5M17.5 17.5 19 19M5 19l1.5-1.5M17.5 6.5 19 5"/>',
    dark: '<path d="M20.8 13A9 9 0 0 1 11 3.2 9 9 0 1 0 20.8 13Z"/>',
  };
  // All SVG is code-owned; no asset or model markup enters this control.
  $("theme").innerHTML =
    '<svg aria-hidden="true" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">' +
    icons[mode] +
    "</svg>";
  $("theme").onclick = () => {
    window.unfoldTheme(next, true);
    drawTheme();
  };
}
drawTheme();
