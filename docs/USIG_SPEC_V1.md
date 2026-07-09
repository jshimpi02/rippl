# USIG Specification v1

USIG is the Universal Software Intelligence Graph used by Rippl.

## Node schema

Every node contains:

- id
- type
- name
- qualified_name
- language
- source
- attributes
- metrics
- provenance

## Edge schema

Every edge contains:

- id
- source
- target
- type
- attributes
- provenance

## MVP node types

- Repository
- File
- Class
- Function
- BusinessRule
- RiskFinding

## MVP edge types

- CONTAINS
- DECLARES
- CALLS
- IMPLEMENTS_RULE
- HAS_RISK

## Design principle

Facts from static analysis should have high confidence. LLM or heuristic facts must include confidence and evidence.
