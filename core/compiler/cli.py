from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.compiler.compiler_registry import CompilerRegistry
from core.compiler.language_detector import LanguageDetector
from core.usig.merger import USIGMerger
from passes.business_rules.business_rule_pass import BusinessRulePass
from passes.manager import PassManager
from passes.risk.risk_pass import RiskPass


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Rippl USBGC: detect repository languages, "
            "compile supported source code into USIG, "
            "merge compiler graphs, and run analysis passes."
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

    # Phase 1: Detect repository languages.
    detection = LanguageDetector(args.repo).detect()

    if detection.total_files == 0:
        raise SystemExit(
            "No recognized source-language files detected."
        )

    print(
        "Detected languages: "
        + ", ".join(
            f"{language} ({count})"
            for language, count in detection.counts.items()
        )
    )

    # Phase 2: Find available compilers.
    registry = CompilerRegistry()

    detected_languages = detection.detected_languages()

    supported_languages = [
        language
        for language in detected_languages
        if registry.supports(language)
    ]

    unsupported_languages = [
        language
        for language in detected_languages
        if not registry.supports(language)
    ]

    if unsupported_languages:
        print(
            "Detected but not yet compilable: "
            + ", ".join(unsupported_languages)
        )

    if not supported_languages:
        raise SystemExit(
            "Rippl detected source code, but no compiler "
            "is currently available for the detected languages."
        )

    # Phase 3: Run every available language compiler.
    compiled_graphs = []

    for language in supported_languages:
        compiler = registry.create(
            language,
            args.repo,
        )

        print(
            f"Using compiler for {language}: "
            f"{type(compiler).__name__}"
        )

        graph = compiler.compile()

        compiled_graphs.append(graph)

    # Phase 4: Merge all compiler-generated USIG graphs.
    merger = USIGMerger()

    graph = merger.merge(
        compiled_graphs
    )

    print(
        f"Merged {len(compiled_graphs)} "
        f"compiler graph(s)"
    )

    # Phase 5: Run language-independent analysis passes.
    pass_manager = PassManager(
        [
            BusinessRulePass(),
            RiskPass(),
        ]
    )

    graph = pass_manager.run(graph)

    # Phase 6: Serialize enriched USIG.
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
        "Languages in merged USIG: "
        + ", ".join(
            graph.project.get(
                "languages",
                [],
            )
        )
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