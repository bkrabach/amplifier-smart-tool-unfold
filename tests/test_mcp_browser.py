"""Real App SDK, independent bridge, and decoded media: no provider/model calls."""

import asyncio
import subprocess
from pathlib import Path

import pytest

pytest.importorskip("mcp")
pytest.importorskip("playwright")
from mcp import Client
from mcp_fixtures import seed_media_library
from playwright.async_api import async_playwright, expect

from unfold.mcp import create_server
from unfold.store import digest

ROOT = Path(__file__).parents[1]


def test_mcp_app_video_drafts_shared_position_and_reopen(tmp_path):
    node_modules = ROOT / "mcp-app" / "node_modules"
    if not node_modules.exists():
        pytest.skip("Run npm ci --prefix mcp-app for the independent AppBridge fixture.")
    script = subprocess.run(
        [
            str(node_modules / ".bin" / "esbuild"),
            str(ROOT / "mcp-app" / "test-host.js"),
            "--bundle",
            "--format=iife",
            "--log-level=error",
        ],
        check=True,
        capture_output=True,
        text=True,
    ).stdout

    async def run():
        library, _, revisions, artifacts = seed_media_library(tmp_path)
        async with Client(create_server(library)) as client, async_playwright() as pw:
            browser = await pw.chromium.launch()
            page = await browser.new_page(viewport={"width": 1000, "height": 1350})
            errors, calls, reads = [], [], []
            page.on("pageerror", lambda error: errors.append(str(error)))

            async def call(params):
                calls.append(params)
                result = await client.call_tool(params["name"], params.get("arguments", {}))
                return result.model_dump(by_alias=True, exclude_none=True)

            async def read(params):
                reads.append(params)
                result = await client.read_resource(params["uri"])
                return result.model_dump(by_alias=True, exclude_none=True)

            await page.expose_function("hostCall", call)
            await page.expose_function("hostRead", read)
            await page.goto("about:blank")
            await page.add_script_tag(content=script)
            initial = await client.call_tool("unfold_review_state", {})
            html = (ROOT / "src" / "unfold" / "resources" / "mcp_app.html").read_text()
            wire = initial.model_dump(by_alias=True, exclude_none=True)
            await page.evaluate("([html,result])=>mountUnfold(html,result)", [html, wire])
            frame = page.frame_locator("#app")
            await expect(frame.locator("#notice")).to_have_text("Ready to review retained work.")
            await expect(frame.locator("#identity")).to_have_text(revisions[-1])
            await expect(frame.locator("#video")).to_be_visible()
            video = frame.locator("#video")
            await expect(video).to_have_js_property("videoWidth", 320)
            await expect(video).to_have_js_property("videoHeight", 180)
            assert 4.9 <= await video.evaluate("v=>v.duration") <= 5.1
            assert (await video.get_attribute("src")).startswith("blob:")
            await frame.locator("#play").click()
            await expect(frame.locator("#notice")).to_have_text("Playback updated.")
            await page.wait_for_timeout(350)
            assert await video.evaluate("v=>v.currentTime") > 0.1
            await frame.locator("#play").click()
            await frame.locator("#scrub").fill("2")
            await frame.locator("#scrub").dispatch_event("change")
            await expect(frame.locator("#notice")).to_have_text("Review position saved.")
            assert library.review_state()["views"][0]["at"] == 2
            await frame.locator("#draft").fill("Keep the handoff visible")
            await expect(frame.locator("#notice")).to_have_text("Draft saved; no work started.")
            assert library.review_state()["drafts"][0]["text"] == "Keep the handoff visible"
            # Agent selection flows through the same public method and quiet polling.
            old_notice = await frame.locator("#notice").inner_text()
            reads_before = len(reads)
            view = library.review_state()["views"][0]
            await client.call_tool(
                "unfold_save_review_view",
                {
                    "revision_id": revisions[0],
                    "artifact_id": artifacts[0],
                    "at": 1,
                    "expected_version": view["version"],
                },
            )
            await expect(frame.locator("#identity")).to_have_text(revisions[0], timeout=8000)
            await expect(frame.locator("#draft")).to_have_value("")
            await expect(frame.locator("#notice")).to_have_text(old_notice)
            assert len(reads) > reads_before
            # Agent draft edits on the already displayed revision also appear quietly.
            await client.call_tool(
                "unfold_save_draft",
                {
                    "revision_id": revisions[0],
                    "text": "Agent draft context",
                    "sequence": 9999999999999,
                },
            )
            await expect(frame.locator("#draft")).to_have_value("Agent draft context", timeout=8000)
            # Same media is not fetched again during the next routine refresh.
            reads_before = len(reads)
            await page.wait_for_timeout(5200)
            assert len(reads) == reads_before
            await expect(frame.locator("#notice")).to_have_text(old_notice)
            await frame.locator("#revisions").select_option(revisions[-1])
            await expect(frame.locator("#draft")).to_have_value("Keep the handoff visible")
            await frame.locator("#note").click()
            await expect(frame.locator("#notice")).to_have_text("Note recorded without generation.")
            assert library.store.list("feedback")[0]["revision_id"] == revisions[-1]
            # Invalid grants produce useful feedback, never hidden provider calls.
            await frame.locator("#refine").click()
            await expect(frame.locator("#notice.error")).to_contain_text(
                "Choose a vision-capable model"
            )
            assert not any(
                c["name"] in ("unfold_submit_creation", "unfold_submit_refinement") for c in calls
            )
            assert library.store.list("operation") == []
            assert library.store.list("review_job") == []
            assert (
                await page.evaluate("window.savedContext.structuredContent.draft_is_authority")
                is False
            )
            # Reopening observes durable state; no new work or authority is inferred.
            await page.evaluate("([html,result])=>mountUnfold(html,result)", [html, wire])
            frame = page.frame_locator("#app")
            await expect(frame.locator("#draft")).to_have_value("Keep the handoff visible")
            await expect(frame.locator("#video")).to_have_js_property("videoWidth", 320)
            await page.screenshot(path=str(tmp_path / "unfold-mcp-review.png"), full_page=True)
            await page.set_viewport_size({"width": 440, "height": 1000})
            assert await frame.locator("body").evaluate("el => el.scrollWidth <= window.innerWidth")
            await page.screenshot(
                path=str(tmp_path / "unfold-mcp-review-narrow.png"), full_page=True
            )
            # A host lacking resources gets a visible honest capability limitation.
            await page.evaluate("([html,result])=>mountUnfold(html,result,false)", [html, wire])
            await expect(page.frame_locator("#app").locator("#notice.error")).to_contain_text(
                "does not support MCP resource reads"
            )
            # Large media is an explicit limit; no resource fetch begins.
            record = library.store.get(artifacts[-1], "artifact")
            media_path = library.store.root / record["relative_path"]
            media_path.write_bytes(b"large-media-limit-fixture" * (33 * 1024 * 1024 // 24 + 1))
            record["sha256"] = digest(media_path)
            library.store.put("artifact", record)
            reads_before = len(reads)
            await page.evaluate("([html,result])=>mountUnfold(html,result)", [html, wire])
            await expect(page.frame_locator("#app").locator("#notice.error")).to_contain_text(
                "exceeds the 32 MiB view limit"
            )
            assert len(reads) == reads_before
            assert not errors, errors
            await browser.close()

    asyncio.run(run())
