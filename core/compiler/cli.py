from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.compiler.python_compiler import PythonUSIGCompiler


def main() -> None:
    parser = argparse.ArgumentParser(description="Rippl USBGC: compile a repository into USIG JSON.")
    parser.add_argument("repo", help="Path to local repository")
    parser.add_argument("--out", default="usig.json", help="Output JSON path")
    args = parser.parse_args()

    compiler = PythonUSIGCompiler(args.repo)
    graph = compiler.compile()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph.to_dict(), indent=2), encoding="utf-8")
    print(f"Wrote {out} with {len(graph.nodes)} nodes and {len(graph.edges)} edges")


if __name__ == "__main__":
    main()
