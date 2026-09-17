"""Private process entry point. Public clients use the library, never this protocol."""

import asyncio
import json
import sys
from pathlib import Path

from .models import UnfoldError
from .store import write_json


def main():
    path = Path(sys.argv[1])
    try:
        from .agent import execute
        from .intelligence import Production

        result = asyncio.run(execute(Production(json.loads(path.read_text()))))
    except Exception as exc:
        error = (
            exc
            if isinstance(exc, UnfoldError)
            else UnfoldError(
                "AGENT_FAILED",
                "Embedded agent execution failed.",
                "Inspect local worker diagnostics and prerequisites.",
            )
        )
        result = {"error": error.as_dict()}
    write_json(path.parent / "result.json", result)


if __name__ == "__main__":
    main()
