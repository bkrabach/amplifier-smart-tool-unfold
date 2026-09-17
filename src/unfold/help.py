"""Library-owned self-description, available without intelligence or credentials."""

from importlib.resources import files

from .models import Brief, Grant


def skill():
    return files("unfold").joinpath("SMART_TOOL.md").read_text()


def manifest():
    return {
        "name": "unfold",
        "version": "0.1.0.dev0",
        "smart_tool_format": 1,
        "description": "Create and revise silent motion explanations with embedded Amplifier Agent.",
        "library": "unfold.Unfold",
        "capabilities": {
            "create": "model-backed",
            "revise": "model-backed",
            **{
                name: "deterministic"
                for name in (
                    "doctor",
                    "projects",
                    "inspect",
                    "observe",
                    "rename",
                    "export",
                    "render",
                    "feedback",
                    "address-feedback",
                    "cancel",
                    "dashboard",
                    "manifest",
                    "schemas",
                    "backend-package",
                )
            },
        },
    }


def schemas():
    return {"Brief": Brief.model_json_schema(), "Grant": Grant.model_json_schema()}


def backend_package():
    import json

    return json.loads(files("unfold").joinpath("resources/backend.json").read_text())
