# Rippl

See the ripple before you commit.

Rippl is an AI-powered software impact intelligence platform that predicts the impact of software changes using graph reasoning and AI.

## Components

- USBGC (Universal Software Behavior Graph Compiler)
- USIG (Universal Software Intelligence Graph)
- RPE (Ripple Propagation Engine)

# Rippl MVP Core

Rippl predicts the ripple effect of software changes before they are committed.

This repository contains the first working prototype of:

- **USIG** — Universal Software Intelligence Graph
- **USBGC** — Universal Software Behavior Graph Compiler
- **RPE** — Ripple Propagation Engine

## Current MVP

Supported input:

- Local Python repositories

Generated graph includes:

- Repository nodes
- File nodes
- Class nodes
- Function nodes
- CALLS edges
- BusinessRule nodes from conditional logic
- RiskFinding nodes from financial keywords and complexity

## Compile a repo into USIG

```bash
cd rippl
PYTHONPATH=. python -m core.compiler.cli examples/sample_python_app --out outputs/usig.json
```

## Run ripple analysis

```bash
python -m passes.ripple.rpe outputs/usig.json function:billing.py.calculate_total --out outputs/ripple_report.json
```

## Main files

```text
core/usig/schema.py          # Universal graph schema
core/usig/factory.py         # Node and edge factory helpers
core/compiler/python_compiler.py # Python compiler frontend
core/compiler/cli.py         # USBGC CLI
passes/ripple/rpe.py         # Ripple Propagation Engine
examples/sample_python_app/  # Demo app
outputs/usig.json            # Example generated graph
outputs/ripple_report.json   # Example impact report
```

## Next implementation steps

1. Add Java parser frontend.
2. Add database/API detectors.
3. Add proper test detector.
4. Replace heuristic business-rule extraction with LLM-assisted extraction.
5. Add NestJS backend wrapper.
6. Add browser extension UI.
