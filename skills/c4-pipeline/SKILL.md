---
name: c4-pipeline
description: Automate a C4 diagram from Docker Compose or Kubernetes manifests. Use when the user wants a diagram generated in CI, kept in sync with the repository, or asks whether automating one is worth it. Assesses the sources first, then writes a generator.
---

# c4-pipeline

Decides whether a repository's manifests can feed an automatic `c4-diagrams` JSON diagram, then writes the generator in
the user's repository. Markdown only: no scripts.

Sources covered: Docker Compose and Kubernetes (Helm and kustomize after rendering). Terraform, Ansible and OpenAPI are
not covered yet: say so and stop. A one-off diagram of a codebase is `c4-diagrams`.

Load the `c4-diagrams` skill first. Its rules apply here: source before images, explicit backend flags, consent before
any remote service, warning before network access, `--help` for unknown flags.

## Rules

1. **Verdict before code.** No generator until the verdict is stated and the user agrees.
2. **Evidence.** Every rating and verdict cites files you opened. A claim without a file is a guess.
3. **No-go stops.** After a No-go write no generator unless the user insists; then build the minimum and repeat the
   main risks in the summary.
4. **Inferred means assumption.** A relationship from a naming guess, an environment variable or a URL is labeled an
   assumption in the output and listed as unresolved.
5. **The user's repository owns the generator.** Ship nothing from this skill.

## Steps

1. **Inventory.** Find the Compose files and Kubernetes manifests (including Helm charts and kustomize overlays). List
   each with its path. None found, or only other sources: say it is not covered and stop.
2. **Rate** each source on formality, extraction (elements and relationships separately), stability and value:
   [references/assessment.md](references/assessment.md). What each source yields:
   [references/sources.md](references/sources.md).
3. **Verdict.** One of Go, Go partially, No-go, with the evidence and the report from `assessment.md`.
4. **Agreement.** Wait for the user. This is the gate: nothing below runs before a yes, and not after a No-go (Rule 3).
5. **Target.** Ask which target and recommend one: [references/generator-patterns.md](references/generator-patterns.md),
   section Target.
6. **Generate** with the patterns in the same file.
7. **Validate** by loading the output with `c4 render`, then add the drift check. Both are in `generator-patterns.md`.
