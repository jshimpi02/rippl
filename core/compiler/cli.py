from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.compiler.python_compiler import PythonUSIGCompiler
from passes.business_rules.business_rule_pass import BusinessRulePass
from passes.manager import PassManager
from passes.risk.risk_pass import RiskPass


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Rippl USBGC: compile a repository into "
            "an enriched USIG JSON graph."
        )
    )

    parser.add_argument(
        "repo",
        help="Path to local repository",
    )

    parser.add_argument(
        "--out",
        default="usig.json",
        help="Output JSON path",
    )

    args = parser.parse_args()

    # Phase 1: Compile source code into the base USIG.
    compiler = PythonUSIGCompiler(args.repo)
    graph = compiler.compile()

    # Phase 2: Run language-independent analysis passes.
    pass_manager = PassManager(
        [
            BusinessRulePass(),
            RiskPass(),
        ]
    )

    graph = pass_manager.run(graph)

    # Phase 3: Serialize the enriched USIG.
    out = Path(args.out)
    out.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    out.write_text(
        json.dumps(
            graph.to_dict(),
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Wrote {out} with "
        f"{len(graph.nodes)} nodes and "
        f"{len(graph.edges)} edges"
    )

    print(
        "Analysis passes: "
        + ", ".join(
            analysis_pass.name
            for analysis_pass in pass_manager.passes
        )
    )


if __name__ == "__main__":
    main()